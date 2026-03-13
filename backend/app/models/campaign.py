"""
Campaign model for autonomous content generation blueprints.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base


class Campaign(Base):
    """
    An autonomous blueprint that links a profile to specific content categories and schedules.
    """
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Relationships
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    
    # Targeting
    categories = Column(JSONB, default=[])  # e.g., ["Military", "Economy"]
    regions = Column(JSONB, default=[])     # e.g., ["Middle East", "Global"]
    
    # Scheduling & Automation
    is_active = Column(Boolean, default=True)
    # cron, hourly, daily, etc.
    schedule_type = Column(String(50), default="daily")
    schedule_config = Column(JSONB, default={})
    
    # Execution Tracking
    last_run_at = Column(DateTime)
    next_run_at = Column(DateTime)
    
    # Results
    # JSON list of recent generated script/video IDs
    history = Column(JSONB, default=[])
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "profileId": str(self.profile_id),
            "categories": self.categories,
            "regions": self.regions,
            "isActive": self.is_active,
            "scheduleType": self.schedule_type,
            "scheduleConfig": self.schedule_config,
            "lastRunAt": self.last_run_at.isoformat() if self.last_run_at else None,
            "nextRunAt": self.next_run_at.isoformat() if self.next_run_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
