import logging
from datetime import datetime, timedelta
from typing import Dict, List

import mlflow
import numpy as np

from app.core.cache import cache_manager
from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelService:
    """ML model serving service with caching and versioning"""

    def __init__(self):
        self.model = None
        self.model_version = None
        self.features = None
        self.preprocessing_pipeline = None

    def load_production_model(self):
        """Load production model from MLflow"""
        try:
            # In a real scenario, we would connect to a remote MLflow server.
            # For this implementation, we assume local or configured URI.
            if (
                hasattr(settings, "MLFLOW_TRACKING_URI")
                and settings.MLFLOW_TRACKING_URI
            ):
                mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)

            # Get production model
            client = mlflow.tracking.MlflowClient()
            # Note: This assumes a registered model named "stock_prediction_lstm"
            # exists. If not, we should handle it gracefully or mock it for now.
            try:
                versions = client.get_latest_versions(
                    "stock_prediction_lstm", stages=["Production"]
                )
            except Exception:
                logger.warning(
                    "No registered model 'stock_prediction_lstm' found. "
                    "Skipping model load."
                )
                return

            if not versions:
                logger.warning(
                    "No production model found for 'stock_prediction_lstm'."
                )
                return

            version = versions[0]
            self.model_version = version.version

            # Load model
            model_uri = "models:/stock_prediction_lstm/Production"
            # We use pyfunc for generic model loading, or specific flavor if known
            # (e.g. keras, sklearn)
            # Using pyfunc is safer for generic usage.
            self.model = mlflow.pyfunc.load_model(model_uri)

            # Load feature list from artifacts
            # run = client.get_run(version.run_id)
            # artifacts_uri = run.info.artifact_uri
            # Here we would load features.json. For now, we'll use a placeholder.
            # self.features = ...
            self.features = ["close", "volume", "rsi", "macd"]  # Default placeholder

            logger.info(f"Loaded production model version {self.model_version}")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # We might want to raise here if model is critical, or just log.
            # raise

    async def predict(self, stock_code: str, horizon: str = "1d") -> Dict:
        """
        Generate prediction for a stock

        Args:
            stock_code: Stock code (e.g., "005930")
            horizon: Prediction horizon ("1d", "5d", "20d")

        Returns:
            Dict containing prediction details
        """
        # Check cache first
        cache_key = f"prediction:{stock_code}:{self.model_version}:{horizon}"
        cached = await cache_manager.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {stock_code}")
            return cached

        # If model is not loaded, we can't predict
        if self.model is None:
            # Try loading again?
            self.load_production_model()
            if self.model is None:
                # Mock response for development if no model available
                logger.warning("Model not loaded, returning mock prediction")
                return self._mock_prediction(stock_code, horizon)

        # Get latest features for stock
        # In a real app, we'd call FeatureService.
        # from app.services.feature_service import get_stock_features
        # features = await get_stock_features(stock_code, sequence_length=60)
        # Mock implementation for now
        # In reality, this would load a model from disk or S3
        features = np.random.rand(1, 60, 4)  # Batch size 1, seq len 60, 4 features

        # Generate prediction
        try:
            prediction_result = self.model.predict(features)
            # Handle different return types (numpy array, dataframe, list)
            if isinstance(prediction_result, np.ndarray):
                if prediction_result.size == 1:
                    prediction_proba = float(prediction_result[0])
                else:
                    prediction_proba = float(prediction_result[0][0])
            else:
                prediction_proba = 0.5  # Fallback
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return self._mock_prediction(stock_code, horizon)

        # Convert to class
        if prediction_proba > 0.6:
            prediction = "up"
            confidence = prediction_proba
        elif prediction_proba < 0.4:
            prediction = "down"
            confidence = 1 - prediction_proba
        else:
            prediction = "neutral"
            confidence = 0.5

        result = {
            "stock_code": stock_code,
            "prediction": prediction,
            "confidence": float(confidence),
            "model_version": str(self.model_version),
            "predicted_at": datetime.utcnow().isoformat(),
            "features_used": self.features,
            "horizon": horizon
        }

        # Cache result (TTL until next trading day)
        ttl = self._calculate_ttl_to_next_trading_day()
        await cache_manager.set(cache_key, result, ttl=ttl)

        logger.info(
            f"Generated prediction for {stock_code}: {prediction} ({confidence:.2f})"
        )

        return result

    def _mock_prediction(self, stock_code: str, horizon: str) -> Dict:
        """Return a mock prediction for development/fallback"""
        return {
            "stock_code": stock_code,
            "prediction": "neutral",
            "confidence": 0.5,
            "model_version": "mock",
            "predicted_at": datetime.utcnow().isoformat(),
            "features_used": ["mock_feature"],
            "horizon": horizon
        }

    async def predict_batch(
        self, stock_codes: List[str], horizon: str = "1d"
    ) -> List[Dict]:
        """Generate predictions for multiple stocks"""
        results = []
        for code in stock_codes[:100]:  # Limit to 100
            try:
                result = await self.predict(code, horizon)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to predict {code}: {e}")
                results.append({
                    "stock_code": code,
                    "error": str(e)
                })
        return results

    def get_model_info(self) -> Dict:
        """Get current production model information"""
        return {
            "model_name": "stock_prediction_lstm",
            "version": str(self.model_version) if self.model_version else "None",
            "stage": "Production",
            "features": self.features or [],
            "mlflow_uri": getattr(settings, "MLFLOW_TRACKING_URI", "Not Configured")
        }

    def _calculate_ttl_to_next_trading_day(self) -> int:
        """Calculate TTL in seconds until next trading day"""
        from datetime import time

        now = datetime.now()
        # If before 9 AM, expire at 9 AM today
        # If after 3:30 PM, expire at 9 AM tomorrow
        # Korean market hours: 9:00 AM - 3:30 PM

        if now.time() < time(9, 0):
            next_refresh = now.replace(hour=9, minute=0, second=0)
        else:
            next_refresh = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0)

        ttl = int((next_refresh - now).total_seconds())
        return ttl


# Global instance
ml_service = ModelService()

model_service = ml_service
