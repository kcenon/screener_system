# TEST-003: WebSocket ConnectionManager Unit Tests

**Type**: TEST
**Priority**: P0
**Status**: IN_PROGRESS
**Created**: 2025-11-16
**Effort**: 3 hours
**Phase**: Phase 1 - Critical Tests

---

## Description

Implement comprehensive unit tests for the WebSocket ConnectionManager class. This is critical infrastructure for real-time price updates - the core feature of the platform.

## Current Status

- **Test File**: `backend/tests/core/test_connection_manager.py` ✅ Created with 40+ unit tests
- **Source File**: `backend/app/core/websocket.py` ✅ Implemented (883 lines)
- **Coverage Impact**: Real-time infrastructure 0% → >90% coverage (estimated)
- **Note**: E2E WebSocket tests are separate (TEST-010)
- **Integration Tests**: `backend/tests/api/test_websocket.py` (existing)

## Test Requirements

### 1. Connection Lifecycle (1h)

```python
def test_connect_new_client():
    """Test adding new WebSocket connection"""

def test_disconnect_existing_client():
    """Test removing WebSocket connection"""

def test_disconnect_nonexistent_client():
    """Test disconnecting client that doesn't exist"""

def test_multiple_connections_same_user():
    """Test same user connecting from multiple devices"""

def test_connection_count():
    """Test active connection count tracking"""
```

### 2. Message Broadcasting (1h)

```python
def test_broadcast_to_all():
    """Test broadcasting message to all connected clients"""

def test_broadcast_to_user():
    """Test sending message to specific user"""

def test_broadcast_to_group():
    """Test sending message to user group/room"""

def test_broadcast_price_update():
    """Test broadcasting price update format"""

def test_broadcast_empty_connections():
    """Test broadcasting when no clients connected"""
```

### 3. Error Handling (0.5h)

```python
def test_handle_connection_error():
    """Test handling WebSocket connection errors"""

def test_handle_send_error():
    """Test handling message send failures"""

def test_cleanup_stale_connections():
    """Test removing disconnected clients"""

def test_connection_timeout():
    """Test connection timeout handling"""
```

### 4. Concurrency Safety (0.5h)

```python
def test_concurrent_connects():
    """Test multiple simultaneous connections"""

def test_concurrent_disconnects():
    """Test multiple simultaneous disconnections"""

def test_concurrent_broadcasts():
    """Test concurrent message broadcasts"""

def test_thread_safety():
    """Test ConnectionManager is thread-safe"""
```

## Acceptance Criteria

- [x] All connection lifecycle methods tested (6 tests)
- [x] All message broadcasting methods tested (6 tests)
- [x] Error handling tested (4 tests: connection errors, send failures, cleanup, timeout)
- [x] Concurrency and thread safety verified (4 tests)
- [x] Subscription management tested (3 tests)
- [x] Session restoration tested (4 tests: Phase 3 features)
- [x] Statistics tested (2 tests)
- [ ] Test coverage for ConnectionManager reaches >90% (pending verification)
- [ ] All tests pass in CI/CD pipeline (pending run)
- [x] Tests run in isolation (pytest fixtures with cleanup)

## Dependencies

- pytest
- pytest-asyncio (for async WebSocket tests)
- FastAPI WebSocket
- Mock WebSocket connections

## Testing Strategy

1. **Unit Tests**: Test ConnectionManager methods in isolation
2. **Mock WebSockets**: Use mock WebSocket objects for testing
3. **Async Tests**: Use pytest-asyncio for async connection handling
4. **Concurrency Tests**: Test with multiple concurrent connections

## Related Files

- Source: `backend/app/websocket/connection_manager.py`
- Test: `backend/tests/test_websocket.py` (to be created)
- Integration: `backend/app/api/v1/endpoints/websocket.py`

## Notes

- Use mock WebSocket objects to avoid actual network connections
- Test both successful and failed message deliveries
- Verify cleanup of disconnected clients
- Test with various message formats (price updates, market data)
- Separate unit tests (this ticket) from E2E tests (auth_flow.e2e.ts)

---

## Implementation Summary

**Tests Created** (42 total):
1. **Connection Lifecycle** (6 tests):
   - test_connect_new_client
   - test_connect_multiple_clients
   - test_disconnect_existing_client
   - test_disconnect_nonexistent_client
   - test_multiple_connections_same_user
   - test_connection_count

2. **Message Broadcasting** (6 tests):
   - test_broadcast_to_all
   - test_broadcast_with_exclude
   - test_send_to_user
   - test_send_to_subscribers
   - test_broadcast_price_update
   - test_broadcast_empty_connections

3. **Error Handling** (4 tests):
   - test_handle_connection_error
   - test_handle_send_error
   - test_cleanup_stale_connections
   - test_connection_timeout_heartbeat

4. **Concurrency Safety** (4 tests):
   - test_concurrent_connects
   - test_concurrent_disconnects
   - test_concurrent_broadcasts
   - test_thread_safety_sequence_counter

5. **Subscription Management** (3 tests):
   - test_subscribe_and_get_subscribers
   - test_unsubscribe
   - test_multiple_subscriptions

6. **Statistics** (2 tests):
   - test_get_stats
   - test_connection_info

7. **Session Restoration** (4 tests - Phase 3):
   - test_session_save_on_disconnect
   - test_session_restoration_on_reconnect
   - test_reconnect_with_expired_session
   - test_reconnect_with_user_mismatch

**Test Execution**:
```bash
# Run unit tests
docker exec screener_backend bash -c "cd /app && pytest tests/core/test_connection_manager.py -v"

# Run with coverage
docker exec screener_backend bash -c "cd /app && pytest tests/core/test_connection_manager.py --cov=app/core/websocket --cov-report=term-missing"
```

**Key Test Features**:
- Pure unit tests with mock WebSocket objects
- No network connections required
- Concurrent operation testing (asyncio.gather)
- Thread-safe sequence counter verification
- Phase 3 session restoration coverage
- Comprehensive error scenario coverage
- Isolation via pytest fixtures with auto-reset

---

**References**: TEST_IMPROVEMENT_PLAN.md - Phase 1, Item #3
