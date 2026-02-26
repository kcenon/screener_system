"""Usage tracking database model"""

from datetime import date
from enum import Enum

from sqlalchemy import (JSON, CheckConstraint, Column, Date, ForeignKey,
                        Integer, String, UniqueConstraint)
# from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class ResourceType(str, Enum):
    """Resource type enum for usage tracking"""

    SCREENING = "screening"
    API_CALL = "api_call"
    ALERT = "alert"
    EXPORT = "export"
    PORTFOLIO = "portfolio"


class PeriodType(str, Enum):
    """Period type enum for usage aggregation"""

    DAILY = "daily"
    MONTHLY = "monthly"


class UsageTracking(BaseModel):
    """Usage tracking model for rate limiting and analytics"""

    __tablename__ = "usage_tracking"

    # Foreign key
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Usage details
    resource_type = Column(String(50), nullable=False, index=True)
    count = Column(Integer, nullable=False, default=1)
    period_start = Column(Date, nullable=False, index=True)
    period_type = Column(
        String(20),
        nullable=False,
        default=PeriodType.DAILY.value,
    )

    # Additional data (Note: 'metadata' is reserved in SQLAlchemy)
    tracking_metadata = Column(JSON, default=dict)

    # Relationships
    user = relationship("User", back_populates="usage_records")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "resource_type",
            "period_start",
            "period_type",
            name="unique_user_resource_period",
        ),
        CheckConstraint(
            "period_type IN ('daily', 'monthly')",
            name="valid_period_type",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<UsageTracking(user_id={self.user_id}, resource={self.resource_type}, "
            f"count={self.count}, period={self.period_start})>"
        )

    @classmethod
    def get_current_period_start(cls, period_type: str = "daily") -> date:
        """
        Get the start date for the current period.

        Args:
            period_type: 'daily' or 'monthly'

        Returns:
            Start date for the period
        """
        today = date.today()
        if period_type == "monthly":
            return today.replace(day=1)
        return today

    def increment(self, amount: int = 1) -> int:
        """
        Increment usage count.

        Args:
            amount: Amount to increment by

        Returns:
            New count value
        """
        self.count += amount
        return self.count

    def reset(self) -> None:
        """Reset usage count to zero"""
        self.count = 0
