---
id: srs-nonfunctional-other
title: SRS - Non-Functional & Other
description: Non-functional requirements, legal requirements, and appendices
sidebar_label: Non-Functional
sidebar_position: 3
tags:
  - specification
  - requirements
  - software
---

:::info Navigation
- [Introduction](introduction.md)
- [Requirements](requirements.md)
- [Non-Functional](nonfunctional-other.md) (Current)
:::

# Software Requirements Specification - Non-Functional

## 6. Non-Functional Requirements

### 6.1 Performance Requirements

**PERF-001: API Response Time**
- **Requirement**: 95th percentile API response time < 200ms
- **Measurement**: Application Performance Monitoring (Sentry APM)
- **Rationale**: Ensure responsive user experience

**PERF-002: Screening Query Time**
- **Requirement**: 99th percentile screening query < 500ms
- **Measurement**: Database query logging + APM
- **Rationale**: Core feature must feel instant

**PERF-003: Page Load Time**
- **Requirement**: 95th percentile page load (First Contentful Paint) < 1.5s
- **Measurement**: Real User Monitoring (RUM), Lighthouse CI
- **Rationale**: Industry standard for good user experience

**PERF-004: Chart Rendering**
- **Requirement**: Render 1 year of daily data (252 points) in < 1 second
- **Measurement**: Frontend performance profiling
- **Rationale**: Charts are frequently used, must be fast

**PERF-005: Concurrent Users**
- **Requirement**: Support 10,000 concurrent users without degradation
- **Measurement**: Load testing (k6), production monitoring
- **Rationale**: Ensure scalability for user growth

**PERF-006: Database Query Optimization**
- **Requirement**: No database query exceeds 1 second execution time
- **Measurement**: Slow query log, pg_stat_statements
- **Rationale**: Prevent database from becoming bottleneck

**PERF-007: Cache Hit Rate**
- **Requirement**: Redis cache hit rate > 80%
- **Measurement**: Redis INFO stats
- **Rationale**: Reduce database load and improve response time

**PERF-008: Rate Limiting**
- **Requirement**: Enforce tiered rate limits without performance degradation
  - Free tier: 100 requests/hour
  - Basic tier: 1000 requests/hour
  - Premium tier: 10000 requests/hour
- **Measurement**: Rate limiter overhead < 5ms per request
- **Rationale**: Protect API from abuse while maintaining performance

**PERF-009: WebSocket Real-time Updates**
- **Requirement**: WebSocket message latency < 100ms (p99)
- **Concurrent Connections**: Support 10,000+ simultaneous WebSocket connections
- **Message Delivery**: 99.9% message delivery rate
- **Measurement**: WebSocket latency monitoring, connection count metrics
- **Rationale**: Enable true real-time user experience for stock price updates

### 6.2 Safety Requirements

**SAFE-001: Data Backup**
- **Requirement**: Daily automated backups with 30-day retention
- **Verification**: Restore test monthly
- **Rationale**: Protect against data loss

**SAFE-002: Disaster Recovery**
- **Requirement**: Recovery Time Objective (RTO) < 4 hours, Recovery Point Objective (RPO) < 1 hour
- **Implementation**: Database replication, automated failover
- **Rationale**: Minimize downtime and data loss

**SAFE-003: Graceful Degradation**
- **Requirement**: System remains operational with degraded functionality if non-critical services fail
- **Example**: Screening works even if alerts service is down
- **Rationale**: Maximize availability of core features

### 6.3 Security Requirements

**SEC-001: Authentication**
- **Requirement**: Use JWT with 15-minute access token expiry, 30-day refresh token
- **Implementation**: bcrypt password hashing (cost 12), secure token storage
- **Rationale**: Industry best practice for web authentication

**SEC-002: Authorization**
- **Requirement**: Enforce role-based access control (RBAC) on all protected resources
- **Implementation**: Middleware checks subscription tier before feature access
- **Rationale**: Prevent unauthorized access to premium features

**SEC-003: Data Encryption**
- **Requirement**:
  - Encrypt all data in transit (TLS 1.3)
  - Encrypt PII at rest (AES-256)
- **Implementation**: HTTPS only, database column encryption for sensitive fields
- **Rationale**: Comply with GDPR/PIPA, protect user data

**SEC-004: SQL Injection Prevention**
- **Requirement**: Use parameterized queries or ORM for all database operations
- **Implementation**: SQLAlchemy ORM, never concatenate user input into SQL
- **Rationale**: Prevent SQL injection attacks

**SEC-005: XSS Prevention**
- **Requirement**: Sanitize all user inputs, escape outputs, use Content Security Policy (CSP)
- **Implementation**: React auto-escaping, CSP headers
- **Rationale**: Prevent cross-site scripting attacks

**SEC-006: CSRF Protection**
- **Requirement**: Use SameSite cookies, CSRF tokens for state-changing operations
- **Implementation**: SameSite=Strict for session cookies
- **Rationale**: Prevent cross-site request forgery

**SEC-007: Rate Limiting**
- **Requirement**: Enforce rate limits per user and per IP
  - Free: 100 req/min
  - Basic: 500 req/min
  - Pro: 2000 req/min
- **Implementation**: Redis-based rate limiter
- **Rationale**: Prevent API abuse and DDoS attacks

**SEC-008: Dependency Scanning**
- **Requirement**: Scan dependencies weekly for vulnerabilities, apply patches within 7 days
- **Implementation**: Dependabot, npm audit, safety (Python)
- **Rationale**: Prevent exploitation of known vulnerabilities

**SEC-009: Audit Logging**
- **Requirement**: Log all security-relevant events (logins, permission changes, data access)
- **Implementation**: Write to user_activity_log table
- **Rationale**: Enable forensic analysis and compliance audits

### 6.4 Software Quality Attributes

**QUAL-001: Reliability (Availability)**
- **Target**: 99.9% uptime (< 8.76 hours downtime per year)
- **Measurement**: Uptime monitoring (UptimeRobot), incident tracking
- **Strategies**: Redundant servers, automated failover, health checks

**QUAL-002: Reliability (Error Rate)**
- **Target**: < 0.1% error rate for all API requests
- **Measurement**: Error tracking (Sentry)
- **Strategies**: Comprehensive error handling, retry logic, circuit breakers

**QUAL-003: Maintainability (Code Quality)**
- **Target**: SonarQube quality gate pass (A rating)
- **Metrics**: Code smells < 50, duplicated lines < 5%, cognitive complexity < 15
- **Strategies**: Code reviews, linting, static analysis

**QUAL-004: Maintainability (Documentation)**
- **Target**: All public APIs documented with OpenAPI, all functions have docstrings
- **Verification**: Documentation coverage > 90%
- **Strategies**: Automated doc generation, documentation as code

**QUAL-005: Maintainability (Test Coverage)**
- **Target**: > 80% unit test coverage for backend, > 70% for frontend
- **Measurement**: Coverage reports (pytest-cov, vitest)
- **Strategies**: Test-driven development (TDD), CI/CD pipeline enforcement

**QUAL-006: Usability (Learnability)**
- **Target**: New users can complete first screening within 2 minutes
- **Measurement**: User testing, onboarding analytics
- **Strategies**: Guided tutorial, pre-built templates, tooltips

**QUAL-007: Usability (Error Handling)**
- **Target**: All errors have clear, actionable messages
- **Example**: "Invalid email format" instead of "400 Bad Request"
- **Verification**: Manual review of all error messages

**QUAL-008: Portability**
- **Target**: Run on any Linux distribution with Docker support
- **Implementation**: Container-based architecture
- **Rationale**: Avoid vendor lock-in

**QUAL-009: Scalability (Horizontal)**
- **Target**: Support horizontal scaling of API servers, workers
- **Implementation**: Stateless architecture, load balancer
- **Rationale**: Handle traffic growth without code changes

**QUAL-010: Scalability (Vertical)**
- **Target**: Optimize for efficient resource usage (CPU, memory)
- **Metrics**: < 500MB memory per API instance, < 50% CPU under normal load
- **Strategies**: Profiling, query optimization, caching

---

### 6.5 Documentation Requirements

This section defines requirements for technical documentation, API documentation, user documentation, and documentation infrastructure to ensure comprehensive knowledge transfer and system maintainability.

#### 6.5.1 Documentation Platform

**DOC-001: Unified Documentation Platform**
- **Requirement**: Implement a unified documentation platform that consolidates all project documentation (user guides, API references, architecture docs, specifications)
- **Technology**: Docusaurus (React-based static site generator)
- **Rationale**:
  - Single source of truth for all documentation
  - Modern, searchable, mobile-friendly interface
  - Support for versioning
  - Easy contribution via Markdown
- **Implementation**: Deploy to `docs.screener.kr` with CDN
- **Priority**: High
- **Verification**: Documentation site accessible and all existing docs migrated

**DOC-002: Documentation Auto-Generation**
- **Requirement**: API documentation must be auto-generated from source code
- **Python Backend**: Use Sphinx + autodoc to generate docs from docstrings
- **TypeScript Frontend**: Use TypeDoc to generate docs from TSDoc comments
- **REST API**: Use FastAPI's built-in OpenAPI documentation
- **Rationale**: Ensure documentation stays synchronized with code
- **Verification**:
  - Run `sphinx-build` and verify HTML output
  - Run `typedoc` and verify TypeScript docs
  - Access `/docs` and `/redoc` endpoints for API docs

**DOC-003: Documentation Build in CI/CD**
- **Requirement**: Documentation must build and deploy automatically on every commit to main branch
- **Implementation**: GitHub Actions workflow
- **Steps**:
  1. Build Python docs (Sphinx)
  2. Build TypeScript docs (TypeDoc)
  3. Build documentation site (Docusaurus)
  4. Check for broken links
  5. Deploy to hosting platform
- **Success Criteria**: Build completes in < 5 minutes
- **Verification**: Check CI/CD pipeline status after commit

#### 6.5.2 API Documentation Requirements

**DOC-004: REST API Documentation**
- **Requirement**: All REST API endpoints must be documented in OpenAPI 3.0 format
- **Required Fields**:
  - Operation summary and description
  - Request parameters (query, path, body)
  - Response schemas (success and error)
  - Authentication requirements
  - Rate limiting info
  - Example requests/responses
- **Accessibility**: Interactive API documentation available at `/docs` (Swagger UI) and `/redoc` (ReDoc)
- **Verification**: All endpoints appear in `/docs` with complete information

**DOC-005: Python API Documentation**
- **Requirement**: All public Python functions, classes, and methods must have docstrings
- **Format**: Google style docstrings
- **Required Sections**: Description, Args, Returns, Raises, Example (for complex functions)
- **Coverage Target**: > 90% of public APIs documented
- **Verification**: Run `sphinx-build` and check documentation coverage report

**DOC-006: TypeScript API Documentation**
- **Requirement**: All exported React components, hooks, and utilities must have TSDoc comments
- **Required Information**:
  - Component description and purpose
  - Props documentation
  - Usage examples
  - Return types for hooks
- **Coverage Target**: > 80% of exported symbols documented
- **Verification**: Run `typedoc` and review generated documentation

**DOC-007: WebSocket API Documentation**
- **Requirement**: WebSocket API must be fully documented including:
  - Connection establishment
  - Message formats (subscribe, unsubscribe, data updates)
  - Error handling
  - Connection limits and rate limits
- **Format**: Dedicated Markdown documentation
- **Location**: `docs/api-reference/websocket-api.md`
- **Verification**: Documentation includes complete protocol specification

#### 6.5.3 User Documentation Requirements

**DOC-008: Getting Started Guide**
- **Requirement**: Provide comprehensive getting started guide for new users
- **Contents**:
  - System requirements
  - Installation instructions (local dev and Docker)
  - First-time setup
  - Quick tutorial (create first screening)
- **Format**: Step-by-step with screenshots
- **Location**: `docs/getting-started/`
- **Verification**: New developer can set up system in < 30 minutes following guide

**DOC-009: User Feature Guides**
- **Requirement**: Document all major user-facing features
- **Required Guides**:
  - Stock screening (filters, indicators, results)
  - Stock detail pages
  - Portfolio management
  - Price alerts
  - Real-time updates (WebSocket)
- **Format**: Task-oriented guides with screenshots
- **Location**: `docs/guides/user-guides/`
- **Verification**: Each feature has corresponding guide

**DOC-010: Developer Guides**
- **Requirement**: Provide development guides for contributors
- **Required Topics**:
  - Local development setup
  - Testing strategy and running tests
  - Debugging techniques
  - Code review process
  - Git workflow
  - Documentation contribution guidelines
- **Location**: `docs/guides/developer-guides/`
- **Verification**: Covers all aspects of development workflow

#### 6.5.4 Architecture Documentation Requirements

**DOC-011: System Architecture**
- **Requirement**: Maintain comprehensive architecture documentation
- **Required Diagrams**:
  - High-level system architecture
  - Component interaction diagram
  - Database schema (ER diagram)
  - Data flow diagrams
  - Deployment architecture
- **Format**: Markdown with embedded diagrams (Mermaid or images)
- **Location**: `docs/architecture/`
- **Update Frequency**: On any architecture change
- **Verification**: Diagrams accurately reflect current system

**DOC-012: Database Schema Documentation**
- **Requirement**: Document all database tables, columns, indexes, and relationships
- **Auto-generation**: Use SchemaSpy or similar tool to generate from live database
- **Required Information**:
  - Table descriptions and purpose
  - Column types and constraints
  - Foreign key relationships
  - Indexes and their purpose
- **Location**: `docs/architecture/database-schema.md`
- **Verification**: All tables and columns documented

**DOC-013: Data Pipeline Documentation**
- **Requirement**: Document all Airflow DAGs and data workflows
- **Required Information**:
  - DAG purpose and schedule
  - Task dependencies
  - Data sources and destinations
  - Error handling and retry logic
- **Location**: `docs/architecture/data-pipeline.md`
- **Verification**: All DAGs have corresponding documentation

#### 6.5.5 Documentation Quality Requirements

**DOC-014: Documentation Standards**
- **Requirement**: Establish and enforce documentation standards
- **Standards Include**:
  - Writing style guide (tone, voice, terminology)
  - Code example formatting
  - Screenshot guidelines
  - Markdown linting rules
- **Implementation**:
  - Create `docs/contributing/documentation-style-guide.md`
  - Configure markdownlint
  - Add documentation checklist to PR template
- **Verification**: All new documentation passes linting checks

**DOC-015: Link Validation**
- **Requirement**: All internal and external links in documentation must be valid
- **Implementation**: Automated link checking in CI/CD pipeline
- **Frequency**: On every PR and daily scheduled check
- **Action on Failure**: Block PR merge if broken internal links found
- **Verification**: Link check reports zero broken links

**DOC-016: Documentation Search**
- **Requirement**: Documentation platform must have functional search capability
- **Implementation**: Algolia DocSearch integration
- **Search Quality**: > 90% of queries return relevant results
- **Verification**: Manual testing of common search queries

**DOC-017: Documentation Accessibility**
- **Requirement**: Documentation must be accessible and mobile-friendly
- **Standards**:
  - WCAG 2.1 Level AA compliance
  - Responsive design (works on mobile, tablet, desktop)
  - Lighthouse accessibility score > 90
- **Verification**: Run Lighthouse audit on documentation site

**DOC-018: Documentation Versioning**
- **Requirement**: Support multiple documentation versions aligned with software releases
- **Implementation**: Docusaurus versioning feature
- **Retention**: Maintain docs for current version + 2 previous major versions
- **Verification**: Version selector works, old versions remain accessible

#### 6.5.6 Documentation Maintenance Requirements

**DOC-019: Documentation Updates**
- **Requirement**: Documentation must be updated whenever related code changes
- **Process**:
  - PRs that change public APIs must update corresponding docs
  - Documentation review required before merge
  - Breaking changes must update migration guide
- **Enforcement**: PR checklist includes documentation update confirmation
- **Verification**: No API changes without documentation updates

**DOC-020: Documentation Coverage Tracking**
- **Requirement**: Track and report documentation coverage metrics
- **Metrics**:
  - % of public APIs with docstrings/TSDoc
  - % of user features with guides
  - % of architecture components documented
- **Reporting**: Weekly dashboard showing coverage trends
- **Target**: Maintain > 80% overall coverage
- **Verification**: Coverage metrics available in CI/CD dashboard

**DOC-021: Documentation Review Process**
- **Requirement**: All documentation changes must be reviewed
- **Reviewers**: At least one reviewer with domain knowledge
- **Review Criteria**:
  - Technical accuracy
  - Clarity and completeness
  - Adherence to style guide
  - Working code examples
- **Verification**: PR approval required from documentation reviewer

#### 6.5.7 Documentation Hosting Requirements

**DOC-022: GitHub Pages Hosting**
- **Requirement**: Documentation site must be publicly accessible via GitHub Pages
- **Platform**: GitHub Pages (mandatory)
- **Rationale**:
  - Free and unlimited for public repositories
  - Integrated with GitHub Actions
  - Simple configuration
  - No third-party dependencies
  - GitHub's infrastructure SLA
- **Configuration**:
  - **Primary URL**: `https://docs.screener.kr` (custom domain with CNAME)
  - **Fallback URL**: `https://kcenon.github.io/screener_system/`
  - **Deployment Branch**: `gh-pages` (auto-created by GitHub Actions)
  - **HTTPS**: Enforced with auto-managed SSL certificate
  - **CDN**: GitHub's global CDN (Fastly-backed)
- **Requirements**:
  - HTTPS enforced (SSL certificate auto-renewal)
  - Page load time < 1 second (P95)
  - DNS configured with CNAME record
  - GitHub Actions workflow deploys on main branch push
- **Verification**:
  - Access `https://docs.screener.kr` (200 OK)
  - Verify SSL certificate validity
  - Check Lighthouse performance score > 90
  - Confirm automatic deployment from CI/CD

**DOC-023: Documentation Deployment Automation**
- **Requirement**: Documentation must deploy automatically on every commit to main branch
- **Implementation**: GitHub Actions workflow with peaceiris/actions-gh-pages
- **Workflow Triggers**:
  - Push to main branch (paths: docs/**, frontend/src/**, backend/app/**)
  - Manual workflow dispatch (for emergency rebuilds)
- **Deployment Process**:
  1. Build Sphinx Python documentation
  2. Build TypeDoc TypeScript documentation
  3. Build Docusaurus main site
  4. Deploy to gh-pages branch
  5. GitHub Pages serves from gh-pages branch
- **Success Criteria**:
  - Build completes in < 3 minutes
  - Zero deployment failures (auto-retry on transient errors)
  - GitHub Actions deployment status visible in repository
- **Verification**:
  - Check GitHub Actions workflow runs successfully
  - Verify deployment appears in repository's Environments tab
  - Confirm updated content visible on live site within 5 minutes

---

## 7. Other Requirements

### 7.1 Legal Requirements

**LEGAL-001: Data Licensing Compliance**
- **Requirement**: Display KRX and F&Guide data attribution as required by license agreements
- **Implementation**: Footer with "Data provided by KRX and F&Guide" on all pages
- **Penalty**: License termination if violated

**LEGAL-002: Investment Disclaimer**
- **Requirement**: Display investment disclaimer on all pages with financial data
- **Text**: "The information provided is for reference only and does not constitute investment advice. Screener Platform is not responsible for investment losses resulting from use of this service."
- **Placement**: Footer or prominent notice

**LEGAL-003: Privacy Policy**
- **Requirement**: Comply with GDPR (if serving EU users) and PIPA (Korea)
- **Implementation**:
  - Obtain consent for data collection
  - Allow users to export/delete their data
  - Encrypt PII
  - Privacy policy page linked in footer

**LEGAL-004: Terms of Service**
- **Requirement**: Users must agree to ToS before registration
- **Contents**: Service scope, user obligations, limitation of liability, dispute resolution
- **Implementation**: Checkbox during registration

**LEGAL-005: Cookie Consent**
- **Requirement**: Obtain consent for non-essential cookies (if applicable)
- **Implementation**: Cookie banner on first visit
- **Rationale**: EU Cookie Law compliance

### 7.2 Regulatory Requirements

**REG-001: Financial Data Restrictions**
- **Requirement**: Cannot redistribute financial data to third parties
- **Implementation**: Terms of Service prohibit data scraping/resale
- **Rationale**: Comply with data provider agreements

**REG-002: No Investment Advice**
- **Requirement**: System must not provide personalized investment recommendations
- **Implementation**: Generic screening results only, no "buy/sell" signals
- **Rationale**: Avoid financial advisor licensing requirements

**REG-003: Age Restriction**
- **Requirement**: Users must be 18+ to register
- **Implementation**: Age verification during registration
- **Rationale**: Investment-related service

### 7.3 Localization Requirements

**LOC-001: Language**
- **Requirement**: User interface in Korean, code and documentation in English
- **Implementation**: i18n framework (react-i18next), Korean translations
- **Rationale**: Primary market is Korea

**LOC-002: Currency**
- **Requirement**: Display prices in Korean Won (₩), formatted with commas
- **Implementation**: Number formatting utilities
- **Example**: 70000 → ₩70,000

**LOC-003: Date/Time**
- **Requirement**: Display dates in YYYY-MM-DD format, times in KST timezone
- **Implementation**: date-fns with Korea locale
- **Rationale**: Korean market hours (09:00-15:30 KST)

**LOC-004: Number Formatting**
- **Requirement**: Use Korean number formatting (10,000 → 만)
- **Implementation**: Custom formatting function for large numbers
- **Example**: 10억 (1 billion), 조 (trillion)

---

## 8. Appendices

### Appendix A: Requirement Traceability Matrix

| Requirement ID | PRD Section | Priority | Verification Method |
|----------------|-------------|----------|---------------------|
| REQ-AUTH-001 | 5.2.5 | Critical | Unit test, E2E test |
| REQ-STOCK-001 | 5.2.1 | Critical | Integration test |
| REQ-SCREEN-001 | 5.2.2 | Critical | Performance test, E2E test |
| REQ-MARKET-001 | 5.2.3 | High | Integration test |
| REQ-PORT-001 | 5.2.4 | High | E2E test |
| REQ-ALERT-001 | 5.2.7 | High | Integration test |
| PERF-001 | 6.3 | Critical | Load test, APM monitoring |
| SEC-001 | 6.4 | Critical | Security audit, penetration test |

### Appendix B: Glossary

See Section 1.3

### Appendix C: Analysis Models

**C.1 Use Case Diagram**

```
                  Stock Screening Platform

    ┌──────────┐                           ┌──────────┐
    │  Novice  │                           │  Active  │
    │ Investor │                           │  Trader  │
    └────┬─────┘                           └────┬─────┘
         │                                      │
         │  ┌─────────────────────────────┐    │
         ├──│ Browse Stock List           │────┤
         ├──│ View Stock Details          │────┤
         ├──│ Screen Stocks (Templates)   │────┤
         │  └─────────────────────────────┘    │
         │                                      │
         │  ┌─────────────────────────────┐    │
         │  │ Custom Screening            │────┤
         │  │ Create Alerts               │────┤
         │  │ Manage Portfolio            │────┤
         │  │ Export Data (Premium)       │────┤
         │  └─────────────────────────────┘    │
         │                                      │
    ┌────┴─────┐                           ┌────┴─────┐
    │   User   │                           │  System  │
    │  (Base)  │                           │   Admin  │
    └──────────┘                           └──────────┘
                                                 │
                                  ┌──────────────┴──────────────┐
                                  │ Monitor Data Pipeline       │
                                  │ Manage Users                │
                                  │ View System Health          │
                                  └─────────────────────────────┘
```

**C.2 Entity-Relationship Diagram**

See `database/migrations/01_create_tables.sql` for full schema

**C.3 State Transition Diagram (User Subscription)**

```
           ┌──────┐
    ┌─────→│ Free │
    │      └──┬───┘
    │         │ upgrade
    │         ▼
    │      ┌──────┐
    │  ┌──→│Basic │──┐
    │  │   └──────┘  │ upgrade
    │  │             ▼
    │  │          ┌─────┐
    │  │          │ Pro │
    │  │          └──┬──┘
    │  │             │
    │  │  downgrade  │ cancel
    │  └─────────────┘
    │                │
    └────────────────┘
         (grace period ends)
```

### Appendix D: Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-09 | Engineering Team | Initial SRS creation |

---

**END OF DOCUMENT**