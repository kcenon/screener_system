"""Financial statement database model"""

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class FinancialStatement(Base, TimestampMixin):
    """Quarterly and annual financial statements model"""

    __tablename__ = "financial_statements"

    # Primary Key (auto-increment)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign Key
    stock_code = Column(
        String(6),
        ForeignKey("stocks.code", ondelete="CASCADE"),
        nullable=False,
    )

    # Period Information
    period_type = Column(String(10), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer, nullable=True)
    report_date = Column(Date, nullable=False)

    # Income Statement
    revenue = Column(BigInteger, nullable=True)
    cost_of_revenue = Column(BigInteger, nullable=True)
    gross_profit = Column(BigInteger, nullable=True)
    operating_expenses = Column(BigInteger, nullable=True)
    operating_profit = Column(BigInteger, nullable=True)
    non_operating_income = Column(BigInteger, nullable=True)
    non_operating_expenses = Column(BigInteger, nullable=True)
    ebt = Column(BigInteger, nullable=True)  # Earnings Before Tax
    tax_expense = Column(BigInteger, nullable=True)
    net_profit = Column(BigInteger, nullable=True)

    # Per Share Metrics
    eps = Column(Numeric(10, 2), nullable=True)  # Earnings Per Share
    bps = Column(Numeric(10, 2), nullable=True)  # Book Value Per Share
    dps = Column(Numeric(10, 2), nullable=True)  # Dividend Per Share

    # Balance Sheet
    current_assets = Column(BigInteger, nullable=True)
    non_current_assets = Column(BigInteger, nullable=True)
    total_assets = Column(BigInteger, nullable=True)
    current_liabilities = Column(BigInteger, nullable=True)
    non_current_liabilities = Column(BigInteger, nullable=True)
    total_liabilities = Column(BigInteger, nullable=True)
    equity = Column(BigInteger, nullable=True)

    # Cash Flow Statement
    operating_cash_flow = Column(BigInteger, nullable=True)
    investing_cash_flow = Column(BigInteger, nullable=True)
    financing_cash_flow = Column(BigInteger, nullable=True)
    free_cash_flow = Column(BigInteger, nullable=True)
    capital_expenditure = Column(BigInteger, nullable=True)

    # Relationships
    stock = relationship("Stock", back_populates="financial_statements")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "period_type IN ('quarterly', 'annual')",
            name="valid_period_type",
        ),
        CheckConstraint(
            "fiscal_year BETWEEN 1900 AND 2100",
            name="valid_fiscal_year",
        ),
        CheckConstraint(
            """
            (period_type = 'annual' AND fiscal_quarter IS NULL) OR
            (period_type = 'quarterly' AND fiscal_quarter IS NOT NULL)
            """,
            name="quarterly_has_quarter",
        ),
        # Unique constraint on stock_code, period_type, fiscal_year, fiscal_quarter
        # This is implicitly created by the database migration
    )

    def __repr__(self) -> str:
        """String representation"""
        quarter_str = f"Q{self.fiscal_quarter}" if self.fiscal_quarter else "Annual"
        return (
            f"<FinancialStatement(stock_code={self.stock_code}, "
            f"{self.fiscal_year}-{quarter_str}, revenue={self.revenue})>"
        )

    @property
    def is_quarterly(self) -> bool:
        """Check if this is a quarterly report"""
        return self.period_type == "quarterly"

    @property
    def is_annual(self) -> bool:
        """Check if this is an annual report"""
        return self.period_type == "annual"

    @property
    def gross_margin(self) -> Optional[Decimal]:
        """Calculate gross margin percentage"""
        if self.revenue and self.gross_profit and self.revenue > 0:
            return Decimal(self.gross_profit) / Decimal(self.revenue) * 100
        return None

    @property
    def operating_margin(self) -> Optional[Decimal]:
        """Calculate operating margin percentage"""
        if self.revenue and self.operating_profit and self.revenue > 0:
            return Decimal(self.operating_profit) / Decimal(self.revenue) * 100
        return None

    @property
    def net_margin(self) -> Optional[Decimal]:
        """Calculate net margin percentage"""
        if self.revenue and self.net_profit and self.revenue > 0:
            return Decimal(self.net_profit) / Decimal(self.revenue) * 100
        return None

    @property
    def debt_to_equity(self) -> Optional[Decimal]:
        """Calculate debt to equity ratio"""
        if self.total_liabilities and self.equity and self.equity > 0:
            return Decimal(self.total_liabilities) / Decimal(self.equity)
        return None

    @property
    def current_ratio(self) -> Optional[Decimal]:
        """Calculate current ratio"""
        if self.current_assets and self.current_liabilities and self.current_liabilities > 0:
            return Decimal(self.current_assets) / Decimal(self.current_liabilities)
        return None
