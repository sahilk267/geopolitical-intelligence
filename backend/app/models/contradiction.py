"""
Contradiction Detection Models
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Float, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class ContradictionStatus(str, PyEnum):
    """Contradiction resolution status."""
    DETECTED = "detected"
    UNDER_REVIEW = "under_review"
    CONFIRMED = "confirmed"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class ContradictionType(str, PyEnum):
    """Types of contradictions."""
    DIRECT = "direct"  # Direct opposite claims
    TEMPORAL = "temporal"  # Same claim at different times
    SCOPE = "scope"  # Different scope/scale
    ATTRIBUTION = "attribution"  # Different sources for same claim


class Contradiction(Base):
    """Detected contradiction between claims."""
    __tablename__ = "contradictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Claims involved
    claim_a_id = Column(UUID(as_uuid=True), ForeignKey("claims.id"), nullable=False, index=True)
    claim_b_id = Column(UUID(as_uuid=True), ForeignKey("claims.id"), nullable=False, index=True)
    
    # Contradiction details
    contradiction_type = Column(Enum(ContradictionType), default=ContradictionType.DIRECT)
    severity = Column(Integer, default=1)  # 1-10 scale
    confidence = Column(Float, default=0.0)  # Detection confidence
    
    # Explanation
    explanation = Column(Text)  # Why these contradict
    key_difference = Column(Text)  # What specifically differs
    
    # Resolution
    status = Column(Enum(ContradictionStatus), default=ContradictionStatus.DETECTED)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Which claim is considered correct (if resolved)
    correct_claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id"))
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    claim_a = relationship("Claim", foreign_keys=[claim_a_id], back_populates="contradictions")
    claim_b = relationship("Claim", foreign_keys=[claim_b_id])
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "claim_a": self.claim_a.text if self.claim_a else None,
            "claim_b": self.claim_b.text if self.claim_b else None,
            "type": self.contradiction_type.value,
            "severity": self.severity,
            "confidence": self.confidence,
            "status": self.status.value,
            "explanation": self.explanation,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }
    
    @staticmethod
    def calculate_severity(claim_a: "Claim", claim_b: "Claim") -> int:
        """Calculate contradiction severity based on claim importance."""
        # Higher severity for claims involving major actors
        major_actors = ["iran", "israel", "usa", "russia", "china", "saudi arabia"]
        
        severity = 5  # Base severity
        
        # Check if major actors involved
        for actor in major_actors:
            if (claim_a.subject_entity and actor in claim_a.subject_entity.normalized_name.lower()) or \
               (claim_b.subject_entity and actor in claim_b.subject_entity.normalized_name.lower()):
                severity += 2
        
        # Higher severity for military/security claims
        security_predicates = ["attack", "strike", "sanction", "threaten", "violate"]
        if claim_a.predicate in security_predicates or claim_b.predicate in security_predicates:
            severity += 2
        
        return min(severity, 10)
