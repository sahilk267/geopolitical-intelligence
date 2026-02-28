"""
Dashboard API Endpoints
"""
from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta

from app.db.base import get_db
from app.models.source import Source
from app.models.article import RawArticle, NormalizedArticle, ArticleStatus
from app.models.risk import RiskScore
from app.models.eri import ERIAssessment
from app.models.audit import AuditLog, AuditAction
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard statistics."""
    # Source stats
    sources_result = await db.execute(select(Source))
    sources = sources_result.scalars().all()
    
    total_sources = len(sources)
    active_sources = sum(1 for s in sources if s.is_enabled)
    error_sources = sum(1 for s in sources if s.last_fetch_status == "error")
    total_items_fetched = sum(s.items_fetched for s in sources)
    
    # Article stats
    articles_result = await db.execute(select(NormalizedArticle))
    articles = articles_result.scalars().all()
    
    total_articles = len(articles)
    pending_review = sum(1 for a in articles if a.status == ArticleStatus.PENDING_REVIEW)
    published = sum(1 for a in articles if a.status == ArticleStatus.PUBLISHED)
    flagged = sum(1 for a in articles if a.status == ArticleStatus.FLAGGED)
    
    # Risk stats
    risk_result = await db.execute(select(RiskScore))
    risk_scores = risk_result.scalars().all()
    
    avg_risk = sum(r.overall_score for r in risk_scores) / len(risk_scores) if risk_scores else 0
    high_risk = sum(1 for r in risk_scores if r.overall_score > 60)
    blocked_by_safe_mode = sum(1 for r in risk_scores if r.safe_mode_blocked)
    
    # Latest ERI
    eri_result = await db.execute(
        select(ERIAssessment).order_by(desc(ERIAssessment.created_at)).limit(1)
    )
    latest_eri = eri_result.scalar_one_or_none()
    
    # Recent activity
    recent_logs_result = await db.execute(
        select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(10)
    )
    recent_logs = recent_logs_result.scalars().all()
    
    return {
        "sources": {
            "total": total_sources,
            "active": active_sources,
            "error": error_sources,
            "items_fetched": total_items_fetched,
        },
        "articles": {
            "total": total_articles,
            "pending_review": pending_review,
            "published": published,
            "flagged": flagged,
        },
        "risk": {
            "average_score": round(avg_risk, 1),
            "high_risk_count": high_risk,
            "blocked_by_safe_mode": blocked_by_safe_mode,
        },
        "eri": {
            "current_score": latest_eri.overall_score if latest_eri else None,
            "classification": latest_eri.classification.value if latest_eri else None,
            "week": latest_eri.week_number if latest_eri else None,
        },
        "recent_activity": [log.to_dict() for log in recent_logs],
    }


@router.get("/eri-history")
async def get_eri_history(
    weeks: int = 12,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get ERI history for charts."""
    result = await db.execute(
        select(ERIAssessment)
        .order_by(desc(ERIAssessment.created_at))
        .limit(weeks)
    )
    assessments = result.scalars().all()
    
    return [
        {
            "week": f"W{a.week_number}",
            "year": a.year,
            "score": a.overall_score,
            "classification": a.classification.value,
            "dimensions": {
                "military": a.military_score,
                "political": a.political_score,
                "proxy": a.proxy_score,
                "economic": a.economic_score,
                "diplomatic": a.diplomatic_score,
            },
        }
        for a in reversed(assessments)
    ]


@router.get("/source-health")
async def get_source_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get source health status."""
    result = await db.execute(select(Source).where(Source.is_enabled == True))
    sources = result.scalars().all()
    
    return {
        "overall": "healthy" if sum(1 for s in sources if s.last_fetch_status == "error") < len(sources) / 3 else "degraded",
        "sources": [
            {
                "id": str(s.id),
                "name": s.name,
                "status": "error" if s.last_fetch_status == "error" else "up",
                "last_fetch": s.last_fetch_at.isoformat() if s.last_fetch_at else None,
                "success_rate": round(s.get_success_rate(), 1),
                "response_time": s.average_response_time_ms,
            }
            for s in sources
        ],
    }


@router.get("/pipeline")
async def get_pipeline_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get content pipeline status."""
    result = await db.execute(select(NormalizedArticle))
    articles = result.scalars().all()
    
    pipeline = {
        "ingestion": sum(1 for a in articles if a.status == ArticleStatus.NEW),
        "review": sum(1 for a in articles if a.status == ArticleStatus.PENDING_REVIEW),
        "risk_assessment": sum(1 for a in articles if a.risk_score_id is None and a.status != ArticleStatus.NEW),
        "approved": sum(1 for a in articles if a.status == ArticleStatus.APPROVED),
        "published": sum(1 for a in articles if a.status == ArticleStatus.PUBLISHED),
    }
    
    return pipeline
