"""Stock service layer for business logic and caching.

This module provides the StockService class that implements business logic
for stock-related operations with intelligent caching strategies.

The service layer acts as an intermediary between API endpoints and the
data access layer (repositories), providing:
    - Data transformation and validation
    - Caching logic with appropriate TTLs
    - Business logic orchestration
    - Error handling and exception translation

Example:
    Initialize the service with a database session and cache manager::

        from app.services import StockService
        from app.core.cache import cache_manager
        from app.db import get_session

        async with get_session() as session:
            service = StockService(session, cache_manager)
            stock = await service.get_stock_by_code("005930")
            print(f"{stock.name}: {stock.latest_price.close_price:,} KRW")
"""

from datetime import date
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheManager
from app.core.exceptions import NotFoundException
from app.repositories import StockRepository
from app.schemas import (CalculatedIndicator, DailyPrice, FinancialStatement,
                         PaginationMeta, StockDetail, StockListItem,
                         StockListResponse, StockSearchResponse,
                         StockSearchResult)


class StockService:
    """Service for stock operations with intelligent caching strategies.

    This class implements business logic for stock-related operations including
    listing, searching, retrieving details, and accessing historical data.
    All operations are cached with appropriate TTLs to optimize performance.

    Attributes:
        STOCK_DETAIL_TTL: Cache TTL for stock details (5 minutes).
        STOCK_LIST_TTL: Cache TTL for stock listings (5 minutes).
        PRICE_DATA_TTL: Cache TTL for price history (30 minutes).
        FINANCIAL_TTL: Cache TTL for financial statements (1 day).
        SEARCH_TTL: Cache TTL for search results (10 minutes).
        session: Async SQLAlchemy session for database operations.
        cache: Cache manager instance for Redis operations.
        stock_repo: Stock repository for data access.

    Example:
        >>> service = StockService(session, cache_manager)
        >>> stocks = await service.list_stocks(market="KOSPI", page=1)
        >>> print(f"Found {stocks.meta.total} stocks")
    """

    # Cache TTL (seconds)
    STOCK_DETAIL_TTL = 5 * 60  # 5 minutes
    STOCK_LIST_TTL = 5 * 60  # 5 minutes
    PRICE_DATA_TTL = 30 * 60  # 30 minutes
    FINANCIAL_TTL = 24 * 60 * 60  # 1 day
    SEARCH_TTL = 10 * 60  # 10 minutes

    def __init__(self, session: AsyncSession, cache: CacheManager):
        """Initialize service with database session and cache manager.

        Args:
            session: Async SQLAlchemy session for database operations.
            cache: CacheManager instance for Redis caching operations.
        """
        self.session = session
        self.cache = cache
        self.stock_repo = StockRepository(session)

    # ========================================================================
    # Stock Operations
    # ========================================================================

    async def list_stocks(
        self,
        market: Optional[str] = None,
        sector: Optional[str] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> StockListResponse:
        """
        List stocks with pagination and caching

        Args:
            market: Market filter (KOSPI, KOSDAQ, or ALL)
            sector: Sector filter
            page: Page number (1-indexed)
            per_page: Items per page (1-100)

        Returns:
            StockListResponse with items and pagination metadata
        """
        # Validate pagination
        page = max(1, page)
        per_page = min(100, max(1, per_page))
        offset = (page - 1) * per_page

        # Check cache
        cache_key = f"stocks:list:{market}:{sector}:{page}:{per_page}"
        cached = await self.cache.get(cache_key)
        if cached:
            return StockListResponse(**cached)

        # Get from repository
        stocks_data, total = await self.stock_repo.list_stocks_with_latest_price(
            market=market, sector=sector, offset=offset, limit=per_page
        )

        # Transform to list items
        items = []
        for stock, latest_price, latest_indicators in stocks_data:
            items.append(
                StockListItem(
                    code=stock.code,
                    name=stock.name,
                    market=stock.market,
                    sector=stock.sector,
                    latest_close=latest_price.close_price if latest_price else None,
                    price_change_1d=(
                        latest_indicators.price_change_1d if latest_indicators else None
                    ),
                    volume=latest_price.volume if latest_price else None,
                    market_cap=latest_price.market_cap if latest_price else None,
                )
            )

        # Calculate pagination metadata
        total_pages = (total + per_page - 1) // per_page
        meta = PaginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

        # Create response
        response = StockListResponse(items=items, meta=meta)

        # Cache result
        await self.cache.set(cache_key, response.model_dump(), ttl=self.STOCK_LIST_TTL)

        return response

    async def get_stock_by_code(self, stock_code: str) -> StockDetail:
        """Get comprehensive stock details by stock code with caching.

        Retrieves detailed stock information including basic info, latest price data,
        and calculated technical indicators. Results are cached for 5 minutes to
        improve performance and reduce database load.

        Args:
            stock_code: 6-digit Korean stock code
            (e.g., "005930" for Samsung Electronics).

        Returns:
            StockDetail: Comprehensive stock information containing:
                - Basic info: code, name, market, sector, industry
                - Latest price: OHLCV data with timestamps
                - Latest indicators: 200+ technical and financial indicators
                - Company info: shares outstanding, listing date, etc.

        Raises:
            NotFoundException: If the stock code does not exist in the database.
            ValidationError: If the stock code format is invalid
            (implicit via Pydantic).

        Note:
            This method uses Redis cache with key format: `stock:detail:{stock_code}`
            Cache TTL is 5 minutes (STOCK_DETAIL_TTL).

        Example:
            >>> service = StockService(session, cache)
            >>> detail = await service.get_stock_by_code("005930")
            >>> print(f"{detail.name}: {detail.latest_price.close_price:,} KRW")
            Samsung Electronics: 71,000 KRW
            >>> print(f"P/E Ratio: {detail.latest_indicators.per:.2f}")
            P/E Ratio: 15.23
        """
        # Check cache
        cache_key = f"stock:detail:{stock_code}"
        cached = await self.cache.get(cache_key)
        if cached:
            return StockDetail(**cached)

        # Get from repository
        result = await self.stock_repo.get_by_code_with_latest(stock_code)
        if not result:
            raise NotFoundException(f"Stock {stock_code} not found")

        stock, latest_price, latest_indicators = result

        # Transform to detail schema
        detail = StockDetail(
            code=stock.code,
            name=stock.name,
            name_english=stock.name_english,
            market=stock.market,
            sector=stock.sector,
            industry=stock.industry,
            listing_date=stock.listing_date,
            delisting_date=stock.delisting_date,
            shares_outstanding=stock.shares_outstanding,
            created_at=stock.created_at,
            updated_at=stock.updated_at,
            latest_price=(
                DailyPrice.model_validate(latest_price) if latest_price else None
            ),
            latest_indicators=(
                CalculatedIndicator.model_validate(latest_indicators)
                if latest_indicators
                else None
            ),
        )

        # Cache result
        await self.cache.set(cache_key, detail.model_dump(), ttl=self.STOCK_DETAIL_TTL)

        return detail

    async def search_stocks(
        self, query: str, market: Optional[str] = None, limit: int = 10
    ) -> StockSearchResponse:
        """
        Search stocks by name with caching

        Args:
            query: Search query string
            market: Market filter (KOSPI, KOSDAQ, or ALL)
            limit: Maximum results (1-50)

        Returns:
            StockSearchResponse with matching stocks
        """
        # Validate limit
        limit = min(50, max(1, limit))

        # Check cache
        cache_key = f"stocks:search:{query}:{market}:{limit}"
        cached = await self.cache.get(cache_key)
        if cached:
            return StockSearchResponse(**cached)

        # Search from repository
        stocks = await self.stock_repo.search_stocks(query, market, limit)

        # Transform to search results
        # TODO: Add similarity calculation when pg_trgm is enabled
        items = [
            StockSearchResult(
                code=stock.code,
                name=stock.name,
                name_english=stock.name_english,
                market=stock.market,
                sector=stock.sector,
                similarity=1.0,  # Placeholder
            )
            for stock in stocks
        ]

        # Create response
        response = StockSearchResponse(
            items=items,
            query=query,
            total=len(items),
        )

        # Cache result
        await self.cache.set(cache_key, response.model_dump(), ttl=self.SEARCH_TTL)

        return response

    # ========================================================================
    # Price Data Operations
    # ========================================================================

    async def get_price_history(
        self,
        stock_code: str,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 365,
    ) -> List[DailyPrice]:
        """
        Get price history with caching

        Args:
            stock_code: 6-digit stock code
            from_date: Start date (optional)
            to_date: End date (optional)
            limit: Maximum records (1-1000)

        Returns:
            List of DailyPrice

        Raises:
            NotFoundException: If stock not found
        """
        # Check if stock exists
        exists = await self.stock_repo.exists_by_code(stock_code)
        if not exists:
            raise NotFoundException(f"Stock {stock_code} not found")

        # Validate limit
        limit = min(1000, max(1, limit))

        # Check cache
        cache_key = f"stock:prices:{stock_code}:{from_date}:{to_date}:{limit}"
        cached = await self.cache.get(cache_key)
        if cached:
            return [DailyPrice(**item) for item in cached]

        # Get from repository
        prices = await self.stock_repo.get_price_history(
            stock_code, from_date, to_date, limit
        )

        # Transform to schemas
        price_schemas = [DailyPrice.model_validate(price) for price in prices]

        # Cache result
        await self.cache.set(
            cache_key,
            [price.model_dump() for price in price_schemas],
            ttl=self.PRICE_DATA_TTL,
        )

        return price_schemas

    # ========================================================================
    # Financial Statement Operations
    # ========================================================================

    async def get_financials(
        self,
        stock_code: str,
        period_type: Optional[str] = None,
        years: int = 5,
    ) -> List[FinancialStatement]:
        """
        Get financial statements with caching

        Args:
            stock_code: 6-digit stock code
            period_type: "quarterly" or "annual" (optional)
            years: Number of years (1-10)

        Returns:
            List of FinancialStatement

        Raises:
            NotFoundException: If stock not found
        """
        # Check if stock exists
        exists = await self.stock_repo.exists_by_code(stock_code)
        if not exists:
            raise NotFoundException(f"Stock {stock_code} not found")

        # Validate years
        years = min(10, max(1, years))

        # Check cache
        cache_key = f"stock:financials:{stock_code}:{period_type}:{years}"
        cached = await self.cache.get(cache_key)
        if cached:
            return [FinancialStatement(**item) for item in cached]

        # Get from repository
        financials = await self.stock_repo.get_financials(
            stock_code, period_type, years
        )

        # Transform to schemas
        financial_schemas = [
            FinancialStatement.model_validate(fin) for fin in financials
        ]

        # Cache result
        await self.cache.set(
            cache_key,
            [fin.model_dump() for fin in financial_schemas],
            ttl=self.FINANCIAL_TTL,
        )

        return financial_schemas

    # ========================================================================
    # Cache Management
    # ========================================================================

    async def invalidate_stock_cache(self, stock_code: str) -> None:
        """
        Invalidate all cache entries for a specific stock

        Args:
            stock_code: 6-digit stock code
        """
        patterns = [
            f"stock:detail:{stock_code}",
            f"stock:prices:{stock_code}:*",
            f"stock:financials:{stock_code}:*",
        ]

        for pattern in patterns:
            await self.cache.clear(pattern)

    async def invalidate_list_cache(self) -> None:
        """Invalidate stock list cache"""
        await self.cache.clear("stocks:list:*")
