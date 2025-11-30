"""
Prometheus Metrics Middleware

Automatically tracks HTTP metrics for all requests:
- Request count (by method, endpoint, status)
- Request duration (by method, endpoint)
- Requests in progress
- Error count (5xx errors)
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
    http_errors_total,
)


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for HTTP requests.

    Tracks:
    - Total requests
    - Request duration
    - In-progress requests
    - HTTP errors (5xx)
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and collect metrics.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware/handler in the chain

        Returns:
            The HTTP response
        """
        # Extract method and path
        method = request.method
        path = request.url.path

        # Normalize path for metrics (remove IDs, query params)
        endpoint = self._normalize_path(path)

        # Skip metrics endpoint itself to avoid recursion
        if endpoint == "/metrics":
            return await call_next(request)

        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Start timer
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code

            # Record metrics
            duration = time.time() - start_time

            # Request count
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()

            # Request duration
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Track 5xx errors
            if 500 <= status_code < 600:
                http_errors_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()

            return response

        except Exception:
            # Record error metrics
            duration = time.time() - start_time

            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()

            http_errors_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Re-raise the exception
            raise

        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()

    @staticmethod
    def _normalize_path(path: str) -> str:
        """
        Normalize URL path for metric labels.

        Replaces dynamic segments (IDs, UUIDs) with placeholders to prevent
        high cardinality in metric labels.

        Examples:
            /api/stocks/005930 -> /api/stocks/{code}
            /api/users/123 -> /api/users/{id}

        Args:
            path: The original URL path

        Returns:
            Normalized path with placeholders
        """
        parts = path.split('/')
        normalized_parts = []

        for i, part in enumerate(parts):
            # Empty part (leading slash)
            if not part:
                normalized_parts.append(part)
                continue

            # Check if part looks like an ID or code
            if PrometheusMetricsMiddleware._is_dynamic_segment(part):
                # Determine placeholder based on context
                if i > 0:
                    prev_part = parts[i - 1]
                    if prev_part == 'stocks':
                        normalized_parts.append('{code}')
                    elif prev_part == 'users':
                        normalized_parts.append('{id}')
                    elif prev_part == 'portfolios':
                        normalized_parts.append('{id}')
                    elif prev_part == 'prices':
                        normalized_parts.append('{code}')
                    else:
                        normalized_parts.append('{id}')
                else:
                    normalized_parts.append('{id}')
            else:
                normalized_parts.append(part)

        return '/'.join(normalized_parts)

    @staticmethod
    def _is_dynamic_segment(segment: str) -> bool:
        """
        Check if a URL segment is dynamic (ID, UUID, etc.).

        Args:
            segment: URL path segment

        Returns:
            True if segment appears to be dynamic
        """
        # Check if it's all digits (numeric ID)
        if segment.isdigit():
            return True

        # Check if it's a stock code (6 digits)
        if len(segment) == 6 and segment.isdigit():
            return True

        # Check if it's a UUID pattern (contains hyphens and alphanumeric)
        if '-' in segment and len(segment) >= 32:
            return True

        # Check if it matches common ID patterns
        if len(segment) > 10 and any(c.isdigit() for c in segment):
            return True

        return False


# Export for easy import
__all__ = ['PrometheusMetricsMiddleware']
