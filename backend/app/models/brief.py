"""
Weekly Intelligence Brief Models
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base


class WeeklyBrief(Base):
    """Weekly intelligence brief report."""
    __tablename__ = "weekly_briefs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Time period
    week_number = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    subtitle = Column(String(500))
    
    # ERI reference
    eri_assessment_id = Column(UUID(as_uuid=True), ForeignKey("eri_assessments.id"))
    eri_score = Column(Integer)
    
    # Version
    version = Column(String(10), default="1.0")
    
    # Content sections
    executive_summary = Column(JSONB, default={})
    key_developments = Column(JSONB, default=[])
    energy_watch = Column(JSONB, default={})
    stakeholder_positions = Column(JSONB, default=[])
    scenario_outlook = Column(JSONB, default=[])
    indicators_to_watch = Column(ARRAY(String), default=[])
    methodology = Column(Text)
    
    # Export
    pdf_url = Column(Text)
    html_content = Column(Text)
    
    # Status
    is_published = Column(Integer, default=0)  # 0=draft, 1=published
    published_at = Column(DateTime)
    published_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Distribution
    subscriber_count = Column(Integer, default=0)
    open_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "week_number": self.week_number,
            "year": self.year,
            "title": self.title,
            "eri_score": self.eri_score,
            "version": self.version,
            "is_published": bool(self.is_published),
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def generate_html(self) -> str:
        """Generate HTML version of the brief."""
        # This would be implemented with a proper template
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{self.title} - Week {self.week_number}</title>
    <style>
        body {{ font-family: Georgia, serif; max-width: 800px; margin: 0 auto; padding: 40px; }}
        .header {{ text-align: center; border-bottom: 3px solid #0B1F3A; padding-bottom: 20px; margin-bottom: 30px; }}
        .eri-score {{ font-size: 48px; font-weight: bold; color: #C7A84A; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ color: #0B1F3A; border-bottom: 2px solid #C7A84A; padding-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.title}</h1>
        <p>{self.subtitle}</p>
        <div class="eri-score">ERI: {self.eri_score}</div>
        <p>Week {self.week_number}, {self.year}</p>
    </div>
    <!-- Content sections would be rendered here -->
</body>
</html>
        """
        return html
