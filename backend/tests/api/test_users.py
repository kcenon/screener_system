"""Integration tests for User Portfolio API endpoints"""

import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.db.models import Stock, User, UserPreferences, Watchlist, WatchlistStock


@pytest.fixture
async def test_user(db):
    """Create test user"""
    from app.core.security import get_password_hash

    user = User(
        email="test@example.com",
        password_hash=get_password_hash("password"),
        name="Test User",
        subscription_tier="free",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def test_user_preferences(db, test_user):
    """Create test user preferences"""
    reset_at = datetime.now() + timedelta(days=30)
    prefs = UserPreferences(
        user_id=test_user.id,
        screening_quota_used=0,
        screening_quota_reset_at=reset_at,
    )
    db.add(prefs)
    await db.commit()
    return prefs


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
async def auth_headers(client: AsyncClient, test_user):
    """Get authentication headers"""
    # Login to get access token
    response = await client.post(
        "/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password",
        },
    )
    assert response.status_code == 200
    data = response.json()
    access_token = data["access_token"]

    return {"Authorization": f"Bearer {access_token}"}


# =============================================================================
# WATCHLIST ENDPOINTS TESTS
# =============================================================================


class TestWatchlistEndpoints:
    """Test Watchlist API endpoints"""

    async def test_list_watchlists_empty(
        self, client: AsyncClient, auth_headers, test_user
    ):
        """Test listing watchlists when user has none"""
        response = await client.get("/v1/users/watchlists", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["watchlists"] == []

    async def test_create_watchlist(
        self, client: AsyncClient, auth_headers, db, test_user
    ):
        """Test creating a watchlist"""
        response = await client.post(
            "/v1/users/watchlists",
            headers=auth_headers,
            json={
                "name": "My Tech Stocks",
                "description": "Technology stocks to watch",
                "stock_codes": [],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Tech Stocks"
        assert data["description"] == "Technology stocks to watch"
        assert data["stock_count"] == 0
        assert "id" in data
        assert data["user_id"] == test_user.id

    async def test_create_watchlist_with_stocks(
        self, client: AsyncClient, auth_headers, db, test_user, test_stocks
    ):
        """Test creating watchlist with initial stocks"""
        response = await client.post(
            "/v1/users/watchlists",
            headers=auth_headers,
            json={
                "name": "Tech Watchlist",
                "description": "Top tech stocks",
                "stock_codes": ["005930", "000660"],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["stock_count"] == 2

    async def test_create_watchlist_invalid_stock_code(
        self, client: AsyncClient, auth_headers, test_user
    ):
        """Test creating watchlist with non-existent stock code"""
        response = await client.post(
            "/v1/users/watchlists",
            headers=auth_headers,
            json={
                "name": "Invalid Watchlist",
                "stock_codes": ["999999"],  # Non-existent stock
            },
        )

        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"]

    async def test_create_watchlist_exceeds_limit(
        self, client: AsyncClient, auth_headers, db, test_user
    ):
        """Test exceeding watchlist limit (max 10)"""
        # Create 10 watchlists
        for i in range(10):
            watchlist = Watchlist(user_id=test_user.id, name=f"Watchlist {i}")
            db.add(watchlist)
        await db.commit()

        # Try to create 11th
        response = await client.post(
            "/v1/users/watchlists",
            headers=auth_headers,
            json={"name": "Overflow Watchlist"},
        )

        assert response.status_code == 400
        assert "limit reached" in response.json()["detail"].lower()

    async def test_create_watchlist_validation_error(
        self, client: AsyncClient, auth_headers
    ):
        """Test validation errors"""
        # Empty name
        response = await client.post(
            "/v1/users/watchlists",
            headers=auth_headers,
            json={"name": "   ", "description": "Test"},
        )

        assert response.status_code == 422  # Validation error

    async def test_list_watchlists_with_data(
        self, client: AsyncClient, auth_headers, db, test_user
    ):
        """Test listing watchlists"""
        # Create watchlists
        for i in range(3):
            watchlist = Watchlist(user_id=test_user.id, name=f"Watchlist {i}")
            db.add(watchlist)
        await db.commit()

        response = await client.get("/v1/users/watchlists", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["watchlists"]) == 3

    async def test_list_watchlists_pagination(
        self, client: AsyncClient, auth_headers, db, test_user
    ):
        """Test watchlist pagination"""
        # Create 5 watchlists
        for i in range(5):
            watchlist = Watchlist(user_id=test_user.id, name=f"Watchlist {i}")
            db.add(watchlist)
        await db.commit()

        # Get first page (3 items)
        response = await client.get(
            "/v1/users/watchlists?page=1&limit=3", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["watchlists"]) == 3
        assert data["page"] == 1

        # Get second page
        response = await client.get(
            "/v1/users/watchlists?page=2&limit=3", headers=auth_headers
        )

        data = response.json()
        assert len(data["watchlists"]) == 2
        assert data["page"] == 2

    async def test_get_watchlist_by_id(
        self, client: AsyncClient, auth_headers, db, test_user, test_stocks
    ):
        """Test getting watchlist by ID"""
        # Create watchlist with stocks
        watchlist = Watchlist(user_id=test_user.id, name="Test Watchlist")
        db.add(watchlist)
        await db.commit()
        await db.refresh(watchlist)

        ws = WatchlistStock(
            watchlist_id=watchlist.id,
            stock_code="005930",
        )
        db.add(ws)
        await db.commit()

        response = await client.get(
            f"/v1/users/watchlists/{watchlist.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(watchlist.id)
        assert data["name"] == "Test Watchlist"
        assert len(data["stocks"]) == 1
        assert data["stocks"][0]["stock_code"] == "005930"

    async def test_get_watchlist_not_found(
        self, client: AsyncClient, auth_headers, test_user
    ):
        """Test getting non-existent watchlist"""
        fake_id = uuid.uuid4()
        response = await client.get(
            f"/v1/users/watchlists/{fake_id}", headers=auth_headers
        )

        assert response.status_code == 404

    async def test_get_watchlist_unauthorized_access(
        self, client: AsyncClient, auth_headers, db
    ):
        """Test accessing another user's watchlist"""
        # Create another user and their watchlist
        from app.core.security import get_password_hash

        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("password"),
            name="Other User",
            subscription_tier="free",
        )
        db.add(other_user)
        await db.commit()
        await db.refresh(other_user)

        watchlist = Watchlist(user_id=other_user.id, name="Other's Watchlist")
        db.add(watchlist)
        await db.commit()
        await db.refresh(watchlist)

        # Try to access with current user's token
        response = await client.get(
            f"/v1/users/watchlists/{watchlist.id}", headers=auth_headers
        )

        assert response.status_code == 404  # Not found (ownership check)

    async def test_update_watchlist_name(
        self, client: AsyncClient, auth_headers, db, test_user
    ):
        """Test updating watchlist name"""
        watchlist = Watchlist(user_id=test_user.id, name="Original Name")
        db.add(watchlist)
        await db.commit()
        await db.refresh(watchlist)

        response = await client.put(
            f"/v1/users/watchlists/{watchlist.id}",
            headers=auth_headers,
            json={"name": "Updated Name", "description": "New description"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    async def test_update_watchlist_add_stocks(
        self, client: AsyncClient, auth_headers, db, test_user, test_stocks
    ):
        """Test adding stocks to watchlist via update"""
        watchlist = Watchlist(user_id=test_user.id, name="Test")
        db.add(watchlist)
        await db.commit()
        await db.refresh(watchlist)

        response = await client.put(
            f"/v1/users/watchlists/{watchlist.id}",
            headers=auth_headers,
            json={"add_stocks": ["005930", "000660"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["stock_count"] == 2

    async def test_update_watchlist_remove_stocks(
        self, client: AsyncClient, auth_headers, db, test_user, test_stocks
    ):
        """Test removing stocks from watchlist via update"""
        watchlist = Watchlist(user_id=test_user.id, name="Test")
        db.add(watchlist)
        await db.commit()
        await db.refresh(watchlist)

        # Add stocks first
        for code in ["005930", "000660"]:
            ws = WatchlistStock(watchlist_id=watchlist.id, stock_code=code)
            db.add(ws)
        await db.commit()

        # Remove one stock
        response = await client.put(
            f"/v1/users/watchlists/{watchlist.id}",
            headers=auth_headers,
            json={"remove_stocks": ["000660"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["stock_count"] == 1

    async def test_delete_watchlist(
        self, client: AsyncClient, auth_headers, db, test_user
    ):
        """Test deleting watchlist"""
        watchlist = Watchlist(user_id=test_user.id, name="To Delete")
        db.add(watchlist)
        await db.commit()
        await db.refresh(watchlist)

        watchlist_id = watchlist.id

        response = await client.delete(
            f"/v1/users/watchlists/{watchlist_id}", headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deleted
        result = await db.execute(select(Watchlist).where(Watchlist.id == watchlist_id))
        assert result.scalar_one_or_none() is None

    async def test_delete_watchlist_not_found(
        self, client: AsyncClient, auth_headers, test_user
    ):
        """Test deleting non-existent watchlist"""
        fake_id = uuid.uuid4()
        response = await client.delete(
            f"/v1/users/watchlists/{fake_id}", headers=auth_headers
        )

        assert response.status_code == 404

    async def test_watchlist_unauthorized(self, client: AsyncClient, test_user):
        """Test accessing watchlist endpoints without authentication"""
        response = await client.get("/v1/users/watchlists")

        # Without auth token, FastAPI returns 403 (Forbidden) not 401
        assert response.status_code == 403


# =============================================================================
# USER ACTIVITY ENDPOINTS TESTS
# =============================================================================


class TestUserActivityEndpoints:
    """Test User Activity API endpoints"""

    async def test_get_recent_activity_empty(
        self, client: AsyncClient, auth_headers, test_user
    ):
        """Test getting recent activity when user has none"""
        response = await client.get("/v1/users/recent-activity", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["activities"] == []

    async def test_get_recent_activity_with_data(
        self, client: AsyncClient, auth_headers, db, test_user
    ):
        """Test getting recent activities"""
        # Create a watchlist to generate activity
        response = await client.post(
            "/v1/users/watchlists",
            headers=auth_headers,
            json={"name": "Test Watchlist"},
        )
        assert response.status_code == 201

        # Get activities
        response = await client.get("/v1/users/recent-activity", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert len(data["activities"]) > 0
        assert data["activities"][0]["activity_type"] == "watchlist_create"

    async def test_get_recent_activity_with_limit(
        self, client: AsyncClient, auth_headers, db, test_user
    ):
        """Test activity limit parameter"""
        # Create multiple watchlists to generate activities
        for i in range(5):
            await client.post(
                "/v1/users/watchlists",
                headers=auth_headers,
                json={"name": f"Watchlist {i}"},
            )

        # Get only 3 activities
        response = await client.get(
            "/v1/users/recent-activity?limit=3", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["activities"]) == 3

    async def test_get_recent_activity_filter_by_type(
        self, client: AsyncClient, auth_headers, db, test_user
    ):
        """Test filtering activities by type"""
        # Create watchlist (generates watchlist_create activity)
        await client.post(
            "/v1/users/watchlists",
            headers=auth_headers,
            json={"name": "Test"},
        )

        # Filter by type
        response = await client.get(
            "/v1/users/recent-activity?activity_type=watchlist_create",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert all(a["activity_type"] == "watchlist_create" for a in data["activities"])


# =============================================================================
# DASHBOARD ENDPOINTS TESTS
# =============================================================================


class TestDashboardEndpoints:
    """Test Dashboard API endpoints"""

    async def test_get_dashboard_summary(
        self, client: AsyncClient, auth_headers, test_user, test_user_preferences
    ):
        """Test getting dashboard summary"""
        response = await client.get("/v1/users/dashboard", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "watchlist_count" in data
        assert "total_stocks" in data
        assert "recent_activity_count" in data
        assert "subscription_tier" in data
        assert "screening_quota" in data
        assert data["subscription_tier"] == "free"

    async def test_dashboard_summary_with_data(
        self, client: AsyncClient, auth_headers, db, test_user, test_user_preferences, test_stocks
    ):
        """Test dashboard summary with actual data"""
        # Create watchlist with stocks
        watchlist = Watchlist(user_id=test_user.id, name="My Watchlist")
        db.add(watchlist)
        await db.commit()
        await db.refresh(watchlist)

        ws = WatchlistStock(watchlist_id=watchlist.id, stock_code="005930")
        db.add(ws)
        await db.commit()

        response = await client.get("/v1/users/dashboard", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["watchlist_count"] == 1
        assert data["total_stocks"] == 1

    async def test_dashboard_screening_quota(
        self, client: AsyncClient, auth_headers, test_user, test_user_preferences
    ):
        """Test screening quota in dashboard"""
        response = await client.get("/v1/users/dashboard", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        quota = data["screening_quota"]
        assert "used" in quota
        assert "limit" in quota
        assert "remaining" in quota
        assert "reset_at" in quota
        assert quota["limit"] == 100  # Free tier limit
        assert quota["remaining"] == 100  # No usage yet
