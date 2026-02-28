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
    Script, ScriptSegment, ScriptStatus, ScriptLayer,
    VideoJob, VideoJobStatus,
    AuditLog, AuditAction,
    WeeklyBrief,
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
    
    # Create default admin user
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    admin_user = User(
        email="admin@geopolintel.com",
        username="admin",
        hashed_password=pwd_context.hash("admin123"),  # Change in production!
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
