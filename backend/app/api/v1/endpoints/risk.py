"""
Risk Assessment API Endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.risk import RiskScore
from app.models.user import User, UserRole
from app.api.v1.endpoints.auth import get_current_active_user, require_role
from app.core.config import settings
from app.services.risk_service import risk_service

router = APIRouter()


@router.get("/")
async def list_risk_assessments(
    article_id: Optional[UUID] = None,
    min_score: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List risk assessments."""
    query = select(RiskScore)
    
    if article_id:
        query = query.where(RiskScore.article_id == article_id)
    if min_score:
        query = query.where(RiskScore.overall_score >= min_score)
    
    query = query.order_by(desc(RiskScore.created_at))
    
    result = await db.execute(query)
    assessments = result.scalars().all()
    
    return [assessment.to_dict() for assessment in assessments]


@router.get("/{assessment_id}")
async def get_risk_assessment(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get risk assessment details."""
    result = await db.execute(
        select(RiskScore).where(RiskScore.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Risk assessment not found")
    
    return assessment.to_dict()


@router.post("/assess/{article_id}")
async def assess_article_risk(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.JUNIOR_EDITOR))
):
    """Run risk assessment on article."""
    from app.models.article import NormalizedArticle
    
    result = await db.execute(
        select(NormalizedArticle).where(NormalizedArticle.id == article_id)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    assessment = await risk_service.assess_article(
        article=article,
        assessed_by=str(current_user.id),
        db=db,
        safe_mode_enabled=settings.SAFE_MODE_ENABLED,
    )

    return assessment.to_dict()


@router.post("/{assessment_id}/approve")
async def approve_risk_assessment(
    assessment_id: UUID,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Approve risk assessment."""
    result = await db.execute(
        select(RiskScore).where(RiskScore.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Risk assessment not found")
    
    # Check if user can approve this risk level
    if not current_user.can_approve_risk(assessment.overall_score) and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail=f"Requires approval level for risk score {assessment.overall_score}"
        )
    
    from datetime import datetime
    assessment.approved_by = current_user.id
    assessment.approved_at = datetime.utcnow()
    assessment.approval_notes = notes
    
    await db.commit()
    
    return assessment.to_dict()


@router.get("/config/safe-mode")
async def get_safe_mode_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get Safe Mode status."""
    return {
        "enabled": settings.SAFE_MODE_ENABLED,
        "threshold": settings.RISK_THRESHOLD,
    }


@router.put("/config/safe-mode")
async def toggle_safe_mode(
    enabled: bool,
    current_user: User = Depends(require_role(UserRole.EDITOR_IN_CHIEF))
):
    """Toggle Safe Mode (Editor in Chief only)."""
    settings.SAFE_MODE_ENABLED = enabled
    return {"enabled": enabled, "message": f"Safe Mode {'enabled' if enabled else 'disabled'}"}
