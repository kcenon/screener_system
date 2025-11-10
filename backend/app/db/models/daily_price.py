"""Daily price database model"""


from sqlalchemy import (BigInteger, CheckConstraint, Column, Date, ForeignKey,
                        Integer, String)
from sqlalchemy.orm import relationship

from app.db.base import Base


class DailyPrice(Base):
    """Daily OHLCV data model"""

    __tablename__ = "daily_prices"

    # Composite Primary Key
    stock_code = Column(
        String(6),
        ForeignKey("stocks.code", ondelete="CASCADE"),
        primary_key=True,
    )
    trade_date = Column(Date, primary_key=True)

    # Price Data (OHLC)
    open_price = Column(Integer, nullable=True)
    high_price = Column(Integer, nullable=True)
    low_price = Column(Integer, nullable=True)
    close_price = Column(Integer, nullable=False)
    adjusted_close = Column(Integer, nullable=True)

    # Volume Data
    volume = Column(BigInteger, nullable=True)
    trading_value = Column(BigInteger, nullable=True)
    market_cap = Column(BigInteger, nullable=True)

    # Relationships
    stock = relationship("Stock", back_populates="daily_prices")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            """
            open_price > 0 AND
            high_price >= open_price AND
            low_price <= open_price AND
            close_price > 0 AND
            high_price >= low_price
            """,
            name="valid_prices",
        ),
        CheckConstraint(
            "volume >= 0",
            name="valid_volume",
        ),
        CheckConstraint(
            "market_cap IS NULL OR market_cap > 0",
            name="valid_market_cap",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<DailyPrice(stock_code={self.stock_code}, "
            f"trade_date={self.trade_date}, close={self.close_price})>"
        )

    @property
    def price_change(self) -> int:
        """Calculate price change (close - open)"""
        if self.open_price and self.close_price:
            return self.close_price - self.open_price
        return 0

    @property
    def price_change_pct(self) -> float:
        """Calculate price change percentage"""
        if self.open_price and self.close_price and self.open_price > 0:
            return ((self.close_price - self.open_price) / self.open_price) * 100
        return 0.0

    @property
    def daily_range(self) -> int:
        """Calculate daily price range (high - low)"""
        if self.high_price and self.low_price:
            return self.high_price - self.low_price
        return 0
