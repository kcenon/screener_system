from typing import List

from sqlalchemy.orm import Session

from app.db.models.user_behavior import UserBehaviorEvent
from app.schemas.recommendation import RecommendationResponse, UserBehaviorEventCreate


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    async def track_event(self, user_id: int, event: UserBehaviorEventCreate):
        """Track a user behavior event"""
        db_event = UserBehaviorEvent(
            user_id=user_id,
            event_type=event.event_type,
            stock_code=event.stock_code,
            metadata_=event.metadata,
        )
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    async def get_recommendations(
        self, user_id: int, top_k: int = 10
    ) -> List[RecommendationResponse]:
        """
        Generate personalized recommendations.
        Currently returns mock data until the engine is fully implemented.
        """
        # Mock implementation
        return [
            RecommendationResponse(
                stock_code="AAPL",
                company_name="Apple Inc.",
                sector="Technology",
                current_price=150.0,
                recommendation_score=0.95,
                confidence=0.9,
                reasons=["Similar users liked this", "AI predicts bullish"],
                ai_prediction={"direction": "bullish", "probability": 0.85},
                key_metrics={"per": 25.5, "pbr": 10.2, "dividend_yield": 0.5},
            )
        ]
