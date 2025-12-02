"""User subscription database model"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from app.db.base import BaseModel
from sqlalchemy import (JSON, Boolean, CheckConstraint, Column, DateTime,
                        ForeignKey, Integer, String)
# from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship


class SubscriptionStatus(str, Enum):
    """Subscription status enum"""

    ACTIVE = "active"
    CANCELED = "canceled"
    EXPIRED = "expired"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    INCOMPLETE = "incomplete"


class BillingCycle(str, Enum):
    """Billing cycle enum"""

    MONTHLY = "monthly"
    YEARLY = "yearly"


class UserSubscription(BaseModel):
    """User subscription model linking users to their subscription plans"""

    __tablename__ = "user_subscriptions"

    # Foreign keys
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)

    # Subscription details
    status = Column(
        String(20),
        nullable=False,
        default=SubscriptionStatus.ACTIVE.value,
        index=True,
    )
    billing_cycle = Column(
        String(20),
        nullable=False,
        default=BillingCycle.MONTHLY.value,
    )

    # Billing period
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False, index=True)

    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime(timezone=True))

    # Trial period
    trial_start = Column(DateTime(timezone=True))
    trial_end = Column(DateTime(timezone=True))

    # Stripe integration
    stripe_subscription_id = Column(String(255), unique=True, index=True)
    stripe_customer_id = Column(String(255), index=True)
    stripe_price_id = Column(String(255))

    # Additional data (Note: 'metadata' is reserved in SQLAlchemy)
    subscription_metadata = Column(JSON, default=dict)

    # Relationships
    user = relationship("User", back_populates="subscription")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    payments = relationship(
        "Payment",
        back_populates="subscription",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'canceled', 'expired', 'trial', 'past_due', "
            "'incomplete')",
            name="valid_subscription_status",
        ),
        CheckConstraint(
            "billing_cycle IN ('monthly', 'yearly')",
            name="valid_billing_cycle",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<UserSubscription(user_id={self.user_id}, status={self.status}, "
            f"plan_id={self.plan_id})>"
        )

    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        return self.status in (
            SubscriptionStatus.ACTIVE.value,
            SubscriptionStatus.TRIAL.value,
        )

    @property
    def is_trial(self) -> bool:
        """Check if subscription is in trial period"""
        return self.status == SubscriptionStatus.TRIAL.value

    @property
    def is_canceled(self) -> bool:
        """Check if subscription is canceled"""
        return self.status == SubscriptionStatus.CANCELED.value

    @property
    def is_expired(self) -> bool:
        """Check if subscription has expired"""
        now = datetime.now(timezone.utc)
        return (
            self.current_period_end < now
            or self.status == SubscriptionStatus.EXPIRED.value
        )

    @property
    def days_until_renewal(self) -> int:
        """Calculate days until next renewal/expiration"""
        now = datetime.now(timezone.utc)
        if self.current_period_end < now:
            return 0
        delta = self.current_period_end - now
        return delta.days

    @property
    def trial_days_remaining(self) -> Optional[int]:
        """Calculate remaining trial days"""
        if not self.is_trial or not self.trial_end:
            return None
        now = datetime.now(timezone.utc)
        if self.trial_end < now:
            return 0
        delta = self.trial_end - now
        return delta.days

    def mark_as_canceled(self, immediate: bool = False) -> None:
        """
        Mark subscription as canceled.

        Args:
            immediate: If True, cancel immediately. Otherwise, cancel at period end.
        """
        self.canceled_at = datetime.now(timezone.utc)
        if immediate:
            self.status = SubscriptionStatus.CANCELED.value
        else:
            self.cancel_at_period_end = True

    def mark_as_expired(self) -> None:
        """Mark subscription as expired"""
        self.status = SubscriptionStatus.EXPIRED.value

    def renew(self, new_period_end: datetime) -> None:
        """
        Renew subscription for another billing period.

        Args:
            new_period_end: New period end date
        """
        self.current_period_start = self.current_period_end
        self.current_period_end = new_period_end
        self.status = SubscriptionStatus.ACTIVE.value
        self.cancel_at_period_end = False

    def upgrade_to_plan(self, new_plan_id: int) -> None:
        """
        Upgrade/downgrade to a different plan.

        Args:
            new_plan_id: ID of the new plan
        """
        self.plan_id = new_plan_id
        # Reset trial if upgrading from trial
        if self.is_trial:
            self.status = SubscriptionStatus.ACTIVE.value
            self.trial_end = None
