---
id: websocket-api
title: WebSocket API
description: Real-time WebSocket API for stock price updates and order book data
sidebar_label: WebSocket API
sidebar_position: 3
tags:
  - api
  - websocket
  - real-time
  - streaming
last_updated: 2025-11-13
---

# WebSocket API Documentation

## Overview

The Stock Screening Platform provides a WebSocket API for real-time stock price updates, order book data, and market alerts. The WebSocket server supports:

- **Real-time updates**: Sub-100ms latency for price and order book changes
- **Multi-instance support**: Redis Pub/Sub for horizontal scalability
- **High performance**: Message batching, compression, and rate limiting
- **Session restoration**: Automatic reconnection with subscription recovery
- **10K+ concurrent connections**: Load tested and production-ready

## Connection

### Endpoint

```
ws://localhost:8000/v1/ws
wss://api.screener.kr/v1/ws (production)
```

### Authentication

Optional JWT token can be passed as query parameter:

```javascript
const ws = new WebSocket('ws://localhost:8000/v1/ws?token=YOUR_JWT_TOKEN');
```

Anonymous connections are supported for public data.

### Connection Options

```javascript
// Enable compression (recommended for production)
const ws = new WebSocket('ws://localhost:8000/v1/ws', {
  perMessageDeflate: true
});
```

## Message Format

All messages are JSON with the following base structure:

```json
{
  "type": "message_type",
  "timestamp": "2025-11-11T00:00:00Z",
  "sequence": 12345,
  ...additional fields
}
```

### Message Types

#### Client → Server

- `subscribe`: Subscribe to stock/market updates
- `unsubscribe`: Unsubscribe from updates
- `ping`: Heartbeat check
- `refresh_token`: Refresh JWT token
- `reconnect`: Reconnect with session restoration

#### Server → Client

- `price_update`: Stock price change
- `orderbook_update`: Order book (호가) change
- `market_status`: Market open/close events
- `alert`: Price alerts
- `error`: Error messages
- `pong`: Heartbeat response
- `batch`: Batched messages (Phase 4)

## Subscription

### Subscribe to Stock Updates

```json
{
  "type": "subscribe",
  "subscription_type": "stock",
  "targets": ["005930", "000660", "035720"]
}
```

Response:

```json
{
  "type": "subscribed",
  "subscription_type": "stock",
  "targets": ["005930", "000660", "035720"],
  "timestamp": "2025-11-11T00:00:00Z"
}
```

### Subscribe to Market Updates

```json
{
  "type": "subscribe",
  "subscription_type": "market",
  "targets": ["KOSPI", "KOSDAQ"]
}
```

### Subscribe to Sector Updates

```json
{
  "type": "subscribe",
  "subscription_type": "sector",
  "targets": ["IT", "FINANCE"]
}
```

### Unsubscribe

```json
{
  "type": "unsubscribe",
  "subscription_type": "stock",
  "targets": ["005930"]
}
```

## Real-time Updates

### Price Update

```json
{
  "type": "price_update",
  "code": "005930",
  "name": "Samsung Electronics",
  "price": 73000,
  "change": 1000,
  "change_percent": 1.39,
  "volume": 12345678,
  "timestamp": "2025-11-11T09:30:00Z",
  "sequence": 12345
}
```

### Order Book Update

```json
{
  "type": "orderbook_update",
  "code": "005930",
  "bids": [
    {"price": 72900, "quantity": 1000},
    {"price": 72800, "quantity": 1500}
  ],
  "asks": [
    {"price": 73000, "quantity": 800},
    {"price": 73100, "quantity": 1200}
  ],
  "timestamp": "2025-11-11T09:30:00Z",
  "sequence": 12346
}
```

### Market Status

```json
{
  "type": "market_status",
  "market": "KOSPI",
  "status": "open",
  "timestamp": "2025-11-11T09:00:00Z",
  "sequence": 12347
}
```

### Alert

```json
{
  "type": "alert",
  "code": "005930",
  "alert_type": "price_above",
  "threshold": 75000,
  "current_price": 75100,
  "message": "Samsung Electronics exceeded 75,000 KRW",
  "timestamp": "2025-11-11T10:00:00Z",
  "sequence": 12348
}
```

## Phase 4: Performance Features

### Message Batching

:::tip Performance Optimization
Message batching is **enabled by default** to reduce network overhead and improve throughput.
:::

Messages are queued and sent in batches every **30ms** (configurable):

```json
{
  "type": "batch",
  "batch_size": 5,
  "messages": [
    {
      "type": "price_update",
      "code": "005930",
      "price": 73000,
      ...
    },
    {
      "type": "price_update",
      "code": "000660",
      "price": 145000,
      ...
    },
    ...
  ],
  "timestamp": "2025-11-11T09:30:00.030Z",
  "sequence": 12349
}
```

**Client Implementation:**

```javascript
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  if (message.type === 'batch') {
    // Process batched messages
    message.messages.forEach(msg => {
      handleMessage(msg);
    });
  } else {
    // Process single message
    handleMessage(message);
  }
};
```

**Performance Impact:**
- Reduces WebSocket send() calls by ~80%
- Lower CPU usage on both server and client
- Better throughput for high-frequency updates

### Rate Limiting

**100 messages per second per connection** (default, configurable)

If rate limit is exceeded:

```json
{
  "type": "error",
  "code": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded (100 messages/second)",
  "details": {
    "rate_limit": 100
  },
  "timestamp": "2025-11-11T09:30:00Z"
}
```

**Best Practices:**
- Subscribe only to stocks you're actively monitoring
- Unsubscribe when switching views
- Use market/sector subscriptions for overview pages

See [Rate Limiting Guide](./rate-limiting.md) for more details.

### Compression

**Per-message deflate** compression is auto-negotiated with clients.

Enable in browser:

```javascript
const ws = new WebSocket('ws://localhost:8000/v1/ws', {
  perMessageDeflate: {
    clientMaxWindowBits: 14,
    serverMaxWindowBits: 14
  }
});
```

**Performance Impact:**
- Reduces bandwidth by 60-80% for text messages
- Minimal CPU overhead
- Recommended for production

## Session Restoration (Phase 3)

If disconnected, reconnect with your previous session ID:

```javascript
// Save session ID on connect
let sessionId = null;

ws.onopen = () => {
  // Extract connection_id from first message
};

ws.onclose = () => {
  // Reconnect with session restoration
  const reconnectUrl = `ws://localhost:8000/v1/ws?session_id=${sessionId}&token=${jwt}`;
  ws = new WebSocket(reconnectUrl);
};
```

Session restoration response:

```json
{
  "type": "reconnected",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "restored_subscriptions": {
    "stock": ["005930", "000660"],
    "market": ["KOSPI"]
  },
  "missed_messages_count": 5,
  "timestamp": "2025-11-11T09:30:10Z"
}
```

**Session TTL**: 5 minutes

## Error Handling

### Error Codes

- `INVALID_MESSAGE`: Malformed JSON or invalid message type
- `INVALID_TOKEN`: JWT token validation failed
- `SUBSCRIPTION_FAILED`: Unable to subscribe to target
- `RATE_LIMIT_EXCEEDED`: Too many messages sent
- `SESSION_RESTORATION_FAILED`: Session not found or expired
- `TOKEN_REFRESH_ERROR`: Token refresh failed

### Error Message Format

```json
{
  "type": "error",
  "code": "ERROR_CODE",
  "message": "Human-readable error description",
  "details": {
    "additional": "context"
  },
  "timestamp": "2025-11-11T09:30:00Z"
}
```

## Monitoring

### Connection Statistics

**GET** `/v1/ws/stats`

```json
{
  "active_connections": 1234,
  "total_subscriptions": 5678,
  "subscriptions_by_type": {
    "stock": 4000,
    "market": 1000,
    "sector": 678
  },
  "messages_sent": 123456,
  "saved_sessions": 5,
  "batching_enabled": true,
  "batch_interval_ms": 30,
  "queued_messages": 45,
  "rate_limiting_enabled": true,
  "rate_limit": 100
}
```

### Connection List

**GET** `/v1/ws/connections`

```json
[
  {
    "connection_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user-123",
    "connected_at": "2025-11-11T09:00:00Z",
    "subscriptions": {
      "stock": ["005930", "000660"],
      "market": ["KOSPI"]
    },
    "message_count": 1234,
    "last_activity": "2025-11-11T09:30:00Z"
  }
]
```

## Load Testing

Use the provided load testing script:

```bash
cd backend/tests/load
python websocket_load_test.py --connections 10000 --duration 60
```

Options:
- `--url`: WebSocket URL (default: ws://localhost:8000/v1/ws)
- `--connections`: Number of concurrent connections (default: 1000)
- `--duration`: Test duration in seconds (default: 60)
- `--ramp-up`: Ramp-up time in seconds (default: 10)
- `--batch-size`: Connections per batch (default: 100)

## Performance Targets

| Metric | Target | Achieved |
|--------|--------|----------|
| Concurrent connections | 10,000 | ✅ |
| Latency (p99) | < 100ms | ✅ |
| Message throughput | 100,000 msg/s | ✅ |
| Memory per connection | < 100KB | ✅ |
| CPU usage (10K connections) | < 50% | ✅ |

## Best Practices

### Client Implementation

```javascript
class StockWebSocket {
  constructor(url, token) {
    this.url = url;
    this.token = token;
    this.ws = null;
    this.sessionId = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    const wsUrl = this.sessionId
      ? `${this.url}?session_id=${this.sessionId}&token=${this.token}`
      : `${this.url}?token=${this.token}`;

    this.ws = new WebSocket(wsUrl, {
      perMessageDeflate: true  // Enable compression
    });

    this.ws.onopen = () => {
      console.log('Connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onclose = () => {
      console.log('Disconnected');
      this.reconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  handleMessage(message) {
    // Handle batch messages
    if (message.type === 'batch') {
      message.messages.forEach(msg => this.processMessage(msg));
      return;
    }

    this.processMessage(message);
  }

  processMessage(message) {
    switch (message.type) {
      case 'price_update':
        this.onPriceUpdate(message);
        break;
      case 'orderbook_update':
        this.onOrderBookUpdate(message);
        break;
      case 'error':
        this.onError(message);
        break;
      // ... handle other types
    }
  }

  subscribe(type, targets) {
    this.ws.send(JSON.stringify({
      type: 'subscribe',
      subscription_type: type,
      targets: targets
    }));
  }

  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);

    console.log(`Reconnecting in ${delay}ms...`);
    setTimeout(() => this.connect(), delay);
  }
}
```

### Subscription Management

```javascript
// Subscribe to individual stocks
ws.subscribe('stock', ['005930', '000660', '035720']);

// Subscribe to markets for overview
ws.subscribe('market', ['KOSPI', 'KOSDAQ']);

// Unsubscribe when leaving detail page
ws.unsubscribe('stock', ['005930']);
```

### Memory Management

```javascript
// Limit subscription count to prevent rate limiting
const MAX_SUBSCRIPTIONS = 50;

function addSubscription(code) {
  if (subscriptions.size >= MAX_SUBSCRIPTIONS) {
    // Remove oldest subscription
    const oldest = subscriptions.values().next().value;
    ws.unsubscribe('stock', [oldest]);
    subscriptions.delete(oldest);
  }

  ws.subscribe('stock', [code]);
  subscriptions.add(code);
}
```

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to WebSocket

**Solutions**:
1. Check if backend server is running: `curl http://localhost:8000/health`
2. Verify WebSocket URL (ws:// for http, wss:// for https)
3. Check JWT token validity: `curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me`

### Rate Limiting

**Problem**: Getting `RATE_LIMIT_EXCEEDED` errors

**Solutions**:
1. Reduce subscription count
2. Unsubscribe from unused stocks
3. Use market/sector subscriptions instead of individual stocks
4. Contact support to increase rate limit for your tier

### High Latency

**Problem**: Messages arriving with >100ms delay

**Solutions**:
1. Enable compression on client
2. Check network latency: `ping api.screener.kr`
3. Verify server load: `GET /v1/ws/stats`
4. Consider using regional endpoint

### Session Restoration Failures

**Problem**: Cannot restore session after disconnect

**Solutions**:
1. Session may have expired (5-minute TTL)
2. Verify user ID matches original connection
3. Create new connection if session not found

## Support

For issues or questions:
- **Documentation**: https://docs.screener.kr
- **Email**: kcenon@gmail.com
- **GitHub Issues**: https://github.com/kcenon/screener_system/issues
