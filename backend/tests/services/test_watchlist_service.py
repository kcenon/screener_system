"""Tests for WatchlistService"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.services.watchlist_service import WatchlistService


@pytest.fixture
def mock_session():
    """Create mock database session"""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def watchlist_service(mock_session):
    """Create WatchlistService with mocked dependencies"""
    return WatchlistService(mock_session)


class TestWatchlistServiceInit:
    """Test WatchlistService initialization"""

    def test_init_sets_session(self, mock_session):
        """Test initialization sets session"""
        service = WatchlistService(mock_session)
        assert service.session == mock_session
        assert service.watchlist_repo is not None
        assert service.activity_repo is not None
        assert service.stock_repo is not None


class TestGetUserWatchlists:
    """Test get_user_watchlists method"""

    @pytest.mark.asyncio
    async def test_get_user_watchlists(self, watchlist_service):
        """Test fetching user watchlists"""
        mock_watchlist = MagicMock()
        mock_watchlist.id = uuid4()
        mock_watchlist.name = "Test Watchlist"

        with patch.object(
            watchlist_service.watchlist_repo,
            "get_user_watchlists",
            new_callable=AsyncMock,
            return_value=[mock_watchlist],
        ), patch.object(
            watchlist_service.watchlist_repo,
            "count_user_watchlists",
            new_callable=AsyncMock,
            return_value=1,
        ):
            watchlists, total = await watchlist_service.get_user_watchlists(
                user_id=1, skip=0, limit=10
            )

            assert len(watchlists) == 1
            assert total == 1

    @pytest.mark.asyncio
    async def test_get_user_watchlists_with_stocks(self, watchlist_service):
        """Test fetching user watchlists with stock details"""
        with patch.object(
            watchlist_service.watchlist_repo,
            "get_user_watchlists",
            new_callable=AsyncMock,
            return_value=[],
        ), patch.object(
            watchlist_service.watchlist_repo,
            "count_user_watchlists",
            new_callable=AsyncMock,
            return_value=0,
        ):
            watchlists, total = await watchlist_service.get_user_watchlists(
                user_id=1, load_stocks=True
            )

            watchlist_service.watchlist_repo.get_user_watchlists.assert_called_with(
                user_id=1, skip=0, limit=10, load_stocks=True
            )


class TestGetWatchlistById:
    """Test get_watchlist_by_id method"""

    @pytest.mark.asyncio
    async def test_get_watchlist_by_id(self, watchlist_service):
        """Test fetching watchlist by ID"""
        watchlist_id = uuid4()
        mock_watchlist = MagicMock()
        mock_watchlist.id = watchlist_id

        with patch.object(
            watchlist_service.watchlist_repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ):
            result = await watchlist_service.get_watchlist_by_id(
                watchlist_id=watchlist_id, user_id=1
            )

            assert result == mock_watchlist

    @pytest.mark.asyncio
    async def test_get_watchlist_by_id_not_found(self, watchlist_service):
        """Test fetching non-existent watchlist"""
        with patch.object(
            watchlist_service.watchlist_repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await watchlist_service.get_watchlist_by_id(
                watchlist_id=uuid4(), user_id=1
            )
            assert result is None


class TestCreateWatchlist:
    """Test create_watchlist method"""

    @pytest.mark.asyncio
    async def test_create_watchlist_success(self, watchlist_service, mock_session):
        """Test successful watchlist creation"""
        from app.schemas.watchlist import WatchlistCreate

        mock_watchlist = MagicMock()
        mock_watchlist.id = uuid4()
        mock_watchlist.name = "Test Watchlist"

        with patch.object(
            watchlist_service.watchlist_repo,
            "count_user_watchlists",
            new_callable=AsyncMock,
            return_value=0,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "create",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ), patch.object(
            watchlist_service.activity_repo,
            "create",
            new_callable=AsyncMock,
        ):
            data = WatchlistCreate(name="Test Watchlist", description="Test")
            result = await watchlist_service.create_watchlist(user_id=1, data=data)

            assert result == mock_watchlist
            mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_create_watchlist_limit_exceeded(self, watchlist_service):
        """Test watchlist creation fails when limit exceeded"""
        from app.schemas.watchlist import WatchlistCreate

        with patch.object(
            watchlist_service.watchlist_repo,
            "count_user_watchlists",
            new_callable=AsyncMock,
            return_value=10,  # MAX_WATCHLISTS_PER_USER
        ):
            data = WatchlistCreate(name="Test Watchlist")

            with pytest.raises(ValueError, match="Watchlist limit reached"):
                await watchlist_service.create_watchlist(user_id=1, data=data)

    @pytest.mark.asyncio
    async def test_create_watchlist_invalid_stock_code(self, watchlist_service):
        """Test watchlist creation fails with invalid stock code"""
        from app.schemas.watchlist import WatchlistCreate

        with patch.object(
            watchlist_service.watchlist_repo,
            "count_user_watchlists",
            new_callable=AsyncMock,
            return_value=0,
        ), patch.object(
            watchlist_service.stock_repo,
            "get_by_code",
            new_callable=AsyncMock,
            return_value=None,  # Stock doesn't exist
        ):
            data = WatchlistCreate(name="Test Watchlist", stock_codes=["999999"])

            with pytest.raises(ValueError, match="does not exist"):
                await watchlist_service.create_watchlist(user_id=1, data=data)

    @pytest.mark.asyncio
    async def test_create_watchlist_with_stocks(self, watchlist_service, mock_session):
        """Test watchlist creation with initial stocks"""
        from app.schemas.watchlist import WatchlistCreate

        mock_watchlist = MagicMock()
        mock_watchlist.id = uuid4()
        mock_stock = MagicMock()

        with patch.object(
            watchlist_service.watchlist_repo,
            "count_user_watchlists",
            new_callable=AsyncMock,
            return_value=0,
        ), patch.object(
            watchlist_service.stock_repo,
            "get_by_code",
            new_callable=AsyncMock,
            return_value=mock_stock,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "create",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "add_stock",
            new_callable=AsyncMock,
        ), patch.object(
            watchlist_service.activity_repo,
            "create",
            new_callable=AsyncMock,
        ):
            data = WatchlistCreate(name="Test Watchlist", stock_codes=["005930"])
            result = await watchlist_service.create_watchlist(user_id=1, data=data)

            watchlist_service.watchlist_repo.add_stock.assert_called_once()


class TestUpdateWatchlist:
    """Test update_watchlist method"""

    @pytest.mark.asyncio
    async def test_update_watchlist_success(self, watchlist_service, mock_session):
        """Test successful watchlist update"""
        from app.schemas.watchlist import WatchlistUpdate

        watchlist_id = uuid4()
        mock_watchlist = MagicMock()
        mock_watchlist.id = watchlist_id
        mock_watchlist.name = "Old Name"

        with patch.object(
            watchlist_service.watchlist_repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "update",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ), patch.object(
            watchlist_service.activity_repo,
            "create",
            new_callable=AsyncMock,
        ):
            data = WatchlistUpdate(name="New Name")
            result = await watchlist_service.update_watchlist(
                watchlist_id=watchlist_id, user_id=1, data=data
            )

            assert result == mock_watchlist

    @pytest.mark.asyncio
    async def test_update_watchlist_not_found(self, watchlist_service):
        """Test update fails when watchlist not found"""
        from app.schemas.watchlist import WatchlistUpdate

        with patch.object(
            watchlist_service.watchlist_repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            data = WatchlistUpdate(name="New Name")

            with pytest.raises(ValueError, match="not found"):
                await watchlist_service.update_watchlist(
                    watchlist_id=uuid4(), user_id=1, data=data
                )

    @pytest.mark.asyncio
    async def test_update_watchlist_add_stocks(self, watchlist_service, mock_session):
        """Test adding stocks to watchlist"""
        from app.schemas.watchlist import WatchlistUpdate

        watchlist_id = uuid4()
        mock_watchlist = MagicMock()
        mock_watchlist.id = watchlist_id
        mock_stock = MagicMock()

        with patch.object(
            watchlist_service.watchlist_repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ), patch.object(
            watchlist_service.stock_repo,
            "get_by_code",
            new_callable=AsyncMock,
            return_value=mock_stock,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "stock_in_watchlist",
            new_callable=AsyncMock,
            return_value=False,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "add_stock",
            new_callable=AsyncMock,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "update",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ), patch.object(
            watchlist_service.activity_repo,
            "create",
            new_callable=AsyncMock,
        ):
            data = WatchlistUpdate(add_stocks=["005930"])
            await watchlist_service.update_watchlist(
                watchlist_id=watchlist_id, user_id=1, data=data
            )

            watchlist_service.watchlist_repo.add_stock.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_watchlist_remove_stocks(self, watchlist_service, mock_session):
        """Test removing stocks from watchlist"""
        from app.schemas.watchlist import WatchlistUpdate

        watchlist_id = uuid4()
        mock_watchlist = MagicMock()
        mock_watchlist.id = watchlist_id

        with patch.object(
            watchlist_service.watchlist_repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "remove_stock",
            new_callable=AsyncMock,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "update",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ), patch.object(
            watchlist_service.activity_repo,
            "create",
            new_callable=AsyncMock,
        ):
            data = WatchlistUpdate(remove_stocks=["005930"])
            await watchlist_service.update_watchlist(
                watchlist_id=watchlist_id, user_id=1, data=data
            )

            watchlist_service.watchlist_repo.remove_stock.assert_called_once()


class TestDeleteWatchlist:
    """Test delete_watchlist method"""

    @pytest.mark.asyncio
    async def test_delete_watchlist_success(self, watchlist_service, mock_session):
        """Test successful watchlist deletion"""
        watchlist_id = uuid4()
        mock_watchlist = MagicMock()
        mock_watchlist.id = watchlist_id
        mock_watchlist.name = "Test Watchlist"

        with patch.object(
            watchlist_service.watchlist_repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "delete",
            new_callable=AsyncMock,
        ), patch.object(
            watchlist_service.activity_repo,
            "create",
            new_callable=AsyncMock,
        ):
            await watchlist_service.delete_watchlist(
                watchlist_id=watchlist_id, user_id=1
            )

            watchlist_service.watchlist_repo.delete.assert_called_once()
            mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_delete_watchlist_not_found(self, watchlist_service):
        """Test delete fails when watchlist not found"""
        with patch.object(
            watchlist_service.watchlist_repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(ValueError, match="not found"):
                await watchlist_service.delete_watchlist(
                    watchlist_id=uuid4(), user_id=1
                )


class TestAddStockToWatchlist:
    """Test add_stock_to_watchlist method"""

    @pytest.mark.asyncio
    async def test_add_stock_success(self, watchlist_service, mock_session):
        """Test successful stock addition"""
        watchlist_id = uuid4()
        mock_watchlist = MagicMock()
        mock_watchlist.id = watchlist_id
        mock_stock = MagicMock()
        mock_stock.name = "삼성전자"
        mock_watchlist_stock = MagicMock()

        with patch.object(
            watchlist_service.watchlist_repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ), patch.object(
            watchlist_service.stock_repo,
            "get_by_code",
            new_callable=AsyncMock,
            return_value=mock_stock,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "add_stock",
            new_callable=AsyncMock,
            return_value=mock_watchlist_stock,
        ), patch.object(
            watchlist_service.activity_repo,
            "create",
            new_callable=AsyncMock,
        ):
            result = await watchlist_service.add_stock_to_watchlist(
                watchlist_id=watchlist_id, user_id=1, stock_code="005930"
            )

            assert result == mock_watchlist_stock

    @pytest.mark.asyncio
    async def test_add_stock_watchlist_not_found(self, watchlist_service):
        """Test add stock fails when watchlist not found"""
        with patch.object(
            watchlist_service.watchlist_repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(ValueError, match="not found"):
                await watchlist_service.add_stock_to_watchlist(
                    watchlist_id=uuid4(), user_id=1, stock_code="005930"
                )

    @pytest.mark.asyncio
    async def test_add_stock_invalid_stock_code(self, watchlist_service):
        """Test add stock fails with invalid stock code"""
        mock_watchlist = MagicMock()

        with patch.object(
            watchlist_service.watchlist_repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ), patch.object(
            watchlist_service.stock_repo,
            "get_by_code",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(ValueError, match="does not exist"):
                await watchlist_service.add_stock_to_watchlist(
                    watchlist_id=uuid4(), user_id=1, stock_code="999999"
                )


class TestRemoveStockFromWatchlist:
    """Test remove_stock_from_watchlist method"""

    @pytest.mark.asyncio
    async def test_remove_stock_success(self, watchlist_service, mock_session):
        """Test successful stock removal"""
        watchlist_id = uuid4()
        mock_watchlist = MagicMock()
        mock_watchlist.id = watchlist_id

        with patch.object(
            watchlist_service.watchlist_repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "remove_stock",
            new_callable=AsyncMock,
            return_value=1,  # 1 row deleted
        ), patch.object(
            watchlist_service.activity_repo,
            "create",
            new_callable=AsyncMock,
        ):
            await watchlist_service.remove_stock_from_watchlist(
                watchlist_id=watchlist_id, user_id=1, stock_code="005930"
            )

            watchlist_service.watchlist_repo.remove_stock.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_stock_not_in_watchlist(self, watchlist_service):
        """Test remove fails when stock not in watchlist"""
        watchlist_id = uuid4()
        mock_watchlist = MagicMock()

        with patch.object(
            watchlist_service.watchlist_repo,
            "get_by_id",
            new_callable=AsyncMock,
            return_value=mock_watchlist,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "remove_stock",
            new_callable=AsyncMock,
            return_value=0,  # 0 rows deleted
        ):
            with pytest.raises(ValueError, match="not found in watchlist"):
                await watchlist_service.remove_stock_from_watchlist(
                    watchlist_id=watchlist_id, user_id=1, stock_code="005930"
                )


class TestLogActivity:
    """Test log_activity method"""

    @pytest.mark.asyncio
    async def test_log_activity(self, watchlist_service):
        """Test logging user activity"""
        mock_activity = MagicMock()

        with patch.object(
            watchlist_service.activity_repo,
            "create",
            new_callable=AsyncMock,
            return_value=mock_activity,
        ):
            result = await watchlist_service.log_activity(
                user_id=1,
                activity_type="test",
                description="Test activity",
                activity_metadata={"key": "value"},
            )

            assert result == mock_activity
            watchlist_service.activity_repo.create.assert_called_once()


class TestGetRecentActivities:
    """Test get_recent_activities method"""

    @pytest.mark.asyncio
    async def test_get_recent_activities(self, watchlist_service):
        """Test fetching recent activities"""
        mock_activity = MagicMock()

        with patch.object(
            watchlist_service.activity_repo,
            "get_user_activities",
            new_callable=AsyncMock,
            return_value=[mock_activity],
        ), patch.object(
            watchlist_service.activity_repo,
            "count_user_activities",
            new_callable=AsyncMock,
            return_value=1,
        ):
            activities, total = await watchlist_service.get_recent_activities(
                user_id=1, limit=10
            )

            assert len(activities) == 1
            assert total == 1


class TestGetDashboardSummary:
    """Test get_dashboard_summary method"""

    @pytest.mark.asyncio
    async def test_get_dashboard_summary(self, watchlist_service, mock_session):
        """Test fetching dashboard summary"""
        mock_watchlist = MagicMock()
        mock_watchlist.id = uuid4()
        mock_activity = MagicMock()
        mock_activity.created_at = datetime.now()
        mock_prefs = MagicMock()
        mock_prefs.screening_quota_used = 5
        mock_prefs.screening_quota_reset_at = datetime.now() + timedelta(days=30)

        with patch.object(
            watchlist_service.watchlist_repo,
            "count_user_watchlists",
            new_callable=AsyncMock,
            return_value=2,
        ), patch.object(
            watchlist_service.watchlist_repo,
            "get_user_watchlists",
            new_callable=AsyncMock,
            return_value=[mock_watchlist],
        ), patch.object(
            watchlist_service.watchlist_repo,
            "get_watchlist_stocks",
            new_callable=AsyncMock,
            return_value=["005930", "000660"],
        ), patch.object(
            watchlist_service.activity_repo,
            "count_user_activities",
            new_callable=AsyncMock,
            return_value=10,
        ), patch.object(
            watchlist_service.activity_repo,
            "get_user_activities",
            new_callable=AsyncMock,
            return_value=[mock_activity],
        ), patch(
            "app.services.watchlist_service.UserPreferencesRepository"
        ) as mock_prefs_repo_class:
            mock_prefs_repo = AsyncMock()
            mock_prefs_repo.get_by_user_id.return_value = mock_prefs
            mock_prefs_repo_class.return_value = mock_prefs_repo

            result = await watchlist_service.get_dashboard_summary(
                user_id=1, user_tier="free"
            )

            assert result.watchlist_count == 2
            assert result.total_stocks == 2
            assert result.recent_activity_count == 10
            assert result.subscription_tier == "free"
