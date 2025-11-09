"""Stock Pydantic schemas"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Base Schemas
# ============================================================================


class StockBase(BaseModel):
    """Base stock schema with common fields"""

    code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$")
    name: str = Field(..., min_length=1, max_length=100)
    name_english: Optional[str] = Field(None, max_length=100)
    market: str = Field(..., pattern="^(KOSPI|KOSDAQ)$")
    sector: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)


class Stock(StockBase):
    """Stock schema for database retrieval"""

    listing_date: Optional[date] = None
    delisting_date: Optional[date] = None
    shares_outstanding: Optional[int] = Field(None, gt=0)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Daily Price Schemas
# ============================================================================


class DailyPriceBase(BaseModel):
    """Base daily price schema"""

    trade_date: date
    open_price: Optional[int] = Field(None, gt=0)
    high_price: Optional[int] = Field(None, gt=0)
    low_price: Optional[int] = Field(None, gt=0)
    close_price: int = Field(..., gt=0)
    adjusted_close: Optional[int] = Field(None, gt=0)
    volume: Optional[int] = Field(None, ge=0)
    trading_value: Optional[int] = Field(None, ge=0)
    market_cap: Optional[int] = Field(None, gt=0)


class DailyPrice(DailyPriceBase):
    """Daily price schema for database retrieval"""

    stock_code: str

    model_config = {"from_attributes": True}


class DailyPriceWithChanges(DailyPrice):
    """Daily price with calculated change percentages"""

    price_change: int = 0
    price_change_pct: float = 0.0
    daily_range: int = 0


# ============================================================================
# Financial Statement Schemas
# ============================================================================


class FinancialStatementBase(BaseModel):
    """Base financial statement schema"""

    period_type: str = Field(..., pattern="^(quarterly|annual)$")
    fiscal_year: int = Field(..., ge=1900, le=2100)
    fiscal_quarter: Optional[int] = Field(None, ge=1, le=4)
    report_date: date

    # Income Statement
    revenue: Optional[int] = None
    cost_of_revenue: Optional[int] = None
    gross_profit: Optional[int] = None
    operating_expenses: Optional[int] = None
    operating_profit: Optional[int] = None
    non_operating_income: Optional[int] = None
    non_operating_expenses: Optional[int] = None
    ebt: Optional[int] = None
    tax_expense: Optional[int] = None
    net_profit: Optional[int] = None

    # Per Share Metrics
    eps: Optional[Decimal] = None
    bps: Optional[Decimal] = None
    dps: Optional[Decimal] = None

    # Balance Sheet
    current_assets: Optional[int] = None
    non_current_assets: Optional[int] = None
    total_assets: Optional[int] = None
    current_liabilities: Optional[int] = None
    non_current_liabilities: Optional[int] = None
    total_liabilities: Optional[int] = None
    equity: Optional[int] = None

    # Cash Flow
    operating_cash_flow: Optional[int] = None
    investing_cash_flow: Optional[int] = None
    financing_cash_flow: Optional[int] = None
    free_cash_flow: Optional[int] = None
    capital_expenditure: Optional[int] = None

    @field_validator("fiscal_quarter")
    @classmethod
    def validate_quarter(cls, v: Optional[int], info) -> Optional[int]:
        """Validate fiscal quarter based on period type"""
        period_type = info.data.get("period_type")
        if period_type == "annual" and v is not None:
            raise ValueError("Annual reports should not have fiscal_quarter")
        if period_type == "quarterly" and v is None:
            raise ValueError("Quarterly reports must have fiscal_quarter")
        return v


class FinancialStatement(FinancialStatementBase):
    """Financial statement schema for database retrieval"""

    id: int
    stock_code: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FinancialStatementWithRatios(FinancialStatement):
    """Financial statement with calculated ratios"""

    gross_margin: Optional[Decimal] = None
    operating_margin: Optional[Decimal] = None
    net_margin: Optional[Decimal] = None
    debt_to_equity: Optional[Decimal] = None
    current_ratio: Optional[Decimal] = None


# ============================================================================
# Calculated Indicator Schemas
# ============================================================================


class CalculatedIndicatorBase(BaseModel):
    """Base calculated indicator schema"""

    calculation_date: date

    # Valuation Metrics
    per: Optional[Decimal] = None
    pbr: Optional[Decimal] = None
    psr: Optional[Decimal] = None
    pcr: Optional[Decimal] = None
    ev_ebitda: Optional[Decimal] = None
    ev_sales: Optional[Decimal] = None
    ev_fcf: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    payout_ratio: Optional[Decimal] = None
    peg_ratio: Optional[Decimal] = None

    # Profitability Metrics
    roe: Optional[Decimal] = None
    roa: Optional[Decimal] = None
    roic: Optional[Decimal] = None
    gross_margin: Optional[Decimal] = None
    operating_margin: Optional[Decimal] = None
    net_margin: Optional[Decimal] = None
    ebitda_margin: Optional[Decimal] = None
    fcf_margin: Optional[Decimal] = None

    # Growth Metrics
    revenue_growth_yoy: Optional[Decimal] = None
    profit_growth_yoy: Optional[Decimal] = None
    eps_growth_yoy: Optional[Decimal] = None
    revenue_growth_qoq: Optional[Decimal] = None
    profit_growth_qoq: Optional[Decimal] = None
    revenue_cagr_3y: Optional[Decimal] = None
    revenue_cagr_5y: Optional[Decimal] = None
    eps_cagr_3y: Optional[Decimal] = None
    eps_cagr_5y: Optional[Decimal] = None

    # Stability Metrics
    debt_to_equity: Optional[Decimal] = None
    debt_to_assets: Optional[Decimal] = None
    interest_coverage: Optional[Decimal] = None
    current_ratio: Optional[Decimal] = None
    quick_ratio: Optional[Decimal] = None
    cash_ratio: Optional[Decimal] = None
    altman_z_score: Optional[Decimal] = None
    piotroski_f_score: Optional[int] = Field(None, ge=0, le=9)

    # Efficiency Metrics
    asset_turnover: Optional[Decimal] = None
    inventory_turnover: Optional[Decimal] = None
    receivables_turnover: Optional[Decimal] = None
    payables_turnover: Optional[Decimal] = None
    cash_conversion_cycle: Optional[int] = None

    # Technical Metrics
    price_change_1d: Optional[Decimal] = None
    price_change_1w: Optional[Decimal] = None
    price_change_1m: Optional[Decimal] = None
    price_change_3m: Optional[Decimal] = None
    price_change_6m: Optional[Decimal] = None
    price_change_1y: Optional[Decimal] = None
    price_change_3y: Optional[Decimal] = None
    price_change_5y: Optional[Decimal] = None
    volume_20d_avg: Optional[int] = None
    volume_60d_avg: Optional[int] = None
    volume_surge_pct: Optional[Decimal] = None

    # Moving Averages
    ma_5d: Optional[Decimal] = None
    ma_20d: Optional[Decimal] = None
    ma_60d: Optional[Decimal] = None
    ma_120d: Optional[Decimal] = None
    ma_200d: Optional[Decimal] = None

    # Technical Indicators
    rsi_14d: Optional[Decimal] = Field(None, ge=0, le=100)
    macd: Optional[Decimal] = None
    macd_signal: Optional[Decimal] = None
    bollinger_upper: Optional[Decimal] = None
    bollinger_lower: Optional[Decimal] = None

    # Composite Scores
    quality_score: Optional[int] = Field(None, ge=1, le=100)
    value_score: Optional[int] = Field(None, ge=1, le=100)
    growth_score: Optional[int] = Field(None, ge=1, le=100)
    momentum_score: Optional[int] = Field(None, ge=1, le=100)
    overall_score: Optional[int] = Field(None, ge=1, le=100)


class CalculatedIndicator(CalculatedIndicatorBase):
    """Calculated indicator schema for database retrieval"""

    stock_code: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Composite Schemas
# ============================================================================


class StockDetail(Stock):
    """Stock detail with latest price and indicators"""

    latest_price: Optional[DailyPrice] = None
    latest_indicators: Optional[CalculatedIndicator] = None


class StockListItem(BaseModel):
    """Stock list item with minimal information"""

    code: str
    name: str
    market: str
    sector: Optional[str] = None
    latest_close: Optional[int] = None
    price_change_1d: Optional[Decimal] = None
    volume: Optional[int] = None
    market_cap: Optional[int] = None

    model_config = {"from_attributes": True}


# ============================================================================
# Response Schemas with Pagination
# ============================================================================


class PaginationMeta(BaseModel):
    """Pagination metadata"""

    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1, le=100)
    total_pages: int = Field(..., ge=0)


class StockListResponse(BaseModel):
    """Stock list response with pagination"""

    items: List[StockListItem]
    meta: PaginationMeta


class DailyPriceListResponse(BaseModel):
    """Daily price list response"""

    items: List[DailyPrice]
    meta: PaginationMeta


class FinancialStatementListResponse(BaseModel):
    """Financial statement list response"""

    items: List[FinancialStatement]
    meta: PaginationMeta


# ============================================================================
# Search Schemas
# ============================================================================


class StockSearchQuery(BaseModel):
    """Stock search query parameters"""

    q: str = Field(..., min_length=1, max_length=100)
    market: Optional[str] = Field(None, pattern="^(KOSPI|KOSDAQ|ALL)$")
    limit: int = Field(10, ge=1, le=50)


class StockSearchResult(BaseModel):
    """Stock search result item"""

    code: str
    name: str
    name_english: Optional[str] = None
    market: str
    sector: Optional[str] = None
    similarity: float = Field(..., ge=0, le=1)

    model_config = {"from_attributes": True}


class StockSearchResponse(BaseModel):
    """Stock search response"""

    items: List[StockSearchResult]
    query: str
    total: int
