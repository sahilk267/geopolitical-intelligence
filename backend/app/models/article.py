"""
Article Models - Raw and Normalized
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Float, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base


class ArticleStatus(str, PyEnum):
    """Article processing status."""
    NEW = "new"
    PENDING_REVIEW = "pending_review"
    NORMALIZED = "normalized"
    FLAGGED = "flagged"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class RawArticle(Base):
    """Raw article as fetched from source."""
    __tablename__ = "raw_articles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False, index=True)
    
    # Original content
    title = Column(Text, nullable=False)
    summary = Column(Text)
    content = Column(Text)
    url = Column(Text, nullable=False)
    published_at = Column(DateTime)
    author = Column(String(255))
    
    # Raw metadata
    raw_metadata = Column(JSONB)  # Original RSS/API response
    raw_content_hash = Column(String(64))  # SHA-256 hash for deduplication
    
    # Processing
    status = Column(Enum(ArticleStatus), default=ArticleStatus.NEW)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    normalized_at = Column(DateTime)
    
    # Relationships
    source = relationship("Source", back_populates="raw_articles")
    normalized_article = relationship("NormalizedArticle", uselist=False, back_populates="raw_article")
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "source_id": str(self.source_id),
            "title": self.title,
            "summary": self.summary[:200] + "..." if self.summary and len(self.summary) > 200 else self.summary,
            "url": self.url,
            "status": self.status.value,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }


class NormalizedArticle(Base):
    """Normalized and processed article."""
    __tablename__ = "normalized_articles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_article_id = Column(UUID(as_uuid=True), ForeignKey("raw_articles.id"), unique=True)
    
    # Normalized content
    headline = Column(Text, nullable=False)
    summary = Column(Text)
    content = Column(Text)
    
    # Classification
    category = Column(String(100))
    region = Column(String(100))
    topics = Column(ARRAY(String))
    tags = Column(ARRAY(String))
    
    # Quality metrics
    relevance_score = Column(Float, default=0.0)  # 0-100
    credibility_score = Column(Float, default=0.0)  # Based on source tier
    
    # Processing status
    status = Column(Enum(ArticleStatus), default=ArticleStatus.PENDING_REVIEW)
    priority = Column(Integer, default=0)  # 0=normal, 1=important, 2=breaking, 3=emergency
    
    # Risk assessment
    risk_score_id = Column(UUID(as_uuid=True), ForeignKey("risk_scores.id"))
    
    # Editorial workflow
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    published_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    
    # Relationships
    raw_article = relationship("RawArticle", back_populates="normalized_article")
    entities = relationship("Entity", secondary="article_entities", back_populates="articles")
    claims = relationship("Claim", back_populates="article")
    risk_score = relationship("RiskScore", uselist=False)
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "headline": self.headline,
            "summary": self.summary[:300] + "..." if self.summary and len(self.summary) > 300 else self.summary,
            "category": self.category,
            "region": self.region,
            "topics": self.topics or [],
            "tags": self.tags or [],
            "relevance_score": self.relevance_score,
            "credibility_score": self.credibility_score,
            "status": self.status.value,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }




