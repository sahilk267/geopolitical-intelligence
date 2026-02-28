"""
Script Generation Models
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class ScriptStatus(str, PyEnum):
    """Script generation status."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    READY_FOR_VIDEO = "ready_for_video"


class ScriptLayer(str, PyEnum):
    """Script content layers."""
    FACTUAL_REPORTING = "factual_reporting"
    HISTORICAL_CONTEXT = "historical_context"
    ANALYTICAL_ASSESSMENT = "analytical_assessment"
    SCENARIO_ANALYSIS = "scenario_analysis"


class Script(Base):
    """Generated script for video production."""
    __tablename__ = "scripts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("normalized_articles.id"))
    
    # Script metadata
    title = Column(String(500), nullable=False)
    topic = Column(String(200))
    target_duration_seconds = Column(Integer, default=600)  # 10 minutes default
    
    # Content layers included
    layers = Column(JSONB, default=[])
    
    # Script content
    segments = Column(JSONB, default=[])  # List of script segments
    full_script = Column(Text)
    
    # Word count and timing
    word_count = Column(Integer, default=0)
    estimated_duration_seconds = Column(Integer, default=0)
    
    # AI generation
    ai_model = Column(String(100))
    ai_prompt = Column(Text)
    generation_params = Column(JSONB)
    
    # Status
    status = Column(Enum(ScriptStatus), default=ScriptStatus.DRAFT)
    version = Column(Integer, default=1)
    
    # Review
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    review_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    video_jobs = relationship("VideoJob", back_populates="script")
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "title": self.title,
            "topic": self.topic,
            "layers": self.layers or [],
            "word_count": self.word_count,
            "estimated_duration": self.estimated_duration_seconds,
            "status": self.status.value,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def calculate_duration(self) -> int:
        """Calculate estimated duration based on word count."""
        # Average speaking rate: 150 words per minute
        words_per_minute = 150
        duration_minutes = self.word_count / words_per_minute
        return round(duration_minutes * 60)


class ScriptSegment(Base):
    """Individual segment of a script."""
    __tablename__ = "script_segments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    script_id = Column(UUID(as_uuid=True), ForeignKey("scripts.id"), nullable=False)
    
    # Segment info
    segment_type = Column(String(50))  # headline, facts, background, analysis, scenario, closing
    order = Column(Integer, default=0)
    
    # Content
    content = Column(Text, nullable=False)
    sources = Column(JSONB, default=[])  # Source references
    
    # Timing
    word_count = Column(Integer, default=0)
    estimated_duration_seconds = Column(Integer, default=0)
    
    # Approval
    approved = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
