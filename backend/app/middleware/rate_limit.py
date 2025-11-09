"""Rate limiting middleware"""

from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.cache import cache_manager
from app.core.config import settings
from app.core.logging import logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to implement rate limiting"""

    # Whitelist paths that should not be rate limited
    WHITELIST_PATHS = ["/health", "/health/db", "/health/redis", "/docs", "/redoc", "/openapi.json"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Apply rate limiting based on user tier

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response from next handler or 429 if rate limit exceeded
        """
        # Skip rate limiting for whitelisted paths
        if request.url.path in self.WHITELIST_PATHS:
            return await call_next(request)

        # Get user tier from request state (set by auth middleware)
        # Default to 'free' if not authenticated
        tier = getattr(request.state, "user_tier", "free")

        # Get rate limit for tier
        limits = {
            "free": settings.RATE_LIMIT_FREE,
            "basic": settings.RATE_LIMIT_BASIC,
            "pro": settings.RATE_LIMIT_PRO,
        }
        limit = limits.get(tier, settings.RATE_LIMIT_FREE)

        # Create rate limit key
        # Use IP address as identifier (in production, use user ID if authenticated)
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}:{tier}"

        try:
            # Check if Redis is available
            if not cache_manager.redis:
                logger.warning("Redis not available, skipping rate limiting")
                return await call_next(request)

            # Increment counter
            current = await cache_manager.redis.incr(key)

            # Set expiry on first request (1 minute window)
            if current == 1:
                await cache_manager.redis.expire(key, 60)

            # Check if limit exceeded
            if current > limit:
                logger.warning(
                    f"Rate limit exceeded | "
                    f"IP: {client_ip} | "
                    f"Tier: {tier} | "
                    f"Current: {current} | "
                    f"Limit: {limit}"
                )

                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "success": False,
                        "message": "Rate limit exceeded",
                        "detail": f"Maximum {limit} requests per minute allowed for {tier} tier",
                    },
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": "60",
                        "Retry-After": "60",
                    },
                )

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            remaining = max(0, limit - current)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = "60"

            return response

        except Exception as e:
            # Log error but don't block request if rate limiting fails
            logger.error(f"Rate limiting error: {e}")
            return await call_next(request)
