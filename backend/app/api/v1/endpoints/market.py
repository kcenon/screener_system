"""Market overview endpoints for indices, breadth, sectors, and movers"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheManager, get_cache
from app.db.session import get_db
from app.services.market_service import MarketService

router = APIRouter(prefix="/market", tags=["market"])


def get_market_service(
    db: AsyncSession = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
) -> MarketService:
    """Dependency to get market service instance"""
    return MarketService(db, cache)


# ============================================================================
# Market Indices Endpoints
# ============================================================================


@router.get(
    "/indices",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get current market indices",
    description="""
    Get current values for all market indices (KOSPI, KOSDAQ, KRX100).

    **Features:**
    - Real-time index values with change amounts and percentages
    - High/low values for the day
    - Trading volume and value
    - Sparkline data (last 30 data points) for mini charts
    - Cached for 5 minutes

    **Response includes:**
    - `indices`: List of index objects
    - `updated_at`: Timestamp of last update
    """,
)
async def get_market_indices(
    market_service: MarketService = Depends(get_market_service),
):
    """
    Get current market indices with sparklines

    Returns KOSPI, KOSDAQ, and KRX100 with real-time values,
    change metrics, and sparkline data for visualization.
    """
    return await market_service.get_market_indices()


@router.get(
    "/trend",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get historical market trend",
    description="""
    Get historical index data for charting and analysis.

    **Query Parameters:**
    - `index`: Index code (KOSPI, KOSDAQ, KRX100)
    - `timeframe`: Time range (1D, 5D, 1M, 3M, 6M, 1Y)

    **Interval Selection** (automatic):
    - 1D, 5D: 1-minute or 5-minute intervals
    - 1M, 3M: 1-hour intervals
    - 6M, 1Y: 1-day intervals

    **Response includes:**
    - `data`: Array of OHLCV data points
    - `interval`: Automatically selected interval
    - `count`: Number of data points

    **Caching:**
    - Cached for 30 minutes (historical data changes infrequently)
    """,
)
async def get_market_trend(
    index: str = Query(
        "KOSPI",
        description="Index code",
        pattern="^(KOSPI|KOSDAQ|KRX100)$",
    ),
    timeframe: str = Query(
        "1M",
        description="Timeframe for historical data",
        pattern="^(1D|5D|1M|3M|6M|1Y)$",
    ),
    market_service: MarketService = Depends(get_market_service),
):
    """
    Get historical market trend data

    Returns OHLCV data for the specified index and timeframe,
    suitable for rendering trend charts.
    """
    return await market_service.get_market_trend(
        index=index,
        timeframe=timeframe,
    )


# ============================================================================
# Market Breadth Endpoints
# ============================================================================


@router.get(
    "/breadth",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get market breadth indicators",
    description="""
    Get market breadth indicators (advancing/declining/unchanged stocks).

    **Features:**
    - Counts of advancing, declining, and unchanged stocks
    - Advance/Decline (A/D) ratio calculation
    - Market sentiment determination (bullish/neutral/bearish)
    - Filter by market (KOSPI, KOSDAQ, or ALL)

    **Sentiment Calculation:**
    - `bullish`: A/D ratio > 1.2
    - `neutral`: 0.8 <= A/D ratio <= 1.2
    - `bearish`: A/D ratio < 0.8

    **Caching:**
    - Cached for 5 minutes
    """,
)
async def get_market_breadth(
    market: str = Query(
        "ALL",
        description="Market filter",
        pattern="^(KOSPI|KOSDAQ|ALL)$",
    ),
    market_service: MarketService = Depends(get_market_service),
):
    """
    Get market breadth indicators with sentiment analysis

    Returns advancing/declining/unchanged stock counts with
    A/D ratio and calculated sentiment for the market.
    """
    return await market_service.get_market_breadth(market=market)


# ============================================================================
# Sector Performance Endpoints
# ============================================================================


@router.get(
    "/sectors",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get sector performance",
    description="""
    Get aggregated sector performance metrics.

    **Features:**
    - Average change percentage per sector
    - Stock count in each sector
    - Total market capitalization
    - Trading volume aggregation
    - Top performing stock in each sector
    - Filter by market and timeframe

    **Timeframe Options:**
    - `1D`: 1-day performance
    - `1W`: 1-week performance
    - `1M`: 1-month performance
    - `3M`: 3-month performance

    **Sectors Included:**
    - Technology (기술)
    - Finance (금융)
    - Healthcare (헬스케어)
    - Consumer (소비재)
    - Materials (소재)
    - Industrial (산업재)
    - Energy (에너지)
    - Utilities (유틸리티)
    - Telecom (통신)
    - Real Estate (부동산)

    **Caching:**
    - Cached for 5 minutes
    """,
)
async def get_sector_performance(
    timeframe: str = Query(
        "1D",
        description="Timeframe for performance calculation",
        pattern="^(1D|1W|1M|3M)$",
    ),
    market: str = Query(
        "ALL",
        description="Market filter",
        pattern="^(KOSPI|KOSDAQ|ALL)$",
    ),
    market_service: MarketService = Depends(get_market_service),
):
    """
    Get sector performance aggregation

    Returns sector-level performance metrics including average
    change percentage, market cap, volume, and top stock.
    """
    return await market_service.get_sector_performance(
        timeframe=timeframe,
        market=market,
    )


# ============================================================================
# Market Movers Endpoints
# ============================================================================


@router.get(
    "/movers",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get top market movers",
    description="""
    Get top gaining or losing stocks.

    **Query Parameters:**
    - `type`: Type of movers (`gainers` or `losers`)
    - `market`: Market filter (KOSPI, KOSDAQ, ALL)
    - `limit`: Maximum results (1-100, default: 20)

    **Stock Information Included:**
    - Stock code and name
    - Market classification
    - Sector
    - Current price
    - Change amount and percentage
    - Trading volume and value

    **Use Cases:**
    - Identify strongest/weakest performers
    - Market momentum analysis
    - Trading opportunities

    **Caching:**
    - Cached for 5 minutes
    """,
)
async def get_market_movers(
    move_type: str = Query(
        "gainers",
        alias="type",
        description="Type of movers",
        pattern="^(gainers|losers)$",
    ),
    market: str = Query(
        "ALL",
        description="Market filter",
        pattern="^(KOSPI|KOSDAQ|ALL)$",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Maximum number of results",
    ),
    market_service: MarketService = Depends(get_market_service),
):
    """
    Get top gaining or losing stocks

    Returns a ranked list of stocks with the highest price gains
    or losses for the day, with detailed price and volume info.
    """
    return await market_service.get_market_movers(
        move_type=move_type,
        market=market,
        limit=limit,
    )


# ============================================================================
# Most Active Endpoints
# ============================================================================


@router.get(
    "/active",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get most active stocks",
    description="""
    Get stocks with highest trading volume or value.

    **Query Parameters:**
    - `metric`: Sorting metric (`volume` or `value`)
    - `market`: Market filter (KOSPI, KOSDAQ, ALL)
    - `limit`: Maximum results (1-100, default: 20)

    **Metrics:**
    - `volume`: Sort by trading volume (number of shares)
    - `value`: Sort by trading value (KRW amount)

    **Stock Information Included:**
    - Stock code and name
    - Market classification
    - Sector
    - Current price
    - Change percentage
    - Trading volume and value

    **Use Cases:**
    - Identify high-liquidity stocks
    - Market participation analysis
    - Trading opportunity discovery

    **Caching:**
    - Cached for 5 minutes
    """,
)
async def get_most_active(
    metric: str = Query(
        "volume",
        description="Sorting metric",
        pattern="^(volume|value)$",
    ),
    market: str = Query(
        "ALL",
        description="Market filter",
        pattern="^(KOSPI|KOSDAQ|ALL)$",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Maximum number of results",
    ),
    market_service: MarketService = Depends(get_market_service),
):
    """
    Get stocks with highest trading volume or value

    Returns a ranked list of most actively traded stocks
    based on volume or trading value.
    """
    return await market_service.get_most_active(
        metric=metric,
        market=market,
        limit=limit,
    )
