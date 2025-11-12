---
id: sds-tech-stack-decisions
title: SDS - Tech Stack & Decisions
description: Software design specification - tech stack & decisions
sidebar_label: Tech Stack & Decisions
sidebar_position: 10
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
- [Deployment](deployment.md)
- [Tech Stack & Decisions](tech-stack-decisions.md) (Current)
:::

# Software Design Specification - Tech Stack & Decisions

## 10. Technology Stack

### 10.1 Frontend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | React | 18.x | UI library |
| **Language** | TypeScript | 5.x | Type-safe JavaScript |
| **Build Tool** | Vite | 5.x | Fast build and HMR |
| **State Management** | Zustand | 4.x | Lightweight state management |
| **Data Fetching** | TanStack Query | 5.x | Server state management, caching |
| **Routing** | React Router | 6.x | Client-side routing |
| **UI Components** | Radix UI | 1.x | Accessible primitives |
| **Styling** | Tailwind CSS | 3.x | Utility-first CSS |
| **Charts** | TradingView Lightweight Charts | 4.x | Financial charts |
| **Charts** | Recharts | 2.x | Data visualization |
| **Forms** | React Hook Form | 7.x | Form validation |
| **HTTP Client** | Axios | 1.x | API requests |

### 10.2 Backend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | FastAPI | 0.104.x | Async web framework |
| **Language** | Python | 3.11+ | Programming language |
| **ASGI Server** | Uvicorn | 0.24.x | Production server |
| **ORM** | SQLAlchemy | 2.0.x | Database ORM |
| **Async DB Driver** | asyncpg | 0.29.x | PostgreSQL async driver |
| **Migrations** | Alembic | 1.12.x | Database migrations |
| **Validation** | Pydantic | 2.x | Data validation |
| **Authentication** | python-jose | 3.3.x | JWT tokens |
| **Password Hashing** | passlib | 1.7.x | bcrypt hashing |
| **Task Queue** | Celery | 5.3.x | Background tasks |
| **Caching** | Redis | 7.x | In-memory cache |

### 10.3 Database

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **RDBMS** | PostgreSQL | 16.x | Primary database |
| **Time-Series** | TimescaleDB | 2.14.x | Time-series extension |
| **Extensions** | pg_trgm | - | Fuzzy text search |
| **Extensions** | uuid-ossp | - | UUID generation |

### 10.4 Data Pipeline

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Orchestration** | Apache Airflow | 2.8.x | Workflow scheduling |
| **Data Processing** | Pandas | 2.x | Data manipulation |
| **Numerical Computing** | NumPy | 1.x | Array operations |

### 10.5 Infrastructure

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Containerization** | Docker | 24.x | Application packaging |
| **Container Orchestration** | Kubernetes | 1.29.x | Production orchestration |
| **Reverse Proxy** | NGINX | 1.25.x | Load balancing, SSL |
| **Monitoring** | Prometheus | 2.x | Metrics collection |
| **Visualization** | Grafana | 10.x | Dashboards |
| **Logging** | ELK Stack | 8.x | Log aggregation |
| **CI/CD** | GitHub Actions | - | Automated deployments |

---

## 11. Documentation Architecture

This section describes the technical architecture of the unified documentation system that consolidates all project documentation (API references, user guides, architecture docs, specifications) into a single, searchable platform.

### 11.1 Documentation Platform Overview

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Documentation Platform                   │
│                      (docs.screener.kr)                      │
└────────────────┬────────────────────────────────────────────┘
                 │
     ┌───────────┴────────────┬──────────────┬──────────────┐
     │                        │              │              │
     ▼                        ▼              ▼              ▼
┌──────────┐          ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Docusaurus│          │  Sphinx  │   │ TypeDoc  │   │ FastAPI  │
│  (Main    │          │ (Python  │   │(TypeScript│   │ OpenAPI  │
│ Platform) │          │  Docs)   │   │  Docs)   │   │   Docs   │
└─────┬─────┘          └─────┬────┘   └────┬─────┘   └────┬─────┘
      │                      │              │              │
      │  ┌───────────────────┴──────────────┴──────────────┘
      │  │
      ▼  ▼
┌────────────────────────────────────────────────────────────┐
│              Source Documentation Files                     │
├────────────────────────────────────────────────────────────┤
│ • Markdown Files (guides, architecture)                    │
│ • Python Docstrings (backend code)                         │
│ • TSDoc Comments (frontend code)                           │
│ • OpenAPI Spec (REST API)                                  │
└────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│                  Build Process (CI/CD)                      │
├────────────────────────────────────────────────────────────┤
│ 1. Build Sphinx Python docs                                │
│ 2. Build TypeDoc TypeScript docs                           │
│ 3. Build Docusaurus site (integrate Sphinx + TypeDoc)      │
│ 4. Check links, run Lighthouse audit                       │
│ 5. Deploy to CDN                                            │
└────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│                  Hosting & Delivery                         │
├────────────────────────────────────────────────────────────┤
│ • CDN: Global edge distribution                            │
│ • SSL: Auto-managed HTTPS                                  │
│ • Search: Algolia DocSearch                                │
│ • Analytics: Plausible/Google Analytics                    │
└────────────────────────────────────────────────────────────┘
```

### 12.2 Component Architecture

#### 12.2.1 Docusaurus (Main Platform)

**Technology**: Docusaurus 3.x (React-based static site generator)

**Responsibilities**:
- Serve as the main documentation platform
- Aggregate content from multiple sources (Markdown, Sphinx, TypeDoc)
- Provide navigation, search, and versioning
- Generate static HTML for deployment

**Configuration** (`docusaurus.config.js`):
```javascript
module.exports = {
  title: 'Screener Platform Documentation',
  tagline: 'Comprehensive docs for developers and users',
  url: 'https://docs.screener.kr',
  baseUrl: '/',

  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/kcenon/screener_system/edit/main/docs/',
        },
        blog: {
          showReadingTime: true,
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'api',
        path: 'api',
        routeBasePath: 'api',
        sidebarPath: require.resolve('./sidebarsApi.js'),
      },
    ],
    [
      'docusaurus-plugin-typedoc',
      {
        entryPoints: ['../frontend/src'],
        tsconfig: '../frontend/tsconfig.json',
        out: 'api/frontend',
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Screener Docs',
      items: [
        { to: 'docs/getting-started', label: 'Docs', position: 'left' },
        { to: 'api/backend', label: 'API Reference', position: 'left' },
        { href: 'https://github.com/kcenon/screener_system', label: 'GitHub', position: 'right' },
      ],
    },
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_API_KEY',
      indexName: 'screener_docs',
    },
  },
};
```

**Directory Structure**:
```
docs-site/
├── docs/                      # Main documentation
│   ├── 01-getting-started/
│   ├── 02-guides/
│   ├── 03-api-reference/
│   ├── 04-architecture/
│   ├── 05-specifications/
│   └── 06-operations/
├── api/                       # Auto-generated API docs
│   ├── backend/               # From Sphinx
│   └── frontend/              # From TypeDoc
├── blog/                      # Release notes, updates
├── src/                       # Custom React components
├── static/                    # Static assets (images, diagrams)
├── docusaurus.config.js
├── sidebars.js
└── package.json
```

#### 12.2.2 Sphinx (Python Documentation)

**Technology**: Sphinx 7.x with autodoc extension

**Responsibilities**:
- Auto-generate Python API documentation from docstrings
- Support Google-style docstrings
- Generate cross-references and type hints
- Export to HTML for integration with Docusaurus

**Configuration** (`conf.py`):
```python
import os
import sys
sys.path.insert(0, os.path.abspath('../../backend'))

project = 'Screener Backend API'
author = 'Engineering Team'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
]

# Napoleon settings (Google style)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'member-order': 'bysource',
}

# HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
```

**Output**: HTML documentation in `api/backend/`

#### 12.2.3 TypeDoc (TypeScript Documentation)

**Technology**: TypeDoc 0.25.x

**Responsibilities**:
- Auto-generate TypeScript/React component documentation
- Extract TSDoc comments from source code
- Generate props tables for React components
- Export to Markdown for Docusaurus integration

**Configuration** (`typedoc.json`):
```json
{
  "entryPoints": ["../frontend/src"],
  "out": "api/frontend",
  "plugin": ["typedoc-plugin-markdown"],
  "excludePrivate": true,
  "excludeProtected": true,
  "categorizeByGroup": true,
  "categoryOrder": [
    "Components",
    "Hooks",
    "Services",
    "Store",
    "Types",
    "*"
  ],
  "readme": "none",
  "githubPages": false
}
```

**Output**: Markdown files in `api/frontend/`

#### 12.2.4 FastAPI OpenAPI Documentation

**Technology**: FastAPI's built-in Swagger UI and ReDoc

**Responsibilities**:
- Auto-generate REST API documentation from route definitions
- Provide interactive API playground
- Export OpenAPI 3.0 specification

**Access**:
- Swagger UI: `https://api.screener.kr/docs`
- ReDoc: `https://api.screener.kr/redoc`
- OpenAPI JSON: `https://api.screener.kr/openapi.json`

**Integration with Docusaurus**:
- Link to live API docs from main documentation
- Embed OpenAPI spec for offline viewing (optional)

### 12.3 Build & Deployment Pipeline

#### 12.3.1 GitHub Actions Workflow

**File**: `.github/workflows/docs.yml`

```yaml
name: Deploy Documentation to GitHub Pages

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'frontend/src/**'
      - 'backend/app/**'
      - 'docs-site/**'

jobs:
  deploy:
    runs-on: ubuntu-latest

    permissions:
      contents: write  # Required for gh-pages deployment

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: 'docs-site/package-lock.json'

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Python dependencies
        run: |
          pip install -r requirements-docs.txt

      - name: Build Sphinx docs
        run: |
          cd docs/api/python
          sphinx-build -b html . ../../_build/api/backend

      - name: Build TypeDoc documentation
        run: |
          cd docs-site
          npm ci
          npx typedoc

      - name: Build Docusaurus site
        run: |
          cd docs-site
          npm run build
        env:
          NODE_ENV: production

      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs-site/build
          cname: docs.screener.kr
          user_name: 'github-actions[bot]'
          user_email: 'github-actions[bot]@users.noreply.github.com'
          commit_message: 'docs: deploy documentation [skip ci]'
```

#### 12.3.2 Build Performance

**Target**: < 3 minutes total build time

**Optimizations**:
- Parallel builds (Sphinx, TypeDoc, Docusaurus)
- Incremental builds (only rebuild changed files)
- Caching dependencies (npm cache, pip cache)

### 12.4 Search Architecture

#### Algolia DocSearch Integration

**Implementation**:
```javascript
// docusaurus.config.js
themeConfig: {
  algolia: {
    appId: 'SCREENER_DOCS',
    apiKey: 'search-only-api-key',
    indexName: 'screener_platform',
    contextualSearch: true,
    searchPagePath: 'search',
  },
}
```

**Indexing Strategy**:
- Automatic re-indexing on every deployment
- Index all documentation content (headings, paragraphs, code)
- Custom ranking: Getting Started > API Reference > Architecture

**Search Quality Metrics**:
- Average click position: < 3
- % queries with clicks: > 90%
- % queries with no results: < 5%

### 12.5 Versioning Strategy

**Approach**: Maintain documentation for current version + 2 previous major versions

**Implementation**:
```bash
# Create new version
npm run docusaurus docs:version 1.0

# Directory structure
docs-site/
├── docs/              # Current (unreleased) docs
├── versioned_docs/
│   ├── version-1.0/
│   └── version-0.9/
└── versions.json      # ["1.0", "0.9"]
```

**Version Selector**: Dropdown in navbar to switch between versions

### 12.6 Analytics & Monitoring

#### Page Analytics

**Tool**: Plausible Analytics (privacy-friendly)

**Metrics Tracked**:
- Page views
- Most visited pages
- Search queries
- Time on page
- Bounce rate

**Goals**:
- Track documentation usage patterns
- Identify missing or unclear content
- Prioritize documentation improvements

#### Documentation Health Dashboard

**Metrics**:
- Documentation coverage (% APIs documented)
- Broken link count
- Build success rate
- Average build time
- Search quality metrics

**Tools**:
- Custom dashboard (Grafana + Prometheus)
- Weekly reports via email

### 12.7 Security Considerations

**Content Security Policy**:
```javascript
// docusaurus.config.js
scripts: [
  {
    src: 'https://plausible.io/js/script.js',
    defer: true,
    'data-domain': 'docs.screener.kr',
  },
],
```

**Access Control**:
- Documentation site is public (no authentication required)
- Admin features (analytics, search config) require authentication
- Source code access via GitHub (public repository)

**HTTPS Enforcement**:
- All traffic redirected to HTTPS
- SSL certificate auto-managed by hosting platform
- HSTS header enabled

---

## 12. Design Decisions

### 12.1 Key Architectural Decisions

#### 12.1.1 Monolith vs Microservices

**Decision**: Start with **Modular Monolith**, design for future microservices split.

**Rationale**:
- **Pros**:
  - Simpler deployment and operations
  - Faster development velocity (no inter-service communication overhead)
  - Easier debugging and testing
  - Lower infrastructure costs
- **Cons**:
  - Scaling limitations (must scale entire application)
  - Tighter coupling

**Future Migration Path**:
- Module boundaries are clear (stock, user, portfolio, alert)
- Each module has independent database tables
- API versioning allows gradual service extraction

#### 12.1.2 PostgreSQL + TimescaleDB vs Specialized Time-Series DB

**Decision**: Use **TimescaleDB** (PostgreSQL extension).

**Rationale**:
- **Pros**:
  - Single database for relational + time-series data
  - Full SQL support (no learning new query language)
  - ACID compliance for all data
  - Excellent compression (10x for time-series data)
- **Cons**:
  - Not as optimized as pure time-series databases (InfluxDB, Prometheus)

**Why not InfluxDB/Prometheus**:
- Need relational data (users, portfolios)
- TimescaleDB compression is sufficient for our scale
- Simpler operations (one database)

#### 12.1.3 Server-Side Rendering (SSR) vs Client-Side Rendering (CSR)

**Decision**: Use **Client-Side Rendering** (React SPA).

**Rationale**:
- **Pros**:
  - Better user experience (instant navigation)
  - API-first architecture (enables mobile app later)
  - Lower server load
- **Cons**:
  - SEO challenges (mitigated with static landing pages)
  - Slower initial page load

**Why not Next.js (SSR)**:
- Application is behind authentication (SEO not critical)
- API-first approach is priority
- Simpler deployment

#### 12.1.4 JWT vs Session-Based Authentication

**Decision**: Use **JWT tokens** (stateless).

**Rationale**:
- **Pros**:
  - Stateless (no server-side session storage)
  - Scalable (no session affinity needed)
  - Works across multiple servers
  - Mobile-friendly
- **Cons**:
  - Cannot revoke access tokens before expiry (mitigated with short expiry)
  - Larger request size (token in header)

**Implementation**:
- Short-lived access tokens (15 minutes)
- Long-lived refresh tokens (30 days, revocable)

#### 12.1.5 Materialized Views vs Real-Time Aggregation

**Decision**: Use **Materialized Views** for screening.

**Rationale**:
- Screening queries are complex (join stocks, prices, indicators)
- Real-time aggregation would be too slow
- Data updates once per day (materialized views are perfect fit)

**Refresh Strategy**:
- Refresh after indicator calculation DAG completes
- CONCURRENTLY to avoid locking

### 12.2 Database Design Decisions

#### 12.2.1 Integer Prices vs Decimal/Float

**Decision**: Store prices as **INTEGER** (KRW, no decimals).

**Rationale**:
- Korean stocks trade in whole KRW amounts (no cents)
- Avoids floating-point precision issues
- Faster arithmetic and comparisons
- Smaller storage size

#### 12.2.2 Composite Primary Key vs Surrogate Key

**Decision**: Use **Composite PRIMARY KEY** for daily_prices.

```sql
PRIMARY KEY (stock_code, trade_date)
```

**Rationale**:
- Natural key is available (stock_code + date)
- No need for surrogate UUID/SERIAL
- Clearer semantics
- Smaller index size

#### 12.2.3 NULL Handling for Optional Indicators

**Decision**: Allow **NULL** values for indicators that cannot be calculated.

**Example**: `per` is NULL if company has negative earnings.

**Rationale**:
- NULL has semantic meaning ("not applicable" vs "zero")
- Avoids magic values (-1, 0, etc.)
- Database can optimize NULL handling

**Query Implications**:
```sql
-- Filter by PER, excluding NULL values
WHERE per BETWEEN 0 AND 15
  AND per IS NOT NULL  -- Explicit NULL handling
```

### 12.3 API Design Decisions

#### 12.3.1 REST vs GraphQL

**Decision**: Use **REST API**.

**Rationale**:
- Simpler to implement and understand
- Better caching (HTTP caching standards)
- OpenAPI documentation tools
- Sufficient for our use case

**Why not GraphQL**:
- No complex nested queries needed
- Over-fetching not a major issue
- Adds complexity

#### 12.3.2 Versioning Strategy

**Decision**: **URL Path Versioning** (`/v1/`, `/v2/`).

**Alternatives Considered**:
- Header versioning (`Accept: application/vnd.api.v1+json`)
- Query parameter (`?version=1`)

**Rationale**:
- Most visible and intuitive
- Easy to test (just change URL)
- Industry standard (Stripe, GitHub)

---

## 13. Appendices

### 12.1 Glossary

| Term | Definition |
|------|------------|
| **OHLCV** | Open, High, Low, Close, Volume - standard format for price data |
| **PER** | Price-to-Earnings Ratio - valuation metric |
| **PBR** | Price-to-Book Ratio - valuation metric |
| **ROE** | Return on Equity - profitability metric |
| **Hypertable** | TimescaleDB's abstraction for time-series tables |
| **Materialized View** | Pre-computed query results stored as a table |
| **Continuous Aggregate** | TimescaleDB feature for real-time aggregated views |
| **DAG** | Directed Acyclic Graph - Airflow workflow definition |

### 12.2 Acronyms

| Acronym | Full Form |
|---------|-----------|
| **API** | Application Programming Interface |
| **JWT** | JSON Web Token |
| **CORS** | Cross-Origin Resource Sharing |
| **CSRF** | Cross-Site Request Forgery |
| **XSS** | Cross-Site Scripting |
| **SPA** | Single Page Application |
| **ORM** | Object-Relational Mapping |
| **ACID** | Atomicity, Consistency, Isolation, Durability |
| **TTL** | Time To Live |
| **HPA** | Horizontal Pod Autoscaler |
| **APM** | Application Performance Monitoring |
| **RUM** | Real User Monitoring |

### 12.3 External Dependencies

**Production Dependencies**:

```python
# backend/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.12.1
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis[hiredis]==5.0.1
celery[redis]==5.3.4
pandas==2.1.3
numpy==1.26.2
```

```json
// frontend/package.json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@tanstack/react-query": "^5.12.0",
    "zustand": "^4.4.7",
    "axios": "^1.6.2",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "tailwindcss": "^3.3.6",
    "lightweight-charts": "^4.1.1",
    "recharts": "^2.10.3",
    "react-hook-form": "^7.48.2",
    "date-fns": "^2.30.0"
  }
}
```

### 12.4 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/16/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [React Documentation](https://react.dev/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

### 12.5 Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-09 | Architecture Team | Initial SDS document |

---

**END OF DOCUMENT**