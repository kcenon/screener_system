# Software Design Specification (SDS)
# Stock Screening Platform

## Document Control

| Item | Details |
|------|---------|
| **Project Name** | Stock Screening Platform |
| **Document Version** | 1.0 |
| **Status** | Final |
| **Created Date** | 2025-11-09 |
| **Last Updated** | 2025-11-09 |
| **Authors** | Architecture Team |
| **Reviewers** | Engineering Team, QA Team |
| **Classification** | Internal - Confidential |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Component Design](#3-component-design)
4. [Database Design](#4-database-design)
5. [API Design](#5-api-design)
6. [Data Pipeline Design](#6-data-pipeline-design)
7. [Security Design](#7-security-design)
8. [Performance Design](#8-performance-design)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Technology Stack](#10-technology-stack)
11. [Design Decisions](#11-design-decisions)
12. [Appendices](#12-appendices)

---

## 1. Introduction

### 1.1 Purpose

This Software Design Specification (SDS) describes the technical design of the Stock Screening Platform. It provides detailed information about:

- System architecture and component interactions
- Database schema and data models
- API design and interface specifications
- Data processing pipelines
- Security mechanisms
- Performance optimization strategies

**Audience**: Software architects, senior developers, DevOps engineers, and technical stakeholders.

### 1.2 Scope

This document covers the design of all major subsystems:

- **Frontend**: React-based Single Page Application (SPA)
- **Backend API**: FastAPI REST API server
- **Database**: PostgreSQL with TimescaleDB extension
- **Data Pipeline**: Apache Airflow orchestration
- **Infrastructure**: Docker containerization and deployment

### 1.3 Design Goals

1. **Scalability**: Support 10,000+ concurrent users with horizontal scaling
2. **Performance**: Sub-500ms query response times for screening operations
3. **Reliability**: 99.9% uptime with automated failover
4. **Maintainability**: Clean architecture with separation of concerns
5. **Security**: Defense-in-depth with multiple security layers

### 1.4 References

- [Product Requirements Document (PRD)](PRD.md)
- [Software Requirements Specification (SRS)](SRS.md)
- [Database Schema](../database/README.md)
- [API Documentation](../api/README.md)

---

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

## 3. Component Design

### 3.1 Frontend Architecture

#### 3.1.1 Directory Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── common/          # Buttons, inputs, modals
│   │   ├── stock/           # Stock-related components
│   │   ├── portfolio/       # Portfolio management
│   │   └── charts/          # TradingView chart wrappers
│   │
│   ├── pages/               # Route-level page components
│   │   ├── HomePage.tsx
│   │   ├── ScreenerPage.tsx
│   │   ├── StockDetailPage.tsx
│   │   ├── PortfolioPage.tsx
│   │   └── AlertsPage.tsx
│   │
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.ts       # Authentication state
│   │   ├── useStockData.ts  # Stock data fetching
│   │   └── useWebSocket.ts  # Real-time updates
│   │
│   ├── services/            # API client services
│   │   ├── api.ts           # Axios instance setup
│   │   ├── stockService.ts  # Stock-related API calls
│   │   ├── authService.ts   # Authentication API
│   │   └── portfolioService.ts
│   │
│   ├── store/               # Zustand state management
│   │   ├── authStore.ts     # Auth state (user, tokens)
│   │   ├── stockStore.ts    # Stock data cache
│   │   └── uiStore.ts       # UI state (modals, etc.)
│   │
│   ├── utils/               # Utility functions
│   │   ├── formatting.ts    # Number/date formatting
│   │   ├── validation.ts    # Form validation
│   │   └── constants.ts     # App constants
│   │
│   ├── types/               # TypeScript type definitions
│   │   ├── stock.types.ts
│   │   ├── user.types.ts
│   │   └── api.types.ts
│   │
│   ├── App.tsx              # Root component
│   ├── main.tsx             # Entry point
│   └── router.tsx           # React Router setup
│
├── public/                  # Static assets
│   ├── index.html
│   └── assets/
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

#### 3.1.2 Component Design Patterns

**Container/Presentational Pattern**

```typescript
// Container Component (ScreenerPageContainer.tsx)
const ScreenerPageContainer: React.FC = () => {
  const [filters, setFilters] = useState<ScreenFilters>({});
  const [results, setResults] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const data = await stockService.screenStocks(filters);
      setResults(data.stocks);
    } catch (error) {
      toast.error('Failed to fetch stocks');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScreenerPage
      filters={filters}
      onFiltersChange={setFilters}
      results={results}
      loading={loading}
      onSearch={handleSearch}
    />
  );
};

// Presentational Component (ScreenerPage.tsx)
interface ScreenerPageProps {
  filters: ScreenFilters;
  onFiltersChange: (filters: ScreenFilters) => void;
  results: Stock[];
  loading: boolean;
  onSearch: () => void;
}

const ScreenerPage: React.FC<ScreenerPageProps> = ({
  filters,
  onFiltersChange,
  results,
  loading,
  onSearch
}) => {
  return (
    <div className="screener-page">
      <FilterPanel filters={filters} onChange={onFiltersChange} />
      <ResultsTable results={results} loading={loading} />
      <Button onClick={onSearch}>Search</Button>
    </div>
  );
};
```

**Custom Hooks Pattern**

```typescript
// hooks/useStockData.ts
export const useStockData = (stockCode: string) => {
  const { data, error, isLoading } = useQuery({
    queryKey: ['stock', stockCode],
    queryFn: () => stockService.getStock(stockCode),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });

  return {
    stock: data,
    error,
    isLoading,
  };
};

// Usage in component
const StockDetailPage: React.FC = () => {
  const { stockCode } = useParams();
  const { stock, error, isLoading } = useStockData(stockCode);

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;

  return <StockDetails stock={stock} />;
};
```

#### 3.1.3 State Management (Zustand)

```typescript
// store/authStore.ts
interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: localStorage.getItem('access_token'),
  isAuthenticated: false,

  login: async (email, password) => {
    const response = await authService.login(email, password);
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    set({
      user: response.user,
      accessToken: response.access_token,
      isAuthenticated: true,
    });
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, accessToken: null, isAuthenticated: false });
  },

  refreshToken: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      get().logout();
      return;
    }

    try {
      const response = await authService.refresh(refreshToken);
      localStorage.setItem('access_token', response.access_token);
      set({ accessToken: response.access_token });
    } catch (error) {
      get().logout();
    }
  },
}));
```

### 3.2 Backend Architecture

#### 3.2.1 Directory Structure

```
backend/
├── app/
│   ├── api/                 # API endpoints
│   │   ├── v1/              # API version 1
│   │   │   ├── auth.py      # Authentication endpoints
│   │   │   ├── stocks.py    # Stock endpoints
│   │   │   ├── screening.py # Screening endpoints
│   │   │   ├── portfolios.py
│   │   │   ├── alerts.py
│   │   │   └── users.py
│   │   └── dependencies.py  # Dependency injection
│   │
│   ├── core/                # Core functionality
│   │   ├── config.py        # Configuration management
│   │   ├── security.py      # JWT, password hashing
│   │   ├── cache.py         # Redis cache wrapper
│   │   └── exceptions.py    # Custom exceptions
│   │
│   ├── db/                  # Database layer
│   │   ├── base.py          # Base model class
│   │   ├── session.py       # Database session management
│   │   └── models/          # SQLAlchemy models
│   │       ├── stock.py
│   │       ├── user.py
│   │       ├── portfolio.py
│   │       └── alert.py
│   │
│   ├── schemas/             # Pydantic schemas
│   │   ├── stock.py         # Stock DTOs
│   │   ├── user.py          # User DTOs
│   │   ├── portfolio.py
│   │   └── screening.py
│   │
│   ├── services/            # Business logic
│   │   ├── stock_service.py
│   │   ├── screening_service.py
│   │   ├── portfolio_service.py
│   │   ├── alert_service.py
│   │   └── notification_service.py
│   │
│   ├── repositories/        # Data access layer
│   │   ├── stock_repository.py
│   │   ├── user_repository.py
│   │   └── portfolio_repository.py
│   │
│   ├── celery_app.py        # Celery configuration
│   ├── tasks/               # Background tasks
│   │   ├── alerts.py        # Alert checking tasks
│   │   └── reports.py       # Report generation
│   │
│   └── main.py              # FastAPI application
│
├── tests/                   # Test suites
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── alembic/                 # Database migrations
│   ├── versions/
│   └── env.py
│
├── requirements.txt
├── pytest.ini
└── Dockerfile
```

#### 3.2.2 Layered Architecture Implementation

**API Layer** (api/v1/stocks.py)

```python
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.stock import Stock, StockDetail
from app.services.stock_service import StockService
from app.api.dependencies import get_stock_service

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.get("/{stock_code}", response_model=StockDetail)
async def get_stock(
    stock_code: str,
    stock_service: StockService = Depends(get_stock_service)
):
    """Get detailed stock information."""
    stock = await stock_service.get_stock_by_code(stock_code)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@router.get("", response_model=List[Stock])
async def list_stocks(
    market: Optional[str] = Query(None, regex="^(KOSPI|KOSDAQ|ALL)$"),
    sector: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    stock_service: StockService = Depends(get_stock_service)
):
    """List all stocks with optional filters."""
    return await stock_service.list_stocks(
        market=market,
        sector=sector,
        page=page,
        per_page=per_page
    )
```

**Service Layer** (services/stock_service.py)

```python
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.stock_repository import StockRepository
from app.core.cache import cache
from app.schemas.stock import Stock, StockDetail

class StockService:
    """Business logic for stock operations."""

    def __init__(self, db: AsyncSession):
        self.repository = StockRepository(db)

    async def get_stock_by_code(self, stock_code: str) -> Optional[StockDetail]:
        """Get stock with indicators and latest price."""
        # Try cache first
        cached = await cache.get(f"stock:{stock_code}")
        if cached:
            return StockDetail(**cached)

        # Fetch from database
        stock = await self.repository.get_by_code(stock_code)
        if not stock:
            return None

        # Get latest price and indicators
        latest_price = await self.repository.get_latest_price(stock_code)
        indicators = await self.repository.get_latest_indicators(stock_code)

        stock_detail = StockDetail(
            **stock.dict(),
            latest_price=latest_price,
            indicators=indicators
        )

        # Cache for 5 minutes
        await cache.set(
            f"stock:{stock_code}",
            stock_detail.dict(),
            ttl=300
        )

        return stock_detail

    async def list_stocks(
        self,
        market: Optional[str] = None,
        sector: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ) -> List[Stock]:
        """List stocks with pagination."""
        return await self.repository.list_stocks(
            market=market,
            sector=sector,
            offset=(page - 1) * per_page,
            limit=per_page
        )
```

**Repository Layer** (repositories/stock_repository.py)

```python
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.stock import Stock, DailyPrice, CalculatedIndicator

class StockRepository:
    """Data access layer for stocks."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_code(self, stock_code: str) -> Optional[Stock]:
        """Get stock by code."""
        result = await self.db.execute(
            select(Stock).where(Stock.code == stock_code)
        )
        return result.scalar_one_or_none()

    async def get_latest_price(self, stock_code: str) -> Optional[DailyPrice]:
        """Get most recent price data."""
        result = await self.db.execute(
            select(DailyPrice)
            .where(DailyPrice.stock_code == stock_code)
            .order_by(DailyPrice.trade_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_indicators(
        self,
        stock_code: str
    ) -> Optional[CalculatedIndicator]:
        """Get latest calculated indicators."""
        result = await self.db.execute(
            select(CalculatedIndicator)
            .where(CalculatedIndicator.stock_code == stock_code)
            .order_by(CalculatedIndicator.calculation_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_stocks(
        self,
        market: Optional[str] = None,
        sector: Optional[str] = None,
        offset: int = 0,
        limit: int = 50
    ) -> List[Stock]:
        """List stocks with filters."""
        query = select(Stock).where(Stock.delisting_date.is_(None))

        if market and market != "ALL":
            query = query.where(Stock.market == market)

        if sector:
            query = query.where(Stock.sector == sector)

        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()
```

#### 3.2.3 Dependency Injection

```python
# api/dependencies.py
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.stock_service import StockService
from app.core.security import decode_access_token

security = HTTPBearer()

async def get_stock_service(
    db: AsyncSession = Depends(get_db)
) -> StockService:
    """Dependency to get StockService instance."""
    return StockService(db)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user."""
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
```

### 3.3 Caching Strategy

#### 3.3.1 Redis Cache Architecture

```python
# core/cache.py
from typing import Any, Optional
import json
import redis.asyncio as redis
from app.core.config import settings

class CacheManager:
    """Redis cache manager with async support."""

    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (seconds)."""
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )

    async def delete(self, key: str):
        """Delete key from cache."""
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return await self.redis.exists(key) > 0

cache = CacheManager()
```

#### 3.3.2 Cache Patterns

**Read-Through Cache**

```python
async def get_stock_with_cache(stock_code: str) -> StockDetail:
    # Try cache
    cached = await cache.get(f"stock:{stock_code}")
    if cached:
        return StockDetail(**cached)

    # Cache miss - fetch from DB
    stock = await fetch_stock_from_db(stock_code)

    # Store in cache
    await cache.set(f"stock:{stock_code}", stock.dict(), ttl=300)

    return stock
```

**Cache Invalidation**

```python
async def update_stock_price(stock_code: str, price_data: dict):
    # Update database
    await db.update_price(stock_code, price_data)

    # Invalidate cache
    await cache.delete(f"stock:{stock_code}")
    await cache.delete(f"prices:{stock_code}")
```

**Cache Warming**

```python
# tasks/cache_warming.py
@celery_app.task
def warm_popular_stocks_cache():
    """Pre-load popular stocks into cache."""
    popular_stocks = ["005930", "000660", "035420"]  # Samsung, SK Hynix, NAVER

    for stock_code in popular_stocks:
        stock_data = fetch_stock_from_db(stock_code)
        cache.set(f"stock:{stock_code}", stock_data.dict(), ttl=600)
```

---

## 4. Database Design

### 4.1 Entity-Relationship Diagram

```
┌─────────────────┐
│     stocks      │
│─────────────────│
│ code (PK)       │
│ name            │
│ market          │
│ sector          │
│ industry        │
│ listing_date    │
│ delisting_date  │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴───────────────────────────────────────┐
    │                                            │
    ▼                                            ▼
┌────────────────────┐                  ┌─────────────────────┐
│   daily_prices     │                  │ financial_statements│
│────────────────────│                  │─────────────────────│
│ stock_code (PK,FK) │                  │ id (PK)             │
│ trade_date (PK)    │                  │ stock_code (FK)     │
│ open_price         │                  │ period_type         │
│ high_price         │                  │ fiscal_year         │
│ low_price          │                  │ fiscal_quarter      │
│ close_price        │                  │ revenue             │
│ volume             │                  │ operating_profit    │
│ market_cap         │                  │ net_profit          │
└────────────────────┘                  │ total_assets        │
         │                               │ total_liabilities   │
         │ 1:1                           │ equity              │
         ▼                               └─────────────────────┘
┌────────────────────────┐                        │
│ calculated_indicators  │                        │
│────────────────────────│                        │
│ stock_code (PK,FK)     │                        │
│ calculation_date (PK)  │                        │
│ per, pbr, psr          │◄───────────────────────┘
│ roe, roa, margins      │           (Used for calculations)
│ growth metrics         │
│ technical indicators   │
│ composite scores       │
└────────────────────────┘

┌─────────────┐
│    users    │
│─────────────│
│ id (PK)     │
│ email       │
│ password    │
│ tier        │
└──────┬──────┘
       │
       │ 1:N
       │
   ┌───┴─────────────┬──────────────┬──────────────┐
   ▼                 ▼              ▼              ▼
┌──────────┐  ┌────────────┐  ┌──────────┐  ┌──────────┐
│portfolios│  │  alerts    │  │watchlists│  │ saved_   │
│──────────│  │────────────│  │──────────│  │ screens  │
│ id (PK)  │  │ id (PK)    │  │ id (PK)  │  │ id (PK)  │
│ user (FK)│  │ user (FK)  │  │ user (FK)│  │ user (FK)│
│ name     │  │ stock (FK) │  │ name     │  │ name     │
└────┬─────┘  │ condition  │  └────┬─────┘  │ filters  │
     │        │ threshold  │       │        └──────────┘
     │ 1:N    └────────────┘       │ N:M
     ▼                              ▼
┌─────────────┐            ┌────────────────┐
│  holdings   │            │ watchlist_items│
│─────────────│            │────────────────│
│ id (PK)     │            │ id (PK)        │
│ portfolio   │            │ watchlist (FK) │
│   (FK)      │            │ stock_code (FK)│
│ stock (FK)  │            └────────────────┘
│ quantity    │
│ avg_price   │
└─────────────┘
```

### 4.2 Table Schemas (Key Tables)

#### 4.2.1 stocks

```sql
CREATE TABLE stocks (
    code VARCHAR(6) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    name_english VARCHAR(100),
    market VARCHAR(10) NOT NULL CHECK (market IN ('KOSPI', 'KOSDAQ')),
    sector VARCHAR(50),
    industry VARCHAR(100),
    listing_date DATE,
    delisting_date DATE,
    shares_outstanding BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_stocks_market ON stocks(market) WHERE delisting_date IS NULL;
CREATE INDEX idx_stocks_sector ON stocks(sector) WHERE delisting_date IS NULL;
CREATE INDEX idx_stocks_name_trgm ON stocks USING gin (name gin_trgm_ops);
```

**Design Decisions**:
- `code` as PRIMARY KEY (natural key, always 6 digits)
- `delisting_date IS NULL` for active stocks (cleaner than boolean flag)
- Trigram index on `name` for fuzzy search
- Partial indexes on `market` and `sector` (only active stocks)

#### 4.2.2 daily_prices (TimescaleDB Hypertable)

```sql
CREATE TABLE daily_prices (
    stock_code VARCHAR(6) NOT NULL,
    trade_date DATE NOT NULL,
    open_price INTEGER,
    high_price INTEGER,
    low_price INTEGER,
    close_price INTEGER NOT NULL,
    adjusted_close INTEGER,
    volume BIGINT,
    trading_value BIGINT,
    market_cap BIGINT,
    PRIMARY KEY (stock_code, trade_date),
    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('daily_prices', 'trade_date');

-- Compression policy (compress data older than 365 days)
ALTER TABLE daily_prices SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'stock_code'
);

SELECT add_compression_policy('daily_prices', INTERVAL '365 days');

-- Retention policy (delete data older than 10 years)
SELECT add_retention_policy('daily_prices', INTERVAL '10 years');
```

**Design Decisions**:
- TimescaleDB for time-series optimization
- Composite PRIMARY KEY (stock_code, trade_date)
- Compression after 1 year (10x storage reduction)
- Automatic data retention (10 years)
- Integer prices (stored in KRW, avoid floating-point issues)

#### 4.2.3 calculated_indicators

```sql
CREATE TABLE calculated_indicators (
    stock_code VARCHAR(6) NOT NULL,
    calculation_date DATE NOT NULL,

    -- Valuation (15 metrics)
    per NUMERIC(10, 2),
    pbr NUMERIC(10, 2),
    psr NUMERIC(10, 2),
    -- ... (200+ total indicators)

    -- Composite Scores
    quality_score INTEGER CHECK (quality_score BETWEEN 0 AND 100),
    value_score INTEGER CHECK (value_score BETWEEN 0 AND 100),
    growth_score INTEGER CHECK (growth_score BETWEEN 0 AND 100),
    overall_score INTEGER CHECK (overall_score BETWEEN 0 AND 100),

    PRIMARY KEY (stock_code, calculation_date),
    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE
);

CREATE INDEX idx_indicators_date ON calculated_indicators(calculation_date DESC);
```

**Design Decisions**:
- Composite PRIMARY KEY for historical tracking
- Scores constrained to 0-100 range
- Indexed by date for "latest indicators" queries

### 4.3 Materialized Views

#### 4.3.1 stock_screening_view

```sql
CREATE MATERIALIZED VIEW stock_screening_view AS
SELECT
    s.code,
    s.name,
    s.market,
    s.sector,
    dp.close_price,
    dp.volume,
    dp.market_cap,
    ci.per,
    ci.pbr,
    ci.psr,
    ci.roe,
    ci.roa,
    ci.operating_margin,
    ci.net_margin,
    ci.revenue_growth_yoy,
    ci.profit_growth_yoy,
    ci.debt_to_equity,
    ci.current_ratio,
    ci.dividend_yield,
    ci.quality_score,
    ci.value_score,
    ci.growth_score,
    ci.overall_score,
    ci.price_change_1d,
    ci.price_change_1w,
    ci.price_change_1m,
    ci.volume_surge_pct
FROM stocks s
INNER JOIN LATERAL (
    SELECT *
    FROM daily_prices
    WHERE stock_code = s.code
    ORDER BY trade_date DESC
    LIMIT 1
) dp ON true
INNER JOIN LATERAL (
    SELECT *
    FROM calculated_indicators
    WHERE stock_code = s.code
    ORDER BY calculation_date DESC
    LIMIT 1
) ci ON true
WHERE s.delisting_date IS NULL;

-- Indexes for screening queries
CREATE UNIQUE INDEX idx_screening_code ON stock_screening_view(code);
CREATE INDEX idx_screening_market ON stock_screening_view(market);
CREATE INDEX idx_screening_per ON stock_screening_view(per) WHERE per IS NOT NULL;
CREATE INDEX idx_screening_pbr ON stock_screening_view(pbr) WHERE pbr IS NOT NULL;
CREATE INDEX idx_screening_roe ON stock_screening_view(roe) WHERE roe IS NOT NULL;
CREATE INDEX idx_screening_scores ON stock_screening_view(quality_score, value_score, growth_score);

-- Refresh policy (updated after indicator calculations)
CREATE OR REPLACE FUNCTION refresh_screening_view()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY stock_screening_view;
END;
$$ LANGUAGE plpgsql;
```

**Design Decisions**:
- Pre-joins latest prices and indicators
- Eliminates expensive JOIN during screening queries
- CONCURRENTLY refresh to avoid locking
- Indexes on common filter columns
- Partial indexes (skip NULL values)

### 4.4 Database Functions

#### 4.4.1 get_market_overview()

```sql
CREATE OR REPLACE FUNCTION get_market_overview(p_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
    market VARCHAR,
    total_stocks INTEGER,
    advancers INTEGER,
    decliners INTEGER,
    unchanged INTEGER,
    total_volume BIGINT,
    total_value BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.market,
        COUNT(*)::INTEGER AS total_stocks,
        COUNT(*) FILTER (WHERE ci.price_change_1d > 0)::INTEGER AS advancers,
        COUNT(*) FILTER (WHERE ci.price_change_1d < 0)::INTEGER AS decliners,
        COUNT(*) FILTER (WHERE ci.price_change_1d = 0)::INTEGER AS unchanged,
        SUM(dp.volume) AS total_volume,
        SUM(dp.trading_value) AS total_value
    FROM stocks s
    INNER JOIN daily_prices dp ON s.code = dp.stock_code AND dp.trade_date = p_date
    LEFT JOIN calculated_indicators ci ON s.code = ci.stock_code AND ci.calculation_date = p_date
    WHERE s.delisting_date IS NULL
    GROUP BY s.market;
END;
$$ LANGUAGE plpgsql STABLE;
```

#### 4.4.2 get_hot_stocks()

```sql
CREATE OR REPLACE FUNCTION get_hot_stocks(
    p_min_surge_pct NUMERIC DEFAULT 150,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    stock_code VARCHAR,
    stock_name VARCHAR,
    close_price INTEGER,
    volume BIGINT,
    volume_surge_pct NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.code,
        s.name,
        dp.close_price,
        dp.volume,
        ci.volume_surge_pct
    FROM stocks s
    INNER JOIN LATERAL (
        SELECT *
        FROM daily_prices
        WHERE stock_code = s.code
        ORDER BY trade_date DESC
        LIMIT 1
    ) dp ON true
    INNER JOIN LATERAL (
        SELECT *
        FROM calculated_indicators
        WHERE stock_code = s.code
        ORDER BY calculation_date DESC
        LIMIT 1
    ) ci ON true
    WHERE s.delisting_date IS NULL
      AND ci.volume_surge_pct >= p_min_surge_pct
    ORDER BY ci.volume_surge_pct DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;
```

### 4.5 Query Optimization Strategies

#### 4.5.1 Index Usage Analysis

```sql
-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Find unused indexes
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey'
  AND schemaname = 'public';
```

#### 4.5.2 Query Performance Monitoring

```sql
-- Enable pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow queries
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- queries slower than 100ms
ORDER BY mean_exec_time DESC
LIMIT 20;
```

---

## 5. API Design

### 5.1 RESTful API Principles

**Design Principles**:
1. **Resource-Based URLs**: `/stocks/{code}`, `/portfolios/{id}`
2. **HTTP Methods**: GET (read), POST (create), PUT/PATCH (update), DELETE (delete)
3. **Stateless**: No server-side session state
4. **Hypermedia (HATEOAS)**: Include links in responses (Phase 2+)
5. **Versioning**: `/v1/` in URL path

### 5.2 API Endpoints

#### 5.2.1 Authentication Endpoints

```yaml
POST /v1/auth/register
  Summary: Register new user account
  Request Body:
    {
      "email": "user@example.com",
      "password": "SecurePass123",
      "name": "John Doe"
    }
  Response: 201 Created
    {
      "access_token": "eyJ...",
      "refresh_token": "eyJ...",
      "user": {
        "id": "uuid",
        "email": "user@example.com",
        "name": "John Doe",
        "tier": "free"
      }
    }

POST /v1/auth/login
  Summary: Login and receive JWT tokens
  Request Body:
    {
      "email": "user@example.com",
      "password": "SecurePass123"
    }
  Response: 200 OK
    {
      "access_token": "eyJ...",
      "refresh_token": "eyJ...",
      "user": { ... }
    }

POST /v1/auth/refresh
  Summary: Refresh expired access token
  Request Body:
    {
      "refresh_token": "eyJ..."
    }
  Response: 200 OK
    {
      "access_token": "eyJ..."
    }

POST /v1/auth/logout
  Summary: Revoke refresh token
  Headers: Authorization: Bearer <access_token>
  Response: 204 No Content
```

#### 5.2.2 Stock Endpoints

```yaml
GET /v1/stocks
  Summary: List all stocks with pagination
  Query Parameters:
    - market: KOSPI | KOSDAQ | ALL (default: ALL)
    - sector: string (optional)
    - page: integer (default: 1)
    - per_page: integer (default: 50, max: 100)
  Response: 200 OK
    {
      "stocks": [
        {
          "code": "005930",
          "name": "삼성전자",
          "market": "KOSPI",
          "sector": "Technology",
          "industry": "Semiconductors"
        },
        ...
      ],
      "meta": {
        "page": 1,
        "per_page": 50,
        "total": 2400,
        "pages": 48
      }
    }

GET /v1/stocks/{stock_code}
  Summary: Get detailed stock information
  Path Parameters:
    - stock_code: 6-digit string
  Response: 200 OK
    {
      "code": "005930",
      "name": "삼성전자",
      "market": "KOSPI",
      "sector": "Technology",
      "latest_price": {
        "close_price": 71000,
        "change_pct": 1.43,
        "volume": 15234567,
        "market_cap": 423000000000000,
        "trade_date": "2024-11-08"
      },
      "indicators": {
        "per": 15.2,
        "pbr": 1.4,
        "roe": 12.5,
        "dividend_yield": 2.8,
        "quality_score": 85,
        "value_score": 72,
        "growth_score": 65
      }
    }

GET /v1/stocks/{stock_code}/prices
  Summary: Get historical price data
  Path Parameters:
    - stock_code: 6-digit string
  Query Parameters:
    - from_date: YYYY-MM-DD (default: 1 year ago)
    - to_date: YYYY-MM-DD (default: today)
    - interval: daily | weekly | monthly (default: daily)
  Response: 200 OK
    {
      "stock_code": "005930",
      "interval": "daily",
      "prices": [
        {
          "trade_date": "2024-11-08",
          "open": 70000,
          "high": 72000,
          "low": 69500,
          "close": 71000,
          "volume": 15234567
        },
        ...
      ]
    }

GET /v1/stocks/{stock_code}/financials
  Summary: Get financial statements
  Path Parameters:
    - stock_code: 6-digit string
  Query Parameters:
    - period_type: quarterly | annual (default: quarterly)
    - years: integer (default: 5, max: 10)
  Response: 200 OK
    {
      "stock_code": "005930",
      "period_type": "quarterly",
      "financials": [
        {
          "fiscal_year": 2024,
          "fiscal_quarter": 3,
          "report_date": "2024-10-31",
          "revenue": 67400000000000,
          "operating_profit": 12520000000000,
          "net_profit": 9180000000000,
          "eps": 6250.00,
          "roe": 12.5
        },
        ...
      ]
    }
```

#### 5.2.3 Screening Endpoint

```yaml
POST /v1/screen
  Summary: Screen stocks with custom filters
  Request Body:
    {
      "market": "KOSPI" | "KOSDAQ" | "ALL",
      "filters": {
        "per": {"min": 0, "max": 15},
        "pbr": {"min": 0, "max": 1.5},
        "roe": {"min": 10},
        "dividend_yield": {"min": 3},
        "quality_score": {"min": 70}
      },
      "sort_by": "market_cap" | "per" | "roe" | ...,
      "order": "asc" | "desc",
      "page": 1,
      "per_page": 50
    }
  Response: 200 OK
    {
      "stocks": [
        {
          "code": "005930",
          "name": "삼성전자",
          "close_price": 71000,
          "per": 15.2,
          "pbr": 1.4,
          "roe": 12.5,
          "dividend_yield": 2.8,
          "quality_score": 85
        },
        ...
      ],
      "meta": {
        "page": 1,
        "per_page": 50,
        "total": 123,
        "pages": 3,
        "query_time_ms": 234
      }
    }
```

#### 5.2.4 Portfolio Endpoints

```yaml
POST /v1/portfolios
  Summary: Create new portfolio
  Headers: Authorization: Bearer <access_token>
  Request Body:
    {
      "name": "Growth Portfolio",
      "description": "High-growth tech stocks"
    }
  Response: 201 Created
    {
      "id": "uuid",
      "name": "Growth Portfolio",
      "description": "High-growth tech stocks",
      "created_at": "2024-11-08T10:30:00Z"
    }

GET /v1/portfolios
  Summary: List user's portfolios
  Headers: Authorization: Bearer <access_token>
  Response: 200 OK
    {
      "portfolios": [
        {
          "id": "uuid",
          "name": "Growth Portfolio",
          "holdings_count": 5,
          "total_value": 50000000,
          "unrealized_gain": 2500000,
          "unrealized_gain_pct": 5.26
        },
        ...
      ]
    }

GET /v1/portfolios/{portfolio_id}
  Summary: Get portfolio details with holdings
  Headers: Authorization: Bearer <access_token>
  Path Parameters:
    - portfolio_id: UUID
  Response: 200 OK
    {
      "id": "uuid",
      "name": "Growth Portfolio",
      "holdings": [
        {
          "stock_code": "005930",
          "stock_name": "삼성전자",
          "quantity": 10,
          "avg_price": 68000,
          "current_price": 71000,
          "purchase_value": 680000,
          "current_value": 710000,
          "unrealized_gain": 30000,
          "unrealized_gain_pct": 4.41
        },
        ...
      ],
      "summary": {
        "total_purchase_value": 47500000,
        "total_current_value": 50000000,
        "total_unrealized_gain": 2500000,
        "total_unrealized_gain_pct": 5.26
      }
    }

POST /v1/portfolios/{portfolio_id}/holdings
  Summary: Add stock to portfolio
  Headers: Authorization: Bearer <access_token>
  Request Body:
    {
      "stock_code": "005930",
      "quantity": 10,
      "avg_price": 68000,
      "purchase_date": "2024-09-10"
    }
  Response: 201 Created
    {
      "id": "uuid",
      "stock_code": "005930",
      "quantity": 10,
      "avg_price": 68000
    }
```

### 5.3 Error Handling

#### 5.3.1 Error Response Format

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": ["specific error"]
  },
  "timestamp": "2024-11-08T10:30:00Z",
  "path": "/v1/portfolios",
  "request_id": "uuid"
}
```

#### 5.3.2 HTTP Status Codes

| Code | Error Type | Usage |
|------|------------|-------|
| 400 | Bad Request | Invalid request parameters or validation errors |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Valid token but insufficient permissions (tier) |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource already exists (duplicate email, etc.) |
| 422 | Unprocessable Entity | Semantic errors in request |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Temporary service outage |

#### 5.3.3 Error Examples

**Validation Error (400)**

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid request parameters",
  "details": {
    "per_page": ["must be between 1 and 100"],
    "market": ["must be one of: KOSPI, KOSDAQ, ALL"]
  }
}
```

**Authentication Error (401)**

```json
{
  "error": "UNAUTHORIZED",
  "message": "Invalid or expired access token",
  "details": {}
}
```

**Tier Limit Error (403)**

```json
{
  "error": "TIER_LIMIT_EXCEEDED",
  "message": "Feature not available in your tier",
  "details": {
    "required_tier": "pro",
    "current_tier": "basic",
    "upgrade_url": "https://screener.kr/pricing"
  }
}
```

**Rate Limit Error (429)**

```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests",
  "details": {
    "limit": 100,
    "remaining": 0,
    "reset_at": "2024-11-08T11:00:00Z"
  }
}
```

### 5.4 Rate Limiting

#### 5.4.1 Rate Limit Implementation

```python
# core/rate_limiter.py
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.core.cache import cache

class RateLimiter:
    """Token bucket rate limiter using Redis."""

    TIER_LIMITS = {
        "free": 100,      # 100 requests/minute
        "basic": 500,     # 500 requests/minute
        "pro": 2000,      # 2000 requests/minute
    }

    async def check_rate_limit(self, user_id: str, tier: str):
        """Check if user has exceeded rate limit."""
        limit = self.TIER_LIMITS.get(tier, 100)
        key = f"rate_limit:{user_id}"

        # Get current count
        current = await cache.get(key)

        if current is None:
            # First request in this window
            await cache.set(key, 1, ttl=60)  # 60 seconds window
            return {
                "limit": limit,
                "remaining": limit - 1,
                "reset_at": datetime.utcnow() + timedelta(seconds=60)
            }

        current = int(current)

        if current >= limit:
            # Rate limit exceeded
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests",
                    "details": {
                        "limit": limit,
                        "remaining": 0,
                        "reset_at": (
                            datetime.utcnow() + timedelta(seconds=60)
                        ).isoformat()
                    }
                }
            )

        # Increment counter
        await cache.redis.incr(key)

        return {
            "limit": limit,
            "remaining": limit - current - 1,
            "reset_at": datetime.utcnow() + timedelta(seconds=60)
        }

rate_limiter = RateLimiter()
```

#### 5.4.2 Rate Limit Middleware

```python
# api/dependencies.py
from fastapi import Request
from app.core.rate_limiter import rate_limiter

async def check_rate_limit(request: Request, user: User = Depends(get_current_user)):
    """Dependency to check rate limits."""
    rate_info = await rate_limiter.check_rate_limit(str(user.id), user.tier)

    # Add rate limit headers
    request.state.rate_limit_info = rate_info

# Middleware to add headers
@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    response = await call_next(request)

    if hasattr(request.state, "rate_limit_info"):
        info = request.state.rate_limit_info
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = info["reset_at"].isoformat()

    return response
```

### 5.5 WebSocket Architecture

#### 5.5.1 WebSocket Server Design

**Purpose**: Real-time bidirectional communication for price updates, order book data, and alerts.

**Architecture**:

```
┌─────────────────────────────────────────────────────────────────┐
│                        WebSocket Clients                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Browser 1   │  │  Browser 2   │  │  Browser N   │          │
│  │  (React)     │  │  (React)     │  │  (React)     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │ WSS              │ WSS              │ WSS
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                 WebSocket Connection Manager                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Connection Pool (10,000+ concurrent connections)          │ │
│  │  - JWT authentication on handshake                         │ │
│  │  - Heartbeat (ping/pong every 30s)                         │ │
│  │  - Auto-reconnect with exponential backoff                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Room-Based Subscription Manager                           │ │
│  │  - Subscribe/unsubscribe to stock codes                    │ │
│  │  - Subscribe to market (KOSPI/KOSDAQ)                      │ │
│  │  - Subscribe to sector                                     │ │
│  │  - Multiple subscriptions per connection                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Redis Pub/Sub Layer                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Channels:                                                  │ │
│  │  - price:{stock_code}     (e.g., price:005930)            │ │
│  │  - orderbook:{stock_code} (e.g., orderbook:005930)        │ │
│  │  - market:{market_type}   (e.g., market:KOSPI)            │ │
│  │  - alert:{user_id}        (e.g., alert:123)               │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────────┘
                           ▲
                           │ Publish Updates
                           │
┌──────────────────────────┴───────────────────────────────────────┐
│               Data Source Adapter (KIS API)                      │
│  - Polls KIS API for price/orderbook updates                    │
│  - Publishes changes to Redis channels                          │
│  - Rate limiting (20 req/sec)                                   │
└──────────────────────────────────────────────────────────────────┘
```

#### 5.5.2 WebSocket Endpoint Implementation

```python
# api/websockets/stock_ws.py
from fastapi import WebSocket, WebSocketDisconnect, Depends
from app.core.auth import verify_ws_token
from app.core.cache import redis_client
import json
import asyncio

class ConnectionManager:
    """Manage WebSocket connections and subscriptions."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.subscriptions: dict[str, set[str]] = {}  # {connection_id: {room1, room2}}
        self.rooms: dict[str, set[str]] = {}  # {room: {conn_id1, conn_id2}}

    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.subscriptions[connection_id] = set()

    def disconnect(self, connection_id: str):
        """Remove connection and all subscriptions."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # Remove from all subscribed rooms
        if connection_id in self.subscriptions:
            for room in self.subscriptions[connection_id]:
                if room in self.rooms:
                    self.rooms[room].discard(connection_id)
            del self.subscriptions[connection_id]

    def subscribe(self, connection_id: str, room: str):
        """Subscribe connection to a room."""
        if connection_id in self.subscriptions:
            self.subscriptions[connection_id].add(room)

        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(connection_id)

    def unsubscribe(self, connection_id: str, room: str):
        """Unsubscribe connection from a room."""
        if connection_id in self.subscriptions:
            self.subscriptions[connection_id].discard(room)

        if room in self.rooms:
            self.rooms[room].discard(connection_id)

    async def send_to_connection(self, connection_id: str, message: dict):
        """Send message to specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            await websocket.send_json(message)

    async def broadcast_to_room(self, room: str, message: dict):
        """Broadcast message to all connections in a room."""
        if room in self.rooms:
            disconnected = []
            for connection_id in self.rooms[room]:
                try:
                    await self.send_to_connection(connection_id, message)
                except Exception:
                    disconnected.append(connection_id)

            # Clean up disconnected clients
            for connection_id in disconnected:
                self.disconnect(connection_id)

manager = ConnectionManager()


@router.websocket("/ws/stocks")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time stock data.

    Authentication: JWT token in query parameter.
    """
    # Verify JWT token
    try:
        user = await verify_ws_token(token)
    except Exception:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    connection_id = f"{user.id}_{datetime.utcnow().timestamp()}"

    await manager.connect(websocket, connection_id)

    try:
        # Start heartbeat task
        heartbeat_task = asyncio.create_task(
            send_heartbeat(websocket, connection_id)
        )

        # Start Redis Pub/Sub listener
        pubsub_task = asyncio.create_task(
            redis_subscriber(connection_id)
        )

        while True:
            # Receive messages from client
            data = await websocket.receive_json()

            message_type = data.get("type")

            if message_type == "subscribe":
                # Subscribe to stock updates
                stock_code = data.get("stock_code")
                room = f"price:{stock_code}"
                manager.subscribe(connection_id, room)

                await websocket.send_json({
                    "type": "subscribed",
                    "stock_code": stock_code,
                    "timestamp": datetime.utcnow().isoformat()
                })

            elif message_type == "unsubscribe":
                # Unsubscribe from stock updates
                stock_code = data.get("stock_code")
                room = f"price:{stock_code}"
                manager.unsubscribe(connection_id, room)

                await websocket.send_json({
                    "type": "unsubscribed",
                    "stock_code": stock_code,
                    "timestamp": datetime.utcnow().isoformat()
                })

            elif message_type == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        heartbeat_task.cancel()
        pubsub_task.cancel()

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(connection_id)
        heartbeat_task.cancel()
        pubsub_task.cancel()


async def send_heartbeat(websocket: WebSocket, connection_id: str):
    """Send periodic heartbeat to keep connection alive."""
    while True:
        try:
            await asyncio.sleep(30)
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception:
            break


async def redis_subscriber(connection_id: str):
    """
    Subscribe to Redis Pub/Sub and forward messages to WebSocket.
    """
    pubsub = redis_client.pubsub()

    while True:
        # Get subscribed rooms for this connection
        rooms = manager.subscriptions.get(connection_id, set())

        # Subscribe to Redis channels for each room
        for room in rooms:
            await pubsub.subscribe(room)

        # Listen for messages
        try:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message and message['type'] == 'message':
                data = json.loads(message['data'])

                # Forward to WebSocket client
                await manager.send_to_connection(connection_id, data)

        except Exception as e:
            logger.error(f"Redis subscriber error: {e}")
            break

        await asyncio.sleep(0.01)  # Prevent tight loop
```

#### 5.5.3 Message Format Specification

**Subscribe Message** (Client → Server):
```json
{
  "type": "subscribe",
  "stock_code": "005930",
  "timestamp": "2025-11-09T10:30:00Z"
}
```

**Price Update Message** (Server → Client):
```json
{
  "type": "price_update",
  "stock_code": "005930",
  "data": {
    "current_price": 75000,
    "change_amount": 1000,
    "change_percent": 1.35,
    "volume": 12500000,
    "timestamp": "2025-11-09T10:30:15.123Z"
  },
  "sequence": 12345,
  "timestamp": "2025-11-09T10:30:15.125Z"
}
```

**Order Book Update Message** (Server → Client):
```json
{
  "type": "orderbook_update",
  "stock_code": "005930",
  "data": {
    "asks": [
      {"price": 75100, "volume": 5000, "total": 5000},
      {"price": 75200, "volume": 3000, "total": 8000},
      // ... up to 10 levels
    ],
    "bids": [
      {"price": 75000, "volume": 8000, "total": 8000},
      {"price": 74900, "volume": 4000, "total": 12000},
      // ... up to 10 levels
    ],
    "spread": 100,
    "spread_pct": 0.13,
    "timestamp": "2025-11-09T10:30:15.123Z"
  },
  "sequence": 12346,
  "timestamp": "2025-11-09T10:30:15.125Z"
}
```

#### 5.5.4 Performance Considerations

**Connection Pooling**:
- Target: Support 10,000+ concurrent connections
- Memory per connection: ~10KB → 100MB for 10K connections
- CPU overhead: Minimal (event-driven architecture)

**Message Batching**:
- Batch updates within 10-50ms window
- Reduce message frequency for high-update stocks
- Example: If price changes 100 times/sec, batch to 20 messages/sec

**Compression**:
- Use per-message deflate extension (WebSocket compression)
- Reduces message size by ~60-70% for JSON payloads

**Redis Pub/Sub Scalability**:
- Horizontal scaling: Multiple API instances subscribe to same Redis
- Automatic broadcasting to all connected clients across instances
- No single point of failure

---

## 6. Data Pipeline Design

### 6.1 Apache Airflow Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Airflow Web UI                            │
│              (DAG Monitoring & Management)                    │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                  Airflow Scheduler                           │
│  - Parses DAGs from dags/ directory                          │
│  - Triggers scheduled runs (cron expressions)                │
│  - Monitors task states (queued, running, success, failed)   │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                  Airflow Executor                            │
│              (LocalExecutor / CeleryExecutor)                 │
│  - Executes tasks in parallel                                │
│  - Manages task concurrency                                  │
└───────────────────────────┬──────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Python Task  │   │  SQL Task     │   │  Bash Task    │
│  (Operators)  │   │  (PostgreSQL) │   │  (Scripts)    │
└───────────────┘   └───────────────┘   └───────────────┘
```

### 6.2 DAG Design

#### 6.2.1 daily_price_ingestion DAG

**Schedule**: Mon-Fri at 18:00 KST (after market close)

**Task Flow**:

```
fetch_krx_prices (5 min)
    ↓
validate_price_data (1 min)
    ↓
load_prices_to_db (2 min)
    ↓
check_data_completeness (30 sec)
    ↓
refresh_timescale_aggregates (1 min)
    ↓
trigger_indicator_calculation
    ↓
log_ingestion_status
```

**Task Implementations**: See data_pipeline/dags/daily_price_ingestion_dag.py

**Failure Handling**:
- **Retries**: 3 attempts with 5-minute intervals
- **Alerts**: Email on failure
- **Partial Success**: Accept if ≥95% completeness

#### 6.2.2 indicator_calculation DAG

**Schedule**: Triggered by daily_price_ingestion

**Task Flow**:

```
calculate_indicators (20 min)
    ↓
refresh_materialized_views (2 min)
    ↓
log_calculation_status
```

**Performance Optimizations**:
- Batch database commits (100 stocks)
- Parallel processing (can be extended to Celery workers)
- Connection pooling

### 6.3 Data Quality Checks

#### 6.3.1 Price Data Validation

```python
def validate_price_data(record: dict) -> List[str]:
    """
    Validate price data quality.

    Returns list of validation errors (empty if valid).
    """
    errors = []

    # Required fields
    required = ['stock_code', 'trade_date', 'close_price', 'volume']
    for field in required:
        if field not in record or record[field] is None:
            errors.append(f"Missing required field: {field}")

    # Price relationships
    if record.get('high_price') and record.get('low_price'):
        if record['high_price'] < record['low_price']:
            errors.append(
                f"High price ({record['high_price']}) < "
                f"Low price ({record['low_price']})"
            )

    if record.get('close_price'):
        high = record.get('high_price')
        low = record.get('low_price')

        if high and record['close_price'] > high:
            errors.append("Close price exceeds high price")

        if low and record['close_price'] < low:
            errors.append("Close price below low price")

    # Positive values
    if record.get('close_price') and record['close_price'] <= 0:
        errors.append("Close price must be positive")

    if record.get('volume') and record['volume'] < 0:
        errors.append("Volume cannot be negative")

    return errors
```

#### 6.3.2 Completeness Monitoring

```python
def check_data_completeness(execution_date: str) -> float:
    """
    Check percentage of stocks with price data for given date.

    Returns completeness percentage (0-100).
    """
    active_stocks_count = db.execute(
        "SELECT COUNT(*) FROM stocks WHERE delisting_date IS NULL"
    ).scalar()

    prices_count = db.execute(
        "SELECT COUNT(*) FROM daily_prices WHERE trade_date = %s",
        execution_date
    ).scalar()

    completeness = (prices_count / active_stocks_count * 100
                    if active_stocks_count > 0 else 0)

    if completeness < 95:
        logger.error(
            f"Data completeness below threshold: {completeness:.1f}%"
        )
        send_alert_email(
            subject="Low Data Completeness",
            body=f"Only {completeness:.1f}% of stocks have price data"
        )

    return completeness
```

### 6.4 Error Handling and Recovery

#### 6.4.1 Retry Strategies

```python
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}
```

**Retry Schedule**:
- 1st retry: after 5 minutes
- 2nd retry: after 10 minutes (exponential backoff)
- 3rd retry: after 20 minutes
- Max delay: 30 minutes

#### 6.4.2 Failure Notifications

```python
def on_failure_callback(context):
    """
    Send notification on task failure.

    Called after all retries exhausted.
    """
    task_instance = context['task_instance']
    dag_id = context['dag'].dag_id
    task_id = task_instance.task_id
    execution_date = context['execution_date']
    exception = context.get('exception')

    send_alert_email(
        subject=f"Airflow Task Failed: {dag_id}.{task_id}",
        body=f"""
        Task: {task_id}
        DAG: {dag_id}
        Execution Date: {execution_date}
        Error: {exception}

        View logs: {task_instance.log_url}
        """
    )

    # Also log to database
    log_task_failure(
        dag_id=dag_id,
        task_id=task_id,
        execution_date=execution_date,
        error_message=str(exception)
    )
```

### 6.5 Real-time Data Integration

#### 6.5.1 KIS API Integration Architecture

**Purpose**: Integrate with Korea Investment & Securities (KIS) Open API for real-time market data.

**Architecture**:

```
┌──────────────────────────────────────────────────────────────────┐
│                     Application Layer                             │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Stock Price Service                                       │  │
│  │  - get_current_price(stock_code)                          │  │
│  │  - get_order_book(stock_code)                             │  │
│  │  - get_historical_prices(stock_code, period)              │  │
│  └────────────────────────┬───────────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│              Data Source Abstraction Layer                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  AbstractDataSource (Interface)                            │  │
│  │  - get_current_price(stock_code) -> StockPrice            │  │
│  │  - get_order_book(stock_code) -> OrderBook                │  │
│  │  - get_historical_prices(...) -> List[OHLCV]              │  │
│  └────────────────────────┬───────────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  KISDataSource   │ │  KRXDataSource   │ │  MockDataSource  │
│  (Primary)       │ │  (Fallback)      │ │  (Development)   │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  KIS API Client  │ │  KRX API Client  │ │  Mock Generator  │
│  with:           │ │                  │ │                  │
│  - OAuth 2.0     │ │                  │ │                  │
│  - Circuit       │ │                  │ │                  │
│    Breaker       │ │                  │ │                  │
│  - Connection    │ │                  │ │                  │
│    Pooling       │ │                  │ │                  │
│  - Rate Limiting │ │                  │ │                  │
└────────┬─────────┘ └──────────────────┘ └──────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│         KIS Open API (Korea Investment & Securities)              │
│  https://openapi.koreainvestment.com:9443                        │
└──────────────────────────────────────────────────────────────────┘
```

#### 6.5.2 KIS API Client Implementation

**OAuth 2.0 Token Management**:

```python
# data_pipeline/clients/kis_api_client.py
from datetime import datetime, timedelta
import asyncio
import httpx
from app.core.config import settings

class KISApiClient:
    """
    Korea Investment & Securities API client.

    Features:
    - OAuth 2.0 authentication with automatic token refresh
    - Connection pooling
    - Circuit breaker pattern
    - Rate limiting (20 req/sec)
    """

    BASE_URL = "https://openapi.koreainvestment.com:9443"

    def __init__(self):
        self._http_client: httpx.AsyncClient | None = None
        self._token: str | None = None
        self._token_expires_at: datetime | None = None
        self._lock = asyncio.Lock()

        # Circuit breaker state
        self._circuit_state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._failure_count = 0
        self._last_failure_time: datetime | None = None
        self._circuit_open_until: datetime | None = None

    async def __aenter__(self):
        """Initialize HTTP client with connection pooling."""
        self._http_client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(
                max_connections=20,
                max_keepalive_connections=10
            ),
            http2=True  # Enable HTTP/2 for better performance
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()

    async def _ensure_valid_token(self) -> str:
        """
        Ensure OAuth token is valid.

        Auto-refresh if expired or within 5 minutes of expiry.
        Thread-safe using asyncio.Lock.
        """
        async with self._lock:
            # Check if token exists and is not expiring soon
            if (
                self._token
                and self._token_expires_at
                and self._token_expires_at > datetime.utcnow() + timedelta(minutes=5)
            ):
                return self._token

            # Fetch new token
            self._token = await self._fetch_new_token()
            self._token_expires_at = datetime.utcnow() + timedelta(hours=24)
            return self._token

    async def _fetch_new_token(self) -> str:
        """Fetch new OAuth access token from KIS API."""
        response = await self._http_client.post(
            "/oauth2/tokenP",
            json={
                "grant_type": "client_credentials",
                "appkey": settings.KIS_APP_KEY,
                "appsecret": settings.KIS_APP_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["access_token"]

    async def _check_circuit_breaker(self):
        """
        Check circuit breaker state before making request.

        States:
        - CLOSED: Normal operation
        - OPEN: Failing, reject requests immediately
        - HALF_OPEN: Testing if system recovered
        """
        if self._circuit_state == "OPEN":
            # Check if timeout expired
            if (
                self._circuit_open_until
                and datetime.utcnow() >= self._circuit_open_until
            ):
                # Transition to HALF_OPEN for testing
                self._circuit_state = "HALF_OPEN"
                self._failure_count = 0
            else:
                # Circuit still open, reject request
                raise CircuitBreakerOpenError(
                    f"Circuit breaker OPEN until {self._circuit_open_until}"
                )

    async def _record_success(self):
        """Record successful request."""
        if self._circuit_state == "HALF_OPEN":
            # Test succeeded, close circuit
            self._circuit_state = "CLOSED"
            self._failure_count = 0
            self._circuit_open_until = None

    async def _record_failure(self):
        """Record failed request and potentially open circuit."""
        self._failure_count += 1
        self._last_failure_time = datetime.utcnow()

        if self._failure_count >= 5:  # Threshold
            # Open circuit breaker
            self._circuit_state = "OPEN"
            self._circuit_open_until = datetime.utcnow() + timedelta(seconds=60)
            logger.warning(
                f"Circuit breaker OPEN. Failures: {self._failure_count}. "
                f"Retry after {self._circuit_open_until}"
            )

    async def get_current_price(self, stock_code: str) -> dict:
        """
        Fetch current price for stock.

        Args:
            stock_code: 6-digit stock code (e.g., "005930")

        Returns:
            {
                "stock_code": "005930",
                "current_price": 75000,
                "change_amount": 1000,
                "change_percent": 1.35,
                "volume": 12500000,
                "timestamp": "2025-11-09T10:30:15Z"
            }
        """
        await self._check_circuit_breaker()

        token = await self._ensure_valid_token()

        try:
            response = await self._http_client.get(
                "/uapi/domestic-stock/v1/quotations/inquire-price",
                params={
                    "FID_COND_MRKT_DIV_CODE": "J",  # KOSPI/KOSDAQ
                    "FID_INPUT_ISCD": stock_code
                },
                headers={
                    "Authorization": f"Bearer {token}",
                    "appkey": settings.KIS_APP_KEY,
                    "appsecret": settings.KIS_APP_SECRET,
                    "tr_id": "FHKST01010100"  # Transaction ID for current price
                }
            )
            response.raise_for_status()
            data = response.json()

            await self._record_success()

            # Parse response
            output = data["output"]
            return {
                "stock_code": stock_code,
                "current_price": int(output["stck_prpr"]),  # 주식 현재가
                "change_amount": int(output["prdy_vrss"]),  # 전일 대비
                "change_percent": float(output["prdy_ctrt"]),  # 전일 대비율
                "volume": int(output["acml_vol"]),  # 누적 거래량
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            await self._record_failure()
            logger.error(f"Failed to fetch price for {stock_code}: {e}")
            raise

    async def get_order_book(self, stock_code: str) -> dict:
        """
        Fetch 10-level order book (호가) for stock.

        Returns:
            {
                "stock_code": "005930",
                "asks": [
                    {"price": 75100, "volume": 5000, "total": 5000},
                    // ... 9 more levels
                ],
                "bids": [
                    {"price": 75000, "volume": 8000, "total": 8000},
                    // ... 9 more levels
                ],
                "spread": 100,
                "spread_pct": 0.13,
                "timestamp": "2025-11-09T10:30:15Z"
            }
        """
        await self._check_circuit_breaker()

        token = await self._ensure_valid_token()

        try:
            response = await self._http_client.get(
                "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn",
                params={
                    "FID_COND_MRKT_DIV_CODE": "J",
                    "FID_INPUT_ISCD": stock_code
                },
                headers={
                    "Authorization": f"Bearer {token}",
                    "appkey": settings.KIS_APP_KEY,
                    "appsecret": settings.KIS_APP_SECRET,
                    "tr_id": "FHKST01010200"  # Transaction ID for order book
                }
            )
            response.raise_for_status()
            data = response.json()

            await self._record_success()

            # Parse 10-level ask and bid data
            output = data["output"]

            asks = []
            bids = []
            for i in range(1, 11):  # 10 levels
                # Ask (매도 호가)
                ask_price = int(output[f"askp{i}"])
                ask_volume = int(output[f"askp_rsqn{i}"])
                asks.append({
                    "price": ask_price,
                    "volume": ask_volume,
                    "total": sum(a["volume"] for a in asks) + ask_volume
                })

                # Bid (매수 호가)
                bid_price = int(output[f"bidp{i}"])
                bid_volume = int(output[f"bidp_rsqn{i}"])
                bids.append({
                    "price": bid_price,
                    "volume": bid_volume,
                    "total": sum(b["volume"] for b in bids) + bid_volume
                })

            # Calculate spread
            best_ask = asks[0]["price"]
            best_bid = bids[0]["price"]
            spread = best_ask - best_bid
            spread_pct = (spread / best_bid) * 100 if best_bid > 0 else 0

            return {
                "stock_code": stock_code,
                "asks": asks,
                "bids": bids,
                "spread": spread,
                "spread_pct": round(spread_pct, 2),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            await self._record_failure()
            logger.error(f"Failed to fetch order book for {stock_code}: {e}")
            raise
```

#### 6.5.3 Data Source Factory Pattern

**Factory for Dependency Injection**:

```python
# data_pipeline/factories/data_source_factory.py
from abc import ABC, abstractmethod
from app.core.config import settings

class AbstractDataSource(ABC):
    """Abstract interface for data sources."""

    @abstractmethod
    async def get_current_price(self, stock_code: str) -> dict:
        pass

    @abstractmethod
    async def get_order_book(self, stock_code: str) -> dict:
        pass

    @abstractmethod
    async def get_historical_prices(
        self, stock_code: str, start_date: str, end_date: str
    ) -> list[dict]:
        pass


class KISDataSource(AbstractDataSource):
    """KIS API implementation."""

    def __init__(self):
        self.client = KISApiClient()

    async def get_current_price(self, stock_code: str) -> dict:
        async with self.client:
            return await self.client.get_current_price(stock_code)

    # ... other methods


class MockDataSource(AbstractDataSource):
    """Mock data source for development."""

    async def get_current_price(self, stock_code: str) -> dict:
        return {
            "stock_code": stock_code,
            "current_price": 75000 + randint(-1000, 1000),
            "change_amount": randint(-500, 500),
            "change_percent": uniform(-2.0, 2.0),
            "volume": randint(1000000, 50000000),
            "timestamp": datetime.utcnow().isoformat()
        }

    # ... other methods


class DataSourceFactory:
    """Factory to create appropriate data source."""

    @staticmethod
    def create() -> AbstractDataSource:
        if settings.ENABLE_KIS_API:
            return KISDataSource()
        else:
            return MockDataSource()


# Usage in services
data_source = DataSourceFactory.create()
price_data = await data_source.get_current_price("005930")
```

#### 6.5.4 Rate Limiting Implementation

**Token Bucket Algorithm**:

```python
# data_pipeline/rate_limiters/token_bucket.py
import asyncio
from datetime import datetime

class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for KIS API (20 req/sec).

    Allows bursts while maintaining average rate.
    """

    def __init__(self, rate: int = 20, capacity: int = 20):
        """
        Args:
            rate: Tokens added per second (requests/sec)
            capacity: Maximum tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = datetime.utcnow()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1):
        """
        Acquire tokens before making request.

        Blocks if not enough tokens available.
        """
        async with self._lock:
            while True:
                # Refill bucket based on time passed
                now = datetime.utcnow()
                elapsed = (now - self.last_update).total_seconds()
                self.tokens = min(
                    self.capacity,
                    self.tokens + elapsed * self.rate
                )
                self.last_update = now

                if self.tokens >= tokens:
                    # Enough tokens, consume and return
                    self.tokens -= tokens
                    return

                # Not enough tokens, wait for refill
                wait_time = (tokens - self.tokens) / self.rate
                await asyncio.sleep(wait_time)


# Global rate limiter instance
kis_rate_limiter = TokenBucketRateLimiter(rate=20, capacity=20)


# Usage in KIS API client
async def get_current_price(self, stock_code: str) -> dict:
    await kis_rate_limiter.acquire()  # Wait if rate limit exceeded
    # ... make API request
```

#### 6.5.5 Caching Strategy

**Redis Cache with TTL**:

```python
# services/price_service.py
from app.core.cache import cache
import json

class PriceService:
    """Service for fetching stock prices with caching."""

    def __init__(self, data_source: AbstractDataSource):
        self.data_source = data_source

    async def get_current_price(self, stock_code: str) -> dict:
        """
        Get current price with caching.

        TTL: 30 minutes for current prices.
        """
        cache_key = f"price:{stock_code}"

        # Check cache
        cached_data = await cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

        # Fetch from data source
        data = await self.data_source.get_current_price(stock_code)

        # Cache for 30 minutes
        await cache.set(
            cache_key,
            json.dumps(data),
            ttl=1800  # 30 minutes
        )

        return data

    async def get_order_book(self, stock_code: str) -> dict:
        """
        Get order book with caching.

        TTL: 10 seconds (more frequent updates needed).
        """
        cache_key = f"orderbook:{stock_code}"

        cached_data = await cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

        data = await self.data_source.get_order_book(stock_code)

        # Cache for 10 seconds
        await cache.set(cache_key, json.dumps(data), ttl=10)

        return data
```

**Expected Cache Hit Rates**:
- Current prices: 80%+ (30-minute TTL, updated hourly)
- Order book: 50-60% (10-second TTL, high update frequency)
- Stock info: 95%+ (24-hour TTL, rarely changes)

**Cache Invalidation**:
- Manual: Admin endpoint to clear specific stock cache
- Automatic: TTL expiration
- Event-driven: WebSocket updates trigger cache refresh

---

## 7. Security Design

### 7.1 Authentication & Authorization

#### 7.1.1 JWT Token Design

**Token Structure**:

```json
// Access Token (15 minutes)
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-uuid",
    "email": "user@example.com",
    "tier": "pro",
    "iat": 1699456789,
    "exp": 1699457689
  },
  "signature": "..."
}

// Refresh Token (30 days)
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-uuid",
    "type": "refresh",
    "iat": 1699456789,
    "exp": 1701048789
  },
  "signature": "..."
}
```

**Implementation**:

```python
# core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token."""
    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode = {
        "sub": user_id,
        "type": "refresh",
        "exp": expire
    }
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def decode_access_token(token: str) -> dict:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
```

#### 7.1.2 OAuth Integration

**Supported Providers**: Kakao, Naver, Google

```python
# services/oauth_service.py
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()

# Kakao
oauth.register(
    name='kakao',
    client_id=settings.KAKAO_CLIENT_ID,
    client_secret=settings.KAKAO_CLIENT_SECRET,
    access_token_url='https://kauth.kakao.com/oauth/token',
    authorize_url='https://kauth.kakao.com/oauth/authorize',
    api_base_url='https://kapi.kakao.com',
    client_kwargs={'scope': 'profile_nickname profile_image account_email'}
)

# Naver
oauth.register(
    name='naver',
    client_id=settings.NAVER_CLIENT_ID,
    client_secret=settings.NAVER_CLIENT_SECRET,
    access_token_url='https://nid.naver.com/oauth2.0/token',
    authorize_url='https://nid.naver.com/oauth2.0/authorize',
    api_base_url='https://openapi.naver.com',
    client_kwargs={'scope': 'profile'}
)

# Google
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url=(
        'https://accounts.google.com/.well-known/openid-configuration'
    ),
    client_kwargs={'scope': 'openid email profile'}
)
```

### 7.2 Data Security

#### 7.2.1 Data Encryption

**In Transit**:
- TLS 1.3 for all HTTPS connections
- Certificate management (Let's Encrypt)

**At Rest**:
- PostgreSQL column encryption for PII
- Environment variable encryption (Vault/AWS Secrets Manager)

```python
# core/encryption.py
from cryptography.fernet import Fernet
from app.core.config import settings

cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt_value(value: str) -> str:
    """Encrypt sensitive data."""
    return cipher_suite.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    """Decrypt sensitive data."""
    return cipher_suite.decrypt(encrypted_value.encode()).decode()
```

**Database Model with Encryption**:

```python
# db/models/user.py
from sqlalchemy import Column, String
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.encryption import encrypt_value, decrypt_value

class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    _phone_number = Column("phone_number", String)  # Encrypted

    @hybrid_property
    def phone_number(self):
        """Decrypt phone number."""
        if self._phone_number:
            return decrypt_value(self._phone_number)
        return None

    @phone_number.setter
    def phone_number(self, value: str):
        """Encrypt phone number."""
        if value:
            self._phone_number = encrypt_value(value)
        else:
            self._phone_number = None
```

### 7.3 Input Validation

#### 7.3.1 Pydantic Schemas

```python
# schemas/screening.py
from pydantic import BaseModel, validator, Field
from typing import Optional, Dict
from enum import Enum

class Market(str, Enum):
    KOSPI = "KOSPI"
    KOSDAQ = "KOSDAQ"
    ALL = "ALL"

class FilterRange(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None

    @validator('min', 'max')
    def check_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("Value must be non-negative")
        return v

class ScreeningRequest(BaseModel):
    market: Market = Market.ALL
    filters: Dict[str, FilterRange] = Field(default_factory=dict)
    sort_by: str = "market_cap"
    order: str = Field("desc", regex="^(asc|desc)$")
    page: int = Field(1, ge=1)
    per_page: int = Field(50, ge=1, le=100)

    @validator('filters')
    def validate_filters(cls, v):
        """Validate filter keys are allowed indicators."""
        allowed_filters = {
            'per', 'pbr', 'psr', 'roe', 'roa',
            'operating_margin', 'net_margin',
            'revenue_growth_yoy', 'profit_growth_yoy',
            'debt_to_equity', 'current_ratio',
            'dividend_yield', 'market_cap',
            'quality_score', 'value_score', 'growth_score'
        }

        invalid_keys = set(v.keys()) - allowed_filters
        if invalid_keys:
            raise ValueError(f"Invalid filters: {invalid_keys}")

        return v
```

### 7.4 SQL Injection Prevention

**Using SQLAlchemy ORM** (Parameterized Queries):

```python
# ✅ SAFE: Using ORM
stocks = db.query(Stock).filter(Stock.market == market).all()

# ✅ SAFE: Using parameterized raw SQL
stocks = db.execute(
    "SELECT * FROM stocks WHERE market = :market",
    {"market": market}
).fetchall()

# ❌ UNSAFE: String concatenation (NEVER DO THIS)
stocks = db.execute(
    f"SELECT * FROM stocks WHERE market = '{market}'"
).fetchall()
```

### 7.5 CORS Configuration

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://screener.kr",
        "https://www.screener.kr",
        "http://localhost:5173",  # Development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=3600,  # Cache preflight requests for 1 hour
)
```

### 7.6 Content Security Policy

```python
# middleware/security.py
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.screener.kr;"
    )

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    return response
```

---

## 8. Performance Design

### 8.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (p95) | < 200ms | APM (Sentry) |
| Screening Query (p99) | < 500ms | Database logs + APM |
| Page Load Time (p95) | < 1.5s | Lighthouse CI, RUM |
| Cache Hit Rate | > 80% | Redis INFO stats |
| Database Query Time | < 1s | pg_stat_statements |
| Concurrent Users | 10,000 | Load testing (k6) |

### 8.2 Caching Strategy

#### 8.2.1 Multi-Layer Cache

```
┌─────────────┐
│   Browser   │  Layer 1: Browser Cache (Service Worker)
│   Cache     │  - Static assets (JS, CSS, images)
│             │  - TTL: 1 hour
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    CDN      │  Layer 2: CDN Cache (CloudFlare/CloudFront)
│   Cache     │  - Static files
│             │  - TTL: 24 hours
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Redis     │  Layer 3: Application Cache
│   Cache     │  - API responses
│             │  - Stock data
│             │  - User sessions
│             │  - TTL: 5 minutes (hot data)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  PostgreSQL │  Layer 4: Database
│  (Source of │  - Shared buffers (25% of RAM)
│   Truth)    │  - Query result cache
└─────────────┘
```

#### 8.2.2 Cache Keys Design

```python
# Cache key patterns
CACHE_KEYS = {
    "stock_detail": "stock:{stock_code}",  # TTL: 5 min
    "stock_prices": "prices:{stock_code}:{from_date}:{to_date}",  # TTL: 30 min
    "screening_result": "screening:{hash(filters)}:{page}",  # TTL: 5 min
    "market_overview": "market:overview",  # TTL: 5 min
    "hot_stocks": "hot_stocks",  # TTL: 5 min
    "user_session": "session:{user_id}",  # TTL: 30 days
}

def get_screening_cache_key(filters: dict, page: int) -> str:
    """Generate cache key for screening query."""
    filters_str = json.dumps(filters, sort_keys=True)
    filters_hash = hashlib.md5(filters_str.encode()).hexdigest()
    return f"screening:{filters_hash}:{page}"
```

### 8.3 Database Optimization

#### 8.3.1 Connection Pooling

```python
# db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,           # Base pool size
    max_overflow=10,        # Allow 10 extra connections
    pool_pre_ping=True,     # Verify connections before use
    pool_recycle=3600,      # Recycle connections after 1 hour
    echo=settings.DEBUG     # Log SQL in debug mode
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

#### 8.3.2 Query Optimization

**Index Strategy**:

```sql
-- Covering index for screening queries
CREATE INDEX idx_screening_composite ON calculated_indicators (
    stock_code,
    calculation_date,
    per, pbr, roe, quality_score
) WHERE calculation_date = (
    SELECT MAX(calculation_date)
    FROM calculated_indicators ci2
    WHERE ci2.stock_code = calculated_indicators.stock_code
);

-- Partial index for active stocks
CREATE INDEX idx_stocks_active ON stocks (code)
WHERE delisting_date IS NULL;

-- Index for date range queries
CREATE INDEX idx_prices_date_range ON daily_prices (
    stock_code, trade_date DESC
);
```

**Query Patterns**:

```python
# ❌ SLOW: N+1 query problem
stocks = await db.query(Stock).all()
for stock in stocks:
    latest_price = await db.query(DailyPrice)\
        .filter(DailyPrice.stock_code == stock.code)\
        .order_by(DailyPrice.trade_date.desc())\
        .first()

# ✅ FAST: Use JOIN with subquery
from sqlalchemy.orm import selectinload

stocks = await db.query(Stock)\
    .options(
        selectinload(Stock.latest_price)
    )\
    .all()
```

### 8.4 Frontend Performance

#### 8.4.1 Code Splitting

```typescript
// router.tsx
import { lazy, Suspense } from 'react';

const HomePage = lazy(() => import('./pages/HomePage'));
const ScreenerPage = lazy(() => import('./pages/ScreenerPage'));
const StockDetailPage = lazy(() => import('./pages/StockDetailPage'));

const router = createBrowserRouter([
  {
    path: '/',
    element: <Suspense fallback={<Spinner />}><HomePage /></Suspense>
  },
  {
    path: '/screener',
    element: <Suspense fallback={<Spinner />}><ScreenerPage /></Suspense>
  },
  // ...
]);
```

#### 8.4.2 Virtual Scrolling

```typescript
// components/StockTable.tsx
import { useVirtualizer } from '@tanstack/react-virtual';

const StockTable: React.FC<{ stocks: Stock[] }> = ({ stocks }) => {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: stocks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,  // Row height in pixels
    overscan: 5,             // Render 5 extra rows above/below viewport
  });

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <StockRow
            key={virtualRow.key}
            stock={stocks[virtualRow.index]}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${virtualRow.start}px)`,
            }}
          />
        ))}
      </div>
    </div>
  );
};
```

#### 8.4.3 Debouncing & Throttling

```typescript
// hooks/useDebounce.ts
import { useEffect, useState } from 'react';

export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Usage: Debounce search input
const SearchBar: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  useEffect(() => {
    if (debouncedSearchTerm) {
      fetchSearchResults(debouncedSearchTerm);
    }
  }, [debouncedSearchTerm]);

  return (
    <input
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      placeholder="Search stocks..."
    />
  );
};
```

---

## 9. Deployment Architecture

### 9.1 Docker Compose (Development)

**Services**:

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app

  airflow_webserver:
    image: apache/airflow:2.8.0-python3.11
    ports:
      - "8080:8080"
    depends_on:
      - postgres

  airflow_scheduler:
    image: apache/airflow:2.8.0-python3.11
    depends_on:
      - airflow_webserver

volumes:
  postgres_data:
  redis_data:
  airflow_logs:
```

### 9.2 Kubernetes (Production)

#### 9.2.1 Architecture

```
┌───────────────────────────────────────────────────────┐
│                    Ingress Controller                  │
│                  (NGINX / Traefik)                     │
│              SSL Termination (Let's Encrypt)           │
└────────────────────┬──────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌────────────────┐        ┌────────────────┐
│   Frontend     │        │   Backend      │
│   Service      │        │   Service      │
│   (ClusterIP)  │        │   (ClusterIP)  │
└────────┬───────┘        └────────┬───────┘
         │                         │
    ┌────┴─────┐            ┌──────┴─────┬─────────┐
    ▼          ▼            ▼            ▼         ▼
┌────────┐ ┌────────┐  ┌────────┐  ┌────────┐ ┌────────┐
│Frontend│ │Frontend│  │Backend │  │Backend │ │Backend │
│  Pod   │ │  Pod   │  │  Pod   │  │  Pod   │ │  Pod   │
│ (NGINX)│ │ (NGINX)│  │(FastAPI│  │(FastAPI│ │(FastAPI│
└────────┘ └────────┘  └────────┘  └────────┘ └────────┘
                            │            │         │
                            └────────────┴─────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
            ┌────────────┐     ┌────────────┐    ┌────────────┐
            │ PostgreSQL │     │   Redis    │    │  Celery    │
            │StatefulSet │     │StatefulSet │    │ Deployment │
            └────────────┘     └────────────┘    └────────────┘
                    │                  │
                    ▼                  ▼
            ┌────────────┐     ┌────────────┐
            │Persistent  │     │Persistent  │
            │  Volume    │     │  Volume    │
            └────────────┘     └────────────┘
```

#### 9.2.2 Kubernetes Manifests

**Backend Deployment**:

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: screener
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: screener/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: screener
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

**Horizontal Pod Autoscaler**:

```yaml
# k8s/backend-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: screener
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Database StatefulSet**:

```yaml
# k8s/postgres-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: screener
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: timescale/timescaledb:latest-pg16
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: screener_db
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 100Gi
```

### 9.3 CI/CD Pipeline

#### 9.3.1 GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run linting
        run: |
          cd frontend
          npm run lint

      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage

      - name: Build
        run: |
          cd frontend
          npm run build

  deploy-production:
    needs: [test-backend, test-frontend]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build and push Docker images
        run: |
          docker build -t screener/backend:${{ github.sha }} ./backend
          docker build -t screener/frontend:${{ github.sha }} ./frontend
          docker push screener/backend:${{ github.sha }}
          docker push screener/frontend:${{ github.sha }}

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/backend backend=screener/backend:${{ github.sha }}
          kubectl set image deployment/frontend frontend=screener/frontend:${{ github.sha }}
          kubectl rollout status deployment/backend
          kubectl rollout status deployment/frontend
```

### 9.4 Monitoring & Observability

#### 9.4.1 Prometheus Metrics

```python
# core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Database metrics
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

# Cache metrics
cache_hits_total = Counter('cache_hits_total', 'Total cache hits')
cache_misses_total = Counter('cache_misses_total', 'Total cache misses')

# Custom business metrics
stock_screening_requests = Counter(
    'stock_screening_requests_total',
    'Total stock screening requests'
)

portfolio_creations = Counter(
    'portfolio_creations_total',
    'Total portfolio creations'
)
```

#### 9.4.2 Grafana Dashboards

**API Performance Dashboard**:

```json
{
  "dashboard": {
    "title": "API Performance",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Request Duration (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      }
    ]
  }
}
```

---

## 10. Technology Stack

### 10.1 Frontend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | React | 18.x | UI library |
| **Language** | TypeScript | 5.x | Type-safe JavaScript |
| **Build Tool** | Vite | 5.x | Fast build and HMR |
| **State Management** | Zustand | 4.x | Lightweight state management |
| **Data Fetching** | TanStack Query | 5.x | Server state management, caching |
| **Routing** | React Router | 6.x | Client-side routing |
| **UI Components** | Radix UI | 1.x | Accessible primitives |
| **Styling** | Tailwind CSS | 3.x | Utility-first CSS |
| **Charts** | TradingView Lightweight Charts | 4.x | Financial charts |
| **Charts** | Recharts | 2.x | Data visualization |
| **Forms** | React Hook Form | 7.x | Form validation |
| **HTTP Client** | Axios | 1.x | API requests |

### 10.2 Backend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | FastAPI | 0.104.x | Async web framework |
| **Language** | Python | 3.11+ | Programming language |
| **ASGI Server** | Uvicorn | 0.24.x | Production server |
| **ORM** | SQLAlchemy | 2.0.x | Database ORM |
| **Async DB Driver** | asyncpg | 0.29.x | PostgreSQL async driver |
| **Migrations** | Alembic | 1.12.x | Database migrations |
| **Validation** | Pydantic | 2.x | Data validation |
| **Authentication** | python-jose | 3.3.x | JWT tokens |
| **Password Hashing** | passlib | 1.7.x | bcrypt hashing |
| **Task Queue** | Celery | 5.3.x | Background tasks |
| **Caching** | Redis | 7.x | In-memory cache |

### 10.3 Database

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **RDBMS** | PostgreSQL | 16.x | Primary database |
| **Time-Series** | TimescaleDB | 2.14.x | Time-series extension |
| **Extensions** | pg_trgm | - | Fuzzy text search |
| **Extensions** | uuid-ossp | - | UUID generation |

### 10.4 Data Pipeline

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Orchestration** | Apache Airflow | 2.8.x | Workflow scheduling |
| **Data Processing** | Pandas | 2.x | Data manipulation |
| **Numerical Computing** | NumPy | 1.x | Array operations |

### 10.5 Infrastructure

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Containerization** | Docker | 24.x | Application packaging |
| **Container Orchestration** | Kubernetes | 1.29.x | Production orchestration |
| **Reverse Proxy** | NGINX | 1.25.x | Load balancing, SSL |
| **Monitoring** | Prometheus | 2.x | Metrics collection |
| **Visualization** | Grafana | 10.x | Dashboards |
| **Logging** | ELK Stack | 8.x | Log aggregation |
| **CI/CD** | GitHub Actions | - | Automated deployments |

---

## 11. Documentation Architecture

This section describes the technical architecture of the unified documentation system that consolidates all project documentation (API references, user guides, architecture docs, specifications) into a single, searchable platform.

### 11.1 Documentation Platform Overview

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Documentation Platform                   │
│                      (docs.screener.kr)                      │
└────────────────┬────────────────────────────────────────────┘
                 │
     ┌───────────┴────────────┬──────────────┬──────────────┐
     │                        │              │              │
     ▼                        ▼              ▼              ▼
┌──────────┐          ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Docusaurus│          │  Sphinx  │   │ TypeDoc  │   │ FastAPI  │
│  (Main    │          │ (Python  │   │(TypeScript│   │ OpenAPI  │
│ Platform) │          │  Docs)   │   │  Docs)   │   │   Docs   │
└─────┬─────┘          └─────┬────┘   └────┬─────┘   └────┬─────┘
      │                      │              │              │
      │  ┌───────────────────┴──────────────┴──────────────┘
      │  │
      ▼  ▼
┌────────────────────────────────────────────────────────────┐
│              Source Documentation Files                     │
├────────────────────────────────────────────────────────────┤
│ • Markdown Files (guides, architecture)                    │
│ • Python Docstrings (backend code)                         │
│ • TSDoc Comments (frontend code)                           │
│ • OpenAPI Spec (REST API)                                  │
└────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│                  Build Process (CI/CD)                      │
├────────────────────────────────────────────────────────────┤
│ 1. Build Sphinx Python docs                                │
│ 2. Build TypeDoc TypeScript docs                           │
│ 3. Build Docusaurus site (integrate Sphinx + TypeDoc)      │
│ 4. Check links, run Lighthouse audit                       │
│ 5. Deploy to CDN                                            │
└────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│                  Hosting & Delivery                         │
├────────────────────────────────────────────────────────────┤
│ • CDN: Global edge distribution                            │
│ • SSL: Auto-managed HTTPS                                  │
│ • Search: Algolia DocSearch                                │
│ • Analytics: Plausible/Google Analytics                    │
└────────────────────────────────────────────────────────────┘
```

### 12.2 Component Architecture

#### 12.2.1 Docusaurus (Main Platform)

**Technology**: Docusaurus 3.x (React-based static site generator)

**Responsibilities**:
- Serve as the main documentation platform
- Aggregate content from multiple sources (Markdown, Sphinx, TypeDoc)
- Provide navigation, search, and versioning
- Generate static HTML for deployment

**Configuration** (`docusaurus.config.js`):
```javascript
module.exports = {
  title: 'Screener Platform Documentation',
  tagline: 'Comprehensive docs for developers and users',
  url: 'https://docs.screener.kr',
  baseUrl: '/',

  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/kcenon/screener_system/edit/main/docs/',
        },
        blog: {
          showReadingTime: true,
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'api',
        path: 'api',
        routeBasePath: 'api',
        sidebarPath: require.resolve('./sidebarsApi.js'),
      },
    ],
    [
      'docusaurus-plugin-typedoc',
      {
        entryPoints: ['../frontend/src'],
        tsconfig: '../frontend/tsconfig.json',
        out: 'api/frontend',
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Screener Docs',
      items: [
        { to: 'docs/getting-started', label: 'Docs', position: 'left' },
        { to: 'api/backend', label: 'API Reference', position: 'left' },
        { href: 'https://github.com/kcenon/screener_system', label: 'GitHub', position: 'right' },
      ],
    },
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_API_KEY',
      indexName: 'screener_docs',
    },
  },
};
```

**Directory Structure**:
```
docs-site/
├── docs/                      # Main documentation
│   ├── 01-getting-started/
│   ├── 02-guides/
│   ├── 03-api-reference/
│   ├── 04-architecture/
│   ├── 05-specifications/
│   └── 06-operations/
├── api/                       # Auto-generated API docs
│   ├── backend/               # From Sphinx
│   └── frontend/              # From TypeDoc
├── blog/                      # Release notes, updates
├── src/                       # Custom React components
├── static/                    # Static assets (images, diagrams)
├── docusaurus.config.js
├── sidebars.js
└── package.json
```

#### 12.2.2 Sphinx (Python Documentation)

**Technology**: Sphinx 7.x with autodoc extension

**Responsibilities**:
- Auto-generate Python API documentation from docstrings
- Support Google-style docstrings
- Generate cross-references and type hints
- Export to HTML for integration with Docusaurus

**Configuration** (`conf.py`):
```python
import os
import sys
sys.path.insert(0, os.path.abspath('../../backend'))

project = 'Screener Backend API'
author = 'Engineering Team'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
]

# Napoleon settings (Google style)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'member-order': 'bysource',
}

# HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
```

**Output**: HTML documentation in `api/backend/`

#### 12.2.3 TypeDoc (TypeScript Documentation)

**Technology**: TypeDoc 0.25.x

**Responsibilities**:
- Auto-generate TypeScript/React component documentation
- Extract TSDoc comments from source code
- Generate props tables for React components
- Export to Markdown for Docusaurus integration

**Configuration** (`typedoc.json`):
```json
{
  "entryPoints": ["../frontend/src"],
  "out": "api/frontend",
  "plugin": ["typedoc-plugin-markdown"],
  "excludePrivate": true,
  "excludeProtected": true,
  "categorizeByGroup": true,
  "categoryOrder": [
    "Components",
    "Hooks",
    "Services",
    "Store",
    "Types",
    "*"
  ],
  "readme": "none",
  "githubPages": false
}
```

**Output**: Markdown files in `api/frontend/`

#### 12.2.4 FastAPI OpenAPI Documentation

**Technology**: FastAPI's built-in Swagger UI and ReDoc

**Responsibilities**:
- Auto-generate REST API documentation from route definitions
- Provide interactive API playground
- Export OpenAPI 3.0 specification

**Access**:
- Swagger UI: `https://api.screener.kr/docs`
- ReDoc: `https://api.screener.kr/redoc`
- OpenAPI JSON: `https://api.screener.kr/openapi.json`

**Integration with Docusaurus**:
- Link to live API docs from main documentation
- Embed OpenAPI spec for offline viewing (optional)

### 12.3 Build & Deployment Pipeline

#### 12.3.1 GitHub Actions Workflow

**File**: `.github/workflows/docs.yml`

```yaml
name: Deploy Documentation to GitHub Pages

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'frontend/src/**'
      - 'backend/app/**'
      - 'docs-site/**'

jobs:
  deploy:
    runs-on: ubuntu-latest

    permissions:
      contents: write  # Required for gh-pages deployment

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: 'docs-site/package-lock.json'

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Python dependencies
        run: |
          pip install -r requirements-docs.txt

      - name: Build Sphinx docs
        run: |
          cd docs/api/python
          sphinx-build -b html . ../../_build/api/backend

      - name: Build TypeDoc documentation
        run: |
          cd docs-site
          npm ci
          npx typedoc

      - name: Build Docusaurus site
        run: |
          cd docs-site
          npm run build
        env:
          NODE_ENV: production

      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs-site/build
          cname: docs.screener.kr
          user_name: 'github-actions[bot]'
          user_email: 'github-actions[bot]@users.noreply.github.com'
          commit_message: 'docs: deploy documentation [skip ci]'
```

#### 12.3.2 Build Performance

**Target**: < 3 minutes total build time

**Optimizations**:
- Parallel builds (Sphinx, TypeDoc, Docusaurus)
- Incremental builds (only rebuild changed files)
- Caching dependencies (npm cache, pip cache)

### 12.4 Search Architecture

#### Algolia DocSearch Integration

**Implementation**:
```javascript
// docusaurus.config.js
themeConfig: {
  algolia: {
    appId: 'SCREENER_DOCS',
    apiKey: 'search-only-api-key',
    indexName: 'screener_platform',
    contextualSearch: true,
    searchPagePath: 'search',
  },
}
```

**Indexing Strategy**:
- Automatic re-indexing on every deployment
- Index all documentation content (headings, paragraphs, code)
- Custom ranking: Getting Started > API Reference > Architecture

**Search Quality Metrics**:
- Average click position: < 3
- % queries with clicks: > 90%
- % queries with no results: < 5%

### 12.5 Versioning Strategy

**Approach**: Maintain documentation for current version + 2 previous major versions

**Implementation**:
```bash
# Create new version
npm run docusaurus docs:version 1.0

# Directory structure
docs-site/
├── docs/              # Current (unreleased) docs
├── versioned_docs/
│   ├── version-1.0/
│   └── version-0.9/
└── versions.json      # ["1.0", "0.9"]
```

**Version Selector**: Dropdown in navbar to switch between versions

### 12.6 Analytics & Monitoring

#### Page Analytics

**Tool**: Plausible Analytics (privacy-friendly)

**Metrics Tracked**:
- Page views
- Most visited pages
- Search queries
- Time on page
- Bounce rate

**Goals**:
- Track documentation usage patterns
- Identify missing or unclear content
- Prioritize documentation improvements

#### Documentation Health Dashboard

**Metrics**:
- Documentation coverage (% APIs documented)
- Broken link count
- Build success rate
- Average build time
- Search quality metrics

**Tools**:
- Custom dashboard (Grafana + Prometheus)
- Weekly reports via email

### 12.7 Security Considerations

**Content Security Policy**:
```javascript
// docusaurus.config.js
scripts: [
  {
    src: 'https://plausible.io/js/script.js',
    defer: true,
    'data-domain': 'docs.screener.kr',
  },
],
```

**Access Control**:
- Documentation site is public (no authentication required)
- Admin features (analytics, search config) require authentication
- Source code access via GitHub (public repository)

**HTTPS Enforcement**:
- All traffic redirected to HTTPS
- SSL certificate auto-managed by hosting platform
- HSTS header enabled

---

## 12. Design Decisions

### 12.1 Key Architectural Decisions

#### 12.1.1 Monolith vs Microservices

**Decision**: Start with **Modular Monolith**, design for future microservices split.

**Rationale**:
- **Pros**:
  - Simpler deployment and operations
  - Faster development velocity (no inter-service communication overhead)
  - Easier debugging and testing
  - Lower infrastructure costs
- **Cons**:
  - Scaling limitations (must scale entire application)
  - Tighter coupling

**Future Migration Path**:
- Module boundaries are clear (stock, user, portfolio, alert)
- Each module has independent database tables
- API versioning allows gradual service extraction

#### 12.1.2 PostgreSQL + TimescaleDB vs Specialized Time-Series DB

**Decision**: Use **TimescaleDB** (PostgreSQL extension).

**Rationale**:
- **Pros**:
  - Single database for relational + time-series data
  - Full SQL support (no learning new query language)
  - ACID compliance for all data
  - Excellent compression (10x for time-series data)
- **Cons**:
  - Not as optimized as pure time-series databases (InfluxDB, Prometheus)

**Why not InfluxDB/Prometheus**:
- Need relational data (users, portfolios)
- TimescaleDB compression is sufficient for our scale
- Simpler operations (one database)

#### 12.1.3 Server-Side Rendering (SSR) vs Client-Side Rendering (CSR)

**Decision**: Use **Client-Side Rendering** (React SPA).

**Rationale**:
- **Pros**:
  - Better user experience (instant navigation)
  - API-first architecture (enables mobile app later)
  - Lower server load
- **Cons**:
  - SEO challenges (mitigated with static landing pages)
  - Slower initial page load

**Why not Next.js (SSR)**:
- Application is behind authentication (SEO not critical)
- API-first approach is priority
- Simpler deployment

#### 12.1.4 JWT vs Session-Based Authentication

**Decision**: Use **JWT tokens** (stateless).

**Rationale**:
- **Pros**:
  - Stateless (no server-side session storage)
  - Scalable (no session affinity needed)
  - Works across multiple servers
  - Mobile-friendly
- **Cons**:
  - Cannot revoke access tokens before expiry (mitigated with short expiry)
  - Larger request size (token in header)

**Implementation**:
- Short-lived access tokens (15 minutes)
- Long-lived refresh tokens (30 days, revocable)

#### 12.1.5 Materialized Views vs Real-Time Aggregation

**Decision**: Use **Materialized Views** for screening.

**Rationale**:
- Screening queries are complex (join stocks, prices, indicators)
- Real-time aggregation would be too slow
- Data updates once per day (materialized views are perfect fit)

**Refresh Strategy**:
- Refresh after indicator calculation DAG completes
- CONCURRENTLY to avoid locking

### 12.2 Database Design Decisions

#### 12.2.1 Integer Prices vs Decimal/Float

**Decision**: Store prices as **INTEGER** (KRW, no decimals).

**Rationale**:
- Korean stocks trade in whole KRW amounts (no cents)
- Avoids floating-point precision issues
- Faster arithmetic and comparisons
- Smaller storage size

#### 12.2.2 Composite Primary Key vs Surrogate Key

**Decision**: Use **Composite PRIMARY KEY** for daily_prices.

```sql
PRIMARY KEY (stock_code, trade_date)
```

**Rationale**:
- Natural key is available (stock_code + date)
- No need for surrogate UUID/SERIAL
- Clearer semantics
- Smaller index size

#### 12.2.3 NULL Handling for Optional Indicators

**Decision**: Allow **NULL** values for indicators that cannot be calculated.

**Example**: `per` is NULL if company has negative earnings.

**Rationale**:
- NULL has semantic meaning ("not applicable" vs "zero")
- Avoids magic values (-1, 0, etc.)
- Database can optimize NULL handling

**Query Implications**:
```sql
-- Filter by PER, excluding NULL values
WHERE per BETWEEN 0 AND 15
  AND per IS NOT NULL  -- Explicit NULL handling
```

### 12.3 API Design Decisions

#### 12.3.1 REST vs GraphQL

**Decision**: Use **REST API**.

**Rationale**:
- Simpler to implement and understand
- Better caching (HTTP caching standards)
- OpenAPI documentation tools
- Sufficient for our use case

**Why not GraphQL**:
- No complex nested queries needed
- Over-fetching not a major issue
- Adds complexity

#### 12.3.2 Versioning Strategy

**Decision**: **URL Path Versioning** (`/v1/`, `/v2/`).

**Alternatives Considered**:
- Header versioning (`Accept: application/vnd.api.v1+json`)
- Query parameter (`?version=1`)

**Rationale**:
- Most visible and intuitive
- Easy to test (just change URL)
- Industry standard (Stripe, GitHub)

---

## 13. Appendices

### 12.1 Glossary

| Term | Definition |
|------|------------|
| **OHLCV** | Open, High, Low, Close, Volume - standard format for price data |
| **PER** | Price-to-Earnings Ratio - valuation metric |
| **PBR** | Price-to-Book Ratio - valuation metric |
| **ROE** | Return on Equity - profitability metric |
| **Hypertable** | TimescaleDB's abstraction for time-series tables |
| **Materialized View** | Pre-computed query results stored as a table |
| **Continuous Aggregate** | TimescaleDB feature for real-time aggregated views |
| **DAG** | Directed Acyclic Graph - Airflow workflow definition |

### 12.2 Acronyms

| Acronym | Full Form |
|---------|-----------|
| **API** | Application Programming Interface |
| **JWT** | JSON Web Token |
| **CORS** | Cross-Origin Resource Sharing |
| **CSRF** | Cross-Site Request Forgery |
| **XSS** | Cross-Site Scripting |
| **SPA** | Single Page Application |
| **ORM** | Object-Relational Mapping |
| **ACID** | Atomicity, Consistency, Isolation, Durability |
| **TTL** | Time To Live |
| **HPA** | Horizontal Pod Autoscaler |
| **APM** | Application Performance Monitoring |
| **RUM** | Real User Monitoring |

### 12.3 External Dependencies

**Production Dependencies**:

```python
# backend/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.12.1
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis[hiredis]==5.0.1
celery[redis]==5.3.4
pandas==2.1.3
numpy==1.26.2
```

```json
// frontend/package.json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@tanstack/react-query": "^5.12.0",
    "zustand": "^4.4.7",
    "axios": "^1.6.2",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "tailwindcss": "^3.3.6",
    "lightweight-charts": "^4.1.1",
    "recharts": "^2.10.3",
    "react-hook-form": "^7.48.2",
    "date-fns": "^2.30.0"
  }
}
```

### 12.4 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/16/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [React Documentation](https://react.dev/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

### 12.5 Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-09 | Architecture Team | Initial SDS document |

---

**END OF DOCUMENT**
