from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PredictionResponse(BaseModel):
    stock_code: str = Field(..., description="Stock code")
    prediction: str = Field(..., description="Prediction: up, down, or neutral")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    model_version: str = Field(..., description="Model version used")
    predicted_at: datetime = Field(..., description="Prediction timestamp")
    features_used: List[str] = Field(..., description="Features used for prediction")
    horizon: str = Field(..., description="Prediction horizon")

    class Config:
        json_schema_extra = {
            "example": {
                "stock_code": "005930",
                "prediction": "up",
                "confidence": 0.75,
                "model_version": "3",
                "predicted_at": "2025-11-30T10:00:00Z",
                "features_used": ["price", "volume", "rsi", "macd"],
                "horizon": "1d"
            }
        }

class BatchPredictionRequest(BaseModel):
    stock_codes: List[str] = Field(..., min_items=1, max_items=100)
    horizon: str = Field("1d", pattern="^(1d|5d|20d)$")

class ModelInfoResponse(BaseModel):
    model_name: str
    version: str
    stage: str
    features: List[str]
    mlflow_uri: str
