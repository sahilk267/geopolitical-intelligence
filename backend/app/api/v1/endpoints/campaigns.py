"""
Campaign Management API
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.campaign import Campaign
from app.api.v1.endpoints.auth import get_current_active_user, require_role
from app.models.user import UserRole

router = APIRouter()


@router.get("/")
async def list_campaigns(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all autonomous campaigns."""
    result = await db.execute(select(Campaign).order_by(desc(Campaign.created_at)))
    campaigns = result.scalars().all()
    return [c.to_dict() for c in campaigns]


from pydantic import BaseModel

class CampaignCreate(BaseModel):
    name: str
    profile_id: UUID
    description: Optional[str] = None
    categories: List[str] = []
    regions: List[str] = []
    schedule_type: str = "daily"
    schedule_config: dict = {}

@router.post("/")
async def create_campaign(
    campaign_in: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Create a new autonomous campaign."""
    # Verify profile exists
    from app.models.profile import Profile
    profile_result = await db.execute(select(Profile).where(Profile.id == campaign_in.profile_id))
    if not profile_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Profile not found")

    campaign = Campaign(
        name=campaign_in.name,
        profile_id=campaign_in.profile_id,
        description=campaign_in.description,
        categories=campaign_in.categories,
        regions=campaign_in.regions,
        schedule_type=campaign_in.schedule_type,
        schedule_config=campaign_in.schedule_config,
        created_by=current_user.id
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign.to_dict()


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get campaign details."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign.to_dict()


@router.patch("/{campaign_id}")
async def update_campaign(
    campaign_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    profile_id: Optional[UUID] = None,
    categories: Optional[List[str]] = None,
    regions: Optional[List[str]] = None,
    is_active: Optional[bool] = None,
    schedule_type: Optional[str] = None,
    schedule_config: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Update campaign settings."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if name is not None: campaign.name = name
    if description is not None: campaign.description = description
    if profile_id is not None: campaign.profile_id = profile_id
    if categories is not None: campaign.categories = categories
    if regions is not None: campaign.regions = regions
    if is_active is not None: campaign.is_active = is_active
    if schedule_type is not None: campaign.schedule_type = schedule_type
    if schedule_config is not None: campaign.schedule_config = schedule_config
    
    await db.commit()
    await db.refresh(campaign)
    return campaign.to_dict()


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.ADMIN))
):
    """Delete campaign."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    await db.delete(campaign)
    await db.commit()
    return {"message": "Campaign deleted"}


@router.post("/{campaign_id}/run")
async def trigger_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Manually trigger a campaign run."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    from app.services.pipeline_service import pipeline_service
    from datetime import datetime
    
    categories = campaign.categories or ["General"]
    results = []
    for cat in categories:
        res = await pipeline_service.run_full_pipeline(
            db=db,
            category=cat,
            profile_id=campaign.profile_id,
            generate_short=True,
            generate_presenter=True,
        )
        results.append(res)
    
    campaign.last_run_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Campaign triggered successfully", "results": results}
