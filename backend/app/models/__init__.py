"""
Geopolitical Intelligence Platform - Database Models
"""
from app.models.user import User, Role, UserRole, UserRoleLink

from app.models.source import Source, SourceType, SourceTier
from app.models.article import RawArticle, NormalizedArticle, ArticleStatus
from app.models.entity import Entity, EntityType, ArticleEntity

from app.models.claim import Claim, ClaimStatus
from app.models.contradiction import Contradiction, ContradictionStatus
from app.models.risk import RiskScore, RiskDimension
from app.models.eri import ERIAssessment, ERIDimension, ERIClassification

from app.models.script import Script, ScriptSegment, ScriptStatus, ScriptLayer

from app.models.video import VideoJob, VideoJobStatus
from app.models.audit import AuditLog, AuditAction
from app.models.brief import WeeklyBrief

__all__ = [
    "User",
    "Role",
    "UserRole",
    "UserRoleLink",
    "Source",

    "SourceType",
    "SourceTier",
    "RawArticle",
    "NormalizedArticle",
    "ArticleStatus",
    "Entity",
    "EntityType",
    "ArticleEntity",

    "Claim",
    "ClaimStatus",
    "Contradiction",
    "ContradictionStatus",
    "RiskScore",
    "RiskDimension",
    "ERIAssessment",
    "ERIDimension",
    "ERIClassification",
    "Script",
    "ScriptSegment",
    "ScriptStatus",
    "ScriptLayer",

    "VideoJob",
    "VideoJobStatus",
    "AuditLog",
    "AuditAction",
    "WeeklyBrief",
]
