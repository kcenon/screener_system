"""Unit and integration tests for user session repository"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_session_repository import UserSessionRepository
from app.db.models import UserSession


class TestUserSessionRepository:
    """Test UserSessionRepository"""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        session = Mock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = Mock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance with mock session"""
        return UserSessionRepository(session=mock_session)

    @pytest.fixture
    def sample_session_id(self):
        """Create sample session UUID"""
        return uuid4()

    @pytest.fixture
    def sample_user_session(self, sample_session_id):
        """Create sample user session object"""
        now = datetime.utcnow()
        expires_at = now + timedelta(days=30)

        session = UserSession(
            id=sample_session_id,
            user_id=1,
            refresh_token="sample_refresh_token_12345",
            expires_at=expires_at,
            created_at=now,
            last_accessed_at=now,
            revoked=False,
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )
        return session

    # ========================================================================
    # Initialization Tests
    # ========================================================================

    def test_init(self, mock_session):
        """Test repository initialization"""
        repo = UserSessionRepository(session=mock_session)
        assert repo.session == mock_session

    # ========================================================================
    # get_by_id Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_by_id_found(
        self, repository, mock_session, sample_session_id, sample_user_session
    ):
        """Test get_by_id when session exists"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user_session
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_by_id(sample_session_id)

        # Assert
        assert result == sample_user_session
        assert mock_session.execute.called

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test get_by_id when session does not exist"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_by_id(uuid4())

        # Assert
        assert result is None
        assert mock_session.execute.called

    # ========================================================================
    # get_by_refresh_token Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_by_refresh_token_found(
        self, repository, mock_session, sample_user_session
    ):
        """Test get_by_refresh_token when session exists"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user_session
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_by_refresh_token("sample_refresh_token_12345")

        # Assert
        assert result == sample_user_session
        assert mock_session.execute.called

    @pytest.mark.asyncio
    async def test_get_by_refresh_token_not_found(self, repository, mock_session):
        """Test get_by_refresh_token when session does not exist"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_by_refresh_token("invalid_token")

        # Assert
        assert result is None
        assert mock_session.execute.called

    # ========================================================================
    # get_active_sessions_by_user_id Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_active_sessions_by_user_id_with_sessions(
        self, repository, mock_session, sample_user_session
    ):
        """Test get_active_sessions_by_user_id when active sessions exist"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_user_session]
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_active_sessions_by_user_id(1)

        # Assert
        assert len(result) == 1
        assert result[0] == sample_user_session
        assert mock_session.execute.called

    @pytest.mark.asyncio
    async def test_get_active_sessions_by_user_id_no_sessions(
        self, repository, mock_session
    ):
        """Test get_active_sessions_by_user_id when no active sessions exist"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_active_sessions_by_user_id(1)

        # Assert
        assert len(result) == 0
        assert mock_session.execute.called

    @pytest.mark.asyncio
    async def test_get_active_sessions_by_user_id_with_limit(
        self, repository, mock_session, sample_user_session
    ):
        """Test get_active_sessions_by_user_id with custom limit"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_user_session]
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_active_sessions_by_user_id(1, limit=5)

        # Assert
        assert len(result) == 1
        assert mock_session.execute.called

    # ========================================================================
    # create Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_create_session(
        self, repository, mock_session, sample_user_session
    ):
        """Test creating a new session"""
        # Execute
        result = await repository.create(sample_user_session)

        # Assert
        assert result == sample_user_session
        mock_session.add.assert_called_once_with(sample_user_session)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_user_session)

    # ========================================================================
    # revoke Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_revoke_session(
        self, repository, mock_session, sample_user_session
    ):
        """Test revoking a session"""
        # Setup - mock the revoke method on the session object
        sample_user_session.revoke = Mock()

        # Execute
        result = await repository.revoke(sample_user_session)

        # Assert
        assert result == sample_user_session
        sample_user_session.revoke.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_user_session)

    # ========================================================================
    # revoke_by_refresh_token Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_revoke_by_refresh_token_found(
        self, repository, sample_user_session
    ):
        """Test revoking session by refresh token when session exists"""
        # Mock the methods
        repository.get_by_refresh_token = AsyncMock(return_value=sample_user_session)
        repository.revoke = AsyncMock(return_value=sample_user_session)

        # Execute
        result = await repository.revoke_by_refresh_token("sample_refresh_token_12345")

        # Assert
        assert result is True
        repository.get_by_refresh_token.assert_called_once_with(
            "sample_refresh_token_12345"
        )
        repository.revoke.assert_called_once_with(sample_user_session)

    @pytest.mark.asyncio
    async def test_revoke_by_refresh_token_not_found(self, repository):
        """Test revoking session by refresh token when session does not exist"""
        # Mock the method to return None
        repository.get_by_refresh_token = AsyncMock(return_value=None)

        # Execute
        result = await repository.revoke_by_refresh_token("invalid_token")

        # Assert
        assert result is False
        repository.get_by_refresh_token.assert_called_once_with("invalid_token")

    # ========================================================================
    # revoke_all_user_sessions Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_revoke_all_user_sessions_with_sessions(
        self, repository, sample_user_session
    ):
        """Test revoking all sessions when user has active sessions"""
        # Create multiple sample sessions
        session1 = sample_user_session
        session2 = Mock(spec=UserSession)

        # Mock the methods
        repository.get_active_sessions_by_user_id = AsyncMock(
            return_value=[session1, session2]
        )
        repository.revoke = AsyncMock()

        # Execute
        count = await repository.revoke_all_user_sessions(1)

        # Assert
        assert count == 2
        repository.get_active_sessions_by_user_id.assert_called_once_with(1, limit=100)
        assert repository.revoke.call_count == 2

    @pytest.mark.asyncio
    async def test_revoke_all_user_sessions_no_sessions(self, repository):
        """Test revoking all sessions when user has no active sessions"""
        # Mock the method to return empty list
        repository.get_active_sessions_by_user_id = AsyncMock(return_value=[])

        # Execute
        count = await repository.revoke_all_user_sessions(1)

        # Assert
        assert count == 0
        repository.get_active_sessions_by_user_id.assert_called_once_with(1, limit=100)

    # ========================================================================
    # delete_expired_sessions Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_delete_expired_sessions(self, repository, mock_session):
        """Test deleting expired sessions"""
        # Setup mock
        mock_result = Mock()
        mock_result.rowcount = 5
        mock_session.execute.return_value = mock_result

        # Execute
        count = await repository.delete_expired_sessions()

        # Assert
        assert count == 5
        assert mock_session.execute.called
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_expired_sessions_with_custom_cutoff(
        self, repository, mock_session
    ):
        """Test deleting expired sessions with custom cutoff date"""
        # Setup mock
        mock_result = Mock()
        mock_result.rowcount = 3
        mock_session.execute.return_value = mock_result

        # Execute with custom cutoff
        cutoff = datetime.utcnow() - timedelta(days=60)
        count = await repository.delete_expired_sessions(before=cutoff)

        # Assert
        assert count == 3
        assert mock_session.execute.called

    @pytest.mark.asyncio
    async def test_delete_expired_sessions_none_expired(
        self, repository, mock_session
    ):
        """Test deleting expired sessions when none are expired"""
        # Setup mock
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        # Execute
        count = await repository.delete_expired_sessions()

        # Assert
        assert count == 0
        assert mock_session.execute.called
