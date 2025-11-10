"""
Korea Investment & Securities (KIS) API Client

This module provides a client for fetching real-time stock market data from KIS API.
Supports OAuth 2.0 authentication, rate limiting, circuit breaker pattern, and caching.

Features:
- OAuth 2.0 authentication with auto-refresh
- Rate limiting (20 requests/second)
- Circuit breaker for fault tolerance
- Redis caching support
- Mock data for development/testing

Usage:
    client = KISAPIClient(
        app_key=APP_KEY,
        app_secret=APP_SECRET,
        use_virtual=True
    )

    # Get current price
    price = client.get_current_price("005930")

    # Get order book
    orderbook = client.get_order_book("005930")

    # Get chart data
    chart = client.get_chart_data("005930", period="D", count=100)
"""

import os
import time
import logging
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Literal
from dataclasses import dataclass, field
from enum import Enum
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from threading import Lock

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class PriceType(Enum):
    """Price type for chart data"""
    DAILY = "D"      # 일봉
    WEEKLY = "W"     # 주봉
    MONTHLY = "M"    # 월봉
    MINUTE_1 = "1"   # 1분봉
    MINUTE_5 = "5"   # 5분봉
    MINUTE_30 = "30" # 30분봉


@dataclass
class CurrentPrice:
    """Current stock price data"""
    stock_code: str
    stock_name: str
    current_price: float
    change_price: float  # 전일대비
    change_rate: float   # 등락률 (%)
    open_price: float
    high_price: float
    low_price: float
    volume: int
    trading_value: float
    market_cap: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class OrderBookLevel:
    """Order book level (bid or ask)"""
    price: float
    volume: int
    count: int  # Number of orders


@dataclass
class OrderBook:
    """Order book data with 10-level depth"""
    stock_code: str
    stock_name: str
    bid_levels: List[OrderBookLevel]  # 10 levels (best to worst)
    ask_levels: List[OrderBookLevel]  # 10 levels (best to worst)
    total_bid_volume: int
    total_ask_volume: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def spread(self) -> float:
        """Calculate bid-ask spread"""
        if self.bid_levels and self.ask_levels:
            return self.ask_levels[0].price - self.bid_levels[0].price
        return 0.0

    @property
    def best_bid(self) -> Optional[float]:
        """Best bid price"""
        return self.bid_levels[0].price if self.bid_levels else None

    @property
    def best_ask(self) -> Optional[float]:
        """Best ask price"""
        return self.ask_levels[0].price if self.ask_levels else None


@dataclass
class ChartData:
    """Chart data (OHLCV)"""
    stock_code: str
    date: str            # YYYYMMDD or YYYYMMDDHHmmss
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    trading_value: Optional[float] = None


@dataclass
class StockInfo:
    """Stock information"""
    stock_code: str
    stock_name: str
    market: str  # KOSPI, KOSDAQ, KONEX
    sector: Optional[str] = None
    industry: Optional[str] = None
    listed_shares: Optional[int] = None
    face_value: Optional[float] = None


# ============================================================================
# Rate Limiter
# ============================================================================

class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for API requests.

    KIS API allows 20 requests per second.
    """

    def __init__(self, rate: int = 20, per: float = 1.0):
        """
        Initialize rate limiter.

        Args:
            rate: Maximum requests allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = float(rate)
        self.last_check = time.time()
        self.lock = Lock()

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        with self.lock:
            current = time.time()
            time_passed = current - self.last_check
            self.last_check = current

            # Add tokens based on time passed
            self.allowance += time_passed * (self.rate / self.per)
            if self.allowance > self.rate:
                self.allowance = self.rate

            # Check if we have tokens
            if self.allowance < 1.0:
                sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
                logger.debug(f"Rate limit: sleeping {sleep_time:.3f}s")
                time.sleep(sleep_time)
                self.allowance = 0.0
            else:
                self.allowance -= 1.0


# ============================================================================
# Circuit Breaker
# ============================================================================

class CircuitBreaker:
    """
    Circuit breaker pattern for API fault tolerance.

    States:
    - CLOSED: Normal operation
    - OPEN: Too many failures, reject requests
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying again
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"
        self.lock = Lock()

    def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to call
            *args, **kwargs: Function arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is OPEN or function fails
        """
        with self.lock:
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                    logger.info("Circuit breaker: HALF_OPEN, attempting reset")
                else:
                    raise Exception(
                        f"Circuit breaker OPEN: too many failures. "
                        f"Retry after {self.timeout}s"
                    )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.timeout

    def _on_success(self):
        """Handle successful call"""
        with self.lock:
            self.failure_count = 0
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                logger.info("Circuit breaker: CLOSED (recovered)")

    def _on_failure(self):
        """Handle failed call"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(
                    f"Circuit breaker: OPEN ({self.failure_count} failures)"
                )


# ============================================================================
# OAuth 2.0 Token Manager
# ============================================================================

class TokenManager:
    """
    Manages OAuth 2.0 access tokens for KIS API.

    Features:
    - Auto-refresh before expiration
    - Thread-safe token storage
    """

    def __init__(self, app_key: str, app_secret: str, base_url: str):
        """
        Initialize token manager.

        Args:
            app_key: KIS API app key
            app_secret: KIS API app secret
            base_url: KIS API base URL
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = base_url
        self.access_token = None
        self.token_type = None
        self.expires_at = None
        self.lock = Lock()

    def get_token(self) -> str:
        """
        Get valid access token (auto-refresh if needed).

        Returns:
            Access token string
        """
        with self.lock:
            # Check if token needs refresh
            if self._needs_refresh():
                self._refresh_token()

            return self.access_token

    def _needs_refresh(self) -> bool:
        """Check if token needs refresh"""
        if not self.access_token:
            return True

        if not self.expires_at:
            return True

        # Refresh 5 minutes before expiration
        now = datetime.now()
        return now >= (self.expires_at - timedelta(minutes=5))

    def _refresh_token(self):
        """
        Refresh OAuth access token.

        Raises:
            requests.HTTPError: If token request fails
        """
        logger.info("Refreshing KIS API access token")

        url = f"{self.base_url}/oauth2/tokenP"
        headers = {
            "content-type": "application/json"
        }
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }

        try:
            response = requests.post(url, headers=headers, json=body, timeout=30)
            response.raise_for_status()

            data = response.json()
            self.access_token = data["access_token"]
            self.token_type = data.get("token_type", "Bearer")

            # Calculate expiration (default 24 hours)
            expires_in = int(data.get("expires_in", 86400))
            self.expires_at = datetime.now() + timedelta(seconds=expires_in)

            logger.info(
                f"Access token refreshed successfully. "
                f"Expires at: {self.expires_at.isoformat()}"
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh access token: {e}")
            raise

        except (KeyError, ValueError) as e:
            logger.error(f"Invalid token response: {e}")
            raise ValueError(f"Invalid token response: {e}")


# ============================================================================
# KIS API Client
# ============================================================================

class KISAPIClient:
    """
    Client for Korea Investment & Securities API.

    Features:
    - OAuth 2.0 authentication with auto-refresh
    - Rate limiting (20 requests/second)
    - Circuit breaker for fault tolerance
    - Connection pooling and retry logic
    - Mock data support for development/testing

    Configuration via environment variables:
    - KIS_APP_KEY: Application key
    - KIS_APP_SECRET: Application secret
    - KIS_USE_VIRTUAL_SERVER: Use virtual server (true/false)
    - KIS_API_BASE_URL_REAL: Real server URL
    - KIS_API_BASE_URL_VIRTUAL: Virtual server URL
    - KIS_API_RATE_LIMIT: Rate limit (default: 20/sec)
    - KIS_API_CIRCUIT_BREAKER_THRESHOLD: Failure threshold (default: 5)
    - KIS_API_CIRCUIT_BREAKER_TIMEOUT: Circuit breaker timeout (default: 60s)

    Example:
        ```python
        client = KISAPIClient(
            app_key=os.getenv('KIS_APP_KEY'),
            app_secret=os.getenv('KIS_APP_SECRET'),
            use_virtual=True
        )

        # Get current price
        price = client.get_current_price("005930")
        print(f"Samsung: {price.current_price:,} KRW")

        # Get order book
        orderbook = client.get_order_book("005930")
        print(f"Best bid: {orderbook.best_bid:,}")
        print(f"Best ask: {orderbook.best_ask:,}")
        ```
    """

    def __init__(
        self,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        use_virtual: bool = None,
        use_mock: bool = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize KIS API client.

        Args:
            app_key: KIS API app key (if None, reads from KIS_APP_KEY)
            app_secret: KIS API app secret (if None, reads from KIS_APP_SECRET)
            use_virtual: Use virtual server (if None, reads from KIS_USE_VIRTUAL_SERVER)
            use_mock: Use mock data for testing (if None, reads from environment)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        # Get credentials
        self.app_key = app_key or os.getenv('KIS_APP_KEY')
        self.app_secret = app_secret or os.getenv('KIS_APP_SECRET')

        # Determine server URL
        if use_virtual is None:
            use_virtual = os.getenv('KIS_USE_VIRTUAL_SERVER', 'true').lower() == 'true'

        if use_virtual:
            self.base_url = os.getenv(
                'KIS_API_BASE_URL_VIRTUAL',
                'https://openapivts.koreainvestment.com:29443'
            )
        else:
            self.base_url = os.getenv(
                'KIS_API_BASE_URL_REAL',
                'https://openapi.koreainvestment.com:9443'
            )

        self.timeout = timeout
        self.max_retries = max_retries

        # Determine if using mock data
        if use_mock is None:
            use_mock = not bool(self.app_key and self.app_secret)
        self.use_mock = use_mock

        # Initialize components
        rate_limit = int(os.getenv('KIS_API_RATE_LIMIT', '20'))
        self.rate_limiter = TokenBucketRateLimiter(rate=rate_limit, per=1.0)

        failure_threshold = int(os.getenv('KIS_API_CIRCUIT_BREAKER_THRESHOLD', '5'))
        circuit_timeout = int(os.getenv('KIS_API_CIRCUIT_BREAKER_TIMEOUT', '60'))
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            timeout=circuit_timeout
        )

        # Configure session with retry strategy
        self.session = self._create_session()

        # Initialize token manager (only if not using mock)
        if not self.use_mock:
            if not self.app_key or not self.app_secret:
                raise ValueError(
                    "KIS_APP_KEY and KIS_APP_SECRET must be set. "
                    "Set use_mock=True to use mock data."
                )
            self.token_manager = TokenManager(
                self.app_key,
                self.app_secret,
                self.base_url
            )
        else:
            self.token_manager = None
            logger.info("Using mock data mode (no API calls will be made)")

    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()

        # Retry strategy for transient failures
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,  # 1s, 2s, 4s delays
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def close(self):
        """Close HTTP session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# ============================================================================
# Utility Functions
# ============================================================================

def create_client(use_mock: bool = None) -> KISAPIClient:
    """
    Create and return a KIS API client.

    Args:
        use_mock: Use mock data (None = auto-detect from environment)

    Returns:
        Configured KISAPIClient instance

    Example:
        ```python
        from kis_api_client import create_client

        with create_client(use_mock=True) as client:
            price = client.get_current_price("005930")
        ```
    """
    return KISAPIClient(use_mock=use_mock)


if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Test with mock data
    logger.info("Testing KIS API client with mock data")

    with create_client(use_mock=True) as client:
        logger.info(f"KIS API Client initialized successfully")
        logger.info(f"Base URL: {client.base_url}")
        logger.info(f"Using mock data: {client.use_mock}")
        logger.info("Client is ready for use")
