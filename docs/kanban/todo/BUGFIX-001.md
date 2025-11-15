# BUGFIX-001: Frontend Data Loading Error - Backend Server Not Running

## Metadata
- **Type**: Bug Fix
- **Priority**: P0 (Critical)
- **Status**: TODO
- **Created**: 2025-11-15
- **Assignee**: Backend Team
- **Estimated Time**: 2 hours
- **Labels**: backend, deployment, dependencies, critical

## Problem Description

### Symptom
Frontend displays error message: "데이터를 불러오는 중 오류가 발생했습니다" (An error occurred while loading data)

### Root Cause Analysis

**Primary Issue**: Backend server is not running

**Contributing Factors**:
1. Python dependencies not installed
   - pandas compilation fails with ninja build error
   - uvicorn module missing
2. No virtual environment configured for backend
3. Backend .env file was missing (now created)
4. Redis not installed (rate limiting middleware requires it)

**Impact**:
- All frontend API calls fail
- Users cannot access any stock data
- Application is completely unusable

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

### Missing Components
- Python virtual environment
- Backend dependencies (uvicorn, pandas, etc.)
- Redis server (optional but recommended)
- Configured .env file

## Solution Steps

### Step 1: Setup Python Virtual Environment
```bash
cd /Users/dongcheolshin/Sources/screener_system/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows
```

### Step 2: Install Build Dependencies (macOS)
```bash
# Install system dependencies for pandas compilation
brew install gcc python@3.11

# Ensure Xcode Command Line Tools are installed
xcode-select --install
```

### Step 3: Install Python Dependencies
```bash
# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Install dependencies with build isolation
pip install -r requirements.txt --no-cache-dir

# If pandas still fails, install pre-built binary:
pip install pandas --only-binary=:all:
```

### Step 4: Configure Environment
```bash
# .env file already created at:
# /Users/dongcheolshin/Sources/screener_system/backend/.env

# Key settings for development:
RATE_LIMIT_FREE=999999  # Very high limit to avoid rate limiting
DATABASE_URL=postgresql://...  # Update with actual DB credentials
REDIS_URL=redis://localhost:6379/0  # Optional
```

### Step 5: Install Redis (Optional but Recommended)
```bash
# macOS
brew install redis
brew services start redis

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

### Step 6: Start Backend Server
```bash
cd /Users/dongcheolshin/Sources/screener_system/backend

# Ensure virtual environment is activated
source venv/bin/activate

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Verify server is running
curl http://localhost:8000/docs  # Should show Swagger UI
```

### Step 7: Verify API Endpoints
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test stocks endpoint
curl http://localhost:8000/api/v1/stocks

# Expected: JSON response with stock data (not rate limit error)
```

## Alternative Solution (Docker)

If local setup is too complex, use Docker:

```bash
cd /Users/dongcheolshin/Sources/screener_system

# Build and run backend with Docker Compose
docker-compose up backend redis

# Backend will be available at http://localhost:8000
```

## Testing & Validation

### Test Plan
1. ✅ Backend server starts without errors
2. ✅ Health check endpoint returns 200 OK
3. ✅ Swagger docs accessible at http://localhost:8000/docs
4. ✅ Frontend can fetch data without errors
5. ✅ No "데이터를 불러오는 중 오류가 발생했습니다" message

### Acceptance Criteria
- [ ] Backend server runs on http://localhost:8000
- [ ] All Python dependencies installed successfully
- [ ] Frontend loads data without errors
- [ ] No connection refused errors in browser console
- [ ] API endpoints return valid JSON responses

## Documentation Updates

### Files to Update
- [ ] `README.md` - Add backend setup instructions
- [ ] `docs/DEVELOPMENT_SETUP.md` - Detail environment setup
- [ ] `.env.example` - Provide example configuration
- [ ] `docs/TROUBLESHOOTING.md` - Add common issues section

## Prevention Measures

### Future Improvements
1. **Docker-first Development**
   - Use Docker Compose for consistent environment
   - Avoid dependency installation issues

2. **Pre-built Binary Wheels**
   - Host pre-compiled pandas wheels for faster setup
   - Update requirements.txt with explicit versions

3. **Environment Validation Script**
   - Create `scripts/validate_environment.sh`
   - Check all prerequisites before starting server

4. **Improved Error Messages**
   - Frontend should detect backend unavailability
   - Display: "서버 연결 실패" instead of generic data error

## Related Issues
- None (first occurrence)

## References
- Backend Requirements: `/backend/requirements.txt`
- Configuration: `/backend/app/core/config.py`
- Rate Limit Middleware: `/backend/app/middleware/rate_limit.py`

## Notes
- .env file was missing - now created with development-friendly settings
- Rate limits set to 999999 for development to prevent throttling
- Redis is optional for development (middleware skips if unavailable)
- Chrome was using port 8000 - caused initial confusion
