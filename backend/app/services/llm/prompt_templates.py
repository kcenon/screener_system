from typing import Dict, Any
from jinja2 import Template


class PromptTemplate:
    """Collection of prompt templates"""

    STOCK_ANALYSIS_TEMPLATE = """
You are a professional stock market analyst. Analyze the following stock
and provide a comprehensive report.

Stock Code: {{ stock_code }}
Company: {{ company_name }}
Sector: {{ sector }}

## Financial Data
- Current Price: {{ current_price }}
- PER: {{ per }}
- PBR: {{ pbr }}
- ROE: {{ roe }}%
- Debt Ratio: {{ debt_ratio }}%
- Dividend Yield: {{ dividend_yield }}%

## Technical Indicators
- RSI: {{ rsi }}
- MACD Status: {{ macd_status }}
- Moving Average Status: {{ ma_status }}
- Returns: 1M {{ return_1m }}%, 3M {{ return_3m }}%, 6M {{ return_6m }}%

## AI Prediction
{{ ai_prediction }}

Please provide a detailed analysis including:
1. **Overall Rating** (Strong Buy / Buy / Hold / Sell / Strong Sell)
   with confidence percentage
2. **Key Strengths** (3-5 bullet points)
3. **Key Risks** (3-5 bullet points)
4. **Technical Analysis Summary**
5. **Fundamental Analysis Summary**
6. **Investment Recommendation**

Format the output as a JSON object with the following keys:
- overall_rating: string
- confidence: number (0-100)
- strengths: list of strings
- risks: list of strings
- technical_summary: string
- fundamental_assessment: string
- recommendation: string
- price_targets: object (with conservative, moderate, optimistic keys)
"""

    @classmethod
    def render(cls, template_name: str, context: Dict[str, Any]) -> str:
        """Render template with context variables"""
        if template_name == "stock_analysis":
            template = Template(cls.STOCK_ANALYSIS_TEMPLATE)
        else:
            raise ValueError(f"Unknown template: {template_name}")

        return template.render(**context)
