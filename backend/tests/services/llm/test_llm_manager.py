from unittest.mock import AsyncMock

import pytest
from app.services.llm.base import LLMProvider
from app.services.llm.manager import (LLMManager, LLMMessage, LLMProviderError,
                                      LLMResponse)


@pytest.fixture
def mock_openai_provider():
    provider = AsyncMock(spec=LLMProvider)
    provider.health_check.return_value = True
    provider.generate.return_value = LLMResponse(
        content="OpenAI response",
        model="gpt-4",
        usage={"total_tokens": 10},
        provider="openai",
    )
    return provider


@pytest.fixture
def mock_anthropic_provider():
    provider = AsyncMock(spec=LLMProvider)
    provider.health_check.return_value = True
    provider.generate.return_value = LLMResponse(
        content="Anthropic response",
        model="claude-3",
        usage={"total_tokens": 10},
        provider="anthropic",
    )
    return provider


@pytest.fixture
def manager(mock_openai_provider, mock_anthropic_provider):
    manager = LLMManager(
        config={
            "openai": {"api_key": "test", "model": "gpt-4"},
            "anthropic": {"api_key": "test", "model": "claude-3"},
        }
    )
    # Inject mocks
    manager.providers["openai"] = mock_openai_provider
    manager.providers["anthropic"] = mock_anthropic_provider
    return manager


@pytest.mark.asyncio
async def test_generate_success_primary(manager, mock_openai_provider):
    messages = [LLMMessage(role="user", content="Hello")]
    response = await manager.generate(messages)

    assert response.content == "OpenAI response"
    assert response.provider == "openai"
    mock_openai_provider.generate.assert_called_once()


@pytest.mark.asyncio
async def test_health_check_failover(
    manager, mock_openai_provider, mock_anthropic_provider
):
    # Make OpenAI unhealthy
    mock_openai_provider.health_check.return_value = False

    messages = [LLMMessage(role="user", content="Hello")]
    response = await manager.generate(messages)

    assert response.content == "Anthropic response"
    mock_openai_provider.generate.assert_not_called()
    mock_anthropic_provider.generate.assert_called_once()


@pytest.mark.asyncio
async def test_generate_failover(
    manager, mock_openai_provider, mock_anthropic_provider
):
    # Make OpenAI fail
    mock_openai_provider.generate.side_effect = Exception("OpenAI Error")

    messages = [LLMMessage(role="user", content="Hello")]
    response = await manager.generate(messages)

    assert response.content == "Anthropic response"
    assert response.provider == "anthropic"
    # Mock both providers failing
    mock_openai = AsyncMock(spec=LLMProvider)
    mock_openai.health_check.return_value = True
    mock_openai.generate.side_effect = Exception("OpenAI Error")
    manager.providers["openai"] = mock_openai

    mock_anthropic = AsyncMock(spec=LLMProvider)
    mock_anthropic.health_check.return_value = True
    mock_anthropic.generate.side_effect = Exception("Anthropic Error")
    manager.providers["anthropic"] = mock_anthropic

    messages = [LLMMessage(role="user", content="Hello")]

    with pytest.raises(LLMProviderError):
        await manager.generate(messages)
