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
from app.models.profile import Profile

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/run-full")
async def run_full_pipeline(
    category: str,
    region: str = "Global",
    voice_id: str = "default",
    profile_id: Optional[UUID] = None,
    generate_short: bool = True,
    generate_presenter: bool = True,
    distribute_to: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role(UserRole.JUNIOR_EDITOR)),
):
    """
    Run the complete pipeline for a category.
    """
    from app.services.pipeline_service import pipeline_service
    
    result = await pipeline_service.run_full_pipeline(
        db=db,
        category=category,
        region=region,
        profile_id=profile_id,
        voice_id=voice_id,
        generate_short=generate_short,
        generate_presenter=generate_presenter,
        distribute_to=distribute_to,
    )
    
    if "error" in result and not result.get("steps"):
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result


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
