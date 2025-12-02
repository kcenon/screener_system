"""Market Index database model"""

from app.db.base import Base, TimestampMixin
from sqlalchemy import BigInteger, CheckConstraint, Column, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import TIMESTAMP


class MarketIndex(Base, TimestampMixin):
    """Market indices data model for KOSPI, KOSDAQ, KRX100"""

    __tablename__ = "market_indices"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Index Identification
    code = Column(String(20), nullable=False, index=True)
    timestamp = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        index=True,
    )

    # OHLC Data
    open_value = Column(Numeric(10, 2), nullable=True)
    high_value = Column(Numeric(10, 2), nullable=True)
    low_value = Column(Numeric(10, 2), nullable=True)
    close_value = Column(Numeric(10, 2), nullable=False)

    # Volume & Value
    volume = Column(BigInteger, nullable=True)
    trading_value = Column(BigInteger, nullable=True)

    # Change Metrics
    change_value = Column(Numeric(10, 2), nullable=True)
    change_percent = Column(Numeric(10, 4), nullable=True)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "code IN ('KOSPI', 'KOSDAQ', 'KRX100')",
            name="valid_index_code",
        ),
        CheckConstraint(
            "open_value IS NULL OR open_value > 0",
            name="valid_open_value",
        ),
        CheckConstraint(
            "close_value > 0",
            name="valid_close_value",
        ),
        CheckConstraint(
            "high_value IS NULL OR low_value IS NULL OR high_value >= low_value",
            name="valid_high_low",
        ),
        CheckConstraint(
            "volume IS NULL OR volume >= 0",
            name="valid_volume",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<MarketIndex(code={self.code}, name={self.name}, "
            f"price={self.current_price})>"
        )

    @property
    def is_kospi(self) -> bool:
        """Check if index is KOSPI"""
        return self.code == "KOSPI"

    @property
    def is_kosdaq(self) -> bool:
        """Check if index is KOSDAQ"""
        return self.code == "KOSDAQ"

    @property
    def is_krx100(self) -> bool:
        """Check if index is KRX100"""
        return self.code == "KRX100"

    @property
    def is_positive(self) -> bool:
        """Check if index change is positive"""
        return self.change_percent and self.change_percent > 0

    @property
    def is_negative(self) -> bool:
        """Check if index change is negative"""
        return self.change_percent and self.change_percent < 0

    def calculate_change(self, previous_close: float) -> tuple[float, float]:
        """
        Calculate change value and percent from previous close

        Args:
            previous_close: Previous day's close value

        Returns:
            Tuple of (change_value, change_percent)
        """
        if not previous_close or previous_close == 0:
            return (0.0, 0.0)

        change_val = float(self.close_value) - previous_close
        change_pct = (change_val / previous_close) * 100

        return (round(change_val, 2), round(change_pct, 4))

    def to_dict(self) -> dict:
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "code": self.code,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "open": float(self.open_value) if self.open_value else None,
            "high": float(self.high_value) if self.high_value else None,
            "low": float(self.low_value) if self.low_value else None,
            "close": float(self.close_value),
            "volume": self.volume,
            "trading_value": self.trading_value,
            "change": float(self.change_value) if self.change_value else None,
            "change_percent": (
                float(self.change_percent) if self.change_percent else None
            ),
        }
