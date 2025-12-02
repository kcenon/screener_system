from unittest.mock import MagicMock

import pytest
from app.schemas.recommendation import UserBehaviorEventCreate
from app.services.recommendation_service import RecommendationService
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def service(mock_db):
    return RecommendationService(mock_db)


@pytest.mark.asyncio
async def test_track_event(service, mock_db):
    event = UserBehaviorEventCreate(
        event_type="view_stock", stock_code="AAPL", metadata={"source": "dashboard"}
    )

    await service.track_event(user_id=1, event=event)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_get_recommendations(service):
    recs = await service.get_recommendations(user_id=1)

    assert len(recs) > 0
    assert recs[0].stock_code == "AAPL"
    assert recs[0].recommendation_score > 0
