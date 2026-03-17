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
from pydantic import BaseModel

class GenerateFromUrlRequest(BaseModel):
    url: str
    topic: Optional[str] = None
    region: Optional[str] = None

class ArticleCreate(BaseModel):
    headline: str
    content: str
    summary: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    topics: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    priority: Optional[int] = 0

router = APIRouter()


@router.post("/", response_model=dict)
async def create_article(
    article_in: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.JUNIOR_EDITOR))
):
    """Create a new normalized article manually."""
    db_article = NormalizedArticle(
        headline=article_in.headline,
        content=article_in.content,
        summary=article_in.summary or article_in.content[:200] + "...",
        category=article_in.category or "General",
        region=article_in.region or "Global",
        topics=article_in.topics or [],
        tags=article_in.tags or [],
        priority=article_in.priority or 0,
        status=ArticleStatus.DRAFT,
    )
    
    db.add(db_article)
    await db.commit()
    await db.refresh(db_article)
    
    # Pre-generate dictionary to avoid lazy loading issues during serialization
    article_dict = {
        "id": str(db_article.id),
        "headline": db_article.headline,
        "summary": db_article.summary,
        "category": db_article.category,
        "region": db_article.region,
        "status": db_article.status.value,
        "priority": db_article.priority,
        "createdAt": db_article.created_at.isoformat() if db_article.created_at else None
    }
    
    return article_dict


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


@router.delete("/cleanup/all")
async def cleanup_articles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Delete all normalized articles (Admin only)."""
    from sqlalchemy import delete
    
    await db.execute(delete(NormalizedArticle))
    await db.commit()
    
    return {"message": "All normalized articles cleared"}
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
    )
    
    db.add(normalized)
    await db.commit()
    await db.refresh(normalized)
    
    return normalized.to_dict()


@router.post("/generate-from-url")
async def generate_from_url(
    request: GenerateFromUrlRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Fetch content from URL and generate initial draft using AI."""
    from app.services.ai_service import ai_service
    
    # Scrape content
    scraped = await ai_service.get_content_from_url(request.url)
    if "error" in scraped:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {scraped['error']}")
        
    headline = scraped["headline"]
    content = scraped["content"]
    
    # Summarize
    summary = await ai_service.summarize_article(headline, content)
    
    return {
        "headline": headline,
        "content": content,
        "summary": summary,
        "topic": request.topic or "Strategic Analysis",
        "region": request.region or "Global"
    }
