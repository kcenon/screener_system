# [TECH-DEBT-005] Fix Test Infrastructure and Increase Coverage

## Metadata
- **Status**: TODO
- **Priority**: High
- **Assignee**: TBD
- **Estimated Time**: 8 hours
- **Sprint**: Sprint 2 (Week 3-4)
- **Tags**: #tech-debt #testing #coverage

## Description
Fix failing tests and increase test coverage to meet CI/CD requirements (80% backend, 70% frontend).

## Context
CI/CD pipeline (INFRA-002) revealed test infrastructure issues:
1. SQLite incompatibility with UUID types in backend tests
2. Test coverage below requirements (61.47% vs 80% target)
3. Frontend test configuration needs validation

## Subtasks

### Backend Test Fixes
- [ ] Fix UUID type compatibility in SQLite tests
  - [ ] Use String representation for UUID in SQLite
  - [ ] Or switch to PostgreSQL for all tests
  - [ ] Update conftest.py database setup
- [ ] Investigate CompileError in user_sessions table
- [ ] Fix all 9 failing test cases in test_auth.py
- [ ] Add missing test cases to reach 80% coverage
  - [ ] Stock repository tests
  - [ ] Stock service tests
  - [ ] Additional API endpoint tests

### Frontend Test Fixes
- [ ] Verify Vitest configuration
- [ ] Fix any failing frontend tests
- [ ] Add tests to reach 70% coverage
  - [ ] Component tests
  - [ ] Hook tests
  - [ ] Utility function tests

### CI/CD Updates
- [ ] After fixes, enable test failures as blocking
- [ ] Remove `continue-on-error: true` from test steps
- [ ] Verify coverage thresholds are enforced

## Acceptance Criteria
- [ ] **Backend Tests**
  - [ ] All tests pass (0 errors)
  - [ ] Coverage >= 80%
  - [ ] No SQLite compatibility issues
  - [ ] Tests run in < 2 minutes

- [ ] **Frontend Tests**
  - [ ] All tests pass
  - [ ] Coverage >= 70%
  - [ ] Tests run in < 1 minute

- [ ] **CI/CD**
  - [ ] Test failures block PR merges
  - [ ] Coverage reports uploaded to Codecov
  - [ ] Clear error messages on failures

## Technical Solutions

### Option 1: Use PostgreSQL for all tests
```python
# conftest.py
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/screener_test"
```
**Pros**: Same database as production
**Cons**: Slower tests, requires service

### Option 2: Fix UUID types for SQLite
```python
# Use type_decorator to convert UUID to String for SQLite
from sqlalchemy import TypeDecorator, String

class GUID(TypeDecorator):
    impl = String(36)
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)
```
**Pros**: Fast tests, no external services
**Cons**: Different from production DB

### Recommended: Option 1 (PostgreSQL)
- Tests already set up PostgreSQL service in CI
- More realistic test environment
- No type conversion issues

## Dependencies
- **Depends on**: INFRA-002 (CI/CD Pipeline)
- **Blocks**: None (but critical for quality)

## References
- **INFRA-002**: CI/CD Pipeline implementation
- **Test failures**: https://github.com/kcenon/screener_system/actions
- [SQLAlchemy UUID docs](https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.Uuid)
- [pytest-cov docs](https://pytest-cov.readthedocs.io/)

## Progress
- **0%** - Not started

## Notes
- Current coverage: 61.47% (backend)
- Target: 80% (backend), 70% (frontend)
- Gap: ~19% more coverage needed
- Tests are currently non-blocking in CI to allow INFRA-002 merge
- Must be fixed before production deployment
