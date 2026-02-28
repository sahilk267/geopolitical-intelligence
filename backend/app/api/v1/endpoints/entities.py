"""
Entities API Endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.entity import Entity, EntityType
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter()


@router.get("/")
async def list_entities(
    type: Optional[EntityType] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List entities."""
    query = select(Entity)
    
    if type:
        query = query.where(Entity.type == type)
    if search:
        query = query.where(
            Entity.name.ilike(f"%{search}%") |
            Entity.normalized_name.ilike(f"%{search}%")
        )
    
    query = query.order_by(desc(Entity.mention_count))
    query = query.limit(limit)
    
    result = await db.execute(query)
    entities = result.scalars().all()
    
    return [entity.to_dict() for entity in entities]


@router.get("/{entity_id}")
async def get_entity(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get entity details."""
    result = await db.execute(
        select(Entity).where(Entity.id == entity_id)
    )
    entity = result.scalar_one_or_none()
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return {
        **entity.to_dict(),
        "articles": [a.to_dict() for a in entity.articles[:10]],
        "claims_as_subject": [c.to_dict() for c in entity.claims_as_subject[:10]],
    }


@router.get("/{entity_id}/graph")
async def get_entity_graph(
    entity_id: UUID,
    depth: int = Query(2, ge=1, le=3),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get entity graph relationships."""
    # This would query Neo4j in production
    # For now, return stub data
    return {
        "entity_id": str(entity_id),
        "depth": depth,
        "nodes": [],
        "relationships": [],
        "message": "Graph data would be fetched from Neo4j",
    }
