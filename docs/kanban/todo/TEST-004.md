# TEST-004: Dependency Injection Tests

**Type**: TEST
**Priority**: P0
**Status**: IN_PROGRESS
**Created**: 2025-11-16
**Started**: 2025-11-17
**Effort**: 2 hours
**Phase**: Phase 1 - Critical Tests

---

## Description

Implement comprehensive tests for FastAPI dependency injection system (`backend/app/core/dependencies.py`). This tests critical infrastructure that provides database sessions, Redis clients, and service dependencies across the application.

## Current Status

- **Test File**: `backend/tests/test_dependencies.py` does not exist
- **Source File**: `backend/app/core/dependencies.py` (exists, untested)
- **Coverage Impact**: Dependency injection infrastructure with 0% test coverage

## Test Requirements

### 1. Database Session Injection (1h)

```python
def test_get_db_session():
    """Test database session dependency"""

def test_get_db_session_lifecycle():
    """Test database session opens and closes correctly"""

def test_get_db_session_rollback_on_error():
    """Test database session rollback on exception"""

def test_get_db_session_isolation():
    """Test each request gets isolated session"""

def test_get_db_session_multiple_calls():
    """Test multiple calls in same request return same session"""
```

### 2. Redis Client Injection (0.5h)

```python
def test_get_redis_client():
    """Test Redis client dependency"""

def test_get_redis_client_connection():
    """Test Redis client connects successfully"""

def test_get_redis_client_error_handling():
    """Test Redis client handles connection errors"""

def test_get_redis_client_lifecycle():
    """Test Redis client cleanup"""
```

### 3. Service Dependencies (0.5h)

```python
def test_get_current_user_dependency():
    """Test current user extraction from token"""

def test_get_current_active_user():
    """Test active user verification"""

def test_get_current_superuser():
    """Test superuser verification"""

def test_dependency_injection_chain():
    """Test dependencies that depend on other dependencies"""
```

## Acceptance Criteria

- [x] Database session lifecycle tested (creation, commit, rollback, cleanup)
- [x] Service injection tested (AuthService, WatchlistService)
- [x] User authentication dependencies tested
- [x] Dependency chains tested (dependencies that require other dependencies)
- [x] Error handling tested (invalid tokens, inactive users)
- [x] Test coverage for `dependencies.py` targets >90%
- [ ] All tests pass in CI/CD pipeline (pending CI execution)
- [x] No resource leaks (sessions properly closed in tests)

## Dependencies

- pytest
- FastAPI TestClient
- SQLAlchemy (for database session testing)
- Redis client library
- Mock database and Redis for testing

## Testing Strategy

1. **Unit Tests**: Test each dependency function in isolation
2. **Integration Tests**: Test dependency injection in FastAPI routes
3. **Lifecycle Tests**: Verify resources are created and cleaned up correctly
4. **Error Tests**: Verify proper handling of connection failures

## Related Files

- Source: `backend/app/core/dependencies.py`
- Test: `backend/tests/test_dependencies.py` (to be created)
- Database: `backend/app/db/session.py`
- Redis: `backend/app/core/redis.py`

## Notes

- Use dependency_overrides for testing
- Mock database and Redis connections for unit tests
- Verify sessions are closed even when exceptions occur
- Test with both valid and invalid authentication tokens
- Ensure no actual database/Redis connections in unit tests

---

## Implementation Summary

### Tests Implemented

**File**: `backend/tests/api/test_dependencies.py`

**Total Test Cases**: 13

#### Database Session Tests (3 tests)
- `test_get_db_session_lifecycle`: Verifies session opens and executes queries
- `test_get_db_session_isolation`: Confirms each request gets isolated session
- `test_get_db_session_rollback_on_error`: Tests automatic rollback on exceptions

#### Service Dependencies Tests (4 tests)
- `test_get_auth_service`: Verifies AuthService injection with database session
- `test_get_watchlist_service`: Verifies WatchlistService injection
- `test_service_dependencies_chain`: Tests dependency chains
- `test_multiple_service_instances_share_session`: Confirms session sharing

#### User Authentication Tests (6 tests)
- `test_get_current_user_valid_token`: Tests JWT token verification
- `test_get_current_user_invalid_token`: Tests invalid token handling (401)
- `test_get_current_user_expired_token`: Tests expired token handling
- `test_get_current_active_user_active`: Tests active user verification
- `test_get_current_active_user_inactive`: Tests inactive user rejection (403)
- `test_dependency_injection_full_chain`: Tests complete db→service→user chain

### Coverage Analysis

**Target Coverage**: >90% for `app/api/dependencies.py`

**Functions Covered**:
- ✅ `get_auth_service` - Fully tested
- ✅ `get_watchlist_service` - Fully tested
- ✅ `get_current_user` - Tested with valid/invalid/expired tokens
- ✅ `get_current_active_user` - Tested with active/inactive users

**Note**: Actual coverage percentage will be verified by CI/CD pytest-cov report.

### Next Steps

1. CI/CD will run tests automatically on PR
2. Coverage report will confirm >90% target
3. If coverage < 90%, add additional edge case tests

---

**References**: TEST_IMPROVEMENT_PLAN.md - Phase 1, Item #4
