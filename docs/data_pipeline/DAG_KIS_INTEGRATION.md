# DAG Integration with KIS API

## Overview

This document describes the integration of Korea Investment & Securities (KIS) API with Airflow DAGs through a data source abstraction layer.

## Architecture

### Data Source Abstraction Layer

```
┌─────────────────────────────────────────────────┐
│           Airflow DAG (daily_price_ingestion)   │
├─────────────────────────────────────────────────┤
│         fetch_stock_prices() function           │
├─────────────────────────────────────────────────┤
│              DataSourceFactory                  │
│         (Environment-based selection)           │
├──────────┬──────────────────────┬───────────────┤
│  KIS API │      KRX API         │   Mock Data   │
│(Production)│    (Legacy)         │  (Testing)    │
└──────────┴──────────────────────┴───────────────┘
```

### Components

1. **AbstractDataSource** (`data_source.py`)
   - Interface defining standard data access methods
   - Ensures consistent API across different data providers

2. **KISDataSource** (`data_source.py`)
   - Wraps `KISAPIClient` with standard interface
   - Handles OAuth authentication, rate limiting, circuit breaker
   - Includes Redis caching for performance

3. **MockDataSource** (`data_source.py`)
   - Provides test data without external dependencies
   - Useful for development and CI/CD pipelines

4. **DataSourceFactory** (`data_source.py`)
   - Factory pattern for creating data source instances
   - Auto-detects configuration from environment variables

## Configuration

### Environment Variables

Set `DATA_SOURCE_TYPE` in `.env` to control data source selection:

```bash
# Options: kis, krx, mock
# Leave empty for auto-detection
DATA_SOURCE_TYPE=kis
```

### Auto-Detection Logic

If `DATA_SOURCE_TYPE` is not set:
1. Check if `KIS_APP_KEY` and `KIS_APP_SECRET` are available
2. If yes → use KIS API
3. If no → use Mock data

### KIS API Configuration

Required environment variables for KIS API:
```bash
# Authentication
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret

# Server selection
KIS_USE_VIRTUAL_SERVER=true  # Use virtual server for testing

# Rate limiting (optional)
KIS_API_RATE_LIMIT=20

# Cache TTL (optional)
KIS_CACHE_TTL_CHART=3600
```

## DAG Modifications

### New Functions

#### `fetch_stock_prices(**context)`

Main entry point that dispatches to appropriate data source based on configuration.

**Features:**
- Environment-based data source selection
- Backward compatible with existing XCom structure
- Comprehensive error handling and logging

#### `fetch_prices_with_data_source(execution_date, source_type, context)`

Fetches prices using DataSourceFactory (KIS or Mock).

**Process:**
1. Queries database for active stock codes
2. Fetches chart data for each stock via data source
3. Converts chart data to price_data format
4. Logs progress every 100 stocks
5. Returns consolidated price list

#### `convert_chart_data_to_price_data(chart_data_list, stock_code)`

Converts KIS `ChartData` objects to DAG's price_data format.

**Mapping:**
```python
ChartData           →  price_data dict
─────────────────      ──────────────────
date                →  trade_date
open_price          →  open_price
high_price          →  high_price
low_price           →  low_price
close_price         →  close_price
volume              →  volume
trading_value       →  trading_value
(not available)     →  market_cap (None)
```

#### `get_all_stock_codes(**context)`

Fetches list of active stock codes from database.

**Query:**
```sql
SELECT stock_code
FROM stocks
WHERE delisting_date IS NULL
ORDER BY stock_code
```

### Enhanced Validation

The `validate_price_data` function now includes:

1. **Error Categorization**
   - Missing fields
   - Invalid price relationships (high < low)
   - Negative values
   - Missing market cap (warning only for KIS data)

2. **Performance Metrics**
   - Validation processing time
   - Records per second throughput
   - Validity rate percentage

3. **Detailed Logging**
   - Data source identification
   - Execution date
   - Validation summary with error breakdown
   - Sample invalid records (first 10)

## Usage Examples

### Example 1: Using KIS API

```bash
# Set environment
export DATA_SOURCE_TYPE=kis
export KIS_APP_KEY=your_key
export KIS_APP_SECRET=your_secret
export KIS_USE_VIRTUAL_SERVER=true

# Run DAG (through Airflow)
airflow dags trigger daily_price_ingestion
```

### Example 2: Using Mock Data (Development)

```bash
# Set environment
export DATA_SOURCE_TYPE=mock

# Run DAG
airflow dags trigger daily_price_ingestion
```

### Example 3: Auto-Detection

```bash
# No DATA_SOURCE_TYPE set
# Will auto-detect based on KIS credentials

# If KIS_APP_KEY is set → uses KIS
# If not → uses Mock

airflow dags trigger daily_price_ingestion
```

## Testing

### Unit Tests

Run the integration test script:

```bash
cd data_pipeline/scripts
python test_dag_integration.py
```

**Test Coverage:**
1. Import verification
2. DataSourceFactory functionality
3. Data conversion functions
4. DAG import (syntax check)
5. Environment detection logic

### Integration Tests

The DAG should be tested in actual Airflow environment:

1. **Mock Data Test**
   ```bash
   export DATA_SOURCE_TYPE=mock
   airflow dags test daily_price_ingestion 2024-01-01
   ```

2. **KIS Virtual Server Test**
   ```bash
   export DATA_SOURCE_TYPE=kis
   export KIS_USE_VIRTUAL_SERVER=true
   airflow dags test daily_price_ingestion 2024-01-01
   ```

## Performance Considerations

### KIS API Limitations

- **Rate Limit**: 20 requests per second
- **Sequential Processing**: Must fetch stocks one by one
- **Expected Duration**:
  - 2,400 stocks × 50ms per request = ~2 minutes (with rate limiting)
  - Redis cache can reduce this significantly on subsequent runs

### Optimization Strategies

1. **Redis Caching**
   - Chart data cached for 1 hour
   - Reduces API calls by 80%+ after first run

2. **Batch Processing** (Future Enhancement)
   - Group stocks by market sector
   - Parallel processing with worker pool
   - Respect rate limits across workers

3. **Incremental Updates**
   - Only fetch updated stocks
   - Compare last_update timestamps

## Migration Path

### Phase 1: Parallel Operation (Current)
- Both KRX and KIS data sources available
- Selection via `DATA_SOURCE_TYPE` environment variable
- No breaking changes to existing DAGs

### Phase 2: Gradual Transition
- Run KIS and KRX in parallel
- Compare data quality
- Validate KIS data accuracy

### Phase 3: KIS Primary
- Switch `DATA_SOURCE_TYPE=kis` in production
- Keep KRX as backup/fallback

### Phase 4: KRX Deprecation
- Remove KRX-specific code
- Keep abstraction layer for future providers

## Troubleshooting

### Issue: "No module named 'requests'"

**Solution:**
```bash
cd data_pipeline
pip install -r requirements.txt
```

### Issue: "No price data received"

**Causes:**
1. No active stocks in database
2. KIS API credentials invalid
3. Rate limit exceeded

**Debug Steps:**
```bash
# Check database
psql -d screener_db -c "SELECT COUNT(*) FROM stocks WHERE delisting_date IS NULL"

# Test KIS credentials
python -c "from data_source import DataSourceFactory; \
  with DataSourceFactory.create() as ds: \
    print(ds.get_current_price('005930'))"
```

### Issue: "Too many invalid records"

**Causes:**
1. Data quality issues from API
2. Network errors during fetch
3. Validation rules too strict

**Debug Steps:**
1. Check validation logs for error categories
2. Review sample invalid records
3. Adjust validation threshold if needed (currently 5%)

## Future Enhancements

1. **Batch API Support**
   - Implement when KIS releases batch endpoints
   - Reduce API calls significantly

2. **WebSocket Integration**
   - Real-time price updates
   - Complementary to daily batch ingestion

3. **Multi-Provider Fallback**
   - Try KIS first
   - Fall back to KRX if KIS fails
   - Ensure data continuity

4. **Smart Caching**
   - Cache warming strategy
   - Predictive pre-fetching
   - Invalidation on market close

## References

- **KIS API Documentation**: https://apiportal.koreainvestment.com/
- **Data Source Code**: `data_pipeline/scripts/data_source.py`
- **KIS Client Code**: `data_pipeline/scripts/kis_api_client.py`
- **DAG Code**: `data_pipeline/dags/daily_price_ingestion_dag.py`
- **Ticket**: `docs/kanban/todo/DP-004.md`

## Change Log

### 2025-11-10: Initial Integration
- Added data source abstraction layer
- Integrated KIS API with daily_price_ingestion DAG
- Enhanced validation with detailed metrics
- Added test script for integration verification
- Updated .env.example with configuration documentation

---

*Last Updated: 2025-11-10*
*Author: AI Assistant*
*Related Ticket: DP-004*
