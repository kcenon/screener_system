# [TECH-DEBT-008] Increase Test Coverage to 80%

## Metadata
- **Status**: BACKLOG
- **Priority**: Medium
- **Assignee**: TBD
- **Estimated Time**: 16 hours
- **Sprint**: Sprint 3 (Week 5-6)
- **Tags**: #testing #coverage #quality
- **Created**: 2025-11-10
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

### Phase 1: Repository Tests (8h)
- [ ] Add tests for screening_repository
  - [ ] Test get_filtered_stocks with various filters
  - [ ] Test build_query_filters
  - [ ] Test apply_sorting
  - [ ] Test pagination
- [ ] Add tests for stock_repository
  - [ ] Test get_all, get_by_id, get_by_code
  - [ ] Test search functionality
  - [ ] Test get_by_sector
  - [ ] Test get_top_by_market_cap
- [ ] Add tests for user_session_repository
  - [ ] Test create, get_by_id, get_by_refresh_token
  - [ ] Test get_active_sessions_for_user
  - [ ] Test revoke_session, revoke_all_for_user

### Phase 2: Service Tests (6h)
- [ ] Add tests for screening_service
  - [ ] Test screen_stocks with different filters
  - [ ] Test cache key generation
  - [ ] Test predefined templates
- [ ] Add tests for stock_service
  - [ ] Test get_stocks, get_stock_by_code
  - [ ] Test search_stocks
  - [ ] Test get_stock_prices
- [ ] Add tests for auth_service
  - [ ] Test refresh_access_token
  - [ ] Test logout, logout_all_sessions
  - [ ] Test session management

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
