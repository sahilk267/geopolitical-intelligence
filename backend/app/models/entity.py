"""
Entity Extraction Models for Intelligence Graph
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Float, Integer, Boolean, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base


class EntityType(str, PyEnum):
    """Types of entities in the intelligence graph."""
    PERSON = "person"
    COUNTRY = "country"
    ORGANIZATION = "organization"
    EVENT = "event"
    SANCTION = "sanction"
    MILITARY_ACTION = "military_action"
    TREATY = "treaty"
    LOCATION = "location"
    WEAPON_SYSTEM = "weapon_system"
    ECONOMIC_INDICATOR = "economic_indicator"


class Entity(Base):
    """Extracted entity from articles."""
    __tablename__ = "entities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    normalized_name = Column(String(255), nullable=False, index=True)
    type = Column(Enum(EntityType), nullable=False)
    
    # Additional info
    aliases = Column(ARRAY(String))
    description = Column(Text)
    wikidata_id = Column(String(50))  # Link to Wikidata
    
    # For countries
    country_code = Column(String(3))
    region = Column(String(100))
    
    # For persons
    title = Column(String(100))
    organization_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
    
    # Metadata
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    mention_count = Column(Integer, default=1)
    
    # Graph properties
    graph_node_id = Column(String(100))  # Neo4j node ID
    graph_properties = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    articles = relationship("NormalizedArticle", secondary="article_entities", back_populates="entities")
    claims_as_subject = relationship("Claim", foreign_keys="Claim.subject_entity_id", back_populates="subject_entity")
    claims_as_object = relationship("Claim", foreign_keys="Claim.object_entity_id", back_populates="object_entity")
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "normalized_name": self.normalized_name,
            "type": self.type.value,
            "aliases": self.aliases or [],
            "description": self.description,
            "mention_count": self.mention_count,
            "first_seen": self.first_seen_at.isoformat() if self.first_seen_at else None,
            "last_seen": self.last_seen_at.isoformat() if self.last_seen_at else None,
        }
    
    def update_mention(self):
        """Update entity when mentioned again."""
        self.mention_count += 1
        self.last_seen_at = datetime.utcnow()


# Association table
class ArticleEntity(Base):
    """Association between articles and entities."""
    __tablename__ = "article_entities"
    
    article_id = Column(UUID(as_uuid=True), ForeignKey('normalized_articles.id'), primary_key=True)
    entity_id = Column(UUID(as_uuid=True), ForeignKey('entities.id'), primary_key=True)
    confidence = Column(Float, default=1.0)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    context = Column(Text)  # Surrounding text
