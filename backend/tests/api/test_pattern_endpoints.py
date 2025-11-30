import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.dependencies import get_current_user

# Mock user


async def mock_get_current_user():
    return {"id": "test_user", "email": "test@example.com"}


@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides = {}


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_patterns_endpoint(client: AsyncClient):
    # Since we don't have real data, it should return empty list
    response = await client.get(
        "/v1/ai/patterns/AAPL"
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_alert_endpoint(client: AsyncClient):
    payload = {
        "user_id": "test_user",
        "stock_code": "AAPL",
        "pattern_types": ["Head and Shoulders"],
        "min_confidence": 0.8,
        "notification_methods": ["email"]
    }
    response = await client.post(
        "/v1/ai/patterns/alerts",
        json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["stock_code"] == "AAPL"
    assert "alert_id" in data
