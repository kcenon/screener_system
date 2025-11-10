# API Rate Limiting

## Overview

The Stock Screening Platform API implements rate limiting to ensure fair usage, system stability, and protection against abuse. Rate limits are tiered based on your account level and vary by endpoint complexity.

## Rate Limit Architecture

### Two-Level Rate Limiting

Our API uses a two-level rate limiting system:

1. **Tier-based limits**: Apply to all API endpoints combined
2. **Endpoint-specific limits**: Apply to specific expensive endpoints (e.g., screening queries)

Both limits are enforced independently. A request must pass both checks to succeed.

### Time Window

- **Window Size**: 1 hour (3600 seconds)
- **Reset**: Limits reset on a rolling window basis
- **Tracking**: Per-user (authenticated) or per-IP (anonymous)

## Rate Limits by Tier

| Tier | Requests/Hour | Requests/Day | Use Case | Monthly Cost |
|------|---------------|--------------|----------|--------------|
| **Free** | 100 | 2,400 | Personal use, testing, evaluation | Free |
| **Basic** | 1,000 | 24,000 | Small applications, hobby projects | $29 |
| **Pro** | 10,000 | 240,000 | Production applications | $99 |
| **Enterprise** | Custom | Custom | High-volume applications | Contact sales |

## Endpoint-Specific Limits

Some endpoints have additional rate limits due to their computational complexity:

| Endpoint | Limit (req/hour) | Reason | Tier Applies? |
|----------|------------------|--------|---------------|
| `POST /v1/screen` | 50 | Complex database queries with 200+ indicators | Yes |
| `GET /v1/stocks/{code}` | 200 | Detailed stock data with indicators | Yes |
| `POST /v1/auth/register` | 10 | Prevent account spam | Yes |
| `POST /v1/auth/login` | 10 | Prevent brute force attacks | Yes |
| `GET /v1/screen/templates` | No limit | Cached responses | No |
| `GET /health/*` | No limit | Health check endpoints | No |

**Note**: Endpoint-specific limits are **in addition** to tier-based limits. For example, a Free tier user making screening requests is limited to:
- 50 requests/hour to `/v1/screen` (endpoint limit)
- 100 requests/hour total across all endpoints (tier limit)

## Rate Limit Headers

Every API response includes rate limit information in the headers:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 3600
X-RateLimit-Endpoint: /v1/screen

{
  "stocks": [...],
  "meta": {...}
}
```

### Header Reference

| Header | Type | Description | Example |
|--------|------|-------------|---------|
| `X-RateLimit-Limit` | integer | Maximum requests allowed per hour | `50` |
| `X-RateLimit-Remaining` | integer | Requests remaining in current window | `45` |
| `X-RateLimit-Reset` | integer | Seconds until limit resets (always 3600) | `3600` |
| `X-RateLimit-Endpoint` | string | Current endpoint path (endpoint limits only) | `/v1/screen` |
| `Retry-After` | integer | Seconds to wait before retrying (429 only) | `3600` |

## Rate Limit Exceeded (429 Response)

When you exceed a rate limit, you'll receive a `429 Too Many Requests` response:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 3600
X-RateLimit-Endpoint: /v1/screen
Retry-After: 3600

{
  "success": false,
  "message": "Endpoint rate limit exceeded",
  "detail": "Maximum 50 requests per hour allowed for /v1/screen"
}
```

### Recommended Response Handling

```python
import requests
import time

def make_api_request(url, data):
    response = requests.post(url, json=data)

    # Check rate limit status
    remaining = int(response.headers.get("X-RateLimit-Remaining", 100))

    if response.status_code == 429:
        # Rate limit exceeded
        retry_after = int(response.headers.get("Retry-After", 3600))
        print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
        time.sleep(retry_after)
        return make_api_request(url, data)  # Retry

    elif remaining < 10:
        # Approaching limit, slow down
        print(f"Warning: Only {remaining} requests remaining")
        time.sleep(2)  # Add delay between requests

    return response.json()
```

## Best Practices

### 1. Monitor Rate Limit Headers

Always check `X-RateLimit-Remaining` to avoid hitting limits:

```python
import requests

response = requests.post("/v1/screen", json=filters)

# Check remaining quota
remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
limit = int(response.headers.get("X-RateLimit-Limit", 0))

print(f"Used {limit - remaining}/{limit} requests")

if remaining < 10:
    print("Warning: Approaching rate limit!")
```

### 2. Leverage Caching

Screening results are cached for 5 minutes. Identical requests return cached results instantly:

```python
# First request - Cache MISS (200-500ms)
response1 = requests.post("/v1/screen", json=filters)

# Second request within 5 minutes - Cache HIT (<50ms)
# Does NOT count against rate limit!
response2 = requests.post("/v1/screen", json=filters)
```

**Caching Tips**:
- Reuse filter combinations when possible
- Avoid randomized parameters (timestamps, UUIDs) in filters
- Use consistent sorting and pagination

### 3. Batch Requests Efficiently

Instead of making multiple separate requests:

```python
# ❌ BAD: 100 separate requests (hits rate limit fast)
for sector in all_sectors:
    stocks = screen_stocks({"sector": sector})
    process(stocks)
```

Use a single request and filter client-side:

```python
# ✅ GOOD: 1 request, client-side filtering
all_stocks = screen_stocks({})  # Get all stocks
for sector in all_sectors:
    sector_stocks = [s for s in all_stocks if s["sector"] == sector]
    process(sector_stocks)
```

### 4. Use Predefined Templates

Predefined templates are optimized and cached more aggressively:

```python
# More efficient than custom filters
response = requests.post("/v1/screen/templates/dividend_stocks")

# vs custom filters (same result, but slower)
response = requests.post("/v1/screen", json={
    "filters": {"dividend_yield": {"min": 3.0}, "quality_score": {"min": 70}}
})
```

### 5. Implement Exponential Backoff

For resilient applications, use exponential backoff on 429 responses:

```python
import time
import random

def api_call_with_backoff(url, data, max_retries=5):
    for attempt in range(max_retries):
        response = requests.post(url, json=data)

        if response.status_code != 429:
            return response.json()

        # Exponential backoff: 1s, 2s, 4s, 8s, 16s
        wait_time = (2 ** attempt) + random.uniform(0, 1)
        print(f"Rate limited. Waiting {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})")
        time.sleep(wait_time)

    raise Exception("Max retries exceeded")
```

### 6. Distribute Load Over Time

Instead of bursting all requests at once:

```python
import time

# ❌ BAD: Burst 50 requests immediately
for i in range(50):
    screen_stocks(filters[i])

# ✅ GOOD: Distribute over time
for i in range(50):
    screen_stocks(filters[i])
    time.sleep(1)  # 1 request per second = 3600/hour (within Free tier)
```

## Rate Limiting Implementation

### Technical Details

- **Storage**: Redis with atomic operations (Lua script)
- **Algorithm**: Token bucket with fixed window
- **Granularity**: Per-user (authenticated) or per-IP (anonymous)
- **Precision**: Millisecond-level tracking
- **Failure Mode**: Graceful degradation (allows requests if Redis is down)

### Lua Script (Atomic Increment + Expire)

```lua
-- Atomically increment counter and set expiration
local current = redis.call('incr', KEYS[1])
if current == 1 then
    redis.call('expire', KEYS[1], ARGV[1])
end
return current
```

This prevents race conditions where:
1. Request A increments counter
2. Request B increments counter
3. Request A sets expiration
4. Request B overwrites expiration
5. Counter persists forever without expiration ❌

## Upgrading Your Tier

### When to Upgrade

Consider upgrading if you:
- Consistently hit rate limits
- Need higher request volumes for production applications
- Require faster screening queries
- Want priority support

### How to Upgrade

1. Visit [Pricing Page](https://screener.example.com/pricing)
2. Select **Basic** ($29/month) or **Pro** ($99/month)
3. Complete payment
4. Tier upgrade is instant (no code changes needed)

### Enterprise Plan

For custom requirements:
- Volume > 10,000 requests/hour
- White-label deployment
- Dedicated infrastructure
- Custom SLA guarantees
- Priority feature requests

Contact: enterprise@screener.example.com

## Frequently Asked Questions

### Q: Do cached requests count against rate limits?

**A**: No. Cache hits are served directly from Redis without executing database queries, and do not count against any rate limit.

### Q: What happens if I exceed both tier and endpoint limits?

**A**: You'll receive the first limit you hit. For example:
- If you make 51 screening requests (exceeding endpoint limit of 50), you'll get a 429 for endpoint limit
- If you make 101 total requests (exceeding tier limit of 100), you'll get a 429 for tier limit

### Q: Can I purchase additional requests?

**A**: Not currently. Rate limits are fixed per tier. Consider upgrading to a higher tier or contact enterprise sales for custom plans.

### Q: Do health check endpoints count against limits?

**A**: No. The following endpoints are whitelisted:
- `/health`
- `/health/db`
- `/health/redis`
- `/docs`
- `/redoc`
- `/openapi.json`

### Q: How do I know which limit I exceeded?

**A**: Check the `detail` field in the 429 response:
```json
{
  "detail": "Maximum 50 requests per hour allowed for /v1/screen"  // Endpoint limit
}
```
or
```json
{
  "detail": "Maximum 100 requests per hour allowed for free tier"  // Tier limit
}
```

### Q: Can I get a temporary rate limit increase for testing?

**A**: Yes. Contact support@screener.example.com with:
- Your use case
- Required request volume
- Testing duration
- Expected production tier

We can temporarily increase limits for legitimate testing purposes.

## Support

### Rate Limit Questions

- **Email**: api-support@screener.example.com
- **Docs**: https://docs.screener.example.com/rate-limiting
- **Status**: https://status.screener.example.com

### Reporting Issues

If you believe you're being rate limited incorrectly:

1. Capture the full HTTP request and response (including headers)
2. Note the timestamp and endpoint
3. Email api-support@screener.example.com with details

We'll investigate within 24 hours.

---

**Last Updated**: 2025-11-11
**API Version**: v1
**Rate Limiting Version**: 2.0 (Redis-based with atomic operations)
