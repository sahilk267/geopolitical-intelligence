"""
Audit Logs API Endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.audit import AuditLog, AuditAction
from app.models.user import User, UserRole
from app.api.v1.endpoints.auth import get_current_active_user, require_role

router = APIRouter()


@router.get("/")
async def list_audit_logs(
    action: Optional[AuditAction] = None,
    category: Optional[str] = None,
    user_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """List audit logs (senior editors and above)."""
    query = select(AuditLog)
    
    if action:
        query = query.where(AuditLog.action == action)
    if category:
        query = query.where(AuditLog.category == category)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if start_date:
        query = query.where(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.where(AuditLog.timestamp <= end_date)
    
    query = query.order_by(desc(AuditLog.timestamp))
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [log.to_dict() for log in logs]


@router.get("/{log_id}")
async def get_audit_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Get audit log details (admin only)."""
    result = await db.execute(
        select(AuditLog).where(AuditLog.id == log_id)
    )
    log = result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    return {
        **log.to_dict(),
        "old_values": log.old_values,
        "new_values": log.new_values,
        "ip_address": str(log.ip_address) if log.ip_address else None,
        "user_agent": log.user_agent,
        "request_id": log.request_id,
    }


@router.get("/stats/summary")
async def get_audit_stats(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Get audit log statistics (admin only)."""
    from datetime import datetime, timedelta
    
    start = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(AuditLog).where(AuditLog.timestamp >= start)
    )
    logs = result.scalars().all()
    
    # Count by action
    action_counts = {}
    for log in logs:
        action_counts[log.action.value] = action_counts.get(log.action.value, 0) + 1
    
    # Count by category
    category_counts = {}
    for log in logs:
        category_counts[log.category] = category_counts.get(log.category, 0) + 1
    
    return {
        "period_days": days,
        "total_logs": len(logs),
        "by_action": action_counts,
        "by_category": category_counts,
    }
