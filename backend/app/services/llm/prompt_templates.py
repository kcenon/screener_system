from typing import Dict, Any
from jinja2 import Template

class PromptTemplate:
    """Prompt template with variable substitution"""

    STOCK_ANALYSIS_TEMPLATE = """
You are a professional stock market analyst. Analyze the following stock and provide a comprehensive report.

**Stock Information:**
- Company: {{ company_name }} ({{ stock_code }})
- Sector: {{ sector }}
- Current Price: ${{ current_price }}

**Fundamental Data:**
- PER: {{ per }}
- PBR: {{ pbr }}
- ROE: {{ roe }}%
- Debt Ratio: {{ debt_ratio }}%
- Dividend Yield: {{ dividend_yield }}%

**Technical Indicators:**
- RSI (14): {{ rsi }}
- MACD: {{ macd_status }}
- Moving Averages: {{ ma_status }}

**Recent Performance:**
- 1 Month: {{ return_1m }}%
- 3 Months: {{ return_3m }}%
- 6 Months: {{ return_6m }}%

**AI Prediction:**
{{ ai_prediction }}

Please provide:
1. **Overall Rating** (Strong Buy / Buy / Hold / Sell / Strong Sell) with confidence percentage
2. **Key Strengths** (3-5 bullet points)
3. **Key Risks** (3-5 bullet points)
4. **Technical Analysis** (brief summary of chart patterns and indicators)
5. **Fundamental Assessment** (valuation and financial health)
6. **Recommendation** (specific action with price targets)

Format your response as JSON with the following structure:
```json
{
  "overall_rating": "Buy",
  "confidence": 75,
  "strengths": ["...", "..."],
  "risks": ["...", "..."],
  "technical_summary": "...",
  "fundamental_assessment": "...",
  "recommendation": "...",
  "price_targets": {
    "conservative": 50.00,
    "moderate": 55.00,
    "optimistic": 60.00
  }
}
```
"""

    @classmethod
    def render(cls, template_name: str, context: Dict[str, Any]) -> str:
        """Render template with context variables"""
        if template_name == "stock_analysis":
            template = Template(cls.STOCK_ANALYSIS_TEMPLATE)
        else:
            raise ValueError(f"Unknown template: {template_name}")

        return template.render(**context)
