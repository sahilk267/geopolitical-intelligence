"""
Pipeline Orchestration API
Full automation: Data → Report → Audio → Video in one call.
"""
import logging
import uuid
import os
import json
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.article import RawArticle, NormalizedArticle
from app.models.script import Script, ScriptStatus
from app.api.v1.endpoints.auth import get_current_active_user, require_role
from app.models.user import UserRole

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/run-full")
async def run_full_pipeline(
    category: str,
    region: str = "Global",
    voice_id: str = "default",
    generate_short: bool = True,
    generate_presenter: bool = True,
    distribute_to: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(UserRole.JUNIOR_EDITOR)),
):
    """
    Run the complete pipeline for a category:
    1. Fetch & aggregate articles by category
    2. Generate journalist-quality report
    3. Generate audio from report
    4. Generate short clip (30s-1min, no presenter)
    5. Generate presenter video (with lip-sync) [if API configured]
    """
    pipeline_result = {
        "category": category,
        "region": region,
        "steps": {},
        "errors": [],
    }

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
        # Try normalized articles
        query = (
            select(NormalizedArticle)
            .where(NormalizedArticle.category == category)
            .order_by(desc(NormalizedArticle.created_at))
            .limit(10)
        )
        result = await db.execute(query)
        articles = result.scalars().all()

    if not articles:
        raise HTTPException(
            status_code=404,
            detail=f"No articles for category '{category}'. Fetch sources first.",
        )

    article_dicts = [a.to_dict() for a in articles]
    pipeline_result["steps"]["articles"] = {
        "count": len(article_dicts),
        "status": "success",
    }

    # ── Step 2: Generate report ──
    from app.services.ai_service import ai_service

    try:
        report = await ai_service.generate_journalist_report(article_dicts, category, region)
        if "error" in report:
            pipeline_result["errors"].append(f"Report: {report['error']}")
            pipeline_result["steps"]["report"] = {"status": "failed", "error": report["error"]}
        else:
            pipeline_result["steps"]["report"] = {
                "status": "success",
                "headline": report.get("headline", ""),
                "risk_level": report.get("risk_level", ""),
            }
    except Exception as e:
        pipeline_result["errors"].append(f"Report: {str(e)}")
        pipeline_result["steps"]["report"] = {"status": "failed"}
        return pipeline_result

    # ── Step 3: Generate audio ──
    from app.services.tts_service import tts_service

    narration_text = report.get("executive_summary", "")
    if isinstance(narration_text, dict):
        narration_text = " ".join(str(v) for v in narration_text.values())

    try:
        audio_result = await tts_service.generate_audio(narration_text, voice_id)
        if "error" in audio_result:
            pipeline_result["errors"].append(f"Audio: {audio_result['error']}")
            pipeline_result["steps"]["audio"] = {"status": "failed"}
        else:
            pipeline_result["steps"]["audio"] = {
                "status": "success",
                "url": audio_result["url"],
                "duration": audio_result["duration_seconds"],
                "engine": audio_result["engine"],
            }
    except Exception as e:
        pipeline_result["errors"].append(f"Audio: {str(e)}")
        pipeline_result["steps"]["audio"] = {"status": "failed"}

    # ── Step 4: Generate short clip with AI B-roll ──
    if generate_short and "audio" in pipeline_result["steps"] and pipeline_result["steps"]["audio"].get("status") == "success":
        from app.services.video_service import video_render_service
        
        # 4.1 Generate matching images for B-roll
        image_paths = []
        try:
            image_prompts = await ai_service.generate_image_prompts(report.get("executive_summary", ""))
            for i, p in enumerate(image_prompts[:3]): # Max 3 images for speed
                img_filename = f"broll_{uuid.uuid4().hex[:8]}.png"
                img_path = os.path.join(settings.VIDEO_OUTPUT_DIR, "thumbnails", img_filename)
                path = await ai_service.generate_image(p, img_path)
                if path:
                    image_paths.append(path)
        except Exception as e:
            logger.error(f"Image generation failed: {e}")

        try:
            short_result = await video_render_service.render_short_clip(
                audio_path=audio_result["path"],
                headline=report.get("headline", category),
                script_text=narration_text,
                image_paths=image_paths
            )
            if "error" in short_result:
                pipeline_result["errors"].append(f"Short clip: {short_result['error']}")
                pipeline_result["steps"]["short_clip"] = {"status": "failed"}
            else:
                pipeline_result["steps"]["short_clip"] = {
                    "status": "success",
                    "url": short_result["url"],
                    "duration": short_result["duration_seconds"],
                    "resolution": short_result["resolution"],
                }
        except Exception as e:
            pipeline_result["errors"].append(f"Short clip: {str(e)}")
            pipeline_result["steps"]["short_clip"] = {"status": "failed"}

    # ── Step 5: Generate presenter video ──
    if generate_presenter and "audio" in pipeline_result["steps"] and pipeline_result["steps"]["audio"].get("status") == "success":
        from app.services.avatar_service import avatar_service

        try:
            avatar_result = await avatar_service.generate_lipsync(
                audio_url=audio_result.get("url", ""),
            )
            if "error" in avatar_result:
                if avatar_result.get("fallback"):
                    pipeline_result["steps"]["presenter_video"] = {
                        "status": "skipped",
                        "reason": "No avatar API configured",
                    }
                else:
                    pipeline_result["errors"].append(f"Avatar: {avatar_result['error']}")
                    pipeline_result["steps"]["presenter_video"] = {"status": "failed"}
            else:
                # Composite the presenter video
                from app.services.video_service import video_render_service

                presenter_result = await video_render_service.render_presenter_video(
                    audio_path=audio_result["path"],
                    avatar_video_path=avatar_result["path"],
                    headline=report.get("headline", ""),
                    lower_third_text=f"STRATEGIC CONTEXT | {category.upper()}",
                )
                if "error" in presenter_result:
                    pipeline_result["errors"].append(f"Presenter: {presenter_result['error']}")
                    pipeline_result["steps"]["presenter_video"] = {"status": "failed"}
                else:
                    pipeline_result["steps"]["presenter_video"] = {
                        "status": "success",
                        "url": presenter_result["url"],
                        "duration": presenter_result["duration_seconds"],
                    }
        except Exception as e:
            pipeline_result["errors"].append(f"Presenter: {str(e)}")
            pipeline_result["steps"]["presenter_video"] = {"status": "failed"}

    # ── Step 6: Distribution ──
    if distribute_to and (pipeline_result["steps"].get("short_clip", {}).get("status") == "success" or 
                          pipeline_result["steps"].get("presenter_video", {}).get("status") == "success"):
        from app.services.social_distributor import social_distributor
        
        # Decide which video to distribute (favor presenter if it exists)
        video_url = pipeline_result["steps"].get("presenter_video", {}).get("url") or \
                    pipeline_result["steps"].get("short_clip", {}).get("url")
        
        if video_url:
            # We need the local path for distribution services
            video_path = video_url.replace("/output/", settings.VIDEO_OUTPUT_DIR + "/")
            
            try:
                dist_params = {
                    "video_path": video_path,
                    "title": report.get("headline", f"{category} Intelligence Update"),
                    "description": report.get("executive_summary", "")[:1000]
                }
                dist_results = await social_distributor.distribute("video", distribute_to, dist_params)
                pipeline_result["steps"]["distribution"] = {
                    "status": "success",
                    "results": dist_results
                }
            except Exception as e:
                pipeline_result["errors"].append(f"Distribution: {str(e)}")
                pipeline_result["steps"]["distribution"] = {"status": "failed", "error": str(e)}

    # ── Summary ──
    total_steps = len(pipeline_result["steps"])
    success_steps = sum(1 for s in pipeline_result["steps"].values() if s.get("status") == "success")
    pipeline_result["summary"] = {
        "total_steps": total_steps,
        "successful": success_steps,
        "failed": total_steps - success_steps,
        "overall_status": "success" if not pipeline_result["errors"] else "partial" if success_steps > 0 else "failed",
    }

    return pipeline_result


@router.get("/status")
async def get_pipeline_status(
    current_user=Depends(get_current_active_user),
):
    """Get overall pipeline status and capabilities."""
    from app.core.config import settings

    return {
        "ai_configured": bool(settings.GEMINI_API_KEY),
        "tts_engine": settings.TTS_ENGINE,
        "tts_configured": bool(settings.ELEVENLABS_API_KEY) or settings.TTS_ENGINE == "gtts",
        "avatar_engine": getattr(settings, "AVATAR_ENGINE", "none"),
        "avatar_configured": bool(getattr(settings, "DID_API_KEY", None)) or bool(getattr(settings, "HEYGEN_API_KEY", None)),
        "video_output_dir": settings.VIDEO_OUTPUT_DIR,
    }
