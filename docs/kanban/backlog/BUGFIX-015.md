# BUGFIX-015: Increase Backend Test Coverage to 80% Target

## Metadata

- **Status**: TODO
- **Priority**: High
- **Assignee**: TBD
- **Estimated Time**: 16 hours
- **Sprint**: Post-MVP
- **Tags**: backend, testing, coverage, quality

## Description

Backend test coverage is currently at **47.05%**, significantly below the **80% target** set in TECH-DEBT-008. This gap of 32.95% represents a significant quality risk, with 4 modules having 0% coverage and many critical services below 25%.

### Current Coverage Summary
- **Overall**: 47.05% (1,752 / 3,724 lines)
- **Target**: 80%
- **Gap**: 32.95% (approximately 1,226 additional lines to cover)

### Critical Gaps (0% Coverage)
1. `app/celery_app.py` - 4 lines
2. `app/core/redis_pubsub.py` - 119 lines
3. `app/services/kis_quota.py` - 127 lines
4. `app/services/price_publisher.py` - 85 lines
**Total**: 335 lines completely untested

### Major Gaps (< 25% Coverage)
| Module | Coverage | Gap |
|--------|----------|-----|
| websocket.py (endpoint) | 12.8% | 130 lines |
| screening_repository.py | 12.9% | 74 lines |
| market_service.py | 16.8% | 99 lines |
| websocket.py (core) | 18.4% | 261 lines |
| watchlist_service.py | 18.0% | 100 lines |
| market_repository.py | 19.2% | 63 lines |
| screening_service.py | 20.8% | 80 lines |
| stock_repository.py | 21.3% | 74 lines |
| auth_service.py | 21.8% | 68 lines |
| rate_limit.py | 22.8% | 44 lines |
| stock_service.py | 23.6% | 68 lines |

## Subtasks

### Phase 1: Zero Coverage Modules (4h)
- [ ] Create tests for `app/core/redis_pubsub.py` (119 lines)
  - [ ] Test RedisPubSub initialization
  - [ ] Test publish/subscribe functionality
  - [ ] Test message handling
  - [ ] Test error recovery
- [ ] Create tests for `app/services/kis_quota.py` (127 lines)
  - [ ] Test quota tracking
  - [ ] Test rate limit calculations
  - [ ] Test quota reset logic
- [ ] Create tests for `app/services/price_publisher.py` (85 lines)
  - [ ] Test price publishing
  - [ ] Test subscriber management
  - [ ] Test message formatting
- [ ] Create tests for `app/celery_app.py` (4 lines)
  - [ ] Test Celery configuration

### Phase 2: WebSocket Module Tests (4h)
- [ ] Improve `app/api/v1/endpoints/websocket.py` (130 lines to cover)
  - [ ] Test WebSocket connection handling
  - [ ] Test message routing
  - [ ] Test authentication flow
  - [ ] Test error handling
- [ ] Improve `app/core/websocket.py` (261 lines to cover)
  - [ ] Test ConnectionManager
  - [ ] Test broadcast functionality
  - [ ] Test subscription management
  - [ ] Test heartbeat mechanism

### Phase 3: Service Layer Tests (4h)
- [ ] Improve `app/services/market_service.py` to >80%
- [ ] Improve `app/services/watchlist_service.py` to >80%
- [ ] Improve `app/services/screening_service.py` to >80%
- [ ] Improve `app/services/stock_service.py` to >80%
- [ ] Improve `app/services/auth_service.py` to >80%

### Phase 4: Repository Layer Tests (3h)
- [ ] Improve `app/repositories/screening_repository.py` to >80%
- [ ] Improve `app/repositories/market_repository.py` to >80%
- [ ] Improve `app/repositories/stock_repository.py` to >80%
- [ ] Improve `app/repositories/watchlist_repository.py` to >80%

### Phase 5: Middleware Tests (1h)
- [ ] Improve `app/middleware/rate_limit.py` to >80%
- [ ] Improve `app/middleware/metrics.py` to >80%
- [ ] Improve `app/middleware/logging.py` to >80%

## Acceptance Criteria

### Coverage Targets
- [ ] Overall backend coverage >= 80%
- [ ] No module with 0% coverage
- [ ] All service modules >= 75% coverage
- [ ] All repository modules >= 75% coverage
- [ ] WebSocket modules >= 70% coverage

### Quality
- [ ] All tests pass in CI/CD pipeline
- [ ] No flaky tests
- [ ] Test execution time < 5 minutes
- [ ] `--cov-fail-under=80` re-enabled in pytest.ini

### Documentation
- [ ] Coverage report updated
- [ ] TECH-DEBT-008.md updated with final status

## Dependencies

- **Depends On**: TECH-DEBT-008 (Partially complete - 77% → 47% regression?)
- **Blocks**: None

## References

- TECH-DEBT-008.md - Original coverage ticket
- `/backend/pytest.ini` - Pytest configuration
- `/backend/tests/` - Existing test files
- Coverage report (XML format available)

## Test Patterns to Follow

```python
# Service test example
@pytest.mark.asyncio
async def test_get_stock_by_code(
    stock_service: StockService,
    mock_stock_repository: AsyncMock
):
    # Arrange
    mock_stock_repository.get_by_code.return_value = sample_stock

    # Act
    result = await stock_service.get_stock_by_code("005930")

    # Assert
    assert result.code == "005930"
    mock_stock_repository.get_by_code.assert_called_once_with("005930")

# WebSocket test example
@pytest.mark.asyncio
async def test_websocket_connect(test_client: TestClient):
    with test_client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "connection_established"
```

## Progress

**0%** - Not started

## Notes

- pytest.ini currently has threshold disabled (set to 59%)
- Need to investigate if coverage regressed from 77% to 47%
- Consider using pytest-cov parallel execution for faster tests
- Mock external services (Redis, KIS API) for unit tests
- Integration tests should use test database
