# [BUGFIX-004] Fix Rate Limiting Redis Script Error

## Metadata
- **Status**: TODO
- **Priority**: High
- **Assignee**: AI Assistant
- **Estimated Time**: 3 hours
- **Sprint**: Sprint 3
- **Tags**: #bugfix #rate-limiting #redis #backend
- **Created**: 2025-11-10

## Description
Rate limiting middleware is failing with a Redis script execution error: `ScriptCommands.eval() got an unexpected keyword argument 'keys'`. This prevents proper rate limiting enforcement.

## Error Details
```
2025-11-10 05:20:19 - screener - ERROR - Rate limiting error: ScriptCommands.eval() got an unexpected keyword argument 'keys'
```

## Root Cause
The Redis client API changed in newer versions. The `keys` parameter should be passed differently in redis-py 5.x vs 4.x.

## Subtasks
- [ ] Check current redis-py version in requirements.txt
- [ ] Review RateLimitMiddleware implementation
- [ ] Update Redis script execution syntax
- [ ] Test with both GET and POST endpoints
- [ ] Verify rate limit headers are returned
- [ ] Test 429 response when limit exceeded

## Acceptance Criteria
- [ ] No Redis script errors in logs
- [ ] Rate limiting middleware processes all requests
- [ ] X-RateLimit-* headers present in responses
- [ ] 429 response when limit exceeded
- [ ] Whitelist paths bypass rate limiting
- [ ] All acceptance criteria from FEATURE-001 still pass

## Fix Strategy
### Option 1: Update Script Execution (Recommended)
```python
# Old (redis-py 4.x)
await redis.eval(script, keys=[key], args=[limit, window])

# New (redis-py 5.x)
await redis.eval(script, numkeys=1, keys_and_args=[key, limit, window])
```

### Option 2: Downgrade redis-py
```txt
# requirements.txt
redis[hiredis]==4.6.0  # Instead of 5.x
```

## Dependencies
- **Depends on**: FEATURE-001 (rate limiting implementation)
- **Blocks**: None (but critical for production)

## Testing Plan
```bash
# Test rate limiting
for i in {1..10}; do
  curl -i http://localhost:8000/v1/stocks?limit=10
done

# Verify headers
curl -i http://localhost:8000/health | grep X-RateLimit

# Test 429 response
ab -n 200 -c 10 http://localhost:8000/v1/stocks?limit=10
```

## References
- **redis-py 5.0 changelog**: https://github.com/redis/redis-py/releases/tag/v5.0.0
- **Middleware**: `backend/app/middleware/rate_limit.py`
- **FEATURE-001**: Rate limiting implementation ticket

## Progress
- **0%** - Not started

## Notes
- This is likely caused by dependency version mismatch
- Check if redis-py was recently upgraded
- May need to update documentation for Redis compatibility
