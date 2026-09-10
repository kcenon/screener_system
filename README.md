> Status: archived 2026-09. No further maintenance; kept for reference.
>
> Performance figures and feature claims in this README were written during active development and have not been re-verified.

# Stock Screening Platform

[![CI Pipeline](https://github.com/kcenon/screener_system/actions/workflows/ci.yml/badge.svg)](https://github.com/kcenon/screener_system/actions/workflows/ci.yml)
[![CD Pipeline](https://github.com/kcenon/screener_system/actions/workflows/cd.yml/badge.svg)](https://github.com/kcenon/screener_system/actions/workflows/cd.yml)
[![Documentation](https://github.com/kcenon/screener_system/actions/workflows/docs.yml/badge.svg)](https://github.com/kcenon/screener_system/actions/workflows/docs.yml)
[![PR Checks](https://github.com/kcenon/screener_system/actions/workflows/pr-checks.yml/badge.svg)](https://github.com/kcenon/screener_system/actions/workflows/pr-checks.yml)
[![codecov](https://codecov.io/gh/kcenon/screener_system/branch/main/graph/badge.svg)](https://codecov.io/gh/kcenon/screener_system)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Docs Status](https://img.shields.io/badge/docs-live-success)](https://kcenon.github.io/screener_system)
[![Project Status](https://img.shields.io/badge/status-production--ready-success)]()
[![Completion](https://img.shields.io/badge/tickets-54%2F54%20(100%25)-brightgreen)]()

A comprehensive stock analysis and screening platform for Korean markets (KOSPI/KOSDAQ) with 200+ financial and technical indicators.

> **🎉 Project Status**: MVP Complete! All 54 planned tickets completed (~358 hours). Production-ready with full documentation, testing, and CI/CD automation.

## 🎯 Features

### ✅ Implemented (Production-Ready)

- **Advanced Stock Screening**: Filter 2,400+ stocks using 200+ technical and financial indicators
  - Complex multi-criteria filtering with AND/OR logic
  - Filter presets (save/load/delete custom filters)
  - Export results to CSV/JSON
  - URL sharing for filter configurations
- **Real-time Market Data**: WebSocket-based live updates
  - Real-time price streaming with JWT authentication
  - Order book visualization (10-level bid/ask)
  - Multi-instance support via Redis Pub/Sub
  - Auto-reconnection with exponential backoff
- **User Authentication & Authorization**: JWT-based security
  - User registration and login
  - Role-based access control (RBAC)
  - Refresh token support
  - Rate limiting by user tier
- **Stock Detail Pages**: Comprehensive stock information
  - Real-time price data and charts
  - Technical indicators visualization
  - Historical data analysis
  - Financial ratios and fundamentals
- **Data Pipeline**: Automated data ingestion and processing
  - Apache Airflow orchestration
  - KIS API integration for real-time data
  - Daily price ingestion (2,400+ stocks)
  - 200+ indicator calculations
  - Error handling and retry logic
- **Monitoring & Observability**: Production-grade monitoring
  - Prometheus metrics collection
  - Grafana dashboards
  - Performance baselines established
  - Alert configuration
- **Documentation**: Comprehensive auto-generated docs
  - Docusaurus documentation platform
  - Python API docs (Sphinx)
  - TypeScript API docs (TypeDoc)
  - OpenAPI/Swagger UI
  - User guides and tutorials

### 🚧 Planned (Future Enhancements)

- **Portfolio Management**: Track holdings and performance vs benchmarks
- **Price Alerts**: Customizable notifications for price movements
- **Mobile App**: React Native mobile application
- **Advanced Analytics**: Backtesting and strategy builder
- **Social Features**: Community discussions and shared analyses

## 📖 Documentation

Comprehensive documentation is automatically built and deployed at **[kcenon.github.io/screener_system](https://kcenon.github.io/screener_system)**

The documentation site includes:
- **Getting Started Guide** - Setup and installation
- **API Reference** - Backend (Python) and Frontend (TypeScript) APIs
- **User Guides** - Feature documentation
- **Architecture** - System design and components
- **Contributing** - Development guidelines

### Building Documentation Locally

```bash
# Build all documentation
cd docs-site
npm install
npm start  # Opens http://localhost:3000

# Build Python API docs (Sphinx)
cd docs/api/python
sphinx-build -b html . _build/html

# Build Frontend API docs (TypeDoc)
cd frontend
npm run docs:generate
```

### Documentation Pipeline

Documentation is automatically built and deployed on every push to `main`:
- **Sphinx** generates Python API documentation
- **TypeDoc** generates TypeScript API documentation
- **Docusaurus** builds the main documentation site
- **GitHub Pages** hosts at https://kcenon.github.io/screener_system

See [CI/CD Setup Guide](docs/CI_CD_SETUP.md) for details.

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
git clone https://github.com/kcenon/screener_system.git
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
git clone https://github.com/kcenon/screener_system.git
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

### Loading Sample Data

After starting the services, load sample stock data for testing:

```bash
# Load pre-generated seed data (150 stocks, 252 days of prices)
docker exec -i screener_postgres psql -U screener_user -d screener_db \
  < database/seeds/seed_data.sql

# Verify data loaded
docker exec screener_postgres psql -U screener_user -d screener_db \
  -c "SELECT COUNT(*) FROM stocks; SELECT COUNT(*) FROM daily_prices;"
```

**Sample Data Includes:**
- 150 stocks (100 KOSPI + 50 KOSDAQ)
- 27,000 daily prices (~252 trading days per stock)
- 600 financial statements (4 quarters per stock)
- 150 calculated indicators

> **Note:** This is test data for development only. For production, use real KRX API data via Airflow DAGs.

See [Data Loading Guide](docs/DATA_LOADING.md) for detailed instructions and customization options.

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

## 📈 Performance Benchmarks

Performance targets measured and validated during Sprint 4:

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Screening Query Time (p99) | < 500ms | ~220ms | ✅ 56% better |
| API Response Time (p95) | < 200ms | ~150ms | ✅ 25% better |
| Page Load Time (p95) | < 1.5s | ~1.2s | ✅ 20% better |
| DAG Execution (Full) | < 10 min | ~8.5 min | ✅ 15% better |
| Cache Hit Rate | > 80% | ~85% | ✅ |
| Test Coverage (Backend) | > 70% | 80% | ✅ |

**Key Optimizations Applied:**
- Window function optimization (45% query speedup)
- Redis caching with 5-minute TTL
- Database connection pooling
- Materialized views for complex queries
- Atomic Redis operations for rate limiting

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

- **Application Metrics**: Grafana dashboard at http://localhost:3000 (development)
- **API Health**: http://localhost:8000/health (development)
- **Database Performance**: TimescaleDB monitoring
- **Error Tracking**: Sentry integration

> **Note**: Production URLs will be configured during deployment phase.

## 🔐 Security

- JWT-based authentication (15-minute access tokens)
- HTTPS only (TLS 1.3)
- Rate limiting (100-2000 req/min based on tier)
- SQL injection prevention (parameterized queries)
- XSS protection (Content Security Policy)
- CSRF protection (SameSite cookies)
- Regular dependency scans (Dependabot)

## 📝 API Documentation

Comprehensive API documentation is available in multiple formats:

**Documentation Portal** (https://kcenon.github.io/screener_system):
- **API Reference**: https://kcenon.github.io/screener_system/docs/api/intro
  - Python Backend API (auto-generated with Sphinx)
  - TypeScript Frontend API (auto-generated with TypeDoc)
  - Architecture and design patterns
  - Code examples and tutorials

**Interactive API Docs** (Backend Server):
- **Swagger UI**: http://localhost:8000/docs (development)
- **ReDoc**: http://localhost:8000/redoc (development)
- **OpenAPI Spec**: http://localhost:8000/openapi.json

> **Note**: Interactive API docs (Swagger/ReDoc) are served by the FastAPI backend. Production URLs will be configured during deployment.

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
- **Issue Tracker**: https://github.com/kcenon/screener_system/issues
- **Documentation**: https://kcenon.github.io/screener_system

## 📊 Project Statistics

| Category | Metrics |
|----------|---------|
| **Development** | 54 tickets completed (100%) |
| **Total Effort** | ~358 hours across 4 sprints |
| **Test Coverage** | Backend: 80%, Frontend: 100% pass rate |
| **Code Quality** | All linting/type checks passing |
| **Documentation** | 100% API coverage, auto-generated |
| **CI/CD** | Fully automated with GitHub Actions |
| **Infrastructure** | Docker, Airflow, Monitoring ready |
| **Security** | JWT auth, rate limiting, SQL injection prevention |

## 🗺️ Development Timeline

### ✅ Sprint 1-2: Foundation & Core Features (Complete)
**Tickets**: 23 tickets, ~137 hours

- ✅ **Infrastructure** (3 tickets)
  - Docker Compose development environment
  - CI/CD pipeline with GitHub Actions
  - Production monitoring and logging
- ✅ **Backend** (6 tickets)
  - FastAPI project setup
  - User authentication API
  - Stock data API
  - Stock screening API (96 tests)
  - API rate limiting and throttling
  - WebSocket real-time streaming
- ✅ **Database** (5 tickets)
  - PostgreSQL + TimescaleDB setup
  - Schema migrations
  - Indexes and materialized views
  - Functions and triggers
  - Order book schema
- ✅ **Data Pipeline** (4 tickets)
  - Apache Airflow environment
  - Daily price ingestion DAG
  - Indicator calculation DAG (200+ indicators)
  - KIS API integration
- ✅ **Frontend** (5 tickets)
  - React + Vite project setup
  - User authentication UI
  - Stock screener page (139 tests)
  - Stock detail page
  - Order book visualization

### ✅ Sprint 3: Polish & Advanced Features (Complete)
**Tickets**: 12 tickets, ~114 hours

- ✅ Technical debt resolution (5 tickets)
- ✅ Security hardening (SQL injection fixes)
- ✅ Performance optimization (45% query improvement)
- ✅ Rate limiting documentation
- ✅ Test coverage increase (59% → 80%)

### ✅ Sprint 4: Quality Assurance & Documentation (Complete)
**Tickets**: 19 tickets, ~107 hours

- ✅ **Bug Fixes & Validation** (7 tickets)
  - Docker environment runtime testing
  - Airflow DAG runtime testing
  - Performance baseline measurement
  - CI/CD validation
  - Acceptance criteria validation
- ✅ **Documentation Sprint** (9 tickets)
  - Docusaurus platform setup
  - Python API documentation (Sphinx)
  - TypeScript API documentation (TypeDoc)
  - Documentation guidelines and templates
  - CI/CD deployment pipeline
- ✅ **Security & Data Quality** (3 tickets)
  - Dependency vulnerability resolution (29 CVEs)
  - Data quality validation
  - Sample data generation

### 🚀 Future Roadmap (Post-MVP)

**Phase 1: Beta Launch** (Next 2 months)
- [ ] User acceptance testing
- [ ] Performance tuning under load
- [ ] Security audit and penetration testing
- [ ] Production deployment and monitoring

**Phase 2: Feature Expansion** (Months 3-6)
- [ ] Portfolio management and tracking
- [ ] Price alerts and notifications
- [ ] Advanced charting features
- [ ] User watchlists and favorites
- [ ] News integration

**Phase 3: Advanced Features** (Months 7-12)
- [ ] Mobile app (React Native)
- [ ] Backtesting engine
- [ ] Strategy builder
- [ ] API access for developers
- [ ] Premium subscription tiers

**Phase 4: Scale & Innovation** (Year 2+)
- [ ] AI-powered stock recommendations
- [ ] Social features and community
- [ ] International markets support
- [ ] Institutional features
- [ ] White-label solutions

## 📚 Documentation

- [Product Requirements Document (PRD)](docs/PRD.md)
- [API Guide](api/README.md)
- [Database Schema](database/README.md)
- [Data Pipeline](data_pipeline/README.md)
- [Architecture Overview](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)

---

**Made with ❤️ by 🍀☀🌕🌥 🌊**
