# Monitoring and Observability Guide

This guide explains how to use the monitoring stack for the Stock Screening Platform.

## Overview

The platform uses **Prometheus** for metrics collection and **Grafana** for visualization.

### Components

- **Prometheus**: Time-series database for metrics
  - URL: http://localhost:9090
  - Retention: 15 days
  - Scrape interval: 15s (API: 10s)

- **Grafana**: Dashboard and visualization
  - URL: http://localhost:3001
  - Default credentials: admin/admin (change in production)
  - Pre-configured dashboards included

## Quick Start

### Starting Monitoring Services

```bash
# Start with monitoring profile
docker-compose --profile monitoring up -d

# Or start everything (including monitoring)
docker-compose --profile full up -d
```

### Accessing Dashboards

1. **Grafana**: http://localhost:3001
   - Login with admin/admin
   - Navigate to Dashboards → Browse
   - Available dashboards:
     - API Performance
     - Database Performance
     - Cache Performance
     - Business Metrics

2. **Prometheus**: http://localhost:9090
   - Query metrics directly
   - Check targets: http://localhost:9090/targets

3. **Metrics Endpoint**: http://localhost:8000/metrics
   - Prometheus text format
   - All application metrics

## Available Metrics

### HTTP Metrics

- `http_requests_total` - Total requests by method, endpoint, status
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_in_progress` - Current in-flight requests
- `http_errors_total` - 5xx error count

**Example Prometheus Queries:**

```promql
# Request rate per second
rate(http_requests_total[1m])

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate percentage
(sum(rate(http_errors_total[5m])) / sum(rate(http_requests_total[5m]))) * 100
```

### Database Metrics

- `db_query_duration_seconds` - Query execution time histogram
- `db_connections_active` - Active connection count
- `db_connections_idle` - Idle connection count
- `db_slow_queries_total` - Queries taking > 1 second
- `db_query_errors_total` - Database error count

**Example Queries:**

```promql
# Average query time
rate(db_query_duration_seconds_sum[5m]) / rate(db_query_duration_seconds_count[5m])

# Slow query rate
rate(db_slow_queries_total[1m])
```

### Cache Metrics (Redis)

- `cache_operations_total` - Cache operations by type and result
- `cache_hit_ratio` - Current hit ratio (0.0-1.0)
- `cache_operation_duration_seconds` - Cache operation latency
- `cache_memory_usage_bytes` - Redis memory usage

**Example Queries:**

```promql
# Cache hit rate
cache_hit_ratio

# Cache operations per second
rate(cache_operations_total[1m])
```

### Business Metrics

- `user_registrations_total` - Total user signups
- `user_logins_total` - Login attempts (success/failure)
- `screening_requests_total` - Stock screening requests
- `screening_results_count` - Results returned per request
- `portfolio_operations_total` - Portfolio CRUD operations
- `active_users_current` - Currently active users
- `websocket_connections_active` - Active WebSocket connections

**Example Queries:**

```promql
# New users today
increase(user_registrations_total[24h])

# Active screening users
rate(screening_requests_total[5m])
```

## Dashboards

### API Performance Dashboard

Monitors HTTP request performance:

- **Request Rate**: Requests per second by endpoint
- **Latency**: p50, p95, p99 response times
- **Error Rate**: 5xx error percentage
- **Top Endpoints**: Most requested endpoints
- **Real-time Stats**: Requests in progress, total requests, error rate

**Alerts:**
- Error rate > 1%
- P95 latency > 500ms

### Database Performance Dashboard

Tracks PostgreSQL/TimescaleDB performance:

- **Query Duration**: p95, p99 query times
- **Connections**: Active and idle connection counts
- **Slow Queries**: Queries exceeding 1 second
- **Errors**: Database error rate

**Alerts:**
- Connection pool exhaustion (> 80% usage)
- Slow query rate spike

### Cache Performance Dashboard

Redis performance metrics:

- **Hit Rate**: Cache hit ratio (target: > 80%)
- **Operations**: Cache get/set rates
- **Latency**: Cache operation duration
- **Memory**: Redis memory usage

**Alerts:**
- Hit rate < 80%
- Memory usage > 80% of limit

### Business Metrics Dashboard

Application-level KPIs:

- **User Activity**: Active users, logins, registrations
- **Screening Requests**: Request rate and results distribution
- **Portfolio Operations**: Create, update, delete operations
- **WebSocket**: Active connection count

## Instrumentation

### Adding Custom Metrics

**1. Define the metric in `app/core/metrics.py`:**

```python
from prometheus_client import Counter

# Add your metric
my_custom_counter = Counter(
    name='my_custom_events_total',
    documentation='Total custom events',
    labelnames=['event_type'],
    registry=REGISTRY
)
```

**2. Use the metric in your code:**

```python
from app.core.metrics import my_custom_counter

# Increment the counter
my_custom_counter.labels(event_type='user_action').inc()
```

**3. Query in Prometheus:**

```promql
rate(my_custom_events_total[5m])
```

### Metric Types

- **Counter**: Monotonically increasing value (e.g., total requests)
- **Gauge**: Value that can go up/down (e.g., active connections)
- **Histogram**: Distribution of values (e.g., response times)
- **Info**: Static information (e.g., application version)

### Best Practices

1. **Label Cardinality**: Keep label values bounded
   - ✅ Good: `status_code` (limited values: 200, 404, 500, etc.)
   - ❌ Bad: `user_id` (unbounded, millions of values)

2. **Naming Convention**: Follow Prometheus standards
   - Format: `{namespace}_{subsystem}_{name}_{unit}`
   - Example: `http_request_duration_seconds`
   - Units: `_seconds`, `_bytes`, `_total`, `_ratio`

3. **Histogram Buckets**: Choose appropriate buckets for your SLO
   ```python
   # For API latency (in seconds)
   buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
   ```

4. **Avoid High-Cardinality Labels**: Don't use IDs as labels
   ```python
   # ❌ Bad - unbounded cardinality
   metric.labels(stock_code='005930')  # 2400+ stocks

   # ✅ Good - use aggregates or log in traces
   metric.labels(market='KOSPI')  # Only 2 values
   ```

## Alerting

### Alert Rules

Alert rules are defined in Grafana dashboards. Example:

```yaml
# Low cache hit rate
- alert: LowCacheHitRate
  expr: cache_hit_ratio < 0.8
  for: 5m
  annotations:
    summary: "Cache hit rate below 80%"
    description: "Current hit rate: {{ $value }}"
```

### Notification Channels

Configure in Grafana → Alerting → Contact Points:

- **Email**: SMTP configuration required
- **Slack**: Webhook URL required
- **PagerDuty**: Integration key required

### Response Procedures

When an alert fires:

1. **Check Grafana Dashboard**: Identify the scope (which endpoint, service)
2. **View Recent Logs**: Check application logs for errors
3. **Check Prometheus**: Query metrics for detailed breakdown
4. **Investigate Root Cause**: Database slow? Cache miss? External API?
5. **Mitigate**: Scale, restart, or deploy fix
6. **Document**: Add incident to runbook

## Performance Targets

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| API Response Time (p95) | < 200ms | > 500ms |
| API Response Time (p99) | < 500ms | > 1000ms |
| Error Rate | < 0.1% | > 1% |
| Cache Hit Rate | > 80% | < 80% |
| DB Query Time (p95) | < 100ms | > 500ms |
| Screening Query (p99) | < 500ms | > 1000ms |

## Troubleshooting

### Prometheus Not Scraping Targets

**Symptom**: Targets show as "DOWN" in Prometheus UI

**Solutions:**
1. Check network connectivity: `docker-compose exec prometheus wget -O- http://backend:8000/metrics`
2. Verify service is healthy: `docker-compose ps`
3. Check Prometheus logs: `docker-compose logs prometheus`

### Grafana Dashboards Not Loading

**Symptom**: Dashboards appear empty or show "No data"

**Solutions:**
1. Check Prometheus data source: Grafana → Data Sources
2. Verify Prometheus is scraping: http://localhost:9090/targets
3. Check time range in dashboard (top-right)
4. Restart Grafana: `docker-compose restart grafana`

### High Memory Usage

**Symptom**: Prometheus container using too much memory

**Solutions:**
1. Reduce retention time: `--storage.tsdb.retention.time=7d`
2. Reduce scrape interval in `prometheus.yml`
3. Remove unused metrics (decrease cardinality)

## Maintenance

### Data Retention

Prometheus retains data for **15 days** by default.

To change retention:

```yaml
# docker-compose.yml
command:
  - '--storage.tsdb.retention.time=30d'  # 30 days
  - '--storage.tsdb.retention.size=10GB'  # or size-based
```

### Backup

**Prometheus Data:**

```bash
# Backup (while Prometheus is running)
docker-compose exec prometheus promtool tsdb snapshot /prometheus

# Data location
docker volume inspect screener_prometheus_data
```

**Grafana Dashboards:**

Dashboards are provisioned from `infrastructure/monitoring/grafana/dashboards/json/`.
Keep these files in version control.

## Production Considerations

### Security

1. **Change default passwords**:
   ```bash
   GF_SECURITY_ADMIN_PASSWORD=strong_password_here
   ```

2. **Enable HTTPS** for Grafana (via NGINX reverse proxy)

3. **Authentication**: Configure SSO or LDAP in Grafana

4. **Network isolation**: Use Docker networks to restrict access

### High Availability

For production, consider:

1. **Prometheus HA**: Run multiple Prometheus instances with remote storage
2. **Grafana HA**: Load balance multiple Grafana instances
3. **Alertmanager**: Add for alert deduplication and routing

### Cloud-Native Monitoring

For Kubernetes deployment:

- Use **Prometheus Operator** for easier management
- Deploy **Thanos** for long-term storage and global view
- Use **Loki** for log aggregation (complements metrics)

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)
- [RED Method](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/)
- [SRE Book - Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)

---

**Last Updated**: 2025-11-11
**Version**: 1.0.0
