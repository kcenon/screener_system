from typing import List, Optional, Dict, AsyncIterator
from app.services.llm.base import LLMProvider, LLMMessage, LLMResponse
from app.services.llm.openai_provider import OpenAIProvider
from app.services.llm.anthropic_provider import AnthropicProvider
import logging

logger = logging.getLogger(__name__)

class LLMProviderError(Exception):
    pass

class LLMRateLimitError(LLMProviderError):
    pass

class LLMManager:
    """Manage multiple LLM providers with failover"""

    def __init__(self, config: Dict):
        self.providers: Dict[str, LLMProvider] = {}

        # Initialize providers
        if config.get("openai"):
            self.providers["openai"] = OpenAIProvider(
                api_key=config["openai"]["api_key"],
                model=config["openai"].get("model", "gpt-4-turbo")
            )

        if config.get("anthropic"):
            self.providers["anthropic"] = AnthropicProvider(
                api_key=config["anthropic"]["api_key"],
                model=config["anthropic"].get("model", "claude-3-opus-20240229")
            )

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        provider_preference: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate with automatic failover"""
        providers_to_try = provider_preference or ["openai", "anthropic"]

        last_error = None
        for provider_name in providers_to_try:
            provider = self.providers.get(provider_name)
            if not provider:
                continue

            try:
                # Check provider health
                is_healthy = await provider.health_check()
                if not is_healthy:
                    logger.warning(f"Provider {provider_name} unhealthy, skipping")
                    continue

                # Generate response
                response = await provider.generate(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )

                logger.info(f"Successfully generated with {provider_name}")
                return response

            except Exception as e:
                logger.error(f"Provider {provider_name} error: {e}")
                last_error = e
                continue

        # All providers failed
        raise LLMProviderError(
            f"All providers failed. Last error: {last_error}"
        ) from last_error

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        provider_name: str = "openai",
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming response"""
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not configured")

        async for chunk in provider.generate_stream(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            yield chunk
