"""Market service layer for market overview business logic and caching"""

from datetime import datetime, timedelta
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheManager
from app.repositories.market_repository import MarketRepository
from app.schemas.market import (
    ActiveStock,
    MarketBreadthResponse,
    MarketIndexData,
    MarketIndicesResponse,
    MarketMover,
    MarketMoversResponse,
    MarketTrendData,
    MarketTrendResponse,
    MostActiveResponse,
    SectorPerformance,
    SectorPerformanceResponse,
    TopStock,
)


class MarketService:
    """Service for market overview operations with caching"""

    # Cache TTL (seconds)
    MARKET_INDEX_TTL = 5 * 60  # 5 minutes (real-time data)
    MARKET_BREADTH_TTL = 5 * 60  # 5 minutes
    SECTOR_PERFORMANCE_TTL = 5 * 60  # 5 minutes
    MARKET_MOVERS_TTL = 5 * 60  # 5 minutes
    MOST_ACTIVE_TTL = 5 * 60  # 5 minutes
    MARKET_TREND_TTL = 30 * 60  # 30 minutes (historical data)

    # Index name mapping
    INDEX_NAMES = {
        "KOSPI": "코스피",
        "KOSDAQ": "코스닥",
        "KRX100": "KRX 100",
    }

    def __init__(self, session: AsyncSession, cache: CacheManager):
        """Initialize service with database session and cache manager"""
        self.session = session
        self.cache = cache
        self.market_repo = MarketRepository(session)

    # ========================================================================
    # Market Indices Operations
    # ========================================================================

    async def get_market_indices(self) -> MarketIndicesResponse:
        """
        Get current market indices with sparkline data

        Returns:
            MarketIndicesResponse with KOSPI, KOSDAQ, KRX100 data
        """
        cache_key = "market:indices:current"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return MarketIndicesResponse(**cached)

        # Fetch from database
        indices_data = await self.market_repo.get_current_indices()

        # Transform to response schema
        indices_list = []
        for market_index, sparkline in indices_data:
            indices_list.append(
                MarketIndexData(
                    code=market_index.code,
                    name=self.INDEX_NAMES.get(market_index.code, market_index.code),
                    current=float(market_index.close_value),
                    change=float(market_index.change_value)
                    if market_index.change_value
                    else None,
                    change_percent=float(market_index.change_percent)
                    if market_index.change_percent
                    else None,
                    high=float(market_index.high_value)
                    if market_index.high_value
                    else None,
                    low=float(market_index.low_value)
                    if market_index.low_value
                    else None,
                    volume=market_index.volume,
                    value=market_index.trading_value,
                    timestamp=market_index.timestamp,
                    sparkline=sparkline,
                )
            )

        response = MarketIndicesResponse(
            indices=indices_list,
            updated_at=datetime.now(),
        )

        # Cache the result
        await self.cache.set(
            cache_key,
            response.model_dump(),
            ttl=self.MARKET_INDEX_TTL,
        )

        return response

    # ========================================================================
    # Market Breadth Operations
    # ========================================================================

    async def get_market_breadth(self, market: str = "ALL") -> MarketBreadthResponse:
        """
        Get market breadth indicators

        Args:
            market: Market filter (KOSPI, KOSDAQ, ALL)

        Returns:
            MarketBreadthResponse with advancing/declining counts
        """
        cache_key = f"market:breadth:{market}"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return MarketBreadthResponse(**cached)

        # Fetch from database
        breadth_data = await self.market_repo.get_market_breadth(market)

        # Calculate sentiment
        sentiment = self._calculate_sentiment(breadth_data["ad_ratio"])

        response = MarketBreadthResponse(
            advancing=breadth_data["advancing"],
            declining=breadth_data["declining"],
            unchanged=breadth_data["unchanged"],
            total=breadth_data["total"],
            ad_ratio=breadth_data["ad_ratio"],
            sentiment=sentiment,
            market=market,
            timestamp=datetime.now(),
        )

        # Cache the result
        await self.cache.set(
            cache_key,
            response.model_dump(),
            ttl=self.MARKET_BREADTH_TTL,
        )

        return response

    def _calculate_sentiment(self, ad_ratio: float) -> str:
        """
        Calculate market sentiment from A/D ratio

        Args:
            ad_ratio: Advance/Decline ratio

        Returns:
            Sentiment string (bullish, neutral, bearish)
        """
        if ad_ratio > 1.2:
            return "bullish"
        elif ad_ratio < 0.8:
            return "bearish"
        return "neutral"

    # ========================================================================
    # Sector Performance Operations
    # ========================================================================

    async def get_sector_performance(
        self,
        timeframe: str = "1D",
        market: str = "ALL",
    ) -> SectorPerformanceResponse:
        """
        Get sector performance aggregated by sector

        Args:
            timeframe: Time period (1D, 1W, 1M, 3M)
            market: Market filter (KOSPI, KOSDAQ, ALL)

        Returns:
            SectorPerformanceResponse with sector data
        """
        cache_key = f"market:sectors:{timeframe}:{market}"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return SectorPerformanceResponse(**cached)

        # Fetch from database
        sectors_data = await self.market_repo.get_sector_performance(market, timeframe)

        # Transform to response schema
        sectors_list = []
        for sector in sectors_data:
            top_stock = None
            if sector.get("top_stock") and sector["top_stock"]["code"]:
                top_stock = TopStock(
                    code=sector["top_stock"]["code"],
                    name=sector["top_stock"]["name"],
                    change_percent=None,  # Can be added if needed
                )

            sectors_list.append(
                SectorPerformance(
                    code=sector["code"],
                    name=sector["name"],
                    change_percent=sector["change_percent"],
                    stock_count=sector["stock_count"],
                    market_cap=sector["market_cap"],
                    volume=None,  # Can be added if needed
                    top_stock=top_stock,
                )
            )

        response = SectorPerformanceResponse(
            sectors=sectors_list,
            timeframe=timeframe,
            market=market,
            updated_at=datetime.now(),
        )

        # Cache the result
        await self.cache.set(
            cache_key,
            response.model_dump(),
            ttl=self.SECTOR_PERFORMANCE_TTL,
        )

        return response

    # ========================================================================
    # Market Movers Operations
    # ========================================================================

    async def get_market_movers(
        self,
        mover_type: str,
        market: str = "ALL",
        limit: int = 20,
    ) -> MarketMoversResponse:
        """
        Get top gaining or losing stocks

        Args:
            mover_type: 'gainers' or 'losers'
            market: Market filter (KOSPI, KOSDAQ, ALL)
            limit: Number of results

        Returns:
            MarketMoversResponse with top movers
        """
        cache_key = f"market:movers:{mover_type}:{market}:{limit}"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return MarketMoversResponse(**cached)

        # Fetch from database
        movers_data = await self.market_repo.get_top_movers(mover_type, market, limit)

        # Transform to response schema
        movers_list = []
        for stock, price_data, change_pct in movers_data:
            # Calculate change value
            prev_close = int(price_data.close_price / (1 + change_pct / 100))
            change_value = price_data.close_price - prev_close

            movers_list.append(
                MarketMover(
                    code=stock.code,
                    name=stock.name,
                    market=stock.market,
                    current_price=price_data.close_price,
                    change=change_value,
                    change_percent=round(change_pct, 2),
                    volume=price_data.volume,
                    value=price_data.trading_value,
                    sector=stock.sector,
                )
            )

        response = MarketMoversResponse(
            type=mover_type,
            market=market,
            stocks=movers_list,
            total=len(movers_list),
            updated_at=datetime.now(),
        )

        # Cache the result
        await self.cache.set(
            cache_key,
            response.model_dump(),
            ttl=self.MARKET_MOVERS_TTL,
        )

        return response

    # ========================================================================
    # Most Active Stocks Operations
    # ========================================================================

    async def get_most_active(
        self,
        metric: str,
        market: str = "ALL",
        limit: int = 20,
    ) -> MostActiveResponse:
        """
        Get stocks with highest volume or trading value

        Args:
            metric: 'volume' or 'value'
            market: Market filter (KOSPI, KOSDAQ, ALL)
            limit: Number of results

        Returns:
            MostActiveResponse with most active stocks
        """
        cache_key = f"market:active:{metric}:{market}:{limit}"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return MostActiveResponse(**cached)

        # Fetch from database
        active_data = await self.market_repo.get_most_active(metric, market, limit)

        # Transform to response schema
        active_list = []
        for stock, price_data in active_data:
            active_list.append(
                ActiveStock(
                    code=stock.code,
                    name=stock.name,
                    market=stock.market,
                    current_price=price_data.close_price,
                    change_percent=None,  # Can be calculated if needed
                    volume=price_data.volume,
                    value=price_data.trading_value,
                    sector=stock.sector,
                )
            )

        response = MostActiveResponse(
            metric=metric,
            market=market,
            stocks=active_list,
            total=len(active_list),
            updated_at=datetime.now(),
        )

        # Cache the result
        await self.cache.set(
            cache_key,
            response.model_dump(),
            ttl=self.MOST_ACTIVE_TTL,
        )

        return response

    # ========================================================================
    # Market Trend Operations
    # ========================================================================

    async def get_market_trend(
        self,
        index: str = "KOSPI",
        timeframe: str = "1M",
    ) -> MarketTrendResponse:
        """
        Get historical market trend data

        Args:
            index: Index code (KOSPI, KOSDAQ, KRX100)
            timeframe: Time period (1D, 5D, 1M, 3M, 6M, 1Y)

        Returns:
            MarketTrendResponse with historical data
        """
        cache_key = f"market:trend:{index}:{timeframe}"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return MarketTrendResponse(**cached)

        # Calculate date range
        end_date = datetime.now()
        start_date = self._calculate_start_date(timeframe)

        # Determine interval
        interval = self._determine_interval(timeframe)

        # Fetch from database
        trend_data = await self.market_repo.get_index_history(
            index, start_date, end_date
        )

        # Transform to response schema
        data_list = []
        for record in trend_data:
            data_list.append(
                MarketTrendData(
                    timestamp=record.timestamp,
                    open=float(record.open_value) if record.open_value else None,
                    high=float(record.high_value) if record.high_value else None,
                    low=float(record.low_value) if record.low_value else None,
                    close=float(record.close_value),
                    volume=record.volume,
                )
            )

        response = MarketTrendResponse(
            index=index,
            timeframe=timeframe,
            interval=interval,
            data=data_list,
            count=len(data_list),
            updated_at=datetime.now(),
        )

        # Cache the result
        await self.cache.set(
            cache_key,
            response.model_dump(),
            ttl=self.MARKET_TREND_TTL,
        )

        return response

    def _calculate_start_date(self, timeframe: str) -> datetime:
        """Calculate start date based on timeframe"""
        now = datetime.now()
        timeframe_map = {
            "1D": timedelta(days=1),
            "5D": timedelta(days=5),
            "1M": timedelta(days=30),
            "3M": timedelta(days=90),
            "6M": timedelta(days=180),
            "1Y": timedelta(days=365),
        }
        return now - timeframe_map.get(timeframe, timedelta(days=30))

    def _determine_interval(self, timeframe: str) -> str:
        """Determine appropriate interval based on timeframe"""
        interval_map = {
            "1D": "1m",
            "5D": "5m",
            "1M": "1h",
            "3M": "1h",
            "6M": "1d",
            "1Y": "1d",
        }
        return interval_map.get(timeframe, "1d")
