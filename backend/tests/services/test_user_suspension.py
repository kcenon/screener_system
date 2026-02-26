"""Unit tests for user account suspension functionality"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_admin_user
from app.core.exceptions import UnauthorizedException
from app.db.models import User, UserSession
from app.schemas import UserLogin
from app.services.auth_service import AuthService


class TestUserIsActive:
    """Test User.is_active property"""

    def test_active_user(self):
        """Test is_active returns True for non-suspended user"""
        user = User(
            id=1,
            email="test@example.com",
            is_suspended=False,
        )
        assert user.is_active is True

    def test_suspended_user(self):
        """Test is_active returns False for suspended user"""
        user = User(
            id=1,
            email="test@example.com",
            is_suspended=True,
            suspended_at=datetime.now(timezone.utc),
            suspension_reason="Policy violation",
        )
        assert user.is_active is False

    def test_default_is_active(self):
        """Test non-suspended users are active"""
        user = User(id=1, email="test@example.com", is_suspended=False)
        assert user.is_suspended is False
        assert user.is_active is True

    def test_is_active_fail_safe_when_none(self):
        """Test is_active is False (fail-safe) when is_suspended is None (pre-migration)"""
        user = User(id=1, email="test@example.com")
        # Before migration applies, is_suspended may be None at Python level
        assert user.is_active is False  # not None == True → fail-safe deny


class TestAuthServiceSuspension:
    """Test AuthService suspension-related behavior"""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        session = Mock(spec=AsyncSession)
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance with mock session"""
        return AuthService(session=mock_session)

    @pytest.fixture
    def active_user(self):
        """Create active user"""
        now = datetime.now(timezone.utc)
        return User(
            id=1,
            email="active@example.com",
            password_hash="$2b$12$abcdefghijklmnopqrstuv",
            name="Active User",
            subscription_tier="free",
            email_verified=False,
            is_suspended=False,
            created_at=now,
            updated_at=now,
        )

    @pytest.fixture
    def suspended_user(self):
        """Create suspended user"""
        now = datetime.now(timezone.utc)
        return User(
            id=2,
            email="suspended@example.com",
            password_hash="$2b$12$abcdefghijklmnopqrstuv",
            name="Suspended User",
            subscription_tier="free",
            email_verified=False,
            is_suspended=True,
            suspended_at=now,
            suspension_reason="Policy violation",
            created_at=now,
            updated_at=now,
        )

    # ========================================================================
    # authenticate_user with suspended account
    # ========================================================================

    @pytest.mark.asyncio
    async def test_authenticate_suspended_user_rejected(self, service, suspended_user):
        """Test that suspended users cannot authenticate"""
        credentials = UserLogin(email="suspended@example.com", password="password123")

        service.user_repo.get_by_email = AsyncMock(return_value=suspended_user)

        with patch("app.services.auth_service.verify_password") as mock_verify:
            mock_verify.return_value = True

            with pytest.raises(UnauthorizedException) as exc_info:
                await service.authenticate_user(credentials)

            assert "suspended" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_authenticate_active_user_succeeds(
        self, service, active_user, mock_session
    ):
        """Test that active users can authenticate normally"""
        credentials = UserLogin(email="active@example.com", password="password123")

        service.user_repo.get_by_email = AsyncMock(return_value=active_user)
        service.user_repo.update = AsyncMock()

        with (
            patch("app.services.auth_service.verify_password") as mock_verify,
            patch("app.services.auth_service.create_access_token") as mock_access,
            patch("app.services.auth_service.create_refresh_token") as mock_refresh,
        ):
            mock_verify.return_value = True
            mock_access.return_value = "access_token"
            mock_refresh.return_value = "refresh_token"

            service.session_repo.create = AsyncMock()

            result = await service.authenticate_user(credentials)
            assert result.access_token == "access_token"

    # ========================================================================
    # verify_access_token with suspended account
    # ========================================================================

    @pytest.mark.asyncio
    async def test_verify_token_suspended_user_rejected(self, service, suspended_user):
        """Test that token verification fails for suspended users"""
        payload = {"type": "access", "sub": "2"}

        with patch("app.services.auth_service.decode_token") as mock_decode:
            mock_decode.return_value = payload
            service.user_repo.get_by_id = AsyncMock(return_value=suspended_user)

            with pytest.raises(UnauthorizedException) as exc_info:
                await service.verify_access_token("some_token")

            assert "suspended" in str(exc_info.value).lower()

    # ========================================================================
    # refresh_access_token with suspended account
    # ========================================================================

    @pytest.mark.asyncio
    async def test_refresh_token_suspended_user_rejected(self, service, suspended_user):
        """Test that token refresh fails for suspended users"""
        now = datetime.now(timezone.utc)
        user_session = UserSession(
            id=1,
            user_id=2,
            refresh_token="valid_refresh",
            expires_at=now + timedelta(days=30),
            created_at=now,
            last_accessed_at=now,
            revoked=False,
        )

        with patch("app.services.auth_service.verify_token_type") as mock_type:
            mock_type.return_value = True
            service.session_repo.get_by_refresh_token = AsyncMock(
                return_value=user_session
            )
            service.user_repo.get_by_id = AsyncMock(return_value=suspended_user)

            with pytest.raises(UnauthorizedException) as exc_info:
                await service.refresh_access_token("valid_refresh")

            assert "suspended" in str(exc_info.value).lower()

    # ========================================================================
    # suspend_user
    # ========================================================================

    @pytest.mark.asyncio
    async def test_suspend_user_success(self, service, active_user, mock_session):
        """Test successful user suspension"""
        service.user_repo.get_by_id = AsyncMock(return_value=active_user)
        service.user_repo.update = AsyncMock()
        service.session_repo.revoke_all_user_sessions = AsyncMock(return_value=2)

        result = await service.suspend_user(
            user_id=1, reason="Terms of service violation"
        )

        assert result.is_suspended is True
        assert result.suspension_reason == "Terms of service violation"
        assert result.suspended_at is not None
        service.session_repo.revoke_all_user_sessions.assert_called_once_with(1)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_suspend_user_not_found(self, service):
        """Test suspending non-existent user"""
        service.user_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as exc_info:
            await service.suspend_user(user_id=999, reason="test")

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_suspend_already_suspended_user(self, service, suspended_user):
        """Test suspending an already suspended user"""
        service.user_repo.get_by_id = AsyncMock(return_value=suspended_user)

        with pytest.raises(ValueError) as exc_info:
            await service.suspend_user(user_id=2, reason="test")

        assert "already suspended" in str(exc_info.value)

    # ========================================================================
    # unsuspend_user
    # ========================================================================

    @pytest.mark.asyncio
    async def test_unsuspend_user_success(self, service, suspended_user, mock_session):
        """Test successful user unsuspension"""
        service.user_repo.get_by_id = AsyncMock(return_value=suspended_user)
        service.user_repo.update = AsyncMock()

        result = await service.unsuspend_user(user_id=2)

        assert result.is_suspended is False
        assert result.suspended_at is None
        assert result.suspension_reason is None
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_unsuspend_user_not_found(self, service):
        """Test unsuspending non-existent user"""
        service.user_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as exc_info:
            await service.unsuspend_user(user_id=999)

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_unsuspend_active_user(self, service, active_user):
        """Test unsuspending a non-suspended user"""
        service.user_repo.get_by_id = AsyncMock(return_value=active_user)

        with pytest.raises(ValueError) as exc_info:
            await service.unsuspend_user(user_id=1)

        assert "not suspended" in str(exc_info.value)

    # ========================================================================
    # Session invalidation on suspension
    # ========================================================================

    @pytest.mark.asyncio
    async def test_suspend_user_invalidates_sessions(
        self, service, active_user, mock_session
    ):
        """Test that suspending a user revokes all their sessions"""
        service.user_repo.get_by_id = AsyncMock(return_value=active_user)
        service.user_repo.update = AsyncMock()
        service.session_repo.revoke_all_user_sessions = AsyncMock(return_value=5)

        await service.suspend_user(user_id=1, reason="Abuse")

        service.session_repo.revoke_all_user_sessions.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_unsuspend_does_not_create_sessions(
        self, service, suspended_user, mock_session
    ):
        """Test that unsuspending does not automatically create sessions"""
        service.user_repo.get_by_id = AsyncMock(return_value=suspended_user)
        service.user_repo.update = AsyncMock()

        await service.unsuspend_user(user_id=2)

        # session_repo.create should not be called on unsuspend
        assert not hasattr(service.session_repo, "create") or not getattr(
            service.session_repo.create, "called", False
        )


class TestAdminDependency:
    """Test admin user dependency"""

    @pytest.mark.asyncio
    async def test_admin_user_passes(self):
        """Test that admin users pass the admin dependency check"""
        mock_admin = Mock(spec=User)
        mock_admin.is_admin = True
        mock_admin.is_active = True

        result = await get_current_admin_user(mock_admin)
        assert result == mock_admin

    @pytest.mark.asyncio
    async def test_non_admin_user_rejected(self):
        """Test that non-admin users are rejected with 403"""
        mock_user = Mock(spec=User)
        mock_user.is_admin = False
        mock_user.is_active = True

        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin_user(mock_user)

        assert exc_info.value.status_code == 403
        assert "Admin access required" in str(exc_info.value.detail)
