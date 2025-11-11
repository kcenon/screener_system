"""
Prometheus Metrics for Stock Screening Platform

This module defines all Prometheus metrics for monitoring the application.
Metrics are categorized into:
- HTTP metrics (request count, duration, errors)
- Database metrics (query duration, connection pool)
- Cache metrics (hit/miss ratio, operations)
- Business metrics (user activity, screening requests)
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client import REGISTRY, CollectorRegistry
from typing import Dict, Any

# ============================================================================
# HTTP Metrics
# ============================================================================

http_requests_total = Counter(
    name='http_requests_total',
    documentation='Total HTTP requests',
    labelnames=['method', 'endpoint', 'status_code'],
    registry=REGISTRY
)

http_request_duration_seconds = Histogram(
    name='http_request_duration_seconds',
    documentation='HTTP request duration in seconds',
    labelnames=['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=REGISTRY
)

http_requests_in_progress = Gauge(
    name='http_requests_in_progress',
    documentation='Number of HTTP requests currently being processed',
    labelnames=['method', 'endpoint'],
    registry=REGISTRY
)

http_errors_total = Counter(
    name='http_errors_total',
    documentation='Total HTTP 5xx errors',
    labelnames=['method', 'endpoint', 'status_code'],
    registry=REGISTRY
)

# ============================================================================
# Database Metrics
# ============================================================================

db_query_duration_seconds = Histogram(
    name='db_query_duration_seconds',
    documentation='Database query duration in seconds',
    labelnames=['operation', 'table'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=REGISTRY
)

db_connections_active = Gauge(
    name='db_connections_active',
    documentation='Number of active database connections',
    registry=REGISTRY
)

db_connections_idle = Gauge(
    name='db_connections_idle',
    documentation='Number of idle database connections',
    registry=REGISTRY
)

db_slow_queries_total = Counter(
    name='db_slow_queries_total',
    documentation='Total number of slow queries (> 1 second)',
    labelnames=['operation', 'table'],
    registry=REGISTRY
)

db_query_errors_total = Counter(
    name='db_query_errors_total',
    documentation='Total database query errors',
    labelnames=['operation', 'error_type'],
    registry=REGISTRY
)

# ============================================================================
# Cache Metrics (Redis)
# ============================================================================

cache_operations_total = Counter(
    name='cache_operations_total',
    documentation='Total cache operations',
    labelnames=['operation', 'result'],  # operation: get/set/delete, result: hit/miss/error
    registry=REGISTRY
)

cache_hit_ratio = Gauge(
    name='cache_hit_ratio',
    documentation='Cache hit ratio (0.0 to 1.0)',
    registry=REGISTRY
)

cache_operation_duration_seconds = Histogram(
    name='cache_operation_duration_seconds',
    documentation='Cache operation duration in seconds',
    labelnames=['operation'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1),
    registry=REGISTRY
)

cache_memory_usage_bytes = Gauge(
    name='cache_memory_usage_bytes',
    documentation='Redis memory usage in bytes',
    registry=REGISTRY
)

# ============================================================================
# Business Metrics
# ============================================================================

user_registrations_total = Counter(
    name='user_registrations_total',
    documentation='Total user registrations',
    registry=REGISTRY
)

user_logins_total = Counter(
    name='user_logins_total',
    documentation='Total user logins',
    labelnames=['result'],  # result: success/failure
    registry=REGISTRY
)

screening_requests_total = Counter(
    name='screening_requests_total',
    documentation='Total stock screening requests',
    labelnames=['template'],  # template: custom/value/growth/momentum etc.
    registry=REGISTRY
)

screening_results_count = Histogram(
    name='screening_results_count',
    documentation='Number of stocks returned per screening request',
    buckets=(0, 10, 50, 100, 500, 1000, 2000),
    registry=REGISTRY
)

portfolio_operations_total = Counter(
    name='portfolio_operations_total',
    documentation='Total portfolio operations',
    labelnames=['operation'],  # operation: create/update/delete
    registry=REGISTRY
)

active_users_gauge = Gauge(
    name='active_users_current',
    documentation='Number of currently active users (WebSocket connections)',
    registry=REGISTRY
)

# ============================================================================
# WebSocket Metrics
# ============================================================================

websocket_connections_active = Gauge(
    name='websocket_connections_active',
    documentation='Number of active WebSocket connections',
    registry=REGISTRY
)

websocket_messages_total = Counter(
    name='websocket_messages_total',
    documentation='Total WebSocket messages',
    labelnames=['direction', 'message_type'],  # direction: sent/received, type: price/orderbook/etc
    registry=REGISTRY
)

# ============================================================================
# Application Info
# ============================================================================

app_info = Info(
    name='app',
    documentation='Application information',
    registry=REGISTRY
)

# Set application info (called at startup)
app_info.info({
    'name': 'stock-screener-backend',
    'version': '1.0.0',
    'environment': 'development'
})

# ============================================================================
# Helper Functions
# ============================================================================

def update_cache_hit_ratio() -> None:
    """Calculate and update cache hit ratio based on operation counters"""
    try:
        # Get hit and miss counts from cache_operations_total metric
        hits = 0
        misses = 0

        for sample in cache_operations_total.collect()[0].samples:
            if 'result' in sample.labels:
                if sample.labels['result'] == 'hit':
                    hits += sample.value
                elif sample.labels['result'] == 'miss':
                    misses += sample.value

        total = hits + misses
        if total > 0:
            ratio = hits / total
            cache_hit_ratio.set(ratio)
        else:
            cache_hit_ratio.set(0.0)
    except Exception:
        # Silently fail to avoid breaking the application
        pass


def get_metrics_summary() -> Dict[str, Any]:
    """
    Get a summary of current metrics for health checks.
    Returns key metrics in a dictionary.
    """
    try:
        return {
            'db': {
                'connections_active': db_connections_active._value.get(),
                'connections_idle': db_connections_idle._value.get(),
            },
            'cache': {
                'hit_ratio': cache_hit_ratio._value.get(),
            },
            'websocket': {
                'active_connections': websocket_connections_active._value.get(),
            },
            'users': {
                'active': active_users_gauge._value.get(),
            }
        }
    except Exception:
        return {}


# Export all metrics for easy import
__all__ = [
    # HTTP
    'http_requests_total',
    'http_request_duration_seconds',
    'http_requests_in_progress',
    'http_errors_total',
    # Database
    'db_query_duration_seconds',
    'db_connections_active',
    'db_connections_idle',
    'db_slow_queries_total',
    'db_query_errors_total',
    # Cache
    'cache_operations_total',
    'cache_hit_ratio',
    'cache_operation_duration_seconds',
    'cache_memory_usage_bytes',
    # Business
    'user_registrations_total',
    'user_logins_total',
    'screening_requests_total',
    'screening_results_count',
    'portfolio_operations_total',
    'active_users_gauge',
    # WebSocket
    'websocket_connections_active',
    'websocket_messages_total',
    # Info
    'app_info',
    # Helpers
    'update_cache_hit_ratio',
    'get_metrics_summary',
]
