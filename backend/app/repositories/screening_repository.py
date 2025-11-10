"""Screening repository for stock filtering operations"""

from typing import Any, Dict, List, Tuple

from sqlalchemy import and_, desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.screening import FilterRange, ScreeningFilters


class ScreeningRepository:
    """Repository for stock screening operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def screen_stocks(
        self,
        filters: ScreeningFilters,
        sort_by: str = "market_cap",
        order: str = "desc",
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Screen stocks using filters with dynamic query building

        Returns:
            Tuple of (results list, total count)
        """
        # Build WHERE conditions
        where_conditions = self._build_where_conditions(filters)

        # Build base query
        base_query = """
            SELECT *
            FROM stock_screening_view
        """

        # Add WHERE clause if filters exist
        if where_conditions:
            where_clause = " AND ".join(where_conditions)
            base_query += f"\nWHERE {where_clause}"

        # Count total results
        count_query = f"SELECT COUNT(*) as total FROM ({base_query}) AS filtered"
        count_result = await self.session.execute(text(count_query))
        total_count = count_result.scalar_one()

        # Build ORDER BY clause
        order_direction = "DESC" if order == "desc" else "ASC"
        # Handle NULL values: put them last
        order_clause = f"""
            ORDER BY
                CASE WHEN {sort_by} IS NULL THEN 1 ELSE 0 END,
                {sort_by} {order_direction}
        """

        # Build final query with pagination
        final_query = f"""
            {base_query}
            {order_clause}
            LIMIT :limit OFFSET :offset
        """

        # Execute query
        result = await self.session.execute(
            text(final_query),
            {"limit": limit, "offset": offset}
        )

        # Convert to dict list
        stocks = [dict(row._mapping) for row in result]

        return stocks, total_count

    def _build_where_conditions(self, filters: ScreeningFilters) -> List[str]:
        """
        Build WHERE clause conditions from filters

        Returns:
            List of SQL condition strings
        """
        conditions = []

        # Market filter
        if filters.market and filters.market != "ALL":
            conditions.append(f"market = '{filters.market}'")

        # Sector filter
        if filters.sector:
            # Escape single quotes to prevent SQL injection
            escaped_sector = filters.sector.replace("'", "''")
            conditions.append(f"sector = '{escaped_sector}'")

        # Industry filter
        if filters.industry:
            escaped_industry = filters.industry.replace("'", "''")
            conditions.append(f"industry = '{escaped_industry}'")

        # Valuation filters
        self._add_range_filter(conditions, "per", filters.per)
        self._add_range_filter(conditions, "pbr", filters.pbr)
        self._add_range_filter(conditions, "psr", filters.psr)
        self._add_range_filter(conditions, "pcr", filters.pcr)
        self._add_range_filter(conditions, "dividend_yield", filters.dividend_yield)

        # Profitability filters
        self._add_range_filter(conditions, "roe", filters.roe)
        self._add_range_filter(conditions, "roa", filters.roa)
        self._add_range_filter(conditions, "roic", filters.roic)
        self._add_range_filter(conditions, "gross_margin", filters.gross_margin)
        self._add_range_filter(conditions, "operating_margin", filters.operating_margin)
        self._add_range_filter(conditions, "net_margin", filters.net_margin)

        # Growth filters
        self._add_range_filter(conditions, "revenue_growth_yoy", filters.revenue_growth_yoy)
        self._add_range_filter(conditions, "profit_growth_yoy", filters.profit_growth_yoy)
        self._add_range_filter(conditions, "eps_growth_yoy", filters.eps_growth_yoy)

        # Stability filters
        self._add_range_filter(conditions, "debt_to_equity", filters.debt_to_equity)
        self._add_range_filter(conditions, "current_ratio", filters.current_ratio)
        self._add_range_filter(conditions, "altman_z_score", filters.altman_z_score)
        self._add_range_filter(conditions, "piotroski_f_score", filters.piotroski_f_score)

        # Price momentum filters
        self._add_range_filter(conditions, "price_change_1d", filters.price_change_1d)
        self._add_range_filter(conditions, "price_change_1w", filters.price_change_1w)
        self._add_range_filter(conditions, "price_change_1m", filters.price_change_1m)
        self._add_range_filter(conditions, "price_change_3m", filters.price_change_3m)
        self._add_range_filter(conditions, "price_change_6m", filters.price_change_6m)
        self._add_range_filter(conditions, "price_change_1y", filters.price_change_1y)

        # Volume filter
        self._add_range_filter(conditions, "volume_surge_pct", filters.volume_surge_pct)

        # Composite score filters
        self._add_range_filter(conditions, "quality_score", filters.quality_score)
        self._add_range_filter(conditions, "value_score", filters.value_score)
        self._add_range_filter(conditions, "growth_score", filters.growth_score)
        self._add_range_filter(conditions, "momentum_score", filters.momentum_score)
        self._add_range_filter(conditions, "overall_score", filters.overall_score)

        # Price and market cap filters
        self._add_range_filter(conditions, "current_price", filters.current_price)
        self._add_range_filter(conditions, "market_cap", filters.market_cap)

        return conditions

    def _add_range_filter(
        self,
        conditions: List[str],
        field_name: str,
        filter_range: FilterRange | None,
    ) -> None:
        """
        Add range filter to conditions list

        Args:
            conditions: List to append conditions to
            field_name: Database column name
            filter_range: FilterRange object with min/max
        """
        if not filter_range:
            return

        # Check if both min and max are None
        if filter_range.min is None and filter_range.max is None:
            return

        # Add min condition
        if filter_range.min is not None:
            conditions.append(f"{field_name} >= {filter_range.min}")

        # Add max condition
        if filter_range.max is not None:
            conditions.append(f"{field_name} <= {filter_range.max}")

    async def get_screening_templates(self) -> List[Dict[str, Any]]:
        """
        Get predefined screening templates

        Returns:
            List of template definitions
        """
        # This could be loaded from database in the future
        # For now, return hardcoded templates
        templates = [
            {
                "id": "dividend_stocks",
                "name": "고배당주 (High Dividend)",
                "description": "Stocks with dividend yield > 3% and quality score > 70",
                "filters": {
                    "dividend_yield": {"min": 3.0},
                    "quality_score": {"min": 70.0},
                },
                "sort_by": "dividend_yield",
                "order": "desc",
            },
            {
                "id": "value_stocks",
                "name": "가치주 (Value Stocks)",
                "description": "Undervalued stocks with low PER/PBR and positive ROE",
                "filters": {
                    "per": {"min": 0.0, "max": 15.0},
                    "pbr": {"min": 0.0, "max": 1.5},
                    "roe": {"min": 5.0},
                },
                "sort_by": "value_score",
                "order": "desc",
            },
            {
                "id": "growth_stocks",
                "name": "성장주 (Growth Stocks)",
                "description": "High growth companies with revenue growth > 20%",
                "filters": {
                    "revenue_growth_yoy": {"min": 20.0},
                    "profit_growth_yoy": {"min": 10.0},
                },
                "sort_by": "growth_score",
                "order": "desc",
            },
            {
                "id": "quality_stocks",
                "name": "우량주 (Quality Stocks)",
                "description": "High quality companies with Piotroski F-Score >= 7",
                "filters": {
                    "piotroski_f_score": {"min": 7.0},
                    "quality_score": {"min": 80.0},
                },
                "sort_by": "quality_score",
                "order": "desc",
            },
            {
                "id": "momentum_stocks",
                "name": "모멘텀주 (Momentum Stocks)",
                "description": "Strong price momentum in recent 1-3 months",
                "filters": {
                    "price_change_1m": {"min": 10.0},
                    "price_change_3m": {"min": 20.0},
                },
                "sort_by": "momentum_score",
                "order": "desc",
            },
        ]

        return templates
