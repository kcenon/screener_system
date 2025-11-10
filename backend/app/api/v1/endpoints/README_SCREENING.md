# Stock Screening API

## Overview

The Stock Screening API allows filtering 2,400+ Korean stocks (KOSPI/KOSDAQ) using 200+ financial and technical indicators.

## Endpoints

### 1. POST /v1/screen

Screen stocks with custom filters.

**Request Body:**
```json
{
  "filters": {
    "market": "KOSPI",
    "per": {"min": 0, "max": 15},
    "roe": {"min": 10},
    "dividend_yield": {"min": 3}
  },
  "sort_by": "market_cap",
  "order": "desc",
  "page": 1,
  "per_page": 50
}
```

**Response:**
```json
{
  "stocks": [
    {
      "code": "005930",
      "name": "삼성전자",
      "market": "KOSPI",
      "current_price": 75000,
      "per": 12.5,
      "roe": 15.3,
      "...": "..."
    }
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "per_page": 50,
    "total_pages": 3
  },
  "query_time_ms": 234.5,
  "filters_applied": {
    "market": "KOSPI",
    "per": {"min": 0, "max": 15},
    "roe": {"min": 10},
    "_count": 3
  }
}
```

### 2. GET /v1/screen/templates

Get predefined screening templates.

**Response:**
```json
{
  "templates": [
    {
      "id": "dividend_stocks",
      "name": "고배당주 (High Dividend)",
      "description": "Stocks with dividend yield > 3% and quality score > 70",
      "filters": {
        "dividend_yield": {"min": 3.0},
        "quality_score": {"min": 70.0}
      },
      "sort_by": "dividend_yield",
      "order": "desc"
    }
  ]
}
```

### 3. POST /v1/screen/templates/{template_id}

Apply a predefined template.

**Path Parameters:**
- `template_id`: Template ID (e.g., `dividend_stocks`)

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Results per page (default: 50)

**Example:**
```bash
POST /v1/screen/templates/dividend_stocks?page=1&per_page=50
```

## Available Filters

### Market Filters
- `market`: KOSPI | KOSDAQ | ALL
- `sector`: Sector name (string)
- `industry`: Industry name (string)

### Valuation Filters (FilterRange)
- `per`: Price-to-Earnings Ratio
- `pbr`: Price-to-Book Ratio
- `psr`: Price-to-Sales Ratio
- `pcr`: Price-to-Cash Flow Ratio
- `dividend_yield`: Dividend Yield (%)

### Profitability Filters (FilterRange)
- `roe`: Return on Equity (%)
- `roa`: Return on Assets (%)
- `roic`: Return on Invested Capital (%)
- `gross_margin`: Gross Margin (%)
- `operating_margin`: Operating Margin (%)
- `net_margin`: Net Margin (%)

### Growth Filters (FilterRange)
- `revenue_growth_yoy`: Revenue Growth YoY (%)
- `profit_growth_yoy`: Profit Growth YoY (%)
- `eps_growth_yoy`: EPS Growth YoY (%)

### Stability Filters (FilterRange)
- `debt_to_equity`: Debt-to-Equity Ratio
- `current_ratio`: Current Ratio
- `altman_z_score`: Altman Z-Score (bankruptcy risk)
- `piotroski_f_score`: Piotroski F-Score (0-9)

### Price Momentum Filters (FilterRange)
- `price_change_1d`: 1-Day Price Change (%)
- `price_change_1w`: 1-Week Price Change (%)
- `price_change_1m`: 1-Month Price Change (%)
- `price_change_3m`: 3-Month Price Change (%)
- `price_change_6m`: 6-Month Price Change (%)
- `price_change_1y`: 1-Year Price Change (%)

### Volume Filter (FilterRange)
- `volume_surge_pct`: Volume Surge (%)

### Composite Score Filters (FilterRange)
- `quality_score`: Quality Score (0-100)
- `value_score`: Value Score (0-100)
- `growth_score`: Growth Score (0-100)
- `momentum_score`: Momentum Score (0-100)
- `overall_score`: Overall Score (0-100)

### Price/Market Cap Filters (FilterRange)
- `current_price`: Current Price (KRW)
- `market_cap`: Market Capitalization (KRW billion)

## FilterRange Format

```json
{
  "min": 10.0,  // Minimum value (inclusive, optional)
  "max": 50.0   // Maximum value (inclusive, optional)
}
```

## Sorting

Available sort fields:
- `code`, `name`, `market`, `sector`
- `current_price`, `market_cap`
- All indicator fields (per, pbr, roe, etc.)
- All score fields (quality_score, value_score, etc.)

Sort order:
- `asc`: Ascending
- `desc`: Descending

## Pagination

- `page`: Page number (1-indexed, default: 1)
- `per_page`: Results per page (1-200, default: 50)

## Caching

- **TTL**: 5 minutes
- **Cache Key**: Hash of filters + sort + pagination
- **Invalidation**: After daily indicator calculation

## Performance Targets

- Simple queries: < 200ms (p95)
- Complex queries: < 500ms (p99)
- Cache hit: < 50ms

## Implementation Details

### Architecture
1. **Schema Layer** (`app/schemas/screening.py`)
   - FilterRange: Min/max range filter
   - ScreeningFilters: All 40+ filter fields
   - ScreeningRequest: Request validation
   - ScreenedStock: Response stock object
   - ScreeningResponse: Response with metadata

2. **Repository Layer** (`app/repositories/screening_repository.py`)
   - Dynamic SQL query builder
   - Uses `stock_screening_view` materialized view
   - Parameterized queries (SQL injection safe)
   - NULL value handling

3. **Service Layer** (`app/services/screening_service.py`)
   - Business logic orchestration
   - Redis caching (MD5 hash of filters)
   - Filter summary generation
   - Template management

4. **API Layer** (`app/api/v1/endpoints/screening.py`)
   - FastAPI endpoints
   - Request validation
   - Response transformation

### Database View

Uses `stock_screening_view` materialized view for performance:
- Pre-joins stock, daily_price, calculated_indicators tables
- Includes 40+ indicator fields
- Indexed for fast filtering
- Refreshed daily

### Security

- SQL injection prevention (parameterized queries)
- Filter validation (allowed fields only)
- Rate limiting (middleware)
- Input sanitization (Pydantic)

## Example Use Cases

### 1. High Dividend Stocks
```json
{
  "filters": {
    "dividend_yield": {"min": 4},
    "quality_score": {"min": 70}
  },
  "sort_by": "dividend_yield",
  "order": "desc"
}
```

### 2. Value Stocks
```json
{
  "filters": {
    "per": {"min": 0, "max": 12},
    "pbr": {"min": 0, "max": 1},
    "roe": {"min": 10}
  },
  "sort_by": "value_score",
  "order": "desc"
}
```

### 3. Growth Stocks
```json
{
  "filters": {
    "revenue_growth_yoy": {"min": 20},
    "profit_growth_yoy": {"min": 15}
  },
  "sort_by": "growth_score",
  "order": "desc"
}
```

### 4. Quality Stocks
```json
{
  "filters": {
    "piotroski_f_score": {"min": 7},
    "quality_score": {"min": 80}
  },
  "sort_by": "overall_score",
  "order": "desc"
}
```

## Testing

```bash
# Run unit tests
pytest tests/api/test_screening.py -v

# Run integration tests
pytest tests/integration/test_screening_integration.py -v

# Performance testing
pytest tests/performance/test_screening_performance.py -v
```

## Monitoring

Key metrics to track:
- Query execution time (p50, p95, p99)
- Cache hit rate (target: > 80%)
- Error rate
- Active filter combinations

## Future Enhancements

- [ ] Save custom screens (authenticated users)
- [ ] Screen comparison feature
- [ ] Real-time screening (WebSocket)
- [ ] Export results (CSV, Excel)
- [ ] Backtesting support
- [ ] Custom indicator formulas
