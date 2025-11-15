# TEST-004: Dependency Injection Tests

**Type**: TEST
**Priority**: P0
**Status**: TODO
**Created**: 2025-11-16
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

- [ ] Database session lifecycle tested (creation, commit, rollback, cleanup)
- [ ] Redis client injection tested
- [ ] User authentication dependencies tested
- [ ] Dependency chains tested (dependencies that require other dependencies)
- [ ] Error handling tested (connection failures, invalid tokens)
- [ ] Test coverage for `dependencies.py` reaches >90%
- [ ] All tests pass in CI/CD pipeline
- [ ] No resource leaks (sessions and connections properly closed)

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

**References**: TEST_IMPROVEMENT_PLAN.md - Phase 1, Item #4
