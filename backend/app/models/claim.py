"""
Claim Extraction Models for Contradiction Detection
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Float, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class ClaimStatus(str, PyEnum):
    """Claim verification status."""
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    DISPUTED = "disputed"
    CONTRADICTED = "contradicted"
    RETRACTED = "retracted"


class Claim(Base):
    """Extracted claim from articles."""
    __tablename__ = "claims"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("normalized_articles.id"), nullable=False, index=True)
    
    # Claim structure: [Subject] [Predicate] [Object]
    text = Column(Text, nullable=False)  # Full claim text
    normalized_text = Column(Text, nullable=False)  # Normalized for comparison
    
    # Entities involved
    subject_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"), index=True)
    object_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"), index=True)
    predicate = Column(String(100))  # e.g., "attacked", "denied", "sanctioned"
    
    # Claim metadata
    claim_type = Column(String(50))  # factual, opinion, prediction
    confidence = Column(Float, default=0.0)  # Extraction confidence
    
    # Verification
    status = Column(Enum(ClaimStatus), default=ClaimStatus.UNVERIFIED)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    verified_at = Column(DateTime)
    verification_notes = Column(Text)
    
    # Source context
    source_quote = Column(Text)  # Original text from article
    context = Column(Text)  # Surrounding paragraph
    
    # Contradiction tracking
    has_contradiction = Column(Boolean, default=False)
    contradiction_count = Column(Integer, default=0)
    
    # Timestamps
    extracted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    article = relationship("NormalizedArticle", back_populates="claims")
    subject_entity = relationship("Entity", foreign_keys=[subject_entity_id], back_populates="claims_as_subject")
    object_entity = relationship("Entity", foreign_keys=[object_entity_id], back_populates="claims_as_object")
    contradictions = relationship("Contradiction", foreign_keys="Contradiction.claim_a_id", back_populates="claim_a")
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "text": self.text,
            "subject": self.subject_entity.name if self.subject_entity else None,
            "predicate": self.predicate,
            "object": self.object_entity.name if self.object_entity else None,
            "confidence": self.confidence,
            "status": self.status.value,
            "has_contradiction": self.has_contradiction,
            "extracted_at": self.extracted_at.isoformat() if self.extracted_at else None,
        }
    
    def get_key(self) -> str:
        """Get normalized key for comparison."""
        subject = self.subject_entity.normalized_name if self.subject_entity else ""
        obj = self.object_entity.normalized_name if self.object_entity else ""
        return f"{subject}:{self.predicate}:{obj}".lower()
