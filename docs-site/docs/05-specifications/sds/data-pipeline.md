---
id: sds-data-pipeline
title: SDS - Data Pipeline
description: Software design specification - data pipeline
sidebar_label: Data Pipeline
sidebar_position: 6
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
- [Data Pipeline](data-pipeline.md) (Current)
- [Security Design](security-design.md)
- [Performance Design](performance-design.md)
- [Deployment](deployment.md)
- [Tech Stack & Decisions](tech-stack-decisions.md)
:::

# Software Design Specification - Data Pipeline

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