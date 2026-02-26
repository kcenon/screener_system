from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.schemas.recommendation import (RecommendationFeedback,
                                        RecommendationResponse)
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def get_recommendation_service(db: Session = Depends(get_db)):
    return RecommendationService(db)


@router.get("/daily", response_model=List[RecommendationResponse])
async def get_daily_recommendations(
    top_k: int = Query(10, ge=1, le=50),
    current_user=Depends(get_current_user),
    service: RecommendationService = Depends(get_recommendation_service),
):
    """
    Get personalized daily stock recommendations
    """
    return await service.get_recommendations(user_id=current_user.id, top_k=top_k)


@router.post("/feedback")
async def submit_feedback(
    feedback: RecommendationFeedback,
    current_user=Depends(get_current_user),
    service: RecommendationService = Depends(get_recommendation_service),
):
    """
    Submit feedback on a recommendation
    """
    # TODO: Implement feedback handling in service
    return {"status": "success", "message": "Feedback received"}
