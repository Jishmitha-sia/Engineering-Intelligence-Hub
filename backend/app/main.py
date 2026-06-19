"""
Engineering Intelligence Hub - FastAPI Main Application

AI-powered engineering knowledge platform backend.
"""

from contextlib import asynccontextmanager
from datetime import datetime
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(str(Path(__file__).parent))

from config import settings, get_cors_origins
from core.exceptions import register_exception_handlers
from db.session import (
    check_database_connection,
    close_database_connections,
    init_database,
)
from utils.logging import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    await init_database()
    yield
    await close_database_connections()


app = FastAPI(
    title="Engineering Intelligence Hub API",
    description="AI-powered engineering knowledge platform for software teams",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    db_healthy = await check_database_connection()
    status_value = "healthy" if db_healthy else "degraded"

    return {
        "status": status_value,
        "service": "engineering-intelligence-hub-backend",
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "checks": {
            "database": "up" if db_healthy else "down",
        },
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Engineering Intelligence Hub API",
        "version": settings.VERSION,
        "documentation": "/docs",
        "health": "/health",
    }


from api.v1.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
