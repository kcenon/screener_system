# TEST-003: WebSocket ConnectionManager Unit Tests

**Type**: TEST
**Priority**: P0
**Status**: TODO
**Created**: 2025-11-16
**Effort**: 3 hours
**Phase**: Phase 1 - Critical Tests

---

## Description

Implement comprehensive unit tests for the WebSocket ConnectionManager class. This is critical infrastructure for real-time price updates - the core feature of the platform.

## Current Status

- **Test File**: `backend/tests/test_websocket.py` (unit tests) does not exist
- **Source File**: `backend/app/websocket/connection_manager.py` (exists, untested)
- **Coverage Impact**: Real-time communication with 0% test coverage
- **Note**: E2E WebSocket tests are separate (TEST-010)

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

- [ ] All connection lifecycle methods tested
- [ ] All message broadcasting methods tested
- [ ] Error handling tested (connection errors, send failures)
- [ ] Concurrency and thread safety verified
- [ ] Test coverage for ConnectionManager reaches >90%
- [ ] All tests pass in CI/CD pipeline
- [ ] Tests run in isolation (no shared state between tests)

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

**References**: TEST_IMPROVEMENT_PLAN.md - Phase 1, Item #3
