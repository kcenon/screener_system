
from typing import Any, Dict, Optional

from pydantic import BaseModel


class UserBehaviorEventCreate(BaseModel):
    event_type: str
    stock_code: Optional[str] = None
    metadata: Dict[str, Any] = {}


class RecommendationBase(BaseModel):
    """Base schema for stock recommendation"""
    stock_code: str
    action: str  # "buy", "sell", "hold"
    confidence: float
    reason: str


class RecommendationCreate(RecommendationBase):
    """Schema for creating a recommendation"""
    pass


class RecommendationResponse(RecommendationBase):
    """Schema for recommendation response"""
    id: int
    created_at: str  # ISO format string

    class Config:
        from_attributes = True
    ai_prediction: Dict[str, Any]
    key_metrics: Dict[str, Any]
    explanation: Optional[Dict[str, Any]] = None


class RecommendationFeedback(BaseModel):
    stock_code: str
    feedback_type: str  # "positive", "negative", "not_interested"
    reason: Optional[str] = None
