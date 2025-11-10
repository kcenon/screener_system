"""Stock screening Pydantic schemas"""

from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Filter Schemas
# ============================================================================


class FilterRange(BaseModel):
    """Range filter with min/max values"""

    min: Optional[float] = Field(None, description="Minimum value (inclusive)")
    max: Optional[float] = Field(None, description="Maximum value (inclusive)")

    @field_validator("min", "max")
    @classmethod
    def validate_numeric(cls, v: Optional[float]) -> Optional[float]:
        """Validate numeric values"""
        if v is not None and (v < 0 and v != -1):  # Allow -1 for special cases
            raise ValueError("Value must be non-negative or -1")
        return v

    def validate_range(self) -> None:
        """Validate min <= max"""
        if self.min is not None and self.max is not None:
            if self.min > self.max:
                raise ValueError("min must be less than or equal to max")


class ScreeningFilters(BaseModel):
    """All available screening filters"""

    # Market filters
    market: Optional[Literal["KOSPI", "KOSDAQ", "ALL"]] = Field(
        "ALL", description="Market filter"
    )
    sector: Optional[str] = Field(None, max_length=50, description="Sector filter")
    industry: Optional[str] = Field(None, max_length=100, description="Industry filter")

    # Valuation filters
    per: Optional[FilterRange] = Field(None, description="Price-to-Earnings Ratio")
    pbr: Optional[FilterRange] = Field(None, description="Price-to-Book Ratio")
    psr: Optional[FilterRange] = Field(None, description="Price-to-Sales Ratio")
    pcr: Optional[FilterRange] = Field(None, description="Price-to-Cash Flow Ratio")
    dividend_yield: Optional[FilterRange] = Field(
        None, description="Dividend Yield (%)"
    )

    # Profitability filters
    roe: Optional[FilterRange] = Field(None, description="Return on Equity (%)")
    roa: Optional[FilterRange] = Field(None, description="Return on Assets (%)")
    roic: Optional[FilterRange] = Field(
        None, description="Return on Invested Capital (%)"
    )
    gross_margin: Optional[FilterRange] = Field(None, description="Gross Margin (%)")
    operating_margin: Optional[FilterRange] = Field(
        None, description="Operating Margin (%)"
    )
    net_margin: Optional[FilterRange] = Field(None, description="Net Margin (%)")

    # Growth filters
    revenue_growth_yoy: Optional[FilterRange] = Field(
        None, description="Revenue Growth YoY (%)"
    )
    profit_growth_yoy: Optional[FilterRange] = Field(
        None, description="Profit Growth YoY (%)"
    )
    eps_growth_yoy: Optional[FilterRange] = Field(
        None, description="EPS Growth YoY (%)"
    )

    # Stability filters
    debt_to_equity: Optional[FilterRange] = Field(
        None, description="Debt-to-Equity Ratio"
    )
    current_ratio: Optional[FilterRange] = Field(None, description="Current Ratio")
    altman_z_score: Optional[FilterRange] = Field(
        None, description="Altman Z-Score (bankruptcy risk)"
    )
    piotroski_f_score: Optional[FilterRange] = Field(
        None, description="Piotroski F-Score (0-9)"
    )

    # Price momentum filters
    price_change_1d: Optional[FilterRange] = Field(
        None, description="1-Day Price Change (%)"
    )
    price_change_1w: Optional[FilterRange] = Field(
        None, description="1-Week Price Change (%)"
    )
    price_change_1m: Optional[FilterRange] = Field(
        None, description="1-Month Price Change (%)"
    )
    price_change_3m: Optional[FilterRange] = Field(
        None, description="3-Month Price Change (%)"
    )
    price_change_6m: Optional[FilterRange] = Field(
        None, description="6-Month Price Change (%)"
    )
    price_change_1y: Optional[FilterRange] = Field(
        None, description="1-Year Price Change (%)"
    )

    # Volume filter
    volume_surge_pct: Optional[FilterRange] = Field(
        None, description="Volume Surge (%)"
    )

    # Composite score filters
    quality_score: Optional[FilterRange] = Field(
        None, description="Quality Score (0-100)"
    )
    value_score: Optional[FilterRange] = Field(None, description="Value Score (0-100)")
    growth_score: Optional[FilterRange] = Field(
        None, description="Growth Score (0-100)"
    )
    momentum_score: Optional[FilterRange] = Field(
        None, description="Momentum Score (0-100)"
    )
    overall_score: Optional[FilterRange] = Field(
        None, description="Overall Score (0-100)"
    )

    # Price and market cap filters
    current_price: Optional[FilterRange] = Field(None, description="Current Price (KRW)")
    market_cap: Optional[FilterRange] = Field(
        None, description="Market Capitalization (KRW billion)"
    )

    @field_validator("*", mode="before")
    @classmethod
    def validate_filter_ranges(cls, v: Any) -> Any:
        """Validate all FilterRange objects"""
        if isinstance(v, dict) and ("min" in v or "max" in v):
            filter_range = FilterRange(**v)
            filter_range.validate_range()
            return filter_range
        return v


# ============================================================================
# Request Schemas
# ============================================================================


class ScreeningRequest(BaseModel):
    """Stock screening request"""

    filters: Optional[ScreeningFilters] = Field(
        default_factory=ScreeningFilters, description="Screening filters"
    )

    # Sorting
    sort_by: str = Field(
        "market_cap",
        description="Field to sort by",
        pattern="^[a-z_]+$",
    )
    order: Literal["asc", "desc"] = Field("desc", description="Sort order")

    # Pagination
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    per_page: int = Field(50, ge=1, le=200, description="Results per page")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_field(cls, v: str) -> str:
        """Validate sort field is allowed"""
        allowed_fields = {
            "code",
            "name",
            "market",
            "sector",
            "current_price",
            "market_cap",
            "per",
            "pbr",
            "psr",
            "dividend_yield",
            "roe",
            "roa",
            "roic",
            "gross_margin",
            "operating_margin",
            "net_margin",
            "revenue_growth_yoy",
            "profit_growth_yoy",
            "eps_growth_yoy",
            "debt_to_equity",
            "current_ratio",
            "altman_z_score",
            "piotroski_f_score",
            "price_change_1d",
            "price_change_1w",
            "price_change_1m",
            "price_change_3m",
            "price_change_6m",
            "price_change_1y",
            "volume_surge_pct",
            "quality_score",
            "value_score",
            "growth_score",
            "momentum_score",
            "overall_score",
        }

        if v not in allowed_fields:
            raise ValueError(f"Invalid sort field: {v}. Must be one of: {allowed_fields}")

        return v


# ============================================================================
# Response Schemas
# ============================================================================


class ScreenedStock(BaseModel):
    """Single stock in screening results"""

    # Stock info
    code: str
    name: str
    name_english: Optional[str] = None
    market: str
    sector: Optional[str] = None
    industry: Optional[str] = None

    # Latest price
    last_trade_date: Optional[date] = None
    current_price: Optional[int] = None
    current_volume: Optional[int] = None
    market_cap: Optional[int] = None

    # Indicators (Optional - may be NULL for some stocks)
    indicators_date: Optional[date] = None
    per: Optional[Decimal] = None
    pbr: Optional[Decimal] = None
    psr: Optional[Decimal] = None
    pcr: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    roe: Optional[Decimal] = None
    roa: Optional[Decimal] = None
    roic: Optional[Decimal] = None
    gross_margin: Optional[Decimal] = None
    operating_margin: Optional[Decimal] = None
    net_margin: Optional[Decimal] = None
    revenue_growth_yoy: Optional[Decimal] = None
    profit_growth_yoy: Optional[Decimal] = None
    eps_growth_yoy: Optional[Decimal] = None
    debt_to_equity: Optional[Decimal] = None
    current_ratio: Optional[Decimal] = None
    altman_z_score: Optional[Decimal] = None
    piotroski_f_score: Optional[int] = None
    price_change_1d: Optional[Decimal] = None
    price_change_1w: Optional[Decimal] = None
    price_change_1m: Optional[Decimal] = None
    price_change_3m: Optional[Decimal] = None
    price_change_6m: Optional[Decimal] = None
    price_change_1y: Optional[Decimal] = None
    volume_surge_pct: Optional[Decimal] = None
    quality_score: Optional[Decimal] = None
    value_score: Optional[Decimal] = None
    growth_score: Optional[Decimal] = None
    momentum_score: Optional[Decimal] = None
    overall_score: Optional[Decimal] = None

    model_config = {"from_attributes": True}


class ScreeningMetadata(BaseModel):
    """Screening response metadata"""

    total: int = Field(..., ge=0, description="Total number of matching stocks")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, description="Results per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")


class ScreeningResponse(BaseModel):
    """Stock screening response"""

    stocks: List[ScreenedStock] = Field(..., description="List of matching stocks")
    meta: ScreeningMetadata = Field(..., description="Pagination metadata")
    query_time_ms: float = Field(..., ge=0, description="Query execution time (ms)")
    filters_applied: Dict[str, Any] = Field(..., description="Applied filters summary")


# ============================================================================
# Screening Template Schemas
# ============================================================================


class ScreeningTemplate(BaseModel):
    """Predefined screening template"""

    id: str = Field(..., pattern="^[a-z_]+$", description="Template ID")
    name: str = Field(..., max_length=100, description="Template display name")
    description: str = Field(..., max_length=500, description="Template description")
    filters: ScreeningFilters = Field(..., description="Predefined filters")
    sort_by: str = Field("overall_score", description="Default sort field")
    order: Literal["asc", "desc"] = Field("desc", description="Default sort order")


class ScreeningTemplateList(BaseModel):
    """List of available screening templates"""

    templates: List[ScreeningTemplate] = Field(..., description="Available templates")
