import pytest
from app.schemas.pattern import AlertConfigCreate
from app.services.pattern_recognition_service import PatternRecognitionService


@pytest.fixture
def service():
    return PatternRecognitionService()


@pytest.mark.asyncio
async def test_get_patterns_empty(service):
    patterns = await service.get_patterns("AAPL")
    assert patterns == []


@pytest.mark.asyncio
async def test_detect_patterns(service):
    # Manually inject data into mock cache
    service._patterns_cache["005930:1D"] = [
        {
            "stock_code": "005930",
            "pattern_type": "double_bottom",
            "confidence": 0.85,
            "detected_at": "2023-01-01T00:00:00",
            "timeframe": "1D",
            "pattern_id": "p1",
            "id": 1,
            "created_at": "2023-01-01T00:00:00",
        }
    ]

    patterns = await service.get_patterns(stock_code="005930")

    assert len(patterns) > 0
    assert patterns[0].pattern_type == "double_bottom"
    assert patterns[0].confidence > 0.8


@pytest.mark.asyncio
async def test_create_and_get_alert(service):
    config = AlertConfigCreate(
        user_id="user123",
        stock_code="AAPL",
        pattern_types=["Head and Shoulders"],
        min_confidence=0.8,
        notification_methods=["email"],
    )

    alert = await service.create_alert(config)
    assert alert.alert_id is not None
    assert alert.stock_code == "AAPL"
    assert alert.status == "active"

    alerts = await service.get_alerts("user123")
    assert len(alerts) == 1
    assert alerts[0].alert_id == alert.alert_id


@pytest.mark.asyncio
async def test_get_patterns_filtering(service):
    # Manually inject data into mock cache
    service._patterns_cache["AAPL:1D"] = [
        {
            "stock_code": "AAPL",
            "pattern_type": "Head and Shoulders",
            "confidence": 0.9,
            "detected_at": "2023-01-01T00:00:00",
            "timeframe": "1D",
            "pattern_id": "p1",
            "id": 1,
            "created_at": "2023-01-01T00:00:00",
        },
        {
            "stock_code": "AAPL",
            "pattern_type": "Triangle",
            "confidence": 0.6,
            "detected_at": "2023-01-01T00:00:00",
            "timeframe": "1D",
            "pattern_id": "p2",
            "id": 2,
            "created_at": "2023-01-01T00:00:00",
        },
    ]

    patterns = await service.get_patterns("AAPL", min_confidence=0.8)
    assert len(patterns) == 1
    assert patterns[0].pattern_type == "Head and Shoulders"
