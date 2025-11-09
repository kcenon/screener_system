"""Stock database model"""

from datetime import date
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, Column, Date, String
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Stock(Base, TimestampMixin):
    """Stock master data model"""

    __tablename__ = "stocks"

    # Primary Key
    code = Column(String(6), primary_key=True)

    # Basic Information
    name = Column(String(100), nullable=False)
    name_english = Column(String(100), nullable=True)
    market = Column(String(10), nullable=False)
    sector = Column(String(50), nullable=True)
    industry = Column(String(100), nullable=True)

    # Listing Information
    listing_date = Column(Date, nullable=True)
    delisting_date = Column(Date, nullable=True)

    # Outstanding Shares
    shares_outstanding = Column(BigInteger, nullable=True)

    # Relationships
    daily_prices = relationship(
        "DailyPrice",
        back_populates="stock",
        cascade="all, delete-orphan",
        lazy="select",
    )

    financial_statements = relationship(
        "FinancialStatement",
        back_populates="stock",
        cascade="all, delete-orphan",
        lazy="select",
    )

    calculated_indicators = relationship(
        "CalculatedIndicator",
        back_populates="stock",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "market IN ('KOSPI', 'KOSDAQ')",
            name="valid_market",
        ),
        CheckConstraint(
            "LENGTH(code) = 6",
            name="valid_code_length",
        ),
        CheckConstraint(
            "shares_outstanding IS NULL OR shares_outstanding > 0",
            name="valid_shares",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return f"<Stock(code={self.code}, name={self.name}, market={self.market})>"

    @property
    def is_listed(self) -> bool:
        """Check if stock is currently listed"""
        return self.delisting_date is None

    @property
    def is_kospi(self) -> bool:
        """Check if stock is KOSPI"""
        return self.market == "KOSPI"

    @property
    def is_kosdaq(self) -> bool:
        """Check if stock is KOSDAQ"""
        return self.market == "KOSDAQ"

    def get_market_cap(self, price: int) -> Optional[int]:
        """Calculate market capitalization"""
        if self.shares_outstanding and price:
            return self.shares_outstanding * price
        return None
