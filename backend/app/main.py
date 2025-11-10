"""Main FastAPI application"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api.error_handlers import (
    app_exception_handler,
    generic_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
from app.api.v1.endpoints import auth, health, screening, stocks
from app.core.cache import cache_manager
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import logger
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events

    Handles startup and shutdown events for the application.
    """
    # Startup
    logger.info("Starting Stock Screening Platform API...")

    # Connect to Redis
    try:
        await cache_manager.connect()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Stock Screening Platform API...")

    # Disconnect from Redis
    try:
        await cache_manager.disconnect()
        logger.info("Disconnected from Redis")
    except Exception as e:
        logger.warning(f"Error disconnecting from Redis: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Stock Screening Platform - Backend API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request logging middleware
app.add_middleware(LoggingMiddleware)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ============================================================================
# ROUTERS
# ============================================================================

# Include health check routes
app.include_router(health.router)

# Include authentication routes
app.include_router(auth.router, prefix="/v1")

# Include stock routes
app.include_router(stocks.router, prefix="/v1")

# Include screening routes
app.include_router(screening.router, prefix="/v1")

# ============================================================================
# ROOT ENDPOINT
# ============================================================================


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Stock Screening Platform API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
