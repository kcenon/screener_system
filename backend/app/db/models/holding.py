"""Holding database model"""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DECIMAL,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.portfolio import Portfolio
    from app.db.models.stock import Stock


class Holding(BaseModel):
    """Holding model for stock positions within portfolios"""

    __tablename__ = "holdings"

    # Foreign Keys
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    stock_symbol = Column(String(20), ForeignKey("stocks.symbol", ondelete="RESTRICT"), nullable=False, index=True)

    # Position Information
    shares = Column(DECIMAL(18, 8), nullable=False)
    average_cost = Column(DECIMAL(18, 2), nullable=False)

    # Tracking
    first_purchase_date = Column(Date, nullable=True)
    last_update_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings", lazy="select")
    stock = relationship("Stock", lazy="select")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "shares >= 0",
            name="valid_shares",
        ),
        CheckConstraint(
            "average_cost >= 0",
            name="valid_average_cost",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return f"<Holding(id={self.id}, portfolio_id={self.portfolio_id}, stock={self.stock_symbol}, shares={self.shares})>"

    @property
    def total_cost(self) -> Decimal:
        """Calculate total cost basis (shares * average_cost)"""
        return Decimal(str(self.shares)) * Decimal(str(self.average_cost))

    def calculate_current_value(self, current_price: Decimal) -> Decimal:
        """Calculate current value based on price"""
        return Decimal(str(self.shares)) * current_price

    def calculate_unrealized_gain(self, current_price: Decimal) -> Decimal:
        """Calculate unrealized gain/loss"""
        return self.calculate_current_value(current_price) - self.total_cost

    def calculate_return_percent(self, current_price: Decimal) -> Decimal:
        """Calculate return percentage"""
        if self.average_cost == 0:
            return Decimal("0")
        return ((current_price - Decimal(str(self.average_cost))) / Decimal(str(self.average_cost))) * Decimal("100")

    def update_average_cost(self, new_shares: Decimal, new_price: Decimal) -> None:
        """Update average cost using weighted average for buy transactions"""
        if new_shares <= 0:
            raise ValueError("New shares must be positive")

        current_total_cost = self.total_cost
        new_total_cost = new_shares * new_price
        total_shares = Decimal(str(self.shares)) + new_shares

        if total_shares > 0:
            self.average_cost = (current_total_cost + new_total_cost) / total_shares
            self.shares = total_shares
        else:
            # If all shares sold, reset
            self.shares = Decimal("0")
            self.average_cost = Decimal("0")

    def reduce_shares(self, shares_to_sell: Decimal) -> None:
        """Reduce shares for sell transactions"""
        if shares_to_sell <= 0:
            raise ValueError("Shares to sell must be positive")
        if shares_to_sell > Decimal(str(self.shares)):
            raise ValueError(f"Cannot sell {shares_to_sell} shares, only {self.shares} available")

        self.shares = Decimal(str(self.shares)) - shares_to_sell

        # If all shares sold, reset average cost
        if self.shares == 0:
            self.average_cost = Decimal("0")
