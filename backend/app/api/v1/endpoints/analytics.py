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
        async with httpx.AsyncClient(timeout=2.0) as client:
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
        async with httpx.AsyncClient(timeout=2.0) as client:
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
        # Check for path mismatch (Docker Linux vs Windows Host)
        sadtalker_dir = settings.SADTALKER_DIR
        is_docker = os.path.exists("/.dockerenv")
        
        if is_docker and (sadtalker_dir.startswith("C:") or sadtalker_dir.startswith("\\")):
             stats["local"]["sadtalker"]["status"] = "path_mismatch"
             stats["local"]["sadtalker"]["warning"] = "Windows path detected in Docker. Mount volume to /app/sadtalker."
        else:
            inference_script = os.path.join(sadtalker_dir, "inference.py")
            if os.path.exists(inference_script):
                stats["local"]["sadtalker"]["status"] = "available"
            else:
                stats["local"]["sadtalker"]["status"] = "missing"
    else:
        stats["local"]["sadtalker"]["status"] = f"disabled (using {settings.AVATAR_ENGINE})"

    return stats


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
