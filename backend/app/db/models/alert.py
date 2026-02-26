"""Alert database model"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (Boolean, CheckConstraint, Column, DateTime, ForeignKey,
                        Integer, Numeric, String)
from sqlalchemy.orm import relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.notification import Notification  # noqa: F401
    from app.db.models.stock import Stock  # noqa: F401
    from app.db.models.user import User  # noqa: F401


class Alert(BaseModel):
    """User-defined stock alert model"""

    __tablename__ = "alerts"

    # Foreign keys
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stock_code = Column(
        String(20),
        ForeignKey("stocks.code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Alert configuration
    alert_type = Column(
        String(30),
        nullable=False,
        index=True,
    )
    condition_value = Column(
        Numeric(18, 2),
        nullable=False,
    )

    # Alert status
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )
    is_recurring = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Trigger information
    triggered_at = Column(DateTime(timezone=True))
    triggered_value = Column(Numeric(18, 2))

    # Relationships
    user = relationship("User", back_populates="alerts", lazy="select")
    stock = relationship("Stock", lazy="select")
    notifications = relationship(
        "Notification",
        back_populates="alert",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "alert_type IN ('PRICE_ABOVE', 'PRICE_BELOW', 'VOLUME_SPIKE', "
            "'CHANGE_PERCENT_ABOVE', 'CHANGE_PERCENT_BELOW')",
            name="valid_alert_type",
        ),
        CheckConstraint(
            "condition_value > 0",
            name="positive_condition_value",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<Alert(id={self.id}, user_id={self.user_id}, "
            f"stock={self.stock_code}, type={self.alert_type}, "
            f"active={self.is_active})>"
        )

    def trigger(
        self,
        current_value: Decimal,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Mark alert as triggered"""
        from app.db.base import utc_now

        self.triggered_at = timestamp or utc_now()
        self.triggered_value = current_value

        # Deactivate if not recurring
        if not self.is_recurring:
            self.is_active = False

    def reset(self) -> None:
        """Reset triggered alert (for recurring alerts)"""
        self.triggered_at = None
        self.triggered_value = None
        self.is_active = True

    def toggle_active(self) -> None:
        """Toggle alert active status"""
        self.is_active = not self.is_active

    @property
    def is_triggered(self) -> bool:
        """Check if alert has been triggered"""
        return self.triggered_at is not None

    def should_trigger(self, current_price: Decimal, current_volume: int) -> bool:
        """
        Check if current market data meets alert condition

        Args:
            current_price: Current stock price
            current_volume: Current trading volume

        Returns:
            True if alert should be triggered
        """
        if not self.is_active:
            return False

        if self.alert_type == "PRICE_ABOVE":
            return current_price >= self.condition_value
        elif self.alert_type == "PRICE_BELOW":
            return current_price <= self.condition_value
        elif self.alert_type == "VOLUME_SPIKE":
            # condition_value represents multiplier (e.g., 2.0 for 2x average volume)
            # This would need average volume calculation from price data
            return False  # Implement when volume tracking is available
        elif self.alert_type in ("CHANGE_PERCENT_ABOVE", "CHANGE_PERCENT_BELOW"):
            # These require previous close price calculation
            return False  # Implement when price change tracking is available

        return False
