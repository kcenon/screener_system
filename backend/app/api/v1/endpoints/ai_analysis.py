from typing import Any, Dict

from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.services.llm.manager import LLMManager
from app.services.stock_analysis_service import (StockAnalysisError,
                                                 StockAnalysisService)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# Dependency for StockAnalysisService
def get_stock_analysis_service(
    db: AsyncSession = Depends(get_db),
) -> StockAnalysisService:
    llm_manager = LLMManager(
        config={
            "openai": {
                "api_key": settings.OPENAI_API_KEY,
                "model": settings.LLM_MODEL_OPENAI,
            },
            "anthropic": {
                "api_key": settings.ANTHROPIC_API_KEY,
                "model": settings.LLM_MODEL_ANTHROPIC,
            },
        }
    )
    return StockAnalysisService(db, llm_manager)


@router.get("/analysis/{stock_code}", response_model=Dict[str, Any], status_code=200)
async def get_stock_analysis(
    stock_code: str,
    use_cache: bool = True,
    current_user=Depends(get_current_user),
    service: StockAnalysisService = Depends(get_stock_analysis_service),
) -> Dict[str, Any]:
    """
    Generate AI-powered stock analysis report
    """
    try:
        analysis = await service.generate_report(
            stock_code=stock_code, use_cache=use_cache
        )
        return analysis

    except StockAnalysisError as e:
        raise HTTPException(status_code=500, detail=str(e))
