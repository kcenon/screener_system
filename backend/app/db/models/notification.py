"""Notification database model"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app.db.base import Base
from sqlalchemy import (Boolean, CheckConstraint, Column, DateTime, ForeignKey,
                        Integer, String, Text, text)
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from app.db.models.alert import Alert  # noqa: F401
    from app.db.models.user import User  # noqa: F401


class Notification(Base):
    """User notification model"""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign keys
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    alert_id = Column(
        Integer,
        ForeignKey("alerts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Notification content
    notification_type = Column(
        String(20),
        nullable=False,
        index=True,
    )
    title = Column(
        String(200),
        nullable=False,
    )
    message = Column(
        Text,
        nullable=False,
    )
    priority = Column(
        String(10),
        nullable=False,
        default="NORMAL",
        server_default="NORMAL",
    )

    # Read status
    is_read = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True,
    )
    read_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
    )

    # Relationships
    user = relationship("User", back_populates="notifications", lazy="select")
    alert = relationship("Alert", back_populates="notifications", lazy="select")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "notification_type IN ('ALERT', 'MARKET_EVENT', 'SYSTEM', 'PORTFOLIO')",
            name="valid_notification_type",
        ),
        CheckConstraint(
            "priority IN ('LOW', 'NORMAL', 'HIGH', 'URGENT')",
            name="valid_priority",
        ),
        CheckConstraint(
            "(is_read = FALSE AND read_at IS NULL) OR "
            "(is_read = TRUE AND read_at IS NOT NULL)",
            name="read_at_requires_is_read",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<Notification(id={self.id}, user_id={self.user_id}, "
            f"type={self.notification_type}, read={self.is_read})>"
        )

    def mark_as_read(self, timestamp: Optional[datetime] = None) -> None:
        """Mark notification as read"""
        from app.db.base import utc_now

        if not self.is_read:
            self.is_read = True
            self.read_at = timestamp or utc_now()

    def mark_as_unread(self) -> None:
        """Mark notification as unread"""
        self.is_read = False
        self.read_at = None

    @property
    def is_urgent(self) -> bool:
        """Check if notification is urgent"""
        return self.priority == "URGENT"

    @property
    def is_from_alert(self) -> bool:
        """Check if notification is from an alert"""
        return self.alert_id is not None

    @classmethod
    def create_from_alert(
        cls,
        user_id: int,
        alert_id: int,
        title: str,
        message: str,
        priority: str = "HIGH",
    ) -> "Notification":
        """
        Create notification from alert trigger

        Args:
            user_id: User ID
            alert_id: Alert ID that triggered this notification
            title: Notification title
            message: Notification message
            priority: Priority level (default: HIGH)

        Returns:
            New Notification instance
        """
        return cls(
            user_id=user_id,
            alert_id=alert_id,
            notification_type="ALERT",
            title=title,
            message=message,
            priority=priority,
        )

    @classmethod
    def create_system_notification(
        cls,
        user_id: int,
        title: str,
        message: str,
        priority: str = "NORMAL",
    ) -> "Notification":
        """
        Create system notification

        Args:
            user_id: User ID
            title: Notification title
            message: Notification message
            priority: Priority level (default: NORMAL)

        Returns:
            New Notification instance
        """
        return cls(
            user_id=user_id,
            notification_type="SYSTEM",
            title=title,
            message=message,
            priority=priority,
        )
