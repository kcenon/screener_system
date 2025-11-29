from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.schemas.ai import PredictionResponse, BatchPredictionRequest, ModelInfoResponse
from app.services.ml_service import model_service
from app.api.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/predict/{stock_code}", response_model=PredictionResponse)
async def predict_stock(
    stock_code: str,
    horizon: str = Query("1d", pattern="^(1d|5d|20d)$"),
    current_user = Depends(get_current_user)  # Require authentication
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

@router.post("/predict/batch", response_model=List[PredictionResponse])
async def predict_batch(
    request: BatchPredictionRequest,
    current_user = Depends(get_current_user)
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
            status_code=400,
            detail="Batch size exceeds limit (max 100 stocks)"
        )

    predictions = await model_service.predict_batch(request.stock_codes, request.horizon)
    return predictions

@router.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info(current_user = Depends(get_current_user)):
    """
    Get current production model information

    Returns:
        Model version, metrics, and metadata
    """
    return model_service.get_model_info()
