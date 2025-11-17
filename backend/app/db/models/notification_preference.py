"""Notification preference database model"""

from datetime import time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.user import User


class NotificationPreference(BaseModel):
    """User notification preferences model"""

    __tablename__ = "notification_preferences"

    # Foreign key
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Channel preferences
    email_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    push_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    in_app_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # Type-specific email preferences
    alert_email = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    market_event_email = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    system_email = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    portfolio_email = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Digest preferences
    daily_digest_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    weekly_digest_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Quiet hours
    quiet_hours_start = Column(Time)
    quiet_hours_end = Column(Time)
    quiet_hours_timezone = Column(
        String(50),
        default="Asia/Seoul",
        server_default="Asia/Seoul",
    )

    # Relationship
    user = relationship(
        "User",
        back_populates="notification_preference",
        lazy="select",
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<NotificationPreference(id={self.id}, user_id={self.user_id}, "
            f"email={self.email_enabled}, push={self.push_enabled})>"
        )

    def should_send_email(self, notification_type: str) -> bool:
        """
        Check if email should be sent for given notification type

        Args:
            notification_type: Type of notification (ALERT, MARKET_EVENT, SYSTEM, PORTFOLIO)

        Returns:
            True if email should be sent
        """
        if not self.email_enabled:
            return False

        type_preferences = {
            "ALERT": self.alert_email,
            "MARKET_EVENT": self.market_event_email,
            "SYSTEM": self.system_email,
            "PORTFOLIO": self.portfolio_email,
        }

        return type_preferences.get(notification_type, False)

    def should_send_push(self) -> bool:
        """Check if push notifications are enabled"""
        return self.push_enabled

    def should_send_in_app(self) -> bool:
        """Check if in-app notifications are enabled"""
        return self.in_app_enabled

    def is_in_quiet_hours(self, current_time: Optional[time] = None) -> bool:
        """
        Check if current time is within quiet hours

        Args:
            current_time: Time to check (default: now in user's timezone)

        Returns:
            True if in quiet hours
        """
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False

        if current_time is None:
            from datetime import datetime

            from app.db.base import utc_now

            current_time = utc_now().time()

        start = self.quiet_hours_start
        end = self.quiet_hours_end

        # Handle overnight quiet hours (e.g., 22:00 - 08:00)
        if start < end:
            return start <= current_time <= end
        else:
            return current_time >= start or current_time <= end

    def enable_all_channels(self) -> None:
        """Enable all notification channels"""
        self.email_enabled = True
        self.push_enabled = True
        self.in_app_enabled = True

    def disable_all_channels(self) -> None:
        """Disable all notification channels"""
        self.email_enabled = False
        self.push_enabled = False
        self.in_app_enabled = False

    def enable_all_email_types(self) -> None:
        """Enable all email notification types"""
        self.alert_email = True
        self.market_event_email = True
        self.system_email = True
        self.portfolio_email = True

    def disable_all_email_types(self) -> None:
        """Disable all email notification types"""
        self.alert_email = False
        self.market_event_email = False
        self.system_email = False
        self.portfolio_email = False

    @classmethod
    def create_default(cls, user_id: int) -> "NotificationPreference":
        """
        Create default notification preferences for a user

        Args:
            user_id: User ID

        Returns:
            New NotificationPreference instance with defaults
        """
        return cls(
            user_id=user_id,
            email_enabled=True,
            push_enabled=False,
            in_app_enabled=True,
            alert_email=True,
            market_event_email=True,
            system_email=True,
            portfolio_email=False,
            daily_digest_enabled=False,
            weekly_digest_enabled=False,
            quiet_hours_timezone="Asia/Seoul",
        )
