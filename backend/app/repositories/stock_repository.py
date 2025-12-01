"""Stock repository for database operations"""

from datetime import date
from typing import List, Optional, Tuple

from app.db.models import (CalculatedIndicator, DailyPrice, FinancialStatement,
                           Stock)
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class StockRepository:
    """Repository for Stock database operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    # ========================================================================
    # Stock Operations
    # ========================================================================

    async def get_by_code(self, stock_code: str) -> Optional[Stock]:
        """Get stock by code"""
        result = await self.session.execute(
            select(Stock).where(Stock.code == stock_code)
        )
        return result.scalar_one_or_none()

    async def get_by_code_with_latest(
        self, stock_code: str
    ) -> Optional[Tuple[Stock, Optional[DailyPrice], Optional[CalculatedIndicator]]]:
        """Get stock with latest price and indicators"""
        # Get stock
        stock = await self.get_by_code(stock_code)
        if not stock:
            return None

        # Get latest price
        latest_price = await self.get_latest_price(stock_code)

        # Get latest indicators
        latest_indicators = await self.get_latest_indicators(stock_code)

        return stock, latest_price, latest_indicators

    async def list_stocks(
        self,
        market: Optional[str] = None,
        sector: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Stock], int]:
        """
        List stocks with pagination and filtering
        Returns (stocks, total_count)
        """
        # Build query
        query = select(Stock).where(Stock.delisting_date.is_(None))

        # Apply filters
        if market and market != "ALL":
            query = query.where(Stock.market == market)
        if sector:
            query = query.where(Stock.sector == sector)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.execute(count_query)
        total_count = total.scalar_one()

        # Apply pagination and ordering
        query = query.order_by(Stock.code).offset(offset).limit(limit)

        # Execute query
        result = await self.session.execute(query)
        stocks = result.scalars().all()

        return list(stocks), total_count

    async def list_stocks_with_latest_price(
        self,
        market: Optional[str] = None,
        sector: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[
        List[Tuple[Stock, Optional[DailyPrice], Optional[CalculatedIndicator]]], int
    ]:
        """
        List stocks with latest price and indicators
        Returns (list of (stock, latest_price, latest_indicators), total_count)
        """
        # Get stocks
        stocks, total_count = await self.list_stocks(market, sector, offset, limit)

        # Get latest prices and indicators for all stocks
        stock_codes = [stock.code for stock in stocks]
        latest_prices = await self._get_latest_prices_bulk(stock_codes)
        latest_indicators = await self._get_latest_indicators_bulk(stock_codes)

        # Combine results
        result = []
        for stock in stocks:
            price = latest_prices.get(stock.code)
            indicators = latest_indicators.get(stock.code)
            result.append((stock, price, indicators))

        return result, total_count

    async def search_stocks(
        self, query: str, market: Optional[str] = None, limit: int = 10
    ) -> List[Stock]:
        """
        Search stocks by name using fuzzy matching (pg_trgm)
        """
        # Build search query using ILIKE for partial matching
        # TODO: Use pg_trgm similarity() for better fuzzy search
        search_query = select(Stock).where(
            and_(
                Stock.delisting_date.is_(None),
                or_(
                    Stock.name.ilike(f"%{query}%"),
                    Stock.name_english.ilike(f"%{query}%") if query else False,
                    Stock.code.ilike(f"{query}%"),
                ),
            )
        )

        # Apply market filter
        if market and market != "ALL":
            search_query = search_query.where(Stock.market == market)

        # Apply limit
        search_query = search_query.limit(limit)

        # Execute
        result = await self.session.execute(search_query)
        return list(result.scalars().all())

    # ========================================================================
    # Daily Price Operations
    # ========================================================================

    async def get_latest_price(self, stock_code: str) -> Optional[DailyPrice]:
        """Get latest daily price for a stock"""
        result = await self.session.execute(
            select(DailyPrice)
            .where(DailyPrice.stock_code == stock_code)
            .order_by(desc(DailyPrice.trade_date))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_price_history(
        self,
        stock_code: str,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 365,
    ) -> List[DailyPrice]:
        """Get price history for a stock within date range"""
        query = select(DailyPrice).where(DailyPrice.stock_code == stock_code)

        # Apply date filters
        if from_date:
            query = query.where(DailyPrice.trade_date >= from_date)
        if to_date:
            query = query.where(DailyPrice.trade_date <= to_date)

        # Order by date descending and apply limit
        query = query.order_by(desc(DailyPrice.trade_date)).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _get_latest_prices_bulk(
        self, stock_codes: List[str]
    ) -> dict[str, DailyPrice]:
        """Get latest prices for multiple stocks"""
        # Subquery to get latest trade_date for each stock
        subquery = (
            select(
                DailyPrice.stock_code,
                func.max(DailyPrice.trade_date).label("max_date"),
            )
            .where(DailyPrice.stock_code.in_(stock_codes))
            .group_by(DailyPrice.stock_code)
            .subquery()
        )

        # Main query to get prices
        query = select(DailyPrice).join(
            subquery,
            and_(
                DailyPrice.stock_code == subquery.c.stock_code,
                DailyPrice.trade_date == subquery.c.max_date,
            ),
        )

        result = await self.session.execute(query)
        prices = result.scalars().all()

        # Convert to dict
        return {price.stock_code: price for price in prices}

    # ========================================================================
    # Financial Statement Operations
    # ========================================================================

    async def get_financials(
        self,
        stock_code: str,
        period_type: Optional[str] = None,
        years: int = 5,
    ) -> List[FinancialStatement]:
        """Get financial statements for a stock"""
        query = select(FinancialStatement).where(
            FinancialStatement.stock_code == stock_code
        )

        # Apply period type filter
        if period_type:
            query = query.where(FinancialStatement.period_type == period_type)

        # Order by fiscal year and quarter descending
        query = query.order_by(
            desc(FinancialStatement.fiscal_year),
            desc(FinancialStatement.fiscal_quarter),
        ).limit(years * 4 if period_type == "quarterly" else years)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ========================================================================
    # Calculated Indicator Operations
    # ========================================================================

    async def get_latest_indicators(
        self, stock_code: str
    ) -> Optional[CalculatedIndicator]:
        """Get latest calculated indicators for a stock"""
        result = await self.session.execute(
            select(CalculatedIndicator)
            .where(CalculatedIndicator.stock_code == stock_code)
            .order_by(desc(CalculatedIndicator.calculation_date))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _get_latest_indicators_bulk(
        self, stock_codes: List[str]
    ) -> dict[str, CalculatedIndicator]:
        """Get latest indicators for multiple stocks"""
        # Subquery to get latest calculation_date for each stock
        subquery = (
            select(
                CalculatedIndicator.stock_code,
                func.max(CalculatedIndicator.calculation_date).label("max_date"),
            )
            .where(CalculatedIndicator.stock_code.in_(stock_codes))
            .group_by(CalculatedIndicator.stock_code)
            .subquery()
        )

        # Main query to get indicators
        query = select(CalculatedIndicator).join(
            subquery,
            and_(
                CalculatedIndicator.stock_code == subquery.c.stock_code,
                CalculatedIndicator.calculation_date == subquery.c.max_date,
            ),
        )

        result = await self.session.execute(query)
        indicators = result.scalars().all()

        # Convert to dict
        return {indicator.stock_code: indicator for indicator in indicators}

    # ========================================================================
    # Utility Operations
    # ========================================================================

    async def count_stocks(
        self, market: Optional[str] = None, sector: Optional[str] = None
    ) -> int:
        """Count stocks matching filters"""
        query = select(func.count(Stock.code)).where(Stock.delisting_date.is_(None))

        if market and market != "ALL":
            query = query.where(Stock.market == market)
        if sector:
            query = query.where(Stock.sector == sector)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def exists_by_code(self, stock_code: str) -> bool:
        """Check if stock exists"""
        stock = await self.get_by_code(stock_code)
        return stock is not None
