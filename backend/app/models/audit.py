"""
Audit and Governance Models
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship

from app.db.base import Base


class AuditAction(str, PyEnum):
    """Types of audit actions."""
    # User actions
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    
    # Content actions
    ARTICLE_CREATE = "article_create"
    ARTICLE_UPDATE = "article_update"
    ARTICLE_PUBLISH = "article_publish"
    ARTICLE_DELETE = "article_delete"
    
    # Risk actions
    RISK_ASSESS = "risk_assess"
    RISK_APPROVE = "risk_approve"
    RISK_REJECT = "risk_reject"
    SAFE_MODE_TOGGLE = "safe_mode_toggle"
    
    # Source actions
    SOURCE_CREATE = "source_create"
    SOURCE_UPDATE = "source_update"
    SOURCE_DELETE = "source_delete"
    SOURCE_FETCH = "source_fetch"
    SOURCE_TEST = "source_test"
    
    # ERI actions
    ERI_CREATE = "eri_create"
    ERI_UPDATE = "eri_update"
    ERI_PUBLISH = "eri_publish"
    
    # Script actions
    SCRIPT_GENERATE = "script_generate"
    SCRIPT_APPROVE = "script_approve"
    SCRIPT_REJECT = "script_reject"
    
    # Video actions
    VIDEO_QUEUE = "video_queue"
    VIDEO_START = "video_start"
    VIDEO_COMPLETE = "video_complete"
    VIDEO_FAIL = "video_fail"
    
    # System actions
    SYSTEM_CONFIG = "system_config"
    BACKUP = "backup"
    RESTORE = "restore"
    
    # Security actions
    PERMISSION_CHANGE = "permission_change"
    ROLE_ASSIGN = "role_assign"


class AuditLog(Base):
    """Immutable audit log entry."""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Actor
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    user_email = Column(String(255))  # Denormalized for immutability
    user_role = Column(String(50))
    
    # Action details
    action = Column(Enum(AuditAction), nullable=False, index=True)
    category = Column(String(50), index=True)  # user, content, risk, system, etc.
    
    # Target object
    target_type = Column(String(50))  # article, user, source, etc.
    target_id = Column(String(100))
    target_name = Column(String(500))  # Human-readable identifier
    
    # Change details
    description = Column(Text, nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    
    # Risk context (for publish actions)
    risk_score = Column(String(10))
    safe_mode_enabled = Column(Boolean)
    risk_threshold = Column(String(10))
    
    # Version control
    version_hash = Column(String(64))  # Git commit hash or content hash
    
    # Request context
    ip_address = Column(INET)
    user_agent = Column(Text)
    request_id = Column(String(100))
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user": self.user_email,
            "action": self.action.value,
            "category": self.category,
            "target": f"{self.target_type}:{self.target_id}" if self.target_type else None,
            "description": self.description,
            "risk_score": self.risk_score,
            "safe_mode": self.safe_mode_enabled,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
    
    @staticmethod
    def create_entry(
        user_id: uuid.UUID,
        user_email: str,
        action: AuditAction,
        description: str,
        target_type: str = None,
        target_id: str = None,
        old_values: Dict = None,
        new_values: Dict = None,
        risk_context: Dict = None,
        **kwargs
    ) -> "AuditLog":
        """Factory method to create audit log entry."""
        entry = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            category=action.value.split("_")[0],
            description=description,
            target_type=target_type,
            target_id=target_id,
            old_values=old_values,
            new_values=new_values,
        )
        
        if risk_context:
            entry.risk_score = str(risk_context.get("score"))
            entry.safe_mode_enabled = risk_context.get("safe_mode")
            entry.risk_threshold = str(risk_context.get("threshold"))
        
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        
        return entry
