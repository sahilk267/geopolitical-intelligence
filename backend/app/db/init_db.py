"""
Database Initialization
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base, engine
from app.models import (
    User, Role, UserRole,
    Source, SourceType, SourceTier,
    RawArticle, NormalizedArticle, ArticleStatus,
    Entity, EntityType, ArticleEntity,
    Claim, ClaimStatus,
    Contradiction, ContradictionStatus,
    RiskScore, RiskDimension,
    ERIAssessment, ERIDimension, ERIClassification,
    WeeklyBrief,
    AutomationSchedule, AutomationTaskType,
)

logger = logging.getLogger(__name__)


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def create_initial_data(db: AsyncSession):
    """Create initial seed data."""
    # Create default roles
    roles = [
        {"name": "admin", "description": "Full system access"},
        {"name": "editor_in_chief", "description": "Can approve all content"},
        {"name": "senior_editor", "description": "Can approve moderate risk content"},
        {"name": "junior_editor", "description": "Can approve low risk content"},
        {"name": "viewer", "description": "Read-only access"},
    ]
    
    for role_data in roles:
        role = Role(**role_data)
        db.add(role)
    
    await db.commit()
    logger.info("Default roles created")
    
    admin_user = User(
        email="admin@geopolintel.com",
        username="admin",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGGa31yy",  # admin123
        full_name="System Administrator",
        primary_role=UserRole.ADMIN,
        is_superuser=True,
        is_active=True,
    )
    db.add(admin_user)
    await db.commit()
    logger.info("Default admin user created")
    
    # Create sample sources
    sources = [
        {
            "name": "Reuters World News",
            "url": "https://www.reuters.com/world/rss.xml",
            "type": SourceType.RSS,
            "tier": SourceTier.ESTABLISHED_MEDIA,
            "category": "International News",
            "region": "Global",
            "is_enabled": True,
            "fetch_interval_minutes": 30,
        },
        {
            "name": "Al Jazeera Middle East",
            "url": "https://www.aljazeera.com/xml/rss/all.xml",
            "type": SourceType.RSS,
            "tier": SourceTier.ESTABLISHED_MEDIA,
            "category": "Regional News",
            "region": "Middle East",
            "is_enabled": True,
            "fetch_interval_minutes": 30,
        },
        {
            "name": "BBC World",
            "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
            "type": SourceType.RSS,
            "tier": SourceTier.ESTABLISHED_MEDIA,
            "category": "International News",
            "region": "Global",
            "is_enabled": True,
            "fetch_interval_minutes": 30,
        },
    ]
    
    for source_data in sources:
        source = Source(**source_data)
        db.add(source)
    
    await db.commit()
    logger.info("Sample sources created")
    
    # Create sample automation schedules
    schedules = [
        {
            "name": "Global News Fetching",
            "description": "Fetch news from all enabled sources every 30 minutes",
            "task_type": AutomationTaskType.FETCH_SOURCES,
            "interval_minutes": 30,
            "is_enabled": True,
        },
        {
            "name": "Daily Risk Assessment",
            "description": "Run risk assessment on new articles every 24 hours",
            "task_type": AutomationTaskType.RISK_ASSESSMENT,
            "cron_expression": "0 0 * * *",
            "is_enabled": True,
        },
        {
            "name": "Weekly Intelligence Briefing",
            "description": "Generate weekly intelligence brief every Friday at 4 PM",
            "task_type": AutomationTaskType.WEEKLY_BRIEF,
            "cron_expression": "0 16 * * 5",
            "is_enabled": True,
        }
    ]
    
    for schedule_data in schedules:
        schedule = AutomationSchedule(**schedule_data)
        db.add(schedule)
        
    await db.commit()
    logger.info("Sample automation schedules created")
