"""Portfolio, Holding, and Transaction Pydantic schemas"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ENUMS
# ============================================================================


class TransactionType(str, Enum):
    """Transaction type enumeration"""

    BUY = "BUY"
    SELL = "SELL"


# ============================================================================
# PORTFOLIO SCHEMAS
# ============================================================================


class PortfolioBase(BaseModel):
    """Base portfolio schema"""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate portfolio name"""
        v = v.strip()

        if not v:
            raise ValueError("Portfolio name cannot be empty or whitespace only")

        if any(char in v for char in ["<", ">", "&", '"', "'"]):
            raise ValueError("Portfolio name contains invalid characters")

        return v


class PortfolioCreate(PortfolioBase):
    """Schema for creating a portfolio"""

    is_default: bool = Field(default=False)


class PortfolioUpdate(BaseModel):
    """Schema for updating a portfolio"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_default: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate portfolio name"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Portfolio name cannot be empty")
        return v


class PortfolioResponse(PortfolioBase):
    """Schema for portfolio response"""

    id: int
    user_id: int
    is_default: bool
    holding_count: int = 0
    total_cost: Decimal = Decimal("0")
    total_value: Optional[Decimal] = None
    unrealized_gain: Optional[Decimal] = None
    return_percent: Optional[Decimal] = None
    day_change: Optional[Decimal] = None
    day_change_percent: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PortfolioListResponse(BaseModel):
    """Schema for paginated portfolio list"""

    items: list[PortfolioResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# HOLDING SCHEMAS
# ============================================================================


class HoldingBase(BaseModel):
    """Base holding schema"""

    stock_symbol: str = Field(..., pattern="^[0-9]{6}$")
    shares: Decimal = Field(..., ge=0)
    average_cost: Decimal = Field(..., ge=0)

    @field_validator("shares")
    @classmethod
    def validate_shares(cls, v: Decimal) -> Decimal:
        """Validate shares are positive"""
        if v <= 0:
            raise ValueError("Shares must be positive")
        return v

    @field_validator("average_cost")
    @classmethod
    def validate_average_cost(cls, v: Decimal) -> Decimal:
        """Validate average cost is non-negative"""
        if v < 0:
            raise ValueError("Average cost cannot be negative")
        return v


class HoldingCreate(HoldingBase):
    """Schema for creating a holding (manual entry)"""

    first_purchase_date: Optional[date] = None


class HoldingUpdate(BaseModel):
    """Schema for updating a holding"""

    shares: Optional[Decimal] = Field(None, ge=0)
    average_cost: Optional[Decimal] = Field(None, ge=0)


class HoldingResponse(HoldingBase):
    """Schema for holding response"""

    id: int
    portfolio_id: int
    stock_name: Optional[str] = None
    sector: Optional[str] = None
    current_price: Optional[Decimal] = None
    total_cost: Decimal
    current_value: Optional[Decimal] = None
    unrealized_gain: Optional[Decimal] = None
    return_percent: Optional[Decimal] = None
    first_purchase_date: Optional[date] = None
    last_update_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HoldingListResponse(BaseModel):
    """Schema for list of holdings"""

    items: list[HoldingResponse]
    total: int
    total_cost: Decimal
    total_value: Optional[Decimal] = None
    total_gain: Optional[Decimal] = None


# ============================================================================
# TRANSACTION SCHEMAS
# ============================================================================


class TransactionBase(BaseModel):
    """Base transaction schema"""

    stock_symbol: str = Field(..., pattern="^[0-9]{6}$")
    transaction_type: TransactionType
    shares: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., ge=0)
    commission: Decimal = Field(default=Decimal("0"), ge=0)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("shares")
    @classmethod
    def validate_shares(cls, v: Decimal) -> Decimal:
        """Validate shares are positive"""
        if v <= 0:
            raise ValueError("Shares must be positive")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        """Validate price is non-negative"""
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v

    @field_validator("commission")
    @classmethod
    def validate_commission(cls, v: Decimal) -> Decimal:
        """Validate commission is non-negative"""
        if v < 0:
            raise ValueError("Commission cannot be negative")
        return v


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction"""

    transaction_date: Optional[datetime] = None


class TransactionResponse(TransactionBase):
    """Schema for transaction response"""

    id: int
    portfolio_id: int
    stock_name: Optional[str] = None
    transaction_value: Decimal
    total_amount: Decimal
    transaction_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Schema for paginated transaction list"""

    items: list[TransactionResponse]
    total: int
    skip: int
    limit: int


# ============================================================================
# PORTFOLIO PERFORMANCE SCHEMAS
# ============================================================================


class PortfolioPerformance(BaseModel):
    """Schema for portfolio performance metrics"""

    portfolio_id: int
    total_cost: Decimal
    total_value: Decimal
    unrealized_gain: Decimal
    return_percent: Decimal
    day_change: Decimal
    day_change_percent: Decimal
    realized_gain: Decimal
    best_performer: Optional[dict] = None
    worst_performer: Optional[dict] = None


class PortfolioAllocation(BaseModel):
    """Schema for portfolio allocation"""

    portfolio_id: int
    by_stock: list[dict]  # [{symbol, name, value, percent}, ...]
    by_sector: list[dict]  # [{sector, value, percent}, ...]
    by_market_cap: dict  # {large: percent, mid: percent, small: percent}


class PortfolioSummary(BaseModel):
    """Schema for portfolio summary with holdings"""

    portfolio: PortfolioResponse
    holdings: list[HoldingResponse]
    performance: Optional[PortfolioPerformance] = None
    allocation: Optional[PortfolioAllocation] = None
    recent_transactions: list[TransactionResponse] = []
