---
id: sds-api-design
title: SDS - API Design
description: Software design specification - api design
sidebar_label: API Design
sidebar_position: 5
tags:
  - specification
  - design
  - architecture
---

:::info Navigation
- [Introduction](introduction.md)
- [System Architecture](system-architecture.md)
- [Component Design](component-design.md)
- [Database Design](database-design.md)
- [API Design](api-design.md) (Current)
- [Data Pipeline](data-pipeline.md)
- [Security Design](security-design.md)
- [Performance Design](performance-design.md)
- [Deployment](deployment.md)
- [Tech Stack & Decisions](tech-stack-decisions.md)
:::

# Software Design Specification - API Design

## 5. API Design

### 5.1 RESTful API Principles

**Design Principles**:
1. **Resource-Based URLs**: `/stocks/{code}`, `/portfolios/{id}`
2. **HTTP Methods**: GET (read), POST (create), PUT/PATCH (update), DELETE (delete)
3. **Stateless**: No server-side session state
4. **Hypermedia (HATEOAS)**: Include links in responses (Phase 2+)
5. **Versioning**: `/v1/` in URL path

### 5.2 API Endpoints

#### 5.2.1 Authentication Endpoints

```yaml
POST /v1/auth/register
  Summary: Register new user account
  Request Body:
    {
      "email": "user@example.com",
      "password": "SecurePass123",
      "name": "John Doe"
    }
  Response: 201 Created
    {
      "access_token": "eyJ...",
      "refresh_token": "eyJ...",
      "user": {
        "id": "uuid",
        "email": "user@example.com",
        "name": "John Doe",
        "tier": "free"
      }
    }

POST /v1/auth/login
  Summary: Login and receive JWT tokens
  Request Body:
    {
      "email": "user@example.com",
      "password": "SecurePass123"
    }
  Response: 200 OK
    {
      "access_token": "eyJ...",
      "refresh_token": "eyJ...",
      "user": { ... }
    }

POST /v1/auth/refresh
  Summary: Refresh expired access token
  Request Body:
    {
      "refresh_token": "eyJ..."
    }
  Response: 200 OK
    {
      "access_token": "eyJ..."
    }

POST /v1/auth/logout
  Summary: Revoke refresh token
  Headers: Authorization: Bearer <access_token>
  Response: 204 No Content
```

#### 5.2.2 Stock Endpoints

```yaml
GET /v1/stocks
  Summary: List all stocks with pagination
  Query Parameters:
    - market: KOSPI | KOSDAQ | ALL (default: ALL)
    - sector: string (optional)
    - page: integer (default: 1)
    - per_page: integer (default: 50, max: 100)
  Response: 200 OK
    {
      "stocks": [
        {
          "code": "005930",
          "name": "삼성전자",
          "market": "KOSPI",
          "sector": "Technology",
          "industry": "Semiconductors"
        },
        ...
      ],
      "meta": {
        "page": 1,
        "per_page": 50,
        "total": 2400,
        "pages": 48
      }
    }

GET /v1/stocks/{stock_code}
  Summary: Get detailed stock information
  Path Parameters:
    - stock_code: 6-digit string
  Response: 200 OK
    {
      "code": "005930",
      "name": "삼성전자",
      "market": "KOSPI",
      "sector": "Technology",
      "latest_price": {
        "close_price": 71000,
        "change_pct": 1.43,
        "volume": 15234567,
        "market_cap": 423000000000000,
        "trade_date": "2024-11-08"
      },
      "indicators": {
        "per": 15.2,
        "pbr": 1.4,
        "roe": 12.5,
        "dividend_yield": 2.8,
        "quality_score": 85,
        "value_score": 72,
        "growth_score": 65
      }
    }

GET /v1/stocks/{stock_code}/prices
  Summary: Get historical price data
  Path Parameters:
    - stock_code: 6-digit string
  Query Parameters:
    - from_date: YYYY-MM-DD (default: 1 year ago)
    - to_date: YYYY-MM-DD (default: today)
    - interval: daily | weekly | monthly (default: daily)
  Response: 200 OK
    {
      "stock_code": "005930",
      "interval": "daily",
      "prices": [
        {
          "trade_date": "2024-11-08",
          "open": 70000,
          "high": 72000,
          "low": 69500,
          "close": 71000,
          "volume": 15234567
        },
        ...
      ]
    }

GET /v1/stocks/{stock_code}/financials
  Summary: Get financial statements
  Path Parameters:
    - stock_code: 6-digit string
  Query Parameters:
    - period_type: quarterly | annual (default: quarterly)
    - years: integer (default: 5, max: 10)
  Response: 200 OK
    {
      "stock_code": "005930",
      "period_type": "quarterly",
      "financials": [
        {
          "fiscal_year": 2024,
          "fiscal_quarter": 3,
          "report_date": "2024-10-31",
          "revenue": 67400000000000,
          "operating_profit": 12520000000000,
          "net_profit": 9180000000000,
          "eps": 6250.00,
          "roe": 12.5
        },
        ...
      ]
    }
```

#### 5.2.3 Screening Endpoint

```yaml
POST /v1/screen
  Summary: Screen stocks with custom filters
  Request Body:
    {
      "market": "KOSPI" | "KOSDAQ" | "ALL",
      "filters": {
        "per": {"min": 0, "max": 15},
        "pbr": {"min": 0, "max": 1.5},
        "roe": {"min": 10},
        "dividend_yield": {"min": 3},
        "quality_score": {"min": 70}
      },
      "sort_by": "market_cap" | "per" | "roe" | ...,
      "order": "asc" | "desc",
      "page": 1,
      "per_page": 50
    }
  Response: 200 OK
    {
      "stocks": [
        {
          "code": "005930",
          "name": "삼성전자",
          "close_price": 71000,
          "per": 15.2,
          "pbr": 1.4,
          "roe": 12.5,
          "dividend_yield": 2.8,
          "quality_score": 85
        },
        ...
      ],
      "meta": {
        "page": 1,
        "per_page": 50,
        "total": 123,
        "pages": 3,
        "query_time_ms": 234
      }
    }
```

#### 5.2.4 Portfolio Endpoints

```yaml
POST /v1/portfolios
  Summary: Create new portfolio
  Headers: Authorization: Bearer <access_token>
  Request Body:
    {
      "name": "Growth Portfolio",
      "description": "High-growth tech stocks"
    }
  Response: 201 Created
    {
      "id": "uuid",
      "name": "Growth Portfolio",
      "description": "High-growth tech stocks",
      "created_at": "2024-11-08T10:30:00Z"
    }

GET /v1/portfolios
  Summary: List user's portfolios
  Headers: Authorization: Bearer <access_token>
  Response: 200 OK
    {
      "portfolios": [
        {
          "id": "uuid",
          "name": "Growth Portfolio",
          "holdings_count": 5,
          "total_value": 50000000,
          "unrealized_gain": 2500000,
          "unrealized_gain_pct": 5.26
        },
        ...
      ]
    }

GET /v1/portfolios/{portfolio_id}
  Summary: Get portfolio details with holdings
  Headers: Authorization: Bearer <access_token>
  Path Parameters:
    - portfolio_id: UUID
  Response: 200 OK
    {
      "id": "uuid",
      "name": "Growth Portfolio",
      "holdings": [
        {
          "stock_code": "005930",
          "stock_name": "삼성전자",
          "quantity": 10,
          "avg_price": 68000,
          "current_price": 71000,
          "purchase_value": 680000,
          "current_value": 710000,
          "unrealized_gain": 30000,
          "unrealized_gain_pct": 4.41
        },
        ...
      ],
      "summary": {
        "total_purchase_value": 47500000,
        "total_current_value": 50000000,
        "total_unrealized_gain": 2500000,
        "total_unrealized_gain_pct": 5.26
      }
    }

POST /v1/portfolios/{portfolio_id}/holdings
  Summary: Add stock to portfolio
  Headers: Authorization: Bearer <access_token>
  Request Body:
    {
      "stock_code": "005930",
      "quantity": 10,
      "avg_price": 68000,
      "purchase_date": "2024-09-10"
    }
  Response: 201 Created
    {
      "id": "uuid",
      "stock_code": "005930",
      "quantity": 10,
      "avg_price": 68000
    }
```

### 5.3 Error Handling

#### 5.3.1 Error Response Format

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": ["specific error"]
  },
  "timestamp": "2024-11-08T10:30:00Z",
  "path": "/v1/portfolios",
  "request_id": "uuid"
}
```

#### 5.3.2 HTTP Status Codes

| Code | Error Type | Usage |
|------|------------|-------|
| 400 | Bad Request | Invalid request parameters or validation errors |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Valid token but insufficient permissions (tier) |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource already exists (duplicate email, etc.) |
| 422 | Unprocessable Entity | Semantic errors in request |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Temporary service outage |

#### 5.3.3 Error Examples

**Validation Error (400)**

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid request parameters",
  "details": {
    "per_page": ["must be between 1 and 100"],
    "market": ["must be one of: KOSPI, KOSDAQ, ALL"]
  }
}
```

**Authentication Error (401)**

```json
{
  "error": "UNAUTHORIZED",
  "message": "Invalid or expired access token",
  "details": {}
}
```

**Tier Limit Error (403)**

```json
{
  "error": "TIER_LIMIT_EXCEEDED",
  "message": "Feature not available in your tier",
  "details": {
    "required_tier": "pro",
    "current_tier": "basic",
    "upgrade_url": "https://screener.kr/pricing"
  }
}
```

**Rate Limit Error (429)**

```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests",
  "details": {
    "limit": 100,
    "remaining": 0,
    "reset_at": "2024-11-08T11:00:00Z"
  }
}
```

### 5.4 Rate Limiting

#### 5.4.1 Rate Limit Implementation

```python
# core/rate_limiter.py
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.core.cache import cache

class RateLimiter:
    """Token bucket rate limiter using Redis."""

    TIER_LIMITS = {
        "free": 100,      # 100 requests/minute
        "basic": 500,     # 500 requests/minute
        "pro": 2000,      # 2000 requests/minute
    }

    async def check_rate_limit(self, user_id: str, tier: str):
        """Check if user has exceeded rate limit."""
        limit = self.TIER_LIMITS.get(tier, 100)
        key = f"rate_limit:{user_id}"

        # Get current count
        current = await cache.get(key)

        if current is None:
            # First request in this window
            await cache.set(key, 1, ttl=60)  # 60 seconds window
            return {
                "limit": limit,
                "remaining": limit - 1,
                "reset_at": datetime.utcnow() + timedelta(seconds=60)
            }

        current = int(current)

        if current >= limit:
            # Rate limit exceeded
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests",
                    "details": {
                        "limit": limit,
                        "remaining": 0,
                        "reset_at": (
                            datetime.utcnow() + timedelta(seconds=60)
                        ).isoformat()
                    }
                }
            )

        # Increment counter
        await cache.redis.incr(key)

        return {
            "limit": limit,
            "remaining": limit - current - 1,
            "reset_at": datetime.utcnow() + timedelta(seconds=60)
        }

rate_limiter = RateLimiter()
```

#### 5.4.2 Rate Limit Middleware

```python
# api/dependencies.py
from fastapi import Request
from app.core.rate_limiter import rate_limiter

async def check_rate_limit(request: Request, user: User = Depends(get_current_user)):
    """Dependency to check rate limits."""
    rate_info = await rate_limiter.check_rate_limit(str(user.id), user.tier)

    # Add rate limit headers
    request.state.rate_limit_info = rate_info

# Middleware to add headers
@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    response = await call_next(request)

    if hasattr(request.state, "rate_limit_info"):
        info = request.state.rate_limit_info
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = info["reset_at"].isoformat()

    return response
```

### 5.5 WebSocket Architecture

#### 5.5.1 WebSocket Server Design

**Purpose**: Real-time bidirectional communication for price updates, order book data, and alerts.

**Architecture**:

```
┌─────────────────────────────────────────────────────────────────┐
│                        WebSocket Clients                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Browser 1   │  │  Browser 2   │  │  Browser N   │          │
│  │  (React)     │  │  (React)     │  │  (React)     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │ WSS              │ WSS              │ WSS
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                 WebSocket Connection Manager                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Connection Pool (10,000+ concurrent connections)          │ │
│  │  - JWT authentication on handshake                         │ │
│  │  - Heartbeat (ping/pong every 30s)                         │ │
│  │  - Auto-reconnect with exponential backoff                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Room-Based Subscription Manager                           │ │
│  │  - Subscribe/unsubscribe to stock codes                    │ │
│  │  - Subscribe to market (KOSPI/KOSDAQ)                      │ │
│  │  - Subscribe to sector                                     │ │
│  │  - Multiple subscriptions per connection                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Redis Pub/Sub Layer                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Channels:                                                  │ │
│  │  - price:{stock_code}     (e.g., price:005930)            │ │
│  │  - orderbook:{stock_code} (e.g., orderbook:005930)        │ │
│  │  - market:{market_type}   (e.g., market:KOSPI)            │ │
│  │  - alert:{user_id}        (e.g., alert:123)               │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────────┘
                           ▲
                           │ Publish Updates
                           │
┌──────────────────────────┴───────────────────────────────────────┐
│               Data Source Adapter (KIS API)                      │
│  - Polls KIS API for price/orderbook updates                    │
│  - Publishes changes to Redis channels                          │
│  - Rate limiting (20 req/sec)                                   │
└──────────────────────────────────────────────────────────────────┘
```

#### 5.5.2 WebSocket Endpoint Implementation

```python
# api/websockets/stock_ws.py
from fastapi import WebSocket, WebSocketDisconnect, Depends
from app.core.auth import verify_ws_token
from app.core.cache import redis_client
import json
import asyncio

class ConnectionManager:
    """Manage WebSocket connections and subscriptions."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.subscriptions: dict[str, set[str]] = {}  # {connection_id: {room1, room2}}
        self.rooms: dict[str, set[str]] = {}  # {room: {conn_id1, conn_id2}}

    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.subscriptions[connection_id] = set()

    def disconnect(self, connection_id: str):
        """Remove connection and all subscriptions."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # Remove from all subscribed rooms
        if connection_id in self.subscriptions:
            for room in self.subscriptions[connection_id]:
                if room in self.rooms:
                    self.rooms[room].discard(connection_id)
            del self.subscriptions[connection_id]

    def subscribe(self, connection_id: str, room: str):
        """Subscribe connection to a room."""
        if connection_id in self.subscriptions:
            self.subscriptions[connection_id].add(room)

        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(connection_id)

    def unsubscribe(self, connection_id: str, room: str):
        """Unsubscribe connection from a room."""
        if connection_id in self.subscriptions:
            self.subscriptions[connection_id].discard(room)

        if room in self.rooms:
            self.rooms[room].discard(connection_id)

    async def send_to_connection(self, connection_id: str, message: dict):
        """Send message to specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            await websocket.send_json(message)

    async def broadcast_to_room(self, room: str, message: dict):
        """Broadcast message to all connections in a room."""
        if room in self.rooms:
            disconnected = []
            for connection_id in self.rooms[room]:
                try:
                    await self.send_to_connection(connection_id, message)
                except Exception:
                    disconnected.append(connection_id)

            # Clean up disconnected clients
            for connection_id in disconnected:
                self.disconnect(connection_id)

manager = ConnectionManager()


@router.websocket("/ws/stocks")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time stock data.

    Authentication: JWT token in query parameter.
    """
    # Verify JWT token
    try:
        user = await verify_ws_token(token)
    except Exception:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    connection_id = f"{user.id}_{datetime.utcnow().timestamp()}"

    await manager.connect(websocket, connection_id)

    try:
        # Start heartbeat task
        heartbeat_task = asyncio.create_task(
            send_heartbeat(websocket, connection_id)
        )

        # Start Redis Pub/Sub listener
        pubsub_task = asyncio.create_task(
            redis_subscriber(connection_id)
        )

        while True:
            # Receive messages from client
            data = await websocket.receive_json()

            message_type = data.get("type")

            if message_type == "subscribe":
                # Subscribe to stock updates
                stock_code = data.get("stock_code")
                room = f"price:{stock_code}"
                manager.subscribe(connection_id, room)

                await websocket.send_json({
                    "type": "subscribed",
                    "stock_code": stock_code,
                    "timestamp": datetime.utcnow().isoformat()
                })

            elif message_type == "unsubscribe":
                # Unsubscribe from stock updates
                stock_code = data.get("stock_code")
                room = f"price:{stock_code}"
                manager.unsubscribe(connection_id, room)

                await websocket.send_json({
                    "type": "unsubscribed",
                    "stock_code": stock_code,
                    "timestamp": datetime.utcnow().isoformat()
                })

            elif message_type == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        heartbeat_task.cancel()
        pubsub_task.cancel()

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(connection_id)
        heartbeat_task.cancel()
        pubsub_task.cancel()


async def send_heartbeat(websocket: WebSocket, connection_id: str):
    """Send periodic heartbeat to keep connection alive."""
    while True:
        try:
            await asyncio.sleep(30)
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception:
            break


async def redis_subscriber(connection_id: str):
    """
    Subscribe to Redis Pub/Sub and forward messages to WebSocket.
    """
    pubsub = redis_client.pubsub()

    while True:
        # Get subscribed rooms for this connection
        rooms = manager.subscriptions.get(connection_id, set())

        # Subscribe to Redis channels for each room
        for room in rooms:
            await pubsub.subscribe(room)

        # Listen for messages
        try:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message and message['type'] == 'message':
                data = json.loads(message['data'])

                # Forward to WebSocket client
                await manager.send_to_connection(connection_id, data)

        except Exception as e:
            logger.error(f"Redis subscriber error: {e}")
            break

        await asyncio.sleep(0.01)  # Prevent tight loop
```

#### 5.5.3 Message Format Specification

**Subscribe Message** (Client → Server):
```json
{
  "type": "subscribe",
  "stock_code": "005930",
  "timestamp": "2025-11-09T10:30:00Z"
}
```

**Price Update Message** (Server → Client):
```json
{
  "type": "price_update",
  "stock_code": "005930",
  "data": {
    "current_price": 75000,
    "change_amount": 1000,
    "change_percent": 1.35,
    "volume": 12500000,
    "timestamp": "2025-11-09T10:30:15.123Z"
  },
  "sequence": 12345,
  "timestamp": "2025-11-09T10:30:15.125Z"
}
```

**Order Book Update Message** (Server → Client):
```json
{
  "type": "orderbook_update",
  "stock_code": "005930",
  "data": {
    "asks": [
      {"price": 75100, "volume": 5000, "total": 5000},
      {"price": 75200, "volume": 3000, "total": 8000},
      // ... up to 10 levels
    ],
    "bids": [
      {"price": 75000, "volume": 8000, "total": 8000},
      {"price": 74900, "volume": 4000, "total": 12000},
      // ... up to 10 levels
    ],
    "spread": 100,
    "spread_pct": 0.13,
    "timestamp": "2025-11-09T10:30:15.123Z"
  },
  "sequence": 12346,
  "timestamp": "2025-11-09T10:30:15.125Z"
}
```

#### 5.5.4 Performance Considerations

**Connection Pooling**:
- Target: Support 10,000+ concurrent connections
- Memory per connection: ~10KB → 100MB for 10K connections
- CPU overhead: Minimal (event-driven architecture)

**Message Batching**:
- Batch updates within 10-50ms window
- Reduce message frequency for high-update stocks
- Example: If price changes 100 times/sec, batch to 20 messages/sec

**Compression**:
- Use per-message deflate extension (WebSocket compression)
- Reduces message size by ~60-70% for JSON payloads

**Redis Pub/Sub Scalability**:
- Horizontal scaling: Multiple API instances subscribe to same Redis
- Automatic broadcasting to all connected clients across instances
- No single point of failure

---