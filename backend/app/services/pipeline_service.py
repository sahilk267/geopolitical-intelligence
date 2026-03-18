"""
Pipeline Orchestration Service
Handles the end-to-end flow: Articles → Report → Audio → Video.
"""
import logging
import uuid
import os
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.config import settings
from app.models.article import RawArticle, NormalizedArticle
from app.models.profile import Profile
from app.services.ai_service import ai_service
from app.services.tts_service import tts_service
from app.services.video_service import video_render_service
from app.services.avatar_service import avatar_service
from app.services.social_distributor import social_distributor

logger = logging.getLogger(__name__)

class PipelineService:
    async def run_full_pipeline(
        self,
        db: AsyncSession,
        category: str,
        region: str = "Global",
        profile_id: Optional[UUID] = None,
        voice_id: str = "default",
        generate_short: bool = True,
        generate_presenter: bool = True,
        distribute_to: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Executes the full content production pipeline.
        """
        pipeline_result = {
            "category": category,
            "region": region,
            "profile_id": str(profile_id) if profile_id else None,
            "steps": {},
            "errors": [],
        }

        # ── Step 0: Get Profile ──
        profile_dict = None
        if profile_id:
            result = await db.execute(select(Profile).where(Profile.id == profile_id))
            profile = result.scalar_one_or_none()
            if profile:
                profile_dict = profile.to_dict()
                logger.info(f"Using profile: {profile.name}")

        # ── Step 1: Get articles ──
        query = (
            select(RawArticle)
            .where(RawArticle.category == category)
            .order_by(desc(RawArticle.fetched_at))
            .limit(10)
        )
        result = await db.execute(query)
        articles = result.scalars().all()

        if not articles:
            query = (
                select(NormalizedArticle)
                .where(NormalizedArticle.category == category)
                .order_by(desc(NormalizedArticle.created_at))
                .limit(10)
            )
            result = await db.execute(query)
            articles = result.scalars().all()

        if not articles:
            return {"error": f"No articles found for category {category}"}

        article_dicts = [a.to_dict() for a in articles]
        pipeline_result["steps"]["articles"] = {"count": len(article_dicts), "status": "success"}

        # ── Step 2: Generate report ──
        try:
            report = await ai_service.generate_journalist_report(
                article_dicts, category, region, profile=profile_dict
            )
            if "error" in report:
                pipeline_result["errors"].append(f"Report: {report['error']}")
                pipeline_result["steps"]["report"] = {"status": "failed", "error": report["error"]}
                return pipeline_result
            pipeline_result["steps"]["report"] = {
                "status": "success",
                "headline": report.get("headline", ""),
            }
        except Exception as e:
            pipeline_result["errors"].append(f"Report: {str(e)}")
            return pipeline_result

        # ── Step 3: Generate audio ──
        narration_text = report.get("executive_summary", "")
        if isinstance(narration_text, dict):
            narration_text = " ".join(str(v) for v in narration_text.values())

        try:
            audio_result = await tts_service.generate_audio(
                narration_text, voice_id, profile=profile_dict
            )
            if "error" in audio_result:
                pipeline_result["errors"].append(f"Audio: {audio_result['error']}")
                pipeline_result["steps"]["audio"] = {"status": "failed"}
            else:
                pipeline_result["steps"]["audio"] = {
                    "status": "success",
                    "url": audio_result["url"],
                    "duration": audio_result["duration_seconds"],
                }
        except Exception as e:
            pipeline_result["errors"].append(f"Audio: {str(e)}")

        # ── Step 4: Generate short clip ──
        if generate_short and pipeline_result["steps"].get("audio", {}).get("status") == "success":
            image_paths = []
            try:
                image_prompts = await ai_service.generate_image_prompts(narration_text)
                for i, p in enumerate(image_prompts[:3]):
                    img_filename = f"broll_{uuid.uuid4().hex[:8]}.png"
                    img_path = os.path.join(settings.VIDEO_OUTPUT_DIR, "thumbnails", img_filename)
                    path = await ai_service.generate_image(p, img_path)
                    if path:
                        image_paths.append(path)
            except Exception as e:
                logger.error(f"Image generation failed: {e}")

            try:
                # Find default music track
                music_path = os.path.join(os.path.dirname(settings.VIDEO_OUTPUT_DIR), "assets", "music", "cinematic_news.mp3")
                if not os.path.exists(music_path):
                    music_path = None

                short_result = await video_render_service.render_short_clip(
                    audio_path=audio_result["path"],
                    headline=report.get("headline", category),
                    script_text=narration_text,
                    image_paths=image_paths,
                    music_path=music_path,
                    profile=profile_dict
                )
                if "error" in short_result:
                    pipeline_result["errors"].append(f"Short clip: {short_result['error']}")
                else:
                    pipeline_result["steps"]["short_clip"] = {
                        "status": "success",
                        "url": short_result["url"],
                    }
            except Exception as e:
                pipeline_result["errors"].append(f"Short clip: {str(e)}")

        # ── Step 5: Generate presenter avatar ──
        if generate_presenter and pipeline_result["steps"].get("audio", {}).get("status") == "success":
            try:
                # Extract avatar settings from video_style (if available)
                avatar_config = profile_dict.get("videoStyle", {}).get("avatar", {}) if profile_dict else {}
                presenter_image = avatar_config.get("presenter_image")
                
                # generate_lipsync takes local path or URL, handled by avatar_service
                avatar_result = await avatar_service.generate_lipsync(
                    audio_url=audio_result["path"],  # Use local path for local engines
                    presenter_image=presenter_image
                )
                
                if avatar_result.get("skipped"):
                    logger.info(f"Avatar generation skipped: {avatar_result.get('reason', 'Engine not available')}")
                    pipeline_result["steps"]["avatar"] = {"status": "skipped", "reason": avatar_result.get("reason", "")}
                elif "error" in avatar_result:
                    logger.warning(f"Avatar generation failed: {avatar_result['error']}")
                    pipeline_result["errors"].append(f"Avatar: {avatar_result['error']}")
                    pipeline_result["steps"]["avatar"] = {"status": "failed"}
                else:
                    pipeline_result["steps"]["avatar"] = {
                        "status": "success",
                        "url": avatar_result["url"],
                        "path": avatar_result["path"]
                    }
            except Exception as e:
                logger.error(f"Avatar step exception: {e}")
                pipeline_result["errors"].append(f"Avatar: {str(e)}")

        # ── Step 6: Distribution ──
        if distribute_to and pipeline_result["steps"].get("short_clip", {}).get("status") == "success":
            video_url = pipeline_result["steps"]["short_clip"]["url"]
            video_path = video_url.replace("/output/", settings.VIDEO_OUTPUT_DIR + os.sep)
            try:
                dist_results = await social_distributor.distribute("video", distribute_to, {
                    "video_path": video_path,
                    "title": report.get("headline", category),
                    "description": narration_text[:1000]
                }, profile_configs=profile_dict.get("platformConfigs") if profile_dict else None)
                pipeline_result["steps"]["distribution"] = {"status": "success", "results": dist_results}
            except Exception as e:
                pipeline_result["errors"].append(f"Distribution: {str(e)}")

        return pipeline_result

pipeline_service = PipelineService()
