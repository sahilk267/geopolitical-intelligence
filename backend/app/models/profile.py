"""
Profile (Persona) model for multi-tenant content generation.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base


class Profile(Base):
    """
    Represents a specific persona or brand identity for content generation.
    Each profile has its own configuration for voice, video style, and platforms.
    """
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Content Settings
    voice_engine = Column(String(50), default="edge-tts")
    voice_id = Column(String(100))  # Specific voice model ID
    video_style = Column(JSONB, default={})  # Style overrides (font, colors, transitions)
    
    # Distribution Settings
    # Map of platform -> {enabled: bool, config: {}}
    platform_configs = Column(JSONB, default={})
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "voiceEngine": self.voice_engine,
            "voiceId": self.voice_id,
            "videoStyle": self.video_style,
            "platformConfigs": self.platform_configs,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
