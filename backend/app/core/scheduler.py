"""
Background Task Scheduler for Source Polling
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

try:
    from croniter import croniter
    _croniter_available = True
except ImportError:
    _croniter_available = False

from app.core.config import settings
from app.db.base import AsyncSessionLocal
from app.models.source import Source
from app.models.campaign import Campaign
from app.models.article import NormalizedArticle
from app.models.user import User
from app.models.brief import WeeklyBrief
from app.models.eri import ERIAssessment
from app.services.risk_service import risk_service

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
                # Process autonomous content campaigns
                await process_campaign_schedules(db)
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

def _compute_next_run(schedule, reference: datetime) -> Optional[datetime]:
    if schedule.interval_minutes:
        return reference + timedelta(minutes=schedule.interval_minutes)
    if schedule.cron_expression:
        if not _croniter_available:
            logger.warning(
                f"Cron expression support requires croniter for schedule {schedule.name}."
            )
            return None
        try:
            return croniter(schedule.cron_expression, reference).get_next(datetime)
        except Exception as e:
            logger.warning(
                f"Invalid cron_expression for schedule {schedule.name}: {e}"
            )
            return None
    return None


def _should_run(schedule, now: datetime) -> bool:
    if not schedule.last_run_at:
        return True
    if schedule.interval_minutes:
        return (now - schedule.last_run_at) >= timedelta(minutes=schedule.interval_minutes)
    if schedule.cron_expression:
        if not _croniter_available:
            return False
        try:
            next_run = croniter(schedule.cron_expression, schedule.last_run_at).get_next(datetime)
            return now >= next_run
        except Exception as e:
            logger.warning(
                f"Invalid cron_expression for schedule {schedule.name}: {e}"
            )
            return False
    return False


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
        if not _should_run(schedule, now):
            continue

        logger.info(f"Executing automation schedule: {schedule.name} (Type: {schedule.task_type})")
        schedule.run_count += 1
        schedule.last_run_at = now
        schedule.next_run_at = _compute_next_run(schedule, now)

        try:
            await _execute_automation_task(schedule, db, source_service)
            schedule.success_count += 1
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to execute schedule {schedule.name}: {e}")
            schedule.failure_count += 1
            try:
                await db.commit()
            except Exception:
                await db.rollback()


async def _execute_automation_task(schedule, db: AsyncSession, source_service):
    from app.models.automation import AutomationTaskType

    if schedule.task_type == AutomationTaskType.CONTENT_FETCH:
        category = (schedule.task_params or {}).get("category")
        if category:
            await source_service.fetch_by_category(category, db)
        else:
            await source_service.fetch_all_enabled(db)

    elif schedule.task_type == AutomationTaskType.RISK_ASSESSMENT:
        logger.info(f"Risk assessment task triggered: {schedule.name}")
        await _run_risk_assessment_automation(db)

    elif schedule.task_type == AutomationTaskType.WEEKLY_BRIEF:
        logger.info(f"Weekly brief task triggered: {schedule.name}")
        await _run_weekly_brief_automation(db)

    elif schedule.task_type == AutomationTaskType.FETCH_SOURCES:
        await source_service.fetch_all_enabled(db)

    else:
        raise ValueError(f"Unknown automation task type: {schedule.task_type}")


async def process_campaign_schedules(db: AsyncSession):
    """Dynamically process autonomous content campaigns."""
    from app.services.pipeline_service import pipeline_service
    
    result = await db.execute(
        select(Campaign).where(Campaign.is_active == True)
    )
    campaigns = result.scalars().all()
    
    now = datetime.utcnow()
    
    for campaign in campaigns:
        should_run = False
        if not campaign.last_run_at:
            should_run = True
        else:
            # Simple interval check based on schedule_type
            interval = timedelta(hours=24) # Default daily
            if campaign.schedule_type == "hourly":
                interval = timedelta(hours=1)
            elif campaign.schedule_type == "6h":
                interval = timedelta(hours=6)
            elif campaign.schedule_type == "12h":
                interval = timedelta(hours=12)
            
            if (now - campaign.last_run_at) >= interval:
                should_run = True
                
        if should_run:
            logger.info(f"Campaign Triggered: {campaign.name} (Profile: {campaign.profile_id})")
            try:
                # Process each category in the campaign
                categories = campaign.categories or ["General"]
                for cat in categories:
                    logger.info(f"Running autonomous pipeline for Campaign {campaign.name}: Category={cat}")
                    await pipeline_service.run_full_pipeline(
                        db=db,
                        category=cat,
                        profile_id=campaign.profile_id,
                        generate_short=True,
                        generate_presenter=False, # Focus on rapid short clips for autonomous mode
                    )
                
                campaign.last_run_at = now
                await db.commit()
                logger.info(f"Campaign {campaign.name} completed successfully.")
            except Exception as e:
                logger.error(f"Failed to execute Campaign {campaign.name}: {e}")
                await db.rollback()


async def _get_system_user_id(db: AsyncSession) -> Optional[str]:
    """Return an admin / superuser ID for automation tasks."""
    result = await db.execute(select(User).where(User.is_superuser == True).limit(1))
    user = result.scalar_one_or_none()
    if user:
        return str(user.id)
    result = await db.execute(select(User).limit(1))
    fallback = result.scalar_one_or_none()
    return str(fallback.id) if fallback else None


async def _run_risk_assessment_automation(db: AsyncSession):
    """Schedule risk assessments for any articles lacking a score."""
    user_id = await _get_system_user_id(db)
    if not user_id:
        logger.warning("Risk automation skipped because no system user exists.")
        return

    result = await db.execute(
        select(NormalizedArticle).options(selectinload(NormalizedArticle.risk_score))
    )
    articles = result.scalars().all()
    created = 0

    for article in articles:
        if article.risk_score is not None:
            continue
        try:
            await risk_service.assess_article(article, user_id, db, settings.SAFE_MODE_ENABLED)
            created += 1
        except Exception as exc:
            logger.error(f"Automated risk assessment failed for article {article.id}: {exc}")

    logger.info(f"Risk automation created {created} new assessments.")


async def _run_weekly_brief_automation(db: AsyncSession):
    """Generate a weekly brief based on the latest ERI assessment."""
    user_id = await _get_system_user_id(db)
    if not user_id:
        logger.warning("Weekly brief automation skipped because no system user exists.")
        return

    now = datetime.utcnow()
    week_number = now.isocalendar()[1]
    year = now.year

    existing = await db.execute(
        select(WeeklyBrief).where(
            WeeklyBrief.week_number == week_number,
            WeeklyBrief.year == year
        )
    )
    if existing.scalar_one_or_none():
        logger.info(f"Weekly brief already exists for {year}-W{week_number}; skipping automation.")
        return

    eri_result = await db.execute(
        select(ERIAssessment).order_by(ERIAssessment.created_at.desc()).limit(1)
    )
    latest_eri = eri_result.scalar_one_or_none()
    if not latest_eri:
        logger.warning("Weekly brief automation skipped because no ERI assessment exists.")
        return

    brief = WeeklyBrief(
        week_number=week_number,
        year=year,
        title=f"Weekly Escalation Brief | Week {week_number}",
        subtitle=f"ERI {latest_eri.overall_score} ({latest_eri.classification.value})",
        eri_assessment_id=latest_eri.id,
        eri_score=latest_eri.overall_score,
        executive_summary={
            "what_changed": f"Overall ERI reached {latest_eri.overall_score} ({latest_eri.classification.value}).",
            "what_is_stable": "Diplomatic engagement remains steady.",
            "risk_increased": "Military activity and proxy movements are trending upward."
            if latest_eri.military_score > 60 else "Military posture held steady.",
            "risk_decreased": "Economic pressures show signs of resilience.",
            "military_activity": f"{latest_eri.military_score}/100",
            "proxy_activity": f"{latest_eri.proxy_score}/100",
            "diplomatic_track": f"{latest_eri.diplomatic_score}/100",
        },
        key_developments=latest_eri.key_developments or [],
        scenario_outlook=latest_eri.scenarios or [],
        indicators_to_watch=latest_eri.indicators_to_watch or [],
        stakeholder_positions=latest_eri.stakeholder_positions or [],
        methodology="Automated weekly risk briefs generated from the latest ERI snapshot.",
        created_by=user_id,
    )
    brief.html_content = brief.generate_html()
    brief.scenarios = latest_eri.scenarios or []

    db.add(brief)
    await db.commit()
    await db.refresh(brief)

    logger.info(f"Weekly brief for {year}-W{week_number} generated automatically (ID: {brief.id}).")
