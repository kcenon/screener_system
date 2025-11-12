---
id: prd-technical
title: PRD - Technical
description: Technical and data requirements
sidebar_label: Technical
sidebar_position: 3
tags:
  - specification
  - product
  - requirements
---

:::info Navigation
- [Overview](overview.md)
- [Users & Features](users-features.md)
- [Technical](technical.md) (Current)
- [Implementation](implementation.md)
:::

# Product Requirements Document - Technical

## 6. Technical Requirements

### 6.1 Technology Stack

#### Frontend

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Framework** | React | 18+ | Industry standard, component reusability, large ecosystem |
| **Build Tool** | Vite | 5+ | Fast HMR, optimized builds, better DX than Webpack |
| **State Management** | Zustand | 4+ | Lightweight, simpler than Redux, sufficient for our needs |
| **Routing** | React Router | 6+ | De facto standard for React SPAs |
| **Data Fetching** | TanStack Query (React Query) | 5+ | Caching, automatic refetch, optimistic updates |
| **Charts** | TradingView Lightweight Charts + Recharts | Latest | Financial charts (TV) + general charts (Recharts) |
| **UI Components** | Radix UI + Tailwind CSS | Latest | Accessible primitives + utility-first CSS |
| **Forms** | React Hook Form | 7+ | Performance, DX, built-in validation |
| **Validation** | Zod | 3+ | TypeScript-first schema validation |
| **HTTP Client** | Axios | 1+ | Interceptors, better error handling than fetch |
| **Date Handling** | date-fns | 3+ | Smaller than moment.js, tree-shakeable |
| **Notifications** | React Hot Toast | 2+ | Lightweight, customizable |
| **Testing** | Vitest + Testing Library | Latest | Fast, Jest-compatible, React Testing Library |

#### Backend

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Framework** | FastAPI (Python) | 0.110+ | High performance, auto OpenAPI docs, async support |
| **ASGI Server** | Uvicorn | 0.27+ | Fast ASGI server for FastAPI |
| **ORM** | SQLAlchemy | 2+ | Mature, supports async, complex queries |
| **Migration** | Alembic | 1.13+ | Database migration tool for SQLAlchemy |
| **Validation** | Pydantic | 2+ | Data validation, serialization (built into FastAPI) |
| **Authentication** | FastAPI-Users + PyJWT | Latest | Flexible auth system, JWT tokens |
| **Task Queue** | Celery | 5+ | Distributed task processing for indicator calculations |
| **Message Broker** | Redis | 7+ | Celery broker, also used for caching |
| **API Documentation** | Swagger UI (auto via FastAPI) | Auto | Interactive API docs |
| **Testing** | Pytest | 8+ | Industry standard for Python testing |
| **Linting** | Ruff | Latest | Fast Python linter (replaces flake8, isort, etc.) |
| **Type Checking** | MyPy | 1.8+ | Static type checking for Python |

#### Database

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Primary DB** | PostgreSQL | 16+ | ACID compliant, JSON support, mature |
| **Time Series** | TimescaleDB (Postgres extension) | 2.14+ | Optimized for time-series data (stock prices) |
| **Cache** | Redis | 7+ | In-memory cache, pub/sub, session storage |
| **Search** | PostgreSQL Full-Text Search | Built-in | Sufficient for stock name/code search, avoid Elasticsearch overhead |

#### Infrastructure

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Container** | Docker | 24+ | Consistent environments, easy deployment |
| **Orchestration** | Kubernetes | 1.29+ | Auto-scaling, self-healing, industry standard |
| **Cloud Provider** | AWS / GCP / Naver Cloud | N/A | TBD based on cost/compliance requirements |
| **CDN** | CloudFlare | N/A | Fast static asset delivery, DDoS protection |
| **CI/CD** | GitHub Actions | N/A | Integrated with repo, free for public repos |
| **Monitoring** | Grafana + Prometheus | Latest | Metrics visualization + time-series DB |
| **Logging** | ELK Stack (Elasticsearch, Logstash, Kibana) | 8+ | Centralized logging, search, visualization |
| **APM** | Sentry | Cloud | Error tracking, performance monitoring |
| **Uptime Monitoring** | UptimeRobot / Pingdom | Cloud | Availability monitoring |

#### Data Pipeline

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Orchestration** | Apache Airflow | 2.8+ | Workflow scheduling, monitoring, retries |
| **Data Processing** | Pandas + NumPy | Latest | Financial calculations, data transformation |
| **API Clients** | Requests + Custom wrappers | Latest | Fetch data from KRX, F&Guide APIs |

---

### 6.2 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Users                                  │
│                     (Web Browser / Mobile)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       CloudFlare CDN                             │
│              (Static Assets, DDoS Protection)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Load Balancer                               │
│                    (NGINX / AWS ALB)                             │
└────────┬────────────────────────────────────────────────────────┘
         │
         ├─────────────┬──────────────┬──────────────┐
         ▼             ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Frontend    │ │ Frontend    │ │ Frontend    │ │ Frontend    │
│ Server 1    │ │ Server 2    │ │ Server 3    │ │ Server N    │
│ (Nginx)     │ │ (Nginx)     │ │ (Nginx)     │ │ (Nginx)     │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
         │             │              │              │
         └─────────────┴──────────────┴──────────────┘
                         │ REST API / GraphQL
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API Gateway                                │
│        (Rate Limiting, Auth Check, Request Routing)             │
└────────┬────────────────────────────────────────────────────────┘
         │
         ├─────────────┬──────────────┬──────────────┐
         ▼             ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ API Server  │ │ API Server  │ │ API Server  │ │ API Server  │
│ 1 (FastAPI) │ │ 2 (FastAPI) │ │ 3 (FastAPI) │ │ N (FastAPI) │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │               │
       └───────────────┴───────────────┴───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Analytics       │ │ Notification    │ │ Auth Service    │
│ Engine          │ │ Service         │ │                 │
│ (Indicator Calc)│ │ (Alerts)        │ │ (JWT Tokens)    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Celery Workers                              │
│              (Async Indicator Calculations)                      │
└─────────────────────────────────────────────────────────────────┘
         │
         └──────────────┬────────────────────────────────┐
                        │                                │
                        ▼                                ▼
┌───────────────────────────────────────┐ ┌─────────────────────────┐
│          Redis Cluster                │ │   PostgreSQL Cluster    │
│  ┌──────────┐  ┌──────────┐          │ │  ┌──────────────────┐   │
│  │ Cache    │  │ Session  │          │ │  │ Primary (RW)     │   │
│  │          │  │ Store    │          │ │  │ + TimescaleDB    │   │
│  └──────────┘  └──────────┘          │ │  └────────┬─────────┘   │
│  ┌──────────┐  ┌──────────┐          │ │           │             │
│  │ Celery   │  │ Pub/Sub  │          │ │           ▼             │
│  │ Broker   │  │          │          │ │  ┌──────────────────┐   │
│  └──────────┘  └──────────┘          │ │  │ Replica 1 (RO)   │   │
└───────────────────────────────────────┘ │  └──────────────────┘   │
                                          │  ┌──────────────────┐   │
                                          │  │ Replica 2 (RO)   │   │
                                          │  └──────────────────┘   │
                                          └─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Pipeline Layer                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │               Apache Airflow Scheduler                   │    │
│  └────────┬────────────────────────────────────────────────┘    │
│           │                                                      │
│  ┌────────▼────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │ KRX Data        │  │ F&Guide API │  │ News Scraper    │    │
│  │ Collector       │  │ Collector   │  │ (Themes)        │    │
│  │ (Daily Prices)  │  │ (Financials)│  │                 │    │
│  └─────────────────┘  └─────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐     │
│  │ KRX API     │  │ F&Guide API │  │ Payment Gateway     │     │
│  │ (Official   │  │ (Financial  │  │ (Stripe / Toss)     │     │
│  │  Prices)    │  │  Data)      │  │                     │     │
│  └─────────────┘  └─────────────┘  └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

### 6.3 API Design

#### RESTful Endpoints

**Base URL**: `https://api.screener.kr/v1`

**Authentication**:
- Public endpoints: No auth required
- Private endpoints: `Authorization: Bearer <JWT_TOKEN>`

#### Stock Endpoints

```
GET    /stocks
       Query params: market, min_per, max_per, min_market_cap, sort_by, page, limit
       Response: { stocks: [...], total: 1234, page: 1, pages: 25 }

GET    /stocks/{stock_code}
       Response: { code, name, market, sector, current_price, ... }

GET    /stocks/{stock_code}/financials
       Query params: period (quarterly/annual), years
       Response: { income_statement: [...], balance_sheet: [...], cash_flow: [...] }

GET    /stocks/{stock_code}/prices
       Query params: from_date, to_date, interval (daily/weekly/monthly)
       Response: { prices: [{ date, open, high, low, close, volume }, ...] }

GET    /stocks/{stock_code}/indicators
       Response: { valuation: {...}, growth: {...}, profitability: {...}, ... }
```

#### Screening Endpoints

```
POST   /screen
       Body: { filters: { per: { max: 15 }, roe: { min: 10 } }, sort: "market_cap", order: "desc" }
       Response: { stocks: [...], count: 50, query_time_ms: 234 }

GET    /screen/templates
       Response: { templates: [{ id, name, description, filters }, ...] }

GET    /screen/templates/{template_id}
       Response: { id, name, filters, ... }
```

#### Market Endpoints

```
GET    /market/overview
       Response: { kospi_index, kosdaq_index, volume, ... }

GET    /market/hot-stocks
       Response: { hot_stocks: [{ code, name, volume_surge_pct, price_change_pct }, ...] }

GET    /market/movers
       Query params: type (gainers/losers), limit
       Response: { movers: [...] }

GET    /market/sectors
       Response: { sectors: [{ name, price_change_pct, volume }, ...] }
```

#### User Endpoints

```
POST   /auth/register
       Body: { email, password }
       Response: { user_id, email, token }

POST   /auth/login
       Body: { email, password }
       Response: { user_id, token, refresh_token }

POST   /auth/refresh
       Body: { refresh_token }
       Response: { token }

GET    /users/me
       Auth: Required
       Response: { id, email, subscription_tier, created_at }

PATCH  /users/me
       Auth: Required
       Body: { name, email, password }
       Response: { updated_user }
```

#### Portfolio Endpoints

```
GET    /portfolios
       Auth: Required
       Response: { portfolios: [...] }

POST   /portfolios
       Auth: Required
       Body: { name }
       Response: { id, name, created_at }

GET    /portfolios/{portfolio_id}
       Auth: Required
       Response: { id, name, holdings: [...], total_value, total_gain, ... }

POST   /portfolios/{portfolio_id}/holdings
       Auth: Required
       Body: { stock_code, quantity, avg_price, purchase_date }
       Response: { holding_id, ... }

DELETE /portfolios/{portfolio_id}/holdings/{holding_id}
       Auth: Required
       Response: { success: true }
```

#### Alert Endpoints

```
GET    /alerts
       Auth: Required
       Response: { alerts: [...] }

POST   /alerts
       Auth: Required
       Body: { stock_code, type: "price", condition: "above", value: 80000, notify_via: ["email", "push"] }
       Response: { alert_id, ... }

DELETE /alerts/{alert_id}
       Auth: Required
       Response: { success: true }
```

---

### 6.4 Database Schema

#### Core Tables

**stocks**
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

CREATE INDEX idx_stocks_market ON stocks(market);
CREATE INDEX idx_stocks_sector ON stocks(sector);
CREATE INDEX idx_stocks_name_trgm ON stocks USING gin (name gin_trgm_ops); -- For fuzzy search
```

**daily_prices** (TimescaleDB hypertable)
```sql
CREATE TABLE daily_prices (
    stock_code VARCHAR(6) NOT NULL REFERENCES stocks(code),
    trade_date DATE NOT NULL,
    open_price INTEGER,
    high_price INTEGER,
    low_price INTEGER,
    close_price INTEGER,
    adjusted_close INTEGER, -- For splits/dividends
    volume BIGINT,
    trading_value BIGINT,
    market_cap BIGINT,
    PRIMARY KEY (stock_code, trade_date)
);

-- Convert to TimescaleDB hypertable for efficient time-series queries
SELECT create_hypertable('daily_prices', 'trade_date');

-- Create continuous aggregate for faster queries
CREATE MATERIALIZED VIEW daily_prices_monthly
WITH (timescaledb.continuous) AS
SELECT
    stock_code,
    time_bucket('1 month', trade_date) AS month,
    first(open_price, trade_date) AS open,
    max(high_price) AS high,
    min(low_price) AS low,
    last(close_price, trade_date) AS close,
    sum(volume) AS total_volume
FROM daily_prices
GROUP BY stock_code, month;
```

**financial_statements**
```sql
CREATE TABLE financial_statements (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(6) NOT NULL REFERENCES stocks(code),
    period_type VARCHAR(10) NOT NULL CHECK (period_type IN ('quarterly', 'annual')),
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER CHECK (fiscal_quarter BETWEEN 1 AND 4),
    report_date DATE NOT NULL,

    -- Income Statement
    revenue BIGINT,
    cost_of_revenue BIGINT,
    gross_profit BIGINT,
    operating_expenses BIGINT,
    operating_profit BIGINT,
    non_operating_income BIGINT,
    non_operating_expenses BIGINT,
    ebt BIGINT, -- Earnings Before Tax
    tax_expense BIGINT,
    net_profit BIGINT,

    -- Balance Sheet
    current_assets BIGINT,
    non_current_assets BIGINT,
    total_assets BIGINT,
    current_liabilities BIGINT,
    non_current_liabilities BIGINT,
    total_liabilities BIGINT,
    equity BIGINT,

    -- Cash Flow Statement
    operating_cash_flow BIGINT,
    investing_cash_flow BIGINT,
    financing_cash_flow BIGINT,
    free_cash_flow BIGINT,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(stock_code, period_type, fiscal_year, fiscal_quarter)
);

CREATE INDEX idx_financials_stock_period ON financial_statements(stock_code, period_type, fiscal_year DESC);
```

**calculated_indicators**
```sql
CREATE TABLE calculated_indicators (
    stock_code VARCHAR(6) NOT NULL REFERENCES stocks(code),
    calculation_date DATE NOT NULL,

    -- Valuation
    per NUMERIC(10, 2),
    pbr NUMERIC(10, 2),
    psr NUMERIC(10, 2),
    pcr NUMERIC(10, 2),
    ev_ebitda NUMERIC(10, 2),
    dividend_yield NUMERIC(5, 2),

    -- Profitability
    roe NUMERIC(5, 2),
    roa NUMERIC(5, 2),
    gross_margin NUMERIC(5, 2),
    operating_margin NUMERIC(5, 2),
    net_margin NUMERIC(5, 2),

    -- Growth (YoY %)
    revenue_growth NUMERIC(6, 2),
    profit_growth NUMERIC(6, 2),
    eps_growth NUMERIC(6, 2),

    -- Stability
    debt_to_equity NUMERIC(6, 2),
    current_ratio NUMERIC(5, 2),
    quick_ratio NUMERIC(5, 2),
    interest_coverage NUMERIC(6, 2),

    -- Efficiency
    asset_turnover NUMERIC(5, 2),
    inventory_turnover NUMERIC(5, 2),
    receivables_turnover NUMERIC(5, 2),

    -- Technical
    price_change_1d NUMERIC(5, 2),
    price_change_1w NUMERIC(5, 2),
    price_change_1m NUMERIC(5, 2),
    price_change_3m NUMERIC(5, 2),
    price_change_6m NUMERIC(5, 2),
    price_change_1y NUMERIC(5, 2),
    volume_20d_avg BIGINT,
    volume_surge_pct NUMERIC(6, 2),

    -- Overall Score
    quality_score INTEGER CHECK (quality_score BETWEEN 1 AND 100),
    value_score INTEGER CHECK (value_score BETWEEN 1 AND 100),
    growth_score INTEGER CHECK (growth_score BETWEEN 1 AND 100),

    created_at TIMESTAMP DEFAULT NOW(),

    PRIMARY KEY (stock_code, calculation_date)
);

CREATE INDEX idx_indicators_date ON calculated_indicators(calculation_date DESC);
CREATE INDEX idx_indicators_per ON calculated_indicators(per) WHERE per IS NOT NULL;
CREATE INDEX idx_indicators_pbr ON calculated_indicators(pbr) WHERE pbr IS NOT NULL;
CREATE INDEX idx_indicators_roe ON calculated_indicators(roe) WHERE roe IS NOT NULL;
```

#### User & Portfolio Tables

**users**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    subscription_tier VARCHAR(20) NOT NULL DEFAULT 'free' CHECK (subscription_tier IN ('free', 'basic', 'pro')),
    subscription_expires_at TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_tier);
```

**portfolios**
```sql
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_portfolios_user ON portfolios(user_id);
```

**portfolio_holdings**
```sql
CREATE TABLE portfolio_holdings (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    stock_code VARCHAR(6) NOT NULL REFERENCES stocks(code),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    avg_price NUMERIC(10, 2) NOT NULL,
    purchase_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(portfolio_id, stock_code)
);

CREATE INDEX idx_holdings_portfolio ON portfolio_holdings(portfolio_id);
```

**alerts**
```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_code VARCHAR(6) NOT NULL REFERENCES stocks(code),
    alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('price', 'volume', 'indicator')),
    condition VARCHAR(20) NOT NULL CHECK (condition IN ('above', 'below', 'equals')),
    threshold_value NUMERIC(15, 4) NOT NULL,
    notify_via VARCHAR(20)[] DEFAULT ARRAY['email'], -- Array of: email, push
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alerts_user_active ON alerts(user_id, is_active);
CREATE INDEX idx_alerts_stock ON alerts(stock_code) WHERE is_active = TRUE;
```

#### Audit & Analytics Tables

**user_activity_log**
```sql
CREATE TABLE user_activity_log (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action_type VARCHAR(50) NOT NULL, -- login, screen, view_stock, create_portfolio, etc.
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    metadata JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_activity_user_date ON user_activity_log(user_id, created_at DESC);
CREATE INDEX idx_activity_type ON user_activity_log(action_type);
```

**data_ingestion_log**
```sql
CREATE TABLE data_ingestion_log (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL, -- krx, fguide, etc.
    data_type VARCHAR(50) NOT NULL, -- prices, financials, etc.
    records_processed INTEGER,
    records_failed INTEGER,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'partial', 'failed')),
    error_message TEXT,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ingestion_source_date ON data_ingestion_log(source, created_at DESC);
```

---

### 6.5 Caching Strategy

#### Cache Layers

**1. Browser Cache**
- Static assets (JS, CSS, images): 1 year TTL
- Service Worker for offline support (optional Phase 3)

**2. CDN Cache (CloudFlare)**
- Static assets: Edge caching
- API responses: Cache-Control headers for public data

**3. Application Cache (Redis)**

| Data Type | Key Pattern | TTL | Update Trigger |
|-----------|-------------|-----|----------------|
| Hot stocks | `hot_stocks:realtime` | 5 min | Scheduled job every 5 min |
| Stock detail | `stock:{code}:detail` | 1 hour | Daily data pipeline |
| Stock prices (recent) | `stock:{code}:prices:1y` | 1 hour | Daily data pipeline |
| Screening results | `screen:{filter_hash}` | 10 min | Calculated on-demand |
| Market overview | `market:overview` | 5 min | Scheduled job every 5 min |
| User session | `session:{user_id}` | 15 min | Token refresh |
| Indicators (all stocks) | `indicators:all:{date}` | 24 hours | Daily calculation |

**4. Database Query Cache**
- PostgreSQL shared_buffers: 25% of RAM
- Materialized views for common aggregations

#### Cache Invalidation

```python
# Example: Invalidate cache on data update
@celery.task
def update_daily_prices():
    # 1. Fetch new prices from KRX
    new_prices = krx_api.get_daily_prices()

    # 2. Update database
    db.bulk_insert(new_prices)

    # 3. Invalidate relevant caches
    for stock_code in new_prices:
        redis.delete(f"stock:{stock_code}:detail")
        redis.delete(f"stock:{stock_code}:prices:*")

    # 4. Update calculated indicators
    recalculate_indicators.delay()
```

---

### 6.6 Security Architecture

#### Authentication Flow

```
1. User Login
   → Client sends { email, password } to /auth/login
   → Server validates credentials
   → Server generates JWT access token (15 min expiry)
   → Server generates refresh token (30 days expiry, stored in DB)
   → Server returns both tokens

2. Authenticated Request
   → Client includes: Authorization: Bearer <access_token>
   → API Gateway validates JWT signature + expiry
   → If valid, request proceeds to API server
   → If expired, client must refresh

3. Token Refresh
   → Client sends refresh token to /auth/refresh
   → Server validates refresh token (check DB, not revoked)
   → Server issues new access token
   → Client stores new access token

4. Logout
   → Client sends request to /auth/logout
   → Server revokes refresh token (add to blacklist)
   → Client discards tokens
```

#### Security Measures

| Threat | Mitigation |
|--------|------------|
| **SQL Injection** | Parameterized queries via SQLAlchemy ORM |
| **XSS** | CSP headers, sanitize user inputs, escape outputs |
| **CSRF** | SameSite cookies, CSRF tokens for state-changing ops |
| **Brute Force** | Rate limiting (5 failed logins → 15 min lockout) |
| **DDoS** | CloudFlare protection, rate limiting per IP |
| **Data Breach** | Encrypt PII at rest (AES-256), TLS 1.3 in transit |
| **Dependency Vulnerabilities** | Weekly Dependabot scans, automated updates |
| **API Abuse** | Rate limiting (100 req/min per user, 1000/min per IP) |

---

### 6.7 Documentation Infrastructure

#### Unified Documentation Platform

To ensure comprehensive, accessible, and maintainable documentation for all stakeholders (developers, users, QA, and business teams), we will implement a unified documentation platform that consolidates all project documentation.

**Documentation Platform**: Docusaurus (React-based)

**Rationale**:
- **Modern & Interactive**: React-based with MDX support for interactive components
- **Multi-language Support**: Integrates with Python (Sphinx) and TypeScript (TypeDoc) auto-documentation
- **Developer-friendly**: Markdown-based authoring with hot reload
- **Search & Navigation**: Built-in search with Algolia DocSearch integration
- **Versioning**: Support for multiple documentation versions
- **Deployment**: Simple deployment to GitHub Pages, Vercel, or Netlify with CDN

#### Documentation Structure

```
docs-site/
├── docs/
│   ├── 01-getting-started/          # Quickstart, installation, setup
│   ├── 02-guides/
│   │   ├── user-guides/             # End-user feature guides
│   │   ├── developer-guides/        # Development, testing, debugging
│   │   └── deployment/              # Docker, K8s, monitoring setup
│   ├── 03-api-reference/
│   │   ├── backend/                 # Auto-generated from Python (Sphinx)
│   │   ├── frontend/                # Auto-generated from TypeScript (TypeDoc)
│   │   ├── rest-api.md              # REST API endpoints
│   │   ├── websocket-api.md         # WebSocket API
│   │   └── rate-limiting.md         # Rate limiting policies
│   ├── 04-architecture/
│   │   ├── system-design.md         # High-level architecture
│   │   ├── database-schema.md       # Database design
│   │   ├── data-pipeline.md         # Airflow DAGs
│   │   ├── security.md              # Security architecture
│   │   └── performance.md           # Performance design
│   ├── 05-specifications/
│   │   ├── prd.md                   # Product Requirements Document
│   │   ├── srs.md                   # Software Requirements Specification
│   │   └── sds.md                   # Software Design Specification
│   └── 06-operations/
│       ├── monitoring.md            # Monitoring & alerting
│       ├── troubleshooting.md       # Common issues & solutions
│       ├── performance-tuning.md    # Optimization guide
│       └── disaster-recovery.md     # DR procedures
└── blog/                            # Release notes, updates
```

#### Auto-Documentation Integration

| Component | Tool | Source | Output |
|-----------|------|--------|--------|
| **Python Backend** | Sphinx + autodoc | Docstrings in `.py` files | API reference HTML |
| **TypeScript Frontend** | TypeDoc | TSDoc comments in `.ts/.tsx` | Component docs |
| **REST API** | FastAPI | OpenAPI spec | Interactive API docs |
| **Database** | SchemaSpy | PostgreSQL schema | ER diagrams, table docs |

#### Documentation Standards

**Python Docstrings** (Google Style):
```python
def get_stock_by_code(stock_code: str) -> StockDetail:
    """
    Get stock detail by code with caching.

    Args:
        stock_code: 6-digit stock code (e.g., "005930").

    Returns:
        StockDetail with latest price and indicators.

    Raises:
        NotFoundException: If stock not found.

    Example:
        >>> detail = service.get_stock_by_code("005930")
        >>> print(f"{detail.name}: {detail.latest_price.close_price:,} KRW")
        Samsung Electronics: 71,000 KRW
    """
```

**TypeScript TSDoc**:
```typescript
/**
 * Stock screening table with advanced filtering.
 *
 * @param props - Component props
 * @param props.filters - Active screening filters
 * @param props.onStockSelect - Callback when stock selected
 *
 * @example
 * ```tsx
 * <StockScreener
 *   filters={{ market: 'KOSPI', per: { max: 20 } }}
 *   onStockSelect={(stock) => navigate(`/stocks/${stock.code}`)}
 * />
 * ```
 */
export const StockScreener: React.FC<Props> = ({ filters, onStockSelect }) => {
  // Implementation
};
```

#### CI/CD Integration

Documentation will be automatically built and deployed on every commit:

```yaml
# .github/workflows/docs.yml
on:
  pull_request:
    paths: ['docs/**', 'frontend/src/**', 'backend/app/**']
  push:
    branches: [main]

jobs:
  build:
    - Build Sphinx Python docs
    - Build TypeDoc TypeScript docs
    - Build Docusaurus site
    - Check for broken links
    - Run Lighthouse CI (performance audit)
    - Deploy preview (PR only)
    - Deploy production (main branch)
```

#### Documentation Hosting (GitHub Pages)

**Platform**: GitHub Pages

**Rationale**:
- **Cost**: Free for public repositories (unlimited bandwidth)
- **Integration**: Seamless integration with GitHub Actions
- **Simplicity**: Single workflow file, no external services needed
- **Reliability**: GitHub's infrastructure and SLA
- **Version Control**: Documentation versioned alongside code
- **No Limits**: Unlike Vercel/Netlify free tiers

**Configuration**:
- **Production URL**: `https://docs.screener.kr` (custom domain)
- **Fallback URL**: `https://kcenon.github.io/screener_system/`
- **Deployment**: Automatic via GitHub Actions on push to main
- **Branch**: `gh-pages` (auto-created by deployment action)
- **CDN**: GitHub's global CDN (Fastly-powered)
- **SSL**: Auto-managed HTTPS with free certificate
- **Search**: Algolia DocSearch integration (free for open source)

#### Success Metrics

| Metric | Target |
|--------|--------|
| **Documentation Coverage** | > 80% of public APIs documented |
| **Build Time** | < 3 minutes |
| **Page Load Speed** | < 1 second (Lighthouse score > 90) |
| **Search Quality** | > 90% of queries return relevant results |
| **Developer Usage** | > 70% of developers consult docs weekly |

#### Benefits

1. **Single Source of Truth**: All documentation in one searchable location
2. **Auto-updated**: API docs generated from source code, always accurate
3. **Version Control**: Documentation versioned alongside code
4. **Discoverable**: Search, navigation, cross-references make finding info easy
5. **Maintainable**: Markdown-based, easy to contribute, automated checks
6. **Professional**: Modern UI, mobile-friendly, fast loading

---

## 7. Data Requirements

### 7.1 Data Sources

#### Primary Sources

**1. Korea Exchange (KRX)**
- **Data**: Daily stock prices (OHLCV), market cap, shares outstanding
- **Update Frequency**: Daily (after market close, ~16:00 KST)
- **Access Method**: Official API / Web scraping (if no API)
- **Cost**: Free for delayed data, paid for real-time
- **License**: Attribution required

**2. F&Guide (Financial data provider)**
- **Data**: Financial statements, earnings estimates, corporate actions
- **Update Frequency**: Quarterly (earnings reports), daily (estimates)
- **Access Method**: Paid API subscription
- **Cost**: ~$500-1000/month (estimated)
- **License**: Restricted usage, no redistribution

#### Supplementary Sources

**3. Financial news / Press releases**
- **Data**: Corporate events, industry trends for theme detection
- **Sources**: Naver Finance, Company IR pages
- **Update Frequency**: Real-time
- **Access Method**: Web scraping
- **Cost**: Free

**4. Bank of Korea (for macro data)**
- **Data**: Interest rates, inflation, economic indicators
- **Update Frequency**: Monthly
- **Access Method**: Open API
- **Cost**: Free

---

### 7.2 Data Specifications

#### Stock Master Data

| Field | Type | Source | Update Frequency |
|-------|------|--------|------------------|
| Stock Code | VARCHAR(6) | KRX | Static (unless new listings) |
| Stock Name (Korean) | VARCHAR(100) | KRX | Static |
| Market (KOSPI/KOSDAQ) | ENUM | KRX | Static |
| Sector | VARCHAR(50) | KRX | Quarterly (reclassifications) |
| Industry | VARCHAR(100) | KRX | Quarterly |
| Listing Date | DATE | KRX | Static |
| Shares Outstanding | BIGINT | KRX | Quarterly (updated on splits) |

#### Price Data

| Field | Type | Source | Update Frequency |
|-------|------|--------|------------------|
| Trade Date | DATE | KRX | Daily |
| Open Price | INTEGER | KRX | Daily |
| High Price | INTEGER | KRX | Daily |
| Low Price | INTEGER | KRX | Daily |
| Close Price | INTEGER | KRX | Daily |
| Adjusted Close | INTEGER | Calculated | Daily (on corporate actions) |
| Volume | BIGINT | KRX | Daily |
| Trading Value | BIGINT | KRX | Daily |
| Market Cap | BIGINT | Calculated | Daily |

#### Financial Statement Data

| Field | Type | Source | Update Frequency |
|-------|------|--------|------------------|
| Period Type | ENUM | F&Guide | Quarterly/Annually |
| Fiscal Year | INTEGER | F&Guide | Quarterly |
| Fiscal Quarter | INTEGER | F&Guide | Quarterly |
| Revenue | BIGINT | F&Guide | Quarterly |
| Operating Profit | BIGINT | F&Guide | Quarterly |
| Net Profit | BIGINT | F&Guide | Quarterly |
| Total Assets | BIGINT | F&Guide | Quarterly |
| Total Liabilities | BIGINT | F&Guide | Quarterly |
| Equity | BIGINT | F&Guide | Quarterly |
| Operating Cash Flow | BIGINT | F&Guide | Quarterly |
| Free Cash Flow | BIGINT | Calculated | Quarterly |

#### Calculated Indicators (200+ total)

**Valuation (15 indicators)**
- PER (Price-to-Earnings Ratio)
- PBR (Price-to-Book Ratio)
- PSR (Price-to-Sales Ratio)
- PCR (Price-to-Cash Flow Ratio)
- EV/EBITDA
- EV/Sales
- EV/FCF
- Dividend Yield
- Payout Ratio
- PEG Ratio
- Graham Number
- Intrinsic Value (DCF-based)
- Price to Tangible Book
- Price to Operating Cash Flow
- Enterprise Value

**Profitability (20 indicators)**
- ROE (Return on Equity)
- ROA (Return on Assets)
- ROIC (Return on Invested Capital)
- Gross Profit Margin
- Operating Profit Margin
- Net Profit Margin
- EBITDA Margin
- Free Cash Flow Margin
- Asset Turnover
- Equity Multiplier
- DuPont ROE Decomposition
- Operating Leverage
- Earnings Quality (CFO / Net Income)
- Accruals Ratio
- ...

**Growth (25 indicators)**
- Revenue Growth (YoY, QoQ, 3Y CAGR, 5Y CAGR)
- Profit Growth (YoY, QoQ, 3Y CAGR, 5Y CAGR)
- EPS Growth (YoY, QoQ, 3Y CAGR, 5Y CAGR)
- Book Value Growth
- Operating Cash Flow Growth
- Free Cash Flow Growth
- Dividend Growth (5Y CAGR)
- Asset Growth
- Equity Growth
- Sales per Employee Growth
- ...

**Stability (20 indicators)**
- Debt-to-Equity Ratio
- Debt-to-Assets Ratio
- Interest Coverage Ratio
- Current Ratio
- Quick Ratio
- Cash Ratio
- Altman Z-Score
- Piotroski F-Score
- Earnings Stability (Std Dev of ROE)
- Revenue Stability
- Beta (market volatility)
- ...

**Efficiency (15 indicators)**
- Asset Turnover
- Inventory Turnover
- Receivables Turnover
- Payables Turnover
- Cash Conversion Cycle
- Days Sales Outstanding
- Days Inventory Outstanding
- Days Payables Outstanding
- Fixed Asset Turnover
- Working Capital Turnover
- ...

**Technical (30 indicators)**
- Price Change (1D, 1W, 1M, 3M, 6M, 1Y, 3Y, 5Y)
- Volume (20D avg, 60D avg)
- Volume Surge % (vs 20D avg)
- Moving Averages (5D, 20D, 60D, 120D, 200D)
- MACD
- RSI (14-day)
- Bollinger Bands
- ATR (Average True Range)
- On-Balance Volume
- Accumulation/Distribution
- 52-week High/Low
- Distance from 52W High
- New High/Low indicators
- ...

**Quality (15 indicators)**
- Piotroski F-Score (0-9)
- Beneish M-Score (earnings manipulation)
- Earnings Quality Score
- Accounting Quality
- Cash Flow Quality
- Dividend Consistency
- Earnings Consistency
- Return Consistency
- Management Efficiency
- Corporate Governance Score
- ...

**Momentum (10 indicators)**
- Relative Strength (vs index)
- Price Momentum (6M, 12M)
- Earnings Momentum
- Estimate Revisions
- Analyst Rating Changes
- Institutional Ownership Change
- Short Interest Ratio
- ...

**Value Composite Scores (10 indicators)**
- Overall Quality Score (1-100)
- Value Score (1-100)
- Growth Score (1-100)
- Momentum Score (1-100)
- Combined Score (weighted)
- Sector-relative scores
- Percentile rankings
- ...

**Total: 200+ indicators**

---

### 7.3 Data Quality Requirements

| Requirement | Target | Validation Method |
|-------------|--------|-------------------|
| **Accuracy** | 99.9% match with official sources | Daily reconciliation against KRX |
| **Completeness** | < 0.1% missing data points | Data quality checks, alert on gaps |
| **Timeliness** | Daily prices loaded within 30 min of market close | Pipeline monitoring |
| **Consistency** | No conflicting data across tables | Foreign key constraints, checksums |
| **Historical Integrity** | No unauthorized changes to historical data | Audit logs, immutable timestamps |

---

### 7.4 Data Retention Policy

| Data Type | Retention Period | Archive Policy |
|-----------|------------------|----------------|
| Daily prices | Indefinite | Compress data older than 5 years (TimescaleDB compression) |
| Financial statements | Indefinite | Keep all historical reports |
| Calculated indicators | 5 years online, older archived | Move to cold storage after 5 years |
| User activity logs | 2 years | Delete after 2 years (GDPR compliance) |
| User portfolios | Until account deletion | Soft delete (30-day grace period) |
| Alert history | 1 year | Delete after 1 year |

---