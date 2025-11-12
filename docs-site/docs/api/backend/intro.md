# Backend API Reference

The backend API is built with FastAPI and provides RESTful endpoints for all platform functionality.

## Base URL

```
http://localhost:8000/api/v1
```

## API Categories

### Authentication API
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh access token

### Stock Data API
- `GET /stocks` - List all stocks
- `GET /stocks/{code}` - Get stock details
- `GET /stocks/{code}/price` - Get current price
- `GET /stocks/{code}/history` - Get price history
- `GET /stocks/{code}/financials` - Get financial statements

### Screening API
- `POST /screen` - Screen stocks with filters
- `GET /screen/presets` - Get saved screen presets
- `POST /screen/presets` - Save screen preset
- `DELETE /screen/presets/{id}` - Delete screen preset

### Portfolio API
- `GET /portfolio` - Get user portfolio
- `POST /portfolio/holdings` - Add holding
- `PUT /portfolio/holdings/{id}` - Update holding
- `DELETE /portfolio/holdings/{id}` - Remove holding
- `GET /portfolio/performance` - Get performance metrics

### Alerts API
- `GET /alerts` - List user alerts
- `POST /alerts` - Create price alert
- `PUT /alerts/{id}` - Update alert
- `DELETE /alerts/{id}` - Delete alert

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## Example: Stock Screening

```python
import requests

# Screen for stocks with specific criteria
response = requests.post(
    'http://localhost:8000/api/v1/screen',
    headers={'Authorization': 'Bearer YOUR_TOKEN'},
    json={
        'filters': {
            'market': 'KOSPI',
            'per': {'min': 0, 'max': 20},
            'pbr': {'min': 0, 'max': 1.5},
            'roe': {'min': 10},
            'market_cap': {'min': 100000000000}  # 100B KRW
        },
        'sort': [
            {'field': 'roe', 'direction': 'desc'}
        ],
        'limit': 50
    }
)

stocks = response.json()['data']
for stock in stocks:
    print(f"{stock['code']}: {stock['name']} - ROE: {stock['roe']}%")
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK` - Request successful
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Next Steps

- [Authentication Details](/docs/api/backend/auth)
- [Stock Data Endpoints](/docs/api/backend/stocks)
- [Screening Guide](/docs/api/backend/screening)
- [Portfolio Management](/docs/api/backend/portfolio)
