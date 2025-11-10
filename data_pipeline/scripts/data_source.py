"""
Data Source Abstraction Layer

This module provides an abstraction layer for stock market data sources.
Allows seamless switching between different data providers (KIS API, KRX API, Mock data).

Features:
- Abstract interface for data sources
- KIS API data source implementation
- Mock data source for testing
- Factory pattern for easy instantiation

Usage:
    # Create data source from configuration
    data_source = DataSourceFactory.create()

    # Fetch current price
    price = data_source.get_current_price("005930")

    # Fetch order book
    orderbook = data_source.get_order_book("005930")
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from enum import Enum

# Import data models and clients
from kis_api_client import (
    KISAPIClient,
    CurrentPrice,
    OrderBook,
    ChartData,
    StockInfo,
    PriceType
)

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Enumerations
# ============================================================================

class DataSourceType(Enum):
    """Data source types"""
    KIS = "kis"       # Korea Investment & Securities
    KRX = "krx"       # Korea Exchange
    MOCK = "mock"     # Mock data for testing


# ============================================================================
# Abstract Data Source Interface
# ============================================================================

class AbstractDataSource(ABC):
    """
    Abstract interface for stock market data sources.

    All data source implementations must implement these methods.
    """

    @abstractmethod
    def get_current_price(self, stock_code: str) -> CurrentPrice:
        """
        Get current price for a stock.

        Args:
            stock_code: 6-digit stock code

        Returns:
            CurrentPrice object
        """
        pass

    @abstractmethod
    def get_order_book(self, stock_code: str) -> OrderBook:
        """
        Get order book with depth.

        Args:
            stock_code: 6-digit stock code

        Returns:
            OrderBook object
        """
        pass

    @abstractmethod
    def get_chart_data(
        self,
        stock_code: str,
        period: PriceType = PriceType.DAILY,
        count: int = 100
    ) -> List[ChartData]:
        """
        Get chart data (OHLCV).

        Args:
            stock_code: 6-digit stock code
            period: Price type (DAILY, WEEKLY, etc.)
            count: Number of data points

        Returns:
            List of ChartData objects
        """
        pass

    @abstractmethod
    def get_stock_info(self, stock_code: str) -> StockInfo:
        """
        Get stock information.

        Args:
            stock_code: 6-digit stock code

        Returns:
            StockInfo object
        """
        pass

    @abstractmethod
    def close(self):
        """Clean up resources"""
        pass


# ============================================================================
# KIS Data Source Implementation
# ============================================================================

class KISDataSource(AbstractDataSource):
    """
    Data source implementation using KIS API.

    This is a wrapper around KISAPIClient that implements
    the AbstractDataSource interface.
    """

    def __init__(
        self,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        use_virtual: bool = True
    ):
        """
        Initialize KIS data source.

        Args:
            app_key: KIS API app key
            app_secret: KIS API app secret
            use_virtual: Use virtual server for testing
        """
        self.client = KISAPIClient(
            app_key=app_key,
            app_secret=app_secret,
            use_virtual=use_virtual,
            use_mock=False
        )
        logger.info("KIS data source initialized")

    def get_current_price(self, stock_code: str) -> CurrentPrice:
        """Get current price from KIS API"""
        return self.client.get_current_price(stock_code)

    def get_order_book(self, stock_code: str) -> OrderBook:
        """Get order book from KIS API"""
        return self.client.get_order_book(stock_code)

    def get_chart_data(
        self,
        stock_code: str,
        period: PriceType = PriceType.DAILY,
        count: int = 100
    ) -> List[ChartData]:
        """Get chart data from KIS API"""
        return self.client.get_chart_data(stock_code, period, count)

    def get_stock_info(self, stock_code: str) -> StockInfo:
        """Get stock info from KIS API"""
        return self.client.get_stock_info(stock_code)

    def close(self):
        """Close KIS API client"""
        self.client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# ============================================================================
# Mock Data Source Implementation
# ============================================================================

class MockDataSource(AbstractDataSource):
    """
    Mock data source for development and testing.

    Uses KISAPIClient's mock data functionality.
    """

    def __init__(self):
        """Initialize mock data source"""
        self.client = KISAPIClient(use_mock=True)
        logger.info("Mock data source initialized")

    def get_current_price(self, stock_code: str) -> CurrentPrice:
        """Get mock current price"""
        return self.client.get_current_price(stock_code)

    def get_order_book(self, stock_code: str) -> OrderBook:
        """Get mock order book"""
        return self.client.get_order_book(stock_code)

    def get_chart_data(
        self,
        stock_code: str,
        period: PriceType = PriceType.DAILY,
        count: int = 100
    ) -> List[ChartData]:
        """Get mock chart data"""
        return self.client.get_chart_data(stock_code, period, count)

    def get_stock_info(self, stock_code: str) -> StockInfo:
        """Get mock stock info"""
        return self.client.get_stock_info(stock_code)

    def close(self):
        """Close mock client"""
        self.client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# ============================================================================
# Data Source Factory
# ============================================================================

class DataSourceFactory:
    """
    Factory for creating data source instances.

    Automatically selects data source based on environment configuration.
    """

    @staticmethod
    def create(source_type: Optional[DataSourceType] = None) -> AbstractDataSource:
        """
        Create data source instance.

        Args:
            source_type: Type of data source (None = auto-detect from env)

        Returns:
            AbstractDataSource implementation

        Raises:
            ValueError: If data source type is unsupported

        Example:
            ```python
            # Auto-detect from environment
            data_source = DataSourceFactory.create()

            # Explicit type
            data_source = DataSourceFactory.create(DataSourceType.KIS)

            # Use with context manager
            with DataSourceFactory.create() as source:
                price = source.get_current_price("005930")
            ```
        """
        # Auto-detect source type from environment if not specified
        if source_type is None:
            source_type = DataSourceFactory._detect_source_type()

        logger.info(f"Creating data source: {source_type.value}")

        if source_type == DataSourceType.KIS:
            # Check if KIS credentials are available
            app_key = os.getenv('KIS_APP_KEY')
            app_secret = os.getenv('KIS_APP_SECRET')

            if not app_key or not app_secret:
                logger.warning(
                    "KIS credentials not found. Falling back to mock data."
                )
                return MockDataSource()

            use_virtual = os.getenv('KIS_USE_VIRTUAL_SERVER', 'true').lower() == 'true'
            return KISDataSource(
                app_key=app_key,
                app_secret=app_secret,
                use_virtual=use_virtual
            )

        elif source_type == DataSourceType.MOCK:
            return MockDataSource()

        elif source_type == DataSourceType.KRX:
            # KRX implementation would go here
            raise NotImplementedError(
                "KRX data source not yet implemented. Use KIS or MOCK."
            )

        else:
            raise ValueError(f"Unsupported data source type: {source_type}")

    @staticmethod
    def _detect_source_type() -> DataSourceType:
        """
        Auto-detect data source type from environment.

        Checks environment variables to determine which data source to use.

        Returns:
            DataSourceType enum value
        """
        # Check if explicitly set in environment
        env_source = os.getenv('DATA_SOURCE_TYPE', '').lower()

        if env_source == 'kis':
            return DataSourceType.KIS
        elif env_source == 'krx':
            return DataSourceType.KRX
        elif env_source == 'mock':
            return DataSourceType.MOCK

        # Auto-detect based on available credentials
        kis_app_key = os.getenv('KIS_APP_KEY')
        kis_app_secret = os.getenv('KIS_APP_SECRET')

        if kis_app_key and kis_app_secret:
            logger.info("KIS credentials found - using KIS data source")
            return DataSourceType.KIS

        # Default to mock if no credentials found
        logger.info("No credentials found - using mock data source")
        return DataSourceType.MOCK


# ============================================================================
# Convenience Functions
# ============================================================================

def create_data_source(source_type: Optional[DataSourceType] = None) -> AbstractDataSource:
    """
    Convenience function to create data source.

    Args:
        source_type: Type of data source (None = auto-detect)

    Returns:
        AbstractDataSource implementation

    Example:
        ```python
        from data_source import create_data_source

        with create_data_source() as source:
            price = source.get_current_price("005930")
            print(f"Price: {price.current_price:,} KRW")
        ```
    """
    return DataSourceFactory.create(source_type)


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 80)
    print("Testing Data Source Abstraction Layer")
    print("=" * 80)

    # Test with mock data source
    print("\n1. Testing MockDataSource")
    print("-" * 80)
    with create_data_source(DataSourceType.MOCK) as source:
        print(f"Data source type: {type(source).__name__}")

        # Test current price
        price = source.get_current_price("005930")
        print(f"\nCurrent Price:")
        print(f"  {price.stock_name}: {price.current_price:,.0f} KRW")
        print(f"  Change: {price.change_price:+,.0f} ({price.change_rate:+.2f}%)")

        # Test order book
        orderbook = source.get_order_book("005930")
        print(f"\nOrder Book:")
        print(f"  Best Ask: {orderbook.best_ask:,.0f} KRW")
        print(f"  Best Bid: {orderbook.best_bid:,.0f} KRW")
        print(f"  Spread: {orderbook.spread:,.0f} KRW")

        # Test chart data
        chart = source.get_chart_data("005930", PriceType.DAILY, 3)
        print(f"\nChart Data (Last 3 days):")
        for candle in chart:
            print(f"  {candle.date}: Close={candle.close_price:,.0f} "
                  f"Volume={candle.volume:,}")

        # Test stock info
        info = source.get_stock_info("005930")
        print(f"\nStock Info:")
        print(f"  Name: {info.stock_name}")
        print(f"  Market: {info.market}")
        print(f"  Sector: {info.sector}")

    # Test with auto-detection
    print("\n2. Testing Auto-Detection")
    print("-" * 80)
    with create_data_source() as source:
        print(f"Auto-detected data source: {type(source).__name__}")

        price = source.get_current_price("000660")
        print(f"\n{price.stock_name}: {price.current_price:,.0f} KRW")

    print("\n" + "=" * 80)
    print("All tests completed successfully!")
    print("=" * 80)
