# Kanban Board

This directory contains work tickets for the Stock Screening Platform project, organized in a Kanban-style workflow.

## Directory Structure

```
docs/kanban/
├── backlog/       # Future work, not yet prioritized
├── todo/          # Ready to start, prioritized
├── in_progress/   # Currently being worked on
├── review/        # Completed, awaiting review
├── done/          # Completed and reviewed
└── README.md      # This file
```

## Ticket Categories

Tickets are prefixed by category:

- **DB-XXX**: Database setup and migrations
- **BE-XXX**: Backend API development
- **FE-XXX**: Frontend development
- **DP-XXX**: Data Pipeline (Airflow)
- **INFRA-XXX**: Infrastructure and DevOps
- **BUGFIX-XXX**: Critical bug fixes
- **FEATURE-XXX**: New feature implementations
- **IMPROVEMENT-XXX**: Enhancement of existing features
- **TECH-DEBT-XXX**: Technical debt resolution
- **TEST-XXX**: Testing (future tickets)

## Ticket Format

Each ticket follows this structure:

### Metadata
- Status: TODO | IN_PROGRESS | REVIEW | DONE
- Priority: Critical | High | Medium | Low
- Assignee: Team member or TBD
- Estimated Time: Hours or days
- Sprint: Sprint number (1-3 for MVP)
- Tags: Categorization tags

### Content
- **Description**: What needs to be done
- **Subtasks**: Checklist of specific tasks
- **Acceptance Criteria**: How to verify completion
- **Dependencies**: What this ticket depends on / blocks
- **References**: Related documentation
- **Progress**: Percentage complete
- **Notes**: Additional context

## Sprint Structure (2-Week Cycles)

**Sprint Duration**: 2 weeks each
- **Sprint 1**: Week 1-2 (Foundation)
- **Sprint 2**: Week 3-4 (Core Features)
- **Sprint 3**: Week 5-6 (Polish & Advanced Features)

## Current Ticket Distribution

### ✅ Done (6 tickets)
**Completed and verified**

These tickets have been fully implemented, tested, and reviewed:

**Infrastructure:**
- **INFRA-001**: Docker Compose Development Environment (High, 8h actual) ✅
  - All services configured with health checks
  - Service profiles implemented (default, frontend, monitoring, full)
  - Comprehensive testing scripts created (test_all.sh, monitor.sh)
  - Runtime verified: All 12 tests passing

**Backend:**
- **BE-001**: FastAPI Project Initial Setup (Critical, 8h actual) ✅
  - Complete project structure with async SQLAlchemy 2.0
  - Request logging and rate limiting middleware implemented
  - All health check endpoints verified
  - Runtime tested: Swagger UI, database, Redis connections working

**Database:**
- **DB-001**: PostgreSQL + TimescaleDB Environment Setup (Critical, 6h actual) ✅
  - PostgreSQL 16 with TimescaleDB extension configured
  - Migration structure and initialization scripts created
  - Runtime verified: Database connections, extensions, pooling working

**Critical Fixes:**
- **BUGFIX-001**: Fix Critical Issues from Code Review (Critical, 2h actual) ✅
  - Fixed Redis health check authentication
  - Removed NGINX CORS header duplication
  - Verified backend health check

**Technical Debt:**
- **TECH-DEBT-001**: Update Deprecated Code Patterns (High, 2h actual) ✅
  - Updated Pydantic to v2 syntax
  - Replaced deprecated datetime.utcnow()
  - Implemented structured logging

**New Features:**
- **FEATURE-001**: Implement Missing Middleware (Medium, 3h actual) ✅
  - Implemented request logging middleware with UUID tracking
  - Implemented Redis-based rate limiting middleware
  - Configured tier-based rate limits (100/500/2000 req/min)

**Sprint 1 Progress**: Core infrastructure complete, all services verified, production-ready middleware implemented.

---

### 📋 Todo (Sprint 1 & 2) - 10 tickets
**Ready to start, prioritized**

**Sprint 1 Remaining (7 tickets):**

**Backend (2):**
- BE-002: User Authentication API Implementation (Critical, 12h)
- BE-003: Stock Data API Implementation (Critical, 10h)

**Database (3):**
- DB-002: Database Schema Migration Implementation (Critical, 10h)
- DB-003: Indexes and Materialized Views Creation (High, 8h)
- DB-004: Database Functions and Triggers Implementation (Medium, 10h)

**Frontend (2):**
- FE-001: React + Vite Project Setup (Critical, 6h)
- FE-002: User Authentication UI Implementation (Critical, 10h)

**Data Pipeline (2):**
- DP-001: Apache Airflow Environment Setup (High, 6h)
- DP-002: Daily Price Ingestion DAG Implementation (Critical, 12h)

**Sprint 2 Improvements (3 tickets):**

**Improvements:**
- **IMPROVEMENT-001**: Rate Limiting Enhancements (Medium, 4h)
  - Atomic Redis operations (prevent race conditions)
  - Externalize configuration (TTL, whitelist paths)

**Technical Debt:**
- **TECH-DEBT-002**: Resolve Logging Circular Import Risk (Medium, 2h)
  - Restructure logging module dependencies
  - Choose: lazy import / dependency injection / env access

- **TECH-DEBT-003**: Database Session Cleanup (Low, 2h)
  - Remove auto-commit behavior
  - Remove SQLite support code
  - Implement explicit transaction management

**Sprint 1 Remaining Total**: 74 hours (~9 person-days)
**Sprint 2 Improvements Total**: 8 hours (~1 person-day)

**Sprint 1 Goals** (Updated):
- ✅ Docker environment operational (DONE - INFRA-001)
- ✅ Backend API foundation complete (DONE - BE-001)
- ✅ Database environment ready (DONE - DB-001)
- ✅ Critical bugs fixed (DONE - BUGFIX-001)
- ✅ Production-ready middleware (DONE - FEATURE-001)
- 🔄 User authentication working (TODO: BE-002, FE-002)
- 🔄 Database schema deployed (TODO: DB-002)
- 🔄 Daily price data ingestion (TODO: DP-002)
- 🔄 Basic stock listing API (TODO: BE-003)

---

### 🔍 Review (1 ticket)
**Awaiting code review:**

**Backend:**
- **BE-004**: Stock Screening API Implementation (Critical, 16h actual) ✅ Ready for review
  - ✅ API implementation complete (3 endpoints)
  - ✅ 96 tests passing (82 unit + 14 integration)
  - ✅ PostgreSQL test database configured
  - ✅ All acceptance criteria met except performance tests
  - ⚠️ Performance testing blocked by DB-003 (materialized view needed)
  - 📝 PR #23 created

---

### Backlog (Sprint 2+: Week 3+) - Core & Advanced Features
**10 tickets for future sprints**

#### Sprint 2 (Week 3-4) - Core Screening Features
**6 tickets:**

**Backend (1):**
- BE-005: API Rate Limiting and Throttling (High, 6h) - Sprint 2

**Database (1):**
- DB-005: Order Book Schema and Storage (Medium, 8h) - Sprint 2

**Data Pipeline (2):**
- DP-003: Indicator Calculation DAG Implementation (Critical, 16h) - Sprint 2
- DP-004: KIS API Integration (Critical, 20h) - Sprint 2

**Frontend (2):**
- FE-003: Stock Screener Page Implementation (Critical, 16h) - Sprint 2
- FE-004: Stock Detail Page Implementation (High, 14h) - Sprint 2

**Infrastructure (1):**
- INFRA-002: CI/CD Pipeline with GitHub Actions (High, 10h) - Sprint 2

**Sprint 2 Total**: 106 hours (~13 person-days)

**Sprint 2 Goal**:
- ✓ Stock screening functionality fully operational
- ✓ 200+ indicators calculated daily
- ✓ Real-time data integration (KIS API)
- ✓ Rate limiting protecting APIs
- ✓ CI/CD pipeline automated

---

#### Sprint 3 (Week 5-6) - Polish & Advanced Features
**4 tickets:**

**Backend (1):**
- BE-006: WebSocket Real-time Price Streaming (High, 16h) - Sprint 3

**Frontend (1):**
- FE-005: Order Book Visualization Component (Medium, 12h) - Sprint 3

**Infrastructure (1):**
- INFRA-003: Production Monitoring and Logging Setup (Medium, 12h) - Sprint 3

**Sprint 3 Total**: 40 hours (~5 person-days)

**Sprint 3 Goal**:
- ✓ Real-time WebSocket streaming operational
- ✓ Order book (호가) visualization for traders
- ✓ Production monitoring and alerting
- ✓ Performance optimization
- ✓ MVP ready for beta launch

## Workflow

1. **Backlog**: Product backlog, not yet prioritized
2. **Todo**: Ready to start, prioritized by sprint
3. **In Progress**: Developer actively working (limit: 1-2 per person)
4. **Review**: Code review, testing, verification
5. **Done**: Merged to main, deployed to staging/production

## Moving Tickets

To move a ticket between stages:

```bash
# Move from todo to in_progress
mv docs/kanban/todo/BE-001.md docs/kanban/in_progress/

# Update status in file
# Change: **Status**: TODO
# To:     **Status**: IN_PROGRESS

# Update progress percentage as you work
```

## Ticket Dependencies

Always check dependencies before starting work:

```mermaid
graph LR
    DB-001 --> DB-002
    DB-002 --> DB-003
    DB-002 --> BE-001
    BE-001 --> BE-002
    BE-002 --> BE-003
    BE-003 --> BE-004
    DB-003 --> BE-004
```

## Team Guidelines

1. **Limit WIP**: Maximum 2 tickets in "In Progress" per person
2. **Update Progress**: Update progress percentage daily
3. **Blocked Tickets**: Add "BLOCKED" label and note blocker
4. **Review Time**: Aim for < 24 hour review turnaround
5. **Definition of Done**:
   - All subtasks completed ✓
   - All acceptance criteria met ✓
   - Tests passing ✓
   - Code reviewed ✓
   - Deployed to staging ✓

## Metrics

Track these metrics weekly:

- **Velocity**: Tickets completed per sprint
- **Cycle Time**: Average time from todo → done
- **Lead Time**: Average time from backlog → done
- **WIP**: Current work in progress count
- **Blocked**: Number of blocked tickets

## Sprint Planning

Before each sprint:

1. Review completed tickets
2. Calculate velocity
3. Prioritize backlog
4. Move tickets to todo (based on velocity)
5. Assign tickets to team members
6. Update sprint goals

## Daily Standup

Each team member answers:

1. What did I complete yesterday?
2. What am I working on today?
3. Am I blocked? (If yes, move ticket and add note)

## References

- **PRD**: Product requirements and features
- **SRS**: Detailed software requirements
- **SDS**: Technical design and architecture

---

## Recent Updates

**2025-11-10 (11:45)**:
- ✅ **BE-004 Stock Screening API** - 98% complete
  - Fixed PostgreSQL test database configuration (SQLite UUID compatibility issue)
  - All 14 integration tests passing with PostgreSQL
  - 96 total tests passing (82 unit + 14 integration)
  - Test coverage: screening.py 100%, screening_service.py 95%, schemas 99%
  - All acceptance criteria met except performance tests (blocked by DB-003)
- 📝 Updated conftest.py to use PostgreSQL for tests
- 📝 Created screener_test database
- ⚠️ Performance testing pending (requires materialized view from DB-003)
- 🔄 **Next**: Complete BE-004 PR and move to review

**2025-11-09 (17:55)**:
- ✅ Runtime testing completed - All 12 tests passing
- ✅ Moved INFRA-001, BE-001, DB-001 to done (runtime verified)
- ✅ Fixed critical configuration issues:
  - DATABASE_URL updated to use async driver (postgresql+asyncpg)
  - CORS_ORIGINS validator fixed for Pydantic v2
  - Docker network conflict resolved (auto-assigned subnet)
  - Python dependency conflict resolved (celery 5.4.0)
- 📝 Created comprehensive testing scripts:
  - scripts/test_all.sh (12 automated tests)
  - scripts/monitor.sh (real-time health monitoring)
- 📖 Updated testing documentation (docs/TESTING.md)
- 🎉 **Sprint 1 Foundation Complete** - 6 tickets done, infrastructure ready

**Sprint 1 Status**:
- ✅ Core infrastructure: 100% complete (INFRA-001, BE-001, DB-001)
- ✅ Critical fixes: 100% complete (BUGFIX-001, TECH-DEBT-001, FEATURE-001)
- 🔄 Remaining work: 74 hours (BE-002, DB-002, FE-001, FE-002, DP-001, DP-002)

**Next Actions**:
1. ✅ ~~Run comprehensive Docker testing~~ DONE
2. ✅ ~~Move review tickets to done~~ DONE
3. 🔄 Begin Sprint 1 remaining tasks (BE-002, DB-002, FE-001, etc.)

---

Last Updated: 2025-11-10 (11:45)
