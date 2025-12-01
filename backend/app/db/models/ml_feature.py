from app.db.base import BaseModel
from sqlalchemy import JSON, Column, ForeignKey, String
# from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship


class MLFeature(BaseModel):
    """Machine learning feature storage"""

    __tablename__ = "ml_features"

    stock_code = Column(
        String(20), ForeignKey("stocks.code", ondelete="CASCADE"), nullable=False
    )
    feature_date = Column(String(10), nullable=False)  # YYYY-MM-DD

    # Feature data stored as JSON
    feature_data = Column(JSON, nullable=False)

    # Relationships
    stock = relationship("Stock", backref="ml_features")
