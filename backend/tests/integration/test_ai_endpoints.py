from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_current_user
from app.main import app

# Mock User
mock_user = MagicMock()
mock_user.id = 1
mock_user.email = "test@example.com"
mock_user.is_active = True  # Ensure user is active


# Override get_current_user


async def override_get_current_user():
    return mock_user


@pytest.fixture
async def client_no_db():
    """Create test client without DB dependency"""
    # Set dependency override inside fixture to avoid being cleared by other tests
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Mock Redis connection in lifespan
    with patch("app.core.cache.cache_manager.connect", new_callable=AsyncMock), patch(
        "app.core.cache.cache_manager.disconnect", new_callable=AsyncMock
    ), patch(
        "app.core.websocket.connection_manager.initialize_redis",
        new_callable=AsyncMock,
    ), patch(
        "app.core.redis_pubsub.redis_pubsub.disconnect",
        new_callable=AsyncMock,
    ):

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    # Clean up override after test
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_predict_endpoint(client_no_db):
    """Test /ai/predict/{stock_code} endpoint"""
    # Mock model service prediction
    mock_prediction = {
        "stock_code": "005930",
        "prediction": "up",
        "confidence": 0.8,
        "model_version": "1",
        "predicted_at": "2025-11-30T10:00:00",
        "features_used": ["f1"],
        "horizon": "1d",
    }

    with patch(
        "app.services.ml_service.model_service.predict", return_value=mock_prediction
    ):
        response = await client_no_db.get("/v1/ai/predict/005930")

        assert response.status_code == 200
        data = response.json()
        assert data["stock_code"] == "005930"
        assert data["prediction"] == "up"


@pytest.mark.asyncio
async def test_batch_prediction(client_no_db):
    """Test batch prediction endpoint"""
    mock_predictions = [
        {
            "stock_code": "005930",
            "prediction": "up",
            "confidence": 0.8,
            "model_version": "1",
            "predicted_at": "2025-11-30T10:00:00",
            "features_used": ["f1"],
            "horizon": "1d",
        },
        {
            "stock_code": "000660",
            "prediction": "down",
            "confidence": 0.7,
            "model_version": "1",
            "predicted_at": "2025-11-30T10:00:00",
            "features_used": ["f1"],
            "horizon": "1d",
        },
    ]
    payload = {"stock_codes": ["005930", "000660"], "horizon": "1d"}
    with patch(
        "app.services.ml_service.model_service.predict_batch",
        return_value=mock_predictions,
    ):
        response = await client_no_db.post("/v1/ai/predict/batch", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


@pytest.mark.asyncio
async def test_model_info(client_no_db):
    """Test model info endpoint"""
    mock_info = {
        "model_name": "stock_prediction_lstm",
        "version": "1",
        "stage": "Production",
        "features": ["f1"],
        "mlflow_uri": "http://localhost:5000",
    }
    with patch(
        "app.services.ml_service.model_service.get_model_info", return_value=mock_info
    ):
        response = await client_no_db.get("/v1/ai/model/info")

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1"
