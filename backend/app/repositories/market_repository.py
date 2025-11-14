"""Market repository for market overview and sector analysis operations"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import and_, case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CalculatedIndicator, DailyPrice, MarketIndex, Stock


class MarketRepository:
    """Repository for market overview database operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    # ========================================================================
    # Market Indices Operations
    # ========================================================================

    async def get_current_indices(
        self,
    ) -> List[Tuple[MarketIndex, List[float]]]:
        """
        Get current values for all market indices with sparkline data

        Returns:
            List of (MarketIndex, sparkline_data) tuples
            sparkline_data contains last 30 data points
        """
        indices = []

        for index_code in ["KOSPI", "KOSDAQ", "KRX100"]:
            # Get latest index value
            latest_query = (
                select(MarketIndex)
                .where(MarketIndex.code == index_code)
                .order_by(desc(MarketIndex.timestamp))
                .limit(1)
            )
            result = await self.session.execute(latest_query)
            latest = result.scalar_one_or_none()

            if not latest:
                continue

            # Get sparkline data (last 30 data points)
            sparkline_query = (
                select(MarketIndex.close_value)
                .where(MarketIndex.code == index_code)
                .order_by(desc(MarketIndex.timestamp))
                .limit(30)
            )
            sparkline_result = await self.session.execute(sparkline_query)
            sparkline_values = [
                float(row[0]) for row in sparkline_result.all()
            ]
            # Reverse to get chronological order
            sparkline_values.reverse()

            indices.append((latest, sparkline_values))

        return indices

    async def get_index_history(
        self,
        index_code: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[MarketIndex]:
        """
        Get historical index data for a specific timeframe

        Args:
            index_code: Index code (KOSPI, KOSDAQ, KRX100)
            start_date: Start datetime
            end_date: End datetime

        Returns:
            List of MarketIndex records
        """
        query = (
            select(MarketIndex)
            .where(
                and_(
                    MarketIndex.code == index_code,
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

    async def get_market_breadth(self, market: str = "ALL") -> dict:
        """
        Get advancing/declining/unchanged stock counts

        Args:
            market: Market filter (KOSPI, KOSDAQ, ALL)

        Returns:
            Dictionary with advancing, declining, unchanged counts and A/D ratio
        """
        # Subquery to get latest price for each stock
        latest_prices = (
            select(
                DailyPrice.stock_code,
                DailyPrice.close_price,
                DailyPrice.open_price,
                func.row_number()
                .over(
                    partition_by=DailyPrice.stock_code,
                    order_by=desc(DailyPrice.trade_date),
                )
                .label("rn"),
            )
            .subquery()
        )

        # Join with stocks and filter by market
        query = (
            select(
                Stock.code,
                Stock.market,
                latest_prices.c.close_price,
                latest_prices.c.open_price,
            )
            .join(latest_prices, Stock.code == latest_prices.c.stock_code)
            .where(
                and_(
                    latest_prices.c.rn == 1,
                    Stock.delisting_date.is_(None),
                )
            )
        )

        if market != "ALL":
            query = query.where(Stock.market == market)

        result = await self.session.execute(query)
        stocks_data = result.all()

        # Calculate advancing, declining, unchanged
        advancing = 0
        declining = 0
        unchanged = 0

        for stock in stocks_data:
            if stock.close_price > stock.open_price:
                advancing += 1
            elif stock.close_price < stock.open_price:
                declining += 1
            else:
                unchanged += 1

        total = advancing + declining + unchanged
        ad_ratio = advancing / declining if declining > 0 else 0.0

        return {
            "advancing": advancing,
            "declining": declining,
            "unchanged": unchanged,
            "total": total,
            "ad_ratio": round(ad_ratio, 2),
        }

    # ========================================================================
    # Sector Performance Operations
    # ========================================================================

    async def get_sector_performance(
        self,
        market: str = "ALL",
        timeframe: str = "1D",
    ) -> List[dict]:
        """
        Get aggregated sector performance

        Args:
            market: Market filter (KOSPI, KOSDAQ, ALL)
            timeframe: Time period (1D, 1W, 1M, 3M)

        Returns:
            List of sector performance dictionaries
        """
        # Calculate lookback days based on timeframe
        lookback_days = {
            "1D": 1,
            "1W": 7,
            "1M": 30,
            "3M": 90,
        }.get(timeframe, 1)

        # Subquery to get latest and previous prices
        latest_prices = (
            select(
                DailyPrice.stock_code,
                DailyPrice.close_price.label("latest_price"),
                func.row_number()
                .over(
                    partition_by=DailyPrice.stock_code,
                    order_by=desc(DailyPrice.trade_date),
                )
                .label("rn"),
            )
            .subquery()
        )

        previous_prices = (
            select(
                DailyPrice.stock_code,
                DailyPrice.close_price.label("previous_price"),
                func.row_number()
                .over(
                    partition_by=DailyPrice.stock_code,
                    order_by=desc(DailyPrice.trade_date),
                )
                .label("rn"),
            )
            .where(
                DailyPrice.trade_date
                <= func.current_date() - timedelta(days=lookback_days)
            )
            .subquery()
        )

        # Calculate change percentage and aggregate by sector
        query = (
            select(
                Stock.sector,
                func.count(Stock.code).label("stock_count"),
                func.avg(
                    ((latest_prices.c.latest_price - previous_prices.c.previous_price)
                     / previous_prices.c.previous_price * 100)
                ).label("avg_change_percent"),
                func.sum(Stock.shares_outstanding * latest_prices.c.latest_price).label(
                    "total_market_cap"
                ),
            )
            .join(latest_prices, Stock.code == latest_prices.c.stock_code)
            .outerjoin(previous_prices, Stock.code == previous_prices.c.stock_code)
            .where(
                and_(
                    latest_prices.c.rn == 1,
                    previous_prices.c.rn == 1,
                    Stock.delisting_date.is_(None),
                    Stock.sector.isnot(None),
                )
            )
            .group_by(Stock.sector)
            .order_by(desc("avg_change_percent"))
        )

        if market != "ALL":
            query = query.where(Stock.market == market)

        result = await self.session.execute(query)
        sectors = result.all()

        # Get top stock for each sector
        sector_data = []
        for sector in sectors:
            # Get top performing stock in this sector
            top_stock_query = (
                select(Stock.code, Stock.name)
                .join(latest_prices, Stock.code == latest_prices.c.stock_code)
                .outerjoin(previous_prices, Stock.code == previous_prices.c.stock_code)
                .where(
                    and_(
                        Stock.sector == sector.sector,
                        latest_prices.c.rn == 1,
                        previous_prices.c.rn == 1,
                        Stock.delisting_date.is_(None),
                    )
                )
                .order_by(
                    desc(
                        (latest_prices.c.latest_price - previous_prices.c.previous_price)
                        / previous_prices.c.previous_price
                    )
                )
                .limit(1)
            )

            top_stock_result = await self.session.execute(top_stock_query)
            top_stock = top_stock_result.first()

            sector_data.append(
                {
                    "code": sector.sector,
                    "name": sector.sector,
                    "stock_count": sector.stock_count,
                    "change_percent": round(float(sector.avg_change_percent), 2)
                    if sector.avg_change_percent
                    else 0.0,
                    "market_cap": int(sector.total_market_cap)
                    if sector.total_market_cap
                    else 0,
                    "top_stock": {
                        "code": top_stock.code if top_stock else None,
                        "name": top_stock.name if top_stock else None,
                    }
                    if top_stock
                    else None,
                }
            )

        return sector_data

    # ========================================================================
    # Market Movers Operations
    # ========================================================================

    async def get_top_movers(
        self,
        mover_type: str,
        market: str = "ALL",
        limit: int = 20,
    ) -> List[Tuple[Stock, DailyPrice, float]]:
        """
        Get top gaining or losing stocks

        Args:
            mover_type: 'gainers' or 'losers'
            market: Market filter (KOSPI, KOSDAQ, ALL)
            limit: Number of results

        Returns:
            List of (Stock, DailyPrice, change_percent) tuples
        """
        # Subquery to get latest prices with previous day comparison
        latest_prices = (
            select(
                DailyPrice.stock_code,
                DailyPrice.close_price,
                DailyPrice.open_price,
                DailyPrice.volume,
                DailyPrice.trading_value,
                DailyPrice.trade_date,
                func.row_number()
                .over(
                    partition_by=DailyPrice.stock_code,
                    order_by=desc(DailyPrice.trade_date),
                )
                .label("rn"),
            )
            .subquery()
        )

        previous_prices = (
            select(
                DailyPrice.stock_code,
                DailyPrice.close_price.label("prev_close"),
                func.row_number()
                .over(
                    partition_by=DailyPrice.stock_code,
                    order_by=desc(DailyPrice.trade_date),
                )
                .label("rn"),
            )
            .where(DailyPrice.trade_date < func.current_date())
            .subquery()
        )

        # Calculate change percentage
        change_expr = (
            (latest_prices.c.close_price - previous_prices.c.prev_close)
            / previous_prices.c.prev_close
            * 100
        )

        query = (
            select(
                Stock,
                latest_prices.c.close_price,
                latest_prices.c.volume,
                latest_prices.c.trading_value,
                change_expr.label("change_percent"),
            )
            .join(latest_prices, Stock.code == latest_prices.c.stock_code)
            .join(previous_prices, Stock.code == previous_prices.c.stock_code)
            .where(
                and_(
                    latest_prices.c.rn == 1,
                    previous_prices.c.rn == 1,
                    Stock.delisting_date.is_(None),
                )
            )
        )

        if market != "ALL":
            query = query.where(Stock.market == market)

        # Order by change percentage
        if mover_type == "gainers":
            query = query.order_by(desc("change_percent"))
        else:  # losers
            query = query.order_by("change_percent")

        query = query.limit(limit)

        result = await self.session.execute(query)
        movers = []

        for row in result.all():
            stock = row[0]
            price_data = DailyPrice(
                stock_code=stock.code,
                trade_date=datetime.now().date(),
                close_price=int(row[1]),
                volume=row[2],
                trading_value=row[3],
            )
            change_pct = float(row[4]) if row[4] else 0.0
            movers.append((stock, price_data, change_pct))

        return movers

    # ========================================================================
    # Most Active Stocks Operations
    # ========================================================================

    async def get_most_active(
        self,
        metric: str,
        market: str = "ALL",
        limit: int = 20,
    ) -> List[Tuple[Stock, DailyPrice]]:
        """
        Get stocks with highest volume or trading value

        Args:
            metric: 'volume' or 'value'
            market: Market filter (KOSPI, KOSDAQ, ALL)
            limit: Number of results

        Returns:
            List of (Stock, DailyPrice) tuples
        """
        # Subquery to get latest prices
        latest_prices = (
            select(
                DailyPrice.stock_code,
                DailyPrice.close_price,
                DailyPrice.volume,
                DailyPrice.trading_value,
                DailyPrice.trade_date,
                func.row_number()
                .over(
                    partition_by=DailyPrice.stock_code,
                    order_by=desc(DailyPrice.trade_date),
                )
                .label("rn"),
            )
            .subquery()
        )

        query = (
            select(Stock, latest_prices)
            .join(latest_prices, Stock.code == latest_prices.c.stock_code)
            .where(
                and_(
                    latest_prices.c.rn == 1,
                    Stock.delisting_date.is_(None),
                )
            )
        )

        if market != "ALL":
            query = query.where(Stock.market == market)

        # Order by volume or trading value
        if metric == "volume":
            query = query.order_by(desc(latest_prices.c.volume))
        else:  # value
            query = query.order_by(desc(latest_prices.c.trading_value))

        query = query.limit(limit)

        result = await self.session.execute(query)
        active_stocks = []

        for row in result.all():
            stock = row[0]
            price_data = DailyPrice(
                stock_code=stock.code,
                trade_date=row[6],  # trade_date
                close_price=int(row[2]),  # close_price
                volume=row[3],  # volume
                trading_value=row[4],  # trading_value
            )
            active_stocks.append((stock, price_data))

        return active_stocks
