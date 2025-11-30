import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.llm.manager import LLMManager, LLMMessage, LLMResponse, LLMProviderError
from app.services.llm.base import LLMProvider

class MockProvider(LLMProvider):
    async def generate(self, messages, **kwargs):
        return LLMResponse(
            content="Mock response",
            model="mock-model",
            usage={"total_tokens": 10},
            provider="mock"
        )
    
    async def generate_stream(self, messages, **kwargs):
        yield "Mock"
        yield " stream"

    async def health_check(self):
        return True

@pytest.fixture
def mock_config():
    return {
        "openai": {"api_key": "sk-test", "model": "gpt-4"},
        "anthropic": {"api_key": "sk-ant-test", "model": "claude-3"}
    }

@pytest.mark.asyncio
async def test_llm_manager_initialization(mock_config):
    manager = LLMManager(mock_config)
    assert "openai" in manager.providers
    assert "anthropic" in manager.providers

@pytest.mark.asyncio
async def test_llm_manager_generate_success(mock_config):
    manager = LLMManager(mock_config)
    
    # Mock OpenAI provider
    mock_openai = AsyncMock(spec=MockProvider)
    mock_openai.health_check.return_value = True
    mock_openai.generate.return_value = LLMResponse(
        content="OpenAI response",
        model="gpt-4",
        usage={"total_tokens": 10},
        provider="openai"
    )
    manager.providers["openai"] = mock_openai

    messages = [LLMMessage(role="user", content="Hello")]
    response = await manager.generate(messages)

    assert response.content == "OpenAI response"
    assert response.provider == "openai"
    mock_openai.generate.assert_called_once()

@pytest.mark.asyncio
async def test_llm_manager_failover(mock_config):
    manager = LLMManager(mock_config)
    
    # Mock OpenAI provider (failing)
    mock_openai = AsyncMock(spec=MockProvider)
    mock_openai.health_check.return_value = False # Unhealthy
    manager.providers["openai"] = mock_openai

    # Mock Anthropic provider (success)
    mock_anthropic = AsyncMock(spec=MockProvider)
    mock_anthropic.health_check.return_value = True
    mock_anthropic.generate.return_value = LLMResponse(
        content="Anthropic response",
        model="claude-3",
        usage={"total_tokens": 10},
        provider="anthropic"
    )
    manager.providers["anthropic"] = mock_anthropic

    messages = [LLMMessage(role="user", content="Hello")]
    response = await manager.generate(messages, provider_preference=["openai", "anthropic"])

    assert response.content == "Anthropic response"
    assert response.provider == "anthropic"
    mock_openai.generate.assert_not_called() # Should skip generate if unhealthy
    mock_anthropic.generate.assert_called_once()

@pytest.mark.asyncio
async def test_llm_manager_all_fail(mock_config):
    manager = LLMManager(mock_config)
    
    # Mock both providers failing
    mock_openai = AsyncMock(spec=MockProvider)
    mock_openai.health_check.return_value = True
    mock_openai.generate.side_effect = Exception("OpenAI error")
    manager.providers["openai"] = mock_openai

    mock_anthropic = AsyncMock(spec=MockProvider)
    mock_anthropic.health_check.return_value = True
    mock_anthropic.generate.side_effect = Exception("Anthropic error")
    manager.providers["anthropic"] = mock_anthropic

    messages = [LLMMessage(role="user", content="Hello")]
    
    with pytest.raises(LLMProviderError):
        await manager.generate(messages)
