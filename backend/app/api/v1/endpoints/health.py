"""Health check endpoints"""

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.core.cache import CacheManager, get_cache
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
)
async def health_check():
    """
    Basic health check endpoint

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": "Stock Screening Platform API",
    }


@router.get(
    "/health/db",
    status_code=status.HTTP_200_OK,
    summary="Database health check",
)
async def health_check_db(db: AsyncSession = Depends(get_db)):
    """
    Check database connection health

    Args:
        db: Database session

    Returns:
        dict: Database health status
    """
    try:
        # Execute simple query to test connection
        result = await db.execute(text("SELECT 1"))
        result.scalar()

        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }


@router.get(
    "/health/redis",
    status_code=status.HTTP_200_OK,
    summary="Redis health check",
)
async def health_check_redis(cache: CacheManager = Depends(get_cache)):
    """
    Check Redis connection health

    Args:
        cache: Cache manager instance

    Returns:
        dict: Redis health status
    """
    try:
        # Test cache connection with ping
        if cache.redis:
            await cache.redis.ping()
            return {
                "status": "healthy",
                "redis": "connected",
            }
        return {
            "status": "unhealthy",
            "redis": "not initialized",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "redis": "disconnected",
            "error": str(e),
        }


@router.get(
    "/metrics",
    status_code=status.HTTP_200_OK,
    summary="Prometheus metrics endpoint",
    response_class=Response,
)
async def metrics():
    """
    Expose Prometheus metrics in text format.

    This endpoint is scraped by Prometheus to collect application metrics.
    Returns metrics in Prometheus text exposition format.

    Returns:
        Response: Prometheus metrics in text format
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
