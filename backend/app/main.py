"""
Geopolitical Intelligence Platform - FastAPI Application
"""
import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.init_db import init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting up Geopolitical Intelligence Platform...")
    from app.db.init_db import create_initial_data
    from app.db.base import AsyncSessionLocal
    
    await init_db()
    
    # Seed data if necessary
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        from app.models.user import User
        from app.models.setting import PlatformSetting
        from app.core.config import settings as app_settings
        
        # Load API keys from database into in-memory settings
        result = await db.execute(select(PlatformSetting).where(PlatformSetting.category == "security"))
        for setting in result.scalars().all():
            if setting.key == "gemini_api_key":
                app_settings.GEMINI_API_KEY = setting.value
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=setting.value)
                    from app.services.ai_service import ai_service
                    ai_service.model = genai.GenerativeModel(app_settings.LLM_MODEL)
                except Exception as e:
                    logger.error(f"Failed to configure Gemini generated model on startup: {e}")
            elif setting.key == "llm_model":
                app_settings.LLM_MODEL = setting.value
                # If Gemini is provider, re-init model
                if app_settings.AI_PROVIDER == "gemini":
                    try:
                        import google.generativeai as genai
                        from app.services.ai_service import ai_service
                        ai_service.model = genai.GenerativeModel(setting.value)
                    except: pass
            elif setting.key == "ai_provider":
                app_settings.AI_PROVIDER = setting.value
            elif setting.key == "ollama_base_url":
                app_settings.OLLAMA_BASE_URL = setting.value
            elif setting.key == "elevenlabs_api_key":
                app_settings.ELEVENLABS_API_KEY = setting.value
            elif setting.key == "did_api_key":
                app_settings.DID_API_KEY = setting.value
            elif setting.key == "heygen_api_key":
                app_settings.HEYGEN_API_KEY = setting.value
                
        result = await db.execute(select(User).limit(1))
        if not result.scalar_one_or_none():
            logger.info("Seeding initial data...")
            await create_initial_data(db)
            logger.info("Database seeded")
        else:
            logger.info("Database already contains data, skipping seed")
    
    logger.info("Database initialized with loaded settings")
    
    # Start background scheduler
    from app.core.scheduler import poll_sources_task
    asyncio.create_task(poll_sources_task())
    logger.info("Background scheduler started")
    
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Academic geopolitical intelligence platform with risk governance",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"], include_in_schema=False)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Academic geopolitical intelligence platform",
        "docs": "/api/docs",
    }


# Import and include routers
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
    automation,
    reports,
    audio,
    settings as settings_api,
    pipeline,
    distribution,
    profiles,
    campaigns,
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["Sources"])
app.include_router(articles.router, prefix="/api/v1/articles", tags=["Articles"])
app.include_router(entities.router, prefix="/api/v1/entities", tags=["Entities"])
app.include_router(claims.router, prefix="/api/v1/claims", tags=["Claims"])
app.include_router(contradictions.router, prefix="/api/v1/contradictions", tags=["Contradictions"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["Risk Assessment"])
app.include_router(eri.router, prefix="/api/v1/eri", tags=["ERI"])
app.include_router(scripts.router, prefix="/api/v1/scripts", tags=["Scripts"])
app.include_router(videos.router, prefix="/api/v1/videos", tags=["Video Production"])
app.include_router(briefs.router, prefix="/api/v1/briefs", tags=["Weekly Briefs"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit Logs"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(automation.router, prefix="/api/v1/automation", tags=["Automation"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(audio.router, prefix="/api/v1/audio", tags=["Audio"])
app.include_router(settings_api.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(pipeline.router, prefix="/api/v1/pipeline", tags=["Pipeline"])
app.include_router(distribution.router, prefix="/api/v1/distribution", tags=["Distribution"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["Profiles"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["Campaigns"])

# Static file serving for generated media (audio, video, thumbnails)
import os
from starlette.staticfiles import StaticFiles

output_dir = settings.VIDEO_OUTPUT_DIR
os.makedirs(output_dir, exist_ok=True)
app.mount("/output", StaticFiles(directory=output_dir), name="output")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
