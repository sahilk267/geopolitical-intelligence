"""
API Endpoints Package
"""
from app.api.v1.endpoints import (
    auth,
    users,
    sources,
    articles,
    entities,
    claims,
    contradictions,
    risk,
    eri,
    scripts,
    videos,
    briefs,
    audit,
    dashboard,
)

__all__ = [
    "auth",
    "users",
    "sources",
    "articles",
    "entities",
    "claims",
    "contradictions",
    "risk",
    "eri",
    "scripts",
    "videos",
    "briefs",
    "audit",
    "dashboard",
]
