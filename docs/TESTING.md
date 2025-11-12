# Testing Guide

This guide provides instructions for testing the Stock Screening Platform in Docker environment.

## Quick Start

### Prerequisites

1. **Docker & Docker Compose**
   ```bash
   # Verify installation
   docker --version          # Should be 20.10+
   docker-compose --version  # Should be 2.0+
   ```

2. **Environment Configuration**
   ```bash
   # Copy example environment file
   cp .env.example .env

   # Edit with your settings
   vim .env  # or nano, code, etc.
   ```

3. **Required Ports Available**
   - 5432 (PostgreSQL)
   - 6379 (Redis)
   - 8000 (Backend API)
   - 8080 (Airflow)
   - 5173 (Frontend Dev)
   - 80/443 (NGINX)
   - 9090 (Prometheus)
   - 3001 (Grafana)

### Environment Setup

Create `.env` file with minimal configuration:

```bash
# Database
DB_NAME=screener_db
DB_USER=screener_user
DB_PASSWORD=screener_password

# Redis
REDIS_PASSWORD=redis_password

# JWT
SECRET_KEY=your-secret-key-change-this-in-production-min-32-chars

# Application
DEBUG=true
ENVIRONMENT=development

# External APIs (optional for testing)
KRX_API_KEY=
FGUIDE_API_KEY=
```

## Service Profiles

The project uses Docker Compose profiles to manage optional services:

### Available Profiles

- **Default** (no profile): Core services only
  - PostgreSQL + TimescaleDB
  - Redis
  - Backend API

- **frontend**: Add frontend development server
  - Includes: Vite dev server, NGINX reverse proxy
  - Usage: `--profile frontend`

- **monitoring**: Add monitoring stack
  - Includes: Prometheus, Grafana
  - Usage: `--profile monitoring`

- **full**: All services
  - Includes everything above + Celery, Airflow
  - Usage: `--profile full`

### Profile Usage Examples

```bash
# Core services only (recommended for initial testing)
docker-compose up -d

# Core + Frontend
docker-compose --profile frontend up -d

# Core + Monitoring
docker-compose --profile monitoring up -d

# All services
docker-compose --profile full up -d

# Multiple profiles
docker-compose --profile frontend --profile monitoring up -d
```

**Note**: FE-001 (Frontend Setup) is not yet complete, so frontend services will fail to build. Use default profile for testing backend infrastructure.

## Testing Procedures

### 1. Build and Start Services

```bash
# Build core services only (recommended for initial testing)
docker-compose build

# Start core services (PostgreSQL, Redis, Backend)
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### 2. Health Check Verification

#### Check Service Status
```bash
# Check all services are running
docker-compose ps

# Expected output: All services should show "Up" and "healthy"
```

#### Test Individual Health Checks

**PostgreSQL:**
```bash
# Test database connection
docker-compose exec postgres psql -U screener_user -d screener_db -c "SELECT 1;"

# Expected: Returns "1"
```

**Redis:**
```bash
# Test Redis connection with authentication
docker-compose exec redis redis-cli -a redis_password ping

# Expected: Returns "PONG"

# Test Redis operations
docker-compose exec redis redis-cli -a redis_password SET test_key "test_value"
docker-compose exec redis redis-cli -a redis_password GET test_key

# Expected: Returns "test_value"
```

**Backend API:**
```bash
# Test health endpoint
curl -f http://localhost:8000/health

# Expected: {"status":"healthy","timestamp":"..."}

# Test database health
curl -f http://localhost:8000/health/db

# Expected: {"status":"healthy","database":"connected"}

# Test Redis health
curl -f http://localhost:8000/health/redis

# Expected: {"status":"healthy","redis":"connected"}
```

**Airflow:**
```bash
# Test Airflow webserver
curl -f http://localhost:8080/health

# Access Airflow UI
open http://localhost:8080
# Login: admin / admin (default)
```

**Frontend (Development):**
```bash
# Test frontend dev server
curl -f http://localhost:5173

# Open in browser
open http://localhost:5173
```

**NGINX:**
```bash
# Test NGINX reverse proxy
curl -f http://localhost/api/health

# Should proxy to backend and return health status
```

### 3. Middleware Testing

#### Request Logging Middleware

```bash
# Make a request and check logs
curl http://localhost:8000/

# Check backend logs for request logging
docker-compose logs backend | grep "Request started"
docker-compose logs backend | grep "Request completed"

# Should see:
# - Request ID (UUID)
# - Method and path
# - Duration
# - Status code
```

#### Rate Limiting Middleware

**Test rate limits:**
```bash
# Create a script to test rate limiting
cat > test_rate_limit.sh << 'EOF'
#!/bin/bash
echo "Testing rate limiting (Free tier: 100 req/min)..."
for i in {1..105}; do
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
  echo "Request $i: HTTP $response"
  if [ "$response" == "429" ]; then
    echo "Rate limit exceeded at request $i"
    break
  fi
done
EOF

chmod +x test_rate_limit.sh
./test_rate_limit.sh

# Expected:
# - First 100 requests: HTTP 200
# - Request 101+: HTTP 429 (Too Many Requests)
```

**Check rate limit headers:**
```bash
# Make a request and inspect headers
curl -v http://localhost:8000/ 2>&1 | grep "X-RateLimit"

# Expected headers:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 99
# X-RateLimit-Reset: 60
```

**Test whitelist paths (should not be rate limited):**
```bash
# These endpoints should never return 429
for i in {1..150}; do
  curl -s http://localhost:8000/health > /dev/null
done
echo "Health check endpoint - should never be rate limited"

# Check status
curl -v http://localhost:8000/health 2>&1 | grep "HTTP"
# Expected: HTTP 200 (no rate limiting)
```

### 4. Database Testing

#### Verify TimescaleDB Extension

```bash
docker-compose exec postgres psql -U screener_user -d screener_db << 'EOF'
-- Check TimescaleDB is installed
SELECT default_version, installed_version
FROM pg_available_extensions
WHERE name = 'timescaledb';

-- List all hypertables (if migrations ran)
SELECT * FROM timescaledb_information.hypertables;
EOF
```

#### Test Migrations

```bash
# Check if migration files were executed
docker-compose exec postgres psql -U screener_user -d screener_db -c "\dt"

# Should show tables created by migrations
```

#### Test Connection Pooling

```bash
# Check active connections
docker-compose exec postgres psql -U screener_user -d screener_db << 'EOF'
SELECT
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active,
    count(*) FILTER (WHERE state = 'idle') as idle
FROM pg_stat_activity
WHERE datname = 'screener_db';
EOF
```

### 5. JWT Token Testing

**Generate a test token (manual):**
```bash
# Enter Python shell in backend container
docker-compose exec backend python

# In Python:
from app.core.security import create_access_token
token = create_access_token("test_user_123")
print(f"Token: {token}")
exit()
```

**Test token with API:**
```bash
# Use the token in Authorization header
TOKEN="<your-token-here>"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/protected-endpoint

# Note: protected-endpoint doesn't exist yet, will return 404
# But if auth works, it won't return 401 Unauthorized
```

### 6. CORS Testing

**Test from browser console:**
```javascript
// Open http://localhost:5173 and run in console:
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)

// Should succeed (CORS allowed from localhost:5173)

// Test from disallowed origin (should fail):
fetch('http://localhost:8000/health', {
  headers: { 'Origin': 'http://evil.com' }
})
// Expected: CORS error
```

**Test CORS headers:**
```bash
# Send preflight request
curl -X OPTIONS http://localhost:8000/ \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET" \
  -v

# Expected headers:
# Access-Control-Allow-Origin: http://localhost:5173
# Access-Control-Allow-Credentials: true
# Access-Control-Allow-Methods: *
```

### 7. Performance Testing

#### Measure Response Time

```bash
# Test API response time
curl -w "\nTime: %{time_total}s\n" http://localhost:8000/health

# Expected: < 100ms for health check
```

#### Load Testing (Optional)

Using `ab` (Apache Bench):
```bash
# Install if needed: brew install httpd (macOS)
ab -n 1000 -c 10 http://localhost:8000/health

# Expected: Most requests < 100ms
```

Using `wrk` (recommended):
```bash
# Install: brew install wrk (macOS)
wrk -t4 -c100 -d30s http://localhost:8000/health

# Expected:
# - Latency avg: < 50ms
# - Requests/sec: > 1000
```

### 8. Monitoring Stack Testing

**Prometheus:**
```bash
# Access Prometheus UI
open http://localhost:9090

# Test query:
# up{job="backend"}
# Should show backend metrics if exported
```

**Grafana:**
```bash
# Access Grafana
open http://localhost:3001

# Login: admin / admin
# Should have Prometheus datasource preconfigured
```

## Common Issues and Solutions

### Issue: Services fail to start

```bash
# Check logs for errors
docker-compose logs

# Common causes:
# 1. Port already in use
sudo lsof -i :5432  # Check PostgreSQL port
sudo lsof -i :6379  # Check Redis port
sudo lsof -i :8000  # Check Backend port

# 2. Missing .env file
ls -la .env

# 3. Docker daemon not running
docker info
```

### Issue: Health checks failing

```bash
# Check individual service
docker-compose ps

# If "unhealthy", check logs
docker-compose logs <service-name>

# Restart specific service
docker-compose restart <service-name>

# Force recreate
docker-compose up -d --force-recreate <service-name>
```

### Issue: Database connection refused

```bash
# Check PostgreSQL is accepting connections
docker-compose exec postgres pg_isready -U screener_user

# Check DATABASE_URL is correct
docker-compose exec backend env | grep DATABASE_URL

# Should be: postgresql://screener_user:screener_password@postgres:5432/screener_db
```

### Issue: Redis authentication errors

```bash
# Check Redis password is set
docker-compose exec redis redis-cli -a redis_password ping

# Check REDIS_URL in backend
docker-compose exec backend env | grep REDIS_URL

# Should be: redis://:redis_password@redis:6379/0
```

### Issue: CORS errors in browser

```bash
# Check CORS_ORIGINS setting
docker-compose exec backend env | grep CORS_ORIGINS

# Should include frontend URL: http://localhost:5173,http://localhost:3000

# Restart backend after changing .env
docker-compose restart backend
```

## Clean Up

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes all data)
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

### Reset Everything
```bash
# Complete cleanup
docker-compose down -v --rmi all
docker system prune -a --volumes

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

## Automated Testing Script

Create `scripts/test_all.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Starting comprehensive testing..."

echo "1️⃣ Building services..."
docker-compose build

echo "2️⃣ Starting services..."
docker-compose up -d

echo "3️⃣ Waiting for services to be healthy..."
sleep 30

echo "4️⃣ Testing PostgreSQL..."
docker-compose exec -T postgres psql -U screener_user -d screener_db -c "SELECT 1;" > /dev/null
echo "✅ PostgreSQL OK"

echo "5️⃣ Testing Redis..."
docker-compose exec -T redis redis-cli -a redis_password ping > /dev/null
echo "✅ Redis OK"

echo "6️⃣ Testing Backend Health..."
curl -f http://localhost:8000/health > /dev/null
echo "✅ Backend Health OK"

echo "7️⃣ Testing Backend DB Health..."
curl -f http://localhost:8000/health/db > /dev/null
echo "✅ Backend DB Connection OK"

echo "8️⃣ Testing Backend Redis Health..."
curl -f http://localhost:8000/health/redis > /dev/null
echo "✅ Backend Redis Connection OK"

echo "9️⃣ Testing Rate Limiting..."
for i in {1..105}; do
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
  if [ "$response" == "429" ]; then
    echo "✅ Rate Limiting OK (hit limit at request $i)"
    break
  fi
done

echo "🔟 Testing Request Logging..."
curl -s http://localhost:8000/ > /dev/null
docker-compose logs backend | grep -q "Request started"
echo "✅ Request Logging OK"

echo ""
echo "🎉 All tests passed!"
echo ""
echo "Services running at:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Airflow: http://localhost:8080"
echo "  - Frontend: http://localhost:5173"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3001"
```

Make it executable:
```bash
chmod +x scripts/test_all.sh
./scripts/test_all.sh
```

## Continuous Testing

### Watch Mode (for development)

```bash
# Watch backend logs
docker-compose logs -f backend

# Auto-reload is enabled in development mode
# Edit code and watch it reload automatically
```

### Periodic Health Checks

```bash
# Create a monitoring script
cat > scripts/monitor.sh << 'EOF'
#!/bin/bash
while true; do
  clear
  echo "=== Service Health Monitor ==="
  echo "Time: $(date)"
  echo ""

  docker-compose ps

  echo ""
  echo "=== Health Endpoints ==="
  curl -s http://localhost:8000/health | jq '.'

  sleep 5
done
EOF

chmod +x scripts/monitor.sh
./scripts/monitor.sh
```

## Next Steps

After verifying all tests pass:

1. ✅ Mark runtime testing as complete in task tickets
2. 📋 Update acceptance criteria in BUGFIX-001, TECH-DEBT-001, FEATURE-001
3. 🔄 Move tasks from review to done (if not already)
4. 🚀 Proceed with next sprint tasks

## Documentation Testing

### Overview

The unified documentation platform must be tested to ensure:
- All documentation builds without errors
- Auto-generated API docs are accurate
- Links are valid
- Search functionality works
- Documentation site is accessible

### 1. Documentation Build Testing

#### Test Sphinx Documentation (Python API)

```bash
# Navigate to Sphinx docs directory
cd docs/api/python

# Build documentation
sphinx-build -b html . _build

# Check for errors and warnings
# Expected: 0 errors, 0 warnings

# View generated docs
open _build/index.html
```

**Validation Checklist**:
- [ ] No Sphinx build errors
- [ ] No missing docstring warnings
- [ ] All modules appear in navigation
- [ ] Code examples render correctly
- [ ] Type hints display properly
- [ ] Cross-references work

#### Test TypeDoc Documentation (TypeScript API)

```bash
# Navigate to docs-site directory
cd docs-site

# Install dependencies
npm ci

# Build TypeDoc documentation
npx typedoc

# Check for errors
# Expected: 0 errors

# View generated docs
open api/frontend/index.html
```

**Validation Checklist**:
- [ ] No TypeDoc build errors
- [ ] All exported components documented
- [ ] Props tables complete
- [ ] React component examples present
- [ ] Hooks documented with parameters
- [ ] Type definitions visible

#### Test Docusaurus Site Build

```bash
# Navigate to docs-site directory
cd docs-site

# Build production site
npm run build

# Check build output
ls -la build/

# Serve locally to test
npx serve build

# Open in browser
open http://localhost:3000
```

**Validation Checklist**:
- [ ] Build completes without errors
- [ ] No broken MDX syntax
- [ ] All pages accessible
- [ ] Navigation works correctly
- [ ] Search index generated
- [ ] Assets load properly
- [ ] Mobile responsive

### 2. Documentation Content Testing

#### Test Documentation Coverage

**Python Backend Coverage**:
```bash
# Check docstring coverage
cd backend

# Install interrogate (docstring coverage tool)
pip install interrogate

# Generate coverage report
interrogate -v app/

# Expected: > 90% coverage
```

**TypeScript Frontend Coverage**:
```bash
# Check TSDoc coverage
cd frontend

# Run custom coverage script
npm run docs:coverage

# Expected: > 80% coverage
```

#### Test Code Examples

**Extract and test Python examples**:
```bash
# Create test script
cat > test_doc_examples.py << 'EOF'
#!/usr/bin/env python3
"""Test code examples from documentation."""
import doctest
import sys

def test_all_docstrings():
    """Run doctests for all modules."""
    import app.services.stock_service
    import app.repositories.stock_repository

    failures = 0

    for module in [app.services.stock_service, app.repositories.stock_repository]:
        result = doctest.testmod(module, verbose=True)
        failures += result.failed

    return failures

if __name__ == "__main__":
    failures = test_all_docstrings()
    sys.exit(1 if failures > 0 else 0)
EOF

# Run tests
python test_doc_examples.py
```

**Test TypeScript examples**:
```bash
# Ensure example code compiles
cd docs-site

# Extract examples and test
npm run docs:test-examples
```

### 3. Link Validation Testing

#### Test Internal Links

```bash
# Install link checker
npm install -g markdown-link-check

# Check all Markdown files
find docs -name "*.md" -exec markdown-link-check {} \;

# Expected: 0 broken links
```

#### Test External Links

```bash
# Check external links (with cache to avoid rate limits)
npx broken-link-checker http://localhost:3000 \
  --recursive \
  --ordered \
  --exclude-external \
  --verbose

# Expected: 0 broken internal links
```

**GitHub Actions Link Check**:
```yaml
# Part of .github/workflows/docs.yml
- name: Check for broken links
  run: |
    npm run docs:check-links
```

### 4. Search Functionality Testing

#### Test Algolia DocSearch (if configured)

```bash
# Test search index exists
curl https://ALGOLIA_APP_ID-dsn.algolia.net/1/indexes/screener_docs \
  -H "X-Algolia-API-Key: SEARCH_ONLY_API_KEY"

# Should return index metadata
```

#### Manual Search Testing

1. Navigate to documentation site
2. Use search bar (Cmd/Ctrl + K)
3. Test queries:
   - "stock service" → should find StockService docs
   - "authentication" → should find auth-related pages
   - "database schema" → should find DB docs
   - "API endpoints" → should find REST API reference

**Validation**:
- [ ] Search results relevant
- [ ] Search highlights match
- [ ] Navigation to results works
- [ ] Search speed < 100ms

### 5. Accessibility Testing

#### Lighthouse Audit

```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run audit on documentation site
lighthouse http://localhost:3000 \
  --only-categories=accessibility,performance,best-practices \
  --output=html \
  --output-path=./lighthouse-report.html

# Expected scores:
# - Accessibility: > 90
# - Performance: > 90
# - Best Practices: > 90
```

#### Manual Accessibility Checks

- [ ] Keyboard navigation works (Tab, Enter, Esc)
- [ ] Screen reader compatible (test with VoiceOver/NVDA)
- [ ] Color contrast meets WCAG 2.1 AA
- [ ] Images have alt text
- [ ] Code blocks have language labels
- [ ] Headings follow logical hierarchy

### 6. Mobile Responsiveness Testing

#### Test on Multiple Devices

```bash
# Use Chrome DevTools device emulation

# Test breakpoints:
# - Mobile: 375px (iPhone SE)
# - Tablet: 768px (iPad)
# - Desktop: 1440px (MacBook)
```

**Validation Checklist**:
- [ ] Navigation menu collapses on mobile
- [ ] Code blocks scroll horizontally
- [ ] Tables are responsive
- [ ] Images scale properly
- [ ] Search works on mobile
- [ ] No horizontal scroll on mobile

### 7. GitHub Pages Deployment Testing

#### Test Local Deployment Simulation

```bash
# Build for GitHub Pages
cd docs-site
npm run build

# Simulate gh-pages serving
npx serve build --single

# Test custom domain simulation
# Add to /etc/hosts: 127.0.0.1 docs.screener.kr

# Access at http://docs.screener.kr:3000
```

#### Test GitHub Actions Workflow

```bash
# Trigger workflow manually
gh workflow run docs.yml

# Monitor workflow
gh run watch

# Check deployment status
gh api repos/kcenon/screener_system/pages

# Verify deployment
curl -I https://docs.screener.kr
# Expected: HTTP/2 200

# Check SSL
curl -vI https://docs.screener.kr 2>&1 | grep -i "SSL certificate verify"
# Expected: OK
```

### 8. Documentation Versioning Testing

#### Test Version Switching

```bash
# Create a new version
npm run docusaurus docs:version 1.0

# Build with versions
npm run build

# Test version selector works
# Navigate to site and switch versions
```

**Validation**:
- [ ] Version selector appears
- [ ] Can switch between versions
- [ ] Old versions remain accessible
- [ ] Links work in old versions

### 9. Performance Testing

#### Measure Build Performance

```bash
# Time the full build
time npm run build

# Expected: < 3 minutes

# Measure individual steps
time sphinx-build -b html . _build    # < 30s
time npx typedoc                      # < 20s
time npm run build                    # < 90s
```

#### Measure Page Load Performance

```bash
# Test page load speed
curl -o /dev/null -s -w "Time: %{time_total}s\n" https://docs.screener.kr

# Expected: < 1 second

# Test with slow 3G simulation
lighthouse https://docs.screener.kr \
  --throttling-method=devtools \
  --throttling.cpuSlowdownMultiplier=4 \
  --only-categories=performance
```

### 10. Automated Testing Script

Create `scripts/test_docs.sh`:

```bash
#!/bin/bash
set -e

echo "🔍 Testing Documentation Platform..."

echo "1️⃣ Testing Sphinx build..."
cd docs/api/python
sphinx-build -b html . _build -W
echo "✅ Sphinx build OK"

echo "2️⃣ Testing TypeDoc build..."
cd ../../../docs-site
npm ci --silent
npx typedoc
echo "✅ TypeDoc build OK"

echo "3️⃣ Testing Docusaurus build..."
npm run build
echo "✅ Docusaurus build OK"

echo "4️⃣ Checking for broken links..."
npm run docs:check-links
echo "✅ No broken links"

echo "5️⃣ Testing documentation coverage..."
cd ../backend
interrogate -v app/ --fail-under 90
echo "✅ Documentation coverage > 90%"

echo "6️⃣ Running Lighthouse audit..."
cd ../docs-site
npx serve build > /dev/null 2>&1 &
SERVER_PID=$!
sleep 3
lighthouse http://localhost:3000 \
  --only-categories=accessibility,performance \
  --quiet \
  --chrome-flags="--headless"
kill $SERVER_PID
echo "✅ Lighthouse audit passed"

echo ""
echo "🎉 All documentation tests passed!"
```

Make executable:
```bash
chmod +x scripts/test_docs.sh
./scripts/test_docs.sh
```

### 11. Integration with CI/CD

Documentation tests are automatically run in GitHub Actions:

```yaml
# .github/workflows/docs.yml includes:
- Build Sphinx docs
- Build TypeDoc docs
- Build Docusaurus site
- Check for broken links
- Run Lighthouse audit
- Deploy to GitHub Pages (if all tests pass)
```

**Status Checks**:
- Documentation build must pass before PR merge
- Broken links block deployment
- Coverage below threshold triggers warning

### 12. Documentation Quality Metrics

Track these metrics over time:

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Build Success Rate** | 100% | TBD | 🟡 |
| **Python Coverage** | > 90% | TBD | 🟡 |
| **TypeScript Coverage** | > 80% | TBD | 🟡 |
| **Broken Links** | 0 | TBD | 🟡 |
| **Lighthouse Score** | > 90 | TBD | 🟡 |
| **Build Time** | < 3 min | TBD | 🟡 |
| **Page Load Time** | < 1s | TBD | 🟡 |

Update metrics after running tests:
```bash
# Generate metrics report
./scripts/docs_metrics.sh > docs/DOCUMENTATION_METRICS.md
```

## References

- **Docker Compose Docs**: https://docs.docker.com/compose/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **PostgreSQL Testing**: https://www.postgresql.org/docs/current/regress.html
- **Redis Testing**: https://redis.io/docs/manual/patterns/
- **Sphinx Testing**: https://www.sphinx-doc.org/en/master/usage/builders/index.html
- **TypeDoc**: https://typedoc.org/
- **Docusaurus Testing**: https://docusaurus.io/docs/deployment
- **Lighthouse**: https://developers.google.com/web/tools/lighthouse
- **Accessibility Testing**: https://www.w3.org/WAI/test-evaluate/
