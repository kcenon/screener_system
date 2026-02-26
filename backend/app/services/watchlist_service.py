"""Watchlist service for user portfolio management"""

from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserActivity, Watchlist, WatchlistStock
from app.repositories import (UserActivityRepository,
                              UserPreferencesRepository, WatchlistRepository)
from app.repositories.stock_repository import StockRepository
from app.schemas.watchlist import (DashboardSummary, ScreeningQuota,
                                   WatchlistCreate, WatchlistUpdate)


class WatchlistService:
    """Service for watchlist operations"""

    MAX_WATCHLISTS_PER_USER = 10
    MAX_STOCKS_PER_WATCHLIST = 1000

    def __init__(self, session: AsyncSession):
        """Initialize service with database session"""
        self.session = session
        self.watchlist_repo = WatchlistRepository(session)
        self.activity_repo = UserActivityRepository(session)
        self.stock_repo = StockRepository(session)

    async def get_user_watchlists(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        load_stocks: bool = False,
    ) -> tuple[list[Watchlist], int]:
        """
        Get user watchlists with pagination

        Args:
            user_id: User UUID
            skip: Number to skip
            limit: Maximum results
            load_stocks: Whether to load stock details

        Returns:
            Tuple of (watchlists, total_count)
        """
        watchlists = await self.watchlist_repo.get_user_watchlists(
            user_id=user_id, skip=skip, limit=limit, load_stocks=load_stocks
        )
        total = await self.watchlist_repo.count_user_watchlists(user_id)
        return watchlists, total

    async def get_watchlist_by_id(
        self, watchlist_id: UUID, user_id: int, load_stocks: bool = True
    ) -> Optional[Watchlist]:
        """Get watchlist by ID (ownership check)"""
        return await self.watchlist_repo.get_by_id(
            watchlist_id=watchlist_id, user_id=user_id, load_stocks=load_stocks
        )

    async def create_watchlist(self, user_id: int, data: WatchlistCreate) -> Watchlist:
        """
        Create new watchlist

        Args:
            user_id: User UUID
            data: Watchlist creation data

        Returns:
            Created watchlist

        Raises:
            ValueError: If user has reached watchlist limit or stock codes invalid
        """
        # Check watchlist limit
        count = await self.watchlist_repo.count_user_watchlists(user_id)
        if count >= self.MAX_WATCHLISTS_PER_USER:
            raise ValueError(
                f"Watchlist limit reached (max {self.MAX_WATCHLISTS_PER_USER})"
            )

        # Validate stock codes if provided
        if data.stock_codes:
            for code in data.stock_codes:
                stock = await self.stock_repo.get_by_code(code)
                if not stock:
                    raise ValueError(f"Stock code {code} does not exist")

        # Create watchlist
        watchlist = Watchlist(
            user_id=user_id,
            name=data.name,
            description=data.description,
        )
        watchlist = await self.watchlist_repo.create(watchlist)

        # Add initial stocks
        if data.stock_codes:
            for code in data.stock_codes:
                await self.watchlist_repo.add_stock(watchlist.id, code)

        # Log activity
        await self.log_activity(
            user_id=user_id,
            activity_type="watchlist_create",
            description=f"Created watchlist '{data.name}'",
            activity_metadata={"watchlist_id": str(watchlist.id)},
        )

        await self.session.commit()
        await self.session.refresh(watchlist)
        return watchlist

    async def update_watchlist(
        self, watchlist_id: UUID, user_id: int, data: WatchlistUpdate
    ) -> Watchlist:
        """
        Update watchlist

        Args:
            watchlist_id: Watchlist UUID
            user_id: User UUID (for ownership check)
            data: Update data

        Returns:
            Updated watchlist

        Raises:
            ValueError: If watchlist not found or stock codes invalid
        """
        # Get watchlist (ownership check)
        watchlist = await self.watchlist_repo.get_by_id(watchlist_id, user_id)
        if not watchlist:
            raise ValueError("Watchlist not found or access denied")

        # Update basic fields
        if data.name is not None:
            watchlist.name = data.name
        if data.description is not None:
            watchlist.description = data.description

        # Add stocks
        if data.add_stocks:
            for code in data.add_stocks:
                # Validate stock exists
                stock = await self.stock_repo.get_by_code(code)
                if not stock:
                    raise ValueError(f"Stock code {code} does not exist")

                # Check if already in watchlist
                if not await self.watchlist_repo.stock_in_watchlist(watchlist_id, code):
                    await self.watchlist_repo.add_stock(watchlist_id, code)

        # Remove stocks
        if data.remove_stocks:
            for code in data.remove_stocks:
                await self.watchlist_repo.remove_stock(watchlist_id, code)

        watchlist = await self.watchlist_repo.update(watchlist)

        # Log activity
        changes = []
        if data.name:
            changes.append(f"renamed to '{data.name}'")
        if data.add_stocks:
            changes.append(f"added {len(data.add_stocks)} stocks")
        if data.remove_stocks:
            changes.append(f"removed {len(data.remove_stocks)} stocks")

        if changes:
            await self.log_activity(
                user_id=user_id,
                activity_type="watchlist_update",
                description=f"Updated watchlist: {', '.join(changes)}",
                activity_metadata={"watchlist_id": str(watchlist_id)},
            )

        await self.session.commit()
        await self.session.refresh(watchlist)
        return watchlist

    async def delete_watchlist(self, watchlist_id: UUID, user_id: int) -> None:
        """
        Delete watchlist

        Args:
            watchlist_id: Watchlist UUID
            user_id: User UUID (for ownership check)

        Raises:
            ValueError: If watchlist not found
        """
        watchlist = await self.watchlist_repo.get_by_id(
            watchlist_id, user_id, load_stocks=False
        )
        if not watchlist:
            raise ValueError("Watchlist not found or access denied")

        watchlist_name = watchlist.name
        await self.watchlist_repo.delete(watchlist)

        # Log activity
        await self.log_activity(
            user_id=user_id,
            activity_type="watchlist_delete",
            description=f"Deleted watchlist '{watchlist_name}'",
            activity_metadata={"watchlist_id": str(watchlist_id)},
        )

        await self.session.commit()

    async def add_stock_to_watchlist(
        self, watchlist_id: UUID, user_id: int, stock_code: str
    ) -> WatchlistStock:
        """Add stock to watchlist"""
        # Verify ownership
        watchlist = await self.watchlist_repo.get_by_id(
            watchlist_id, user_id, load_stocks=False
        )
        if not watchlist:
            raise ValueError("Watchlist not found or access denied")

        # Verify stock exists
        stock = await self.stock_repo.get_by_code(stock_code)
        if not stock:
            raise ValueError(f"Stock code {stock_code} does not exist")

        # Add stock
        watchlist_stock = await self.watchlist_repo.add_stock(watchlist_id, stock_code)

        # Log activity
        await self.log_activity(
            user_id=user_id,
            activity_type="stock_add",
            description=f"Added {stock.name} ({stock_code}) to watchlist",
            activity_metadata={
                "watchlist_id": str(watchlist_id),
                "stock_code": stock_code,
            },
        )

        await self.session.commit()
        return watchlist_stock

    async def remove_stock_from_watchlist(
        self, watchlist_id: UUID, user_id: int, stock_code: str
    ) -> None:
        """Remove stock from watchlist"""
        # Verify ownership
        watchlist = await self.watchlist_repo.get_by_id(
            watchlist_id, user_id, load_stocks=False
        )
        if not watchlist:
            raise ValueError("Watchlist not found or access denied")

        # Remove stock
        removed = await self.watchlist_repo.remove_stock(watchlist_id, stock_code)
        if removed == 0:
            raise ValueError("Stock not found in watchlist")

        # Log activity
        await self.log_activity(
            user_id=user_id,
            activity_type="stock_remove",
            description=f"Removed {stock_code} from watchlist",
            activity_metadata={
                "watchlist_id": str(watchlist_id),
                "stock_code": stock_code,
            },
        )

        await self.session.commit()

    async def log_activity(
        self,
        user_id: int,
        activity_type: str,
        description: str,
        activity_metadata: Optional[dict[str, Any]] = None,
    ) -> UserActivity:
        """Log user activity"""
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            activity_metadata=activity_metadata,
        )
        return await self.activity_repo.create(activity)

    async def get_recent_activities(
        self, user_id: int, limit: int = 10, activity_type: Optional[str] = None
    ) -> tuple[list[UserActivity], int]:
        """Get recent user activities"""
        activities = await self.activity_repo.get_user_activities(
            user_id=user_id, limit=limit, activity_type=activity_type
        )
        total = await self.activity_repo.count_user_activities(
            user_id=user_id, activity_type=activity_type
        )
        return activities, total

    async def get_dashboard_summary(
        self, user_id: int, user_tier: str
    ) -> DashboardSummary:
        """
        Get dashboard summary for user

        Args:
            user_id: User UUID
            user_tier: User subscription tier

        Returns:
            Dashboard summary with stats
        """
        # Get watchlist count
        watchlist_count = await self.watchlist_repo.count_user_watchlists(user_id)

        # Get total stocks across all watchlists
        # Query stock counts separately to avoid relationship loading
        watchlists = await self.watchlist_repo.get_user_watchlists(
            user_id=user_id, skip=0, limit=100, load_stocks=False
        )
        total_stocks = 0
        for wl in watchlists:
            watchlist_stocks = await self.watchlist_repo.get_watchlist_stocks(wl.id)
            total_stocks += len(watchlist_stocks)

        # Get recent activity count (last 30 days)
        recent_count = await self.activity_repo.count_user_activities(user_id)

        # Get last activity
        activities, _ = await self.get_recent_activities(user_id, limit=1)
        last_activity_at = activities[0].created_at if activities else None

        # Get preferences for quota
        prefs_repo = UserPreferencesRepository(self.session)
        prefs = await prefs_repo.get_by_user_id(user_id)
        quota_used = prefs.screening_quota_used if prefs else 0
        quota_reset_at = (
            prefs.screening_quota_reset_at
            if prefs
            else datetime.now() + timedelta(days=30)
        )

        # Build screening quota
        screening_quota = ScreeningQuota.from_tier(
            tier=user_tier, used=quota_used, reset_at=quota_reset_at
        )

        return DashboardSummary(
            watchlist_count=watchlist_count,
            total_stocks=total_stocks,
            recent_activity_count=recent_count,
            last_activity_at=last_activity_at,
            subscription_tier=user_tier,
            screening_quota=screening_quota,
        )
