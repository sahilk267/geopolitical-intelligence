"""
Data Sources API Endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.core.config import settings
from app.models.source import Source, SourceType, SourceTier
from app.models.user import User, UserRole
from app.api.v1.endpoints.auth import get_current_active_user, require_role

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_sources(
    status: Optional[str] = None,
    type: Optional[SourceType] = None,
    region: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all data sources."""
    query = select(Source)
    
    if status:
        query = query.where(Source.last_fetch_status == status)
    if type:
        query = query.where(Source.type == type)
    if region:
        query = query.where(Source.region == region)
    
    query = query.order_by(desc(Source.created_at))
    result = await db.execute(query)
    sources = result.scalars().all()
    
    return [source.to_dict() for source in sources]


@router.get("/{source_id}")
async def get_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get source details."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return source.to_dict()


@router.post("/")
async def create_source(
    name: str,
    url: str,
    type: SourceType,
    category: str,
    region: str,
    tier: SourceTier = SourceTier.UNVERIFIED,
    fetch_interval_minutes: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Create new data source."""
    source = Source(
        name=name,
        url=url,
        type=type,
        tier=tier,
        category=category,
        region=region,
        fetch_interval_minutes=fetch_interval_minutes,
        created_by=current_user.id,
    )
    
    db.add(source)
    await db.commit()
    await db.refresh(source)
    
    return source.to_dict()


@router.put("/{source_id}")
async def update_source(
    source_id: UUID,
    name: Optional[str] = None,
    url: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    fetch_interval_minutes: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Update data source."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    if name:
        source.name = name
    if url:
        source.url = url
    if is_enabled is not None:
        source.is_enabled = is_enabled
    if fetch_interval_minutes:
        source.fetch_interval_minutes = fetch_interval_minutes
    
    await db.commit()
    await db.refresh(source)
    
    return source.to_dict()


@router.delete("/{source_id}")
async def delete_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EDITOR_IN_CHIEF))
):
    """Delete data source."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    await db.delete(source)
    await db.commit()
    
    return {"message": "Source deleted successfully"}


@router.post("/{source_id}/test")
async def test_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Test data source connectivity."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Simulate test (in production, this would actually fetch)
    import asyncio
    import random
    
    await asyncio.sleep(1 + random.random())
    
    success = random.random() > 0.3
    
    # Update source stats
    source.last_fetch_status = "success" if success else "error"
    if not success:
        source.last_fetch_error = "Connection timeout or invalid response"
    source.fetch_count += 1
    if success:
        source.success_count += 1
    else:
        source.error_count += 1
    
    await db.commit()
    
    return {
        "success": success,
        "source": source.to_dict(),
        "response_time_ms": int(random.random() * 2000),
        "items_found": int(random.random() * 50) if success else 0,
    }


@router.post("/{source_id}/fetch")
async def fetch_from_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.JUNIOR_EDITOR))
):
    """Manually fetch from source."""
    from app.services.source_service import source_service
    result = await source_service.fetch_from_source(source_id, db)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    return result


@router.post("/fetch-all")
async def fetch_all_sources(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.JUNIOR_EDITOR))
):
    """Fetch from all enabled sources."""
    result = await db.execute(select(Source).where(Source.is_enabled == True))
    sources = result.scalars().all()
    
    results = []
    for source in sources:
        # Simulate fetch
        import asyncio
        import random
        
        await asyncio.sleep(0.5)
        
        success = random.random() > 0.2
        items_found = int(random.random() * 20) + 3 if success else 0
        
        from datetime import datetime
        source.last_fetch_at = datetime.utcnow()
        source.last_fetch_status = "success" if success else "error"
        source.fetch_count += 1
        source.items_fetched += items_found
        if success:
            source.success_count += 1
        else:
            source.error_count += 1
        
        results.append({
            "source_id": str(source.id),
            "source_name": source.name,
            "success": success,
            "items_fetched": items_found,
        })
    
    await db.commit()
    
    return {
        "total_sources": len(sources),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results,
    }
