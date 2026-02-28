"""
Weekly Briefs API Endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.brief import WeeklyBrief
from app.models.user import User, UserRole
from app.api.v1.endpoints.auth import get_current_active_user, require_role

router = APIRouter()


@router.get("/")
async def list_briefs(
    year: Optional[int] = None,
    is_published: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List weekly briefs."""
    query = select(WeeklyBrief)
    
    if year:
        query = query.where(WeeklyBrief.year == year)
    if is_published is not None:
        query = query.where(WeeklyBrief.is_published == (1 if is_published else 0))
    
    query = query.order_by(desc(WeeklyBrief.created_at))
    
    result = await db.execute(query)
    briefs = result.scalars().all()
    
    return [brief.to_dict() for brief in briefs]


@router.get("/{brief_id}")
async def get_brief(
    brief_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get brief details."""
    result = await db.execute(
        select(WeeklyBrief).where(WeeklyBrief.id == brief_id)
    )
    brief = result.scalar_one_or_none()
    
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    return {
        **brief.to_dict(),
        "executive_summary": brief.executive_summary,
        "key_developments": brief.key_developments,
        "energy_watch": brief.energy_watch,
        "stakeholder_positions": brief.stakeholder_positions,
        "scenario_outlook": brief.scenarios,
        "indicators_to_watch": brief.indicators_to_watch,
        "methodology": brief.methodology,
        "html_content": brief.html_content,
    }


@router.post("/")
async def create_brief(
    week_number: int,
    year: int,
    eri_assessment_id: UUID,
    title: str,
    subtitle: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Create new weekly brief."""
    from app.models.eri import ERIAssessment
    
    # Get ERI assessment
    result = await db.execute(
        select(ERIAssessment).where(ERIAssessment.id == eri_assessment_id)
    )
    eri = result.scalar_one_or_none()
    
    if not eri:
        raise HTTPException(status_code=404, detail="ERI assessment not found")
    
    brief = WeeklyBrief(
        week_number=week_number,
        year=year,
        title=title,
        subtitle=subtitle or f"Escalation Assessment | Energy Outlook | Diplomatic Signals",
        eri_assessment_id=eri_assessment_id,
        eri_score=eri.overall_score,
        executive_summary={
            "what_changed": f"Escalation Risk Index at {eri.overall_score} ({eri.classification.value})",
            "what_is_stable": "Diplomatic channels remain open",
            "risk_increased": "Military activity showing elevated patterns" if eri.military_score > 60 else "Political rhetoric intensifying",
            "risk_decreased": "Economic indicators stabilizing",
            "military_activity": f"{eri.military_score}/100 - {'Elevated' if eri.military_score > 60 else 'Stable'}",
            "proxy_activity": f"{eri.proxy_score}/100 - {'Active' if eri.proxy_score > 60 else 'Isolated'}",
            "diplomatic_track": f"{eri.diplomatic_score}/100 - {'Stalled' if eri.diplomatic_score < 50 else 'Active'}",
        },
        key_developments=eri.key_developments or [],
        scenarios=eri.scenarios or [],
        indicators_to_watch=eri.indicators_to_watch or [],
        stakeholder_positions=eri.stakeholder_positions or [],
        created_by=current_user.id,
    )
    
    # Generate HTML
    brief.html_content = brief.generate_html()
    
    db.add(brief)
    await db.commit()
    await db.refresh(brief)
    
    return brief.to_dict()


@router.put("/{brief_id}")
async def update_brief(
    brief_id: UUID,
    title: Optional[str] = None,
    executive_summary: Optional[dict] = None,
    key_developments: Optional[List[dict]] = None,
    scenarios: Optional[List[dict]] = None,
    indicators_to_watch: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Update brief content."""
    result = await db.execute(
        select(WeeklyBrief).where(WeeklyBrief.id == brief_id)
    )
    brief = result.scalar_one_or_none()
    
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    if title:
        brief.title = title
    if executive_summary:
        brief.executive_summary = executive_summary
    if key_developments:
        brief.key_developments = key_developments
    if scenarios:
        brief.scenarios = scenarios
    if indicators_to_watch:
        brief.indicators_to_watch = indicators_to_watch
    
    # Regenerate HTML
    brief.html_content = brief.generate_html()
    
    await db.commit()
    await db.refresh(brief)
    
    return brief.to_dict()


@router.post("/{brief_id}/publish")
async def publish_brief(
    brief_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EDITOR_IN_CHIEF))
):
    """Publish weekly brief."""
    result = await db.execute(
        select(WeeklyBrief).where(WeeklyBrief.id == brief_id)
    )
    brief = result.scalar_one_or_none()
    
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    from datetime import datetime
    brief.is_published = 1
    brief.published_at = datetime.utcnow()
    brief.published_by = current_user.id
    
    await db.commit()
    
    return {"message": "Brief published successfully", "brief": brief.to_dict()}


@router.get("/{brief_id}/export/pdf")
async def export_brief_pdf(
    brief_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export brief as PDF."""
    result = await db.execute(
        select(WeeklyBrief).where(WeeklyBrief.id == brief_id)
    )
    brief = result.scalar_one_or_none()
    
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    # In production, this would generate actual PDF
    # For now, return HTML that can be printed to PDF
    return {
        "brief_id": str(brief_id),
        "html_content": brief.html_content,
        "message": "Use browser print to save as PDF",
    }
