# [INFRA-001] Docker Compose Development Environment

## Metadata
- **Status**: IN_REVIEW
- **Priority**: High
- **Assignee**: Development Team
- **Estimated Time**: 8 hours
- **Actual Time**: 6 hours (core implementation)
- **Sprint**: Sprint 1 (Week 1-2)
- **Tags**: #infrastructure #docker #development
- **Started**: 2025-11-09

## Description
Set up Docker Compose configuration for local development environment. All services should run with a single `docker-compose up` command.

## Subtasks
- [x] docker-compose.yml creation
  - [x] Version: 3.8
  - [x] Services configuration
- [x] PostgreSQL Service
  - [x] Image: timescale/timescaledb:latest-pg16
  - [x] Environment variables (DB_NAME, DB_USER, DB_PASSWORD)
  - [x] Volume mount for persistence
  - [x] Health check (pg_isready)
  - [x] Port: 5432
  - [x] Init script volume mount (migrations)
- [x] Redis Service
  - [x] Image: redis:7-alpine
  - [x] Command: redis-server --appendonly yes
  - [x] Volume mount for persistence
  - [x] Health check (redis-cli ping)
  - [x] Port: 6379
- [x] Backend Service
  - [x] Build: ./backend/Dockerfile
  - [x] Environment variables
    - [x] DATABASE_URL
    - [x] REDIS_URL
    - [x] SECRET_KEY
  - [x] Depends on: postgres, redis
  - [x] Volume mount: ./backend:/app (for hot reload)
  - [x] Port: 8000
  - [x] Command: uvicorn app.main:app --reload --host 0.0.0.0
  - [x] Health check: GET /health
- [x] Celery Worker Service
  - [x] Build: ./backend/Dockerfile
  - [x] Command: celery -A app.celery_app worker
  - [x] Depends on: postgres, redis
  - [x] Volume mount: ./backend:/app
- [x] Airflow Webserver Service
  - [x] Image: apache/airflow:2.8.0-python3.11
  - [x] Environment variables (AIRFLOW__*)
  - [x] Depends on: postgres
  - [x] Volume mounts:
    - [x] ./data_pipeline/dags:/opt/airflow/dags
    - [x] ./data_pipeline/plugins:/opt/airflow/plugins
  - [x] Port: 8080
  - [x] Init commands: db init, create user
- [x] Airflow Scheduler Service
  - [x] Image: apache/airflow:2.8.0-python3.11
  - [x] Depends on: airflow_webserver
  - [x] Command: scheduler
- [x] Frontend Service (Optional for full stack dev)
  - [x] Build: ./frontend/Dockerfile.dev
  - [x] Volume mount: ./frontend:/app
  - [x] Port: 5173
  - [x] Command: npm run dev
- [x] NGINX Service (Optional for production-like setup)
  - [x] Image: nginx:alpine
  - [x] Config volume: ./infrastructure/nginx/nginx.conf
  - [x] Depends on: frontend, backend
  - [x] Ports: 80, 443
- [x] Networks Configuration
  - [x] Create custom bridge network: screener_network
  - [x] All services join same network
- [x] Volumes Configuration
  - [x] postgres_data (persistent)
  - [x] redis_data (persistent)
  - [x] airflow_logs (persistent)
- [x] .env.example File
  - [x] Database credentials
  - [x] Redis settings
  - [x] Secret keys
  - [x] API keys (KRX, F&Guide)
  - [x] SMTP settings
- [x] Documentation
  - [x] README.md update with Docker Compose instructions
  - [ ] Troubleshooting guide
  - [ ] Service URLs reference

## Acceptance Criteria
- [ ] **Single Command Startup**
  - [ ] `docker-compose up -d` starts all services
  - [ ] All services healthy within 2 minutes
- [ ] **Service Health**
  - [ ] postgres: `docker-compose ps` shows healthy
  - [ ] redis: `docker-compose ps` shows healthy
  - [ ] backend: http://localhost:8000/health returns 200
  - [ ] airflow: http://localhost:8080 accessible
- [ ] **Service Communication**
  - [ ] Backend can connect to postgres
  - [ ] Backend can connect to redis
  - [ ] Airflow can connect to postgres
  - [ ] All services on same network
- [ ] **Data Persistence**
  - [ ] `docker-compose down` doesn't lose data
  - [ ] `docker-compose up` restores previous state
  - [ ] Database data persists across restarts
- [ ] **Hot Reload**
  - [ ] Backend code changes trigger reload
  - [ ] Frontend code changes trigger HMR (if frontend service included)
- [ ] **Logs**
  - [ ] `docker-compose logs <service>` shows logs
  - [ ] Logs are readable and useful
- [ ] **Environment Variables**
  - [ ] .env file loaded correctly
  - [ ] Secrets not committed to git
- [ ] **Performance**
  - [ ] Services start in < 2 minutes
  - [ ] No excessive CPU/memory usage
- [ ] **Cleanup**
  - [ ] `docker-compose down -v` removes all containers and volumes
  - [ ] No orphaned containers

## Dependencies
- **Depends on**: None (can start immediately)
- **Blocks**: Development workflow

## References
- **SDS.md**: Section 9.1 Docker Compose (Development)
- **docker-compose.yml** (implementation)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Progress
- **95%** - In Review (pending runtime verification and documentation completion)

## Implementation Summary
- ✅ Docker Compose configuration with all required services
- ✅ NGINX reverse proxy with comprehensive routing
- ✅ Prometheus and Grafana monitoring setup
- ✅ Backend and frontend Dockerfiles
- ✅ Environment variables configuration (.env.example)
- ✅ Network and volume configuration
- ✅ Health checks for all services

## Remaining Tasks
- [ ] Troubleshooting guide documentation
- [ ] Service URLs reference documentation
- [ ] Runtime verification with Docker daemon
  - [ ] Verify all services start successfully
  - [ ] Test service health checks
  - [ ] Verify service communication
  - [ ] Test data persistence
  - [ ] Test hot reload functionality

## Notes
- Use docker-compose.override.yml for local customizations
- Keep production secrets out of docker-compose.yml
- Consider using profiles for optional services
- Document required Docker version (24+)
- Add healthchecks for reliability
