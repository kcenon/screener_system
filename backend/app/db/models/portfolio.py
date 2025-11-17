"""Portfolio database model"""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.holding import Holding
    from app.db.models.transaction import Transaction
    from app.db.models.user import User


class Portfolio(BaseModel):
    """Portfolio model for tracking user stock holdings"""

    __tablename__ = "portfolios"

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Basic Information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False, server_default="false", nullable=False)

    # Relationships
    user = relationship("User", back_populates="portfolios", lazy="select")
    holdings = relationship(
        "Holding",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        lazy="select",
    )
    transactions = relationship(
        "Transaction",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="Transaction.transaction_date.desc()",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "LENGTH(TRIM(name)) >= 1",
            name="valid_portfolio_name",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return f"<Portfolio(id={self.id}, user_id={self.user_id}, name={self.name})>"

    @property
    def holding_count(self) -> int:
        """Get number of active holdings"""
        return len([h for h in self.holdings if h.shares > 0])

    @property
    def total_cost(self) -> float:
        """Calculate total cost basis of all holdings"""
        return sum(h.total_cost for h in self.holdings if h.shares > 0)

    def get_holding(self, stock_symbol: str) -> Optional["Holding"]:
        """Get holding by stock symbol"""
        return next((h for h in self.holdings if h.stock_symbol == stock_symbol), None)

    def has_holding(self, stock_symbol: str) -> bool:
        """Check if portfolio has holding for stock"""
        holding = self.get_holding(stock_symbol)
        return holding is not None and holding.shares > 0
