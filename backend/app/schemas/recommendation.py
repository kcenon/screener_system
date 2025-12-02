from typing import Any, Dict, List, Optional

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


class RecommendationResponse(BaseModel):
    """Schema for recommendation response"""

    stock_code: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    current_price: Optional[float] = None
    recommendation_score: float
    confidence: float
    reasons: List[str] = []

    ai_prediction: Dict[str, Any]
    key_metrics: Dict[str, Any]
    explanation: Optional[Dict[str, Any]] = None

    id: Optional[int] = None
    created_at: Optional[str] = None
    action: Optional[str] = None
    reason: Optional[str] = None

    class Config:
        from_attributes = True


class RecommendationFeedback(BaseModel):
    stock_code: str
    feedback_type: str  # "positive", "negative", "not_interested"
    reason: Optional[str] = None
