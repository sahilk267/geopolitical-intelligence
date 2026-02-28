"""
Geopolitical Intelligence Platform - FastAPI Application
"""
import logging
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
    await init_db()
    logger.info("Database initialized")
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
