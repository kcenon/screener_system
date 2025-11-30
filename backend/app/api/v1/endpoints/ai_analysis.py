from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.services.stock_analysis_service import StockAnalysisService, StockAnalysisError
from app.services.llm.manager import LLMManager
from app.core.config import settings
from typing import Dict, Any

router = APIRouter()

# Dependency for StockAnalysisService
def get_stock_analysis_service(db: Session = Depends(get_db)) -> StockAnalysisService:
    llm_manager = LLMManager(config={
        "openai": {"api_key": settings.OPENAI_API_KEY, "model": settings.LLM_MODEL_OPENAI},
        "anthropic": {"api_key": settings.ANTHROPIC_API_KEY, "model": settings.LLM_MODEL_ANTHROPIC}
    })
    return StockAnalysisService(db, llm_manager)

@router.get("/analysis/{stock_code}")
async def get_stock_analysis(
    stock_code: str,
    use_cache: bool = True,
    current_user = Depends(get_current_user),
    service: StockAnalysisService = Depends(get_stock_analysis_service)
) -> Dict[str, Any]:
    """
    Generate AI-powered stock analysis report
    """
    try:
        analysis = await service.generate_report(
            stock_code=stock_code,
            use_cache=use_cache
        )
        return analysis

    except StockAnalysisError as e:
        raise HTTPException(status_code=500, detail=str(e))
