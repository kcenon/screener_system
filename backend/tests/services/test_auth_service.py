"""Unit tests for authentication service"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.services.auth_service import AuthService
from app.db.models import User, UserSession
from app.schemas import TokenResponse, UserCreate, UserLogin


class TestAuthService:
    """Test AuthService"""

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
    def sample_user(self):
        """Create sample user object"""
        now = datetime.now(timezone.utc)
        user = User(
            id=1,
            email="test@example.com",
            password_hash="$2b$12$abcdefghijklmnopqrstuv",  # bcrypt hash format
            name="Test User",
            subscription_tier="free",
            email_verified=False,
            created_at=now,
            updated_at=now,
        )
        return user

    @pytest.fixture
    def sample_user_session(self):
        """Create sample user session object"""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=30)

        session = UserSession(
            id=uuid4(),
            user_id=1,
            refresh_token="sample_refresh_token",
            expires_at=expires_at,
            created_at=now,
            last_accessed_at=now,
            revoked=False,
        )
        return session

    # ========================================================================
    # register_user Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_register_user_success(self, service, mock_session):
        """Test successful user registration"""
        # Setup
        user_data = UserCreate(
            email="newuser@example.com",
            password="SecurePassword123!",
            name="New User",
        )

        # Mock to simulate database setting the ID on flush
        async def mock_create_user(user):
            now = datetime.now(timezone.utc)
            user.id = 2
            user.email_verified = False
            user.created_at = now
            user.updated_at = now
            return user

        # Mock repository methods
        service.user_repo.get_by_email = AsyncMock(return_value=None)
        service.user_repo.create = AsyncMock(side_effect=mock_create_user)

        with patch("app.services.auth_service.get_password_hash") as mock_hash, patch(
            "app.services.auth_service.create_access_token"
        ) as mock_access, patch(
            "app.services.auth_service.create_refresh_token"
        ) as mock_refresh:

            mock_hash.return_value = "hashed_password"
            mock_access.return_value = "access_token_abc"
            mock_refresh.return_value = "refresh_token_xyz"

            service.session_repo.create = AsyncMock()

            # Execute
            result = await service.register_user(
                user_data, ip_address="127.0.0.1", user_agent="TestAgent"
            )

            # Assert
            assert isinstance(result, TokenResponse)
            assert result.access_token == "access_token_abc"
            assert result.refresh_token == "refresh_token_xyz"
            assert result.user.email == "newuser@example.com"
            service.user_repo.create.assert_called_once()
            mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_register_user_email_already_exists(self, service, sample_user):
        """Test registration with existing email raises ValueError"""
        # Setup
        user_data = UserCreate(
            email="test@example.com",
            password="SecurePassword123!",
            name="Test User",
        )

        # Mock repository to return existing user
        service.user_repo.get_by_email = AsyncMock(return_value=sample_user)

        # Execute and assert
        with pytest.raises(ValueError) as exc_info:
            await service.register_user(user_data)

        assert "already registered" in str(exc_info.value)

    # ========================================================================
    # authenticate_user Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, service, sample_user, mock_session):
        """Test successful user authentication"""
        # Setup
        credentials = UserLogin(email="test@example.com", password="password123")

        # Mock repository and security functions
        service.user_repo.get_by_email = AsyncMock(return_value=sample_user)
        service.user_repo.update = AsyncMock()

        with patch("app.services.auth_service.verify_password") as mock_verify, patch(
            "app.services.auth_service.create_access_token"
        ) as mock_access, patch(
            "app.services.auth_service.create_refresh_token"
        ) as mock_refresh:

            mock_verify.return_value = True
            mock_access.return_value = "access_token_abc"
            mock_refresh.return_value = "refresh_token_xyz"

            service.session_repo.create = AsyncMock()

            # Execute
            result = await service.authenticate_user(credentials)

            # Assert
            assert isinstance(result, TokenResponse)
            assert result.access_token == "access_token_abc"
            assert result.refresh_token == "refresh_token_xyz"
            service.user_repo.update.assert_called_once()
            mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_email(self, service):
        """Test authentication with non-existent email"""
        # Setup
        credentials = UserLogin(email="invalid@example.com", password="password123")

        # Mock repository to return None (user not found)
        service.user_repo.get_by_email = AsyncMock(return_value=None)

        # Execute and assert
        with pytest.raises(UnauthorizedException) as exc_info:
            await service.authenticate_user(credentials)

        assert "Invalid email or password" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self, service, sample_user):
        """Test authentication with incorrect password"""
        # Setup
        credentials = UserLogin(email="test@example.com", password="wrong_password")

        # Mock repository and security functions
        service.user_repo.get_by_email = AsyncMock(return_value=sample_user)

        with patch("app.services.auth_service.verify_password") as mock_verify:
            mock_verify.return_value = False

            # Execute and assert
            with pytest.raises(UnauthorizedException) as exc_info:
                await service.authenticate_user(credentials)

            assert "Invalid email or password" in str(exc_info.value)

    # ========================================================================
    # refresh_access_token Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_refresh_access_token_success(
        self, service, sample_user, sample_user_session, mock_session
    ):
        """Test successful access token refresh"""
        # Setup
        refresh_token = "valid_refresh_token"

        # Mock functions and repositories
        with patch(
            "app.services.auth_service.verify_token_type"
        ) as mock_verify_type, patch(
            "app.services.auth_service.create_access_token"
        ) as mock_access:

            mock_verify_type.return_value = True
            mock_access.return_value = "new_access_token"

            service.session_repo.get_by_refresh_token = AsyncMock(
                return_value=sample_user_session
            )
            service.session_repo.create = AsyncMock()
            service.user_repo.get_by_id = AsyncMock(return_value=sample_user)

            # Execute
            access_token, user_response = await service.refresh_access_token(
                refresh_token
            )

            # Assert
            assert access_token == "new_access_token"
            assert user_response.email == "test@example.com"
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_access_token_invalid_type(self, service):
        """Test refresh with invalid token type"""
        # Setup
        with patch("app.services.auth_service.verify_token_type") as mock_verify_type:
            mock_verify_type.return_value = False

            # Execute and assert
            with pytest.raises(UnauthorizedException) as exc_info:
                await service.refresh_access_token("invalid_token")

            assert "Invalid refresh token type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_refresh_access_token_not_found(self, service):
        """Test refresh with non-existent token"""
        # Setup
        with patch("app.services.auth_service.verify_token_type") as mock_verify_type:
            mock_verify_type.return_value = True

            service.session_repo.get_by_refresh_token = AsyncMock(return_value=None)

            # Execute and assert
            with pytest.raises(UnauthorizedException) as exc_info:
                await service.refresh_access_token("non_existent_token")

            assert "Invalid refresh token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_refresh_access_token_revoked_session(
        self, service, sample_user_session
    ):
        """Test refresh with revoked session"""
        # Setup
        sample_user_session.revoked = True

        with patch("app.services.auth_service.verify_token_type") as mock_verify_type:
            mock_verify_type.return_value = True

            service.session_repo.get_by_refresh_token = AsyncMock(
                return_value=sample_user_session
            )

            # Execute and assert
            with pytest.raises(UnauthorizedException) as exc_info:
                await service.refresh_access_token("revoked_token")

            assert "revoked or expired" in str(exc_info.value)

    # ========================================================================
    # logout Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_logout_success(self, service, mock_session):
        """Test successful logout"""
        # Setup
        refresh_token = "valid_refresh_token"
        service.session_repo.revoke_by_refresh_token = AsyncMock(return_value=True)

        # Execute
        result = await service.logout(refresh_token)

        # Assert
        assert result is True
        service.session_repo.revoke_by_refresh_token.assert_called_once_with(
            refresh_token
        )
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_logout_token_not_found(self, service, mock_session):
        """Test logout with non-existent token"""
        # Setup
        service.session_repo.revoke_by_refresh_token = AsyncMock(return_value=False)

        # Execute
        result = await service.logout("invalid_token")

        # Assert
        assert result is False
        # Commit should not be called if revocation failed
        mock_session.commit.assert_not_called()

    # ========================================================================
    # logout_all_sessions Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_logout_all_sessions(self, service, mock_session):
        """Test logging out all user sessions"""
        # Setup
        service.session_repo.revoke_all_user_sessions = AsyncMock(return_value=3)

        # Execute
        count = await service.logout_all_sessions(user_id=1)

        # Assert
        assert count == 3
        service.session_repo.revoke_all_user_sessions.assert_called_once_with(1)
        mock_session.commit.assert_called_once()

    # ========================================================================
    # get_user_by_id Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_user_by_id_found(self, service, sample_user):
        """Test getting user by ID when user exists"""
        # Setup
        service.user_repo.get_by_id = AsyncMock(return_value=sample_user)

        # Execute
        result = await service.get_user_by_id(1)

        # Assert
        assert result == sample_user

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, service):
        """Test getting user by ID when user does not exist"""
        # Setup
        service.user_repo.get_by_id = AsyncMock(return_value=None)

        # Execute
        result = await service.get_user_by_id(999)

        # Assert
        assert result is None

    # ========================================================================
    # verify_access_token Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_verify_access_token_success(self, service, sample_user):
        """Test successful access token verification"""
        # Setup
        access_token = "valid_access_token"
        payload = {"type": "access", "sub": "1"}

        with patch("app.services.auth_service.decode_token") as mock_decode:
            mock_decode.return_value = payload

            service.user_repo.get_by_id = AsyncMock(return_value=sample_user)

            # Execute
            result = await service.verify_access_token(access_token)

            # Assert
            assert result == sample_user

    @pytest.mark.asyncio
    async def test_verify_access_token_invalid_type(self, service):
        """Test verification with invalid token type"""
        # Setup
        payload = {"type": "refresh", "sub": "1"}

        with patch("app.services.auth_service.decode_token") as mock_decode:
            mock_decode.return_value = payload

            # Execute and assert
            with pytest.raises(UnauthorizedException) as exc_info:
                await service.verify_access_token("invalid_type_token")

            assert "Invalid token type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_access_token_missing_subject(self, service):
        """Test verification with missing subject in payload"""
        # Setup
        payload = {"type": "access"}  # Missing 'sub'

        with patch("app.services.auth_service.decode_token") as mock_decode:
            mock_decode.return_value = payload

            # Execute and assert
            with pytest.raises(UnauthorizedException) as exc_info:
                await service.verify_access_token("invalid_payload_token")

            assert "Invalid token payload" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_access_token_user_not_found(self, service):
        """Test verification when user no longer exists"""
        # Setup
        payload = {"type": "access", "sub": "999"}

        with patch("app.services.auth_service.decode_token") as mock_decode:
            mock_decode.return_value = payload

            service.user_repo.get_by_id = AsyncMock(return_value=None)

            # Execute and assert
            with pytest.raises(UnauthorizedException) as exc_info:
                await service.verify_access_token("orphan_token")

            assert "User not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_access_token_jwt_error(self, service):
        """Test verification with JWT decode error"""
        # Setup
        with patch("app.services.auth_service.decode_token") as mock_decode:
            mock_decode.side_effect = JWTError("Invalid token")

            # Execute and assert
            with pytest.raises(UnauthorizedException) as exc_info:
                await service.verify_access_token("malformed_token")

            assert "Invalid token" in str(exc_info.value)
