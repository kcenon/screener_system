---
id: sds-performance-design
title: SDS - Performance Design
description: Software design specification - performance design
sidebar_label: Performance Design
sidebar_position: 8
tags:
  - specification
  - design
  - architecture
---

:::info Navigation
- [Introduction](introduction.md)
- [System Architecture](system-architecture.md)
- [Component Design](component-design.md)
- [Database Design](database-design.md)
- [API Design](api-design.md)
- [Data Pipeline](data-pipeline.md)
- [Security Design](security-design.md)
- [Performance Design](performance-design.md) (Current)
- [Deployment](deployment.md)
- [Tech Stack & Decisions](tech-stack-decisions.md)
:::

# Software Design Specification - Performance Design

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