from sqlalchemy import Column, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class MLFeature(Base, TimestampMixin):
    """Model for ML features"""

    stock_code = Column(
        String(6),
        ForeignKey("stocks.code", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    calculation_date = Column(Date, primary_key=True, nullable=False)
    feature_data = Column(JSONB, nullable=False)

    # Relationships
    stock = relationship("Stock", backref="ml_features")
