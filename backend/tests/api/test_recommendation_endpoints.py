import pytest
from app.api.dependencies import get_current_user
from app.main import app
from httpx import ASGITransport, AsyncClient

# Mock user


async def mock_get_current_user():
    class MockUser:
        id = 1
        email = "test@example.com"

    return MockUser()


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
async def test_get_daily_recommendations(client: AsyncClient):
    response = await client.get("/v1/recommendations/daily")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["stock_code"] == "AAPL"


@pytest.mark.asyncio
async def test_submit_feedback(client: AsyncClient):
    payload = {
        "stock_code": "AAPL",
        "feedback_type": "positive",
        "reason": "Good fundamentals",
    }
    response = await client.post("/v1/recommendations/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
