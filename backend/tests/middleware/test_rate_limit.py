"""Tests for rate limiting middleware"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.cache import cache_manager
from app.core.config import settings
from app.middleware.rate_limit import (
    ENDPOINT_RATE_LIMITS,
    InMemoryRateLimiter,
    RateLimitMiddleware,
    _fallback_limiter,
)


@pytest.fixture
def app():
    """Create FastAPI test app with rate limiting"""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}

    @app.post("/v1/screen")
    async def screening_endpoint():
        return {"message": "screening success"}

    @app.get("/v1/stocks/005930")
    async def stock_detail_endpoint():
        return {"message": "stock detail success"}

    @app.post("/v1/auth/login")
    async def login_endpoint():
        return {"token": "fake_token"}

    @app.post("/v1/auth/refresh")
    async def refresh_endpoint():
        return {"token": "refreshed_token"}

    @app.get("/health")
    async def health_endpoint():
        return {"status": "ok"}

    return app


@pytest.fixture(autouse=False)
def mock_redis(monkeypatch):
    """Mock Redis for testing rate limiting without actual Redis connection"""
    # Create a simple in-memory counter for testing
    counters = {}

    class MockRedis:
        async def eval(self, script, numkeys, *keys_and_args):
            """Mock Redis eval for rate limiting Lua script"""
            key = keys_and_args[0]

            if key not in counters:
                counters[key] = {"count": 0, "created": True}

            counters[key]["count"] += 1
            return counters[key]["count"]

        async def flushdb(self):
            """Mock flushdb to clear counters"""
            counters.clear()

    mock_redis_instance = MockRedis()
    monkeypatch.setattr(cache_manager, "redis", mock_redis_instance)

    yield mock_redis_instance

    # Cleanup
    counters.clear()


class TestRateLimitMiddleware:
    """Test suite for rate limiting middleware"""

    def test_tier_rate_limiting_free(self, app: FastAPI, mock_redis, monkeypatch):
        """Test free tier rate limiting (100 req/hour)"""
        # Lower limit for testing
        monkeypatch.setattr(settings, "RATE_LIMIT_FREE", 10)

        client = TestClient(app)

        # Make requests up to limit
        for i in range(settings.RATE_LIMIT_FREE):
            response = client.get("/test")
            assert response.status_code == 200, f"Request {i+1} failed: {response.text}"

            # Check rate limit headers
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
            assert "X-RateLimit-Reset" in response.headers

        # Next request should be rate limited
        response = client.get("/test")
        assert (
            response.status_code == 429
        ), f"Expected 429 but got {response.status_code}: {response.text}"
        assert response.json()["success"] is False
        assert "rate limit exceeded" in response.json()["message"].lower()

        # Check 429 headers
        assert "X-RateLimit-Limit" in response.headers
        assert "Retry-After" in response.headers

    def test_endpoint_specific_rate_limiting(
        self, app: FastAPI, mock_redis, monkeypatch
    ):
        """Test endpoint-specific rate limits"""
        client = TestClient(app)

        # Patch the endpoint limits dictionary directly
        from app.middleware.rate_limit import ENDPOINT_RATE_LIMITS

        original_limit = ENDPOINT_RATE_LIMITS["/v1/screen"]
        ENDPOINT_RATE_LIMITS["/v1/screen"] = 5

        try:
            # Test screening endpoint (5 req/hour)
            for i in range(5):
                response = client.post("/v1/screen")
                assert response.status_code == 200, f"Request {i+1} failed"

            # Next request should be rate limited
            response = client.post("/v1/screen")
            assert (
                response.status_code == 429
            ), f"Expected 429 but got {response.status_code}"
            assert "endpoint rate limit exceeded" in response.json()["message"].lower()
            assert "X-RateLimit-Endpoint" in response.headers
        finally:
            # Restore original limit
            ENDPOINT_RATE_LIMITS["/v1/screen"] = original_limit

    def test_whitelist_paths_bypass_rate_limiting(self, app: FastAPI):
        """Test that whitelisted paths bypass rate limiting"""
        client = TestClient(app)

        # Health endpoint should not be rate limited
        for i in range(200):  # More than any tier limit
            response = client.get("/health")
            assert response.status_code == 200
            # Should not have rate limit headers
            assert "X-RateLimit-Limit" not in response.headers

    def test_rate_limit_headers_accuracy(self, app: FastAPI, mock_redis):
        """Test rate limit headers show accurate information"""
        client = TestClient(app)

        # First request
        response = client.get("/test")
        assert response.status_code == 200

        limit = int(response.headers["X-RateLimit-Limit"])
        remaining = int(response.headers["X-RateLimit-Remaining"])
        reset = int(response.headers["X-RateLimit-Reset"])

        assert (
            limit == settings.RATE_LIMIT_FREE
        ), f"Limit should be {settings.RATE_LIMIT_FREE} but got {limit}"
        assert (
            remaining == settings.RATE_LIMIT_FREE - 1
        ), f"Remaining should be {settings.RATE_LIMIT_FREE - 1} but got {remaining}"
        assert (
            reset == settings.RATE_LIMIT_WINDOW
        ), f"Reset should be {settings.RATE_LIMIT_WINDOW} but got {reset}"

    def test_different_endpoints_separate_limits(
        self, app: FastAPI, mock_redis, monkeypatch
    ):
        """Test that different endpoints have separate rate limits"""
        client = TestClient(app)

        # Patch the endpoint limits dictionary directly
        from app.middleware.rate_limit import ENDPOINT_RATE_LIMITS

        original_limit = ENDPOINT_RATE_LIMITS["/v1/screen"]
        ENDPOINT_RATE_LIMITS["/v1/screen"] = 5

        try:
            # Exhaust screening endpoint limit
            for i in range(5):
                response = client.post("/v1/screen")
                assert response.status_code == 200, f"Screening request {i+1} failed"

            # Screening should be rate limited
            response = client.post("/v1/screen")
            assert response.status_code == 429, "Expected screening to be rate limited"

            # But other endpoints should still work (subject to tier limit)
            response = client.get("/test")
            assert response.status_code == 200, "Other endpoints should still work"
        finally:
            # Restore original limit
            ENDPOINT_RATE_LIMITS["/v1/screen"] = original_limit

    def test_rate_limit_reset_after_window(self, app: FastAPI):
        """Test rate limit resets after time window (simplified)"""
        # Note: In real tests, we'd mock time or use Redis TTL manipulation
        # This is a placeholder for the concept
        pytest.skip("Requires time mocking or Redis TTL manipulation")

    def test_redis_unavailable_uses_fallback(self, app: FastAPI, monkeypatch):
        """Test in-memory fallback rate limiting when Redis is unavailable"""
        monkeypatch.setattr(cache_manager, "redis", None)
        monkeypatch.setattr(settings, "RATE_LIMIT_FREE", 5)
        _fallback_limiter.reset()

        import app.middleware.rate_limit as rl_module

        monkeypatch.setattr(rl_module, "_fallback_logged", False)

        client = TestClient(app)

        # Requests within limit should succeed
        for i in range(5):
            response = client.get("/test")
            assert response.status_code == 200, f"Request {i+1} should succeed"
            assert "X-RateLimit-Limit" in response.headers

        # Request exceeding limit should be blocked
        response = client.get("/test")
        assert response.status_code == 429, "Should be rate limited by fallback"
        assert "rate limit exceeded" in response.json()["message"].lower()

    def test_multiple_clients_separate_limits(self, app: FastAPI):
        """Test that different clients (IPs) have separate rate limits"""
        # Note: TestClient doesn't easily support different IPs
        # In integration tests, we'd use actual HTTP requests with different IPs
        pytest.skip("Requires integration test with actual HTTP requests")

    def test_authenticated_user_tier_limits(self, app: FastAPI):
        """Test tier-based limits for authenticated users"""
        # Note: Requires auth middleware to be set up
        # This would test basic/pro tier limits
        pytest.skip("Requires auth middleware integration")


class TestEndpointRateLimitConfiguration:
    """Test endpoint rate limit configuration"""

    def test_endpoint_limits_defined(self):
        """Test that endpoint limits are properly defined"""
        assert "/v1/screen" in ENDPOINT_RATE_LIMITS
        assert "/v1/stocks/" in ENDPOINT_RATE_LIMITS
        assert "/v1/auth/register" in ENDPOINT_RATE_LIMITS
        assert "/v1/auth/login" in ENDPOINT_RATE_LIMITS
        assert "/v1/auth/refresh" in ENDPOINT_RATE_LIMITS

    def test_endpoint_limits_reasonable(self):
        """Test that endpoint limits are within reasonable ranges"""
        # Skip if running in dev mode with high limits
        if settings.RATE_LIMIT_FREE > 10000:
            pytest.skip(
                "Skipping reasonable limit check in dev environment with high limits"
            )

        from app.middleware.rate_limit import ENDPOINT_RATE_LIMITS

        for endpoint, limit in ENDPOINT_RATE_LIMITS.items():
            assert limit > 0, f"Limit for {endpoint} must be positive"
            assert limit <= 10000, f"Limit for {endpoint} seems too high"


@pytest.mark.asyncio
class TestRateLimitMiddlewareAsync:
    """Async tests for rate limiting"""

    async def test_concurrent_requests_within_limit(self, app: FastAPI, mock_redis):
        """Test handling of concurrent requests within rate limit"""
        import asyncio

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Make 10 concurrent requests
            tasks = [client.get("/test") for _ in range(10)]
            responses = await asyncio.gather(*tasks)

            # All should succeed if limit > 10
            for response in responses:
                assert response.status_code == 200

    async def test_concurrent_requests_exceed_limit(
        self, app: FastAPI, mock_redis, monkeypatch
    ):
        """Test that concurrent requests properly enforce rate limits"""
        import asyncio

        from httpx import ASGITransport, AsyncClient

        # Lower the limit for testing to avoid high concurrency issues
        monkeypatch.setattr(settings, "RATE_LIMIT_FREE", 10)
        request_count = 20

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Make concurrent requests (more than limit)
            tasks = [client.get("/test") for _ in range(request_count)]
            responses = await asyncio.gather(*tasks)

            # Some should be rate limited
            status_codes = [r.status_code for r in responses]
            assert 429 in status_codes, (
                f"Expected some requests to be rate limited. Got: "
                f"{status_codes.count(200)} success, "
                f"{status_codes.count(429)} rate limited"
            )
            assert 200 in status_codes, "Expected some requests to succeed"


@pytest.mark.integration
class TestRateLimitIntegration:
    """Integration tests for rate limiting"""

    def test_rate_limit_with_real_redis(self, app: FastAPI):
        """Test rate limiting with real Redis connection"""
        # This test requires Redis to be running
        if not cache_manager.redis:
            pytest.skip("Redis not available")

        client = TestClient(app)

        # Test basic rate limiting
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers

    def test_rate_limit_persistence_across_requests(self, app: FastAPI):
        """Test that rate limit counter persists across requests"""
        if not cache_manager.redis:
            pytest.skip("Redis not available")

        client = TestClient(app)

        # First request
        response1 = client.get("/test")
        remaining1 = int(response1.headers["X-RateLimit-Remaining"])

        # Second request
        response2 = client.get("/test")
        remaining2 = int(response2.headers["X-RateLimit-Remaining"])

        # Remaining should decrease
        assert remaining2 == remaining1 - 1


class TestInMemoryRateLimiter:
    """Test suite for InMemoryRateLimiter class"""

    def test_increment_counts_requests(self):
        """Test basic increment counting within a window"""
        limiter = InMemoryRateLimiter()
        assert limiter.increment("key1", window=60) == 1
        assert limiter.increment("key1", window=60) == 2
        assert limiter.increment("key1", window=60) == 3

    def test_separate_keys_have_separate_counts(self):
        """Test that different keys are tracked independently"""
        limiter = InMemoryRateLimiter()
        assert limiter.increment("user:A", window=60) == 1
        assert limiter.increment("user:B", window=60) == 1
        assert limiter.increment("user:A", window=60) == 2
        assert limiter.increment("user:B", window=60) == 2

    def test_expired_entries_are_excluded(self, monkeypatch):
        """Test that timestamps outside the window are excluded"""
        import time as time_module

        limiter = InMemoryRateLimiter()

        # Mock monotonic to control time
        current_time = 1000.0

        def mock_monotonic():
            return current_time

        monkeypatch.setattr(time_module, "monotonic", mock_monotonic)

        # Add requests at t=1000
        assert limiter.increment("key1", window=10) == 1
        assert limiter.increment("key1", window=10) == 2

        # Advance time past the window
        current_time = 1011.0
        assert limiter.increment("key1", window=10) == 1  # Old entries expired

    def test_reset_clears_all_counters(self):
        """Test that reset() clears all state"""
        limiter = InMemoryRateLimiter()
        limiter.increment("key1", window=60)
        limiter.increment("key2", window=60)
        limiter.reset()
        assert limiter.increment("key1", window=60) == 1
        assert limiter.increment("key2", window=60) == 1

    def test_cleanup_removes_stale_keys(self, monkeypatch):
        """Test periodic cleanup removes keys with no recent activity"""
        import time as time_module

        current_time = 1000.0

        def mock_monotonic():
            return current_time

        monkeypatch.setattr(time_module, "monotonic", mock_monotonic)

        limiter = InMemoryRateLimiter(cleanup_interval=10)

        # Add entry at t=1000
        limiter.increment("key1", window=5)

        # Advance past cleanup_interval (>10s after key1's last timestamp)
        current_time = 1011.0
        # Next increment triggers cleanup; key1 is stale (1000 < 1011-10=1001)
        limiter.increment("key2", window=60)

        assert "key1" not in limiter._counters
        assert "key2" in limiter._counters


class TestFallbackRateLimitingBehavior:
    """Test fallback behavior when Redis is unavailable"""

    def test_auth_refresh_endpoint_rate_limited(
        self, app: FastAPI, mock_redis, monkeypatch
    ):
        """Test /v1/auth/refresh endpoint has rate limiting"""
        from app.middleware.rate_limit import ENDPOINT_RATE_LIMITS

        original_limit = ENDPOINT_RATE_LIMITS["/v1/auth/refresh"]
        ENDPOINT_RATE_LIMITS["/v1/auth/refresh"] = 3

        try:
            client = TestClient(app)
            for i in range(3):
                response = client.post("/v1/auth/refresh")
                assert response.status_code == 200, f"Request {i+1} failed"

            response = client.post("/v1/auth/refresh")
            assert response.status_code == 429
            assert "endpoint rate limit exceeded" in response.json()["message"].lower()
        finally:
            ENDPOINT_RATE_LIMITS["/v1/auth/refresh"] = original_limit

    def test_fallback_enforces_endpoint_limits(self, app: FastAPI, monkeypatch):
        """Test that fallback also enforces endpoint-specific limits"""
        monkeypatch.setattr(cache_manager, "redis", None)
        _fallback_limiter.reset()

        import app.middleware.rate_limit as rl_module

        monkeypatch.setattr(rl_module, "_fallback_logged", False)

        from app.middleware.rate_limit import ENDPOINT_RATE_LIMITS

        original_limit = ENDPOINT_RATE_LIMITS["/v1/screen"]
        ENDPOINT_RATE_LIMITS["/v1/screen"] = 3

        try:
            client = TestClient(app)
            for i in range(3):
                response = client.post("/v1/screen")
                assert response.status_code == 200, f"Request {i+1} failed"

            response = client.post("/v1/screen")
            assert response.status_code == 429
        finally:
            ENDPOINT_RATE_LIMITS["/v1/screen"] = original_limit

    def test_fallback_log_deduplication(self, app: FastAPI, monkeypatch, caplog):
        """Test that fallback activation is logged only once"""
        import logging

        monkeypatch.setattr(cache_manager, "redis", None)
        monkeypatch.setattr(settings, "RATE_LIMIT_FREE", 100)
        _fallback_limiter.reset()

        import app.middleware.rate_limit as rl_module

        monkeypatch.setattr(rl_module, "_fallback_logged", False)

        client = TestClient(app)

        with caplog.at_level(logging.WARNING):
            # Multiple requests should only log fallback message once
            for _ in range(5):
                client.get("/test")

        fallback_messages = [
            r for r in caplog.records if "in-memory rate limiting fallback" in r.message
        ]
        assert (
            len(fallback_messages) == 1
        ), f"Expected 1 fallback log, got {len(fallback_messages)}"
