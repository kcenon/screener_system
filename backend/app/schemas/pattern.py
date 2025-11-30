from typing import List, Dict, Any
from datetime import datetime

from pydantic import BaseModel


class PatternBase(BaseModel):
    stock_code: str
    pattern_type: str
    confidence: float
    detected_at: datetime
    timeframe: str = "1D"


class PatternRecognitionRequest(BaseModel):
    """Request schema for pattern recognition"""
    stock_code: str
    days: int = 60


class PatternRecognitionResponse(BaseModel):
    """Response schema for pattern recognition"""
    stock_code: str
    patterns: List[Dict[str, Any]]
    summary: str
    timestamp: datetime


class PatternDetail(BaseModel):
    """Detailed schema for a recognized pattern"""
    name: str
    confidence: float
    description: str
    action: str  # "buy", "sell", "hold"


class PatternCreate(PatternBase):
    metadata: Dict[str, Any] = {}


class PatternUpdate(PatternBase):
    pass


class PatternResponse(PatternBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AlertConfigBase(BaseModel):
    stock_code: str
    pattern_types: List[str]
    min_confidence: float = 0.7
    notification_methods: List[str] = ["email"]


class AlertConfigCreate(AlertConfigBase):
    user_id: str


class AlertConfigResponse(AlertConfigBase):
    alert_id: str
    created_at: datetime
    status: str = "active"

    class Config:
        from_attributes = True
