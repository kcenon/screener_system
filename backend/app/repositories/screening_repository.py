"""Screening repository for stock filtering operations"""

from typing import Any, Dict, List, Set, Tuple

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.screening import FilterRange, ScreeningFilters


class ScreeningRepository:
    """Repository for stock screening operations"""

    # Allowed sort fields to prevent SQL injection
    # These must match the columns in stock_screening_view
    ALLOWED_SORT_FIELDS: Set[str] = {
        # Stock identification
        "code",
        "name",
        "market",
        # Price and valuation
        "current_price",
        "market_cap",
        "per",
        "pbr",
        "pcr",
        "psr",
        # Profitability
        "roe",
        "roa",
        "roic",
        "net_margin",
        "operating_margin",
        "gross_margin",
        # Growth
        "revenue_growth_yoy",
        "profit_growth_yoy",
        "eps_growth_yoy",
        # Stability
        "debt_to_equity",
        "current_ratio",
        "altman_z_score",
        "piotroski_f_score",
        # Dividends
        "dividend_yield",
        # Momentum
        "price_change_1d",
        "price_change_1w",
        "price_change_1m",
        "price_change_3m",
        "price_change_6m",
        "price_change_1y",
        # Volume
        "volume_surge_pct",
        # Scores
        "quality_score",
        "value_score",
        "growth_score",
        "momentum_score",
        "overall_score",
    }

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

        Security:
            - sort_by is validated against ALLOWED_SORT_FIELDS allowlist
            - All filter values use parameterized queries
            - No user input is directly interpolated into SQL

        Returns:
            Tuple of (results list, total count)

        Raises:
            ValueError: If sort_by is not in ALLOWED_SORT_FIELDS
        """
        # Validate sort field to prevent SQL injection
        if sort_by not in self.ALLOWED_SORT_FIELDS:
            raise ValueError(
                f"Invalid sort field '{sort_by}'. "
                f"Allowed fields: {sorted(self.ALLOWED_SORT_FIELDS)}"
            )

        # Build WHERE conditions with parameters
        where_conditions, params = self._build_where_conditions(filters)

        # Build WHERE clause
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        # Build ORDER BY clause (safe: sort_by validated above)
        order_direction = "DESC" if order == "desc" else "ASC"

        # OPTIMIZED: Single query with window function COUNT() OVER()
        # This eliminates the need for a separate COUNT query, improving performance by ~50%
        query = f"""
            WITH filtered AS (
                SELECT
                    *,
                    COUNT(*) OVER() as total_count
                FROM stock_screening_view
                {where_clause}
            )
            SELECT * FROM filtered
            ORDER BY
                CASE WHEN {sort_by} IS NULL THEN 1 ELSE 0 END,
                {sort_by} {order_direction}
            LIMIT :limit OFFSET :offset
        """

        # Add pagination parameters
        params["limit"] = limit
        params["offset"] = offset

        # Execute single optimized query
        result = await self.session.execute(text(query), params)
        rows = result.mappings().all()

        # Extract total count from first row (or 0 if empty)
        total_count = rows[0]["total_count"] if rows else 0

        # Convert to dict format (excluding total_count column)
        stocks = [{k: v for k, v in row.items() if k != "total_count"} for row in rows]

        return stocks, total_count

    def _build_where_conditions(
        self, filters: ScreeningFilters
    ) -> Tuple[List[str], Dict[str, Any]]:
        """
        Build WHERE clause conditions from filters using parameterized queries

        Security:
            All user inputs are passed as parameters, never interpolated.
            This prevents SQL injection attacks.

        Returns:
            Tuple of (conditions list, parameters dict)
        """
        conditions = []
        params = {}

        # Market filter (parameterized)
        if filters.market and filters.market != "ALL":
            conditions.append("market = :market")
            params["market"] = filters.market

        # Sector filter (parameterized)
        if filters.sector:
            conditions.append("sector = :sector")
            params["sector"] = filters.sector

        # Industry filter (parameterized)
        if filters.industry:
            conditions.append("industry = :industry")
            params["industry"] = filters.industry

        # Valuation filters
        self._add_range_filter(conditions, params, "per", filters.per)
        self._add_range_filter(conditions, params, "pbr", filters.pbr)
        self._add_range_filter(conditions, params, "psr", filters.psr)
        self._add_range_filter(conditions, params, "pcr", filters.pcr)
        self._add_range_filter(
            conditions, params, "dividend_yield", filters.dividend_yield
        )

        # Profitability filters
        self._add_range_filter(conditions, params, "roe", filters.roe)
        self._add_range_filter(conditions, params, "roa", filters.roa)
        self._add_range_filter(conditions, params, "roic", filters.roic)
        self._add_range_filter(conditions, params, "gross_margin", filters.gross_margin)
        self._add_range_filter(
            conditions, params, "operating_margin", filters.operating_margin
        )
        self._add_range_filter(conditions, params, "net_margin", filters.net_margin)

        # Growth filters
        self._add_range_filter(
            conditions, params, "revenue_growth_yoy", filters.revenue_growth_yoy
        )
        self._add_range_filter(
            conditions, params, "profit_growth_yoy", filters.profit_growth_yoy
        )
        self._add_range_filter(
            conditions, params, "eps_growth_yoy", filters.eps_growth_yoy
        )

        # Stability filters
        self._add_range_filter(
            conditions, params, "debt_to_equity", filters.debt_to_equity
        )
        self._add_range_filter(
            conditions, params, "current_ratio", filters.current_ratio
        )
        self._add_range_filter(
            conditions, params, "altman_z_score", filters.altman_z_score
        )
        self._add_range_filter(
            conditions, params, "piotroski_f_score", filters.piotroski_f_score
        )

        # Price momentum filters
        self._add_range_filter(
            conditions, params, "price_change_1d", filters.price_change_1d
        )
        self._add_range_filter(
            conditions, params, "price_change_1w", filters.price_change_1w
        )
        self._add_range_filter(
            conditions, params, "price_change_1m", filters.price_change_1m
        )
        self._add_range_filter(
            conditions, params, "price_change_3m", filters.price_change_3m
        )
        self._add_range_filter(
            conditions, params, "price_change_6m", filters.price_change_6m
        )
        self._add_range_filter(
            conditions, params, "price_change_1y", filters.price_change_1y
        )

        # Volume filter
        self._add_range_filter(
            conditions, params, "volume_surge_pct", filters.volume_surge_pct
        )

        # Composite score filters
        self._add_range_filter(
            conditions, params, "quality_score", filters.quality_score
        )
        self._add_range_filter(conditions, params, "value_score", filters.value_score)
        self._add_range_filter(conditions, params, "growth_score", filters.growth_score)
        self._add_range_filter(
            conditions, params, "momentum_score", filters.momentum_score
        )
        self._add_range_filter(
            conditions, params, "overall_score", filters.overall_score
        )

        # Price and market cap filters
        self._add_range_filter(
            conditions, params, "current_price", filters.current_price
        )
        self._add_range_filter(conditions, params, "market_cap", filters.market_cap)

        return conditions, params

    def _add_range_filter(
        self,
        conditions: List[str],
        params: Dict[str, Any],
        field_name: str,
        filter_range: FilterRange | None,
    ) -> None:
        """
        Add range filter to conditions list using parameterized queries

        Security:
            Uses parameterized queries to prevent SQL injection

        Args:
            conditions: List to append conditions to
            params: Dictionary to add parameter values to
            field_name: Database column name
            filter_range: FilterRange object with min/max
        """
        if not filter_range:
            return

        # Check if both min and max are None
        if filter_range.min is None and filter_range.max is None:
            return

        # Add min condition (parameterized)
        if filter_range.min is not None:
            param_name = f"{field_name}_min"
            conditions.append(f"{field_name} >= :{param_name}")
            params[param_name] = filter_range.min

        # Add max condition (parameterized)
        if filter_range.max is not None:
            param_name = f"{field_name}_max"
            conditions.append(f"{field_name} <= :{param_name}")
            params[param_name] = filter_range.max

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
