"""
Distribution API Endpoints
Endpoints for managing social media distribution and publishing content.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.v1.endpoints.auth import get_current_active_user, require_role
from app.models.user import UserRole
from app.services.social_distributor import social_distributor

router = APIRouter()

@router.get("/platforms")
async def list_platforms():
    """List all supported and connected platforms."""
    # This is a mock/placeholder until we have a proper registration system
    return [
        {"id": "telegram", "name": "Telegram", "connected": True if settings.TELEGRAM_BOT_TOKEN else False},
        {"id": "youtube", "name": "YouTube", "connected": False}, # Needs OAuth check
        {"id": "twitter", "name": "Twitter/X", "connected": False},
        {"id": "facebook", "name": "Facebook Page", "connected": False},
        {"id": "instagram", "name": "Instagram Reels", "connected": False},
        {"id": "linkedin", "name": "LinkedIn", "connected": False},
        {"id": "whatsapp", "name": "WhatsApp", "connected": False},
    ]

@router.post("/publish")
async def publish_content(
    content_type: str = Body(..., description="video, report, or summary"),
    platforms: List[str] = Body(..., description="List of platforms to post to"),
    params: Dict[str, Any] = Body(..., description="Media paths, titles, etc."),
    current_user=Depends(require_role(UserRole.EDITOR_IN_CHIEF)),
):
    """Publish content to selected platforms."""
    if not platforms:
        raise HTTPException(status_code=400, detail="No platforms selected")
    
    # If video_id is provided, resolve the path
    if content_type == "video" and "video_id" in params:
        from app.models.video import VideoJob
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(VideoJob).where(VideoJob.id == params["video_id"]))
            job = result.scalar_one_or_none()
            if job and job.output_path:
                params["video_path"] = job.output_path
            else:
                raise HTTPException(status_code=404, detail="Video job or output path not found")
    
    results = await social_distributor.distribute(content_type, platforms, params)
    return results

from app.db.base import AsyncSessionLocal

@router.post("/test/{platform}")
async def test_platform_connection(
    platform: str,
    current_user=Depends(require_role(UserRole.EDITOR_IN_CHIEF)),
):
    """Test connection to a specific platform."""
    if platform == "telegram":
        from app.services.platforms.telegram_service import telegram_service
        return await telegram_service.post_text("Test message from Geopolitical Intelligence Platform", "Test Connection")
    elif platform == "youtube":
        from app.services.platforms.youtube_service import youtube_service
        return await youtube_service.test_connection()
    
    raise HTTPException(status_code=400, detail=f"Platform '{platform}' test not implemented yet")

from app.core.config import settings
