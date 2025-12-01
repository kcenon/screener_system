from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
from app.services.ml_service import ModelService


class TestModelService:
    @pytest.fixture
    def model_service(self):
        """Mock MLflow and return model service"""
        service = ModelService()
        # Mock model
        service.model = MagicMock()
        service.model.predict.return_value = np.array([[0.8]])  # High confidence UP
        service.model_version = "1"
        service.features = ["f1", "f2"]
        return service

    @pytest.mark.asyncio
    async def test_predict_single_stock(self, model_service):
        """Test single stock prediction"""
        # Mock cache miss
        with patch(
            "app.services.ml_service.cache_manager.get", return_value=None
        ), patch("app.services.ml_service.cache_manager.set") as mock_set:

            result = await model_service.predict("005930")

            assert result["stock_code"] == "005930"
            assert result["prediction"] == "up"
            assert result["confidence"] == 0.8
            assert result["model_version"] == "1"

            mock_set.assert_called_once()

    @pytest.mark.asyncio
    async def test_predict_mock(self):
        service = ModelService()
        # Mock model loading failure to force mock prediction
        service.load_production_model = lambda: None

        result = await service.predict("005930")

        assert result["stock_code"] == "005930"
        assert result["prediction"] == "neutral"  # Default mock
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_predict_with_caching(self, model_service):
        """Test prediction caching"""
        cached_result = {"stock_code": "005930", "prediction": "up"}

        # Mock cache hit
        with patch(
            "app.services.ml_service.cache_manager.get", return_value=cached_result
        ):
            result = await model_service.predict("005930")
            assert result == cached_result

    @pytest.mark.asyncio
    async def test_batch_prediction(self, model_service):
        """Test batch prediction"""
        stock_codes = ["005930", "000660"]

        # Mock individual predictions
        model_service.predict = AsyncMock(
            side_effect=[
                {"stock_code": "005930", "prediction": "up", "confidence": 0.8},
                {"stock_code": "000660", "prediction": "down", "confidence": 0.7},
            ]
        )

        results = await model_service.predict_batch(stock_codes)

        assert len(results) == 2
        assert model_service.predict.call_count == 2
        assert results[0]["stock_code"] == "005930"
        assert results[1]["stock_code"] == "000660"

    def test_get_model_info(self, model_service):
        info = model_service.get_model_info()
        assert info["version"] == "1"
        assert info["stage"] == "Production"
