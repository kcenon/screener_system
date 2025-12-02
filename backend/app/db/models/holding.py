"""Holding database model"""

from decimal import Decimal
from typing import TYPE_CHECKING

from app.db.base import BaseModel
from sqlalchemy import (CheckConstraint, Column, Float, ForeignKey, Integer,
                        String)
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from app.db.models.portfolio import Portfolio  # noqa: F401
    from app.db.models.stock import Stock  # noqa: F401


class Holding(BaseModel):
    """Stock holding model"""

    __tablename__ = "holdings"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
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

    # Position Information
    shares = Column(Integer, nullable=False, default=0)
    average_price = Column(Float, nullable=False, default=0.0)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    stock = relationship("Stock", back_populates="holdings")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "shares >= 0",
            name="positive_shares",
        ),
        CheckConstraint(
            "average_price >= 0",
            name="positive_average_price",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<Holding(id={self.id}, portfolio_id={self.portfolio_id}, "
            f"code={self.stock_code}, shares={self.shares})>"
        )

    def reduce_shares(self, shares_to_sell: int) -> None:
        """Reduce shares for sell transactions"""
        if shares_to_sell <= 0:
            raise ValueError("Shares to sell must be positive")
        if shares_to_sell > Decimal(str(self.shares)):
            raise ValueError(
                f"Cannot sell {shares_to_sell} shares, only {self.shares} available"
            )

        self.shares = Decimal(str(self.shares)) - shares_to_sell

        # If all shares sold, reset average cost
        if self.shares == 0:
            self.average_cost = Decimal("0")
