"""
User and Role Management Models
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserRole(str, PyEnum):
    """User role enumeration."""
    ADMIN = "admin"
    EDITOR_IN_CHIEF = "editor_in_chief"
    SENIOR_EDITOR = "senior_editor"
    JUNIOR_EDITOR = "junior_editor"
    VIEWER = "viewer"


class Role(Base):
    """Role definition model."""
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(Text)  # JSON string of permissions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=UserRoleLink.__table__, back_populates="roles", foreign_keys=[UserRoleLink.user_id, UserRoleLink.role_id])


class UserRoleLink(Base):

    """User-Role association table."""
    __tablename__ = "user_roles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    
    # Role
    primary_role = Column(Enum(UserRole), default=UserRole.VIEWER)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Security
    last_login = Column(DateTime)
    failed_login_attempts = Column(String(10), default="0")
    password_changed_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=UserRoleLink.__table__, back_populates="users", foreign_keys=[UserRoleLink.role_id, UserRoleLink.user_id])
    audit_logs = relationship("AuditLog", back_populates="user")
    scripts = relationship("Script", back_populates="created_by_user")
    
    def has_role(self, role: UserRole) -> bool:
        """Check if user has specific role."""
        return self.primary_role == role or any(r.name == role.value for r in self.roles)
    
    def can_approve_risk(self, risk_score: int) -> bool:
        """Check if user can approve content with given risk score."""
        approval_limits = {
            UserRole.JUNIOR_EDITOR: 20,
            UserRole.SENIOR_EDITOR: 40,
            UserRole.EDITOR_IN_CHIEF: 100,
            UserRole.ADMIN: 100,
        }
        limit = approval_limits.get(self.primary_role, 0)
        return limit >= risk_score
