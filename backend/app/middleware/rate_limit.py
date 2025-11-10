"""Rate limiting middleware"""

from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.cache import cache_manager
from app.core.config import settings
from app.core.logging import logger

# Lua script for atomic incr+expire operation
# This ensures that the counter is incremented and TTL is set atomically,
# preventing race conditions where a key might persist without expiration
RATE_LIMIT_SCRIPT = """
local current = redis.call('incr', KEYS[1])
if current == 1 then
    redis.call('expire', KEYS[1], ARGV[1])
end
return current
"""


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to implement rate limiting with atomic Redis operations"""

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
        if request.url.path in settings.RATE_LIMIT_WHITELIST_PATHS:
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

            # Atomically increment counter and set TTL
            # Using Lua script to ensure atomicity
            # redis-py 5.x API: eval(script, numkeys, *keys_and_args)
            current = await cache_manager.redis.eval(
                RATE_LIMIT_SCRIPT, 1, key, settings.RATE_LIMIT_WINDOW
            )

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
                        "X-RateLimit-Reset": str(settings.RATE_LIMIT_WINDOW),
                        "Retry-After": str(settings.RATE_LIMIT_WINDOW),
                    },
                )

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            remaining = max(0, limit - current)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(settings.RATE_LIMIT_WINDOW)

            return response

        except Exception as e:
            # Log error but don't block request if rate limiting fails
            logger.error(f"Rate limiting error: {e}")
            return await call_next(request)
