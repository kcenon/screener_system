# API Reference

The Stock Screening Platform provides comprehensive REST and WebSocket APIs for accessing stock market data and platform features.

## API Categories

### Backend API (Python/FastAPI)

The backend provides RESTful APIs for:
- User authentication and authorization
- Stock data retrieval and screening
- Portfolio management
- Financial analysis
- Market data aggregation

[Backend API Documentation →](/docs/api/backend/intro)

### Frontend Components (TypeScript/React)

Reusable React components for:
- Stock screening tables
- Chart visualizations
- Portfolio displays
- Alert management
- Financial metrics

[Frontend Components →](/docs/api/frontend/intro)

## Authentication

All API endpoints require authentication using JWT tokens.

### Getting an Access Token

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using the Token

Include the token in the Authorization header:

```bash
GET /api/v1/stocks
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Rate Limiting

API requests are rate-limited to ensure fair usage:
- **Authenticated users**: 1000 requests/hour
- **Unauthenticated users**: 100 requests/hour

## WebSocket API

Real-time market data is available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/market');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Market update:', data);
};
```

## Response Format

All API responses follow a consistent format:

**Success Response:**
```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "timestamp": "2025-11-12T13:45:00Z",
    "request_id": "uuid"
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Description of the error",
    "details": { ... }
  },
  "meta": {
    "timestamp": "2025-11-12T13:45:00Z",
    "request_id": "uuid"
  }
}
```

## API Versioning

The API is versioned using URL path versioning:
- Current version: `/api/v1/`
- Legacy version: Not applicable (first version)

## Next Steps

- [Backend API Reference](/docs/api/backend/intro)
- [Frontend Components](/docs/api/frontend/intro)
- [WebSocket Events](/docs/api/websocket)
