"""
News Source Management Models
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey, Enum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class SourceType(str, PyEnum):
    """Source type enumeration."""
    RSS = "rss"
    API = "api"
    WEBHOOK = "webhook"
    SCRAPING = "scraping"
    MANUAL = "manual"


class SourceTier(int, PyEnum):
    """Source credibility tier."""
    OFFICIAL = 1  # Government, official statements
    ESTABLISHED_MEDIA = 2  # Reuters, BBC, etc.
    EXPERT_ANALYSIS = 3  # Think tanks, academics
    UNVERIFIED = 4  # Social media, unknown sources


class Source(Base):
    """News source configuration model."""
    __tablename__ = "sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    type = Column(Enum(SourceType), default=SourceType.RSS)
    tier = Column(Enum(SourceTier), default=SourceTier.UNVERIFIED)
    
    # Categorization
    category = Column(String(100))  # News type
    region = Column(String(100))  # Geographic focus
    language = Column(String(10), default="en")
    
    # Fetch configuration
    fetch_interval_minutes = Column(Integer, default=30)
    is_enabled = Column(Boolean, default=True)
    last_fetch_at = Column(DateTime)
    last_fetch_status = Column(String(20))  # success, error, pending
    last_fetch_error = Column(Text)
    
    # Statistics
    fetch_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    average_response_time_ms = Column(Float, default=0.0)
    items_fetched = Column(Integer, default=0)
    
    # API configuration (for API sources)
    api_headers = Column(JSONB)
    api_key = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    raw_articles = relationship("RawArticle", back_populates="source")
    
    def get_success_rate(self) -> float:
        """Calculate fetch success rate."""
        if self.fetch_count == 0:
            return 0.0
        return (self.success_count / self.fetch_count) * 100
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "url": self.url,
            "type": self.type.value,
            "tier": self.tier.value,
            "category": self.category,
            "region": self.region,
            "is_enabled": self.is_enabled,
            "status": self.last_fetch_status,
            "success_rate": round(self.get_success_rate(), 2),
            "items_fetched": self.items_fetched,
            "last_fetch": self.last_fetch_at.isoformat() if self.last_fetch_at else None,
        }
