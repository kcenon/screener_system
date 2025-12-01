"""Payment method database model"""

from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    JSON,
)
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class PaymentMethodType(str, Enum):
    """Payment method type enum"""

    CARD = "card"
    BANK_ACCOUNT = "bank_account"
    SEPA_DEBIT = "sepa_debit"
    IDEAL = "ideal"


class PaymentMethod(BaseModel):
    """Payment method model for storing customer payment methods"""

    __tablename__ = "payment_methods"

    # Foreign key
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Stripe integration
    stripe_payment_method_id = Column(
        String(255), nullable=False, unique=True, index=True
    )

    # Payment method details
    type = Column(
        String(30),
        nullable=False,
        default=PaymentMethodType.CARD.value,
    )
    is_default = Column(Boolean, default=False)

    # Card details (masked)
    card_brand = Column(String(30))  # visa, mastercard, amex, etc.
    card_last4 = Column(String(4))
    card_exp_month = Column(Integer)
    card_exp_year = Column(Integer)

    # Billing details
    billing_name = Column(String(255))
    billing_email = Column(String(255))

    # Additional data (Note: 'metadata' is reserved in SQLAlchemy)
    method_metadata = Column(JSON, default=dict)

    # Relationships
    user = relationship("User", back_populates="payment_methods")
    payments = relationship(
        "Payment",
        back_populates="payment_method",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('card', 'bank_account', 'sepa_debit', 'ideal')",
            name="valid_payment_method_type",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<PaymentMethod(id={self.id}, user_id={self.user_id}, "
            f"type={self.type}, last4={self.card_last4})>"
        )

    @property
    def display_name(self) -> str:
        """Get display name for the payment method"""
        if self.type == PaymentMethodType.CARD.value and self.card_brand:
            return f"{self.card_brand.capitalize()} ****{self.card_last4}"
        return (
            f"{self.type} ending in {self.card_last4}"
            if self.card_last4
            else self.type
        )

    @property
    def is_expired(self) -> bool:
        """Check if card is expired"""
        if not self.card_exp_year or not self.card_exp_month:
            return False
        from datetime import date

        today = date.today()
        return (
            self.card_exp_year < today.year
            or (self.card_exp_year == today.year and self.card_exp_month < today.month)
        )

    @property
    def expiry_string(self) -> Optional[str]:
        """Get expiry date as string (MM/YY)"""
        if self.card_exp_month and self.card_exp_year:
            year_short = str(self.card_exp_year)[-2:]
            return f"{self.card_exp_month:02d}/{year_short}"
        return None

    def set_as_default(self) -> None:
        """Mark this payment method as default"""
        self.is_default = True
