# BUGFIX-007: Complete Docker Environment Runtime Testing

**Status**: TODO
**Priority**: High
**Assignee**: TBD
**Estimated Time**: 4 hours
**Sprint**: Sprint 4
**Tags**: docker, infrastructure, runtime-testing, validation

## Description

Multiple tickets (BUGFIX-001, FEATURE-001) have incomplete Docker runtime testing. While code has been written and unit tests pass, full stack integration testing in Docker environment has not been performed.

This ticket ensures all Docker-based services work correctly together in runtime environment.

## Root Cause

**Incomplete Runtime Validation**:
- Code reviewed and merged based on unit tests only
- Docker Compose health checks not validated in actual environment
- CORS functionality not tested from browser with real origins
- Middleware integration not verified end-to-end

**Affected Tickets**:
- BUGFIX-001: 6 unchecked runtime criteria
- FEATURE-001: 8 unchecked acceptance criteria
- BE-005: Monitoring dashboard deferred

## Impact

- **Production Risk**: Services may fail in production despite passing unit tests
- **Integration Issues**: Service-to-service communication not validated
- **Performance**: Real-world performance unknown (only synthetic tests)
- **User Experience**: CORS, rate limiting may not work as expected

## Subtasks

### Environment Setup
- [ ] Ensure Docker daemon running
- [ ] Clean up any existing containers
  ```bash
  docker-compose down -v
  docker system prune -f
  ```
- [ ] Verify .env file configured correctly
- [ ] Check port availability (5432, 6379, 8000, 8080, 5173)

### BUGFIX-001 Runtime Testing
- [ ] Start all services with Docker Compose
  ```bash
  docker-compose up -d
  ```
- [ ] Verify all services healthy
  ```bash
  docker-compose ps
  # Expected: All services show "healthy" status
  ```
- [ ] Test PostgreSQL connection
  ```bash
  docker-compose exec postgres psql -U screener_user -d screener_db -c "SELECT 1;"
  ```
- [ ] Test Redis authentication
  ```bash
  docker-compose exec redis redis-cli -a redis_password ping
  # Expected: PONG
  ```
- [ ] Test backend health checks
  ```bash
  curl http://localhost:8000/health
  curl http://localhost:8000/health/db
  curl http://localhost:8000/health/redis
  ```
- [ ] Test CORS from browser
  - Open http://localhost:5173
  - Open browser DevTools console
  - Execute: `fetch('http://localhost:8000/health').then(r => r.json()).then(console.log)`
  - Verify no CORS errors
- [ ] Test CORS rejection
  - Add different origin header manually
  - Verify CORS error returned

### FEATURE-001 Middleware Testing
- [ ] Test request logging middleware
  ```bash
  curl http://localhost:8000/v1/screen
  docker-compose logs backend | grep "Request started"
  # Verify: UUID, method, path logged
  ```
- [ ] Test rate limiting - tier limits
  ```bash
  # Test free tier (100 req/min)
  for i in {1..105}; do
    curl -s http://localhost:8000/ -o /dev/null
  done
  # 101st request should return 429
  ```
- [ ] Test rate limiting headers
  ```bash
  curl -v http://localhost:8000/
  # Verify headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
  ```
- [ ] Test endpoint-specific limits
  ```bash
  # Screening endpoint: 50 req/min
  for i in {1..55}; do
    curl -s -X POST http://localhost:8000/v1/screen -H "Content-Type: application/json" -d '{}' -o /dev/null
  done
  # 51st request should return 429
  ```
- [ ] Test whitelist paths (health, docs)
  ```bash
  # Should never be rate limited
  for i in {1..200}; do
    curl -s http://localhost:8000/health -o /dev/null
  done
  curl http://localhost:8000/health  # Should still return 200
  ```
- [ ] Verify sensitive data filtering
  ```bash
  # Login with password
  curl -X POST http://localhost:8000/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"secret123"}'

  # Check logs - password should NOT appear
  docker-compose logs backend | grep "secret123"
  # Expected: No results (password filtered)
  ```
- [ ] Test performance impact
  ```bash
  # Without middleware (baseline)
  # With middleware - should be < 5ms overhead
  wrk -t2 -c10 -d10s http://localhost:8000/health
  ```
- [ ] Test Redis unavailable scenario
  ```bash
  docker-compose stop redis
  curl http://localhost:8000/  # Should still work (graceful degradation)
  docker-compose start redis
  ```

### Service Integration Testing
- [ ] Test backend → database connection pooling
  ```bash
  # Run concurrent requests
  ab -n 1000 -c 50 http://localhost:8000/health/db
  # Check connection count
  docker-compose exec postgres psql -U screener_user -d screener_db -c \
    "SELECT count(*) FROM pg_stat_activity WHERE datname='screener_db';"
  ```
- [ ] Test backend → Redis caching
  ```bash
  # First request (cache miss)
  time curl http://localhost:8000/v1/screen
  # Second request (cache hit, should be faster)
  time curl http://localhost:8000/v1/screen
  ```
- [ ] Test service restart resilience
  ```bash
  docker-compose restart backend
  sleep 5
  curl http://localhost:8000/health  # Should work after restart
  ```

### Performance Baseline
- [ ] Measure cold start time
  ```bash
  docker-compose down
  time docker-compose up -d
  # Record: Time until all services healthy
  ```
- [ ] Measure API response times
  ```bash
  wrk -t4 -c100 -d30s http://localhost:8000/health
  # Record: avg, p50, p95, p99 latencies
  ```
- [ ] Measure screening API performance
  ```bash
  wrk -t4 -c100 -d30s -s post.lua http://localhost:8000/v1/screen
  # Verify: p99 < 500ms
  ```

## Acceptance Criteria

### BUGFIX-001 Complete
- [ ] `docker-compose up -d` starts all services successfully
- [ ] All services show "healthy" status in `docker-compose ps`
- [ ] PostgreSQL responds to queries
- [ ] Redis responds to authenticated ping
- [ ] Backend health check returns 200 OK
- [ ] Backend /health/db endpoint confirms database connection
- [ ] Backend /health/redis endpoint confirms Redis connection
- [ ] CORS requests work from allowed origins (localhost:5173)
- [ ] CORS requests blocked from disallowed origins

### FEATURE-001 Complete
- [ ] All requests logged with method, path, status, duration
- [ ] Sensitive data (passwords, tokens) filtered from logs
- [ ] Rate limiting enforced per tier (free: 100/min, basic: 500/min, pro: 2000/min)
- [ ] 429 status returned when limit exceeded
- [ ] Rate limit headers included in all responses (X-RateLimit-*)
- [ ] Whitelist paths (/health, /docs) bypass rate limiting
- [ ] Rate limits configurable via environment variables
- [ ] Performance impact < 5ms per request
- [ ] Graceful degradation when Redis unavailable

### Documentation
- [ ] Test results documented with evidence (logs, screenshots, metrics)
- [ ] Performance baseline metrics recorded
- [ ] Any issues found documented and resolved
- [ ] Runtime testing checklist added to TESTING.md

## Testing Steps

### Quick Validation
```bash
# Run automated test script
./scripts/test_all.sh

# Expected output:
# ✅ PostgreSQL OK
# ✅ Redis OK
# ✅ Backend Health OK
# ✅ Backend DB Connection OK
# ✅ Backend Redis Connection OK
# ✅ Rate Limiting OK
# ✅ Request Logging OK
```

### Manual Validation
```bash
# 1. Start services
docker-compose up -d

# 2. Check service status
docker-compose ps
# All services should be "healthy"

# 3. Test each component
curl http://localhost:8000/health
curl http://localhost:8000/health/db
curl http://localhost:8000/health/redis

# 4. Test rate limiting
for i in {1..105}; do curl http://localhost:8000/; done
# Request 101 should return 429

# 5. Check logs
docker-compose logs backend | tail -50
# Should see request logs with UUIDs
```

## Dependencies

- Docker installed and running
- Docker Compose v2.0+
- .env file configured
- All services built (`docker-compose build`)

## Blocks

- Production deployment confidence
- Accurate performance metrics
- BUGFIX-001 completion
- FEATURE-001 completion

## References

- BUGFIX-001: docs/kanban/done/BUGFIX-001.md
- FEATURE-001: docs/kanban/done/FEATURE-001.md
- TESTING.md: docs/TESTING.md
- Docker Compose: docker-compose.yml

## Progress

- **Current**: 0%
- **Updated**: 2025-11-11

## Notes

**Why This Matters**:
- Unit tests verify components work in isolation
- Runtime tests verify components work together
- This is the difference between "code works" and "system works"

**Common Issues to Watch For**:
- Docker network configuration
- Environment variable propagation
- Service startup order dependencies
- Port conflicts with local services

**Post-Completion Actions**:
- Update BUGFIX-001 and FEATURE-001 acceptance criteria
- Add results to Verification Report
- Create performance baseline document
- Schedule monthly runtime regression testing

---

**Created**: 2025-11-11
**Last Updated**: 2025-11-11
**Ticket Type**: Bug Fix - Runtime Testing
**Related Tickets**: BUGFIX-001, FEATURE-001, BE-005
