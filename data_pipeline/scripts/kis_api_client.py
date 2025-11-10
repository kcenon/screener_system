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

    def _make_request(
        self,
        endpoint: str,
        tr_id: str,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to KIS API with authentication and rate limiting.

        Args:
            endpoint: API endpoint path
            tr_id: Transaction ID (required by KIS API)
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            requests.HTTPError: If API returns error status
            ValueError: If response is invalid
        """
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()

        # Get access token
        access_token = self.token_manager.get_token()

        url = f"{self.base_url}{endpoint}"
        headers = {
            'authorization': f'Bearer {access_token}',
            'appkey': self.app_key,
            'appsecret': self.app_secret,
            'tr_id': tr_id,
            'custtype': 'P',  # P: 개인, B: 법인
            'content-type': 'application/json; charset=utf-8'
        }

        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Check API-level error
            if data.get('rt_cd') != '0':
                error_msg = data.get('msg1', 'Unknown error')
                logger.error(f"KIS API error: {error_msg}")
                raise ValueError(f"KIS API error: {error_msg}")

            return data

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {self.timeout}s: {url}")
            raise

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {response.status_code}: {response.text[:200]}")
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def get_current_price(self, stock_code: str) -> CurrentPrice:
        """
        Get current price for a stock.

        Args:
            stock_code: 6-digit stock code (e.g., "005930" for Samsung)

        Returns:
            CurrentPrice object with current price data

        Raises:
            ValueError: If stock code is invalid
            requests.HTTPError: If API call fails

        Example:
            >>> client = KISAPIClient()
            >>> price = client.get_current_price("005930")
            >>> print(f"Samsung: {price.current_price:,} KRW")
            Samsung: 71,000 KRW
        """
        # Validate stock code
        if not stock_code or len(stock_code) != 6 or not stock_code.isdigit():
            raise ValueError(f"Invalid stock code: {stock_code}")

        # Use mock data if configured
        if self.use_mock:
            return self._get_mock_current_price(stock_code)

        # Make API request with circuit breaker
        def api_call():
            endpoint = "/uapi/domestic-stock/v1/quotations/inquire-price"
            tr_id = "FHKST01010100"  # 주식현재가 시세
            params = {
                'FID_COND_MRKT_DIV_CODE': 'J',  # J: 주식, ETF, ETN
                'FID_INPUT_ISCD': stock_code
            }

            response = self._make_request(endpoint, tr_id, params)
            output = response.get('output', {})

            return CurrentPrice(
                stock_code=stock_code,
                stock_name=output.get('hts_kor_isnm', ''),
                current_price=float(output.get('stck_prpr', 0)),
                change_price=float(output.get('prdy_vrss', 0)),
                change_rate=float(output.get('prdy_ctrt', 0)),
                open_price=float(output.get('stck_oprc', 0)),
                high_price=float(output.get('stck_hgpr', 0)),
                low_price=float(output.get('stck_lwpr', 0)),
                volume=int(output.get('acml_vol', 0)),
                trading_value=float(output.get('acml_tr_pbmn', 0)),
                market_cap=float(output.get('hts_avls', 0)) if output.get('hts_avls') else None
            )

        return self.circuit_breaker.call(api_call)

    def get_order_book(self, stock_code: str) -> OrderBook:
        """
        Get order book (호가) with 10-level depth.

        Args:
            stock_code: 6-digit stock code

        Returns:
            OrderBook object with bid/ask levels

        Example:
            >>> orderbook = client.get_order_book("005930")
            >>> print(f"Best bid: {orderbook.best_bid:,}")
            >>> print(f"Best ask: {orderbook.best_ask:,}")
            >>> print(f"Spread: {orderbook.spread:,}")
        """
        if not stock_code or len(stock_code) != 6 or not stock_code.isdigit():
            raise ValueError(f"Invalid stock code: {stock_code}")

        if self.use_mock:
            return self._get_mock_order_book(stock_code)

        def api_call():
            endpoint = "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"
            tr_id = "FHKST01010200"  # 주식호가
            params = {
                'FID_COND_MRKT_DIV_CODE': 'J',
                'FID_INPUT_ISCD': stock_code
            }

            response = self._make_request(endpoint, tr_id, params)
            output = response.get('output1', {})

            # Parse bid levels (매수 호가)
            bid_levels = []
            for i in range(1, 11):
                price = float(output.get(f'bidp{i}', 0))
                volume = int(output.get(f'bidp_rsqn{i}', 0))
                count = int(output.get(f'bidp_rsqn_icdc{i}', 0))
                if price > 0:
                    bid_levels.append(OrderBookLevel(price, volume, count))

            # Parse ask levels (매도 호가)
            ask_levels = []
            for i in range(1, 11):
                price = float(output.get(f'askp{i}', 0))
                volume = int(output.get(f'askp_rsqn{i}', 0))
                count = int(output.get(f'askp_rsqn_icdc{i}', 0))
                if price > 0:
                    ask_levels.append(OrderBookLevel(price, volume, count))

            return OrderBook(
                stock_code=stock_code,
                stock_name=output.get('hts_kor_isnm', ''),
                bid_levels=bid_levels,
                ask_levels=ask_levels,
                total_bid_volume=int(output.get('total_bidp_rsqn', 0)),
                total_ask_volume=int(output.get('total_askp_rsqn', 0))
            )

        return self.circuit_breaker.call(api_call)

    def get_chart_data(
        self,
        stock_code: str,
        period: PriceType = PriceType.DAILY,
        count: int = 100,
        adj_price: bool = True
    ) -> List[ChartData]:
        """
        Get chart data (OHLCV) for a stock.

        Args:
            stock_code: 6-digit stock code
            period: Price type (DAILY, WEEKLY, MONTHLY, MINUTE_1, etc.)
            count: Number of data points (max: 100)
            adj_price: Use adjusted price (권리락 수정주가)

        Returns:
            List of ChartData objects (newest first)

        Example:
            >>> chart = client.get_chart_data("005930", PriceType.DAILY, 30)
            >>> for candle in chart[:5]:
            ...     print(f"{candle.date}: {candle.close_price:,}")
        """
        if not stock_code or len(stock_code) != 6 or not stock_code.isdigit():
            raise ValueError(f"Invalid stock code: {stock_code}")

        if count < 1 or count > 100:
            raise ValueError(f"Count must be between 1 and 100, got {count}")

        if self.use_mock:
            return self._get_mock_chart_data(stock_code, period, count)

        def api_call():
            endpoint = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
            tr_id = "FHKST03010100"  # 국내주식기간별시세(일/주/월/년)

            params = {
                'FID_COND_MRKT_DIV_CODE': 'J',
                'FID_INPUT_ISCD': stock_code,
                'FID_INPUT_DATE_1': '',  # Empty for recent data
                'FID_INPUT_DATE_2': '',
                'FID_PERIOD_DIV_CODE': period.value,
                'FID_ORG_ADJ_PRC': '0' if adj_price else '1'
            }

            response = self._make_request(endpoint, tr_id, params)
            output = response.get('output2', [])

            chart_data = []
            for item in output[:count]:
                chart_data.append(ChartData(
                    stock_code=stock_code,
                    date=item.get('stck_bsop_date', ''),
                    open_price=float(item.get('stck_oprc', 0)),
                    high_price=float(item.get('stck_hgpr', 0)),
                    low_price=float(item.get('stck_lwpr', 0)),
                    close_price=float(item.get('stck_clpr', 0)),
                    volume=int(item.get('acml_vol', 0)),
                    trading_value=float(item.get('acml_tr_pbmn', 0))
                ))

            return chart_data

        return self.circuit_breaker.call(api_call)

    def get_stock_info(self, stock_code: str) -> StockInfo:
        """
        Get stock information (종목 정보).

        Args:
            stock_code: 6-digit stock code

        Returns:
            StockInfo object

        Example:
            >>> info = client.get_stock_info("005930")
            >>> print(f"{info.stock_name} ({info.market})")
            >>> print(f"Sector: {info.sector}")
        """
        if not stock_code or len(stock_code) != 6 or not stock_code.isdigit():
            raise ValueError(f"Invalid stock code: {stock_code}")

        if self.use_mock:
            return self._get_mock_stock_info(stock_code)

        def api_call():
            endpoint = "/uapi/domestic-stock/v1/quotations/search-stock-info"
            tr_id = "CTPF1604R"  # 종목기본조회
            params = {
                'PRDT_TYPE_CD': '300',  # 주식
                'PDNO': stock_code
            }

            response = self._make_request(endpoint, tr_id, params)
            output = response.get('output', {})

            return StockInfo(
                stock_code=stock_code,
                stock_name=output.get('prdt_name', ''),
                market=output.get('std_pdno', ''),  # KOSPI/KOSDAQ
                sector=output.get('sctr_name', None),
                industry=output.get('bstp_name', None),
                listed_shares=int(output.get('lstg_stqt', 0)) if output.get('lstg_stqt') else None,
                face_value=float(output.get('face_val', 0)) if output.get('face_val') else None
            )

        return self.circuit_breaker.call(api_call)

    # ========================================================================
    # Mock Data Methods
    # ========================================================================

    def _get_mock_current_price(self, stock_code: str) -> CurrentPrice:
        """Generate mock current price data"""
        import random
        random.seed(stock_code)

        # Mock stock names
        stock_names = {
            '005930': 'Samsung Electronics',
            '000660': 'SK Hynix',
            '035420': 'NAVER',
            '051910': 'LG Chem',
            '035720': 'Kakao'
        }

        base_price = random.randint(50000, 500000)
        change_rate = random.uniform(-5.0, 5.0)

        current_price = base_price * (1 + change_rate / 100)
        change_price = current_price - base_price

        return CurrentPrice(
            stock_code=stock_code,
            stock_name=stock_names.get(stock_code, f'Stock {stock_code}'),
            current_price=round(current_price, 0),
            change_price=round(change_price, 0),
            change_rate=round(change_rate, 2),
            open_price=round(base_price * 0.98, 0),
            high_price=round(current_price * 1.02, 0),
            low_price=round(current_price * 0.98, 0),
            volume=random.randint(1000000, 50000000),
            trading_value=current_price * random.randint(1000000, 50000000),
            market_cap=current_price * random.randint(100000000, 500000000)
        )

    def _get_mock_order_book(self, stock_code: str) -> OrderBook:
        """Generate mock order book data"""
        import random
        random.seed(stock_code)

        stock_names = {
            '005930': 'Samsung Electronics',
            '000660': 'SK Hynix',
            '035420': 'NAVER'
        }

        base_price = random.randint(50000, 500000)

        # Generate bid levels (매수 호가)
        bid_levels = []
        for i in range(10):
            price = base_price - (i * 100)
            volume = random.randint(1000, 100000)
            count = random.randint(10, 500)
            bid_levels.append(OrderBookLevel(price, volume, count))

        # Generate ask levels (매도 호가)
        ask_levels = []
        for i in range(10):
            price = base_price + ((i + 1) * 100)
            volume = random.randint(1000, 100000)
            count = random.randint(10, 500)
            ask_levels.append(OrderBookLevel(price, volume, count))

        return OrderBook(
            stock_code=stock_code,
            stock_name=stock_names.get(stock_code, f'Stock {stock_code}'),
            bid_levels=bid_levels,
            ask_levels=ask_levels,
            total_bid_volume=sum(level.volume for level in bid_levels),
            total_ask_volume=sum(level.volume for level in ask_levels)
        )

    def _get_mock_chart_data(
        self,
        stock_code: str,
        period: PriceType,
        count: int
    ) -> List[ChartData]:
        """Generate mock chart data"""
        import random
        from datetime import datetime, timedelta

        random.seed(stock_code + period.value)
        base_price = random.randint(50000, 500000)

        chart_data = []
        current_date = datetime.now()

        for i in range(count):
            # Calculate date based on period
            if period == PriceType.DAILY:
                date = (current_date - timedelta(days=i)).strftime('%Y%m%d')
            elif period == PriceType.WEEKLY:
                date = (current_date - timedelta(weeks=i)).strftime('%Y%m%d')
            elif period == PriceType.MONTHLY:
                date = (current_date - timedelta(days=i*30)).strftime('%Y%m%d')
            else:
                date = (current_date - timedelta(minutes=i)).strftime('%Y%m%d%H%M%S')

            # Generate OHLCV
            close = base_price * (1 + random.uniform(-0.05, 0.05))
            open_price = close * (1 + random.uniform(-0.02, 0.02))
            high = max(open_price, close) * (1 + random.uniform(0, 0.02))
            low = min(open_price, close) * (1 - random.uniform(0, 0.02))
            volume = random.randint(1000000, 50000000)

            chart_data.append(ChartData(
                stock_code=stock_code,
                date=date,
                open_price=round(open_price, 0),
                high_price=round(high, 0),
                low_price=round(low, 0),
                close_price=round(close, 0),
                volume=volume,
                trading_value=close * volume
            ))

        return chart_data

    def _get_mock_stock_info(self, stock_code: str) -> StockInfo:
        """Generate mock stock info"""
        stock_info = {
            '005930': ('Samsung Electronics', 'KOSPI', 'Technology', 'Semiconductor'),
            '000660': ('SK Hynix', 'KOSPI', 'Technology', 'Semiconductor'),
            '035420': ('NAVER', 'KOSPI', 'Technology', 'Internet'),
            '051910': ('LG Chem', 'KOSPI', 'Materials', 'Chemicals'),
            '035720': ('Kakao', 'KOSPI', 'Technology', 'Internet')
        }

        if stock_code in stock_info:
            name, market, sector, industry = stock_info[stock_code]
        else:
            name = f'Stock {stock_code}'
            market = 'KOSPI'
            sector = 'Unknown'
            industry = 'Unknown'

        return StockInfo(
            stock_code=stock_code,
            stock_name=name,
            market=market,
            sector=sector,
            industry=industry,
            listed_shares=1000000000,
            face_value=100.0
        )

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
    logger.info("=" * 80)
    logger.info("Testing KIS API client with mock data")
    logger.info("=" * 80)

    with create_client(use_mock=True) as client:
        logger.info(f"KIS API Client initialized successfully")
        logger.info(f"Base URL: {client.base_url}")
        logger.info(f"Using mock data: {client.use_mock}")

        # Test stock codes
        test_stocks = ['005930', '000660', '035420']

        print("\n" + "=" * 80)
        print("1. Testing get_current_price()")
        print("=" * 80)
        for stock_code in test_stocks:
            try:
                price = client.get_current_price(stock_code)
                print(f"\n{price.stock_name} ({stock_code})")
                print(f"  Current Price: {price.current_price:,.0f} KRW")
                print(f"  Change: {price.change_price:+,.0f} ({price.change_rate:+.2f}%)")
                print(f"  Volume: {price.volume:,}")
            except Exception as e:
                print(f"  Error: {e}")

        print("\n" + "=" * 80)
        print("2. Testing get_order_book()")
        print("=" * 80)
        try:
            orderbook = client.get_order_book('005930')
            print(f"\n{orderbook.stock_name} Order Book")
            print(f"  Best Ask: {orderbook.best_ask:,.0f} KRW")
            print(f"  Best Bid: {orderbook.best_bid:,.0f} KRW")
            print(f"  Spread: {orderbook.spread:,.0f} KRW")
            print(f"  Total Ask Volume: {orderbook.total_ask_volume:,}")
            print(f"  Total Bid Volume: {orderbook.total_bid_volume:,}")
            print(f"\n  Top 3 Ask Levels:")
            for i, level in enumerate(orderbook.ask_levels[:3], 1):
                print(f"    {i}. {level.price:,.0f} KRW - {level.volume:,} shares ({level.count} orders)")
            print(f"  Top 3 Bid Levels:")
            for i, level in enumerate(orderbook.bid_levels[:3], 1):
                print(f"    {i}. {level.price:,.0f} KRW - {level.volume:,} shares ({level.count} orders)")
        except Exception as e:
            print(f"  Error: {e}")

        print("\n" + "=" * 80)
        print("3. Testing get_chart_data()")
        print("=" * 80)
        try:
            chart = client.get_chart_data('005930', PriceType.DAILY, 5)
            print(f"\nSamsung Electronics - Last 5 Days")
            for candle in chart:
                print(f"  {candle.date}: O={candle.open_price:,.0f} "
                      f"H={candle.high_price:,.0f} L={candle.low_price:,.0f} "
                      f"C={candle.close_price:,.0f} V={candle.volume:,}")
        except Exception as e:
            print(f"  Error: {e}")

        print("\n" + "=" * 80)
        print("4. Testing get_stock_info()")
        print("=" * 80)
        for stock_code in test_stocks:
            try:
                info = client.get_stock_info(stock_code)
                print(f"\n{info.stock_name} ({stock_code})")
                print(f"  Market: {info.market}")
                print(f"  Sector: {info.sector}")
                print(f"  Industry: {info.industry}")
                if info.listed_shares:
                    print(f"  Listed Shares: {info.listed_shares:,}")
            except Exception as e:
                print(f"  Error: {e}")

        print("\n" + "=" * 80)
        print("All tests completed successfully!")
        print("=" * 80)
