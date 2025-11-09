"""
KRX API Client for Stock Data Ingestion

This module provides a client for fetching stock market data from KRX (Korea Exchange).
Supports both production API and mock data for development/testing.

Usage:
    client = KRXAPIClient(api_key=API_KEY, use_mock=False)
    prices = client.fetch_daily_prices(date="2024-01-15")
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logger = logging.getLogger(__name__)


class Market(Enum):
    """Stock market types"""
    KOSPI = "KOSPI"
    KOSDAQ = "KOSDAQ"
    KONEX = "KONEX"


@dataclass
class PriceData:
    """Stock price data structure"""
    stock_code: str
    trade_date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    trading_value: float
    market_cap: Optional[float] = None
    market: Optional[str] = None


class RateLimiter:
    """
    Rate limiter to respect API rate limits.

    KRX API typically allows:
    - 10 requests per second
    - 1000 requests per hour
    """

    def __init__(self, calls_per_second: int = 10, calls_per_hour: int = 1000):
        self.calls_per_second = calls_per_second
        self.calls_per_hour = calls_per_hour
        self.second_calls: List[float] = []
        self.hour_calls: List[float] = []

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()

        # Clean up old calls
        self.second_calls = [t for t in self.second_calls if now - t < 1.0]
        self.hour_calls = [t for t in self.hour_calls if now - t < 3600.0]

        # Wait if needed
        if len(self.second_calls) >= self.calls_per_second:
            sleep_time = 1.0 - (now - self.second_calls[0])
            if sleep_time > 0:
                logger.debug(f"Rate limit: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)

        if len(self.hour_calls) >= self.calls_per_hour:
            sleep_time = 3600.0 - (now - self.hour_calls[0])
            if sleep_time > 0:
                logger.warning(f"Hourly rate limit reached, sleeping {sleep_time:.0f}s")
                time.sleep(sleep_time)

        # Record this call
        now = time.time()
        self.second_calls.append(now)
        self.hour_calls.append(now)


class KRXAPIClient:
    """
    Client for interacting with KRX (Korea Exchange) API.

    Configuration via environment variables:
    - KRX_API_KEY: API authentication key
    - KRX_API_BASE_URL: Base URL for API (default: https://api.krx.co.kr)
    - KRX_USE_MOCK: Set to "true" to use mock data for testing

    Example:
        client = KRXAPIClient(api_key=os.getenv('KRX_API_KEY'))
        prices = client.fetch_daily_prices(date="2024-01-15")
    """

    DEFAULT_BASE_URL = "https://api.krx.co.kr"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        use_mock: bool = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize KRX API client.

        Args:
            api_key: KRX API key (if None, reads from KRX_API_KEY env var)
            base_url: API base URL (if None, uses DEFAULT_BASE_URL)
            use_mock: Use mock data instead of real API (if None, reads from KRX_USE_MOCK)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = api_key or os.getenv('KRX_API_KEY')
        self.base_url = base_url or os.getenv('KRX_API_BASE_URL', self.DEFAULT_BASE_URL)
        self.timeout = timeout
        self.max_retries = max_retries

        # Determine if using mock data
        if use_mock is None:
            use_mock = os.getenv('KRX_USE_MOCK', 'false').lower() == 'true'
        self.use_mock = use_mock

        # Rate limiter
        self.rate_limiter = RateLimiter()

        # Configure session with retry strategy
        self.session = self._create_session()

        # Warn if API key is missing and not using mock
        if not self.use_mock and not self.api_key:
            logger.warning(
                "KRX_API_KEY not set. API calls will fail. "
                "Set KRX_USE_MOCK=true to use mock data."
            )

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

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to KRX API with rate limiting and error handling.

        Args:
            endpoint: API endpoint path
            method: HTTP method (GET or POST)
            params: Query parameters
            data: Request body data

        Returns:
            JSON response data

        Raises:
            requests.HTTPError: If API returns error status
            ValueError: If response is invalid
        """
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()

        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'ScreenerSystem/1.0'
        }

        try:
            if method.upper() == "GET":
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
            elif method.upper() == "POST":
                response = self.session.post(
                    url,
                    params=params,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            # Parse JSON response
            try:
                return response.json()
            except ValueError as e:
                logger.error(f"Invalid JSON response: {response.text[:200]}")
                raise ValueError(f"Invalid JSON response: {e}")

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {self.timeout}s: {url}")
            raise

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {response.status_code}: {response.text[:200]}")
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def authenticate(self) -> bool:
        """
        Authenticate with KRX API and verify API key is valid.

        Returns:
            True if authentication successful, False otherwise
        """
        if self.use_mock:
            logger.info("Using mock data - skipping authentication")
            return True

        if not self.api_key:
            logger.error("No API key provided")
            return False

        try:
            # Try to make a simple API call to verify authentication
            # Replace '/auth/verify' with actual KRX auth endpoint
            response = self._make_request('/auth/verify', method='GET')
            logger.info("Authentication successful")
            return True

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("Authentication failed: invalid API key")
            else:
                logger.error(f"Authentication failed: {e}")
            return False

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def fetch_daily_prices(
        self,
        date: str,
        market: Optional[Market] = None
    ) -> List[PriceData]:
        """
        Fetch daily stock prices for a specific date.

        Args:
            date: Trading date in YYYY-MM-DD format
            market: Filter by market (None for all markets)

        Returns:
            List of PriceData objects

        Raises:
            ValueError: If date format is invalid
            requests.HTTPError: If API call fails

        Example:
            >>> client = KRXAPIClient()
            >>> prices = client.fetch_daily_prices("2024-01-15")
            >>> len(prices)
            2500
        """
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD")

        # Use mock data if configured
        if self.use_mock:
            return self._fetch_mock_data(date, market)

        # Make API request
        params = {'date': date}
        if market:
            params['market'] = market.value

        try:
            # Replace '/data/daily_prices' with actual KRX endpoint
            response = self._make_request(
                endpoint='/data/daily_prices',
                method='GET',
                params=params
            )

            # Transform API response to PriceData objects
            prices = self._transform_response(response)

            logger.info(f"Fetched {len(prices)} stock prices for {date}")
            return prices

        except Exception as e:
            logger.error(f"Failed to fetch daily prices for {date}: {e}")
            raise

    def _transform_response(self, response: Dict[str, Any]) -> List[PriceData]:
        """
        Transform KRX API response to PriceData objects.

        This method should be updated based on actual KRX API response format.
        """
        prices = []

        # Assuming response format: {'data': [list of stock records]}
        # Update this based on actual KRX API response structure
        records = response.get('data', [])

        for record in records:
            try:
                price_data = PriceData(
                    stock_code=record['stock_code'],
                    trade_date=record['trade_date'],
                    open_price=float(record['open_price']),
                    high_price=float(record['high_price']),
                    low_price=float(record['low_price']),
                    close_price=float(record['close_price']),
                    volume=int(record['volume']),
                    trading_value=float(record['trading_value']),
                    market_cap=float(record.get('market_cap')) if record.get('market_cap') else None,
                    market=record.get('market')
                )
                prices.append(price_data)
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping invalid record: {e}")
                continue

        return prices

    def _fetch_mock_data(
        self,
        date: str,
        market: Optional[Market] = None
    ) -> List[PriceData]:
        """
        Generate mock price data for development/testing.

        Creates realistic-looking data for major Korean stocks.
        """
        logger.info(f"Generating mock data for {date}")

        # Mock data for major Korean stocks
        mock_stocks = [
            # KOSPI stocks
            ('005930', 'Samsung Electronics', 'KOSPI', 70000, 75000),
            ('000660', 'SK Hynix', 'KOSPI', 125000, 130000),
            ('035420', 'NAVER', 'KOSPI', 200000, 210000),
            ('051910', 'LG Chem', 'KOSPI', 450000, 470000),
            ('035720', 'Kakao', 'KOSPI', 50000, 52000),
            ('006400', 'Samsung SDI', 'KOSPI', 380000, 395000),
            ('207940', 'Samsung Biologics', 'KOSPI', 850000, 870000),
            ('068270', 'Celltrion', 'KOSPI', 180000, 185000),
            ('028260', 'Samsung C&T', 'KOSPI', 120000, 125000),
            ('012330', 'Hyundai Mobis', 'KOSPI', 230000, 240000),
            # KOSDAQ stocks
            ('247540', 'Ecopro BM', 'KOSDAQ', 280000, 295000),
            ('086520', 'Ecopro', 'KOSDAQ', 580000, 600000),
            ('066970', 'L&F', 'KOSDAQ', 180000, 190000),
            ('091990', 'Celltrion Healthcare', 'KOSDAQ', 68000, 71000),
            ('214150', 'Classis', 'KOSDAQ', 45000, 47000),
        ]

        import random
        random.seed(hash(date))  # Consistent data for same date

        prices = []
        for stock_code, name, mkt, base_price, high_base in mock_stocks:
            # Skip if market filter doesn't match
            if market and market.value != mkt:
                continue

            # Generate realistic OHLCV data
            close_price = base_price * (1 + random.uniform(-0.03, 0.03))
            open_price = close_price * (1 + random.uniform(-0.02, 0.02))
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
            volume = int(random.uniform(1000000, 50000000))
            trading_value = volume * close_price
            market_cap = close_price * random.uniform(100000000, 500000000)

            prices.append(PriceData(
                stock_code=stock_code,
                trade_date=date,
                open_price=round(open_price, 2),
                high_price=round(high_price, 2),
                low_price=round(low_price, 2),
                close_price=round(close_price, 2),
                volume=volume,
                trading_value=round(trading_value, 2),
                market_cap=round(market_cap, 2),
                market=mkt
            ))

        logger.info(f"Generated {len(prices)} mock price records")
        return prices

    def fetch_market_summary(self, date: str) -> Dict[str, Any]:
        """
        Fetch market summary statistics for a date.

        Args:
            date: Trading date in YYYY-MM-DD format

        Returns:
            Dictionary with market statistics (indices, volume, etc.)
        """
        if self.use_mock:
            return {
                'date': date,
                'kospi_index': 2650.50,
                'kosdaq_index': 890.25,
                'kospi_volume': 450000000,
                'kosdaq_volume': 1200000000,
                'kospi_value': 12500000000000,
                'kosdaq_value': 8900000000000
            }

        try:
            response = self._make_request(
                endpoint='/data/market_summary',
                method='GET',
                params={'date': date}
            )
            return response.get('data', {})

        except Exception as e:
            logger.error(f"Failed to fetch market summary for {date}: {e}")
            raise

    def close(self):
        """Close the HTTP session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Utility function for easy import
def create_client(use_mock: bool = None) -> KRXAPIClient:
    """
    Create and return a KRX API client.

    Args:
        use_mock: Use mock data (None = read from environment)

    Returns:
        Configured KRXAPIClient instance

    Example:
        >>> from krx_api_client import create_client
        >>> with create_client(use_mock=True) as client:
        ...     prices = client.fetch_daily_prices("2024-01-15")
    """
    return KRXAPIClient(use_mock=use_mock)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Test with mock data
    with create_client(use_mock=True) as client:
        prices = client.fetch_daily_prices("2024-01-15")
        print(f"Fetched {len(prices)} prices")

        if prices:
            print(f"\nSample price data:")
            sample = prices[0]
            print(f"  Stock: {sample.stock_code}")
            print(f"  Date: {sample.trade_date}")
            print(f"  Close: {sample.close_price:,.0f} KRW")
            print(f"  Volume: {sample.volume:,}")
