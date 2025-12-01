"""Market repository for market overview data operations"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DailyPrice, MarketIndex, Stock


class MarketRepository:
    """Repository for Market Overview database operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    # ========================================================================
    # Market Indices Operations
    # ========================================================================

    async def get_current_indices(self) -> List[MarketIndex]:
        """
        Get current (latest) values for all market indices

        Returns:
            List of latest MarketIndex records for KOSPI, KOSDAQ, KRX100
        """
        # Subquery to get latest timestamp for each index code
        latest_timestamps = (
            select(
                MarketIndex.code,
                func.max(MarketIndex.timestamp).label("max_timestamp"),
            )
            .group_by(MarketIndex.code)
            .subquery()
        )

        # Join to get full records for latest timestamps
        query = (
            select(MarketIndex)
            .join(
                latest_timestamps,
                and_(
                    MarketIndex.code == latest_timestamps.c.code,
                    MarketIndex.timestamp == latest_timestamps.c.max_timestamp,
                ),
            )
            .order_by(MarketIndex.code)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_index_sparkline(
        self, code: str, data_points: int = 30
    ) -> List[float]:
        """
        Get sparkline data (last N closing values) for an index

        Args:
            code: Index code (KOSPI, KOSDAQ, KRX100)
            data_points: Number of recent data points (default: 30)

        Returns:
            List of closing values in chronological order
        """
        query = (
            select(MarketIndex.close_value)
            .where(MarketIndex.code == code)
            .order_by(desc(MarketIndex.timestamp))
            .limit(data_points)
        )

        result = await self.session.execute(query)
        # Reverse to get chronological order (oldest to newest)
        values = [float(v) for v in result.scalars().all()]
        return list(reversed(values))

    async def get_index_history(
        self,
        code: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[MarketIndex]:
        """
        Get historical index data for a time range

        Args:
            code: Index code (KOSPI, KOSDAQ, KRX100)
            start_date: Start datetime
            end_date: End datetime

        Returns:
            List of MarketIndex records in chronological order
        """
        query = (
            select(MarketIndex)
            .where(
                and_(
                    MarketIndex.code == code,
                    MarketIndex.timestamp >= start_date,
                    MarketIndex.timestamp <= end_date,
                )
            )
            .order_by(MarketIndex.timestamp)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ========================================================================
    # Market Breadth Operations
    # ========================================================================

    async def get_market_breadth(self, market: Optional[str] = None) -> Dict[str, int]:
        """
        Get market breadth indicators (advancing/declining/unchanged counts)

        Args:
            market: Market filter (KOSPI, KOSDAQ, or None for ALL)

        Returns:
            Dictionary with advancing, declining, unchanged counts
        """
        # Subquery to get latest price for each stock
        latest_prices = (
            select(
                DailyPrice.stock_code,
                func.max(DailyPrice.trade_date).label("max_date"),
            )
            .group_by(DailyPrice.stock_code)
            .subquery()
        )

        # Join to get full latest price records
        latest_price_data = (
            select(
                DailyPrice.stock_code,
                DailyPrice.close_price,
                DailyPrice.open_price,
            )
            .join(
                latest_prices,
                and_(
                    DailyPrice.stock_code == latest_prices.c.stock_code,
                    DailyPrice.trade_date == latest_prices.c.max_date,
                ),
            )
            .subquery()
        )

        # Calculate change and count
        query = select(
            func.count(
                case(
                    (
                        latest_price_data.c.close_price
                        > latest_price_data.c.open_price,
                        1,
                    )
                )
            ).label("advancing"),
            func.count(
                case(
                    (
                        latest_price_data.c.close_price
                        < latest_price_data.c.open_price,
                        1,
                    )
                )
            ).label("declining"),
            func.count(
                case(
                    (
                        latest_price_data.c.close_price
                        == latest_price_data.c.open_price,
                        1,
                    )
                )
            ).label("unchanged"),
        ).select_from(latest_price_data)

        # Apply market filter if specified
        if market and market != "ALL":
            query = query.join(
                Stock, Stock.code == latest_price_data.c.stock_code
            ).where(Stock.market == market)

        result = await self.session.execute(query)
        data = result.one()

        return {
            "advancing": data.advancing or 0,
            "declining": data.declining or 0,
            "unchanged": data.unchanged or 0,
        }

    # ========================================================================
    # Sector Performance Operations
    # ========================================================================

    async def get_sector_performance(
        self,
        market: Optional[str] = None,
        timeframe_days: int = 1,
    ) -> List[Dict]:
        """
        Get sector-level performance aggregation

        Args:
            market: Market filter (KOSPI, KOSDAQ, or None for ALL)
            timeframe_days: Number of days for performance calculation (1, 7, 30, 90)

        Returns:
            List of sector performance dictionaries
        """
        # Subquery for latest prices
        latest_prices = (
            select(
                DailyPrice.stock_code,
                func.max(DailyPrice.trade_date).label("max_date"),
            )
            .group_by(DailyPrice.stock_code)
            .subquery()
        )

        # Subquery for prices N days ago
        cutoff_date = select(
            func.max(DailyPrice.trade_date) - timedelta(days=timeframe_days)
        ).scalar_subquery()

        previous_prices = (
            select(
                DailyPrice.stock_code,
                DailyPrice.close_price.label("prev_close"),
            )
            .where(DailyPrice.trade_date == cutoff_date)
            .subquery()
        )

        # Calculate sector aggregations
        query = (
            select(
                Stock.sector,
                func.count(Stock.code).label("stock_count"),
                func.sum(Stock.shares_outstanding * DailyPrice.close_price).label(
                    "market_cap"
                ),
                func.sum(DailyPrice.volume).label("total_volume"),
                # Calculate price change
                func.avg(
                    (DailyPrice.close_price - previous_prices.c.prev_close)
                    / previous_prices.c.prev_close
                    * 100
                ).label("avg_change_percent"),
            )
            .select_from(Stock)
            .join(
                latest_prices,
                Stock.code == latest_prices.c.stock_code,
            )
            .join(
                DailyPrice,
                and_(
                    DailyPrice.stock_code == Stock.code,
                    DailyPrice.trade_date == latest_prices.c.max_date,
                ),
            )
            .outerjoin(
                previous_prices,
                Stock.code == previous_prices.c.stock_code,
            )
            .where(
                and_(
                    Stock.sector.isnot(None),
                    Stock.delisting_date.is_(None),
                )
            )
            .group_by(Stock.sector)
            .order_by(desc("avg_change_percent"))
        )

        # Apply market filter
        if market and market != "ALL":
            query = query.where(Stock.market == market)

        result = await self.session.execute(query)
        sectors = result.all()

        return [
            {
                "code": row.sector,
                "stock_count": row.stock_count,
                "market_cap": row.market_cap or 0,
                "volume": row.total_volume or 0,
                "change_percent": round(float(row.avg_change_percent or 0), 2),
            }
            for row in sectors
        ]

    async def get_sector_top_stock(
        self, sector: str
    ) -> Optional[Tuple[str, str, float]]:
        """
        Get top performing stock in a sector

        Args:
            sector: Sector code

        Returns:
            Tuple of (stock_code, stock_name, change_percent) or None
        """
        # Subquery for latest prices
        latest_prices = (
            select(
                DailyPrice.stock_code,
                func.max(DailyPrice.trade_date).label("max_date"),
            )
            .group_by(DailyPrice.stock_code)
            .subquery()
        )

        # Subquery for previous day prices
        prev_prices = (
            select(
                DailyPrice.stock_code,
                DailyPrice.close_price.label("prev_close"),
            )
            .join(
                latest_prices,
                DailyPrice.stock_code == latest_prices.c.stock_code,
            )
            .where(
                DailyPrice.trade_date == latest_prices.c.max_date - timedelta(days=1)
            )
            .subquery()
        )

        # Query top stock by change percent
        query = (
            select(
                Stock.code,
                Stock.name,
                (
                    (DailyPrice.close_price - prev_prices.c.prev_close)
                    / prev_prices.c.prev_close
                    * 100
                ).label("change_percent"),
            )
            .select_from(Stock)
            .join(
                latest_prices,
                Stock.code == latest_prices.c.stock_code,
            )
            .join(
                DailyPrice,
                and_(
                    DailyPrice.stock_code == Stock.code,
                    DailyPrice.trade_date == latest_prices.c.max_date,
                ),
            )
            .join(
                prev_prices,
                Stock.code == prev_prices.c.stock_code,
            )
            .where(
                and_(
                    Stock.sector == sector,
                    Stock.delisting_date.is_(None),
                )
            )
            .order_by(desc("change_percent"))
            .limit(1)
        )

        result = await self.session.execute(query)
        row = result.one_or_none()

        if row:
            return (row.code, row.name, round(float(row.change_percent), 2))
        return None

    # ========================================================================
    # Market Movers Operations
    # ========================================================================

    async def get_top_movers(
        self,
        move_type: str,  # "gainers" or "losers"
        market: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Get top gaining or losing stocks

        Args:
            move_type: "gainers" or "losers"
            market: Market filter (KOSPI, KOSDAQ, or None for ALL)
            limit: Maximum number of results

        Returns:
            List of stock dictionaries with price and change info
        """
        # Subquery for latest prices
        latest_prices = (
            select(
                DailyPrice.stock_code,
                func.max(DailyPrice.trade_date).label("max_date"),
            )
            .group_by(DailyPrice.stock_code)
            .subquery()
        )

        # Subquery for previous day prices
        prev_prices = (
            select(
                DailyPrice.stock_code,
                DailyPrice.close_price.label("prev_close"),
            )
            .join(
                latest_prices,
                DailyPrice.stock_code == latest_prices.c.stock_code,
            )
            .where(
                DailyPrice.trade_date == latest_prices.c.max_date - timedelta(days=1)
            )
            .subquery()
        )

        # Build main query
        change_percent = (
            (DailyPrice.close_price - prev_prices.c.prev_close)
            / prev_prices.c.prev_close
            * 100
        )

        query = (
            select(
                Stock.code,
                Stock.name,
                Stock.market,
                Stock.sector,
                DailyPrice.close_price,
                (DailyPrice.close_price - prev_prices.c.prev_close).label("change"),
                change_percent.label("change_percent"),
                DailyPrice.volume,
                DailyPrice.trading_value,
            )
            .select_from(Stock)
            .join(
                latest_prices,
                Stock.code == latest_prices.c.stock_code,
            )
            .join(
                DailyPrice,
                and_(
                    DailyPrice.stock_code == Stock.code,
                    DailyPrice.trade_date == latest_prices.c.max_date,
                ),
            )
            .join(
                prev_prices,
                Stock.code == prev_prices.c.stock_code,
            )
            .where(Stock.delisting_date.is_(None))
        )

        # Apply market filter
        if market and market != "ALL":
            query = query.where(Stock.market == market)

        # Sort by change percent
        if move_type == "gainers":
            query = query.order_by(desc("change_percent"))
        else:  # losers
            query = query.order_by("change_percent")

        query = query.limit(limit)

        result = await self.session.execute(query)
        stocks = result.all()

        return [
            {
                "code": row.code,
                "name": row.name,
                "market": row.market,
                "sector": row.sector,
                "current_price": row.close_price,
                "change": row.change,
                "change_percent": round(float(row.change_percent), 2),
                "volume": row.volume,
                "value": row.trading_value,
            }
            for row in stocks
        ]

    # ========================================================================
    # Most Active Operations
    # ========================================================================

    async def get_most_active(
        self,
        metric: str,  # "volume" or "value"
        market: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Get stocks with highest trading volume or value

        Args:
            metric: "volume" or "value"
            market: Market filter (KOSPI, KOSDAQ, or None for ALL)
            limit: Maximum number of results

        Returns:
            List of stock dictionaries with trading info
        """
        # Subquery for latest prices
        latest_prices = (
            select(
                DailyPrice.stock_code,
                func.max(DailyPrice.trade_date).label("max_date"),
            )
            .group_by(DailyPrice.stock_code)
            .subquery()
        )

        # Subquery for previous day prices
        prev_prices = (
            select(
                DailyPrice.stock_code,
                DailyPrice.close_price.label("prev_close"),
            )
            .join(
                latest_prices,
                DailyPrice.stock_code == latest_prices.c.stock_code,
            )
            .where(
                DailyPrice.trade_date == latest_prices.c.max_date - timedelta(days=1)
            )
            .subquery()
        )

        # Build main query
        change_percent = (
            (DailyPrice.close_price - prev_prices.c.prev_close)
            / prev_prices.c.prev_close
            * 100
        )

        query = (
            select(
                Stock.code,
                Stock.name,
                Stock.market,
                Stock.sector,
                DailyPrice.close_price,
                change_percent.label("change_percent"),
                DailyPrice.volume,
                DailyPrice.trading_value,
            )
            .select_from(Stock)
            .join(
                latest_prices,
                Stock.code == latest_prices.c.stock_code,
            )
            .join(
                DailyPrice,
                and_(
                    DailyPrice.stock_code == Stock.code,
                    DailyPrice.trade_date == latest_prices.c.max_date,
                ),
            )
            .outerjoin(
                prev_prices,
                Stock.code == prev_prices.c.stock_code,
            )
            .where(Stock.delisting_date.is_(None))
        )

        # Apply market filter
        if market and market != "ALL":
            query = query.where(Stock.market == market)

        # Sort by metric
        if metric == "volume":
            query = query.order_by(desc(DailyPrice.volume))
        else:  # value
            query = query.order_by(desc(DailyPrice.trading_value))

        query = query.limit(limit)

        result = await self.session.execute(query)
        stocks = result.all()

        return [
            {
                "code": row.code,
                "name": row.name,
                "market": row.market,
                "sector": row.sector,
                "current_price": row.close_price,
                "change_percent": round(float(row.change_percent or 0), 2),
                "volume": row.volume,
                "value": row.trading_value,
            }
            for row in stocks
        ]
