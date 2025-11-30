"""Payment database model"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class PaymentStatus(str, Enum):
    """Payment status enum"""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"


class PaymentType(str, Enum):
    """Payment type enum"""

    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    REFUND = "refund"


class Payment(BaseModel):
    """Payment transaction model"""

    __tablename__ = "payments"

    # Foreign keys
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subscription_id = Column(
        Integer,
        ForeignKey("user_subscriptions.id", ondelete="SET NULL"),
        index=True,
    )

    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(
        String(20),
        nullable=False,
        default=PaymentStatus.PENDING.value,
        index=True,
    )
    payment_type = Column(
        String(30),
        nullable=False,
        default=PaymentType.SUBSCRIPTION.value,
    )

    # Stripe integration
    stripe_payment_intent_id = Column(String(255), unique=True, index=True)
    stripe_invoice_id = Column(String(255), index=True)
    stripe_charge_id = Column(String(255))

    # Failure information
    failure_code = Column(String(100))
    failure_message = Column(Text)

    # Refund information
    refund_amount = Column(Numeric(10, 2))
    refunded_at = Column(DateTime(timezone=True))

    # Timestamps
    paid_at = Column(DateTime(timezone=True))

    # Additional data (Note: 'metadata' is reserved in SQLAlchemy)
    payment_metadata = Column(JSONB, default=dict)

    # Relationships
    user = relationship("User", back_populates="payments")
    subscription = relationship("UserSubscription", back_populates="payments")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'succeeded', 'failed', "
            "'refunded', 'canceled')",
            name="valid_payment_status",
        ),
        CheckConstraint(
            "payment_type IN ('subscription', 'one_time', 'refund')",
            name="valid_payment_type",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount}, "
            f"status={self.status})>"
        )

    @property
    def is_successful(self) -> bool:
        """Check if payment was successful"""
        return self.status == PaymentStatus.SUCCEEDED.value

    @property
    def is_refunded(self) -> bool:
        """Check if payment was refunded"""
        return self.status == PaymentStatus.REFUNDED.value

    @property
    def is_pending(self) -> bool:
        """Check if payment is pending"""
        return self.status in (
            PaymentStatus.PENDING.value,
            PaymentStatus.PROCESSING.value,
        )

    @property
    def amount_decimal(self) -> Decimal:
        """Get amount as Decimal"""
        return Decimal(str(self.amount)) if self.amount else Decimal("0")

    @property
    def refund_amount_decimal(self) -> Optional[Decimal]:
        """Get refund amount as Decimal"""
        if self.refund_amount is None:
            return None
        return Decimal(str(self.refund_amount))

    @property
    def net_amount(self) -> Decimal:
        """Calculate net amount after refunds"""
        if self.refund_amount:
            return self.amount_decimal - self.refund_amount_decimal
        return self.amount_decimal

    def mark_as_succeeded(self) -> None:
        """Mark payment as succeeded"""
        self.status = PaymentStatus.SUCCEEDED.value
        self.paid_at = datetime.now(timezone.utc)

    def mark_as_failed(
        self, code: Optional[str] = None, message: Optional[str] = None
    ) -> None:
        """Mark payment as failed with optional error details"""
        self.status = PaymentStatus.FAILED.value
        self.failure_code = code
        self.failure_message = message

    def process_refund(self, amount: Optional[Decimal] = None) -> None:
        """
        Process a refund for this payment.

        Args:
            amount: Refund amount. If None, full refund is processed.
        """
        self.status = PaymentStatus.REFUNDED.value
        self.refund_amount = amount or self.amount
        self.refunded_at = datetime.now(timezone.utc)
