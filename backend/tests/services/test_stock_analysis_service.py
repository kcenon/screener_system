from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.llm.manager import LLMManager, LLMResponse
from app.services.stock_analysis_service import StockAnalysisService


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_llm_manager():
    return AsyncMock(spec=LLMManager)


@pytest.mark.asyncio
async def test_generate_report_success(mock_db, mock_llm_manager):
    service = StockAnalysisService(mock_db, mock_llm_manager)

    # Mock LLM response
    mock_llm_response = LLMResponse(
        content='{"overall_rating": "Buy", "confidence": 80}',
        model="gpt-4",
        usage={"total_tokens": 100},
        provider="openai",
    )
    mock_llm_manager.generate.return_value = mock_llm_response

    # Mock StockService (if we were using it for real data fetching)
    # service.stock_service.get_stock_info = AsyncMock(return_value={...})

    report = await service.generate_report("005930")

    assert report["overall_rating"] == "Buy"
    assert report["confidence"] == 80
    assert report["metadata"]["provider"] == "openai"


@pytest.mark.asyncio
async def test_generate_report_fallback_parsing(mock_db, mock_llm_manager):
    service = StockAnalysisService(mock_db, mock_llm_manager)

    # Mock LLM response with invalid JSON
    mock_llm_response = LLMResponse(
        content="This is not JSON but a text report.",
        model="gpt-4",
        usage={"total_tokens": 100},
        provider="openai",
    )
    mock_llm_manager.generate.return_value = mock_llm_response

    report = await service.generate_report("005930")

    assert report["overall_rating"] == "Unknown"
    assert report["full_text"] == "This is not JSON but a text report."
