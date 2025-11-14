"""Market overview endpoints for indices, sectors, and market analysis"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheManager, get_cache
from app.db.session import get_db
from app.schemas.market import (
    MarketBreadthResponse,
    MarketIndicesResponse,
    MarketMoversResponse,
    MarketTrendResponse,
    MostActiveResponse,
    SectorPerformanceResponse,
)
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
    response_model=MarketIndicesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get market indices",
    description="""
    Get current market indices (KOSPI, KOSDAQ, KRX100) with real-time data.

    - Current value, change, and change percentage
    - High, low, volume, and trading value
    - Sparkline data (last 30 data points)
    - Cached for 5 minutes
    """,
)
async def get_market_indices(
    market_service: MarketService = Depends(get_market_service),
):
    """
    Get current market indices

    Returns real-time data for KOSPI, KOSDAQ, and KRX100 indices
    including sparkline data for visualization.
    """
    return await market_service.get_market_indices()


# ============================================================================
# Market Breadth Endpoints
# ============================================================================


@router.get(
    "/breadth",
    response_model=MarketBreadthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get market breadth indicators",
    description="""
    Get market breadth indicators including advancing/declining stocks.

    - Advancing, declining, and unchanged stock counts
    - Advance/Decline ratio
    - Market sentiment (bullish, neutral, bearish)
    - Filter by market (KOSPI, KOSDAQ, ALL)
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
    Get market breadth indicators

    Returns advancing, declining, and unchanged stock counts
    with A/D ratio and sentiment indicator.
    """
    return await market_service.get_market_breadth(market)


# ============================================================================
# Sector Performance Endpoints
# ============================================================================


@router.get(
    "/sectors",
    response_model=SectorPerformanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get sector performance",
    description="""
    Get aggregated sector performance data.

    - Average change percentage per sector
    - Stock count and market cap
    - Top performing stock in each sector
    - Filter by market and timeframe
    - Cached for 5 minutes
    """,
)
async def get_sector_performance(
    timeframe: str = Query(
        "1D",
        description="Time period",
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
    Get sector performance aggregated by sector

    Returns sector-level statistics including average change percentage,
    market cap, and top performing stock.
    """
    return await market_service.get_sector_performance(timeframe, market)


# ============================================================================
# Market Movers Endpoints
# ============================================================================


@router.get(
    "/movers",
    response_model=MarketMoversResponse,
    status_code=status.HTTP_200_OK,
    summary="Get top market movers",
    description="""
    Get top gaining or losing stocks.

    - Top gainers or losers across markets
    - Stock code, name, price, and change percentage
    - Filter by market
    - Limit results (max 100)
    - Cached for 5 minutes
    """,
)
async def get_market_movers(
    type: str = Query(
        ...,
        description="Mover type",
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
        description="Number of results (max 100)",
    ),
    market_service: MarketService = Depends(get_market_service),
):
    """
    Get top gaining or losing stocks

    Returns a list of stocks with the highest gains or losses,
    including price, change, volume, and sector information.
    """
    return await market_service.get_market_movers(type, market, limit)


# ============================================================================
# Most Active Stocks Endpoints
# ============================================================================


@router.get(
    "/active",
    response_model=MostActiveResponse,
    status_code=status.HTTP_200_OK,
    summary="Get most active stocks",
    description="""
    Get stocks with highest trading volume or value.

    - Stocks sorted by volume or trading value
    - Stock code, name, price, and trading metrics
    - Filter by market
    - Limit results (max 100)
    - Cached for 5 minutes
    """,
)
async def get_most_active(
    metric: str = Query(
        "volume",
        description="Activity metric",
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
        description="Number of results (max 100)",
    ),
    market_service: MarketService = Depends(get_market_service),
):
    """
    Get stocks with highest volume or trading value

    Returns a list of most actively traded stocks,
    sorted by volume or trading value.
    """
    return await market_service.get_most_active(metric, market, limit)


# ============================================================================
# Market Trend Endpoints
# ============================================================================


@router.get(
    "/trend",
    response_model=MarketTrendResponse,
    status_code=status.HTTP_200_OK,
    summary="Get market trend data",
    description="""
    Get historical market trend data for charting.

    - Historical OHLCV data for market indices
    - Support for multiple timeframes (1D to 1Y)
    - Automatic interval selection
    - Cached for 30 minutes
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
        description="Time period",
        pattern="^(1D|5D|1M|3M|6M|1Y)$",
    ),
    market_service: MarketService = Depends(get_market_service),
):
    """
    Get historical market trend data

    Returns OHLCV data for the specified index and timeframe,
    with automatic interval selection for optimal charting.
    """
    return await market_service.get_market_trend(index, timeframe)
