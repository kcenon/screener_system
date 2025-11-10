"""Rate limiting middleware with per-endpoint and KIS API quota management"""

from typing import Callable, Dict, Optional

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

# Per-endpoint rate limit configuration
# Maps path patterns to their specific rate limits (requests per hour)
ENDPOINT_RATE_LIMITS: Dict[str, int] = {
    "/v1/screen": settings.RATE_LIMIT_SCREENING,
    "/v1/stocks/": settings.RATE_LIMIT_STOCK_DETAIL,  # Matches /v1/stocks/{code}
    "/v1/auth/register": settings.RATE_LIMIT_AUTH,
    "/v1/auth/login": settings.RATE_LIMIT_AUTH,
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to implement rate limiting with atomic Redis operations"""

    def _get_endpoint_limit(self, path: str) -> Optional[int]:
        """
        Get endpoint-specific rate limit if configured

        Args:
            path: Request path

        Returns:
            Endpoint rate limit or None if not configured
        """
        for endpoint_pattern, limit in ENDPOINT_RATE_LIMITS.items():
            if path.startswith(endpoint_pattern):
                return limit
        return None

    async def _check_rate_limit(
        self, key: str, limit: int, window: int, identifier: str, limit_type: str
    ) -> tuple[bool, int]:
        """
        Check rate limit for a specific key

        Args:
            key: Redis key for rate limiting
            limit: Maximum allowed requests
            window: Time window in seconds
            identifier: Client identifier for logging
            limit_type: Type of limit (tier/endpoint) for logging

        Returns:
            Tuple of (is_allowed, current_count)
        """
        # Check if Redis is available
        if not cache_manager.redis:
            logger.warning("Redis not available, skipping rate limiting")
            return True, 0

        # Atomically increment counter and set TTL
        current = await cache_manager.redis.eval(
            RATE_LIMIT_SCRIPT, 1, key, window
        )

        # Check if limit exceeded
        if current > limit:
            logger.warning(
                f"Rate limit exceeded | "
                f"Type: {limit_type} | "
                f"Identifier: {identifier} | "
                f"Current: {current} | "
                f"Limit: {limit} | "
                f"Window: {window}s"
            )
            return False, current

        return True, current

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Apply rate limiting based on user tier and endpoint

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
        tier_limits = {
            "free": settings.RATE_LIMIT_FREE,
            "basic": settings.RATE_LIMIT_BASIC,
            "pro": settings.RATE_LIMIT_PRO,
        }
        tier_limit = tier_limits.get(tier, settings.RATE_LIMIT_FREE)

        # Use IP address as identifier (in production, use user ID if authenticated)
        client_ip = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", client_ip)

        try:
            # 1. Check tier-based rate limit
            tier_key = f"rate_limit:tier:{user_id}:{tier}"
            tier_allowed, tier_current = await self._check_rate_limit(
                tier_key, tier_limit, settings.RATE_LIMIT_WINDOW, user_id, f"tier-{tier}"
            )

            if not tier_allowed:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "success": False,
                        "message": "Rate limit exceeded",
                        "detail": f"Maximum {tier_limit} requests per hour allowed for {tier} tier",
                    },
                    headers={
                        "X-RateLimit-Limit": str(tier_limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(settings.RATE_LIMIT_WINDOW),
                        "Retry-After": str(settings.RATE_LIMIT_WINDOW),
                    },
                )

            # 2. Check endpoint-specific rate limit (if configured)
            endpoint_limit = self._get_endpoint_limit(request.url.path)
            endpoint_current = tier_current  # Default to tier current

            if endpoint_limit is not None:
                endpoint_key = f"rate_limit:endpoint:{user_id}:{request.url.path}"
                endpoint_allowed, endpoint_current = await self._check_rate_limit(
                    endpoint_key, endpoint_limit, settings.RATE_LIMIT_WINDOW,
                    user_id, f"endpoint-{request.url.path}"
                )

                if not endpoint_allowed:
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "success": False,
                            "message": "Endpoint rate limit exceeded",
                            "detail": f"Maximum {endpoint_limit} requests per hour allowed for {request.url.path}",
                        },
                        headers={
                            "X-RateLimit-Limit": str(endpoint_limit),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(settings.RATE_LIMIT_WINDOW),
                            "X-RateLimit-Endpoint": request.url.path,
                            "Retry-After": str(settings.RATE_LIMIT_WINDOW),
                        },
                    )

            # Process request
            response = await call_next(request)

            # Add rate limit headers (use endpoint limit if available, else tier limit)
            active_limit = endpoint_limit if endpoint_limit is not None else tier_limit
            active_current = endpoint_current if endpoint_limit is not None else tier_current
            remaining = max(0, active_limit - active_current)

            response.headers["X-RateLimit-Limit"] = str(active_limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(settings.RATE_LIMIT_WINDOW)

            if endpoint_limit is not None:
                response.headers["X-RateLimit-Endpoint"] = request.url.path

            return response

        except Exception as e:
            # Log error but don't block request if rate limiting fails
            logger.error(f"Rate limiting error: {e}")
            return await call_next(request)
