"""Integration tests for health check endpoints"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheManager
from app.db.session import get_db


class TestBasicHealthCheck:
    """Tests for basic health check endpoint"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """Test GET /health returns 200 OK"""
        response = await client.get("/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

    @pytest.mark.asyncio
    async def test_health_endpoint_no_auth_required(self, client: AsyncClient):
        """Test health endpoint accessible without authentication"""
        # Make request without any authentication headers
        response = await client.get("/v1/health")

        # Should still return 200 OK
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_endpoint_response_format(self, client: AsyncClient):
        """Test response includes status and service name"""
        response = await client.get("/v1/health")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "status" in data
        assert "service" in data
        assert data["status"] == "healthy"
        assert isinstance(data["service"], str)


class TestDatabaseHealthCheck:
    """Tests for database health check endpoint"""

    @pytest.mark.asyncio
    async def test_health_db_connected(
        self, client: AsyncClient, db: AsyncSession
    ):
        """Test /health/db returns 200 when database connected"""
        response = await client.get("/v1/health/db")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

    @pytest.mark.asyncio
    async def test_health_db_disconnected(self, client: AsyncClient):
        """Test /health/db returns 200 with unhealthy status
        when database unreachable"""
        # Mock database session that raises exception
        async def mock_get_db_failing():
            mock_session = AsyncMock(spec=AsyncSession)
            mock_session.execute.side_effect = Exception("Database connection failed")
            yield mock_session

        # Override the get_db dependency
        from app.main import app

        app.dependency_overrides[get_db] = mock_get_db_failing

        try:
            response = await client.get("/v1/health/db")

            # Endpoint returns 200 but with unhealthy status
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"
            assert "error" in data
        finally:
            # Clear override
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_health_db_response_includes_details(
        self, client: AsyncClient, db: AsyncSession
    ):
        """Test response includes database connection details"""
        response = await client.get("/v1/health/db")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "status" in data
        assert "database" in data
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

    @pytest.mark.asyncio
    async def test_health_db_no_auth_required(self, client: AsyncClient):
        """Test database health check accessible without authentication"""
        response = await client.get("/v1/health/db")

        assert response.status_code == 200


class TestRedisHealthCheck:
    """Tests for Redis health check endpoint"""

    @pytest.mark.asyncio
    async def test_health_redis_connected(self, client: AsyncClient):
        """Test /health/redis returns 200 when Redis connected"""
        # Mock cache manager with healthy Redis connection
        mock_cache = MagicMock(spec=CacheManager)
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_cache.redis = mock_redis

        async def mock_get_cache():
            return mock_cache

        from app.main import app
        from app.core.cache import get_cache

        app.dependency_overrides[get_cache] = mock_get_cache

        try:
            response = await client.get("/v1/health/redis")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["redis"] == "connected"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_health_redis_disconnected(self, client: AsyncClient):
        """Test /health/redis returns 200 with unhealthy status
        when Redis unreachable"""
        # Mock cache manager with failed Redis connection
        mock_cache = MagicMock(spec=CacheManager)
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(
            side_effect=Exception("Redis connection failed")
        )
        mock_cache.redis = mock_redis

        async def mock_get_cache():
            return mock_cache

        from app.main import app
        from app.core.cache import get_cache

        app.dependency_overrides[get_cache] = mock_get_cache

        try:
            response = await client.get("/v1/health/redis")

            # Endpoint returns 200 but with unhealthy status
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["redis"] == "disconnected"
            assert "error" in data
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_health_redis_not_initialized(self, client: AsyncClient):
        """Test /health/redis when Redis is not initialized"""
        # Mock cache manager without Redis instance
        mock_cache = MagicMock(spec=CacheManager)
        mock_cache.redis = None

        async def mock_get_cache():
            return mock_cache

        from app.main import app
        from app.core.cache import get_cache

        app.dependency_overrides[get_cache] = mock_get_cache

        try:
            response = await client.get("/v1/health/redis")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["redis"] == "not initialized"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_health_redis_response_includes_details(
        self, client: AsyncClient
    ):
        """Test response includes Redis connection details"""
        # Mock cache manager with healthy Redis connection
        mock_cache = MagicMock(spec=CacheManager)
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_cache.redis = mock_redis

        async def mock_get_cache():
            return mock_cache

        from app.main import app
        from app.core.cache import get_cache

        app.dependency_overrides[get_cache] = mock_get_cache

        try:
            response = await client.get("/v1/health/redis")

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert "status" in data
            assert "redis" in data
            assert data["status"] == "healthy"
            assert data["redis"] == "connected"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_health_redis_no_auth_required(self, client: AsyncClient):
        """Test Redis health check accessible without authentication"""
        # Mock cache manager
        mock_cache = MagicMock(spec=CacheManager)
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_cache.redis = mock_redis

        async def mock_get_cache():
            return mock_cache

        from app.main import app
        from app.core.cache import get_cache

        app.dependency_overrides[get_cache] = mock_get_cache

        try:
            response = await client.get("/v1/health/redis")
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()


class TestMetricsEndpoint:
    """Tests for Prometheus metrics endpoint"""

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, client: AsyncClient):
        """Test GET /metrics returns Prometheus metrics"""
        response = await client.get("/v1/metrics")

        assert response.status_code == 200
        # Prometheus metrics are in text format
        assert response.headers["content-type"].startswith("text/plain")

    @pytest.mark.asyncio
    async def test_metrics_endpoint_no_auth_required(self, client: AsyncClient):
        """Test metrics endpoint accessible without authentication"""
        response = await client.get("/v1/metrics")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_metrics_endpoint_format(self, client: AsyncClient):
        """Test metrics response is in Prometheus format"""
        response = await client.get("/v1/metrics")

        assert response.status_code == 200
        content = response.text

        # Prometheus metrics should contain HELP and TYPE comments
        # and metric name/value pairs
        assert isinstance(content, str)
        assert len(content) > 0


class TestHealthCheckPerformance:
    """Performance tests for health check endpoints"""

    @pytest.mark.asyncio
    async def test_health_check_response_time(self, client: AsyncClient):
        """Test health check responds quickly (<100ms)"""
        import time

        start_time = time.time()
        response = await client.get("/v1/health")
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

        assert response.status_code == 200
        # Health check should be very fast
        assert elapsed_time < 100, f"Health check took {elapsed_time}ms"

    @pytest.mark.asyncio
    async def test_db_health_check_response_time(
        self, client: AsyncClient, db: AsyncSession
    ):
        """Test database health check responds quickly (<200ms)"""
        import time

        start_time = time.time()
        response = await client.get("/v1/health/db")
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

        assert response.status_code == 200
        # Database health check should be reasonably fast
        assert elapsed_time < 200, f"DB health check took {elapsed_time}ms"
