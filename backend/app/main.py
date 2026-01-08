"""Main FastAPI application entry point.

This module initializes and configures the Stock Screening Platform FastAPI application,
including middleware, exception handlers, and API route registration.

The application provides REST API endpoints for:
    - Stock screening with 200+ indicators
    - Real-time price data via WebSocket
    - User authentication and authorization
    - Portfolio management and price alerts

Example:
    Start the development server::

        $ uvicorn app.main:app --reload

    Or run directly::

        $ python -m app.main

    The API documentation will be available at http://localhost:8000/docs

Attributes:
    app: Main FastAPI application instance with all routes and middleware configured.
"""

from contextlib import asynccontextmanager

from app.api.error_handlers import (app_exception_handler,
                                    generic_exception_handler,
                                    sqlalchemy_exception_handler,
                                    validation_exception_handler)
from app.api.v1.endpoints import ai_analysis  # Added ai_analysis
from app.api.v1.endpoints import (ai, alerts, auth, health, market,
                                  notifications, oauth, portfolios,
                                  recommendation, screening, stocks,
                                  subscriptions, users, webhooks, websocket)
from app.core.cache import cache_manager
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import logger
from app.middleware.logging import LoggingMiddleware
from app.middleware.metrics import PrometheusMetricsMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.exc import SQLAlchemyError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown events.

    Manages the application lifecycle, handling resource initialization on startup
    and cleanup on shutdown. This includes Redis connections, WebSocket pub/sub,
    and background cleanup tasks.

    Args:
        app: FastAPI application instance.

    Yields:
        None: Control to the application during its lifecycle.

    Note:
        This function uses FastAPI's lifespan context manager pattern (recommended
        over deprecated startup/shutdown events).

    Startup tasks:
        - Connect to Redis cache
        - Initialize WebSocket Redis pub/sub
        - Start WebSocket session cleanup background task

    Shutdown tasks:
        - Stop WebSocket session cleanup task
        - Disconnect WebSocket Redis pub/sub
        - Disconnect from Redis cache

    Example:
        This function is automatically called by FastAPI when the application starts::

            app = FastAPI(lifespan=lifespan)
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
        import asyncio

        from app.core.websocket import connection_manager

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
app.include_router(health.router, prefix="/v1")

# Include AI routes
app.include_router(ai.router, prefix=settings.API_V1_STR)
app.include_router(
    recommendation.router,
    prefix=settings.API_V1_STR + "/recommendations",
    tags=["recommendations"],
)
app.include_router(
    ai_analysis.router,
    prefix=settings.API_V1_STR + "/ai",
    tags=["ai-analysis"],
)

# Include authentication routes
app.include_router(auth.router, prefix="/v1")

# Include OAuth routes
app.include_router(oauth.router, prefix="/v1")

# Include user routes
app.include_router(users.router, prefix="/v1")

# Include portfolio management routes
app.include_router(portfolios.router, prefix="/v1")

# Include alert routes
app.include_router(alerts.router, prefix="/v1")

# Include notification routes
app.include_router(notifications.router, prefix="/v1")

# Include subscription routes
app.include_router(subscriptions.router, prefix="/v1")

# Include webhook routes (no /v1 prefix for Stripe webhooks)
app.include_router(webhooks.router, prefix="/v1")

# Include stock routes
app.include_router(stocks.router, prefix="/v1")

# Include market overview routes
app.include_router(market.router, prefix="/v1")

# Include screening routes
app.include_router(screening.router, prefix="/v1")

# Include recommendation routes
app.include_router(recommendation.router, prefix="/v1")

# Include WebSocket routes
app.include_router(websocket.router, prefix="/v1")

# ============================================================================
# ROOT ENDPOINT
# ============================================================================


@app.get("/", tags=["root"])
async def root():
    """Root API endpoint providing basic information and navigation links.

    Returns a welcome message and links to important API endpoints including
    documentation, health check, and version information.

    Returns:
        dict: API information containing:
            - message (str): Welcome message
            - version (str): Current API version
            - docs (str): URL path to Swagger UI documentation
            - health (str): URL path to health check endpoint

    Example:
        >>> response = await root()
        >>> print(response["message"])
        Welcome to Stock Screening Platform API
        >>> print(response["docs"])
        /docs
    """
    return {
        "message": "Welcome to Stock Screening Platform API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
