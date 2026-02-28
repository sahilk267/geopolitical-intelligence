"""
Articles API Endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.article import NormalizedArticle, ArticleStatus
from app.models.user import User, UserRole
from app.api.v1.endpoints.auth import get_current_active_user, require_role

router = APIRouter()


@router.get("/")
async def list_articles(
    status: Optional[ArticleStatus] = None,
    region: Optional[str] = None,
    priority: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List normalized articles."""
    query = select(NormalizedArticle)
    
    if status:
        query = query.where(NormalizedArticle.status == status)
    if region:
        query = query.where(NormalizedArticle.region == region)
    if priority is not None:
        query = query.where(NormalizedArticle.priority == priority)
    if search:
        query = query.where(
            NormalizedArticle.headline.ilike(f"%{search}%") |
            NormalizedArticle.summary.ilike(f"%{search}%")
        )
    
    query = query.order_by(desc(NormalizedArticle.created_at))
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    return [article.to_dict() for article in articles]


@router.get("/{article_id}")
async def get_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get article details."""
    result = await db.execute(
        select(NormalizedArticle).where(NormalizedArticle.id == article_id)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return {
        **article.to_dict(),
        "content": article.content,
        "entities": [e.to_dict() for e in article.entities],
        "claims": [c.to_dict() for c in article.claims],
    }


@router.put("/{article_id}/status")
async def update_article_status(
    article_id: UUID,
    status: ArticleStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.JUNIOR_EDITOR))
):
    """Update article status."""
    result = await db.execute(
        select(NormalizedArticle).where(NormalizedArticle.id == article_id)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    article.status = status
    
    if status == ArticleStatus.PUBLISHED:
        from datetime import datetime
        article.published_at = datetime.utcnow()
        article.published_by = current_user.id
    
    await db.commit()
    
    return article.to_dict()


@router.put("/{article_id}/priority")
async def update_article_priority(
    article_id: UUID,
    priority: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Update article priority."""
    result = await db.execute(
        select(NormalizedArticle).where(NormalizedArticle.id == article_id)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    article.priority = priority
    await db.commit()
    
    return article.to_dict()
@router.post("/process/{raw_article_id}")
async def process_raw_article(
    raw_article_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.JUNIOR_EDITOR))
):
    """Normalize raw article using Gemini AI."""
    from app.models.article import RawArticle, NormalizedArticle
    from app.services.ai_service import ai_service
    
    result = await db.execute(select(RawArticle).where(RawArticle.id == raw_article_id))
    raw_article = result.scalar_one_or_none()
    
    if not raw_article:
        raise HTTPException(status_code=404, detail="Raw article not found")
        
    # Summarize via Gemini
    summary = await ai_service.summarize_article(raw_article.title, raw_article.content)
    
    normalized = NormalizedArticle(
        raw_article_id=raw_article_id,
        headline=raw_article.title,
        content=raw_article.content,
        summary=summary,
        category=raw_article.category or "General",
        region=raw_article.region or "Global",
        status=ArticleStatus.DRAFT,
        created_by=current_user.id
    )
    
    db.add(normalized)
    await db.commit()
    await db.refresh(normalized)
    
    return normalized.to_dict()
