"""
Contradictions API Endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.contradiction import Contradiction, ContradictionStatus
from app.api.v1.endpoints.auth import get_current_active_user, require_role
from app.models.user import UserRole

router = APIRouter()


@router.get("/")
async def list_contradictions(
    status: Optional[ContradictionStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List contradictions."""
    query = select(Contradiction)
    
    if status:
        query = query.where(Contradiction.status == status)
    
    query = query.order_by(desc(Contradiction.detected_at))
    
    result = await db.execute(query)
    contradictions = result.scalars().all()
    
    return [c.to_dict() for c in contradictions]


@router.get("/{contradiction_id}")
async def get_contradiction(
    contradiction_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get contradiction details."""
    result = await db.execute(
        select(Contradiction).where(Contradiction.id == contradiction_id)
    )
    contradiction = result.scalar_one_or_none()
    
    if not contradiction:
        raise HTTPException(status_code=404, detail="Contradiction not found")
    
    return contradiction.to_dict()


@router.put("/{contradiction_id}/resolve")
async def resolve_contradiction(
    contradiction_id: UUID,
    correct_claim_id: Optional[UUID] = None,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Resolve contradiction."""
    result = await db.execute(
        select(Contradiction).where(Contradiction.id == contradiction_id)
    )
    contradiction = result.scalar_one_or_none()
    
    if not contradiction:
        raise HTTPException(status_code=404, detail="Contradiction not found")
    
    from datetime import datetime
    contradiction.status = ContradictionStatus.RESOLVED
    contradiction.resolved_by = current_user.id
    contradiction.resolved_at = datetime.utcnow()
    contradiction.resolution_notes = notes
    if correct_claim_id:
        contradiction.correct_claim_id = correct_claim_id
    
    await db.commit()
    
    return contradiction.to_dict()
