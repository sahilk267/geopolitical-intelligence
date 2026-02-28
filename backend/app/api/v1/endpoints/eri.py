"""
ERI (Escalation Risk Index) API Endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.eri import ERIAssessment, ERIClassification
from app.models.user import User, UserRole
from app.api.v1.endpoints.auth import get_current_active_user, require_role

router = APIRouter()


@router.get("/")
async def list_eri_assessments(
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List ERI assessments."""
    query = select(ERIAssessment)
    
    if year:
        query = query.where(ERIAssessment.year == year)
    
    query = query.order_by(desc(ERIAssessment.created_at))
    
    result = await db.execute(query)
    assessments = result.scalars().all()
    
    return [assessment.to_dict() for assessment in assessments]


@router.get("/current")
async def get_current_eri(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current/latest ERI assessment."""
    result = await db.execute(
        select(ERIAssessment).order_by(desc(ERIAssessment.created_at)).limit(1)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="No ERI assessment found")
    
    return assessment.to_dict()


@router.get("/{assessment_id}")
async def get_eri_assessment(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get ERI assessment details."""
    result = await db.execute(
        select(ERIAssessment).where(ERIAssessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="ERI assessment not found")
    
    return {
        **assessment.to_dict(),
        "key_developments": assessment.key_developments,
        "scenarios": assessment.scenarios,
        "indicators_to_watch": assessment.indicators_to_watch,
        "energy_watch": assessment.energy_watch,
        "stakeholder_positions": assessment.stakeholder_positions,
        "executive_summary": assessment.executive_summary,
    }


@router.post("/")
async def create_eri_assessment(
    week_number: int,
    year: int,
    military_score: int,
    political_score: int,
    proxy_score: int,
    economic_score: int,
    diplomatic_score: int,
    key_developments: Optional[List[dict]] = None,
    scenarios: Optional[List[dict]] = None,
    indicators_to_watch: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Create new ERI assessment."""
    # Calculate overall score
    weights = {
        "military": 0.30,
        "political": 0.15,
        "proxy": 0.20,
        "economic": 0.15,
        "diplomatic": 0.20,
    }
    
    overall = round(
        military_score * weights["military"] +
        political_score * weights["political"] +
        proxy_score * weights["proxy"] +
        economic_score * weights["economic"] +
        diplomatic_score * weights["diplomatic"]
    )
    
    # Determine classification
    if overall < 20:
        classification = ERIClassification.LOW
    elif overall < 40:
        classification = ERIClassification.MODERATE
    elif overall < 60:
        classification = ERIClassification.ELEVATED
    elif overall < 80:
        classification = ERIClassification.HIGH
    else:
        classification = ERIClassification.CRITICAL
    
    assessment = ERIAssessment(
        week_number=week_number,
        year=year,
        military_score=military_score,
        political_score=political_score,
        proxy_score=proxy_score,
        economic_score=economic_score,
        diplomatic_score=diplomatic_score,
        overall_score=overall,
        classification=classification,
        key_developments=key_developments or [],
        scenarios=scenarios or [],
        indicators_to_watch=indicators_to_watch or [],
        created_by=current_user.id,
    )
    
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    
    return assessment.to_dict()


@router.put("/{assessment_id}")
async def update_eri_assessment(
    assessment_id: UUID,
    military_score: Optional[int] = None,
    political_score: Optional[int] = None,
    proxy_score: Optional[int] = None,
    economic_score: Optional[int] = None,
    diplomatic_score: Optional[int] = None,
    key_developments: Optional[List[dict]] = None,
    scenarios: Optional[List[dict]] = None,
    indicators_to_watch: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Update ERI assessment."""
    result = await db.execute(
        select(ERIAssessment).where(ERIAssessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="ERI assessment not found")
    
    if military_score is not None:
        assessment.military_score = military_score
    if political_score is not None:
        assessment.political_score = political_score
    if proxy_score is not None:
        assessment.proxy_score = proxy_score
    if economic_score is not None:
        assessment.economic_score = economic_score
    if diplomatic_score is not None:
        assessment.diplomatic_score = diplomatic_score
    if key_developments is not None:
        assessment.key_developments = key_developments
    if scenarios is not None:
        assessment.scenarios = scenarios
    if indicators_to_watch is not None:
        assessment.indicators_to_watch = indicators_to_watch
    
    # Recalculate overall score
    assessment.overall_score = assessment.calculate_overall()
    assessment.classification = assessment.get_classification()
    
    await db.commit()
    await db.refresh(assessment)
    
    return assessment.to_dict()


@router.post("/{assessment_id}/publish")
async def publish_eri_assessment(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EDITOR_IN_CHIEF))
):
    """Publish ERI assessment."""
    result = await db.execute(
        select(ERIAssessment).where(ERIAssessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="ERI assessment not found")
    
    from datetime import datetime
    assessment.published_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "ERI assessment published", "assessment": assessment.to_dict()}
