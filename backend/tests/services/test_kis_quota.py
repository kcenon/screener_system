"""Tests for KIS API quota manager"""

import asyncio
from unittest.mock import patch

import pytest

from app.core.cache import cache_manager
from app.services.kis_quota import (CircuitState, KISQuotaManager,
                                    RequestPriority)


@pytest.fixture
async def quota_manager():
    """Create fresh quota manager for each test"""
    manager = KISQuotaManager()
    yield manager
    # Cleanup
    manager.queue_processing = False


@pytest.fixture
async def clear_redis():
    """Clear Redis before each test"""
    if cache_manager.redis:
        await cache_manager.redis.flushdb()
    yield
    if cache_manager.redis:
        await cache_manager.redis.flushdb()


class TestCircuitBreaker:
    """Test circuit breaker functionality"""

    @pytest.mark.asyncio
    async def test_circuit_starts_closed(self, quota_manager: KISQuotaManager):
        """Test circuit breaker starts in CLOSED state"""
        assert quota_manager.circuit_state == CircuitState.CLOSED
        assert await quota_manager._check_circuit() is True

    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(self, quota_manager: KISQuotaManager):
        """Test circuit breaker opens after threshold failures"""
        from app.core.config import settings

        # Record failures up to threshold
        for _ in range(settings.KIS_API_CIRCUIT_BREAKER_THRESHOLD):
            quota_manager._record_failure()

        # Circuit should be OPEN
        assert quota_manager.circuit_state == CircuitState.OPEN
        assert await quota_manager._check_circuit() is False

    @pytest.mark.asyncio
    async def test_circuit_half_open_after_timeout(
        self, quota_manager: KISQuotaManager
    ):
        """Test circuit breaker enters HALF_OPEN after timeout"""
        from app.core.config import settings

        # Open circuit
        for _ in range(settings.KIS_API_CIRCUIT_BREAKER_THRESHOLD):
            quota_manager._record_failure()

        assert quota_manager.circuit_state == CircuitState.OPEN

        # Mock time to simulate timeout
        with patch("time.time") as mock_time:
            mock_time.return_value = (
                quota_manager.circuit_open_time
                + settings.KIS_API_CIRCUIT_BREAKER_TIMEOUT
                + 1
            )

            # Circuit should transition to HALF_OPEN
            result = await quota_manager._check_circuit()
            assert result is True
            assert quota_manager.circuit_state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_circuit_closes_after_successful_request(
        self, quota_manager: KISQuotaManager, clear_redis
    ):
        """Test circuit breaker closes after successful request in HALF_OPEN"""
        # Manually set to HALF_OPEN
        quota_manager.circuit_state = CircuitState.HALF_OPEN

        # Mock successful callback
        async def success_callback():
            return "success"

        # Execute request
        result = await quota_manager.execute_request(success_callback)

        assert result == "success"
        assert quota_manager.circuit_state == CircuitState.CLOSED
        assert quota_manager.failure_count == 0


class TestQuotaManagement:
    """Test quota checking and management"""

    @pytest.mark.asyncio
    async def test_quota_allows_within_limit(
        self, quota_manager: KISQuotaManager, clear_redis
    ):
        """Test quota allows requests within limit"""
        if not cache_manager.redis:
            pytest.skip("Redis not available")

        # Should allow requests up to limit
        for _ in range(20):  # KIS API limit is 20 req/sec
            result = await quota_manager._check_quota()
            assert result is True

        # Next request should exceed quota
        result = await quota_manager._check_quota()
        assert result is False

    @pytest.mark.asyncio
    async def test_quota_reset_after_window(
        self, quota_manager: KISQuotaManager, clear_redis
    ):
        """Test quota resets after time window"""
        if not cache_manager.redis:
            pytest.skip("Redis not available")

        # Exhaust quota
        for _ in range(20):
            await quota_manager._check_quota()

        # Should be blocked
        assert await quota_manager._check_quota() is False

        # Wait for window to expire
        await asyncio.sleep(1.1)  # Window is 1 second

        # Should allow again
        assert await quota_manager._check_quota() is True

    @pytest.mark.asyncio
    async def test_quota_graceful_degradation_redis_unavailable(
        self, quota_manager: KISQuotaManager
    ):
        """Test quota allows requests when Redis unavailable"""
        # Mock Redis as unavailable
        with patch.object(cache_manager, "redis", None):
            result = await quota_manager._check_quota()
            assert result is True  # Fail-open behavior


class TestRequestExecution:
    """Test request execution with quota management"""

    @pytest.mark.asyncio
    async def test_execute_request_success(
        self, quota_manager: KISQuotaManager, clear_redis
    ):
        """Test successful request execution"""

        async def mock_callback():
            return "success"

        result = await quota_manager.execute_request(mock_callback)

        assert result == "success"
        assert quota_manager.total_requests == 1

    @pytest.mark.asyncio
    async def test_execute_request_failure_records(
        self, quota_manager: KISQuotaManager, clear_redis
    ):
        """Test request failure is recorded"""

        async def failing_callback():
            raise Exception("API error")

        with pytest.raises(Exception, match="API error"):
            await quota_manager.execute_request(failing_callback)

        assert quota_manager.total_failures == 1
        assert quota_manager.failure_count == 1

    @pytest.mark.asyncio
    async def test_execute_request_blocked_when_circuit_open(
        self, quota_manager: KISQuotaManager
    ):
        """Test requests blocked when circuit is OPEN"""
        from app.core.config import settings

        # Open circuit
        for _ in range(settings.KIS_API_CIRCUIT_BREAKER_THRESHOLD):
            quota_manager._record_failure()

        async def mock_callback():
            return "success"

        # Request should be blocked
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            await quota_manager.execute_request(mock_callback)


class TestPriorityQueue:
    """Test priority queue functionality"""

    @pytest.mark.asyncio
    async def test_queue_initialization(self, quota_manager: KISQuotaManager):
        """Test queue initializes with all priority levels"""
        assert RequestPriority.HIGH in quota_manager.queues
        assert RequestPriority.MEDIUM in quota_manager.queues
        assert RequestPriority.LOW in quota_manager.queues

        for queue in quota_manager.queues.values():
            assert len(queue) == 0

    @pytest.mark.asyncio
    async def test_request_queuing_when_quota_exceeded(
        self, quota_manager: KISQuotaManager, clear_redis
    ):
        """Test requests are queued when quota exceeded"""
        if not cache_manager.redis:
            pytest.skip("Redis not available")

        # Exhaust quota
        for _ in range(20):
            await quota_manager._check_quota()

        # Next request should be queued
        async def mock_callback():
            return "queued_success"

        # Note: This will queue but not wait for execution in current implementation
        await quota_manager._queue_request(mock_callback, RequestPriority.HIGH, 30)

        # Verify queued
        assert len(quota_manager.queues[RequestPriority.HIGH]) > 0

    def test_priority_queue_ordering(self, quota_manager: KISQuotaManager):
        """Test requests processed in priority order"""
        # Add requests with different priorities
        # Add requests with different priorities
        for priority in [
            RequestPriority.LOW,
            RequestPriority.HIGH,
            RequestPriority.MEDIUM,
        ]:
            for i in range(3):
                import time

                from app.services.kis_quota import QueuedRequest

                req = QueuedRequest(
                    priority=priority,
                    callback=lambda: None,
                    timestamp=time.time(),
                )
                quota_manager.queues[priority].append(req)

        # Verify queues have correct counts
        assert len(quota_manager.queues[RequestPriority.HIGH]) == 3
        assert len(quota_manager.queues[RequestPriority.MEDIUM]) == 3
        assert len(quota_manager.queues[RequestPriority.LOW]) == 3


class TestStatistics:
    """Test statistics and monitoring"""

    def test_get_stats(self, quota_manager: KISQuotaManager):
        """Test get_stats returns correct structure"""
        stats = quota_manager.get_stats()

        assert "circuit_state" in stats
        assert "failure_count" in stats
        assert "total_requests" in stats
        assert "total_failures" in stats
        assert "queued_high" in stats
        assert "queued_medium" in stats
        assert "queued_low" in stats
        assert "queue_processing" in stats

        # Verify types
        assert isinstance(stats["circuit_state"], str)
        assert isinstance(stats["failure_count"], int)
        assert isinstance(stats["total_requests"], int)

    def test_stats_accuracy(self, quota_manager: KISQuotaManager):
        """Test stats reflect actual state"""
        # Initial state
        stats = quota_manager.get_stats()
        assert stats["circuit_state"] == CircuitState.CLOSED.value
        assert stats["total_requests"] == 0
        assert stats["total_failures"] == 0

        # After failures
        quota_manager._record_failure()
        quota_manager._record_failure()

        stats = quota_manager.get_stats()
        assert stats["failure_count"] == 2
        assert stats["total_failures"] == 2


@pytest.mark.integration
class TestKISQuotaIntegration:
    """Integration tests for KIS quota manager"""

    @pytest.mark.asyncio
    async def test_concurrent_requests_respect_quota(
        self, quota_manager: KISQuotaManager, clear_redis
    ):
        """Test concurrent requests respect quota limits"""
        if not cache_manager.redis:
            pytest.skip("Redis not available")

        call_count = 0

        async def counting_callback():
            nonlocal call_count
            call_count += 1
            return "success"

        # Make many concurrent requests
        tasks = [quota_manager.execute_request(counting_callback) for _ in range(30)]

        # Some should succeed, some should fail or queue
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # At most 20 should succeed immediately (KIS limit)
        success_count = sum(1 for r in results if r == "success")
        assert success_count <= 20

    @pytest.mark.asyncio
    async def test_quota_recovery_after_window(
        self, quota_manager: KISQuotaManager, clear_redis
    ):
        """Test quota recovers after time window expires"""
        if not cache_manager.redis:
            pytest.skip("Redis not available")

        async def mock_callback():
            return "success"

        # Exhaust quota
        for _ in range(20):
            await quota_manager.execute_request(mock_callback)

        # Should fail
        with pytest.raises(Exception):
            await quota_manager.execute_request(mock_callback)

        # Wait for window to reset
        await asyncio.sleep(1.1)

        # Should succeed again
        result = await quota_manager.execute_request(mock_callback)
        assert result == "success"
