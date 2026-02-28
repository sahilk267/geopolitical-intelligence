"""
Geopolitical Intelligence Platform - Core Configuration
"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Geopolitical Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database - PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "geopolitical_intel"
    
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values) -> str:
        if isinstance(v, str):
            return v
        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"{values.get('POSTGRES_DB')}",
        ))

    
    # Neo4j Graph Database
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # RSS/API Ingestion
    RSS_FETCH_INTERVAL_MINUTES: int = 30
    MAX_ARTICLES_PER_FETCH: int = 50
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    # Risk Governance
    SAFE_MODE_ENABLED: bool = False
    RISK_THRESHOLD: int = 40
    
    # ERI Configuration
    ERI_DIMENSION_WEIGHTS: dict = {
        "military": 0.30,
        "political": 0.15,
        "proxy": 0.20,
        "economic": 0.15,
        "diplomatic": 0.20,
    }
    
    # AI/LLM Integration
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-1.5-pro"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 4000
    
    # Video Production
    VIDEO_OUTPUT_DIR: str = "./output/videos"
    TTS_ENGINE: str = "elevenlabs"  # or "azure"
    ELEVENLABS_API_KEY: Optional[str] = None
    
    # Audit & Logging
    AUDIT_LOG_RETENTION_DAYS: int = 365
    LOG_LEVEL: str = "INFO"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
