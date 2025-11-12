---
id: sds-deployment
title: SDS - Deployment
description: Software design specification - deployment
sidebar_label: Deployment
sidebar_position: 9
tags:
  - specification
  - design
  - architecture
---

:::info Navigation
- [Introduction](introduction.md)
- [System Architecture](system-architecture.md)
- [Component Design](component-design.md)
- [Database Design](database-design.md)
- [API Design](api-design.md)
- [Data Pipeline](data-pipeline.md)
- [Security Design](security-design.md)
- [Performance Design](performance-design.md)
- [Deployment](deployment.md) (Current)
- [Tech Stack & Decisions](tech-stack-decisions.md)
:::

# Software Design Specification - Deployment

## 9. Deployment Architecture

### 9.1 Docker Compose (Development)

**Services**:

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app

  airflow_webserver:
    image: apache/airflow:2.8.0-python3.11
    ports:
      - "8080:8080"
    depends_on:
      - postgres

  airflow_scheduler:
    image: apache/airflow:2.8.0-python3.11
    depends_on:
      - airflow_webserver

volumes:
  postgres_data:
  redis_data:
  airflow_logs:
```

### 9.2 Kubernetes (Production)

#### 9.2.1 Architecture

```
┌───────────────────────────────────────────────────────┐
│                    Ingress Controller                  │
│                  (NGINX / Traefik)                     │
│              SSL Termination (Let's Encrypt)           │
└────────────────────┬──────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌────────────────┐        ┌────────────────┐
│   Frontend     │        │   Backend      │
│   Service      │        │   Service      │
│   (ClusterIP)  │        │   (ClusterIP)  │
└────────┬───────┘        └────────┬───────┘
         │                         │
    ┌────┴─────┐            ┌──────┴─────┬─────────┐
    ▼          ▼            ▼            ▼         ▼
┌────────┐ ┌────────┐  ┌────────┐  ┌────────┐ ┌────────┐
│Frontend│ │Frontend│  │Backend │  │Backend │ │Backend │
│  Pod   │ │  Pod   │  │  Pod   │  │  Pod   │ │  Pod   │
│ (NGINX)│ │ (NGINX)│  │(FastAPI│  │(FastAPI│ │(FastAPI│
└────────┘ └────────┘  └────────┘  └────────┘ └────────┘
                            │            │         │
                            └────────────┴─────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
            ┌────────────┐     ┌────────────┐    ┌────────────┐
            │ PostgreSQL │     │   Redis    │    │  Celery    │
            │StatefulSet │     │StatefulSet │    │ Deployment │
            └────────────┘     └────────────┘    └────────────┘
                    │                  │
                    ▼                  ▼
            ┌────────────┐     ┌────────────┐
            │Persistent  │     │Persistent  │
            │  Volume    │     │  Volume    │
            └────────────┘     └────────────┘
```

#### 9.2.2 Kubernetes Manifests

**Backend Deployment**:

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: screener
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: screener/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: screener
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

**Horizontal Pod Autoscaler**:

```yaml
# k8s/backend-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: screener
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Database StatefulSet**:

```yaml
# k8s/postgres-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: screener
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: timescale/timescaledb:latest-pg16
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: screener_db
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 100Gi
```

### 9.3 CI/CD Pipeline

#### 9.3.1 GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run linting
        run: |
          cd frontend
          npm run lint

      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage

      - name: Build
        run: |
          cd frontend
          npm run build

  deploy-production:
    needs: [test-backend, test-frontend]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build and push Docker images
        run: |
          docker build -t screener/backend:${{ github.sha }} ./backend
          docker build -t screener/frontend:${{ github.sha }} ./frontend
          docker push screener/backend:${{ github.sha }}
          docker push screener/frontend:${{ github.sha }}

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/backend backend=screener/backend:${{ github.sha }}
          kubectl set image deployment/frontend frontend=screener/frontend:${{ github.sha }}
          kubectl rollout status deployment/backend
          kubectl rollout status deployment/frontend
```

### 9.4 Monitoring & Observability

#### 9.4.1 Prometheus Metrics

```python
# core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Database metrics
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

# Cache metrics
cache_hits_total = Counter('cache_hits_total', 'Total cache hits')
cache_misses_total = Counter('cache_misses_total', 'Total cache misses')

# Custom business metrics
stock_screening_requests = Counter(
    'stock_screening_requests_total',
    'Total stock screening requests'
)

portfolio_creations = Counter(
    'portfolio_creations_total',
    'Total portfolio creations'
)
```

#### 9.4.2 Grafana Dashboards

**API Performance Dashboard**:

```json
{
  "dashboard": {
    "title": "API Performance",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Request Duration (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      }
    ]
  }
}
```

---