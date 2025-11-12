"""
Data Pipeline Scripts Package

This package contains utility modules for the data ingestion pipeline:
- krx_api_client: KRX (Korea Exchange) API client
- kis_api_client: KIS (Korea Investment & Securities) API client
- data_source: Abstract data source layer for multiple providers

Usage:
    from scripts.krx_api_client import create_client, PriceData
    from scripts.kis_api_client import KISAPIClient
    from scripts.data_source import DataSourceFactory
"""

__version__ = "1.0.0"

# Export commonly used classes and functions
from .krx_api_client import (
    KRXAPIClient,
    create_client,
    PriceData,
    Market
)

from .kis_api_client import (
    KISAPIClient,
    PriceType
)

from .data_source import (
    DataSourceFactory,
    DataSourceType,
    ChartData
)

__all__ = [
    # KRX exports
    'KRXAPIClient',
    'create_client',
    'PriceData',
    'Market',
    # KIS exports
    'KISAPIClient',
    'PriceType',
    # Data source exports
    'DataSourceFactory',
    'DataSourceType',
    'ChartData',
]
