"""Transaction database model"""

from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.portfolio import Portfolio  # noqa: F401
    from app.db.models.stock import Stock  # noqa: F401


class TransactionType(str, Enum):
    """Transaction type enumeration"""

    BUY = "BUY"
    SELL = "SELL"
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class Transaction(Base):
    """Transaction model for portfolio operations"""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(
        Integer,
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stock_code = Column(
        String(6),
        ForeignKey("stocks.code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_type = Column(
        String(10), nullable=False
    )  # 'BUY', 'SELL', 'DEPOSIT', 'WITHDRAW'
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)  # Total amount (quantity * price)
    transaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    commission = Column(Float, default=0.0)
    notes = Column(String(255), nullable=True)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions", lazy="select")
    stock = relationship("Stock", lazy="select")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('BUY', 'SELL')",
            name="valid_transaction_type",
        ),
        CheckConstraint(
            "quantity > 0",
            name="valid_quantity",
        ),
        CheckConstraint(
            "price >= 0",
            name="valid_price",
        ),
        CheckConstraint(
            "commission >= 0",
            name="valid_commission",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<Transaction(id={self.id}, type={self.transaction_type}, "
            f"code={self.stock_code}, amount={self.amount})>"
        )

    @property
    def transaction_value(self) -> Decimal:
        """Calculate transaction value (shares * price)"""
        return Decimal(str(self.shares)) * Decimal(str(self.price))

    @property
    def total_amount(self) -> Decimal:
        """Calculate total amount including commission"""
        if self.transaction_type == TransactionType.BUY.value:
            return self.transaction_value + Decimal(str(self.commission))
        else:  # SELL
            return self.transaction_value - Decimal(str(self.commission))

    @property
    def is_buy(self) -> bool:
        """Check if transaction is a buy"""
        return self.transaction_type == TransactionType.BUY.value

    @property
    def is_sell(self) -> bool:
        """Check if transaction is a sell"""
        return self.transaction_type == TransactionType.SELL.value
