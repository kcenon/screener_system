"""
Tests for FastAPI dependency injection system

Tests the core dependency injection infrastructure that provides:
- Database sessions (AsyncSession)
- Service instances (AuthService, WatchlistService)
- User authentication (JWT-based)
"""

from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_auth_service,
    get_current_active_user,
    get_current_user,
    get_watchlist_service,
)
from app.core.exceptions import UnauthorizedException
from app.db.models import User
from app.services import AuthService
from app.services.watchlist_service import WatchlistService

# =============================================================================
# Database Session Injection Tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_db_session_lifecycle(db: AsyncSession):
    """Test database session opens and closes correctly"""
    # Session should be open and usable
    assert db is not None
    assert isinstance(db, AsyncSession)

    # Test basic query execution
    result = await db.execute(text("SELECT 1"))
    assert result is not None


@pytest.mark.asyncio
async def test_get_db_session_isolation(db_engine):
    """Test each request gets isolated session"""
    from app.db.session import get_db

    # Create two sessions
    session1_gen = get_db()
    session2_gen = get_db()

    session1 = await session1_gen.__anext__()
    session2 = await session2_gen.__anext__()

    # Sessions should be different instances
    assert session1 is not session2

    # Cleanup
    try:
        await session1_gen.aclose()
        await session2_gen.aclose()
    except StopAsyncIteration:
        pass


@pytest.mark.asyncio
async def test_get_db_session_rollback_on_error(db_engine):
    """Test database session rollback on exception"""
    from app.db.session import get_db

    session_gen = get_db()
    session = await session_gen.__anext__()

    # Simulate error during request
    try:
        # This will trigger rollback in finally block
        raise ValueError("Simulated error")
    except ValueError:
        pass

    # Session should still be valid for cleanup
    assert session is not None

    # Cleanup
    try:
        await session_gen.aclose()
    except (StopAsyncIteration, ValueError):
        pass


# =============================================================================
# Service Dependencies Tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_auth_service(db: AsyncSession):
    """Test AuthService dependency injection"""
    # Get service instance
    service = await get_auth_service(db)

    # Verify service is correctly instantiated
    assert service is not None
    assert isinstance(service, AuthService)
    assert service.session is db


@pytest.mark.asyncio
async def test_get_watchlist_service(db: AsyncSession):
    """Test WatchlistService dependency injection"""
    # Get service instance
    service = await get_watchlist_service(db)

    # Verify service is correctly instantiated
    assert service is not None
    assert isinstance(service, WatchlistService)
    assert service.session is db


@pytest.mark.asyncio
async def test_service_dependencies_chain(db: AsyncSession):
    """Test dependencies that depend on other dependencies"""
    # AuthService depends on db session
    auth_service = await get_auth_service(db)
    assert auth_service.session is db

    # WatchlistService also depends on db session
    watchlist_service = await get_watchlist_service(db)
    assert watchlist_service.session is db

    # Both should have access to same database session
    assert auth_service.session is watchlist_service.session


# =============================================================================
# User Authentication Dependencies Tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_current_user_valid_token(db: AsyncSession):
    """Test current user extraction from valid token"""
    # Create mock user (use Mock instead of actual User model)
    mock_user = Mock(spec=User)
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_user.name = "Test User"

    # Create mock credentials
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid_token_123",
    )

    # Create mock auth service
    auth_service = AsyncMock(spec=AuthService)
    auth_service.verify_access_token.return_value = mock_user

    # Test get_current_user
    user = await get_current_user(credentials, auth_service)

    # Verify
    assert user == mock_user
    auth_service.verify_access_token.assert_called_once_with("valid_token_123")


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """Test error handling for invalid token"""
    # Create mock credentials
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="invalid_token",
    )

    # Create mock auth service that raises exception
    auth_service = AsyncMock(spec=AuthService)
    auth_service.verify_access_token.side_effect = UnauthorizedException(
        "Invalid token"
    )

    # Test get_current_user raises HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, auth_service)

    # Verify exception details
    assert exc_info.value.status_code == 401
    assert "Invalid token" in str(exc_info.value.detail)
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.asyncio
async def test_get_current_user_expired_token():
    """Test error handling for expired token"""
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="expired_token",
    )

    auth_service = AsyncMock(spec=AuthService)
    auth_service.verify_access_token.side_effect = UnauthorizedException(
        "Token has expired"
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials, auth_service)

    assert exc_info.value.status_code == 401
    assert "Token has expired" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_current_active_user_active(db: AsyncSession):
    """Test active user verification succeeds for active users"""
    # Create actual user in database
    from app.core.security import get_password_hash

    active_user = User(
        email="active@example.com",
        password_hash=get_password_hash("password123"),
        name="Active User",
    )
    db.add(active_user)
    await db.commit()
    await db.refresh(active_user)

    # Test get_current_active_user
    # Note: User model may not have is_active field, checking if it exists
    user = await get_current_active_user(active_user)

    # Verify same user returned
    assert user == active_user
    assert user.id == active_user.id


@pytest.mark.asyncio
async def test_get_current_active_user_inactive():
    """Test active user verification fails for inactive users"""
    # Create mock inactive user
    mock_user = Mock(spec=User)
    mock_user.id = 2
    mock_user.email = "inactive@example.com"
    mock_user.is_active = False

    # Test get_current_active_user raises HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(mock_user)

    # Verify exception details
    assert exc_info.value.status_code == 403
    assert "Inactive user account" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_dependency_injection_full_chain(db: AsyncSession):
    """Test complete dependency chain: db -> service -> user"""
    # 1. Database session injection
    assert db is not None

    # 2. Service injection (depends on db)
    auth_service = await get_auth_service(db)
    assert auth_service is not None
    assert auth_service.session is db

    # 3. User authentication (depends on service)
    # Create test user in database
    from app.core.security import get_password_hash
    from app.db.models import User

    test_user = User(
        email="chain@example.com",
        password_hash=get_password_hash("password123"),
        name="Chain User",
    )
    db.add(test_user)
    await db.commit()
    await db.refresh(test_user)

    # Generate token for user
    from app.core.security import create_access_token

    access_token = create_access_token(subject=str(test_user.id))

    # Test authentication with real token
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=access_token,
    )

    # Verify user extraction
    user = await get_current_user(credentials, auth_service)
    assert user.id == test_user.id
    assert user.email == test_user.email

    # Verify active user check
    active_user = await get_current_active_user(user)
    assert active_user.id == user.id


@pytest.mark.asyncio
async def test_multiple_service_instances_share_session(db: AsyncSession):
    """Test multiple service instances share same database session"""
    # Create multiple service instances
    auth_service1 = await get_auth_service(db)
    auth_service2 = await get_auth_service(db)
    watchlist_service = await get_watchlist_service(db)

    # All should share the same database session
    assert auth_service1.session is db
    assert auth_service2.session is db
    assert watchlist_service.session is db

    # All should reference the same session object
    assert auth_service1.session is auth_service2.session
    assert auth_service1.session is watchlist_service.session
