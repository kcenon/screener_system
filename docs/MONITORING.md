# Monitoring Setup

This document describes the monitoring infrastructure for the Stock Screening Platform.

## Architecture Overview

```
┌──────────────┐     scrape      ┌──────────────┐     alert      ┌───────────────┐
│  Prometheus  │ ◄────────────── │  Exporters   │                │  Alertmanager │
│  :9090       │ ──────────────► │              │                │  :9093        │
└──────┬───────┘   evaluate      └──────────────┘                └───────┬───────┘
       │           rules                                                 │
       │                                                          route/notify
       ▼                                                                 │
┌──────────────┐                                                         ▼
│   Grafana    │                                                 ┌───────────────┐
│   :3001      │                                                 │  Webhook /    │
└──────────────┘                                                 │  Slack / Email│
                                                                 └───────────────┘
```

## Quick Start

### Start monitoring services

```bash
# Start core services + monitoring
docker compose --profile monitoring up -d

# Start everything (includes celery, airflow, frontend, monitoring)
docker compose --profile full up -d
```

### Access dashboards

| Service       | URL                          | Default Credentials         |
|---------------|------------------------------|-----------------------------|
| Grafana       | http://localhost:3001        | `$GRAFANA_USER` / `$GRAFANA_PASSWORD` |
| Prometheus    | http://localhost:9090        | No authentication           |
| Alertmanager  | http://localhost:9093        | No authentication           |

## Components

### Prometheus (Metrics Collection)

- **Image**: `prom/prometheus:latest`
- **Port**: 9090
- **Retention**: 15 days
- **Scrape interval**: 15s (global), 10s (backend), 30s (exporters)
- **Config**: `infrastructure/monitoring/prometheus/prometheus.yml`

### Grafana (Visualization)

- **Image**: `grafana/grafana:latest`
- **Port**: 3001 (mapped from container 3000)
- **Datasource**: Prometheus (auto-provisioned)
- **Dashboards**: Auto-provisioned from `infrastructure/monitoring/grafana/dashboards/json/`

### Alertmanager (Alert Routing)

- **Image**: `prom/alertmanager:latest`
- **Port**: 9093
- **Config**: `infrastructure/monitoring/alertmanager/alertmanager.yml`
- **Default receiver**: Webhook to `backend:8000/v1/webhooks/alertmanager`

## Exporters

| Exporter          | Image                                        | Metrics Port | Target Service |
|-------------------|----------------------------------------------|-------------|----------------|
| postgres-exporter | `prometheuscommunity/postgres-exporter`      | 9187        | PostgreSQL     |
| redis-exporter    | `oliver006/redis_exporter`                   | 9121        | Redis          |
| nginx-exporter    | `nginx/nginx-prometheus-exporter`            | 9113        | Nginx          |
| celery-exporter   | `danihodovic/celery-exporter`                | 9808        | Celery Worker  |

All exporters run under the `monitoring` or `full` Docker Compose profile.

### Nginx Exporter Prerequisites

The nginx-exporter requires `stub_status` to be enabled. This is already configured in
`infrastructure/nginx/nginx.conf` on port 8081:

```nginx
server {
    listen 8081;
    location /stub_status {
        stub_status;
    }
}
```

## Dashboards

Four pre-built Grafana dashboards are auto-provisioned:

| Dashboard              | File                        | Key Metrics                                         |
|------------------------|-----------------------------|-----------------------------------------------------|
| API Performance        | `api_performance.json`      | Request rate, latency (p50/p95/p99), error rate     |
| Business Metrics       | `business_metrics.json`     | Active users, logins, registrations, screenings     |
| Cache Performance      | `cache_performance.json`    | Hit ratio, operations, memory usage                 |
| Database Performance   | `database_performance.json` | Query duration, connections, slow queries, errors   |

## Alert Rules

Alert rules are defined in `infrastructure/monitoring/prometheus/alerts/`:

| File                  | Alerts                                                                      |
|-----------------------|-----------------------------------------------------------------------------|
| `service_health.yml`  | ServiceDown, BackendApiDown, PostgresDown, RedisDown, NginxDown             |
| `performance.yml`     | HighErrorRate, HighLatencyP95/P99, SlowQueries, LowCacheHitRatio           |
| `resources.yml`       | PrometheusStorageHigh, DbConnectionPoolExhaustion, RedisHighMemory         |

### Severity Levels

- **critical**: Immediate attention required (1h repeat interval)
- **warning**: Investigation needed (4h repeat interval)

### Inhibition Rules

When a `critical` alert fires, the corresponding `warning` alert for the same service
is automatically suppressed to reduce noise.

## Application Metrics

The backend exposes Prometheus metrics at `GET /metrics`. All metrics are defined in
`backend/app/core/metrics.py`:

### HTTP Metrics
- `http_requests_total` — Total requests by method, endpoint, status_code
- `http_request_duration_seconds` — Request duration histogram
- `http_requests_in_progress` — Currently processing requests
- `http_errors_total` — 5xx error count

### Database Metrics
- `db_query_duration_seconds` — Query duration by operation and table
- `db_connections_active` / `db_connections_idle` — Connection pool status
- `db_slow_queries_total` — Queries exceeding 1 second
- `db_query_errors_total` — Query error count by type

### Cache Metrics
- `cache_operations_total` — Cache operations by result (hit/miss)
- `cache_hit_ratio` — Calculated hit ratio (0.0-1.0)
- `cache_operation_duration_seconds` — Cache operation latency
- `cache_memory_usage_bytes` — Redis memory usage

### Business Metrics
- `user_registrations_total` / `user_logins_total` — User activity
- `screening_requests_total` — Screening request count by template
- `screening_results_count` — Results per screening histogram
- `active_users_current` — Currently active users
- `websocket_connections_active` — Active WebSocket connections

## Notification Channels

The default Alertmanager configuration uses a webhook receiver. To enable other channels,
edit `infrastructure/monitoring/alertmanager/alertmanager.yml`:

### Slack

```yaml
receivers:
  - name: 'slack-critical'
    slack_configs:
      - api_url: '${ALERTMANAGER_SLACK_WEBHOOK_URL}'
        channel: '#alerts-critical'
        send_resolved: true
```

### Email

```yaml
receivers:
  - name: 'email-critical'
    email_configs:
      - to: '${ALERTMANAGER_EMAIL_TO}'
        from: '${SMTP_FROM}'
        smarthost: '${SMTP_SMARTHOST}'
        require_tls: true
        send_resolved: true
```

## Environment Variables

| Variable                         | Required | Description                          |
|----------------------------------|----------|--------------------------------------|
| `GRAFANA_USER`                   | No       | Grafana admin username (default: admin) |
| `GRAFANA_PASSWORD`               | Yes      | Grafana admin password               |
| `PROMETHEUS_PORT`                | No       | Prometheus port (default: 9090)      |
| `GRAFANA_PORT`                   | No       | Grafana port (default: 3001)         |
| `ALERTMANAGER_PORT`              | No       | Alertmanager port (default: 9093)    |
| `ALERTMANAGER_SLACK_WEBHOOK_URL` | No       | Slack webhook URL for alerts         |
| `ALERTMANAGER_EMAIL_TO`          | No       | Alert recipient email                |
| `SMTP_SMARTHOST`                 | No       | SMTP relay host:port                 |
| `SMTP_FROM`                      | No       | Alert sender email address           |

## Future Enhancements

### Airflow Metrics

Airflow requires a StatsD exporter to expose metrics in Prometheus format.
To enable Airflow monitoring:

1. Add `statsd-exporter` container to `docker-compose.yml`
2. Set Airflow environment variables:
   ```yaml
   AIRFLOW__METRICS__STATSD_ON: 'true'
   AIRFLOW__METRICS__STATSD_HOST: statsd-exporter
   AIRFLOW__METRICS__STATSD_PORT: 9125
   ```
3. Uncomment the `airflow` scrape config in `prometheus.yml`

### Node Exporter (System Metrics)

For host-level metrics (CPU, memory, disk), add `node-exporter` container
and uncomment the corresponding scrape config in `prometheus.yml`.
