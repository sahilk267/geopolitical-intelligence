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
            stats["persona_type"] = profile.persona_type
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
    stats = {
        "ollama": {"status": "unknown", "latency_ms": 0, "model": settings.OLLAMA_MODEL},
        "sd_next": {"status": "unknown", "latency_ms": 0, "url": settings.STABLE_DIFFUSION_URL},
        "sadtalker": {"status": "unknown", "path": settings.SADTALKER_DIR},
        "engine": settings.AI_PROVIDER
    }

    # Check Ollama
    try:
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags"
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                stats["ollama"]["status"] = "online"
                stats["ollama"]["latency_ms"] = int(resp.elapsed.total_seconds() * 1000)
            else:
                stats["ollama"]["status"] = "error"
    except Exception:
        stats["ollama"]["status"] = "offline"

    # Check SD.Next
    try:
        url = f"{settings.STABLE_DIFFUSION_URL.rstrip('/')}/sdapi/v1/progress"
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                stats["sd_next"]["status"] = "online"
                stats["sd_next"]["latency_ms"] = int(resp.elapsed.total_seconds() * 1000)
            else:
                stats["sd_next"]["status"] = "error"
    except Exception:
        stats["sd_next"]["status"] = "offline"

    # Check SadTalker
    if settings.AVATAR_ENGINE == "local":
        inference_script = os.path.join(settings.SADTALKER_DIR, "inference.py")
        if os.path.exists(inference_script):
            stats["sadtalker"]["status"] = "available"
        else:
            stats["sadtalker"]["status"] = "missing"
    else:
        stats["sadtalker"]["status"] = f"disabled (using {settings.AVATAR_ENGINE})"

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
