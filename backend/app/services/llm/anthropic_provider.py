import logging
from typing import AsyncIterator, List

import anthropic
from app.services.llm.base import LLMMessage, LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider implementation"""

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> LLMResponse:
        """Generate completion using Anthropic API"""
        try:
            system_prompt = None
            filtered_messages = []

            for msg in messages:
                if msg.role == "system":
                    system_prompt = msg.content
                else:
                    filtered_messages.append({"role": msg.role, "content": msg.content})

            response = await self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=filtered_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            return LLMResponse(
                content=response.content[0].text,  # type: ignore
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": (
                        response.usage.input_tokens + response.usage.output_tokens
                    ),
                },
                finish_reason=response.stop_reason,
                provider="anthropic",
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Generate completion with streaming"""
        system_message = next((m.content for m in messages if m.role == "system"), None)
        conversation = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role != "system"
        ]

        stream_kwargs = {
            "model": self.model,
            "messages": conversation,  # type: ignore
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        if system_message:
            stream_kwargs["system"] = system_message

        async with self.client.messages.stream(**stream_kwargs) as stream:
            async for text in stream.text_stream:
                yield text

    async def health_check(self) -> bool:
        """Check if Anthropic API is healthy"""
        try:
            # Simple test message
            await self.generate(
                messages=[LLMMessage(role="user", content="Hello")], max_tokens=10
            )
            return True
        except Exception:
            return False
