"""
Report Generation API Endpoints
Generates journalist-quality intelligence reports from aggregated articles.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.article import RawArticle, NormalizedArticle
from app.api.v1.endpoints.auth import get_current_active_user, require_role
from app.models.user import UserRole
from app.services.ai_service import ai_service

router = APIRouter()


@router.post("/generate")
async def generate_report(
    category: str,
    region: str = "Global",
    max_articles: int = Query(default=10, le=20),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Generate a journalist-quality intelligence report for a given category.
    Aggregates recent articles and uses AI to produce a structured report.
    """
    # First try NormalizedArticles, fall back to RawArticles
    query = (
        select(NormalizedArticle)
        .where(NormalizedArticle.category == category)
        .order_by(desc(NormalizedArticle.created_at))
        .limit(max_articles)
    )
    result = await db.execute(query)
    articles = result.scalars().all()

    if not articles:
        # Fall back to raw articles
        query = (
            select(RawArticle)
            .where(RawArticle.category == category)
            .order_by(desc(RawArticle.fetched_at))
            .limit(max_articles)
        )
        result = await db.execute(query)
        articles = result.scalars().all()

    if not articles:
        raise HTTPException(
            status_code=404,
            detail=f"No articles found for category '{category}'. Fetch sources first.",
        )

    # Convert to dicts for AI service
    article_dicts = [a.to_dict() for a in articles]

    report = await ai_service.generate_journalist_report(article_dicts, category, region)

    if "error" in report:
        raise HTTPException(status_code=500, detail=report["error"])

    return {
        "category": category,
        "region": region,
        "articles_used": len(article_dicts),
        "report": report,
    }


@router.post("/generate-from-articles")
async def generate_report_from_articles(
    article_ids: List[UUID],
    category: str = "General",
    region: str = "Global",
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Generate a report from specific selected article IDs."""
    articles = []
    for aid in article_ids:
        result = await db.execute(
            select(NormalizedArticle).where(NormalizedArticle.id == aid)
        )
        article = result.scalar_one_or_none()
        if article:
            articles.append(article)

    if not articles:
        raise HTTPException(status_code=404, detail="No valid articles found for the given IDs.")

    article_dicts = [a.to_dict() for a in articles]
    report = await ai_service.generate_journalist_report(article_dicts, category, region)

    if "error" in report:
        raise HTTPException(status_code=500, detail=report["error"])

    return {
        "category": category,
        "region": region,
        "articles_used": len(article_dicts),
        "report": report,
    }


@router.post("/short-summary")
async def generate_short_summary(
    headline: str,
    content: str,
    current_user=Depends(get_current_active_user),
):
    """Generate a 30-second narration summary for short clips."""
    result = await ai_service.generate_short_summary(headline, content)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.get("/categories")
async def list_available_categories(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """List all categories that have articles available for report generation."""
    from sqlalchemy import func, distinct

    result = await db.execute(
        select(
            RawArticle.category,
            func.count(RawArticle.id).label("article_count"),
        )
        .where(RawArticle.category.isnot(None))
        .group_by(RawArticle.category)
        .order_by(desc(func.count(RawArticle.id)))
    )
    rows = result.all()

    return [
        {"category": row.category, "article_count": row.article_count}
        for row in rows
    ]
