---
id: sds-component-design
title: SDS - Component Design
description: Software design specification - component design
sidebar_label: Component Design
sidebar_position: 3
tags:
  - specification
  - design
  - architecture
---

:::info Navigation
- [Introduction](introduction.md)
- [System Architecture](system-architecture.md)
- [Component Design](component-design.md) (Current)
- [Database Design](database-design.md)
- [API Design](api-design.md)
- [Data Pipeline](data-pipeline.md)
- [Security Design](security-design.md)
- [Performance Design](performance-design.md)
- [Deployment](deployment.md)
- [Tech Stack & Decisions](tech-stack-decisions.md)
:::

# Software Design Specification - Component Design

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