"""
Analytics & Monitoring Endpoints
Serves data for the Advanced Analytics & Monitoring UI.
Includes RAG memory stats and local AI service health capabilities.
"""
from typing import Any, Dict, List
import logging
import httpx
import os

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.profile import Profile
from app.core.config import settings
from app.utils.path_utils import resolve_sadtalker_dir, running_in_docker, is_windows_style_path

try:
    from app.services.rag_service import rag_service
    _rag_available = True
except ImportError:
    _rag_available = False

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/rag", response_model=List[Dict[str, Any]])
async def get_rag_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get RAG memory stats for all profiles."""
    if not _rag_available:
        return []

    # Get all profiles
    result = await db.execute(select(Profile))
    profiles = result.scalars().all()

    stats_list = []
    for profile in profiles:
        try:
            stats = await rag_service.get_memory_stats(str(profile.id))
            stats["profile_name"] = profile.name
            stats_list.append(stats)
        except Exception as e:
            logger.error(f"Failed to get RAG stats for profile {profile.id}: {e}")
            stats_list.append({
                "profile_id": str(profile.id),
                "profile_name": profile.name,
                "total_memories": 0,
                "error": str(e)
            })

    return stats_list


@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_stats(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get performance and health status of local AI services."""
    import shutil
    import subprocess

    try:
        stats = {
            "local": {
                "ollama": {"status": "unknown", "latency_ms": 0, "model": settings.OLLAMA_MODEL},
                "sd_next": {"status": "unknown", "latency_ms": 0, "url": settings.STABLE_DIFFUSION_URL},
                "sadtalker": {"status": "unknown", "path": settings.SADTALKER_DIR},
                "ffmpeg": {"status": "unknown", "version": "unknown"},
            },
            "cloud": {
                "gemini": {"status": "configured" if settings.GEMINI_API_KEY else "missing_key", "model": settings.LLM_MODEL},
                "elevenlabs": {"status": "configured" if settings.ELEVENLABS_API_KEY else "missing_key"},
                "did": {"status": "configured" if getattr(settings, "DID_API_KEY", None) else "missing_key"},
                "heygen": {"status": "configured" if getattr(settings, "HEYGEN_API_KEY", None) else "missing_key"},
            },
            "engine": settings.AI_PROVIDER
        }

        # Check Ollama
        try:
            url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags"
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    stats["local"]["ollama"]["status"] = "online"
                    stats["local"]["ollama"]["latency_ms"] = int(resp.elapsed.total_seconds() * 1000)
                else:
                    stats["local"]["ollama"]["status"] = "error"
        except Exception:
            stats["local"]["ollama"]["status"] = "offline"

        # Check SD.Next
        try:
            url = f"{settings.STABLE_DIFFUSION_URL.rstrip('/')}/sdapi/v1/progress"
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    stats["local"]["sd_next"]["status"] = "online"
                    stats["local"]["sd_next"]["latency_ms"] = int(resp.elapsed.total_seconds() * 1000)
                else:
                    stats["local"]["sd_next"]["status"] = "error"
        except Exception:
            stats["local"]["sd_next"]["status"] = "offline"

        # Check FFmpeg
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            try:
                version_out = subprocess.check_output(["ffmpeg", "-version"], text=True, stderr=subprocess.STDOUT)
                first_line = version_out.split('\n')[0]
                stats["local"]["ffmpeg"]["status"] = "online"
                stats["local"]["ffmpeg"]["version"] = first_line.split('version')[-1].split('Copyright')[0].strip()
            except Exception:
                stats["local"]["ffmpeg"]["status"] = "error"
        else:
            stats["local"]["ffmpeg"]["status"] = "missing"

        # Check SadTalker
        if settings.AVATAR_ENGINE == "local":
            resolved_dir, override_used, windows_path = resolve_sadtalker_dir(
                settings.SADTALKER_DIR,
                settings.SADTALKER_DOCKER_PATH
            )
            docker_active = running_in_docker()
            sadtalker_entry = stats["local"]["sadtalker"]

            inference_script = os.path.join(resolved_dir, "inference.py")
            inference_exists = os.path.exists(inference_script)

            if docker_active and windows_path and not override_used and not inference_exists:
                sadtalker_entry["status"] = "path_mismatch"
                sadtalker_entry["warning"] = (
                    f"Windows path detected while running in Docker. Mount SadTalker to "
                    f"{settings.SADTALKER_DOCKER_PATH} or set SADTALKER_DOCKER_PATH in .env."
                )
            elif inference_exists:
                sadtalker_entry["status"] = "available"
                if override_used:
                    sadtalker_entry["warning"] = f"Resolved SadTalker path to {resolved_dir} inside Docker."
            else:
                sadtalker_entry["status"] = "missing"
                if override_used:
                    sadtalker_entry["warning"] = f"Tried {resolved_dir} inside Docker but inference.py was not found."
        else:
            stats["local"]["sadtalker"]["status"] = f"disabled (using {settings.AVATAR_ENGINE})"

        return stats

    except Exception as e:
        logger.error(f"Performance stats endpoint error: {e}")
        return {
            "local": {
                "ollama": {"status": "error", "latency_ms": 0, "model": "unknown"},
                "sd_next": {"status": "error", "latency_ms": 0},
                "sadtalker": {"status": "error", "path": "unknown"},
                "ffmpeg": {"status": "error", "version": "unknown"},
            },
            "cloud": {},
            "engine": "unknown",
            "error": str(e)
        }


@router.get("/distribution", response_model=Dict[str, Any])
async def get_distribution_stats(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get high-level distribution integration status."""
    return {
        "telegram": bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID),
        "youtube": bool(settings.YOUTUBE_CLIENT_ID and settings.YOUTUBE_CLIENT_SECRET),
        "twitter": bool(settings.TWITTER_API_KEY and settings.TWITTER_ACCESS_TOKEN),
        "discord": bool(settings.DISCORD_WEBHOOK_URL)
    }
