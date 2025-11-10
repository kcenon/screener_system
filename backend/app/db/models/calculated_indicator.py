"""Calculated indicator database model"""


from sqlalchemy import (BigInteger, CheckConstraint, Column, Date, ForeignKey,
                        Integer, Numeric, String)
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class CalculatedIndicator(Base, TimestampMixin):
    """Pre-calculated 200+ indicators for fast screening"""

    __tablename__ = "calculated_indicators"

    # Composite Primary Key
    stock_code = Column(
        String(6),
        ForeignKey("stocks.code", ondelete="CASCADE"),
        primary_key=True,
    )
    calculation_date = Column(Date, primary_key=True)

    # Valuation Metrics
    per = Column(Numeric(10, 2), nullable=True)  # Price-to-Earnings Ratio
    pbr = Column(Numeric(10, 2), nullable=True)  # Price-to-Book Ratio
    psr = Column(Numeric(10, 2), nullable=True)  # Price-to-Sales Ratio
    pcr = Column(Numeric(10, 2), nullable=True)  # Price-to-Cash Flow Ratio
    ev_ebitda = Column(Numeric(10, 2), nullable=True)
    ev_sales = Column(Numeric(10, 2), nullable=True)
    ev_fcf = Column(Numeric(10, 2), nullable=True)
    dividend_yield = Column(Numeric(5, 2), nullable=True)
    payout_ratio = Column(Numeric(5, 2), nullable=True)
    peg_ratio = Column(Numeric(10, 2), nullable=True)

    # Profitability Metrics
    roe = Column(Numeric(5, 2), nullable=True)  # Return on Equity (%)
    roa = Column(Numeric(5, 2), nullable=True)  # Return on Assets (%)
    roic = Column(Numeric(5, 2), nullable=True)  # Return on Invested Capital (%)
    gross_margin = Column(Numeric(5, 2), nullable=True)
    operating_margin = Column(Numeric(5, 2), nullable=True)
    net_margin = Column(Numeric(5, 2), nullable=True)
    ebitda_margin = Column(Numeric(5, 2), nullable=True)
    fcf_margin = Column(Numeric(5, 2), nullable=True)

    # Growth Metrics (YoY %)
    revenue_growth_yoy = Column(Numeric(6, 2), nullable=True)
    profit_growth_yoy = Column(Numeric(6, 2), nullable=True)
    eps_growth_yoy = Column(Numeric(6, 2), nullable=True)
    revenue_growth_qoq = Column(Numeric(6, 2), nullable=True)
    profit_growth_qoq = Column(Numeric(6, 2), nullable=True)
    revenue_cagr_3y = Column(Numeric(6, 2), nullable=True)
    revenue_cagr_5y = Column(Numeric(6, 2), nullable=True)
    eps_cagr_3y = Column(Numeric(6, 2), nullable=True)
    eps_cagr_5y = Column(Numeric(6, 2), nullable=True)

    # Stability Metrics
    debt_to_equity = Column(Numeric(6, 2), nullable=True)
    debt_to_assets = Column(Numeric(6, 2), nullable=True)
    interest_coverage = Column(Numeric(6, 2), nullable=True)
    current_ratio = Column(Numeric(5, 2), nullable=True)
    quick_ratio = Column(Numeric(5, 2), nullable=True)
    cash_ratio = Column(Numeric(5, 2), nullable=True)
    altman_z_score = Column(Numeric(5, 2), nullable=True)
    piotroski_f_score = Column(Integer, nullable=True)

    # Efficiency Metrics
    asset_turnover = Column(Numeric(5, 2), nullable=True)
    inventory_turnover = Column(Numeric(5, 2), nullable=True)
    receivables_turnover = Column(Numeric(5, 2), nullable=True)
    payables_turnover = Column(Numeric(5, 2), nullable=True)
    cash_conversion_cycle = Column(Integer, nullable=True)  # Days

    # Technical Metrics
    price_change_1d = Column(Numeric(5, 2), nullable=True)
    price_change_1w = Column(Numeric(5, 2), nullable=True)
    price_change_1m = Column(Numeric(5, 2), nullable=True)
    price_change_3m = Column(Numeric(5, 2), nullable=True)
    price_change_6m = Column(Numeric(5, 2), nullable=True)
    price_change_1y = Column(Numeric(5, 2), nullable=True)
    price_change_3y = Column(Numeric(6, 2), nullable=True)
    price_change_5y = Column(Numeric(6, 2), nullable=True)
    volume_20d_avg = Column(BigInteger, nullable=True)
    volume_60d_avg = Column(BigInteger, nullable=True)
    volume_surge_pct = Column(Numeric(6, 2), nullable=True)

    # Moving Averages
    ma_5d = Column(Numeric(10, 2), nullable=True)
    ma_20d = Column(Numeric(10, 2), nullable=True)
    ma_60d = Column(Numeric(10, 2), nullable=True)
    ma_120d = Column(Numeric(10, 2), nullable=True)
    ma_200d = Column(Numeric(10, 2), nullable=True)

    # Technical Indicators
    rsi_14d = Column(Numeric(5, 2), nullable=True)
    macd = Column(Numeric(10, 2), nullable=True)
    macd_signal = Column(Numeric(10, 2), nullable=True)
    bollinger_upper = Column(Numeric(10, 2), nullable=True)
    bollinger_lower = Column(Numeric(10, 2), nullable=True)

    # Composite Scores (1-100)
    quality_score = Column(Integer, nullable=True)
    value_score = Column(Integer, nullable=True)
    growth_score = Column(Integer, nullable=True)
    momentum_score = Column(Integer, nullable=True)
    overall_score = Column(Integer, nullable=True)

    # Relationships
    stock = relationship("Stock", back_populates="calculated_indicators")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "rsi_14d BETWEEN 0 AND 100",
            name="valid_rsi",
        ),
        CheckConstraint(
            "piotroski_f_score BETWEEN 0 AND 9",
            name="valid_piotroski",
        ),
        CheckConstraint(
            "quality_score BETWEEN 1 AND 100",
            name="valid_quality_score",
        ),
        CheckConstraint(
            "value_score BETWEEN 1 AND 100",
            name="valid_value_score",
        ),
        CheckConstraint(
            "growth_score BETWEEN 1 AND 100",
            name="valid_growth_score",
        ),
        CheckConstraint(
            "momentum_score BETWEEN 1 AND 100",
            name="valid_momentum_score",
        ),
        CheckConstraint(
            "overall_score BETWEEN 1 AND 100",
            name="valid_overall_score",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<CalculatedIndicator(stock_code={self.stock_code}, "
            f"date={self.calculation_date}, overall_score={self.overall_score})>"
        )

    @property
    def is_undervalued(self) -> bool:
        """Check if stock appears undervalued based on PER and PBR"""
        # Simple heuristic: PER < 15 and PBR < 1.5
        return (
            self.per is not None
            and self.pbr is not None
            and self.per < 15
            and self.pbr < 1.5
        )

    @property
    def is_high_quality(self) -> bool:
        """Check if stock has high quality score"""
        return self.quality_score is not None and self.quality_score >= 70

    @property
    def is_high_growth(self) -> bool:
        """Check if stock has high growth score"""
        return self.growth_score is not None and self.growth_score >= 70

    @property
    def is_momentum_strong(self) -> bool:
        """Check if stock has strong momentum"""
        return (
            self.momentum_score is not None
            and self.momentum_score >= 70
            and self.rsi_14d is not None
            and self.rsi_14d < 70  # Not overbought
        )
