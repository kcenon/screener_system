"""Stock endpoints for listing, detail, prices, and financials"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheManager, get_cache
from app.db.session import get_db
from app.schemas import (DailyPrice, FinancialStatement, StockDetail,
                         StockListResponse, StockSearchResponse)
from app.services.stock_service import StockService

router = APIRouter(prefix="/stocks", tags=["stocks"])


def get_stock_service(
    db: AsyncSession = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
) -> StockService:
    """Dependency to get stock service instance"""
    return StockService(db, cache)


# ============================================================================
# Stock List and Detail Endpoints
# ============================================================================


@router.get(
    "",
    response_model=StockListResponse,
    status_code=status.HTTP_200_OK,
    summary="List stocks with pagination",
    description="""
    Get a paginated list of stocks with filtering options.

    - Filter by market (KOSPI, KOSDAQ, or ALL)
    - Filter by sector
    - Includes latest price and basic indicators
    - Cached for 5 minutes
    """,
)
async def list_stocks(
    market: Optional[str] = Query(
        None,
        description="Market filter: KOSPI, KOSDAQ, or ALL",
        pattern="^(KOSPI|KOSDAQ|ALL)$",
    ),
    sector: Optional[str] = Query(
        None,
        description="Sector filter",
        max_length=50,
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number (1-indexed)",
    ),
    per_page: int = Query(
        50,
        ge=1,
        le=100,
        description="Items per page (max 100)",
    ),
    stock_service: StockService = Depends(get_stock_service),
):
    """
    List stocks with pagination and filtering

    Returns a paginated list of stocks with basic information,
    latest closing price, and price change percentage.
    """
    return await stock_service.list_stocks(
        market=market,
        sector=sector,
        page=page,
        per_page=per_page,
    )


@router.get(
    "/search",
    response_model=StockSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search stocks",
    description="""
    Search stocks by name or code.

    - Fuzzy search by Korean name, English name, or code
    - Filter by market
    - Limit results (max 50)
    - Cached for 10 minutes
    """,
)
async def search_stocks(
    q: str = Query(
        ...,
        min_length=1,
        max_length=100,
        description="Search query (name or code)",
    ),
    market: Optional[str] = Query(
        None,
        description="Market filter: KOSPI, KOSDAQ, or ALL",
        pattern="^(KOSPI|KOSDAQ|ALL)$",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Maximum results (max 50)",
    ),
    stock_service: StockService = Depends(get_stock_service),
):
    """
    Search stocks by name or code

    Uses fuzzy matching to find stocks matching the query.
    Returns results sorted by relevance.
    """
    return await stock_service.search_stocks(
        query=q,
        market=market,
        limit=limit,
    )


@router.get(
    "/{stock_code}",
    response_model=StockDetail,
    status_code=status.HTTP_200_OK,
    summary="Get stock detail",
    description="""
    Get detailed information for a specific stock.

    - Includes basic stock information
    - Latest daily price data
    - Latest calculated indicators
    - Cached for 5 minutes
    """,
)
async def get_stock_detail(
    stock_code: str,
    stock_service: StockService = Depends(get_stock_service),
):
    """
    Get stock detail by code

    Returns complete stock information including latest price
    and calculated indicators.
    """
    return await stock_service.get_stock_by_code(stock_code)


# ============================================================================
# Price Data Endpoints
# ============================================================================


@router.get(
    "/{stock_code}/prices",
    response_model=List[DailyPrice],
    status_code=status.HTTP_200_OK,
    summary="Get price history",
    description="""
    Get historical daily price data for a stock.

    - Filter by date range
    - Limit number of records (max 1000)
    - Ordered by date descending (latest first)
    - Cached for 30 minutes
    """,
)
async def get_price_history(
    stock_code: str,
    from_date: Optional[date] = Query(
        None,
        description="Start date (YYYY-MM-DD)",
    ),
    to_date: Optional[date] = Query(
        None,
        description="End date (YYYY-MM-DD)",
    ),
    limit: int = Query(
        365,
        ge=1,
        le=1000,
        description="Maximum records (max 1000)",
    ),
    stock_service: StockService = Depends(get_stock_service),
):
    """
    Get price history for a stock

    Returns daily OHLCV data within the specified date range.
    If no date range is specified, returns the most recent data.
    """
    return await stock_service.get_price_history(
        stock_code=stock_code,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )


# ============================================================================
# Financial Statement Endpoints
# ============================================================================


@router.get(
    "/{stock_code}/financials",
    response_model=List[FinancialStatement],
    status_code=status.HTTP_200_OK,
    summary="Get financial statements",
    description="""
    Get financial statements for a stock.

    - Filter by period type (quarterly or annual)
    - Specify number of years (max 10)
    - Includes income statement, balance sheet, and cash flow
    - Cached for 1 day
    """,
)
async def get_financials(
    stock_code: str,
    period_type: Optional[str] = Query(
        None,
        description="Period type: quarterly or annual",
        pattern="^(quarterly|annual)$",
    ),
    years: int = Query(
        5,
        ge=1,
        le=10,
        description="Number of years (max 10)",
    ),
    stock_service: StockService = Depends(get_stock_service),
):
    """
    Get financial statements for a stock

    Returns quarterly or annual financial statements including
    income statement, balance sheet, and cash flow data.
    """
    return await stock_service.get_financials(
        stock_code=stock_code,
        period_type=period_type,
        years=years,
    )
