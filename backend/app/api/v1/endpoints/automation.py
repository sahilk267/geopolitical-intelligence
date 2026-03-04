"""
Automation Scheduler API Endpoints
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.base import get_db
from app.models.automation import AutomationSchedule, AutomationTaskType
from app.api.v1.endpoints.auth import get_current_active_user, require_role
from app.models.user import UserRole

router = APIRouter()


@router.get("/schedules")
async def list_schedules(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List automation schedules."""
    result = await db.execute(select(AutomationSchedule).order_by(desc(AutomationSchedule.created_at)))
    schedules = result.scalars().all()
    return [s.to_dict() for s in schedules]


@router.post("/schedules")
async def create_schedule(
    name: str,
    task_type: AutomationTaskType,
    description: Optional[str] = None,
    cron_expression: Optional[str] = None,
    interval_minutes: Optional[int] = None,
    task_params: dict = {},
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Create new automation schedule."""
    schedule = AutomationSchedule(
        name=name,
        description=description,
        task_type=task_type,
        cron_expression=cron_expression,
        interval_minutes=interval_minutes,
        task_params=task_params,
        created_by=current_user.id
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule.to_dict()


@router.patch("/schedules/{schedule_id}")
async def update_schedule(
    schedule_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    cron_expression: Optional[str] = None,
    interval_minutes: Optional[int] = None,
    task_params: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Update automation schedule."""
    result = await db.execute(select(AutomationSchedule).where(AutomationSchedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    if name is not None: schedule.name = name
    if description is not None: schedule.description = description
    if is_enabled is not None: schedule.is_enabled = is_enabled
    if cron_expression is not None: schedule.cron_expression = cron_expression
    if interval_minutes is not None: schedule.interval_minutes = interval_minutes
    if task_params is not None: schedule.task_params = task_params
    
    await db.commit()
    await db.refresh(schedule)
    return schedule.to_dict()


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.ADMIN))
):
    """Delete automation schedule."""
    result = await db.execute(select(AutomationSchedule).where(AutomationSchedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    await db.delete(schedule)
    await db.commit()
    return {"message": "Schedule deleted"}


@router.post("/schedules/{schedule_id}/run")
async def run_schedule_now(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.SENIOR_EDITOR))
):
    """Trigger schedule execution immediately."""
    result = await db.execute(select(AutomationSchedule).where(AutomationSchedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule.last_run_at = datetime.utcnow()
    schedule.run_count += 1
    await db.commit()
    
    return {"message": "Job triggered", "schedule": schedule.to_dict()}
