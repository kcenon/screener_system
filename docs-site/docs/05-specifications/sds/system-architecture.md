---
id: sds-system-architecture
title: SDS - System Architecture
description: Software design specification - system architecture
sidebar_label: System Architecture
sidebar_position: 2
tags:
  - specification
  - design
  - architecture
---

:::info Navigation
- [Introduction](introduction.md)
- [System Architecture](system-architecture.md) (Current)
- [Component Design](component-design.md)
- [Database Design](database-design.md)
- [API Design](api-design.md)
- [Data Pipeline](data-pipeline.md)
- [Security Design](security-design.md)
- [Performance Design](performance-design.md)
- [Deployment](deployment.md)
- [Tech Stack & Decisions](tech-stack-decisions.md)
:::

# Software Design Specification - System Architecture

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                            Client Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Web Browser │  │    Mobile    │  │  External    │             │
│  │   (React)    │  │     App      │  │   API        │             │
│  │              │  │  (Phase 3+)  │  │   Clients    │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
└─────────┼──────────────────┼──────────────────┼───────────────────┘
          │ HTTPS            │ HTTPS            │ HTTPS
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Load Balancer Layer                           │
│                      (NGINX / Cloud LB)                              │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          ▼                                       ▼
┌─────────────────────────┐          ┌─────────────────────────┐
│   Frontend Service      │          │   Backend API Service   │
│   (Static Files)        │          │      (FastAPI)          │
│                         │          │                         │
│  - React App Bundle     │          │  - REST API Endpoints   │
│  - Static Assets        │          │  - Business Logic       │
│  - Service Worker       │          │  - Authentication       │
└─────────────────────────┘          └───────┬─────────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    ▼                        ▼                        ▼
          ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
          │  Cache Layer    │    │  Database       │    │  Task Queue     │
          │    (Redis)      │    │  (PostgreSQL    │    │   (Celery)      │
          │                 │    │   TimescaleDB)  │    │                 │
          │  - Session      │    │                 │    │  - Background   │
          │  - Query Cache  │    │  - Stocks       │    │    Jobs         │
          │  - Rate Limits  │    │  - Prices       │    │  - Alerts       │
          └─────────────────┘    │  - Users        │    │  - Reports      │
                                 │  - Portfolios   │    └─────────────────┘
                                 └─────────────────┘
                                         ▲
                                         │ Updates
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
          ┌─────────────────┐                      ┌─────────────────┐
          │  Data Pipeline  │                      │   External      │
          │   (Airflow)     │◄────────────────────►│   Data APIs     │
          │                 │                      │                 │
          │  - Price        │                      │  - KRX API      │
          │    Ingestion    │                      │  - F&Guide API  │
          │  - Indicator    │                      │  - OAuth        │
          │    Calculation  │                      │    Providers    │
          └─────────────────┘                      └─────────────────┘
```

### 2.2 Architectural Patterns

#### 2.2.1 Layered Architecture

**Presentation Layer** (Frontend)
- React components
- State management (Zustand)
- API client services
- UI/UX interactions

**Application Layer** (Backend API)
- REST API endpoints
- Request validation
- Business logic orchestration
- Response formatting

**Domain Layer**
- Core business entities (Stock, Portfolio, Alert)
- Business rules and validation
- Domain services

**Data Access Layer**
- Database repositories
- Query builders
- ORM (SQLAlchemy)
- Cache abstraction

**Infrastructure Layer**
- External API integrations
- Email notifications
- File storage
- Monitoring/logging

#### 2.2.2 Microservices-Ready Monolith

Current implementation uses a **modular monolith** architecture that can be split into microservices if needed:

**Module Boundaries**:
```
├── Stock Service (read-only public data)
├── User Service (authentication, profiles)
├── Portfolio Service (user-specific data)
├── Alert Service (notifications)
├── Screening Service (complex queries)
└── Admin Service (internal operations)
```

Each module has:
- Independent database tables
- Clear API boundaries
- Minimal cross-module dependencies

### 2.3 Component Interaction

#### 2.3.1 Stock Screening Flow

```
┌─────────┐
│ Browser │
└────┬────┘
     │ 1. POST /v1/screen (filters)
     ▼
┌─────────────┐
│ NGINX       │
│ (Rate Limit)│
└────┬────────┘
     │ 2. Forward request
     ▼
┌─────────────────┐
│ FastAPI Backend │
│                 │
│ 3. Check cache ─┼───────► ┌─────────┐
│    (Redis)      │          │  Redis  │
└────┬────────────┘          └─────────┘
     │ 4. Cache miss
     │
     │ 5. Build query
     ▼
┌──────────────────┐
│ PostgreSQL       │
│                  │
│ 6. Execute query │
│    on screening_ │
│    view (indexed)│
└────┬─────────────┘
     │ 7. Results
     ▼
┌─────────────────┐
│ FastAPI Backend │
│                 │
│ 8. Cache results├────────► Redis (TTL: 5min)
│ 9. Format JSON  │
└────┬────────────┘
     │ 10. Response
     ▼
┌─────────┐
│ Browser │
└─────────┘
```

#### 2.3.2 Data Pipeline Flow

```
        18:00 KST (Market Close)
                │
                ▼
┌───────────────────────────────┐
│  Airflow Scheduler            │
│  Triggers: daily_price_       │
│           ingestion DAG       │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  Task 1: Fetch KRX Prices     │
│  - HTTP GET to KRX API        │
│  - Receive JSON/XML data      │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  Task 2: Validate Data        │
│  - Check price relationships  │
│  - Verify completeness        │
│  - Flag invalid records       │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  Task 3: Load to Database     │
│  - UPSERT to daily_prices     │
│  - Batch commit (1000 rows)   │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  Task 4: Check Completeness   │
│  - Verify 95%+ stocks updated │
│  - Alert if threshold missed  │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  Task 5: Trigger Indicator    │
│         Calculation DAG       │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  Indicator Calculation DAG    │
│  - Calculate 200+ indicators  │
│  - Update screening views     │
│  - Duration: ~20 minutes      │
└───────────────────────────────┘
```

### 2.4 Data Flow Diagrams

#### 2.4.1 User Authentication Flow

```
┌───────┐                    ┌─────────┐                    ┌──────────┐
│ User  │                    │ Backend │                    │ Database │
└───┬───┘                    └────┬────┘                    └────┬─────┘
    │                             │                              │
    │ POST /auth/login           │                              │
    │ {email, password}          │                              │
    ├────────────────────────────►│                              │
    │                             │                              │
    │                             │ SELECT * FROM users         │
    │                             │ WHERE email = ?              │
    │                             ├─────────────────────────────►│
    │                             │                              │
    │                             │ Return user row              │
    │                             │◄─────────────────────────────┤
    │                             │                              │
    │                             │ bcrypt.verify(password,      │
    │                             │   user.password_hash)        │
    │                             │                              │
    │                             │ Generate JWT tokens:         │
    │                             │ - access_token (15min)       │
    │                             │ - refresh_token (30 days)    │
    │                             │                              │
    │                             │ INSERT INTO refresh_tokens   │
    │                             ├─────────────────────────────►│
    │                             │                              │
    │ 200 OK                      │                              │
    │ {access_token,              │                              │
    │  refresh_token, user}       │                              │
    │◄────────────────────────────┤                              │
    │                             │                              │
    │ Subsequent requests:        │                              │
    │ Authorization: Bearer       │                              │
    │   <access_token>            │                              │
    ├────────────────────────────►│                              │
    │                             │                              │
    │                             │ Verify JWT signature         │
    │                             │ Check expiry                 │
    │                             │                              │
    │ 200 OK {data}               │                              │
    │◄────────────────────────────┤                              │
    │                             │                              │
```

---