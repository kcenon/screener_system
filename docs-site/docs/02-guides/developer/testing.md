---
id: testing
title: Testing Guide
description: Comprehensive testing guide for the Stock Screening Platform
sidebar_label: Testing
sidebar_position: 2
tags:
  - development
  - testing
  - docker
  - ci-cd
last_updated: 2025-11-13
---

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

:::info Frontend Setup
FE-001 (Frontend Setup) is not yet complete, so frontend services will fail to build. Use default profile for testing backend infrastructure.
:::

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

For complete testing guide including middleware testing, database validation, and automated scripts, see the full document.

## Automated Testing Script

Create `scripts/test_all.sh` for comprehensive automated testing:

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

echo ""
echo "🎉 All tests passed!"
```

Make it executable:
```bash
chmod +x scripts/test_all.sh
./scripts/test_all.sh
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

## Next Steps

After verifying all tests pass:

1. ✅ Mark runtime testing as complete in task tickets
2. 📋 Update acceptance criteria
3. 🔄 Move tasks from review to done
4. 🚀 Proceed with next sprint tasks

## Related Guides

- [Data Loading Guide](./data-loading.md) - Load sample data for testing
- [Local Development](./local-development.md) - Set up development environment
- [API Documentation](../../03-api-reference/intro.md) - API testing reference

## References

- **Docker Compose Docs**: https://docs.docker.com/compose/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **PostgreSQL Testing**: https://www.postgresql.org/docs/current/regress.html
- **Redis Testing**: https://redis.io/docs/manual/patterns/
