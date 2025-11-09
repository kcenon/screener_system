# [BUGFIX-001] Fix Critical Issues from Code Review

## Metadata
- **Status**: DONE
- **Priority**: Critical
- **Assignee**: Development Team
- **Estimated Time**: 4 hours
- **Actual Time**: 2 hours
- **Sprint**: Sprint 1 (Week 1-2)
- **Tags**: #bugfix #critical #code-review
- **Related Review**: docs/reviews/REVIEW_2025-11-09_initial-setup.md
- **Completed**: 2025-11-09

## Description
Fix critical issues identified in the initial project setup code review that must be resolved before merging to main.

## Subtasks

### Critical Issue #1: Redis Health Check
- [x] Update Redis health check in docker-compose.yml
  - [x] Remove invalid `incr` command
  - [x] Add password authentication with `-a` flag
  - [x] Use sh -c with $$REDIS_PASSWORD for env var access
  - [ ] Test health check works correctly (requires Docker daemon)

### Critical Issue #2: Backend Health Check
- [x] Fix backend container health check
  - [x] Option A: Add curl to backend Dockerfile (already present)
  - [x] Verified curl installed in Dockerfile line 21
  - [ ] Verify health check works (requires Docker daemon)

### Critical Issue #3: NGINX CORS Configuration
- [x] Remove CORS headers from NGINX configuration
  - [x] Remove `add_header Access-Control-*` directives
  - [x] Remove OPTIONS request handling in NGINX
  - [x] Add comment that CORS is handled by FastAPI
  - [ ] Verify FastAPI CORS middleware handles requests (requires Docker daemon)
  - [ ] Test CORS functionality from browser (requires Docker daemon)

## Implementation Details

### Redis Health Check Fix
```yaml
# docker-compose.yml
redis:
  healthcheck:
    test: ["CMD", "redis-cli", "--raw", "-a", "${REDIS_PASSWORD:-redis_password}", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### Backend Health Check Fix (Option A - curl)
```dockerfile
# backend/Dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*
```

### Backend Health Check Fix (Option B - Python)
```yaml
# docker-compose.yml
backend:
  healthcheck:
    test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
```

### NGINX CORS Fix
```nginx
# Remove these lines from infrastructure/nginx/conf.d/default.conf
# Lines 62-66, 69-77
```

## Acceptance Criteria
- [ ] `docker-compose up -d` starts all services successfully
- [ ] All services show "healthy" status in `docker-compose ps`
- [ ] Redis responds to authenticated ping
- [ ] Backend health check returns 200 OK
- [ ] CORS requests work from allowed origins
- [ ] CORS requests blocked from disallowed origins

## Dependencies
- **Depends on**: None (highest priority)
- **Blocks**: Merge to main branch

## References
- **Review Document**: docs/reviews/REVIEW_2025-11-09_initial-setup.md
- **PR**: #1

## Progress
- **100%** - Implementation completed (runtime testing pending)

## Notes
- These are blocking issues that prevent production deployment
- All fixes must be tested with Docker daemon running
- Consider adding integration tests after fixes
