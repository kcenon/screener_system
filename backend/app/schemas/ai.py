from typing import Any, Dict, List

from pydantic import BaseModel, Field


class AIAnalysisRequest(BaseModel):
    """Request schema for AI analysis"""

    stock_code: str
    analysis_type: str = (
        "comprehensive"  # comprehensive, technical, fundamental, sentiment
    )


class AIAnalysisResponse(BaseModel):
    """Response schema for AI analysis"""

    stock_code: str
    analysis_type: str
    summary: str
    details: Dict[str, Any]
    confidence_score: float
    timestamp: str


class SentimentAnalysisRequest(BaseModel):
    """Request schema for sentiment analysis"""

    text: str
    source: str = "news"  # news, social_media, report


class PredictionResponse(BaseModel):
    stock_code: str = Field(..., description="Stock code")
    prediction: str = Field(..., description="Prediction: up, down, or neutral")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    model_version: str = Field(..., description="Model version used")
    predicted_at: str = Field(
        ..., description="Prediction timestamp"
    )  # Changed from datetime to str
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
                "horizon": "1d",
            }
        }


class PortfolioAnalysisRequest(BaseModel):
    stock_codes: List[str]
    start_date: Any  # Should be date, but using Any to avoid import issues for now
    end_date: Any


class PortfolioAnalysisResponse(BaseModel):
    portfolio_score: float
    risk_analysis: Dict[str, Any]
    sector_allocation: Dict[str, float]
    recommendations: List[str]


class BatchPredictionRequest(BaseModel):
    stock_codes: List[str] = Field(..., min_items=1, max_items=100)
    horizon: str = Field("1d", pattern="^(1d|5d|20d)$")


class ModelInfoResponse(BaseModel):
    model_name: str
    version: str
    stage: str
    features: List[str]
    mlflow_uri: str
