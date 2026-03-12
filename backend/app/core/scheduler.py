"""
Background Task Scheduler for Source Polling
"""
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal
from app.models.source import Source
from app.api.v1.endpoints.sources import fetch_from_source

logger = logging.getLogger(__name__)

async def poll_sources_task():
    """Periodically check and poll enabled sources and automation schedules."""
    while True:
        try:
            async with AsyncSessionLocal() as db:
                # Keep legacy polling for now
                await poll_active_sources(db)
                # Process dynamic automation schedules
                await process_automation_schedules(db)
        except Exception as e:
            logger.error(f"Error in poll_sources_task: {e}")
        
        # Check every minute
        await asyncio.sleep(60)

async def poll_active_sources(db: AsyncSession):
    """Business logic for legacy polling of active sources."""
    result = await db.execute(
        select(Source).where(Source.is_enabled == True)
    )
    sources = result.scalars().all()
    
    now = datetime.utcnow()
    from app.services.source_service import source_service
    
    for source in sources:
        if not source.last_fetch_at or (now - source.last_fetch_at) >= timedelta(minutes=source.fetch_interval_minutes):
            logger.info(f"Legacy auto-polling source: {source.name}")
            try:
                await source_service.fetch_from_source(source.id, db)
            except Exception as e:
                logger.error(f"Failed to legacy auto-poll source {source.name}: {e}")

async def process_automation_schedules(db: AsyncSession):
    """Dynamically process automation schedules based on database configuration."""
    from app.models.automation import AutomationSchedule, AutomationTaskType
    from app.services.source_service import source_service
    
    result = await db.execute(
        select(AutomationSchedule).where(AutomationSchedule.is_enabled == True)
    )
    schedules = result.scalars().all()
    
    now = datetime.utcnow()
    
    for schedule in schedules:
        should_run = False
        if not schedule.last_run_at:
            should_run = True
        elif schedule.interval_minutes:
            time_since_last = now - schedule.last_run_at
            if time_since_last >= timedelta(minutes=schedule.interval_minutes):
                should_run = True
        
        if should_run:
            logger.info(f"Executing automation schedule: {schedule.name} (Type: {schedule.task_type})")
            try:
                if schedule.task_type == AutomationTaskType.CONTENT_FETCH:
                    category = (schedule.task_params or {}).get("category")
                    if category:
                        await source_service.fetch_by_category(category, db)
                    else:
                        await source_service.fetch_all_enabled(db)
                
                elif schedule.task_type == AutomationTaskType.RISK_ASSESSMENT:
                    logger.info(f"Risk assessment task triggered: {schedule.name}")
                    # TODO: Implement risk assessment automation in Phase 6
                
                elif schedule.task_type == AutomationTaskType.WEEKLY_BRIEF:
                    logger.info(f"Weekly brief task triggered: {schedule.name}")
                    # TODO: Implement weekly brief automation in Phase 6
                
                elif schedule.task_type == AutomationTaskType.FETCH_SOURCES:
                    await source_service.fetch_all_enabled(db)
                
                else:
                    logger.warning(f"Unknown automation task type: {schedule.task_type}")
                
                schedule.last_run_at = now
                schedule.run_count += 1
                schedule.success_count += 1
                await db.commit()
            except Exception as e:
                logger.error(f"Failed to execute schedule {schedule.name}: {e}")
                schedule.failure_count += 1
                try:
                    await db.commit()
                except Exception:
                    await db.rollback()
