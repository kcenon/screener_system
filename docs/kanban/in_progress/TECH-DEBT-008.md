# [TECH-DEBT-008] Increase Test Coverage to 80%

## Metadata
- **Status**: IN_PROGRESS
- **Priority**: Medium
- **Assignee**: kcenon
- **Estimated Time**: 16 hours
- **Actual Time**: 10 hours (Phase 1 & 2 complete)
- **Sprint**: Sprint 3 (Week 5-6)
- **Tags**: #testing #coverage #quality
- **Created**: 2025-11-10
- **Moved to Todo**: 2025-11-11
- **Started**: 2025-11-11
- **Related**: TECH-DEBT-005

## Description
Increase backend test coverage from current 59% to target 80% by adding comprehensive unit and integration tests for untested modules.

## Context
TECH-DEBT-005 fixed the test infrastructure and all authentication tests are passing. However, coverage is currently at 59.21%, below the project target of 80%.

## Current Coverage Status
- **Total**: 59.21% (target: 80%)
- **Gap**: ~21% additional coverage needed

### Low Coverage Areas
1. **screening_repository.py**: 13% (needs +67%)
2. **stock_repository.py**: 21% (needs +59%)
3. **screening_service.py**: 22% (needs +58%)
4. **stock_service.py**: 24% (needs +56%)
5. **user_session_repository.py**: 33% (needs +47%)
6. **cache.py**: 31% (needs +49%)
7. **auth_service.py**: 22% (needs +58%)

## Subtasks

### Phase 1: Repository Tests (8h) ✅
- [x] Add tests for stock_repository (14 test cases)
  - [x] Test get_by_code, get_by_code_with_latest
  - [x] Test list_stocks with pagination and filters
  - [x] Test search_stocks functionality
  - [x] Test get_latest_price
- [x] Add tests for user_session_repository (18 test cases)
  - [x] Test create, get_by_id, get_by_refresh_token
  - [x] Test get_active_sessions_by_user_id
  - [x] Test revoke, revoke_by_refresh_token, revoke_all
  - [x] Test delete_expired_sessions
- [x] screening_repository already has comprehensive tests

### Phase 2: Service Tests (6h) ✅
- [x] Add tests for stock_service (18 test cases)
  - [x] Test list_stocks with caching and pagination
  - [x] Test get_stock_by_code with cache behavior
  - [x] Test search_stocks with filters
  - [x] Cache integration tests with TTL validation
- [x] Add tests for auth_service (20 test cases)
  - [x] Test register_user and authenticate_user
  - [x] Test refresh_access_token and verify_access_token
  - [x] Test logout and logout_all_sessions
  - [x] Comprehensive error handling tests
- [x] screening_service already has comprehensive tests

### Phase 3: Integration & Edge Cases (2h)
- [ ] Add tests for cache.py
  - [ ] Test Redis connection handling
  - [ ] Test get, set, delete operations
  - [ ] Test cache miss scenarios
- [ ] Add edge case tests
  - [ ] Empty result sets
  - [ ] Invalid inputs
  - [ ] Database errors
  - [ ] Network failures

## Acceptance Criteria
- [ ] **Backend coverage** >= 80%
- [ ] All existing tests still passing
- [ ] New tests follow existing patterns
- [ ] Test execution time < 5 minutes
- [ ] No flaky tests (run 10 times, all pass)

## Implementation Guide

### Example: Testing ScreeningRepository

```python
# tests/repositories/test_screening_repository.py

import pytest
from app.repositories import ScreeningRepository
from app.schemas import ScreeningFilters

@pytest.mark.asyncio
async def test_get_filtered_stocks_with_per_filter(db):
    """Test filtering by PER range"""
    repo = ScreeningRepository(db)

    filters = ScreeningFilters(
        valuation_per=FilterRange(min=5.0, max=15.0)
    )

    result = await repo.get_filtered_stocks(
        filters=filters,
        sort_by="per",
        page=1,
        per_page=10
    )

    assert len(result) > 0
    for stock in result:
        assert 5.0 <= stock.per <= 15.0

@pytest.mark.asyncio
async def test_get_filtered_stocks_pagination(db):
    """Test pagination works correctly"""
    repo = ScreeningRepository(db)

    # Get first page
    page1 = await repo.get_filtered_stocks(
        filters=ScreeningFilters(),
        sort_by="code",
        page=1,
        per_page=10
    )

    # Get second page
    page2 = await repo.get_filtered_stocks(
        filters=ScreeningFilters(),
        sort_by="code",
        page=2,
        per_page=10
    )

    assert len(page1) == 10
    assert len(page2) <= 10
    assert page1[0].code != page2[0].code
```

### Example: Testing ScreeningService with Cache

```python
# tests/services/test_screening_service.py

import pytest
from unittest.mock import AsyncMock, patch
from app.services import ScreeningService
from app.schemas import ScreeningFilters

@pytest.mark.asyncio
async def test_screen_stocks_uses_cache(db):
    """Test that screening results are cached"""
    service = ScreeningService(db)

    filters = ScreeningFilters(market="KOSPI")

    # First call - should hit database
    with patch.object(service.repo, 'get_filtered_stocks') as mock_repo:
        mock_repo.return_value = []
        result1 = await service.screen_stocks(
            filters=filters,
            sort_by="code",
            page=1,
            per_page=50
        )
        assert mock_repo.called

    # Second call - should hit cache (repo not called)
    with patch.object(service.repo, 'get_filtered_stocks') as mock_repo:
        result2 = await service.screen_stocks(
            filters=filters,
            sort_by="code",
            page=1,
            per_page=50
        )
        assert not mock_repo.called
```

## Dependencies
- **Depends on**: TECH-DEBT-005 (test infrastructure)
- **Blocks**: None (quality improvement)

## Testing Strategy
1. **Write tests first** for critical paths
2. **Run coverage** after each module
3. **Refactor** if needed to make code more testable
4. **Document** complex test scenarios

## Success Metrics
- Coverage increases from 59% to 80%
- All tests green in CI/CD
- Test execution time < 5 minutes
- No test flakiness

## Progress
- **0%** - Not started (blocked by TECH-DEBT-005 completion)

## Notes
- Focus on high-value areas first (repositories, services)
- Don't test third-party libraries (SQLAlchemy, Pydantic)
- Mock external dependencies (Redis, database in some cases)
- Prioritize readability over 100% coverage
