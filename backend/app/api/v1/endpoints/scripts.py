"""
Script Generation API Endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.core.config import settings
from app.models.script import Script, ScriptStatus, ScriptLayer
from app.api.v1.endpoints.auth import get_current_active_user, require_role
from app.models.user import UserRole

router = APIRouter()


@router.get("/")
async def list_scripts(
    article_id: Optional[UUID] = None,
    status: Optional[ScriptStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List scripts."""
    query = select(Script)
    
    if article_id:
        query = query.where(Script.article_id == article_id)
    if status:
        query = query.where(Script.status == status)
    
    query = query.order_by(desc(Script.created_at))
    
    result = await db.execute(query)
    scripts = result.scalars().all()
    
    return [s.to_dict() for s in scripts]


@router.get("/{script_id}")
async def get_script(
    script_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get script details."""
    result = await db.execute(
        select(Script).where(Script.id == script_id)
    )
    script = result.scalar_one_or_none()
    
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    return {
        **script.to_dict(),
        "full_script": script.full_script,
        "segments": script.segments,
    }


@router.post("/generate/{article_id}")
async def generate_script(
    article_id: UUID,
    layers: List[ScriptLayer],
    target_duration: int = 600,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.JUNIOR_EDITOR))
):
    """Generate script from article using AI."""
    from app.models.article import NormalizedArticle
    
    result = await db.execute(
        select(NormalizedArticle).where(NormalizedArticle.id == article_id)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Generate script content using Gemini AI Service
    from app.services.ai_service import ai_service
    
    article_dict = article.to_dict()
    ai_result = await ai_service.generate_script(article_dict, [l.value for l in layers])
    
    if "error" in ai_result:
        raise HTTPException(status_code=500, detail=ai_result["error"])
        
    full_script = ai_result.get("full_script", "")
    segments = ai_result.get("segments", [])
    word_count = len(full_script.split())
    
    script = Script(
        article_id=article_id,
        title=article.headline,
        topic=article.topic,
        target_duration_seconds=target_duration,
        layers=[l.value for l in layers],
        segments=segments,
        full_script=full_script,
        word_count=word_count,
        estimated_duration_seconds=int(word_count / 150 * 60),  # 150 wpm
        ai_model=settings.LLM_MODEL,
        created_by=current_user.id,
    )
    
    db.add(script)
    await db.commit()
    await db.refresh(script)
    
    return script.to_dict()


@router.put("/{script_id}/approve")
async def approve_script(
    script_id: UUID,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Approve script."""
    result = await db.execute(
        select(Script).where(Script.id == script_id)
    )
    script = result.scalar_one_or_none()
    
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    from datetime import datetime
    script.status = ScriptStatus.APPROVED
    script.reviewed_by = current_user.id
    script.reviewed_at = datetime.utcnow()
    script.review_notes = notes
    
    await db.commit()
    
    return script.to_dict()
