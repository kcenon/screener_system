"""Market overview Pydantic schemas"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

# ============================================================================
# Market Index Schemas
# ============================================================================


class MarketIndexData(BaseModel):
    """Market index data for API response"""

    code: str = Field(..., pattern="^(KOSPI|KOSDAQ|KRX100)$")
    name: str
    current: float = Field(..., gt=0)
    change: Optional[float] = None
    change_percent: Optional[float] = None
    high: Optional[float] = Field(None, gt=0)
    low: Optional[float] = Field(None, gt=0)
    volume: Optional[int] = Field(None, ge=0)
    value: Optional[int] = Field(None, ge=0)
    timestamp: datetime
    sparkline: List[float] = Field(default_factory=list)


class MarketIndicesResponse(BaseModel):
    """Response for market indices endpoint"""

    indices: List[MarketIndexData]
    updated_at: datetime


# ============================================================================
# Market Breadth Schemas
# ============================================================================


class MarketBreadthResponse(BaseModel):
    """Response for market breadth endpoint"""

    advancing: int = Field(..., ge=0)
    declining: int = Field(..., ge=0)
    unchanged: int = Field(..., ge=0)
    total: int = Field(..., ge=0)
    ad_ratio: float = Field(..., ge=0)
    sentiment: str = Field(..., pattern="^(bullish|neutral|bearish)$")
    market: str = Field(..., pattern="^(KOSPI|KOSDAQ|ALL)$")
    timestamp: datetime


# ============================================================================
# Sector Performance Schemas
# ============================================================================


class TopStock(BaseModel):
    """Top performing stock in a sector"""

    code: str
    name: str
    change_percent: Optional[float] = None


class SectorPerformance(BaseModel):
    """Sector performance data"""

    code: str
    name: str
    change_percent: float
    stock_count: int = Field(..., ge=0)
    market_cap: int = Field(..., ge=0)
    volume: Optional[int] = Field(None, ge=0)
    top_stock: Optional[TopStock] = None


class SectorPerformanceResponse(BaseModel):
    """Response for sector performance endpoint"""

    sectors: List[SectorPerformance]
    timeframe: str = Field(..., pattern="^(1D|1W|1M|3M)$")
    market: str = Field(..., pattern="^(KOSPI|KOSDAQ|ALL)$")
    updated_at: datetime


# ============================================================================
# Market Movers Schemas
# ============================================================================


class MarketMover(BaseModel):
    """Market mover (gainer or loser) data"""

    code: str = Field(..., min_length=6, max_length=6)
    name: str
    market: str = Field(..., pattern="^(KOSPI|KOSDAQ)$")
    current_price: int = Field(..., gt=0)
    change: int
    change_percent: float
    volume: Optional[int] = Field(None, ge=0)
    value: Optional[int] = Field(None, ge=0)
    sector: Optional[str] = None


class MarketMoversResponse(BaseModel):
    """Response for market movers endpoint"""

    type: str = Field(..., pattern="^(gainers|losers)$")
    market: str = Field(..., pattern="^(KOSPI|KOSDAQ|ALL)$")
    stocks: List[MarketMover]
    total: int = Field(..., ge=0)
    updated_at: datetime


# ============================================================================
# Most Active Schemas
# ============================================================================


class ActiveStock(BaseModel):
    """Most active stock data"""

    code: str = Field(..., min_length=6, max_length=6)
    name: str
    market: str = Field(..., pattern="^(KOSPI|KOSDAQ)$")
    current_price: int = Field(..., gt=0)
    change_percent: Optional[float] = None
    volume: Optional[int] = Field(None, ge=0)
    value: Optional[int] = Field(None, ge=0)
    sector: Optional[str] = None


class MostActiveResponse(BaseModel):
    """Response for most active stocks endpoint"""

    metric: str = Field(..., pattern="^(volume|value)$")
    market: str = Field(..., pattern="^(KOSPI|KOSDAQ|ALL)$")
    stocks: List[ActiveStock]
    total: int = Field(..., ge=0)
    updated_at: datetime


# ============================================================================
# Market Trend Schemas
# ============================================================================


class MarketTrendData(BaseModel):
    """Historical market trend data point"""

    timestamp: datetime
    open: Optional[float] = Field(None, gt=0)
    high: Optional[float] = Field(None, gt=0)
    low: Optional[float] = Field(None, gt=0)
    close: float = Field(..., gt=0)
    volume: Optional[int] = Field(None, ge=0)


class MarketTrendResponse(BaseModel):
    """Response for market trend endpoint"""

    index: str = Field(..., pattern="^(KOSPI|KOSDAQ|KRX100)$")
    timeframe: str = Field(..., pattern="^(1D|5D|1M|3M|6M|1Y)$")
    interval: str = Field(..., pattern="^(1m|5m|1h|1d)$")
    data: List[MarketTrendData]
    count: int = Field(..., ge=0)
    updated_at: datetime
