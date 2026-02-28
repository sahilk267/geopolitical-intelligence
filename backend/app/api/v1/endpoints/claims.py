"""
Claims API Endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.claim import Claim, ClaimStatus
from app.api.v1.endpoints.auth import get_current_active_user, require_role
from app.models.user import UserRole

router = APIRouter()


@router.get("/")
async def list_claims(
    article_id: Optional[UUID] = None,
    status: Optional[ClaimStatus] = None,
    has_contradiction: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List claims."""
    query = select(Claim)
    
    if article_id:
        query = query.where(Claim.article_id == article_id)
    if status:
        query = query.where(Claim.status == status)
    if has_contradiction is not None:
        query = query.where(Claim.has_contradiction == has_contradiction)
    
    query = query.order_by(desc(Claim.extracted_at))
    
    result = await db.execute(query)
    claims = result.scalars().all()
    
    return [claim.to_dict() for claim in claims]


@router.get("/{claim_id}")
async def get_claim(
    claim_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get claim details."""
    result = await db.execute(
        select(Claim).where(Claim.id == claim_id)
    )
    claim = result.scalar_one_or_none()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    return {
        **claim.to_dict(),
        "contradictions": [c.to_dict() for c in claim.contradictions],
    }


@router.put("/{claim_id}/status")
async def update_claim_status(
    claim_id: UUID,
    status: ClaimStatus,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Update claim verification status."""
    result = await db.execute(
        select(Claim).where(Claim.id == claim_id)
    )
    claim = result.scalar_one_or_none()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    from datetime import datetime
    claim.status = status
    claim.verified_by = current_user.id
    claim.verified_at = datetime.utcnow()
    claim.verification_notes = notes
    
    await db.commit()
    
    return claim.to_dict()
