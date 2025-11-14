"""Market service layer for market overview business logic and caching.

This module provides the MarketService class that implements business logic
for market overview operations with intelligent caching strategies.

The service layer handles:
    - Market indices aggregation and transformation
    - Market breadth calculations with sentiment analysis
    - Sector performance aggregation
    - Top movers and most active stock identification
    - Cache management with appropriate TTLs
    - Data validation and transformation

Example:
    Initialize the service with a database session and cache manager::

        from app.services import MarketService
        from app.core.cache import cache_manager
        from app.db import get_session

        async with get_session() as session:
            service = MarketService(session, cache_manager)
            breadth = await service.get_market_breadth()
            print(f"A/D Ratio: {breadth['ad_ratio']}, Sentiment: {breadth['sentiment']}")
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheManager
from app.repositories import MarketRepository


class MarketService:
    """Service for market overview operations with intelligent caching.

    This class implements business logic for market-wide data including
    indices, breadth indicators, sector performance, and market movers.
    All operations are cached with appropriate TTLs to optimize performance.

    Attributes:
        MARKET_DATA_TTL: Cache TTL for real-time market data (5 minutes).
        INDEX_HISTORY_TTL: Cache TTL for historical index data (30 minutes).
        SECTOR_DATA_TTL: Cache TTL for sector performance (5 minutes).
        session: Async SQLAlchemy session for database operations.
        cache: Cache manager instance for Redis operations.
        market_repo: Market repository for data access.

    Example:
        >>> service = MarketService(session, cache_manager)
        >>> sectors = await service.get_sector_performance(market="KOSPI")
        >>> print(f"Found {len(sectors)} sectors")
    """

    # Cache TTL (seconds)
    MARKET_DATA_TTL = 5 * 60  # 5 minutes for real-time data
    INDEX_HISTORY_TTL = 30 * 60  # 30 minutes for historical data
    SECTOR_DATA_TTL = 5 * 60  # 5 minutes for sector aggregations

    # Sector name mapping (Korean)
    SECTOR_NAMES = {
        "technology": "기술",
        "finance": "금융",
        "healthcare": "헬스케어",
        "consumer": "소비재",
        "materials": "소재",
        "industrial": "산업재",
        "energy": "에너지",
        "utilities": "유틸리티",
        "telecom": "통신",
        "real_estate": "부동산",
    }

    def __init__(self, session: AsyncSession, cache: CacheManager):
        """Initialize service with database session and cache manager.

        Args:
            session: Async SQLAlchemy session for database operations.
            cache: CacheManager instance for Redis caching operations.
        """
        self.session = session
        self.cache = cache
        self.market_repo = MarketRepository(session)

    # ========================================================================
    # Market Indices Operations
    # ========================================================================

    async def get_market_indices(self) -> Dict[str, List[Dict]]:
        """
        Get current market indices with sparklines

        Returns:
            Dictionary with 'indices' list and 'updated_at' timestamp
        """
        # Check cache
        cache_key = "market:indices:current"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Get current indices
        indices = await self.market_repo.get_current_indices()

        # Get sparklines for each index
        result = []
        for index in indices:
            sparkline = await self.market_repo.get_index_sparkline(
                code=index.code, data_points=30
            )

            result.append(
                {
                    "code": index.code,
                    "name": self._get_index_name(index.code),
                    "current": float(index.close_value),
                    "change": float(index.change_value) if index.change_value else 0.0,
                    "change_percent": (
                        float(index.change_percent) if index.change_percent else 0.0
                    ),
                    "high": float(index.high_value) if index.high_value else None,
                    "low": float(index.low_value) if index.low_value else None,
                    "volume": index.volume,
                    "value": index.trading_value,
                    "timestamp": index.timestamp.isoformat(),
                    "sparkline": sparkline,
                }
            )

        response = {"indices": result, "updated_at": datetime.now().isoformat()}

        # Cache result
        await self.cache.set(cache_key, response, ttl=self.MARKET_DATA_TTL)

        return response

    async def get_market_trend(
        self,
        index: str = "KOSPI",
        timeframe: str = "1M",
    ) -> Dict:
        """
        Get historical market trend data

        Args:
            index: Index code (KOSPI, KOSDAQ, KRX100)
            timeframe: Timeframe (1D, 5D, 1M, 3M, 6M, 1Y)

        Returns:
            Dictionary with historical data points
        """
        # Validate index
        if index not in ["KOSPI", "KOSDAQ", "KRX100"]:
            index = "KOSPI"

        # Check cache
        cache_key = f"market:trend:{index}:{timeframe}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Calculate date range
        end_date = datetime.now()
        days_map = {
            "1D": 1,
            "5D": 5,
            "1M": 30,
            "3M": 90,
            "6M": 180,
            "1Y": 365,
        }
        days = days_map.get(timeframe, 30)
        start_date = end_date - timedelta(days=days)

        # Get historical data
        history = await self.market_repo.get_index_history(
            code=index, start_date=start_date, end_date=end_date
        )

        # Transform to response format
        data_points = [
            {
                "timestamp": point.timestamp.isoformat(),
                "open": float(point.open_value) if point.open_value else None,
                "high": float(point.high_value) if point.high_value else None,
                "low": float(point.low_value) if point.low_value else None,
                "close": float(point.close_value),
                "volume": point.volume,
            }
            for point in history
        ]

        # Determine interval based on timeframe
        interval_map = {
            "1D": "1m",
            "5D": "5m",
            "1M": "1h",
            "3M": "1h",
            "6M": "1d",
            "1Y": "1d",
        }
        interval = interval_map.get(timeframe, "1h")

        response = {
            "index": index,
            "timeframe": timeframe,
            "interval": interval,
            "data": data_points,
            "count": len(data_points),
            "updated_at": datetime.now().isoformat(),
        }

        # Cache result (longer TTL for historical data)
        await self.cache.set(cache_key, response, ttl=self.INDEX_HISTORY_TTL)

        return response

    # ========================================================================
    # Market Breadth Operations
    # ========================================================================

    async def get_market_breadth(self, market: str = "ALL") -> Dict:
        """
        Get market breadth indicators with sentiment analysis

        Args:
            market: Market filter (KOSPI, KOSDAQ, ALL)

        Returns:
            Dictionary with breadth metrics and sentiment
        """
        # Validate market
        if market not in ["KOSPI", "KOSDAQ", "ALL"]:
            market = "ALL"

        # Check cache
        cache_key = f"market:breadth:{market}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Get breadth data
        breadth = await self.market_repo.get_market_breadth(market=market)

        # Calculate A/D ratio
        advancing = breadth["advancing"]
        declining = breadth["declining"]
        unchanged = breadth["unchanged"]
        total = advancing + declining + unchanged

        ad_ratio = round(advancing / declining, 2) if declining > 0 else 0.0

        # Determine sentiment
        sentiment = self._calculate_sentiment(ad_ratio)

        response = {
            "advancing": advancing,
            "declining": declining,
            "unchanged": unchanged,
            "total": total,
            "ad_ratio": ad_ratio,
            "sentiment": sentiment,
            "market": market,
            "timestamp": datetime.now().isoformat(),
        }

        # Cache result
        await self.cache.set(cache_key, response, ttl=self.MARKET_DATA_TTL)

        return response

    # ========================================================================
    # Sector Performance Operations
    # ========================================================================

    async def get_sector_performance(
        self,
        timeframe: str = "1D",
        market: str = "ALL",
    ) -> Dict:
        """
        Get sector performance aggregation

        Args:
            timeframe: Timeframe (1D, 1W, 1M, 3M)
            market: Market filter (KOSPI, KOSDAQ, ALL)

        Returns:
            Dictionary with sectors list and metadata
        """
        # Validate inputs
        if market not in ["KOSPI", "KOSDAQ", "ALL"]:
            market = "ALL"

        timeframe_map = {"1D": 1, "1W": 7, "1M": 30, "3M": 90}
        timeframe_days = timeframe_map.get(timeframe, 1)

        # Check cache
        cache_key = f"market:sectors:{timeframe}:{market}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Get sector data
        sectors_data = await self.market_repo.get_sector_performance(
            market=market, timeframe_days=timeframe_days
        )

        # Enrich with sector names and top stocks
        enriched_sectors = []
        for sector in sectors_data:
            sector_code = sector["code"]

            # Get top stock for this sector
            top_stock = await self.market_repo.get_sector_top_stock(sector_code)

            enriched_sectors.append(
                {
                    "code": sector_code,
                    "name": self._get_sector_name(sector_code),
                    "change_percent": sector["change_percent"],
                    "stock_count": sector["stock_count"],
                    "market_cap": sector["market_cap"],
                    "volume": sector["volume"],
                    "top_stock": (
                        {
                            "code": top_stock[0],
                            "name": top_stock[1],
                            "change_percent": top_stock[2],
                        }
                        if top_stock
                        else None
                    ),
                }
            )

        response = {
            "sectors": enriched_sectors,
            "timeframe": timeframe,
            "market": market,
            "updated_at": datetime.now().isoformat(),
        }

        # Cache result
        await self.cache.set(cache_key, response, ttl=self.SECTOR_DATA_TTL)

        return response

    # ========================================================================
    # Market Movers Operations
    # ========================================================================

    async def get_market_movers(
        self,
        move_type: str,  # "gainers" or "losers"
        market: str = "ALL",
        limit: int = 20,
    ) -> Dict:
        """
        Get top gaining or losing stocks

        Args:
            move_type: Type of movers (gainers or losers)
            market: Market filter (KOSPI, KOSDAQ, ALL)
            limit: Maximum number of results

        Returns:
            Dictionary with stocks list and metadata
        """
        # Validate inputs
        if move_type not in ["gainers", "losers"]:
            move_type = "gainers"

        if market not in ["KOSPI", "KOSDAQ", "ALL"]:
            market = "ALL"

        limit = min(100, max(1, limit))

        # Check cache
        cache_key = f"market:movers:{move_type}:{market}:{limit}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Get movers data
        stocks = await self.market_repo.get_top_movers(
            move_type=move_type, market=market, limit=limit
        )

        response = {
            "type": move_type,
            "market": market,
            "stocks": stocks,
            "total": len(stocks),
            "updated_at": datetime.now().isoformat(),
        }

        # Cache result
        await self.cache.set(cache_key, response, ttl=self.MARKET_DATA_TTL)

        return response

    # ========================================================================
    # Most Active Operations
    # ========================================================================

    async def get_most_active(
        self,
        metric: str = "volume",  # "volume" or "value"
        market: str = "ALL",
        limit: int = 20,
    ) -> Dict:
        """
        Get stocks with highest trading volume or value

        Args:
            metric: Sorting metric (volume or value)
            market: Market filter (KOSPI, KOSDAQ, ALL)
            limit: Maximum number of results

        Returns:
            Dictionary with stocks list and metadata
        """
        # Validate inputs
        if metric not in ["volume", "value"]:
            metric = "volume"

        if market not in ["KOSPI", "KOSDAQ", "ALL"]:
            market = "ALL"

        limit = min(100, max(1, limit))

        # Check cache
        cache_key = f"market:active:{metric}:{market}:{limit}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Get active stocks data
        stocks = await self.market_repo.get_most_active(
            metric=metric, market=market, limit=limit
        )

        response = {
            "metric": metric,
            "market": market,
            "stocks": stocks,
            "total": len(stocks),
            "updated_at": datetime.now().isoformat(),
        }

        # Cache result
        await self.cache.set(cache_key, response, ttl=self.MARKET_DATA_TTL)

        return response

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _calculate_sentiment(self, ad_ratio: float) -> str:
        """
        Calculate market sentiment from A/D ratio

        Args:
            ad_ratio: Advancing/Declining ratio

        Returns:
            Sentiment string (bullish, neutral, bearish)
        """
        if ad_ratio > 1.2:
            return "bullish"
        elif ad_ratio < 0.8:
            return "bearish"
        return "neutral"

    def _get_index_name(self, code: str) -> str:
        """Get Korean name for index code"""
        name_map = {
            "KOSPI": "코스피",
            "KOSDAQ": "코스닥",
            "KRX100": "KRX 100",
        }
        return name_map.get(code, code)

    def _get_sector_name(self, code: str) -> str:
        """Get Korean name for sector code"""
        return self.SECTOR_NAMES.get(code, code)
