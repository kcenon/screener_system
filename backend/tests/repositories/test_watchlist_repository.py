"""Unit tests for Watchlist Repository"""

import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select

from app.db.models import Stock, User, UserActivity, UserPreferences, Watchlist, WatchlistStock
from app.repositories.watchlist_repository import (
    UserActivityRepository,
    UserPreferencesRepository,
    WatchlistRepository,
)


@pytest.fixture
async def test_user(db):
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        full_name="Test User",
        subscription_tier="free",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def test_stocks(db):
    """Create test stocks"""
    stocks = [
        Stock(
            code="005930",
            name="Samsung Electronics",
            market="KOSPI",
            sector="Technology",
        ),
        Stock(
            code="000660",
            name="SK Hynix",
            market="KOSPI",
            sector="Technology",
        ),
        Stock(
            code="035420",
            name="NAVER",
            market="KOSPI",
            sector="IT Services",
        ),
    ]
    for stock in stocks:
        db.add(stock)
    await db.commit()
    return stocks


@pytest.fixture
def watchlist_repo(db):
    """Create WatchlistRepository instance"""
    return WatchlistRepository(db)


@pytest.fixture
def activity_repo(db):
    """Create UserActivityRepository instance"""
    return UserActivityRepository(db)


@pytest.fixture
def preferences_repo(db):
    """Create UserPreferencesRepository instance"""
    return UserPreferencesRepository(db)


# =============================================================================
# WATCHLIST REPOSITORY TESTS
# =============================================================================


class TestWatchlistRepository:
    """Test WatchlistRepository CRUD operations"""

    async def test_create_watchlist(self, db, watchlist_repo, test_user):
        """Test creating a watchlist"""
        watchlist = Watchlist(
            user_id=test_user.id,
            name="My Tech Stocks",
            description="Technology stocks to watch",
        )

        created = await watchlist_repo.create(watchlist)
        await db.commit()

        assert created.id is not None
        assert created.user_id == test_user.id
        assert created.name == "My Tech Stocks"
        assert created.description == "Technology stocks to watch"
        assert created.created_at is not None

    async def test_get_by_id(self, db, watchlist_repo, test_user):
        """Test getting watchlist by ID"""
        # Create watchlist
        watchlist = Watchlist(user_id=test_user.id, name="Test Watchlist")
        created = await watchlist_repo.create(watchlist)
        await db.commit()

        # Get by ID
        retrieved = await watchlist_repo.get_by_id(created.id, test_user.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Watchlist"

    async def test_get_by_id_wrong_user(self, db, watchlist_repo, test_user):
        """Test that getting watchlist with wrong user_id returns None"""
        watchlist = Watchlist(user_id=test_user.id, name="Test Watchlist")
        created = await watchlist_repo.create(watchlist)
        await db.commit()

        # Try to get with different user_id
        wrong_user_id = 99999
        retrieved = await watchlist_repo.get_by_id(created.id, wrong_user_id)

        assert retrieved is None

    async def test_get_user_watchlists(self, db, watchlist_repo, test_user):
        """Test getting all watchlists for a user"""
        # Create multiple watchlists
        for i in range(3):
            watchlist = Watchlist(
                user_id=test_user.id,
                name=f"Watchlist {i}",
            )
            await watchlist_repo.create(watchlist)
        await db.commit()

        # Get all watchlists
        watchlists = await watchlist_repo.get_user_watchlists(test_user.id)

        assert len(watchlists) == 3
        assert all(w.user_id == test_user.id for w in watchlists)

    async def test_get_user_watchlists_pagination(self, db, watchlist_repo, test_user):
        """Test pagination for user watchlists"""
        # Create 5 watchlists
        for i in range(5):
            watchlist = Watchlist(user_id=test_user.id, name=f"Watchlist {i}")
            await watchlist_repo.create(watchlist)
        await db.commit()

        # Get first 3
        page1 = await watchlist_repo.get_user_watchlists(test_user.id, skip=0, limit=3)
        assert len(page1) == 3

        # Get next 2
        page2 = await watchlist_repo.get_user_watchlists(test_user.id, skip=3, limit=3)
        assert len(page2) == 2

    async def test_count_user_watchlists(self, db, watchlist_repo, test_user):
        """Test counting user watchlists"""
        # Initially should be 0
        count = await watchlist_repo.count_user_watchlists(test_user.id)
        assert count == 0

        # Create 3 watchlists
        for i in range(3):
            watchlist = Watchlist(user_id=test_user.id, name=f"Watchlist {i}")
            await watchlist_repo.create(watchlist)
        await db.commit()

        # Should be 3
        count = await watchlist_repo.count_user_watchlists(test_user.id)
        assert count == 3

    async def test_update_watchlist(self, db, watchlist_repo, test_user):
        """Test updating a watchlist"""
        watchlist = Watchlist(user_id=test_user.id, name="Original Name")
        created = await watchlist_repo.create(watchlist)
        await db.commit()

        # Update name
        created.name = "Updated Name"
        created.description = "New description"
        updated = await watchlist_repo.update(created)
        await db.commit()

        assert updated.name == "Updated Name"
        assert updated.description == "New description"

    async def test_delete_watchlist(self, db, watchlist_repo, test_user):
        """Test deleting a watchlist"""
        watchlist = Watchlist(user_id=test_user.id, name="To Delete")
        created = await watchlist_repo.create(watchlist)
        await db.commit()

        watchlist_id = created.id

        # Delete
        await watchlist_repo.delete(created)
        await db.commit()

        # Verify deleted
        retrieved = await watchlist_repo.get_by_id(watchlist_id, test_user.id)
        assert retrieved is None

    async def test_add_stock(self, db, watchlist_repo, test_user, test_stocks):
        """Test adding stock to watchlist"""
        watchlist = Watchlist(user_id=test_user.id, name="Test")
        created = await watchlist_repo.create(watchlist)
        await db.commit()

        # Add stock
        ws = await watchlist_repo.add_stock(created.id, "005930", notes="Great stock")
        await db.commit()

        assert ws.watchlist_id == created.id
        assert ws.stock_code == "005930"
        assert ws.notes == "Great stock"
        assert ws.added_at is not None

    async def test_remove_stock(self, db, watchlist_repo, test_user, test_stocks):
        """Test removing stock from watchlist"""
        watchlist = Watchlist(user_id=test_user.id, name="Test")
        created = await watchlist_repo.create(watchlist)
        await db.commit()

        # Add stock
        await watchlist_repo.add_stock(created.id, "005930")
        await db.commit()

        # Remove stock
        removed_count = await watchlist_repo.remove_stock(created.id, "005930")

        assert removed_count == 1

    async def test_remove_nonexistent_stock(self, db, watchlist_repo, test_user):
        """Test removing stock that doesn't exist in watchlist"""
        watchlist = Watchlist(user_id=test_user.id, name="Test")
        created = await watchlist_repo.create(watchlist)
        await db.commit()

        # Try to remove stock that was never added
        removed_count = await watchlist_repo.remove_stock(created.id, "005930")

        assert removed_count == 0

    async def test_get_watchlist_stocks(self, db, watchlist_repo, test_user, test_stocks):
        """Test getting all stocks in a watchlist"""
        watchlist = Watchlist(user_id=test_user.id, name="Test")
        created = await watchlist_repo.create(watchlist)
        await db.commit()

        # Add multiple stocks
        await watchlist_repo.add_stock(created.id, "005930")
        await watchlist_repo.add_stock(created.id, "000660")
        await db.commit()

        # Get all stocks
        stocks = await watchlist_repo.get_watchlist_stocks(created.id)

        assert len(stocks) == 2
        stock_codes = [s.stock_code for s in stocks]
        assert "005930" in stock_codes
        assert "000660" in stock_codes

    async def test_stock_in_watchlist(self, db, watchlist_repo, test_user, test_stocks):
        """Test checking if stock exists in watchlist"""
        watchlist = Watchlist(user_id=test_user.id, name="Test")
        created = await watchlist_repo.create(watchlist)
        await db.commit()

        # Add stock
        await watchlist_repo.add_stock(created.id, "005930")
        await db.commit()

        # Check existence
        exists = await watchlist_repo.stock_in_watchlist(created.id, "005930")
        not_exists = await watchlist_repo.stock_in_watchlist(created.id, "000660")

        assert exists is True
        assert not_exists is False


# =============================================================================
# USER ACTIVITY REPOSITORY TESTS
# =============================================================================


class TestUserActivityRepository:
    """Test UserActivityRepository operations"""

    async def test_create_activity(self, db, activity_repo, test_user):
        """Test creating user activity log"""
        activity = UserActivity(
            user_id=test_user.id,
            activity_type="screening",
            description="Screened stocks with PER < 10",
            activity_metadata={"filter": "PER < 10"},
        )

        created = await activity_repo.create(activity)
        await db.commit()

        assert created.id is not None
        assert created.user_id == test_user.id
        assert created.activity_type == "screening"
        assert created.description == "Screened stocks with PER < 10"

    async def test_get_user_activities(self, db, activity_repo, test_user):
        """Test getting user activities"""
        # Create multiple activities
        for i in range(5):
            activity = UserActivity(
                user_id=test_user.id,
                activity_type="screening",
                description=f"Activity {i}",
            )
            await activity_repo.create(activity)
        await db.commit()

        # Get activities
        activities = await activity_repo.get_user_activities(test_user.id, limit=10)

        assert len(activities) == 5

    async def test_get_user_activities_with_limit(self, db, activity_repo, test_user):
        """Test getting user activities with limit"""
        # Create 10 activities
        for i in range(10):
            activity = UserActivity(
                user_id=test_user.id,
                activity_type="screening",
                description=f"Activity {i}",
            )
            await activity_repo.create(activity)
        await db.commit()

        # Get only 5
        activities = await activity_repo.get_user_activities(test_user.id, limit=5)

        assert len(activities) == 5

    async def test_get_user_activities_by_type(self, db, activity_repo, test_user):
        """Test filtering activities by type"""
        # Create different types of activities
        screening = UserActivity(
            user_id=test_user.id,
            activity_type="screening",
            description="Screening",
        )
        watchlist = UserActivity(
            user_id=test_user.id,
            activity_type="watchlist_create",
            description="Created watchlist",
        )
        await activity_repo.create(screening)
        await activity_repo.create(watchlist)
        await db.commit()

        # Filter by type
        screenings = await activity_repo.get_user_activities(
            test_user.id, activity_type="screening"
        )

        assert len(screenings) == 1
        assert screenings[0].activity_type == "screening"

    async def test_count_user_activities(self, db, activity_repo, test_user):
        """Test counting user activities"""
        # Create 5 activities
        for i in range(5):
            activity = UserActivity(
                user_id=test_user.id,
                activity_type="screening",
                description=f"Activity {i}",
            )
            await activity_repo.create(activity)
        await db.commit()

        count = await activity_repo.count_user_activities(test_user.id)

        assert count == 5

    async def test_get_recent_screenings(self, db, activity_repo, test_user):
        """Test getting recent screening activities"""
        # Create mixed activities
        for i in range(3):
            screening = UserActivity(
                user_id=test_user.id,
                activity_type="screening",
                description=f"Screening {i}",
            )
            await activity_repo.create(screening)

        watchlist = UserActivity(
            user_id=test_user.id,
            activity_type="watchlist_create",
            description="Watchlist created",
        )
        await activity_repo.create(watchlist)
        await db.commit()

        # Get only screenings
        screenings = await activity_repo.get_recent_screenings(test_user.id)

        assert len(screenings) == 3
        assert all(a.activity_type == "screening" for a in screenings)


# =============================================================================
# USER PREFERENCES REPOSITORY TESTS
# =============================================================================


class TestUserPreferencesRepository:
    """Test UserPreferencesRepository operations"""

    async def test_create_preferences(self, db, preferences_repo, test_user):
        """Test creating user preferences"""
        reset_at = datetime.now() + timedelta(days=30)
        prefs = UserPreferences(
            user_id=test_user.id,
            screening_quota_used=0,
            screening_quota_reset_at=reset_at,
        )

        created = await preferences_repo.create(prefs)
        await db.commit()

        assert created.user_id == test_user.id
        assert created.screening_quota_used == 0

    async def test_get_by_user_id(self, db, preferences_repo, test_user):
        """Test getting preferences by user ID"""
        reset_at = datetime.now() + timedelta(days=30)
        prefs = UserPreferences(
            user_id=test_user.id,
            screening_quota_used=0,
            screening_quota_reset_at=reset_at,
        )
        await preferences_repo.create(prefs)
        await db.commit()

        retrieved = await preferences_repo.get_by_user_id(test_user.id)

        assert retrieved is not None
        assert retrieved.user_id == test_user.id

    async def test_update_preferences(self, db, preferences_repo, test_user):
        """Test updating preferences"""
        reset_at = datetime.now() + timedelta(days=30)
        prefs = UserPreferences(
            user_id=test_user.id,
            screening_quota_used=0,
            screening_quota_reset_at=reset_at,
        )
        created = await preferences_repo.create(prefs)
        await db.commit()

        # Update
        created.screening_quota_used = 10
        updated = await preferences_repo.update(created)
        await db.commit()

        assert updated.screening_quota_used == 10

    async def test_increment_screening_quota(self, db, preferences_repo, test_user):
        """Test incrementing screening quota"""
        reset_at = datetime.now() + timedelta(days=30)
        prefs = UserPreferences(
            user_id=test_user.id,
            screening_quota_used=0,
            screening_quota_reset_at=reset_at,
        )
        await preferences_repo.create(prefs)
        await db.commit()

        # Increment
        await preferences_repo.increment_screening_quota(test_user.id)
        await db.commit()

        # Verify
        updated = await preferences_repo.get_by_user_id(test_user.id)
        assert updated.screening_quota_used == 1

    async def test_reset_screening_quota(self, db, preferences_repo, test_user):
        """Test resetting screening quota"""
        reset_at = datetime.now() + timedelta(days=30)
        prefs = UserPreferences(
            user_id=test_user.id,
            screening_quota_used=50,
            screening_quota_reset_at=reset_at,
        )
        await preferences_repo.create(prefs)
        await db.commit()

        # Reset
        await preferences_repo.reset_screening_quota(test_user.id)
        await db.commit()

        # Verify
        updated = await preferences_repo.get_by_user_id(test_user.id)
        assert updated.screening_quota_used == 0
        assert updated.screening_quota_reset_at > datetime.now()
