from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class PatternBase(BaseModel):
    stock_code: str
    pattern_type: str
    confidence: float
    detected_at: datetime
    timeframe: str = "1D"

class PatternCreate(PatternBase):
    metadata: Dict[str, Any] = {}

class PatternResponse(PatternBase):
    pattern_id: str
    metadata: Dict[str, Any] = {}
    
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
