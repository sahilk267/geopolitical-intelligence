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
@router.patch("/{source_id}")
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
    
    if name is not None:
        source.name = name
    if url is not None:
        source.url = url
    if is_enabled is not None:
        source.is_enabled = is_enabled
    if fetch_interval_minutes is not None:
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
    
    import httpx
    from datetime import timedelta
    
    response_time_ms = 0
    items_found = 0
    success = False
    error_message = None

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(source.url)
            response_time_ms = int(response.elapsed.total_seconds() * 1000)
            success = response.status_code >= 200 and response.status_code < 400
            if success:
                items_found = 1
            else:
                error_message = f"Unexpected status code: {response.status_code}"
    except Exception as exc:
        success = False
        error_message = str(exc)
        response_time_ms = 0
    
    source.last_fetch_status = "success" if success else "error"
    if not success:
        source.last_fetch_error = error_message or "Connection timeout or invalid response"
    source.fetch_count += 1
    if success:
        source.success_count += 1
    else:
        source.error_count += 1
    
    await db.commit()
    
    return {
        "success": success,
        "source": source.to_dict(),
        "response_time_ms": response_time_ms,
        "items_found": items_found,
        "error_message": error_message,
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
    from app.services.source_service import source_service
    result = await source_service.fetch_all_enabled(db)
    
    details = result.get("details", [])
    total = result.get("total_sources", 0)
    successful = sum(1 for r in details if r.get("success", False))
    failed = total - successful
    
    formatted_results = []
    for d in details:
        source_data = d.get("source", {})
        if d.get("success"):
            formatted_results.append({
                "source_id": str(source_data.get("id", "")),
                "source_name": source_data.get("name", ""),
                "success": True,
                "items_fetched": d.get("items_fetched", 0)
            })
        else:
            formatted_results.append({
                "source_id": str(source_data.get("id", "")),
                "source_name": source_data.get("name", ""),
                "success": False,
                "items_fetched": 0,
                "error": d.get("error", "Unknown error")
            })
            
    return {
        "total_sources": total,
        "successful": successful,
        "failed": failed,
        "results": formatted_results
    }
