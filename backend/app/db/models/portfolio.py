"""Portfolio database model"""

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.holding import Holding  # noqa: F401
    from app.db.models.transaction import Transaction  # noqa: F401
    from app.db.models.user import User  # noqa: F401


class Portfolio(Base, TimestampMixin):
    """Portfolio model for user stock holdings"""

    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic Information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship(
        "Holding",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )
    transactions = relationship(
        "Transaction",
        back_populates="portfolio",
        cascade="all, delete-orphan",
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

    def has_holding(self, stock_symbol: str) -> bool:
        """Check if portfolio has holding for stock"""
        holding = self.get_holding(stock_symbol)
        return holding is not None and holding.shares > 0
