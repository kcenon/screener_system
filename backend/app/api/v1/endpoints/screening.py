"""Stock screening endpoints for filtering and templates"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheManager, get_cache
from app.db.session import get_db
from app.schemas.screening import (ScreeningRequest, ScreeningResponse,
                                   ScreeningTemplateList)
from app.services.screening_service import ScreeningService

router = APIRouter(prefix="/screen", tags=["screening"])


def get_screening_service(
    db: AsyncSession = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
) -> ScreeningService:
    """Dependency to get screening service instance"""
    return ScreeningService(db, cache)


# ============================================================================
# Stock Screening Endpoints
# ============================================================================


@router.post(
    "",
    response_model=ScreeningResponse,
    status_code=status.HTTP_200_OK,
    summary="Screen stocks with filters",
    description="""
    Screen stocks using 200+ indicators and filters.

    **Features:**
    - Filter by market, sector, industry
    - 40+ valuation, profitability, growth, stability indicators
    - Price momentum and volume filters
    - Composite quality, value, growth scores
    - Sorting and pagination
    - Response cached for 5 minutes

    **Rate Limits:**

    This endpoint has two levels of rate limiting:

    1. **Tier-based limits** (applies to all API endpoints):
       - Free tier: 100 requests per hour
       - Basic tier: 1,000 requests per hour
       - Pro tier: 10,000 requests per hour

    2. **Endpoint-specific limit** (applies only to screening):
       - 50 requests per hour (additional restriction due to query complexity)

    When you exceed either limit, you'll receive a 429 response:
    ```json
    {
      "success": false,
      "message": "Rate limit exceeded",
      "detail": "Maximum 50 requests per hour allowed for /v1/screen"
    }
    ```

    **Rate Limit Headers:**

    Every response includes rate limit information:
    - `X-RateLimit-Limit`: Maximum requests allowed per hour
    - `X-RateLimit-Remaining`: Requests remaining in current window
    - `X-RateLimit-Reset`: Seconds until limit resets (3600 = 1 hour)
    - `X-RateLimit-Endpoint`: Current endpoint path (screening endpoints only)
    - `Retry-After`: Seconds to wait before retrying (429 responses only)

    **Performance Target:**
    - Simple queries: < 200ms (p95)
    - Complex queries: < 500ms (p99)
    - Cache hit: < 50ms

    **Examples:**
    ```json
    {
      "filters": {
        "market": "KOSPI",
        "per": {"min": 0, "max": 15},
        "roe": {"min": 10},
        "dividend_yield": {"min": 3}
      },
      "sort_by": "market_cap",
      "order": "desc",
      "page": 1,
      "per_page": 50
    }
    ```

    **Best Practices:**
    - Monitor `X-RateLimit-Remaining` header to avoid hitting limits
    - Use caching: identical requests within 5 minutes return cached results
    - Batch filters instead of making multiple separate requests
    - Consider using predefined templates for common queries
    """,
    responses={
        200: {
            "description": "Successful screening with stocks and metadata",
            "headers": {
                "X-RateLimit-Limit": {
                    "description": "Maximum requests allowed per hour for this endpoint",
                    "schema": {"type": "integer", "example": 50}
                },
                "X-RateLimit-Remaining": {
                    "description": "Requests remaining in current 1-hour window",
                    "schema": {"type": "integer", "example": 45}
                },
                "X-RateLimit-Reset": {
                    "description": "Seconds until rate limit resets (always 3600 for 1-hour window)",
                    "schema": {"type": "integer", "example": 3600}
                },
                "X-RateLimit-Endpoint": {
                    "description": "Current endpoint path",
                    "schema": {"type": "string", "example": "/v1/screen"}
                }
            }
        },
        429: {
            "description": "Rate limit exceeded - too many requests",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Endpoint rate limit exceeded",
                        "detail": "Maximum 50 requests per hour allowed for /v1/screen"
                    }
                }
            },
            "headers": {
                "X-RateLimit-Limit": {
                    "description": "Maximum requests allowed per hour",
                    "schema": {"type": "integer", "example": 50}
                },
                "X-RateLimit-Remaining": {
                    "description": "Requests remaining (0 when rate limited)",
                    "schema": {"type": "integer", "example": 0}
                },
                "X-RateLimit-Reset": {
                    "description": "Seconds until rate limit resets",
                    "schema": {"type": "integer", "example": 3600}
                },
                "X-RateLimit-Endpoint": {
                    "description": "Endpoint that exceeded the limit",
                    "schema": {"type": "string", "example": "/v1/screen"}
                },
                "Retry-After": {
                    "description": "Seconds to wait before retrying",
                    "schema": {"type": "integer", "example": 3600}
                }
            }
        }
    },
)
async def screen_stocks(
    request: ScreeningRequest,
    screening_service: ScreeningService = Depends(get_screening_service),
):
    """
    Screen stocks with advanced filters

    Execute stock screening with multiple indicator filters.
    Results are sorted, paginated, and cached for performance.

    **Request Body:**
    - `filters`: ScreeningFilters object with all filter options
    - `sort_by`: Field to sort by (default: market_cap)
    - `order`: Sort order - "asc" or "desc" (default: desc)
    - `page`: Page number, 1-indexed (default: 1)
    - `per_page`: Results per page, 1-200 (default: 50)

    **Response:**
    - `stocks`: List of matching stocks with all indicator data
    - `meta`: Pagination metadata (total, page, per_page, total_pages)
    - `query_time_ms`: Query execution time in milliseconds
    - `filters_applied`: Summary of applied filters

    **Notes:**
    - NULL indicator values are excluded from filters
    - Multiple filters are combined with AND logic
    - Results are cached based on filter hash
    - Cache is invalidated after daily indicator calculation
    """
    return await screening_service.execute_screening(request)


@router.get(
    "/templates",
    response_model=ScreeningTemplateList,
    status_code=status.HTTP_200_OK,
    summary="Get screening templates",
    description="""
    Get predefined screening templates for common strategies.

    **Available Templates:**
    - **dividend_stocks**: High dividend yield stocks (> 3%)
    - **value_stocks**: Undervalued stocks (low PER/PBR, positive ROE)
    - **growth_stocks**: High growth companies (revenue growth > 20%)
    - **quality_stocks**: High quality companies (F-Score >= 7)
    - **momentum_stocks**: Strong price momentum (1-3 month gains)

    **Template Response:**
    Each template includes:
    - `id`: Unique template identifier
    - `name`: Display name (Korean + English)
    - `description`: Strategy description
    - `filters`: Predefined filter criteria
    - `sort_by`: Default sort field
    - `order`: Default sort order

    **Usage:**
    1. GET /v1/screen/templates to see all templates
    2. POST /v1/screen/templates/{template_id} to apply a template
    3. Or use template filters in POST /v1/screen

    Cached for 1 hour.
    """,
)
async def get_screening_templates(
    screening_service: ScreeningService = Depends(get_screening_service),
):
    """
    Get available screening templates

    Returns a list of predefined screening templates
    for common investment strategies.
    """
    return await screening_service.get_templates()


@router.post(
    "/templates/{template_id}",
    response_model=ScreeningResponse,
    status_code=status.HTTP_200_OK,
    summary="Apply screening template",
    description="""
    Apply a predefined screening template.

    **Available Template IDs:**
    - `dividend_stocks`: 고배당주 (High Dividend)
    - `value_stocks`: 가치주 (Value Stocks)
    - `growth_stocks`: 성장주 (Growth Stocks)
    - `quality_stocks`: 우량주 (Quality Stocks)
    - `momentum_stocks`: 모멘텀주 (Momentum Stocks)

    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `per_page`: Results per page (default: 50)

    **Response:**
    Same as POST /v1/screen with template filters applied.

    **Example:**
    ```
    POST /v1/screen/templates/dividend_stocks?page=1&per_page=50
    ```

    Returns stocks with:
    - Dividend yield > 3%
    - Quality score > 70
    - Sorted by dividend yield (descending)
    """,
)
async def apply_screening_template(
    template_id: str,
    page: int = 1,
    per_page: int = 50,
    screening_service: ScreeningService = Depends(get_screening_service),
):
    """
    Apply a predefined screening template

    Execute screening using a predefined template's filters.
    Pagination can be customized via query parameters.
    """
    return await screening_service.apply_template(
        template_id=template_id,
        page=page,
        per_page=per_page,
    )
