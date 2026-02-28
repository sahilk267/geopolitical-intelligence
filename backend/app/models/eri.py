"""
Escalation Risk Index (ERI) Models
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List, Dict

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base


class ERIClassification(str, PyEnum):
    """ERI risk classification."""
    LOW = "Low"
    MODERATE = "Moderate"
    ELEVATED = "Elevated"
    HIGH = "High"
    CRITICAL = "Critical"


class ERIAssessment(Base):
    """Escalation Risk Index assessment for a time period."""
    __tablename__ = "eri_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Time period
    week_number = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Dimension scores (0-100)
    military_score = Column(Integer, default=0)
    political_score = Column(Integer, default=0)
    proxy_score = Column(Integer, default=0)
    economic_score = Column(Integer, default=0)
    diplomatic_score = Column(Integer, default=0)
    
    # Overall score
    overall_score = Column(Integer, default=0)
    classification = Column(Enum(ERIClassification), default=ERIClassification.LOW)
    
    # Dimension weights (stored for audit)
    dimension_weights = Column(JSONB, default={
        "military": 0.30,
        "political": 0.15,
        "proxy": 0.20,
        "economic": 0.15,
        "diplomatic": 0.20,
    })
    
    # Key developments
    key_developments = Column(JSONB, default=[])  # List of developments
    
    # Scenario outlook
    scenarios = Column(JSONB, default=[])  # List of possible scenarios
    
    # Indicators to watch
    indicators_to_watch = Column(ARRAY(String), default=[])
    
    # Energy watch
    energy_watch = Column(JSONB)
    
    # Stakeholder positions
    stakeholder_positions = Column(JSONB, default=[])
    
    # Executive summary
    executive_summary = Column(JSONB)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    version = Column(String(10), default="1.0")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    
    def calculate_overall(self) -> int:
        """Calculate weighted overall ERI score."""
        weights = self.dimension_weights or {
            "military": 0.30,
            "political": 0.15,
            "proxy": 0.20,
            "economic": 0.15,
            "diplomatic": 0.20,
        }
        
        overall = (
            self.military_score * weights["military"] +
            self.political_score * weights["political"] +
            self.proxy_score * weights["proxy"] +
            self.economic_score * weights["economic"] +
            self.diplomatic_score * weights["diplomatic"]
        )
        
        return round(overall)
    
    def get_classification(self) -> ERIClassification:
        """Get ERI classification based on overall score."""
        score = self.overall_score
        if score < 20:
            return ERIClassification.LOW
        elif score < 40:
            return ERIClassification.MODERATE
        elif score < 60:
            return ERIClassification.ELEVATED
        elif score < 80:
            return ERIClassification.HIGH
        else:
            return ERIClassification.CRITICAL
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "week_number": self.week_number,
            "year": self.year,
            "overall_score": self.overall_score,
            "classification": self.classification.value,
            "dimensions": {
                "military": self.military_score,
                "political": self.political_score,
                "proxy": self.proxy_score,
                "economic": self.economic_score,
                "diplomatic": self.diplomatic_score,
            },
            "key_developments": self.key_developments or [],
            "scenarios": self.scenarios or [],
            "indicators_to_watch": self.indicators_to_watch or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ERIDimension(Base):
    """Individual ERI dimension with indicators."""
    __tablename__ = "eri_dimensions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("eri_assessments.id"), nullable=False)
    
    name = Column(String(50), nullable=False)  # military, political, etc.
    score = Column(Integer, default=0)
    weight = Column(Float, default=0.0)
    
    # Indicators for this dimension
    indicators = Column(JSONB, default=[])
    
    # Trend
    trend = Column(String(10), default="stable")  # up, down, stable
    previous_score = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
