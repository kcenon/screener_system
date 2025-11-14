"""Watchlist and User Activity Pydantic schemas"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# WATCHLIST SCHEMAS
# ============================================================================


class WatchlistStockBase(BaseModel):
    """Base schema for stocks in a watchlist"""

    stock_code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$")
    notes: Optional[str] = Field(None, max_length=500)


class WatchlistStockCreate(WatchlistStockBase):
    """Schema for adding stock to watchlist"""

    pass


class WatchlistStockResponse(WatchlistStockBase):
    """Schema for stock in watchlist response"""

    added_at: datetime
    stock_name: Optional[str] = None
    current_price: Optional[int] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None

    class Config:
        from_attributes = True


class WatchlistBase(BaseModel):
    """Base watchlist schema"""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate watchlist name"""
        # Strip whitespace
        v = v.strip()

        # Check non-empty after stripping
        if not v:
            raise ValueError("Watchlist name cannot be empty or whitespace only")

        # Check for invalid characters
        if any(char in v for char in ["<", ">", "&", '"', "'"]):
            raise ValueError("Watchlist name contains invalid characters")

        return v


class WatchlistCreate(WatchlistBase):
    """Schema for creating a watchlist"""

    stock_codes: list[str] = Field(default_factory=list, max_length=100)

    @field_validator("stock_codes")
    @classmethod
    def validate_stock_codes(cls, v: list[str]) -> list[str]:
        """Validate stock codes"""
        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Duplicate stock codes in list")

        # Validate each code format
        for code in v:
            if not code or len(code) != 6 or not code.isdigit():
                raise ValueError(f"Invalid stock code format: {code}")

        return v


class WatchlistUpdate(BaseModel):
    """Schema for updating a watchlist"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    add_stocks: list[str] = Field(default_factory=list)
    remove_stocks: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate watchlist name"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Watchlist name cannot be empty or whitespace only")
            if any(char in v for char in ["<", ">", "&", '"', "'"]):
                raise ValueError("Watchlist name contains invalid characters")
        return v

    @field_validator("add_stocks", "remove_stocks")
    @classmethod
    def validate_stock_codes(cls, v: list[str]) -> list[str]:
        """Validate stock code lists"""
        for code in v:
            if not code or len(code) != 6 or not code.isdigit():
                raise ValueError(f"Invalid stock code format: {code}")
        return v


class WatchlistResponse(WatchlistBase):
    """Schema for watchlist response"""

    id: UUID
    user_id: int
    stock_count: int = 0
    created_at: datetime
    updated_at: datetime
    stocks: list[WatchlistStockResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class WatchlistSummary(BaseModel):
    """Schema for watchlist summary (without full stock list)"""

    id: UUID
    name: str
    description: Optional[str] = None
    stock_count: int = 0
    last_stock_added: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WatchlistListResponse(BaseModel):
    """Schema for paginated watchlist list"""

    total: int
    page: int
    limit: int
    watchlists: list[WatchlistSummary]


# ============================================================================
# USER ACTIVITY SCHEMAS
# ============================================================================


class UserActivityBase(BaseModel):
    """Base user activity schema"""

    activity_type: str = Field(
        ...,
        pattern="^(screening|watchlist_create|watchlist_update|watchlist_delete|"
        "stock_add|stock_remove|stock_view|login|logout)$",
    )
    description: str = Field(..., min_length=1, max_length=500)
    activity_metadata: Optional[dict[str, Any]] = None


class UserActivityCreate(UserActivityBase):
    """Schema for creating user activity log"""

    pass


class UserActivityResponse(UserActivityBase):
    """Schema for user activity response"""

    id: UUID
    user_id: int
    created_at: datetime

    # Additional fields for specific activity types
    result_count: Optional[int] = None
    watchlist_id: Optional[UUID] = None
    stock_code: Optional[str] = None

    class Config:
        from_attributes = True


class UserActivityListResponse(BaseModel):
    """Schema for paginated activity list"""

    total: int
    activities: list[UserActivityResponse]


# ============================================================================
# DASHBOARD SCHEMAS
# ============================================================================


class ScreeningQuota(BaseModel):
    """Schema for screening quota information"""

    used: int = 0
    limit: int = 100
    remaining: int = 100
    reset_at: datetime

    @classmethod
    def from_tier(cls, tier: str, used: int = 0, reset_at: Optional[datetime] = None):
        """Create quota from user tier"""
        limits = {"public": 10, "free": 100, "premium": 500, "enterprise": 2000}
        limit = limits.get(tier, 10)

        if reset_at is None:
            from datetime import datetime, timedelta

            reset_at = datetime.now() + timedelta(days=30)

        return cls(
            used=used, limit=limit, remaining=max(0, limit - used), reset_at=reset_at
        )


class DashboardSummary(BaseModel):
    """Schema for dashboard summary data"""

    watchlist_count: int = 0
    total_stocks: int = 0
    recent_activity_count: int = 0
    last_activity_at: Optional[datetime] = None
    subscription_tier: str = "free"
    screening_quota: ScreeningQuota

    class Config:
        from_attributes = True


# ============================================================================
# USER PREFERENCES SCHEMAS
# ============================================================================


class UserPreferencesBase(BaseModel):
    """Base user preferences schema"""

    default_watchlist_id: Optional[UUID] = None
    dashboard_layout: Optional[dict[str, Any]] = None
    notification_settings: Optional[dict[str, Any]] = None


class UserPreferencesCreate(UserPreferencesBase):
    """Schema for creating user preferences"""

    pass


class UserPreferencesUpdate(UserPreferencesBase):
    """Schema for updating user preferences"""

    pass


class UserPreferencesResponse(UserPreferencesBase):
    """Schema for user preferences response"""

    user_id: int
    screening_quota_used: int = 0
    screening_quota_reset_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
