"""Notification API schemas for request/response serialization.

This module defines Pydantic models for notification-related API operations including
retrieving, marking as read, and managing notification preferences.
"""

from datetime import datetime, time
from typing import Literal, Optional

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """Schema for notification response"""

    id: int = Field(..., description="Notification ID")
    user_id: int = Field(..., description="User ID who owns this notification")
    alert_id: Optional[int] = Field(
        None,
        description="Alert ID if notification was created from an alert",
    )
    notification_type: Literal["ALERT", "MARKET_EVENT", "SYSTEM", "PORTFOLIO"] = Field(
        ...,
        description="Type of notification",
    )
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    priority: Literal["LOW", "NORMAL", "HIGH", "URGENT"] = Field(
        ...,
        description="Priority level",
    )
    is_read: bool = Field(..., description="Whether notification has been read")
    read_at: Optional[datetime] = Field(
        None,
        description="Timestamp when notification was marked as read",
    )
    created_at: datetime = Field(..., description="Notification creation timestamp")

    class Config:
        """Pydantic model configuration"""

        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list response"""

    items: list[NotificationResponse] = Field(..., description="List of notifications")
    total: int = Field(..., description="Total number of notifications")
    unread_count: int = Field(..., description="Number of unread notifications")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        """Pydantic model configuration"""

        from_attributes = True


class NotificationUnreadCountResponse(BaseModel):
    """Schema for unread notification count response"""

    unread_count: int = Field(..., description="Number of unread notifications")

    class Config:
        """Pydantic model configuration"""

        from_attributes = True


class NotificationMarkReadResponse(BaseModel):
    """Schema for mark as read response"""

    id: int = Field(..., description="Notification ID")
    is_read: bool = Field(..., description="Read status (should be True)")
    read_at: datetime = Field(..., description="Timestamp when marked as read")
    message: str = Field(..., description="Success message")

    class Config:
        """Pydantic model configuration"""

        from_attributes = True


class NotificationMarkAllReadResponse(BaseModel):
    """Schema for mark all as read response"""

    marked_count: int = Field(..., description="Number of notifications marked as read")
    message: str = Field(..., description="Success message")

    class Config:
        """Pydantic model configuration"""

        from_attributes = True


class NotificationDeleteResponse(BaseModel):
    """Schema for notification deletion response"""

    id: int = Field(..., description="Deleted notification ID")
    message: str = Field(..., description="Success message")

    class Config:
        """Pydantic model configuration"""

        from_attributes = True


class NotificationPreferenceResponse(BaseModel):
    """Schema for notification preference response"""

    id: int = Field(..., description="Preference ID")
    user_id: int = Field(..., description="User ID")

    # Channel preferences
    email_enabled: bool = Field(..., description="Email notifications enabled")
    push_enabled: bool = Field(..., description="Push notifications enabled")
    in_app_enabled: bool = Field(..., description="In-app notifications enabled")

    # Type-specific email preferences
    alert_email: bool = Field(..., description="Email for alert notifications")
    market_event_email: bool = Field(
        ...,
        description="Email for market event notifications",
    )
    system_email: bool = Field(..., description="Email for system notifications")
    portfolio_email: bool = Field(
        ...,
        description="Email for portfolio notifications",
    )

    # Digest preferences
    daily_digest_enabled: bool = Field(..., description="Daily digest enabled")
    weekly_digest_enabled: bool = Field(..., description="Weekly digest enabled")

    # Quiet hours
    quiet_hours_start: Optional[time] = Field(
        None,
        description="Start time for quiet hours",
    )
    quiet_hours_end: Optional[time] = Field(
        None,
        description="End time for quiet hours",
    )
    quiet_hours_timezone: str = Field(
        ...,
        description="Timezone for quiet hours",
    )

    created_at: datetime = Field(..., description="Preference creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic model configuration"""

        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences"""

    # Channel preferences
    email_enabled: Optional[bool] = Field(
        None,
        description="Email notifications enabled",
    )
    push_enabled: Optional[bool] = Field(
        None,
        description="Push notifications enabled",
    )
    in_app_enabled: Optional[bool] = Field(
        None,
        description="In-app notifications enabled",
    )

    # Type-specific email preferences
    alert_email: Optional[bool] = Field(
        None,
        description="Email for alert notifications",
    )
    market_event_email: Optional[bool] = Field(
        None,
        description="Email for market event notifications",
    )
    system_email: Optional[bool] = Field(
        None,
        description="Email for system notifications",
    )
    portfolio_email: Optional[bool] = Field(
        None,
        description="Email for portfolio notifications",
    )

    # Digest preferences
    daily_digest_enabled: Optional[bool] = Field(
        None,
        description="Daily digest enabled",
    )
    weekly_digest_enabled: Optional[bool] = Field(
        None,
        description="Weekly digest enabled",
    )

    # Quiet hours
    quiet_hours_start: Optional[time] = Field(
        None,
        description="Start time for quiet hours (format: HH:MM)",
    )
    quiet_hours_end: Optional[time] = Field(
        None,
        description="End time for quiet hours (format: HH:MM)",
    )
    quiet_hours_timezone: Optional[str] = Field(
        None,
        description="Timezone for quiet hours (e.g., 'Asia/Seoul')",
    )
