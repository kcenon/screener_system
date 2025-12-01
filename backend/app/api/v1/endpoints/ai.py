import logging
from typing import List

from app.api.dependencies import get_ai_service, get_current_user
from app.schemas.ai import (BatchPredictionRequest, ModelInfoResponse,
                            PortfolioAnalysisRequest,
                            PortfolioAnalysisResponse, PredictionResponse)
from app.schemas.pattern import (AlertConfigCreate, AlertConfigResponse,
                                 PatternResponse)
from app.services.ai_service import AIService
from app.services.ml_service import model_service
from app.services.pattern_recognition_service import pattern_service
from fastapi import APIRouter, Depends, HTTPException, Query, status

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/predict/{stock_code}", response_model=PredictionResponse)
async def predict_stock(
    stock_code: str,
    horizon: str = Query("1d", pattern="^(1d|5d|20d)$"),
    current_user=Depends(get_current_user),  # Require authentication
):
    """
    Get AI prediction for next trading day movement

    Args:
        stock_code: Stock code (e.g., "005930" for Samsung Electronics)
        horizon: Prediction horizon (1d, 5d, 20d)

    Returns:
        Prediction with confidence score and model version
    """
    try:
        prediction = await model_service.predict(stock_code, horizon)
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error for {stock_code}: {e}")
        raise HTTPException(status_code=500, detail="Prediction service error")


@router.post("/explain/portfolio", response_model=PortfolioAnalysisResponse)
async def explain_portfolio(
    request: PortfolioAnalysisRequest,
    current_user=Depends(get_current_user),
    service: AIService = Depends(get_ai_service),
):
    """
    Explain the performance and characteristics of a user's portfolio.
    """
    try:
        analysis = await service.analyze_portfolio(
            request.stock_codes, request.start_date, request.end_date
        )
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Portfolio analysis error: {e}")
        raise HTTPException(status_code=500, detail="Portfolio analysis service error")


@router.post("/predict/batch", response_model=List[PredictionResponse])
async def predict_batch(
    request: BatchPredictionRequest, current_user=Depends(get_current_user)
):
    """
    Get AI predictions for multiple stocks (max 100)

    Args:
        request: {
            "stock_codes": ["005930", "000660", ...],
            "horizon": "1d"
        }

    Returns:
        List of predictions
    """
    if len(request.stock_codes) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch size exceeds limit (max 100 stocks)",
        )

    predictions = await model_service.predict_batch(
        request.stock_codes, request.horizon
    )
    return predictions


@router.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info(current_user=Depends(get_current_user)):
    """
    Get current production model information

    Returns:
        Model version, metrics, and metadata
    """
    return model_service.get_model_info()


@router.get("/patterns/{stock_code}", response_model=List[PatternResponse])
async def get_patterns(
    stock_code: str,
    timeframe: str = Query("1D", regex="^(1D|1W|1M)$"),
    min_confidence: float = Query(0.7, ge=0.0, le=1.0),
    current_user=Depends(get_current_user),
):
    """
    Retrieve detected chart patterns for a stock
    """
    return await pattern_service.get_patterns(stock_code, timeframe, min_confidence)


@router.post("/patterns/alerts", response_model=AlertConfigResponse)
async def create_pattern_alert(
    config: AlertConfigCreate, current_user=Depends(get_current_user)
):
    """
    Configure pattern detection alert
    """
    return await pattern_service.create_alert(config)
