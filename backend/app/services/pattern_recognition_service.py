import uuid
from datetime import datetime
from typing import Dict, List

from app.schemas.pattern import (AlertConfigCreate, AlertConfigResponse,
                                 PatternResponse)


class PatternRecognitionService:
    """Service for managing chart pattern recognition and alerts"""

    def __init__(self):
        # In a real app, inject dependencies like Redis, DB, etc.
        self._patterns_cache: Dict[str, List[Dict]] = {}  # Mock cache
        self._alerts: Dict[str, Dict] = {}  # Mock DB

    async def get_patterns(
        self, stock_code: str, timeframe: str = "1D", min_confidence: float = 0.7
    ) -> List[PatternResponse]:
        """
        Retrieve detected patterns for a stock.
        In a real implementation, this would check Redis, then run detection if missing.
        """
        cache_key = f"{stock_code}:{timeframe}"
        patterns_data = self._patterns_cache.get(cache_key, [])

        # Filter by confidence
        filtered = [
            PatternResponse(**p)
            for p in patterns_data
            if p["confidence"] >= min_confidence
        ]
        return filtered

    async def recognize_patterns(
        self, stock_code: str, days: int = 60
    ) -> List[PatternResponse]:
        """
        Recognize chart patterns for a stock

        Args:
            stock_code: Stock code
            days: Number of days to analyze

        Returns:
            List of recognized patterns
        """
        # Get price history
        prices = await self.stock_repo.get_price_history(stock_code, limit=days)
        if len(prices) < 20:
            return []

        patterns = []

        # Convert to format needed for analysis
        # Note: In real implementation, we would use numpy here
        # opens = np.array([float(p.open) for p in prices])
        # highs = np.array([float(p.high) for p in prices])
        # lows = np.array([float(p.low) for p in prices])
        # closes = np.array([float(p.close) for p in prices])
        # volumes = np.array([float(p.volume) for p in prices])

        return patterns

    async def create_alert(self, config: AlertConfigCreate) -> AlertConfigResponse:
        """Create a new pattern alert configuration"""
        alert_id = str(uuid.uuid4())
        alert = {
            "alert_id": alert_id,
            "created_at": datetime.utcnow(),
            "status": "active",
            **config.model_dump(),
        }
        self._alerts[alert_id] = alert
        return AlertConfigResponse(**alert)

    async def get_alerts(self, user_id: str) -> List[AlertConfigResponse]:
        """Get alerts for a user"""
        return [
            AlertConfigResponse(**a)
            for a in self._alerts.values()
            if a["user_id"] == user_id
        ]


# Global instance
pattern_service = PatternRecognitionService()
