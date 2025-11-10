"""KIS API Quota Manager with Circuit Breaker and Priority Queue"""

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

from app.core.cache import cache_manager
from app.core.config import settings
from app.core.logging import logger


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Too many failures, block requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class RequestPriority(Enum):
    """Request priority levels"""

    HIGH = 1  # Real-time price updates
    MEDIUM = 2  # User-initiated queries
    LOW = 3  # Batch updates, background tasks


@dataclass
class QueuedRequest:
    """Represents a queued API request"""

    priority: RequestPriority
    callback: Callable
    timestamp: float
    timeout: float = settings.KIS_API_QUEUE_TIMEOUT


class KISQuotaManager:
    """
    Manages KIS API quota with circuit breaker and priority queue

    Features:
    - Rate limiting (20 req/sec)
    - Request queuing with priority
    - Circuit breaker pattern
    - Atomic Redis operations
    """

    # Lua script for atomic rate limit check with KIS API
    # Ensures we never exceed 20 req/sec
    KIS_QUOTA_SCRIPT = """
    local current = redis.call('incr', KEYS[1])
    if current == 1 then
        redis.call('expire', KEYS[1], ARGV[1])
    end
    if current > tonumber(ARGV[2]) then
        return 0  -- Quota exceeded
    end
    return 1  -- Quota available
    """

    def __init__(self):
        """Initialize KIS quota manager"""
        self.circuit_state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.circuit_open_time = 0

        # Priority queues (using deque for O(1) operations)
        self.queues = {
            RequestPriority.HIGH: deque(),
            RequestPriority.MEDIUM: deque(),
            RequestPriority.LOW: deque(),
        }

        self.queue_processing = False
        self.total_requests = 0
        self.total_failures = 0

    async def execute_request(
        self,
        callback: Callable,
        priority: RequestPriority = RequestPriority.MEDIUM,
        timeout: Optional[float] = None,
    ):
        """
        Execute KIS API request with quota management

        Args:
            callback: Async function to execute
            priority: Request priority level
            timeout: Request timeout in seconds

        Returns:
            Result from callback

        Raises:
            Exception: If circuit is open or quota exceeded
        """
        # Check circuit breaker
        if not await self._check_circuit():
            raise Exception(
                f"Circuit breaker is OPEN. Service unavailable. "
                f"Retry after {settings.KIS_API_CIRCUIT_BREAKER_TIMEOUT} seconds."
            )

        # Check quota
        if not await self._check_quota():
            if settings.KIS_API_ENABLE_QUEUE:
                # Add to queue if queuing enabled
                logger.info(
                    f"Quota exceeded, queuing request with priority {priority.name}"
                )
                return await self._queue_request(callback, priority, timeout)
            else:
                raise Exception("KIS API quota exceeded (20 req/sec)")

        # Execute request
        try:
            result = await callback()
            self.total_requests += 1

            # Reset failure count on success
            if self.circuit_state == CircuitState.HALF_OPEN:
                logger.info("Circuit breaker closing after successful request")
                self.circuit_state = CircuitState.CLOSED
                self.failure_count = 0

            return result

        except Exception as e:
            self._record_failure()
            raise e

    async def _check_circuit(self) -> bool:
        """
        Check circuit breaker state

        Returns:
            True if circuit allows requests, False otherwise
        """
        if self.circuit_state == CircuitState.CLOSED:
            return True

        if self.circuit_state == CircuitState.OPEN:
            # Check if timeout elapsed
            elapsed = time.time() - self.circuit_open_time
            if elapsed >= settings.KIS_API_CIRCUIT_BREAKER_TIMEOUT:
                logger.info("Circuit breaker entering HALF_OPEN state")
                self.circuit_state = CircuitState.HALF_OPEN
                return True
            return False

        # HALF_OPEN state allows limited requests to test recovery
        return True

    async def _check_quota(self) -> bool:
        """
        Check if KIS API quota available using Redis

        Returns:
            True if quota available, False if exceeded
        """
        if not cache_manager.redis:
            logger.warning("Redis not available, allowing request")
            return True

        try:
            # Use atomic Lua script to check and increment quota
            key = "kis_api_quota"
            window = settings.KIS_API_QUOTA_WINDOW
            limit = settings.KIS_API_RATE_LIMIT

            result = await cache_manager.redis.eval(
                self.KIS_QUOTA_SCRIPT, 1, key, window, limit
            )

            return result == 1

        except Exception as e:
            logger.error(f"Error checking KIS quota: {e}")
            # Allow request on Redis error (fail-open)
            return True

    async def _queue_request(
        self,
        callback: Callable,
        priority: RequestPriority,
        timeout: Optional[float],
    ):
        """
        Queue a request for later execution

        Args:
            callback: Function to execute
            priority: Request priority
            timeout: Timeout in seconds

        Returns:
            Result from callback when executed
        """
        queued = QueuedRequest(
            priority=priority,
            callback=callback,
            timestamp=time.time(),
            timeout=timeout or settings.KIS_API_QUEUE_TIMEOUT,
        )

        self.queues[priority].append(queued)

        # Start queue processor if not running
        if not self.queue_processing:
            asyncio.create_task(self._process_queue())

        # Wait for request to be processed (simplified, needs proper implementation)
        # In production, use asyncio.Event or similar for proper waiting
        logger.warning(
            "Queue processing not fully implemented. Request queued but may not execute."
        )
        return None

    async def _process_queue(self):
        """Process queued requests in priority order"""
        if self.queue_processing:
            return

        self.queue_processing = True
        logger.info("Starting KIS API queue processor")

        try:
            while True:
                # Check if any requests in queue
                total_queued = sum(len(q) for q in self.queues.values())
                if total_queued == 0:
                    await asyncio.sleep(1)
                    continue

                # Process in priority order (HIGH -> MEDIUM -> LOW)
                for priority in [RequestPriority.HIGH, RequestPriority.MEDIUM, RequestPriority.LOW]:
                    queue = self.queues[priority]

                    if not queue:
                        continue

                    # Get next request
                    request = queue.popleft()

                    # Check if request expired
                    if time.time() - request.timestamp > request.timeout:
                        logger.warning(
                            f"Dropping expired request (waited {time.time() - request.timestamp:.2f}s)"
                        )
                        continue

                    # Check quota
                    if not await self._check_quota():
                        # Put back and wait
                        queue.appendleft(request)
                        await asyncio.sleep(0.1)
                        continue

                    # Execute request
                    try:
                        await request.callback()
                        self.total_requests += 1
                    except Exception as e:
                        logger.error(f"Queue request execution failed: {e}")
                        self._record_failure()

        finally:
            self.queue_processing = False
            logger.info("KIS API queue processor stopped")

    def _record_failure(self):
        """Record API failure for circuit breaker"""
        self.failure_count += 1
        self.total_failures += 1
        self.last_failure_time = time.time()

        logger.warning(
            f"KIS API failure recorded | "
            f"Count: {self.failure_count} | "
            f"Threshold: {settings.KIS_API_CIRCUIT_BREAKER_THRESHOLD}"
        )

        # Open circuit if threshold exceeded
        if self.failure_count >= settings.KIS_API_CIRCUIT_BREAKER_THRESHOLD:
            logger.error(
                f"Circuit breaker opening after {self.failure_count} failures"
            )
            self.circuit_state = CircuitState.OPEN
            self.circuit_open_time = time.time()

    def get_stats(self) -> dict:
        """
        Get quota manager statistics

        Returns:
            Dictionary with current stats
        """
        return {
            "circuit_state": self.circuit_state.value,
            "failure_count": self.failure_count,
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "queued_high": len(self.queues[RequestPriority.HIGH]),
            "queued_medium": len(self.queues[RequestPriority.MEDIUM]),
            "queued_low": len(self.queues[RequestPriority.LOW]),
            "queue_processing": self.queue_processing,
        }


# Global KIS quota manager instance
kis_quota_manager = KISQuotaManager()
