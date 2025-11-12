---
id: sds-database-design
title: SDS - Database Design
description: Software design specification - database design
sidebar_label: Database Design
sidebar_position: 4
tags:
  - specification
  - design
  - architecture
---

:::info Navigation
- [Introduction](introduction.md)
- [System Architecture](system-architecture.md)
- [Component Design](component-design.md)
- [Database Design](database-design.md) (Current)
- [API Design](api-design.md)
- [Data Pipeline](data-pipeline.md)
- [Security Design](security-design.md)
- [Performance Design](performance-design.md)
- [Deployment](deployment.md)
- [Tech Stack & Decisions](tech-stack-decisions.md)
:::

# Software Design Specification - Database Design

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