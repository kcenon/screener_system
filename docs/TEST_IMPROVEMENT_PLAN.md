# Test Improvement Plan
# Stock Screening Platform

## Document Information

| Field | Value |
|-------|-------|
| **Created** | 2025-11-15 |
| **Status** | Action Plan |
| **Priority** | Critical |
| **Target** | 70-80% Test Coverage |

---

## Current Status

- **Overall Coverage**: ~40%
- **Backend Coverage**: ~65%
- **Frontend Coverage**: ~21%
- **E2E Coverage**: ~10%

**Gap**: 30-40 percentage points below target

---

## Phase 1: Critical Tests (Week 1-2) 🔴

### Backend Core Modules (8 tests)

**Priority**: P0 - Critical Infrastructure

1. **test_security.py**
   - JWT token generation/validation
   - Password hashing/verification
   - Authentication flows
   - Estimated: 4 hours

2. **test_exceptions.py**
   - Custom exception handling
   - Error response formatting
   - HTTP status codes
   - Estimated: 2 hours

3. **test_websocket.py** (unit)
   - ConnectionManager unit tests
   - Connection lifecycle
   - Message broadcasting
   - Estimated: 3 hours

4. **test_dependencies.py**
   - Database session injection
   - Redis client injection
   - Service dependencies
   - Estimated: 2 hours

### Critical API Endpoints (3 tests)

5. **test_stocks.py**
   - GET /stocks/ (listing with pagination)
   - GET /stocks/{symbol} (detail)
   - GET /stocks/{symbol}/prices (price history)
   - GET /stocks/{symbol}/financials
   - Estimated: 4 hours

6. **test_health.py**
   - Health check endpoints
   - Database health
   - Redis health
   - Estimated: 1 hour

### Frontend Critical Path (3 tests)

7. **LoginPage.test.tsx**
   - Login form submission
   - Error handling
   - Redirect after login
   - Estimated: 3 hours

8. **ScreenerPage.test.tsx**
   - Filter application
   - Results rendering
   - Export functionality
   - Estimated: 4 hours

9. **StockDetailPage.test.tsx**
   - Stock data display
   - Chart rendering
   - Watchlist actions
   - Estimated: 3 hours

### E2E Critical Journey (1 test)

10. **auth_flow.e2e.ts**
    - Login → Dashboard → Logout
    - Authentication state
    - Protected routes
    - Estimated: 4 hours

**Phase 1 Total**: ~30 hours, 10 critical tests

---

## Phase 2: High Priority (Week 3-4) 🟠

### Service Layer Tests (3 tests)

11. **test_market_service.py**
    - Market data fetching
    - Index calculation
    - Sector aggregation
    - Estimated: 3 hours

12. **test_watchlist_service.py**
    - CRUD operations
    - Stock management
    - User isolation
    - Estimated: 3 hours

13. **test_price_publisher.py**
    - Real-time price publishing
    - Redis pub/sub
    - Connection handling
    - Estimated: 3 hours

### Frontend Data Hooks (6 tests)

14. **useAuth.test.ts**
    - Login/logout
    - Token refresh
    - Auth state
    - Estimated: 2 hours

15. **useScreening.test.ts**
    - Filter application
    - Results fetching
    - Pagination
    - Estimated: 3 hours

16. **useStockData.test.ts**
    - Stock detail fetching
    - Price updates
    - Error handling
    - Estimated: 2 hours

17-19. **Additional hooks** (useWatchlistPrices, useDashboard, useMarketIndices)
    - Estimated: 6 hours total

### Schema Validation (6 tests)

20. **test_stock_schemas.py**
21. **test_user_schemas.py**
22. **test_watchlist_schemas.py**
23-25. **Additional schemas** (websocket, market, screening)
    - Estimated: 12 hours total

**Phase 2 Total**: ~34 hours, 15 tests

---

## Phase 3: Medium Priority (Week 5-6) 🟡

### Component Integration (20 tests)

26-35. **Stock detail components** (9 components)
    - StockHeader, PriceChart, FinancialMetrics, etc.
    - Estimated: 18 hours

36-45. **Market components** (10 components)
    - MarketIndices, SectorPerformance, MarketMovers, etc.
    - Estimated: 20 hours

46-55. **Additional components** (watchlist, navigation, etc.)
    - Estimated: 20 hours

### Data Pipeline Automation

56. **Automated pytest for DAGs**
    - DAG validation
    - Task execution tests
    - Error handling
    - Estimated: 8 hours

**Phase 3 Total**: ~66 hours, 30+ tests

---

## Phase 4: Low Priority (Week 7-8) 🟢

### Middleware & Utilities

57. **test_logging_middleware.py** (2h)
58. **test_metrics_middleware.py** (2h)
59. **Frontend utility tests** (formatNumber, etc.) (6h)

### Load & Performance

60. **Screening query load tests** (4h)
61. **WebSocket connection load tests** (4h)

**Phase 4 Total**: ~18 hours, 5+ tests

---

## Summary

| Phase | Duration | Tests | Estimated Hours | Coverage Gain |
|-------|----------|-------|-----------------|---------------|
| Phase 1 (Critical) | Week 1-2 | 10 | 30h | +15% |
| Phase 2 (High) | Week 3-4 | 15 | 34h | +10% |
| Phase 3 (Medium) | Week 5-6 | 30+ | 66h | +10% |
| Phase 4 (Low) | Week 7-8 | 5+ | 18h | +5% |
| **Total** | **8 weeks** | **60+** | **148h** | **+40%** |

**Expected Final Coverage**: 40% → 80%

---

## Missing Features (Not Test Items)

These require feature implementation, not just tests:

### P0 Features:
1. **Portfolio Management** (0% implemented)
   - Backend: models, services, API
   - Frontend: pages, components
   - Estimated: 40-60 hours

2. **Alerts & Notifications** (0% implemented)
   - Alert system, email service
   - Estimated: 30-40 hours

3. **Email System** (verification, reset)
   - Email templates, SMTP
   - Estimated: 20-30 hours

### P1 Features:
4. **OAuth Login** (0% implemented)
   - Google, Kakao, Naver
   - Estimated: 20-30 hours

5. **Subscription & Billing** (0% implemented)
   - Payment processing
   - Estimated: 40-50 hours

**Total Feature Work**: ~150-210 hours (separate from testing)

---

## Recommendations

1. **Immediate Action (Week 1-2)**:
   - Start Phase 1 critical tests
   - Blocks deployment confidence

2. **Short-term (Week 3-4)**:
   - Complete Phase 2 high-priority tests
   - Establishes baseline quality

3. **Medium-term (Week 5-8)**:
   - Phase 3-4 tests
   - Reaches 70-80% coverage target

4. **Feature Backlog**:
   - Portfolio Management
   - Alerts & Notifications
   - OAuth & Email systems
   - Should be separate tickets from test improvements

---

**Next Steps**: Create tickets in docs/kanban/backlog/ for each test improvement task.
