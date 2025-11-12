# Architecture Overview

The Stock Screening Platform follows a modern microservices architecture with clear separation of concerns.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                         │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼───────┐          ┌───────▼────────┐
        │   Frontend    │          │   Backend API   │
        │  (React SPA)  │          │   (FastAPI)     │
        └───────────────┘          └────────┬────────┘
                                            │
                ┌───────────────────────────┼───────────────────┐
                │                           │                   │
        ┌───────▼───────┐         ┌────────▼────────┐  ┌──────▼──────┐
        │   PostgreSQL   │         │      Redis      │  │   Celery    │
        │  (TimescaleDB) │         │     (Cache)     │  │  (Workers)  │
        └────────────────┘         └─────────────────┘  └──────┬──────┘
                                                               │
                                                       ┌───────▼───────┐
                                                       │    Airflow    │
                                                       │ (Data Pipeline)│
                                                       └───────────────┘
```

## Components

### Frontend (React + TypeScript)
- **Technology**: React 18, TypeScript, Vite
- **State Management**: Zustand
- **Data Fetching**: TanStack Query
- **UI Framework**: Radix UI + Tailwind CSS
- **Charts**: TradingView Lightweight Charts

**Responsibilities:**
- User interface and interaction
- Client-side state management
- Data visualization and charts
- Real-time updates via WebSocket

### Backend API (FastAPI)
- **Technology**: Python 3.11, FastAPI, SQLAlchemy 2.0
- **Database**: PostgreSQL 16 with TimescaleDB extension
- **Cache**: Redis 7
- **Authentication**: JWT tokens

**Responsibilities:**
- REST API endpoints
- User authentication and authorization
- Business logic and data processing
- WebSocket connections for real-time data
- API rate limiting and request validation

### Database Layer

#### PostgreSQL + TimescaleDB
- **Purpose**: Primary data storage
- **Features**:
  - Relational data (users, portfolios, alerts)
  - Time-series data (stock prices, volumes)
  - Hypertables for efficient time-series queries

#### Redis
- **Purpose**: Caching and session storage
- **Features**:
  - API response caching
  - Rate limiting counters
  - Session data
  - WebSocket pub/sub

### Background Processing

#### Celery Workers
- **Technology**: Celery with Redis broker
- **Responsibilities**:
  - Async email sending
  - Price alert monitoring
  - Report generation
  - Data aggregation tasks

#### Apache Airflow
- **Technology**: Apache Airflow 2.x
- **Responsibilities**:
  - Daily market data ingestion
  - Financial data updates
  - Data quality checks
  - ETL workflows

## Data Flow

### User Request Flow
1. User interacts with React frontend
2. Frontend sends authenticated API request
3. Backend validates JWT token
4. Backend checks Redis cache
5. If cache miss, query PostgreSQL
6. Business logic processing
7. Response cached in Redis
8. JSON response to frontend
9. Frontend updates UI

### Real-time Data Flow
1. Airflow ingests market data
2. Data stored in PostgreSQL
3. Celery worker detects price changes
4. Worker checks alert conditions
5. WebSocket push to connected clients
6. Frontend updates charts in real-time

## Security Architecture

### Authentication Flow
```
1. User login (email + password)
2. Backend validates credentials
3. Generate JWT access token (1 hour TTL)
4. Generate refresh token (7 days TTL)
5. Store refresh token in HTTP-only cookie
6. Access token sent in JSON response
7. Frontend stores access token (memory)
8. Include token in Authorization header
```

### Authorization
- **Role-Based Access Control (RBAC)**
  - Admin: Full system access
  - Premium User: Advanced features
  - Free User: Basic features

### API Security
- HTTPS enforcement
- CORS configuration
- Rate limiting per user
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Content Security Policy)

## Scalability

### Horizontal Scaling
- **Frontend**: Static files served via CDN
- **Backend**: Multiple Gunicorn workers
- **Database**: Read replicas for queries
- **Cache**: Redis cluster
- **Workers**: Multiple Celery workers

### Performance Optimizations
- Database query optimization and indexing
- Redis caching (1-5 minute TTL)
- Connection pooling (SQLAlchemy)
- Lazy loading of heavy data
- Pagination for large datasets
- WebSocket for real-time (vs polling)

## Monitoring & Observability

### Metrics (Prometheus)
- Request latency and throughput
- Database query performance
- Cache hit/miss rates
- Worker queue lengths
- Error rates by endpoint

### Logging (ELK Stack)
- Structured JSON logs
- Request/response logging
- Error tracking and alerting
- Audit trail for critical actions

### Dashboards (Grafana)
- System health overview
- API performance metrics
- Database performance
- User activity metrics
- Business KPIs

## Deployment

### Docker Compose (Development)
- All services in containers
- Hot reload for development
- Shared volumes for code
- Service profiles for selective start

### Kubernetes (Production)
- Auto-scaling based on load
- Rolling updates (zero downtime)
- Health checks and self-healing
- Resource limits and requests
- Secrets management

## Next Steps

- [Backend Architecture Details](/docs/architecture/backend)
- [Frontend Architecture Details](/docs/architecture/frontend)
- [Database Schema](/docs/architecture/database)
- [Data Pipeline](/docs/architecture/data-pipeline)
