# Stock Screening Platform

[![CI Pipeline](https://github.com/USERNAME/screener_system/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/screener_system/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/USERNAME/screener_system/branch/main/graph/badge.svg)](https://codecov.io/gh/USERNAME/screener_system)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive stock analysis and screening platform for Korean markets (KOSPI/KOSDAQ) with 200+ financial and technical indicators.

## 🎯 Features

- **Advanced Stock Screening**: Filter 2,400+ stocks using 200+ indicators
- **Real-time Market Data**: Live price updates and volume tracking
- **Portfolio Management**: Track holdings and performance vs benchmarks
- **Price Alerts**: Customizable notifications for price movements
- **Financial Analysis**: Detailed financial statements and ratio analysis
- **Technical Analysis**: Charts with indicators (MA, RSI, MACD, etc.)

## 📊 Tech Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **UI Components**: Radix UI + Tailwind CSS
- **Charts**: TradingView Lightweight Charts + Recharts

### Backend
- **API Framework**: FastAPI (Python)
- **Database**: PostgreSQL 16 + TimescaleDB
- **Caching**: Redis 7
- **Task Queue**: Celery
- **Authentication**: JWT (FastAPI-Users)

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Grafana + Prometheus
- **Logging**: ELK Stack

### Data Pipeline
- **Workflow Orchestration**: Apache Airflow
- **Data Processing**: Pandas + NumPy
- **Data Sources**: KRX API, F&Guide API

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.9+
- PostgreSQL 16+ (with TimescaleDB extension)
- Redis 7+

### Installation

**Option 1: Docker Compose (Recommended)**

```bash
# Clone repository
git clone https://github.com/your-org/screener_system.git
cd screener_system

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Start all services with Docker Compose
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f backend
```

**Option 2: Local Development**

```bash
# Clone repository
git clone https://github.com/your-org/screener_system.git
cd screener_system

# Setup environment
cp .env.example .env

# Start database and cache only
docker-compose up -d postgres redis

# Backend setup
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend setup (in another terminal)
cd frontend
npm install
npm run dev

# Data pipeline setup (optional, in another terminal)
cd data_pipeline
# Follow data_pipeline/README.md for setup
```

Access the application:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Airflow UI**: http://localhost:8080

## 📁 Project Structure

```
screener_system/
├── frontend/                 # React SPA
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API client services
│   │   ├── store/           # Zustand state management
│   │   └── utils/           # Utility functions
│   ├── public/              # Static assets
│   └── package.json
│
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── core/            # Core functionality
│   │   ├── db/              # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── tests/               # Unit & integration tests
│   └── requirements.txt
│
├── database/                 # Database schema & migrations
│   ├── migrations/          # SQL migration files
│   ├── seeds/               # Seed data
│   ├── scripts/             # Utility scripts
│   └── README.md
│
├── data_pipeline/            # Apache Airflow DAGs
│   ├── dags/                # DAG definitions
│   ├── plugins/             # Custom Airflow plugins
│   ├── config/              # Configuration files
│   └── README.md
│
├── api/                      # API specification
│   ├── openapi.yaml         # OpenAPI 3.0 spec
│   └── README.md
│
├── infrastructure/           # Infrastructure as Code
│   ├── docker/              # Dockerfiles
│   ├── kubernetes/          # K8s manifests
│   ├── terraform/           # Cloud infrastructure
│   └── monitoring/          # Grafana dashboards
│
├── docs/                     # Documentation
│   ├── PRD.md               # Product Requirements
│   ├── architecture.md      # System architecture
│   ├── api-guide.md         # API usage guide
│   └── deployment.md        # Deployment guide
│
├── tests/                    # End-to-end tests
│   ├── e2e/                 # Cypress tests
│   └── load/                # k6 load tests
│
├── .github/                  # GitHub workflows
│   └── workflows/
│       ├── ci.yml           # Continuous Integration
│       └── cd.yml           # Continuous Deployment
│
├── docker-compose.yml        # Local development stack
├── .env.example              # Environment variables template
├── .gitignore
└── README.md                 # This file
```

## 🔧 Development

### Running Tests

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest

# End-to-end tests
cd tests/e2e
npx cypress run
```

### Code Quality

```bash
# Frontend linting
cd frontend
npm run lint

# Backend linting
cd backend
ruff check .
mypy app/

# Format code
cd frontend && npm run format
cd backend && ruff format .
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📈 Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Screening Query Time (p99) | < 500ms | ✅ |
| API Response Time (p95) | < 200ms | ✅ |
| Page Load Time (p95) | < 1.5s | ✅ |
| System Uptime | 99.9% | ✅ |
| Cache Hit Rate | > 80% | ✅ |

## 🚢 Deployment

### Docker Production Build

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f infrastructure/kubernetes/

# Check status
kubectl get pods -n screener

# View logs
kubectl logs -f deployment/backend -n screener
```

## 📊 Monitoring

- **Application Metrics**: Grafana dashboard at http://grafana.screener.kr
- **API Health**: http://api.screener.kr/health
- **Database Performance**: TimescaleDB monitoring
- **Error Tracking**: Sentry integration

## 🔐 Security

- JWT-based authentication (15-minute access tokens)
- HTTPS only (TLS 1.3)
- Rate limiting (100-2000 req/min based on tier)
- SQL injection prevention (parameterized queries)
- XSS protection (Content Security Policy)
- CSRF protection (SameSite cookies)
- Regular dependency scans (Dependabot)

## 📝 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://api.screener.kr/docs
- **ReDoc**: http://api.screener.kr/redoc
- **OpenAPI Spec**: `api/openapi.yaml`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Email**: kcenon@gmail.com
- **Issue Tracker**: https://github.com/your-org/screener_system/issues

## 🗺️ Roadmap

### Phase 1: MVP (Months 1-3) ✅
- [x] Core stock screening (20 indicators)
- [x] Stock detail pages
- [x] User authentication
- [x] Basic UI/UX

### Phase 2: Public Launch (Months 4-6) 🚧
- [x] 200+ indicators
- [x] Portfolio management
- [ ] Real-time hot stocks
- [ ] Subscription tiers

### Phase 3: Growth (Months 7-12) 📅
- [ ] Mobile app (React Native)
- [ ] Advanced alerts
- [ ] API access
- [ ] Backtesting

### Phase 4: Advanced Features (Months 13+) 💡
- [ ] AI-powered recommendations
- [ ] Social features
- [ ] International markets
- [ ] Institutional features

## 📚 Documentation

- [Product Requirements Document (PRD)](docs/PRD.md)
- [API Guide](api/README.md)
- [Database Schema](database/README.md)
- [Data Pipeline](data_pipeline/README.md)
- [Architecture Overview](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)

---

**Made with ❤️ by 🍀☀🌕🌥 🌊**
