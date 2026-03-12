"""
Platform Settings Model
Database-driven settings for real-time configuration changes.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class PlatformSetting(Base):
    """Platform-wide settings stored in database for runtime configuration."""
    __tablename__ = "platform_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text)
    category = Column(String(50))  # "general", "ai", "tts", "video", "security"
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "category": self.category,
            "description": self.description,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
