"""
Profile Management API
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.profile import Profile
from app.api.v1.endpoints.auth import get_current_active_user, require_role
from app.models.user import UserRole

router = APIRouter()


@router.get("/")
async def list_profiles(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all content profiles."""
    result = await db.execute(select(Profile).order_by(desc(Profile.created_at)))
    profiles = result.scalars().all()
    return [p.to_dict() for p in profiles]


@router.post("/")
async def create_profile(
    name: str,
    description: Optional[str] = None,
    voice_engine: str = "edge-tts",
    voice_id: Optional[str] = None,
    video_style: dict = {},
    platform_configs: dict = {},
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Create a new content profile."""
    profile = Profile(
        name=name,
        description=description,
        voice_engine=voice_engine,
        voice_id=voice_id,
        video_style=video_style,
        platform_configs=platform_configs,
        created_by=current_user.id
    )
    db.add(profile)
    try:
        await db.commit()
        await db.refresh(profile)
        return profile.to_dict()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{profile_id}")
async def get_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get profile details."""
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile.to_dict()


@router.patch("/{profile_id}")
async def update_profile(
    profile_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    voice_engine: Optional[str] = None,
    voice_id: Optional[str] = None,
    video_style: Optional[dict] = None,
    platform_configs: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Update profile settings."""
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if name is not None: profile.name = name
    if description is not None: profile.description = description
    if voice_engine is not None: profile.voice_engine = voice_engine
    if voice_id is not None: profile.voice_id = voice_id
    if video_style is not None: profile.video_style = video_style
    if platform_configs is not None: profile.platform_configs = platform_configs
    
    await db.commit()
    await db.refresh(profile)
    return profile.to_dict()


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.ADMIN))
):
    """Delete profile."""
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    await db.delete(profile)
    await db.commit()
    return {"message": "Profile deleted"}
