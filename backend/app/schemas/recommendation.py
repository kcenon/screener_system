from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel

class UserBehaviorEventCreate(BaseModel):
    event_type: str
    stock_code: Optional[str] = None
    metadata: Dict[str, Any] = {}

class RecommendationResponse(BaseModel):
    stock_code: str
    company_name: str
    sector: str
    current_price: float
    recommendation_score: float
    confidence: float
    reasons: List[str]
    ai_prediction: Dict[str, Any]
    key_metrics: Dict[str, Any]
    explanation: Optional[Dict[str, Any]] = None

class RecommendationFeedback(BaseModel):
    stock_code: str
    feedback_type: str  # "positive", "negative", "not_interested"
    reason: Optional[str] = None
