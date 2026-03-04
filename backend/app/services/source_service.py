"""
Service for Managing and Polling Data Sources
"""
import logging
import httpx
import feedparser
from datetime import datetime
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Source
from app.models.article import RawArticle
from app.core.config import settings

logger = logging.getLogger(__name__)

class SourceService:
    """Service for source management and polling."""
    
    async def fetch_from_source(self, source_id: UUID, db: AsyncSession) -> dict:
        """Fetch and process articles from a specific source."""
        result = await db.execute(select(Source).where(Source.id == source_id))
        source = result.scalar_one_or_none()
        
        if not source:
            return {"success": False, "error": "Source not found"}
        
        if not source.is_enabled:
            return {"success": False, "error": "Source is disabled"}
        
        try:
            logger.info(f"Fetching from source: {source.name} ({source.url})")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(source.url, timeout=settings.REQUEST_TIMEOUT_SECONDS)
                feed = feedparser.parse(response.text)
                
            items_found = 0
            for entry in feed.entries[:settings.MAX_ARTICLES_PER_FETCH]:
                # Check if article exists
                existing_result = await db.execute(
                    select(RawArticle).where(RawArticle.url == entry.link)
                )
                if existing_result.scalar_one_or_none():
                    continue
                    
                raw_article = RawArticle(
                    source_id=source_id,
                    title=entry.get('title', 'No Title'),
                    content=entry.get('summary', entry.get('description', '')),
                    url=entry.link,
                    published_at=datetime.utcnow(),
                    category=source.category,
                    region=source.region
                )
                db.add(raw_article)
                items_found += 1
                
            source.last_fetch_at = datetime.utcnow()
            source.last_fetch_status = "success"
            source.fetch_count += 1
            source.items_fetched += items_found
            source.success_count += 1
            
            await db.commit()
            return {"success": True, "items_fetched": items_found, "source": source.to_dict()}
            
        except Exception as e:
            logger.error(f"Fetch failed for {source.name}: {e}")
            source.last_fetch_status = "error"
            source.last_fetch_error = str(e)
            source.error_count += 1
            await db.commit()
            return {"success": False, "error": str(e), "source": source.to_dict()}

    async def fetch_by_category(self, category: str, db: AsyncSession) -> dict:
        """Fetch from all enabled sources in a specific category."""
        result = await db.execute(
            select(Source).where(Source.category == category, Source.is_enabled == True)
        )
        sources = result.scalars().all()
        
        results = []
        for source in sources:
            res = await self.fetch_from_source(source.id, db)
            results.append(res)
            
        return {
            "success": True,
            "category": category,
            "sources_processed": len(sources),
            "details": results
        }

    async def fetch_all_enabled(self, db: AsyncSession) -> dict:
        """Fetch from all enabled sources."""
        result = await db.execute(select(Source).where(Source.is_enabled == True))
        sources = result.scalars().all()
        
        results = []
        for source in sources:
            res = await self.fetch_from_source(source.id, db)
            results.append(res)
            
        return {
            "success": True,
            "total_sources": len(sources),
            "details": results
        }

source_service = SourceService()
