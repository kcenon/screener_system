from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import BaseModel

class UserBehaviorEvent(BaseModel):
    __tablename__ = "user_behavior_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)  # e.g., 'view_stock', 'click_recommendation'
    stock_code = Column(String, nullable=True, index=True)
    metadata_ = Column("metadata", JSON, default={})  # 'metadata' is reserved in some contexts, using metadata_ mapped to metadata column if possible, or just metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="behavior_events")
