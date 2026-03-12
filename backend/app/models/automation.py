"""
Automation Scheduler Models
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base


class AutomationTaskType(str, PyEnum):
    """Types of automated tasks."""
    CONTENT_FETCH = "content_fetch"
    FETCH_SOURCES = "fetch_sources"
    RISK_ASSESSMENT = "risk_assessment"
    WEEKLY_BRIEF = "weekly_brief"
    VIDEO_GENERATION = "video_generation"
    REPORT_GENERATION = "report_generation"
    SYSTEM_MAINTENANCE = "system_maintenance"


class AutomationSchedule(Base):
    """Automation schedule configuration."""
    __tablename__ = "automation_schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_enabled = Column(Boolean, default=True)
    
    # Schedule configuration
    cron_expression = Column(String(100))  # e.g., "0 9 * * *"
    interval_minutes = Column(Integer)     # alternative to cron
    
    # Task configuration
    task_type = Column(Enum(AutomationTaskType), nullable=False)
    task_params = Column(JSONB, default={})
    
    # Status tracking
    last_run_at = Column(DateTime)
    next_run_at = Column(DateTime)
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "isEnabled": self.is_enabled,
            "cronExpression": self.cron_expression,
            "intervalMinutes": self.interval_minutes,
            "taskType": self.task_type.value,
            "taskParams": self.task_params,
            "lastRunAt": self.last_run_at.isoformat() if self.last_run_at else None,
            "nextRunAt": self.next_run_at.isoformat() if self.next_run_at else None,
            "runCount": self.run_count,
            "successCount": self.success_count,
            "failureCount": self.failure_count,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
