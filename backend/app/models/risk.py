"""
Risk Governance Models
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Float, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class RiskDimension(str, PyEnum):
    """Risk assessment dimensions."""
    LEGAL = "legal"
    DEFAMATION = "defamation"
    PLATFORM = "platform"
    POLITICAL = "political"


class RiskScore(Base):
    """4-dimensional risk assessment for content."""
    __tablename__ = "risk_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("normalized_articles.id"), nullable=False)
    
    # Individual dimension scores (0-100)
    legal_risk = Column(Integer, default=0)
    defamation_risk = Column(Integer, default=0)
    platform_risk = Column(Integer, default=0)
    political_risk = Column(Integer, default=0)
    
    # Overall weighted score
    overall_score = Column(Integer, default=0)
    
    # Risk classification
    classification = Column(String(20))  # Low, Moderate, Elevated, High, Critical
    
    # Risk factors detected
    risk_factors = Column(JSONB)  # List of detected risk factors
    
    # Safe mode check
    safe_mode_blocked = Column(Boolean, default=False)
    safe_mode_violations = Column(JSONB)  # List of violations if blocked
    
    # Mitigation suggestions
    mitigation_suggestions = Column(JSONB)
    
    # Approval
    requires_senior_review = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    
    # Assessment metadata
    assessed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assessed_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_overall(self) -> int:
        """Calculate weighted overall risk score."""
        weights = {
            RiskDimension.LEGAL: 0.30,
            RiskDimension.DEFAMATION: 0.30,
            RiskDimension.PLATFORM: 0.20,
            RiskDimension.POLITICAL: 0.20,
        }
        
        overall = (
            self.legal_risk * weights[RiskDimension.LEGAL] +
            self.defamation_risk * weights[RiskDimension.DEFAMATION] +
            self.platform_risk * weights[RiskDimension.PLATFORM] +
            self.political_risk * weights[RiskDimension.POLITICAL]
        )
        
        return round(overall)
    
    def get_classification(self) -> str:
        """Get risk classification based on overall score."""
        score = self.overall_score
        if score <= 20:
            return "Low"
        elif score <= 40:
            return "Moderate"
        elif score <= 60:
            return "Elevated"
        elif score <= 80:
            return "High"
        else:
            return "Critical"
    
    def get_required_approval_level(self) -> str:
        """Get required approval level based on risk score."""
        score = self.overall_score
        if score <= 20:
            return "Junior Editor"
        elif score <= 40:
            return "Senior Editor"
        elif score <= 60:
            return "Editor in Chief"
        else:
            return "Editor in Chief + Legal Review"
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "legal_risk": self.legal_risk,
            "defamation_risk": self.defamation_risk,
            "platform_risk": self.platform_risk,
            "political_risk": self.political_risk,
            "overall_score": self.overall_score,
            "classification": self.classification,
            "safe_mode_blocked": self.safe_mode_blocked,
            "requires_senior_review": self.requires_senior_review,
            "mitigation_suggestions": self.mitigation_suggestions or [],
            "assessed_at": self.assessed_at.isoformat() if self.assessed_at else None,
        }
