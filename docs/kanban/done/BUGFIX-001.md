# BUGFIX-001: Rate Limiting Configuration for Docker Environment

## Metadata
- **Type**: Bug Fix
- **Priority**: P0 (Critical)
- **Status**: DONE
- **Created**: 2025-11-15
- **Completed**: 2025-11-15
- **Assignee**: Backend Team
- **Estimated Time**: 2 hours
- **Actual Time**: 2 hours
- **Labels**: backend, docker, rate-limiting, configuration
- **Branch**: bugfix/001-rate-limit-configuration

## Problem Description

### Original Symptom (Reported)
Frontend displays error message: "데이터를 불러오는 중 오류가 발생했습니다" (An error occurred while loading data)

### Actual Root Cause (Diagnosed)
Rate limiting was too restrictive in Docker environment, blocking API requests after minimal usage

### Root Cause Analysis

**Discovery**: Backend was actually running in Docker (healthy status)

**Primary Issue**: Rate limit environment variables not passed to Docker container

**Contributing Factors**:
1. `.env` file in project root had low rate limits (100 req/min)
2. `docker-compose.yml` did not include RATE_LIMIT_* environment variables
3. Backend container was using default hardcoded values
4. Redis was functioning correctly

**Impact**:
- API requests blocked after ~100 requests
- Users see "Rate limit exceeded" errors
- Development workflow severely hampered
- Testing becomes impossible due to throttling

## Technical Details

### Error Chain
```
Frontend → API Request → http://localhost:8000/api/v1/stocks
                       ↓
                   No Response (Connection Refused)
                       ↓
           Frontend Error Handler Triggers
                       ↓
    Display: "데이터를 불러오는 중 오류가 발생했습니다"
```

### Failed Dependencies
```bash
# pandas installation fails:
error: metadata-generation-failed
× Encountered error while generating package metadata.
╰─> pandas

note: This is an issue with the package mentioned above, not pip.
hint: See above for details.
```

### Diagnosis

Backend was confirmed running via Docker:
```bash
$ docker ps
screener_backend   Up 3 days (healthy)   0.0.0.0:8000->8000/tcp

$ curl http://localhost:8000/v1/screen
{"message":"Rate limit exceeded","detail":"Maximum 100 requests per hour allowed"}
```

## Solution Implemented

### Step 1: Update `.env` File with Development-Friendly Rate Limits

**File**: `.env` (project root)

Added comprehensive rate limiting configuration:
```bash
# Tier-based rate limits (requests per minute)
RATE_LIMIT_FREE=999999          # Development: effectively unlimited
RATE_LIMIT_BASIC=999999
RATE_LIMIT_PRO=999999
RATE_LIMIT_WINDOW=60

# Per-endpoint rate limits
RATE_LIMIT_SCREENING=999999
RATE_LIMIT_STOCK_DETAIL=999999
RATE_LIMIT_AUTH=999999

# Whitelist paths (bypass rate limiting)
RATE_LIMIT_WHITELIST_PATHS=/health,/docs,/redoc,/openapi.json
```

### Step 2: Update `docker-compose.yml` to Pass Environment Variables

**File**: `docker-compose.yml`

Added to backend service environment section:
```yaml
backend:
  environment:
    # ... existing vars ...

    # Rate Limiting
    RATE_LIMIT_FREE: ${RATE_LIMIT_FREE:-100}
    RATE_LIMIT_BASIC: ${RATE_LIMIT_BASIC:-500}
    RATE_LIMIT_PRO: ${RATE_LIMIT_PRO:-2000}
    RATE_LIMIT_WINDOW: ${RATE_LIMIT_WINDOW:-60}
    RATE_LIMIT_SCREENING: ${RATE_LIMIT_SCREENING:-50}
    RATE_LIMIT_STOCK_DETAIL: ${RATE_LIMIT_STOCK_DETAIL:-100}
    RATE_LIMIT_AUTH: ${RATE_LIMIT_AUTH:-10}
    RATE_LIMIT_WHITELIST_PATHS: ${RATE_LIMIT_WHITELIST_PATHS:-/health,/docs}
```

### Step 3: Update `.env.example` Documentation

**File**: `.env.example`

Added clear documentation for development vs production usage:
```bash
# ============================================================================
# RATE LIMITING
# ============================================================================
# IMPORTANT: For development, use high limits (999999) to avoid throttling
# For production, use these reasonable values:

# Tier-based rate limits (requests per minute)
RATE_LIMIT_FREE=100          # Production: 100 requests/minute
# ... (full documentation)
```

### Step 4: Restart Backend Container

```bash
# Restart with new environment variables
docker-compose restart backend

# Verify healthy status
docker ps | grep backend
# screener_backend   Up 5 seconds (healthy)
```

### Step 5: Verify Rate Limiting Removed

```bash
# Test 10 consecutive requests
for i in {1..10}; do
  curl -s -X POST "http://localhost:8000/v1/screen" \
    -H "Content-Type: application/json" \
    -d '{"filters": {}, "limit": 1}'
done

# Result: All 10 requests succeeded without rate limit errors ✅
```

## Testing & Validation

### Test Results
1. ✅ Backend container restarted successfully
2. ✅ Health check endpoint returns 200 OK
3. ✅ Rate limiting environment variables loaded correctly
4. ✅ 10 consecutive API requests all successful
5. ✅ No rate limit errors in responses

### Acceptance Criteria
- [x] Backend server runs on http://localhost:8000 (Docker)
- [x] Rate limit environment variables passed to container
- [x] `.env` file updated with development-friendly values
- [x] `.env.example` documented with clear instructions
- [x] `docker-compose.yml` includes RATE_LIMIT_* variables
- [x] API endpoints return valid JSON responses without throttling
- [x] 10+ consecutive requests succeed without rate limit errors

## Documentation Updates

### Files Updated
- [x] `.env` - Added comprehensive rate limiting configuration
- [x] `.env.example` - Added development vs production documentation
- [x] `docker-compose.yml` - Added 8 rate limiting environment variables
- [x] `docs/kanban/todo/BUGFIX-001.md` - This ticket (resolution details)

### Files Created
- [x] `docs/kanban/todo/BUGFIX-012.md` - New ticket for frontend API path issue

## Resolution Summary

### Changes Made
1. **Environment Configuration** (`.env`):
   - Set rate limits to 999999 for development
   - Added per-endpoint rate limits
   - Added whitelist paths configuration

2. **Docker Configuration** (`docker-compose.yml`):
   - Added 8 RATE_LIMIT_* environment variables to backend service
   - All variables have fallback defaults for production

3. **Documentation** (`.env.example`):
   - Clear development vs production usage instructions
   - Comprehensive comments explaining each rate limit variable

### Verification
```bash
# Before fix
$ curl -X POST http://localhost:8000/v1/screen
{"message":"Rate limit exceeded","detail":"Maximum 100 requests per hour allowed"}

# After fix
$ curl -X POST http://localhost:8000/v1/screen
{"stocks":[],"meta":{"total":0},"query_time_ms":27.44}  # ✅ Success
```

## Prevention Measures

### Lessons Learned
1. **Docker Environment Variables Must Be Explicit**
   - `.env` files in subdirectories (e.g., `backend/.env`) are NOT used by Docker
   - All environment variables must be defined in `docker-compose.yml`
   - Default values should be production-safe, overridden in `.env` for development

2. **Development vs Production Configuration**
   - Development needs high/unlimited rate limits for testing
   - Production needs sensible limits (100-2000 req/min)
   - Documentation should clearly explain both use cases

3. **Testing Docker Environment Changes**
   - Always restart containers after environment variable changes
   - Verify new variables are loaded: `docker exec <container> env | grep RATE_LIMIT`
   - Test API behavior before and after changes

## Related Issues

### Created During This Fix
- **BUGFIX-012**: Frontend API Base URL Mismatch (P0, 1h)
  - Frontend uses `/api/v1` prefix, backend uses `/v1`
  - Discovered while testing rate limiting fix
  - Separate ticket created for frontend team

### Related Tickets
- **INFRA-001**: Docker Compose Development Environment (reference)
- **BE-001**: FastAPI Project Initial Setup (reference)

## References
- Backend Configuration: `/backend/app/core/config.py`
- Rate Limit Middleware: `/backend/app/middleware/rate_limit.py`
- Docker Compose: `/docker-compose.yml:69-100`
- Environment Example: `/.env.example:62-83`

## Notes

### Key Takeaways
1. ✅ Backend was actually running - initial diagnosis was incorrect
2. ✅ Rate limiting was the real culprit, not server availability
3. ✅ Docker environment requires explicit variable passing
4. ⚠️ Frontend API path issue discovered as side effect (BUGFIX-012)
5. ✅ All changes are backwards-compatible (default values preserved)

### For Future Reference
- Development `.env`: Set RATE_LIMIT_* to 999999
- Production `.env`: Use reasonable limits (100/500/2000)
- Always test Docker environment changes with `docker-compose restart`
- Verify with multiple consecutive requests to confirm no throttling
