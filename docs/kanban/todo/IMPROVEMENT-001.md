# [IMPROVEMENT-001] Rate Limiting Enhancements

## Metadata
- **Status**: TODO
- **Priority**: Medium
- **Assignee**: Development Team
- **Estimated Time**: 4 hours
- **Sprint**: Sprint 2 (Week 3-4)
- **Tags**: #improvement #rate-limiting #redis #configuration
- **Related Review**: docs/reviews/REVIEW_2025-11-09_initial-setup.md (Follow-up Review)
- **Related**: FEATURE-001 (Rate Limiting Middleware Implementation)

## Description
Improve the rate limiting middleware implementation to address atomicity concerns, externalize configuration values, and enhance maintainability.

## Issues Identified

### 1. Race Condition in Redis Operations
**File**: `backend/app/middleware/rate_limit.py:59-63`
**Severity**: Medium
**Impact**: Non-atomic operations could cause rate limit keys to persist without TTL if crash occurs between `incr` and `expire` commands.

Current implementation:
```python
current = await cache_manager.redis.incr(key)
if current == 1:
    await cache_manager.redis.expire(key, 60)
```

**Risk**: Very low in practice (Redis is single-threaded), but not atomic.

### 2. Hardcoded TTL Values
**File**: `backend/app/middleware/rate_limit.py:63, 85, 86, 97`
**Severity**: Medium
**Impact**: Rate limit window (60 seconds) hardcoded in multiple places, reducing configurability.

### 3. Hardcoded Whitelist Paths
**File**: `backend/app/middleware/rate_limit.py:18`
**Severity**: Low
**Impact**: Whitelist paths hardcoded in class constant, should be configurable.

## Subtasks

### Make Redis Operations Atomic
- [ ] Research Redis atomic operations options
  - [ ] Option A: Redis Lua script for incr+expire
  - [ ] Option B: Use SET with NX and EX flags
  - [ ] Option C: Use SETEX command pattern
- [ ] Implement chosen atomic approach
- [ ] Test atomicity with concurrent requests
- [ ] Update inline documentation

### Externalize Configuration Values
- [ ] Add `RATE_LIMIT_WINDOW` to `backend/app/core/config.py`
  - [ ] Default value: 60 seconds
  - [ ] Document in docstring
- [ ] Add `RATE_LIMIT_WHITELIST_PATHS` to config
  - [ ] Default: health check and docs endpoints
  - [ ] Support comma-separated string from env
- [ ] Update middleware to use config values
- [ ] Replace all hardcoded "60" references
- [ ] Update .env.example with new variables

### Testing
- [ ] Add unit tests for atomic operations
- [ ] Test rate limiting with different windows
- [ ] Verify whitelist configuration works
- [ ] Test edge cases (Redis failure, concurrent requests)

## Implementation Details

### Option A: Redis Lua Script (Recommended)
```python
# Lua script for atomic incr+expire
RATE_LIMIT_SCRIPT = """
local current = redis.call('incr', KEYS[1])
if current == 1 then
    redis.call('expire', KEYS[1], ARGV[1])
end
return current
"""

# In middleware
current = await cache_manager.redis.eval(
    RATE_LIMIT_SCRIPT,
    keys=[key],
    args=[settings.RATE_LIMIT_WINDOW]
)
```

### Option B: SET with NX/EX Pattern
```python
# Try to set with expiry first
success = await cache_manager.redis.set(
    key, 1, ex=settings.RATE_LIMIT_WINDOW, nx=True
)
if success:
    current = 1
else:
    current = await cache_manager.redis.incr(key)
```

### Configuration Updates
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # ... existing fields ...

    # ========================================================================
    # RATE LIMITING
    # ========================================================================

    RATE_LIMIT_FREE: int = 100
    RATE_LIMIT_BASIC: int = 500
    RATE_LIMIT_PRO: int = 2000
    RATE_LIMIT_WINDOW: int = 60  # seconds

    RATE_LIMIT_WHITELIST_PATHS: List[str] = [
        "/health",
        "/health/db",
        "/health/redis",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]

    @field_validator("RATE_LIMIT_WHITELIST_PATHS", mode="before")
    @classmethod
    def parse_whitelist_paths(cls, v):
        """Parse whitelist paths from comma-separated string or list"""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
```

### Middleware Updates
```python
# backend/app/middleware/rate_limit.py
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to implement rate limiting"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Use config instead of hardcoded whitelist
        if request.url.path in settings.RATE_LIMIT_WHITELIST_PATHS:
            return await call_next(request)

        # ... existing code ...

        # Use config for window
        current = await self._atomic_incr_with_ttl(
            key,
            settings.RATE_LIMIT_WINDOW
        )

        # ... rest of logic ...

    async def _atomic_incr_with_ttl(
        self, key: str, ttl: int
    ) -> int:
        """Atomically increment counter with TTL"""
        # Implementation of chosen atomic approach
        pass
```

## Acceptance Criteria
- [ ] Redis operations are atomic (no race condition possible)
- [ ] Rate limit window configurable via `RATE_LIMIT_WINDOW` env variable
- [ ] Whitelist paths configurable via `RATE_LIMIT_WHITELIST_PATHS` env variable
- [ ] No hardcoded TTL values in middleware code
- [ ] All existing rate limiting functionality preserved
- [ ] Unit tests cover atomic operations
- [ ] Documentation updated

## Dependencies
- **Depends on**: FEATURE-001 (completed)
- **Blocks**: None

## References
- **Review Document**: docs/reviews/REVIEW_2025-11-09_initial-setup.md (§ New Issues #1, #2, #4)
- **Redis Atomic Operations**: https://redis.io/docs/manual/programmability/eval-intro/
- **SET Command Options**: https://redis.io/commands/set/
- **Rate Limiting Patterns**: https://redis.io/glossary/rate-limiting/

## Progress
- **0%** - Not started

## Notes
- Lua script approach is most robust but requires Redis 2.6+
- SET with NX/EX is simpler but requires two calls for subsequent increments
- Current implementation is acceptable for MVP but should be improved for production
- Consider adding metrics for rate limit hits/misses
- Future: Consider sliding window algorithm instead of fixed window
