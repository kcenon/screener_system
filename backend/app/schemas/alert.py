"""Alert API schemas for request/response serialization.

This module defines Pydantic models for alert-related API operations including
creating, updating, and retrieving alerts.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class AlertBase(BaseModel):
    """Base schema for alert data"""

    stock_code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Stock code (e.g., '005930' for Samsung Electronics)",
        examples=["005930"],
    )
    alert_type: Literal[
        "PRICE_ABOVE",
        "PRICE_BELOW",
        "VOLUME_SPIKE",
        "CHANGE_PERCENT_ABOVE",
        "CHANGE_PERCENT_BELOW",
    ] = Field(
        ...,
        description="Type of alert condition",
        examples=["PRICE_ABOVE"],
    )
    condition_value: Decimal = Field(
        ...,
        gt=0,
        description="Threshold value for alert (price, volume multiplier, or percent)",
        examples=[70000],
    )
    is_recurring: bool = Field(
        default=False,
        description="Whether alert should reactivate after being triggered",
    )


class AlertCreate(AlertBase):
    """Schema for creating a new alert"""

    pass


class AlertUpdate(BaseModel):
    """Schema for updating an existing alert"""

    alert_type: Optional[
        Literal[
            "PRICE_ABOVE",
            "PRICE_BELOW",
            "VOLUME_SPIKE",
            "CHANGE_PERCENT_ABOVE",
            "CHANGE_PERCENT_BELOW",
        ]
    ] = Field(
        None,
        description="Type of alert condition",
    )
    condition_value: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Threshold value for alert",
    )
    is_recurring: Optional[bool] = Field(
        None,
        description="Whether alert should reactivate after being triggered",
    )


class AlertResponse(AlertBase):
    """Schema for alert response"""

    id: int = Field(..., description="Alert ID")
    user_id: int = Field(..., description="User ID who owns this alert")
    is_active: bool = Field(..., description="Whether alert is actively monitored")
    triggered_at: Optional[datetime] = Field(
        None,
        description="Timestamp when alert was last triggered",
    )
    triggered_value: Optional[Decimal] = Field(
        None,
        description="Value that triggered the alert",
    )
    created_at: datetime = Field(..., description="Alert creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic model configuration"""

        from_attributes = True


class AlertListResponse(BaseModel):
    """Schema for paginated alert list response"""

    items: list[AlertResponse] = Field(..., description="List of alerts")
    total: int = Field(..., description="Total number of alerts")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        """Pydantic model configuration"""

        from_attributes = True


class AlertToggleResponse(BaseModel):
    """Schema for alert toggle response"""

    id: int = Field(..., description="Alert ID")
    is_active: bool = Field(..., description="New active status")
    message: str = Field(..., description="Success message")

    class Config:
        """Pydantic model configuration"""

        from_attributes = True
