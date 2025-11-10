"""WebSocket message schemas"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """WebSocket message types"""

    # Client -> Server
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PING = "ping"

    # Server -> Client
    PRICE_UPDATE = "price_update"
    ORDERBOOK_UPDATE = "orderbook_update"
    MARKET_STATUS = "market_status"
    ALERT = "alert"
    ERROR = "error"
    PONG = "pong"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"


class SubscriptionType(str, Enum):
    """Subscription types"""

    STOCK = "stock"  # Individual stock by code
    MARKET = "market"  # KOSPI, KOSDAQ
    SECTOR = "sector"  # Industry sector
    WATCHLIST = "watchlist"  # User watchlist


# ============================================================================
# Base Message Schemas
# ============================================================================


class WebSocketMessage(BaseModel):
    """Base WebSocket message"""

    type: MessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sequence: Optional[int] = None  # For message ordering


class WebSocketRequest(WebSocketMessage):
    """Client request message"""

    data: Dict[str, Any] = Field(default_factory=dict)


class WebSocketResponse(WebSocketMessage):
    """Server response message"""

    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


# ============================================================================
# Subscription Messages
# ============================================================================


class SubscribeRequest(BaseModel):
    """Subscribe to updates"""

    type: MessageType = MessageType.SUBSCRIBE
    subscription_type: SubscriptionType
    targets: List[str]  # Stock codes, market names, or sector names

    class Config:
        json_schema_extra = {
            "example": {
                "type": "subscribe",
                "subscription_type": "stock",
                "targets": ["005930", "000660"],
            }
        }


class UnsubscribeRequest(BaseModel):
    """Unsubscribe from updates"""

    type: MessageType = MessageType.UNSUBSCRIBE
    subscription_type: SubscriptionType
    targets: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "type": "unsubscribe",
                "subscription_type": "stock",
                "targets": ["005930"],
            }
        }


class SubscriptionResponse(WebSocketMessage):
    """Subscription confirmation"""

    subscription_type: SubscriptionType
    targets: List[str]


# ============================================================================
# Data Update Messages
# ============================================================================


class PriceUpdate(WebSocketMessage):
    """Real-time price update"""

    type: MessageType = MessageType.PRICE_UPDATE
    stock_code: str
    price: float
    change: float
    change_percent: float
    volume: int

    class Config:
        json_schema_extra = {
            "example": {
                "type": "price_update",
                "stock_code": "005930",
                "price": 72500.0,
                "change": 500.0,
                "change_percent": 0.69,
                "volume": 15234567,
                "timestamp": "2025-11-10T12:00:00Z",
            }
        }


class OrderBookLevel(BaseModel):
    """Single order book level"""

    price: float
    quantity: int
    orders: int = 0


class OrderBookUpdate(WebSocketMessage):
    """Real-time order book update"""

    type: MessageType = MessageType.ORDERBOOK_UPDATE
    stock_code: str
    bids: List[OrderBookLevel]  # Buy orders (highest to lowest)
    asks: List[OrderBookLevel]  # Sell orders (lowest to highest)

    class Config:
        json_schema_extra = {
            "example": {
                "type": "orderbook_update",
                "stock_code": "005930",
                "bids": [
                    {"price": 72500, "quantity": 1000, "orders": 5},
                    {"price": 72400, "quantity": 2000, "orders": 8},
                ],
                "asks": [
                    {"price": 72600, "quantity": 1500, "orders": 6},
                    {"price": 72700, "quantity": 1800, "orders": 7},
                ],
                "timestamp": "2025-11-10T12:00:00Z",
            }
        }


class MarketStatus(WebSocketMessage):
    """Market status update"""

    type: MessageType = MessageType.MARKET_STATUS
    market: str  # KOSPI, KOSDAQ
    status: str  # open, closed, pre_market, after_hours


class Alert(WebSocketMessage):
    """Alert notification"""

    type: MessageType = MessageType.ALERT
    alert_id: str
    stock_code: str
    alert_type: str  # price_target, volume_spike, news, etc.
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Control Messages
# ============================================================================


class PingMessage(WebSocketMessage):
    """Ping message (keep-alive)"""

    type: MessageType = MessageType.PING


class PongMessage(WebSocketMessage):
    """Pong response"""

    type: MessageType = MessageType.PONG


class ErrorMessage(WebSocketMessage):
    """Error message"""

    type: MessageType = MessageType.ERROR
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "type": "error",
                "code": "INVALID_SUBSCRIPTION",
                "message": "Stock code not found: 999999",
                "details": {"stock_code": "999999"},
                "timestamp": "2025-11-10T12:00:00Z",
            }
        }


# ============================================================================
# Connection Info
# ============================================================================


class ConnectionInfo(BaseModel):
    """WebSocket connection information"""

    connection_id: str
    user_id: Optional[str] = None
    connected_at: datetime
    subscriptions: Dict[SubscriptionType, List[str]] = Field(default_factory=dict)
    message_count: int = 0
    last_activity: datetime
