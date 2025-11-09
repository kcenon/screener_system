# [FEATURE-001] Implement Missing Middleware

## Metadata
- **Status**: TODO
- **Priority**: Medium
- **Assignee**: TBD
- **Estimated Time**: 6 hours
- **Sprint**: Sprint 1 (Week 1-2)
- **Tags**: #feature #middleware #backend
- **Related**: BE-001 (remaining subtasks)

## Description
Implement the missing middleware components that were identified in the BE-001 requirements but not yet completed.

## Subtasks

### Request Logging Middleware
- [ ] Create `app/middleware/logging.py`
  - [ ] Implement request/response logging
  - [ ] Log request method, path, status code
  - [ ] Log request duration
  - [ ] Include request ID for tracing
  - [ ] Filter sensitive data (passwords, tokens)
  - [ ] Configure log format and destination
- [ ] Add middleware to `app/main.py`
- [ ] Test logging output
- [ ] Document configuration options

### Rate Limiting Middleware
- [ ] Create `app/middleware/rate_limit.py`
  - [ ] Implement Redis-based rate limiting
  - [ ] Support different limits per subscription tier
    - [ ] Free: 100 requests/minute
    - [ ] Basic: 500 requests/minute
    - [ ] Pro: 2000 requests/minute
  - [ ] Return 429 status code when limit exceeded
  - [ ] Include rate limit headers
    - [ ] X-RateLimit-Limit
    - [ ] X-RateLimit-Remaining
    - [ ] X-RateLimit-Reset
  - [ ] Support per-user and per-IP rate limiting
- [ ] Add middleware to `app/main.py`
- [ ] Test rate limiting behavior
- [ ] Document configuration

### Request ID Middleware (Optional)
- [ ] Create `app/middleware/request_id.py`
  - [ ] Generate unique request ID
  - [ ] Add to response headers
  - [ ] Include in logs
  - [ ] Support X-Request-ID header passthrough

## Implementation Details

### Logging Middleware
```python
# app/middleware/logging.py
import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Duration: {duration:.3f}s"
        )

        return response
```

### Rate Limiting Middleware
```python
# app/middleware/rate_limit.py
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.cache import cache_manager
from app.core.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get user tier (from auth or default to free)
        tier = getattr(request.state, "user_tier", "free")

        # Get rate limit for tier
        limits = {
            "free": settings.RATE_LIMIT_FREE,
            "basic": settings.RATE_LIMIT_BASIC,
            "pro": settings.RATE_LIMIT_PRO,
        }
        limit = limits.get(tier, settings.RATE_LIMIT_FREE)

        # Check rate limit
        key = f"rate_limit:{request.client.host}:{tier}"
        current = await cache_manager.redis.incr(key)

        if current == 1:
            await cache_manager.redis.expire(key, 60)  # 1 minute window

        if current > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current))

        return response
```

### Middleware Registration
```python
# app/main.py
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

# Add after CORS middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
```

## Acceptance Criteria
- [ ] All requests logged with method, path, status, duration
- [ ] Sensitive data (passwords, tokens) filtered from logs
- [ ] Rate limiting enforced per tier
- [ ] 429 status returned when limit exceeded
- [ ] Rate limit headers included in all responses
- [ ] Rate limits configurable via environment variables
- [ ] Middleware tests pass
- [ ] Performance impact < 5ms per request

## Dependencies
- **Depends on**: BUGFIX-001 (for working Redis)
- **Blocks**: None

## References
- **BE-001**: Middleware subtasks (lines 49-50)
- **FastAPI Middleware**: https://fastapi.tiangolo.com/advanced/middleware/
- **Rate Limiting Pattern**: https://redis.io/glossary/rate-limiting/

## Progress
- **0%** - Not started

## Notes
- Use Redis for rate limiting state
- Consider using slowapi library for rate limiting
- Ensure middleware order is correct (logging last)
- Add whitelist for health check endpoints
- Consider adding Prometheus metrics in logging middleware
