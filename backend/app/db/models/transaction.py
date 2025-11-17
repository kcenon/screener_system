"""Transaction database model"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    DECIMAL,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.portfolio import Portfolio
    from app.db.models.stock import Stock


class TransactionType(str, Enum):
    """Transaction type enumeration"""

    BUY = "BUY"
    SELL = "SELL"


class Transaction(Base, TimestampMixin):
    """Transaction model for buy/sell activities"""

    __tablename__ = "transactions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign Keys
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    stock_symbol = Column(String(20), ForeignKey("stocks.code", ondelete="RESTRICT"), nullable=False, index=True)

    # Transaction Details
    transaction_type = Column(String(10), nullable=False, index=True)
    shares = Column(DECIMAL(18, 8), nullable=False)
    price = Column(DECIMAL(18, 2), nullable=False)
    commission = Column(DECIMAL(18, 2), nullable=False, default=0, server_default="0")
    transaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    notes = Column(Text, nullable=True)

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
            "shares > 0",
            name="valid_shares",
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
        return f"<Transaction(id={self.id}, type={self.transaction_type}, stock={self.stock_symbol}, shares={self.shares}, price={self.price})>"

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
