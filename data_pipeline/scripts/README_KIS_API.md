# Korea Investment & Securities (KIS) API Integration

Complete implementation of KIS API client for real-time stock market data integration.

## Features

✅ **OAuth 2.0 Authentication**
- Auto-refresh token mechanism
- Thread-safe token storage
- Automatic expiration handling (refreshes 5 minutes before expiry)

✅ **Rate Limiting**
- Token bucket algorithm (20 requests/second)
- Configurable rate limits via environment variables
- Request queuing support

✅ **Circuit Breaker Pattern**
- Automatic failure detection (5 failures threshold)
- 60-second timeout before retry
- Three states: CLOSED, OPEN, HALF_OPEN

✅ **API Endpoints**
- Current price (`get_current_price`)
- Order book with 10-level depth (`get_order_book`)
- Historical chart data (`get_chart_data`)
- Stock information (`get_stock_info`)

✅ **Mock Data Support**
- Full mock implementation for development/testing
- No API credentials required for testing
- Realistic data generation

✅ **Data Source Abstraction**
- Pluggable architecture
- Easy switching between KIS, KRX, or mock data
- Auto-detection based on available credentials

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r data_pipeline/requirements.txt
```

### 2. Configuration

Add KIS API credentials to `.env`:

```bash
# KIS API Credentials
KIS_APP_KEY=your_app_key_here
KIS_APP_SECRET=your_app_secret_here

# Use virtual server for testing
KIS_USE_VIRTUAL_SERVER=true

# Optional: Explicit data source selection
DATA_SOURCE_TYPE=kis  # or 'mock' for testing
```

### 3. Basic Usage

```python
from data_pipeline.scripts.data_source import create_data_source

# Create data source (auto-detects from environment)
with create_data_source() as source:
    # Get current price
    price = source.get_current_price("005930")
    print(f"{price.stock_name}: {price.current_price:,} KRW")
    print(f"Change: {price.change_rate:+.2f}%")

    # Get order book
    orderbook = source.get_order_book("005930")
    print(f"Best Bid: {orderbook.best_bid:,}")
    print(f"Best Ask: {orderbook.best_ask:,}")
    print(f"Spread: {orderbook.spread:,}")

    # Get chart data
    chart = source.get_chart_data("005930", PriceType.DAILY, 30)
    for candle in chart[:5]:
        print(f"{candle.date}: Close={candle.close_price:,}")
```

## API Reference

### KISAPIClient

Main client for interacting with KIS API.

```python
from data_pipeline.scripts.kis_api_client import KISAPIClient, PriceType

client = KISAPIClient(
    app_key="your_key",
    app_secret="your_secret",
    use_virtual=True,  # Use virtual server
    use_mock=False     # Use real API
)
```

#### Methods

##### get_current_price(stock_code)

Get real-time stock price.

```python
price = client.get_current_price("005930")

# Returns: CurrentPrice
# - stock_code: str
# - stock_name: str
# - current_price: float
# - change_price: float  # 전일대비
# - change_rate: float   # 등락률 (%)
# - open_price: float
# - high_price: float
# - low_price: float
# - volume: int
# - trading_value: float
# - market_cap: float (optional)
# - timestamp: str
```

##### get_order_book(stock_code)

Get 10-level order book (호가).

```python
orderbook = client.get_order_book("005930")

# Returns: OrderBook
# - stock_code: str
# - stock_name: str
# - bid_levels: List[OrderBookLevel]  # 10 levels
# - ask_levels: List[OrderBookLevel]  # 10 levels
# - total_bid_volume: int
# - total_ask_volume: int
# - best_bid: float (property)
# - best_ask: float (property)
# - spread: float (property)
# - timestamp: str

# Each OrderBookLevel contains:
# - price: float
# - volume: int
# - count: int  # Number of orders
```

##### get_chart_data(stock_code, period, count)

Get historical OHLCV data.

```python
from kis_api_client import PriceType

# Daily data
chart = client.get_chart_data("005930", PriceType.DAILY, 100)

# Weekly data
chart = client.get_chart_data("005930", PriceType.WEEKLY, 52)

# Minute data
chart = client.get_chart_data("005930", PriceType.MINUTE_1, 100)

# Returns: List[ChartData]
# - stock_code: str
# - date: str  # YYYYMMDD or YYYYMMDDHHmmss
# - open_price: float
# - high_price: float
# - low_price: float
# - close_price: float
# - volume: int
# - trading_value: float
```

**Available PriceTypes:**
- `PriceType.DAILY` - 일봉
- `PriceType.WEEKLY` - 주봉
- `PriceType.MONTHLY` - 월봉
- `PriceType.MINUTE_1` - 1분봉
- `PriceType.MINUTE_5` - 5분봉
- `PriceType.MINUTE_30` - 30분봉

##### get_stock_info(stock_code)

Get stock information.

```python
info = client.get_stock_info("005930")

# Returns: StockInfo
# - stock_code: str
# - stock_name: str
# - market: str  # KOSPI, KOSDAQ, KONEX
# - sector: str (optional)
# - industry: str (optional)
# - listed_shares: int (optional)
# - face_value: float (optional)
```

### Data Source Abstraction

For production use, prefer the abstraction layer:

```python
from data_pipeline.scripts.data_source import (
    create_data_source,
    DataSourceType
)

# Auto-detect from environment
source = create_data_source()

# Explicit KIS source
source = create_data_source(DataSourceType.KIS)

# Mock source for testing
source = create_data_source(DataSourceType.MOCK)

# Use as context manager
with create_data_source() as source:
    price = source.get_current_price("005930")
```

## Testing

### Unit Tests

Test with mock data (no API credentials needed):

```bash
# Test KIS API client
python3 data_pipeline/scripts/kis_api_client.py

# Test data source abstraction
python3 data_pipeline/scripts/data_source.py
```

Expected output:
```
================================================================================
Testing KIS API client with mock data
================================================================================
...
1. Testing get_current_price()
================================================================================

Samsung Electronics (005930)
  Current Price: 71,000 KRW
  Change: +1,420 (+2.04%)
  Volume: 25,483,920
...
All tests completed successfully!
```

### Integration Tests

Test with real KIS API (requires credentials):

```python
import os
os.environ['KIS_APP_KEY'] = 'your_key'
os.environ['KIS_APP_SECRET'] = 'your_secret'
os.environ['KIS_USE_VIRTUAL_SERVER'] = 'true'

from data_pipeline.scripts.kis_api_client import create_client

with create_client(use_mock=False) as client:
    price = client.get_current_price("005930")
    assert price.current_price > 0
    assert price.stock_name == "Samsung Electronics"
    print("✓ Integration test passed")
```

## Environment Variables

All configuration via `.env`:

```bash
# KIS API Credentials (Required for real API)
KIS_APP_KEY=your_app_key_here
KIS_APP_SECRET=your_app_secret_here
KIS_ACCOUNT_NUMBER=your_account  # Optional, only for trading

# Server Selection
KIS_USE_VIRTUAL_SERVER=true  # true=virtual, false=real

# URLs (auto-configured based on KIS_USE_VIRTUAL_SERVER)
KIS_API_BASE_URL_REAL=https://openapi.koreainvestment.com:9443
KIS_API_BASE_URL_VIRTUAL=https://openapivts.koreainvestment.com:29443

# Rate Limiting
KIS_API_RATE_LIMIT=20             # Requests per second
KIS_API_QUEUE_TIMEOUT=30          # Queue timeout (seconds)

# Circuit Breaker
KIS_API_CIRCUIT_BREAKER_THRESHOLD=5   # Failures before opening
KIS_API_CIRCUIT_BREAKER_TIMEOUT=60    # Timeout before retry (seconds)

# Cache TTL (for future Redis integration)
KIS_CACHE_TTL_PRICE=1800          # Current price: 30 minutes
KIS_CACHE_TTL_ORDERBOOK=10        # Order book: 10 seconds
KIS_CACHE_TTL_CHART=3600          # Chart data: 1 hour
KIS_CACHE_TTL_STOCK_INFO=86400    # Stock info: 24 hours

# Data Source Selection
DATA_SOURCE_TYPE=                 # Leave empty for auto-detection
                                   # Options: kis, krx, mock
```

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Source Layer                       │
├─────────────────────────────────────────────────────────────┤
│  DataSourceFactory                                          │
│  ├─ Auto-detection from environment                         │
│  ├─ Credential validation                                   │
│  └─ Instance creation                                       │
│                                                              │
│  AbstractDataSource (Interface)                             │
│  ├─ get_current_price()                                     │
│  ├─ get_order_book()                                        │
│  ├─ get_chart_data()                                        │
│  └─ get_stock_info()                                        │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │ KISDataSource │ │ KRXDataSource │ │ MockDataSource│
    └───────┬───────┘ └───────────────┘ └───────┬───────┘
            │                                    │
            │         ┌──────────────────────────┘
            ▼         ▼
    ┌─────────────────────────────────────────────────────────┐
    │                  KIS API Client Layer                    │
    ├─────────────────────────────────────────────────────────┤
    │  TokenManager (OAuth 2.0)                               │
    │  ├─ Auto-refresh (5 min before expiry)                  │
    │  ├─ Thread-safe storage                                 │
    │  └─ Error recovery                                      │
    │                                                          │
    │  TokenBucketRateLimiter                                 │
    │  ├─ 20 requests/second                                  │
    │  ├─ Request queuing                                     │
    │  └─ Backpressure handling                               │
    │                                                          │
    │  CircuitBreaker                                         │
    │  ├─ Failure detection (5 threshold)                     │
    │  ├─ State management (CLOSED/OPEN/HALF_OPEN)            │
    │  └─ Auto-recovery (60s timeout)                         │
    │                                                          │
    │  HTTP Session Pool                                      │
    │  ├─ Connection pooling (10-20 connections)              │
    │  ├─ Retry strategy (3 retries, exponential backoff)     │
    │  └─ Timeout handling (30s default)                      │
    └─────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   KIS API        │
                    │   Virtual/Real   │
                    │   Server         │
                    └──────────────────┘
```

## Error Handling

The client implements comprehensive error handling:

### Circuit Breaker States

```
CLOSED (Normal)
    │
    │ 5 consecutive failures
    ▼
OPEN (Reject requests)
    │
    │ 60 seconds timeout
    ▼
HALF_OPEN (Test recovery)
    │
    ├─ Success ──→ CLOSED
    └─ Failure ──→ OPEN
```

### Exception Hierarchy

```python
try:
    price = client.get_current_price("005930")
except ValueError as e:
    # Invalid input (e.g., wrong stock code format)
    print(f"Input error: {e}")
except requests.exceptions.Timeout:
    # Request timeout (>30s)
    print("Request timeout")
except requests.exceptions.HTTPError as e:
    # HTTP error (401, 429, 500, etc.)
    print(f"HTTP error: {e.response.status_code}")
except Exception as e:
    # Circuit breaker OPEN or other errors
    print(f"Service unavailable: {e}")
```

## Performance Considerations

### Rate Limiting
- KIS API limit: **20 requests/second**
- Automatic queuing when limit exceeded
- Configurable timeout for queued requests

### Caching Strategy (Future)
| Data Type | TTL | Justification |
|-----------|-----|---------------|
| Current Price | 30 min | Price updates frequently, balance freshness vs API calls |
| Order Book | 10 sec | Very dynamic, needs near real-time |
| Chart Data | 1 hour | Historical data changes infrequently |
| Stock Info | 24 hours | Static metadata, rarely changes |

### Connection Pooling
- Pool size: 10-20 connections
- Reuses connections for better performance
- Automatic cleanup on client close

## Troubleshooting

### Common Issues

**1. "No API key provided" error**
```bash
# Solution: Add credentials to .env
KIS_APP_KEY=your_key_here
KIS_APP_SECRET=your_secret_here
```

**2. "Circuit breaker OPEN" error**
```python
# Solution: Wait 60 seconds or check KIS API status
# The circuit breaker will auto-recover
import time
time.sleep(60)
# Or use mock data temporarily
client = KISAPIClient(use_mock=True)
```

**3. "Rate limit exceeded" (429 error)**
```python
# Solution: Reduce request frequency
# The rate limiter handles this automatically
# Just retry after a short delay
time.sleep(1)
```

**4. Token refresh fails**
```bash
# Check credentials are correct
# Check network connectivity
# Try virtual server first
KIS_USE_VIRTUAL_SERVER=true
```

## Future Enhancements

- [ ] Redis caching integration
- [ ] WebSocket support for real-time streaming
- [ ] Bulk request optimization
- [ ] Historical data backfill utility
- [ ] Performance monitoring and metrics
- [ ] DAG integration for automated data ingestion

## References

- [KIS API Portal](https://apiportal.koreainvestment.com/)
- [KIS API Documentation](https://apiportal.koreainvestment.com/apiservice/)
- [OAuth 2.0 Specification](https://oauth.net/2/)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)

## License

See LICENSE file in project root.

## Support

For issues or questions:
1. Check this documentation
2. Review `.env.example` for configuration
3. Test with mock data first
4. Check KIS API portal for service status
