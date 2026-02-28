"""
Video Production Pipeline Models
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class VideoJobStatus(str, PyEnum):
    """Video production job status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    TTS_GENERATING = "tts_generating"
    AVATAR_RENDERING = "avatar_rendering"
    VIDEO_COMPOSITING = "video_compositing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoJob(Base):
    """Video production job."""
    __tablename__ = "video_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    script_id = Column(UUID(as_uuid=True), ForeignKey("scripts.id"), nullable=False)
    
    # Job configuration
    job_type = Column(String(50), default="standard")  # standard, short, premium
    priority = Column(Integer, default=0)  # 0=normal, 1=high, 2=urgent
    
    # Output settings
    output_format = Column(String(20), default="mp4")
    resolution = Column(String(20), default="1920x1080")
    fps = Column(Integer, default=30)
    
    # Status tracking
    status = Column(Enum(VideoJobStatus), default=VideoJobStatus.QUEUED)
    progress_percent = Column(Float, default=0.0)
    
    # Stage tracking
    current_stage = Column(String(50))
    stage_progress = Column(JSONB, default={})
    
    # Assets
    tts_audio_url = Column(Text)
    avatar_video_url = Column(Text)
    background_video_url = Column(Text)
    final_video_url = Column(Text)
    
    # Processing metadata
    worker_id = Column(String(100))
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    
    # Error tracking
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Output metadata
    file_size_bytes = Column(Integer)
    duration_seconds = Column(Integer)
    thumbnail_url = Column(Text)
    
    # Publishing
    youtube_video_id = Column(String(50))
    published_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    script = relationship("Script", back_populates="video_jobs")
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "script_id": str(self.script_id),
            "status": self.status.value,
            "progress": self.progress_percent,
            "current_stage": self.current_stage,
            "priority": self.priority,
            "output_url": self.final_video_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def get_duration_string(self) -> str:
        """Get formatted duration string."""
        if not self.duration_seconds:
            return "00:00"
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
