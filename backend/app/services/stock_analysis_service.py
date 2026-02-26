import json
import logging
from datetime import datetime
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm.manager import LLMManager, LLMMessage
from app.services.llm.prompt_templates import PromptTemplate
from app.services.stock_service import StockService

# Assuming we have a Redis cache manager, if not we'll use a simple dict
# or mock
# from app.core.cache import CacheManager

logger = logging.getLogger(__name__)


class StockAnalysisError(Exception):
    pass


class StockAnalysisService:
    """Generate AI-powered stock analysis reports"""

    def __init__(
        self,
        db: AsyncSession,
        llm_manager: LLMManager,
        # cache_manager: CacheManager
    ):
        self.db = db
        self.llm = llm_manager
        # self.cache = cache_manager

        # Mock cache for StockService since we don't have it yet in this
        # service. In real implementation, we should inject it
        from unittest.mock import MagicMock

        mock_cache = MagicMock()
        self.stock_service = StockService(db, mock_cache)

    async def generate_report(
        self, stock_code: str, use_cache: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive stock analysis report"""
        # TODO: Implement caching
        # if use_cache:
        #     cache_key = f"llm:analysis:{stock_code}:v1"
        #     cached = await self.cache.get(cache_key)
        #     if cached:
        #         return json.loads(cached)

        try:
            # Gather stock data
            # Note: StockService might need async methods or we run sync
            # methods in threadpool. For now assuming we can get data.
            # In real implementation, we'd need to ensure StockService exposes
            # necessary data or we fetch it here.

            # Mocking data gathering for now as StockService might not have
            # all methods ready. In a real scenario, we would call:
            # stock_info = await self.stock_service.get_stock_info(stock_code)
            # etc.

            # Placeholder data
            context = {
                "stock_code": stock_code,
                "company_name": "Samsung Electronics",  # Mock
                "sector": "Technology",
                "current_price": 75000,
                "per": 15.5,
                "pbr": 1.2,
                "roe": 12.5,
                "debt_ratio": 35.0,
                "dividend_yield": 2.5,
                "rsi": 65.5,
                "macd_status": "Bullish Crossover",
                "ma_status": "Above MA20, MA60",
                "return_1m": 5.2,
                "return_3m": 12.1,
                "return_6m": -3.5,
                "ai_prediction": ("AI predicts bullish movement with 85% confidence."),
            }

            # Render prompt
            prompt = PromptTemplate.render("stock_analysis", context)

            # Generate analysis with LLM
            messages = [
                LLMMessage(
                    role="system", content="You are an expert stock market analyst."
                ),
                LLMMessage(role="user", content=prompt),
            ]

            response = await self.llm.generate(
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                provider_preference=["openai", "anthropic"],
            )

            # Parse response
            analysis = self._parse_response(response.content)

            # Add metadata
            analysis["metadata"] = {
                "generated_at": datetime.utcnow().isoformat(),
                "model": response.model,
                "provider": response.provider,
                "tokens_used": response.usage["total_tokens"],
            }

            # TODO: Cache result
            # await self.cache.set(cache_key, json.dumps(analysis), ttl=3600)

            return analysis

        except Exception as e:
            logger.error(
                f"Failed to generate analysis for {stock_code}: {e}. "
                f"LLM response: "
                f"{response.content if 'response' in locals() else 'N/A'}",
                exc_info=True,
            )
            raise StockAnalysisError(f"Analysis generation failed: {e}") from e

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse LLM response to structured format"""
        try:
            # Try to extract JSON from response
            json_start = content.find("{")
            json_end = content.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in response, using fallback parser")
                return self._fallback_parse(content)

        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}, using fallback")
            return self._fallback_parse(content)

    def _fallback_parse(self, content: str) -> Dict[str, Any]:
        """Fallback text parser for non-JSON responses"""
        return {
            "overall_rating": "Unknown",
            "confidence": 50,
            "strengths": [],
            "risks": [],
            "technical_summary": content[:500],
            "fundamental_assessment": "",
            "recommendation": "Please review the full text for details",
            "full_text": content,
        }
