"""Pydantic schemas package"""

from app.schemas.screening import (FilterRange, ScreenedStock,
                                   ScreeningFilters, ScreeningMetadata,
                                   ScreeningRequest, ScreeningResponse,
                                   ScreeningTemplate, ScreeningTemplateList)
from app.schemas.stock import (CalculatedIndicator, DailyPrice,
                               DailyPriceListResponse, DailyPriceWithChanges,
                               FinancialStatement,
                               FinancialStatementListResponse,
                               FinancialStatementWithRatios, PaginationMeta,
                               Stock, StockDetail, StockListItem,
                               StockListResponse, StockSearchQuery,
                               StockSearchResponse, StockSearchResult)
from app.schemas.user import (RefreshTokenRequest, TokenPayload, TokenResponse,
                              UserCreate, UserLogin, UserResponse, UserUpdate)

__all__ = [
    # User schemas
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "TokenPayload",
    "TokenResponse",
    "RefreshTokenRequest",
    # Stock schemas
    "Stock",
    "StockDetail",
    "StockListItem",
    "StockListResponse",
    "DailyPrice",
    "DailyPriceWithChanges",
    "DailyPriceListResponse",
    "FinancialStatement",
    "FinancialStatementWithRatios",
    "FinancialStatementListResponse",
    "CalculatedIndicator",
    "PaginationMeta",
    "StockSearchQuery",
    "StockSearchResult",
    "StockSearchResponse",
    # Screening schemas
    "FilterRange",
    "ScreeningFilters",
    "ScreeningRequest",
    "ScreenedStock",
    "ScreeningMetadata",
    "ScreeningResponse",
    "ScreeningTemplate",
    "ScreeningTemplateList",
]
