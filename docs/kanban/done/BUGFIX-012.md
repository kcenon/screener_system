# BUGFIX-012: Frontend API Base URL Mismatch

## Metadata
- **Type**: Bug Fix
- **Priority**: P0 (Critical)
- **Status**: DONE
- **Created**: 2025-11-15
- **Completed**: 2025-11-15
- **Assignee**: Frontend Team
- **Estimated Time**: 1 hour
- **Actual Time**: 0.5 hours
- **Labels**: frontend, api, configuration, critical
- **Parent**: BUGFIX-001 (discovered during rate limit fix)

## Problem Description

### Symptom
Frontend displays error: "데이터를 불러오는 중 오류가 발생했습니다" (An error occurred while loading data)

All API requests return 404 Not Found.

### Root Cause
**Frontend API Base URL mismatch with backend routes:**

```typescript
// Frontend (src/services/api.ts)
const API_BASE_URL = 'http://localhost:8000/api/v1'
                                          // ^^^^^ Extra /api prefix

// Backend (app/main.py)
app.include_router(screening.router, prefix="/v1")
                                     // ^^^^^^^^^^ No /api prefix
```

### Impact
- All frontend API calls fail with 404 errors
- Users cannot access any stock data
- Application is completely unusable
- Discovered as side effect while fixing rate limiting (BUGFIX-001)

## Technical Details

### Error Chain
```
Frontend Request:
  GET http://localhost:8000/api/v1/screen
                           ^^^^^^^
                           Incorrect prefix
       ↓
Backend Routes:
  GET http://localhost:8000/v1/screen
                           ^^^^
                           Correct prefix
       ↓
Result: 404 Not Found
```

### Actual Backend Routes (from OpenAPI spec)
```
/health
/v1/auth/login
/v1/auth/register
/v1/market/indices
/v1/screen
/v1/screen/templates
```

## Solution

### Option 1: Fix Frontend Base URL (Recommended)
Update frontend API configuration to match backend routes.

**File**: `frontend/src/services/api.ts`

```typescript
// Before
const API_BASE_URL = 'http://localhost:8000/api/v1'

// After
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/v1'
```

**File**: `frontend/.env`
```bash
# Before
VITE_API_BASE_URL=http://localhost:8000/api/v1

# After
VITE_API_BASE_URL=http://localhost:8000/v1
```

**File**: `frontend/.env.example`
```bash
# Update documentation
VITE_API_BASE_URL=http://localhost:8000/v1
```

### Option 2: Update Backend Routes (Not Recommended)
Add `/api` prefix to all backend routes.

**File**: `backend/app/main.py`
```python
# Before
app.include_router(screening.router, prefix="/v1")

# After
app.include_router(screening.router, prefix="/api/v1")
```

**Why Not Recommended:**
- Requires changing all route registrations
- OpenAPI spec would change
- Documentation would need updates
- More breaking changes

## Implementation Steps

1. Update frontend API base URL configuration
2. Update environment files (.env, .env.example)
3. Clear browser cache and localStorage
4. Test all API endpoints
5. Verify frontend loads data correctly

## Testing Checklist

- [x] Frontend successfully calls `/v1/screen`
- [x] Frontend successfully calls `/v1/auth/login`
- [x] Frontend successfully calls `/v1/market/indices`
- [x] No 404 errors in browser console
- [x] Stock screener page loads data
- [x] Market overview displays correctly

## Acceptance Criteria

- [x] Frontend API Base URL is `http://localhost:8000/v1`
- [x] All API endpoints return 200 OK
- [x] Frontend loads data without errors
- [x] No "데이터를 불러오는 중 오류가 발생했습니다" message
- [x] Browser console shows no 404 errors

## Related Issues

- BUGFIX-001: Rate Limiting Configuration (parent ticket)
- BE-001: Backend API Initial Setup
- FE-001: Frontend Project Setup

## References

- Backend Router Configuration: `/backend/app/main.py:195-217`
- Frontend API Client: `/frontend/src/services/api.ts:23`
- OpenAPI Spec: `http://localhost:8000/openapi.json`

## Implementation Result

### Files Changed
1. **frontend/src/services/api.ts** (line 21, 23)
   - Updated `API_BASE_URL` default from `http://localhost:8000/api/v1` to `http://localhost:8000/v1`
   - Updated JSDoc `@defaultValue` annotation to match

2. **frontend/.env** (line 2)
   - Updated `VITE_API_BASE_URL` from `http://localhost:8000/api/v1` to `http://localhost:8000/v1`

3. **frontend/.env.example** (line 2)
   - Updated `VITE_API_BASE_URL` template from `http://localhost:8000/api/v1` to `http://localhost:8000/v1`

### Summary
- Fixed API path mismatch by removing `/api` prefix from all frontend configuration
- No backend changes required
- Minimal, focused change affecting only 3 lines across 2 tracked files
- Solution aligned with recommended Option 1 from ticket analysis

## Notes

- This issue was discovered while fixing BUGFIX-001 (rate limiting)
- Backend routes are correctly configured at `/v1/*`
- Frontend was incorrectly using `/api/v1/*` prefix
- Simple configuration fix, no code logic changes required
- Completed in 0.5 hours (estimated 1 hour)
