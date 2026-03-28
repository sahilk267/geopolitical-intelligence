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
    
    # Relationships
    article = relationship("NormalizedArticle", back_populates="risk_score")
    
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
        """Return API-ready risk assessment."""
        scores = {
            "legalRisk": self.legal_risk,
            "defamationRisk": self.defamation_risk,
            "platformRisk": self.platform_risk,
            "politicalSensitivity": self.political_risk,
            "overallScore": self.overall_score,
        }

        return {
            "id": str(self.id),
            "articleId": str(self.article_id),
            "contentId": str(self.article_id),
            "scores": scores,
            "classification": self.classification,
            "riskFactors": self.risk_factors or {},
            "factors": self.risk_factors or {},
            "notes": self.approval_notes or "",
            "requiresSeniorReview": self.requires_senior_review,
            "safeModeBlocked": self.safe_mode_blocked,
            "safeModeViolations": self.safe_mode_violations or [],
            "mitigationSuggestions": self.mitigation_suggestions or [],
            "assessedBy": str(self.assessed_by) if self.assessed_by else None,
            "assessedAt": self.assessed_at.isoformat() if self.assessed_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
