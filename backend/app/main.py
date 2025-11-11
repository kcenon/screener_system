"""Main FastAPI application"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.error_handlers import (app_exception_handler,
                                    generic_exception_handler,
                                    sqlalchemy_exception_handler,
                                    validation_exception_handler)
from app.api.v1.endpoints import auth, health, screening, stocks, websocket
from app.core.cache import cache_manager
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import logger
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.metrics import PrometheusMetricsMiddleware


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

    # Initialize WebSocket Redis Pub/Sub
    try:
        from app.core.websocket import connection_manager
        import asyncio

        await connection_manager.initialize_redis()
        logger.info("WebSocket Redis Pub/Sub initialized")

        # Phase 3: Start session cleanup task
        if not connection_manager._session_cleanup_task:
            connection_manager._session_cleanup_task = asyncio.create_task(
                connection_manager._cleanup_expired_sessions()
            )
            logger.info("WebSocket session cleanup task started")
    except Exception as e:
        logger.warning(f"Failed to initialize WebSocket Redis Pub/Sub: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Stock Screening Platform API...")

    # Phase 3: Stop session cleanup task
    try:
        from app.core.websocket import connection_manager

        if connection_manager._session_cleanup_task:
            connection_manager._session_cleanup_task.cancel()
            try:
                await connection_manager._session_cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("WebSocket session cleanup task stopped")
    except Exception as e:
        logger.warning(f"Error stopping session cleanup task: {e}")

    # Disconnect WebSocket Redis Pub/Sub
    try:
        from app.core.redis_pubsub import redis_pubsub

        await redis_pubsub.disconnect()
        logger.info("WebSocket Redis Pub/Sub disconnected")
    except Exception as e:
        logger.warning(f"Error disconnecting WebSocket Redis Pub/Sub: {e}")

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

# Prometheus metrics middleware (before logging to track all requests)
app.add_middleware(PrometheusMetricsMiddleware)

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

# Include WebSocket routes
app.include_router(websocket.router, prefix="/v1")

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
