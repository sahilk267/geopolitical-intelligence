"""
Risk Assessment API Endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.risk import RiskScore, RiskDimension
from app.models.user import User, UserRole
from app.api.v1.endpoints.auth import get_current_active_user, require_role
from app.core.config import settings

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
    
    # Analyze article content for risk factors
    content = (article.headline + " " + (article.summary or "")).lower()
    
    risk_factors = {
        "named_individual": any(word in content for word in ["president", "minister", "leader", "mr.", "dr."]),
        "criminal_allegation": any(word in content for word in ["guilty", "crime", "corruption", "fraud"]),
        "single_anonymous_source": "anonymous" in content or "unnamed" in content,
        "war_topic": any(word in content for word in ["war", "attack", "strike", "military"]),
        "religious_framing": any(word in content for word in ["muslim", "islamic", "christian", "jewish"]),
        "israel_mentioned": "israel" in content,
        "iran_mentioned": "iran" in content,
        "palestine_mentioned": "palestine" in content,
    }
    
    # Calculate dimension scores
    legal_risk = 0
    defamation_risk = 0
    platform_risk = 0
    political_risk = 0
    
    if risk_factors["named_individual"]:
        legal_risk += 15
        defamation_risk += 20
        platform_risk += 10
        political_risk += 10
    
    if risk_factors["criminal_allegation"]:
        legal_risk += 25
        defamation_risk += 30
        platform_risk += 20
        political_risk += 15
    
    if risk_factors["single_anonymous_source"]:
        legal_risk += 20
        defamation_risk += 25
        platform_risk += 15
    
    if risk_factors["war_topic"]:
        platform_risk += 25
        political_risk += 20
    
    if risk_factors["religious_framing"]:
        platform_risk += 30
        political_risk += 20
    
    if risk_factors["israel_mentioned"] or risk_factors["iran_mentioned"] or risk_factors["palestine_mentioned"]:
        political_risk += 15
    
    # Cap scores at 100
    legal_risk = min(legal_risk, 100)
    defamation_risk = min(defamation_risk, 100)
    platform_risk = min(platform_risk, 100)
    political_risk = min(political_risk, 100)
    
    # Calculate overall
    overall = round(
        legal_risk * 0.30 +
        defamation_risk * 0.30 +
        platform_risk * 0.20 +
        political_risk * 0.20
    )
    
    # Check safe mode
    safe_mode_blocked = False
    safe_mode_violations = []
    
    if settings.SAFE_MODE_ENABLED:
        if risk_factors["criminal_allegation"]:
            safe_mode_blocked = True
            safe_mode_violations.append("Criminal allegations not allowed in Safe Mode")
        if risk_factors["war_topic"]:
            safe_mode_blocked = True
            safe_mode_violations.append("Active conflict analysis restricted in Safe Mode")
    
    # Create risk assessment
    assessment = RiskScore(
        article_id=article_id,
        legal_risk=legal_risk,
        defamation_risk=defamation_risk,
        platform_risk=platform_risk,
        political_risk=political_risk,
        overall_score=overall,
        classification="Critical" if overall > 80 else "High" if overall > 60 else "Elevated" if overall > 40 else "Moderate" if overall > 20 else "Low",
        risk_factors=risk_factors,
        safe_mode_blocked=safe_mode_blocked,
        safe_mode_violations=safe_mode_violations if safe_mode_violations else None,
        requires_senior_review=overall > 40,
        assessed_by=current_user.id,
    )
    
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    
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
