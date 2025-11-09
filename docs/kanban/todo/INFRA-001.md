# [INFRA-001] Docker Compose Development Environment

## Metadata
- **Status**: TODO
- **Priority**: High
- **Assignee**: TBD
- **Estimated Time**: 8 hours
- **Sprint**: Sprint 1 (Week 1-2)
- **Tags**: #infrastructure #docker #development

## Description
Set up Docker Compose configuration for local development environment. All services should run with a single `docker-compose up` command.

## Subtasks
- [ ] docker-compose.yml creation
  - [ ] Version: 3.8
  - [ ] Services configuration
- [ ] PostgreSQL Service
  - [ ] Image: timescale/timescaledb:latest-pg16
  - [ ] Environment variables (DB_NAME, DB_USER, DB_PASSWORD)
  - [ ] Volume mount for persistence
  - [ ] Health check (pg_isready)
  - [ ] Port: 5432
  - [ ] Init script volume mount (migrations)
- [ ] Redis Service
  - [ ] Image: redis:7-alpine
  - [ ] Command: redis-server --appendonly yes
  - [ ] Volume mount for persistence
  - [ ] Health check (redis-cli ping)
  - [ ] Port: 6379
- [ ] Backend Service
  - [ ] Build: ./backend/Dockerfile
  - [ ] Environment variables
    - [ ] DATABASE_URL
    - [ ] REDIS_URL
    - [ ] SECRET_KEY
  - [ ] Depends on: postgres, redis
  - [ ] Volume mount: ./backend:/app (for hot reload)
  - [ ] Port: 8000
  - [ ] Command: uvicorn app.main:app --reload --host 0.0.0.0
  - [ ] Health check: GET /health
- [ ] Celery Worker Service
  - [ ] Build: ./backend/Dockerfile
  - [ ] Command: celery -A app.celery_app worker
  - [ ] Depends on: postgres, redis
  - [ ] Volume mount: ./backend:/app
- [ ] Airflow Webserver Service
  - [ ] Image: apache/airflow:2.8.0-python3.11
  - [ ] Environment variables (AIRFLOW__*)
  - [ ] Depends on: postgres
  - [ ] Volume mounts:
    - [ ] ./data_pipeline/dags:/opt/airflow/dags
    - [ ] ./data_pipeline/plugins:/opt/airflow/plugins
  - [ ] Port: 8080
  - [ ] Init commands: db init, create user
- [ ] Airflow Scheduler Service
  - [ ] Image: apache/airflow:2.8.0-python3.11
  - [ ] Depends on: airflow_webserver
  - [ ] Command: scheduler
- [ ] Frontend Service (Optional for full stack dev)
  - [ ] Build: ./frontend/Dockerfile.dev
  - [ ] Volume mount: ./frontend:/app
  - [ ] Port: 5173
  - [ ] Command: npm run dev
- [ ] NGINX Service (Optional for production-like setup)
  - [ ] Image: nginx:alpine
  - [ ] Config volume: ./infrastructure/nginx/nginx.conf
  - [ ] Depends on: frontend, backend
  - [ ] Ports: 80, 443
- [ ] Networks Configuration
  - [ ] Create custom bridge network: screener_network
  - [ ] All services join same network
- [ ] Volumes Configuration
  - [ ] postgres_data (persistent)
  - [ ] redis_data (persistent)
  - [ ] airflow_logs (persistent)
- [ ] .env.example File
  - [ ] Database credentials
  - [ ] Redis settings
  - [ ] Secret keys
  - [ ] API keys (KRX, F&Guide)
  - [ ] SMTP settings
- [ ] Documentation
  - [ ] README.md update with Docker Compose instructions
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
- **0%** - Not started

## Notes
- Use docker-compose.override.yml for local customizations
- Keep production secrets out of docker-compose.yml
- Consider using profiles for optional services
- Document required Docker version (24+)
- Add healthchecks for reliability
