"""Watchlist repository for database operations"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import UserActivity, UserPreferences, Watchlist, WatchlistStock


class WatchlistRepository:
    """Repository for Watchlist database operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def get_by_id(
        self, watchlist_id: UUID, user_id: int, load_stocks: bool = True
    ) -> Optional[Watchlist]:
        """
        Get watchlist by ID (only if owned by user)

        Args:
            watchlist_id: Watchlist UUID
            user_id: User UUID (for ownership check)
            load_stocks: Whether to load associated stocks

        Returns:
            Watchlist if found and owned by user, None otherwise
        """
        query = select(Watchlist).where(
            Watchlist.id == watchlist_id, Watchlist.user_id == user_id
        )

        if load_stocks:
            from sqlalchemy.orm import joinedload
            query = query.options(
                selectinload(Watchlist.stocks).joinedload(WatchlistStock.stock)
            )

        result = await self.session.execute(query)
        watchlist = result.scalar_one_or_none()

        # Force load relationships before returning
        if watchlist and load_stocks:
            # Access the relationship to trigger lazy loading
            _ = watchlist.stocks
            # Also access nested stock relationship for each WatchlistStock
            for ws in watchlist.stocks:
                _ = ws.stock

        return watchlist

    async def get_user_watchlists(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        load_stocks: bool = False,
    ) -> list[Watchlist]:
        """
        Get all watchlists for a user

        Args:
            user_id: User UUID
            skip: Number of watchlists to skip (pagination)
            limit: Maximum number of watchlists to return
            load_stocks: Whether to load associated stocks

        Returns:
            List of watchlists
        """
        query = (
            select(Watchlist)
            .where(Watchlist.user_id == user_id)
            .order_by(Watchlist.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        if load_stocks:
            from sqlalchemy.orm import joinedload
            query = query.options(
                selectinload(Watchlist.stocks).joinedload(WatchlistStock.stock)
            )

        result = await self.session.execute(query)
        watchlists = list(result.scalars().all())

        # Force load relationships before returning
        if load_stocks:
            for watchlist in watchlists:
                # Access the relationship to trigger lazy loading
                _ = watchlist.stocks
                # Also access nested stock relationship for each WatchlistStock
                for ws in watchlist.stocks:
                    _ = ws.stock

        return watchlists

    async def count_user_watchlists(self, user_id: int) -> int:
        """Count watchlists owned by user"""
        result = await self.session.execute(
            select(func.count(Watchlist.id)).where(Watchlist.user_id == user_id)
        )
        return result.scalar_one()

    async def create(self, watchlist: Watchlist) -> Watchlist:
        """Create new watchlist"""
        self.session.add(watchlist)
        await self.session.flush()
        await self.session.refresh(watchlist)
        return watchlist

    async def update(self, watchlist: Watchlist) -> Watchlist:
        """Update existing watchlist"""
        await self.session.flush()
        await self.session.refresh(watchlist)
        return watchlist

    async def delete(self, watchlist: Watchlist) -> None:
        """Delete watchlist (cascade deletes stocks)"""
        await self.session.delete(watchlist)
        await self.session.flush()

    async def add_stock(
        self, watchlist_id: UUID, stock_code: str, notes: Optional[str] = None
    ) -> WatchlistStock:
        """
        Add stock to watchlist

        Args:
            watchlist_id: Watchlist UUID
            stock_code: Stock code (6 digits)
            notes: Optional user notes

        Returns:
            Created WatchlistStock
        """
        watchlist_stock = WatchlistStock(
            watchlist_id=watchlist_id,
            stock_code=stock_code,
            notes=notes,
        )
        self.session.add(watchlist_stock)
        await self.session.flush()
        await self.session.refresh(watchlist_stock)
        return watchlist_stock

    async def remove_stock(self, watchlist_id: UUID, stock_code: str) -> int:
        """
        Remove stock from watchlist

        Args:
            watchlist_id: Watchlist UUID
            stock_code: Stock code to remove

        Returns:
            Number of rows deleted (0 or 1)
        """
        stmt = delete(WatchlistStock).where(
            WatchlistStock.watchlist_id == watchlist_id,
            WatchlistStock.stock_code == stock_code,
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

    async def get_watchlist_stocks(self, watchlist_id: UUID) -> list[WatchlistStock]:
        """Get all stocks in a watchlist"""
        result = await self.session.execute(
            select(WatchlistStock)
            .where(WatchlistStock.watchlist_id == watchlist_id)
            .order_by(WatchlistStock.added_at.desc())
        )
        return list(result.scalars().all())

    async def stock_in_watchlist(self, watchlist_id: UUID, stock_code: str) -> bool:
        """Check if stock exists in watchlist"""
        result = await self.session.execute(
            select(WatchlistStock).where(
                WatchlistStock.watchlist_id == watchlist_id,
                WatchlistStock.stock_code == stock_code,
            )
        )
        return result.scalar_one_or_none() is not None


class UserActivityRepository:
    """Repository for UserActivity database operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def create(self, activity: UserActivity) -> UserActivity:
        """Create new activity log entry"""
        self.session.add(activity)
        await self.session.flush()
        await self.session.refresh(activity)
        return activity

    async def get_user_activities(
        self,
        user_id: int,
        limit: int = 10,
        activity_type: Optional[str] = None,
    ) -> list[UserActivity]:
        """
        Get user activities

        Args:
            user_id: User UUID
            limit: Maximum number of activities
            activity_type: Optional filter by activity type

        Returns:
            List of user activities
        """
        query = (
            select(UserActivity)
            .where(UserActivity.user_id == user_id)
            .order_by(UserActivity.created_at.desc())
            .limit(limit)
        )

        if activity_type:
            query = query.where(UserActivity.activity_type == activity_type)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_user_activities(
        self, user_id: int, activity_type: Optional[str] = None
    ) -> int:
        """Count user activities"""
        query = select(func.count(UserActivity.id)).where(
            UserActivity.user_id == user_id
        )

        if activity_type:
            query = query.where(UserActivity.activity_type == activity_type)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_recent_screenings(
        self, user_id: int, limit: int = 10
    ) -> list[UserActivity]:
        """Get recent screening activities"""
        return await self.get_user_activities(
            user_id=user_id, limit=limit, activity_type="screening"
        )


class UserPreferencesRepository:
    """Repository for UserPreferences database operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def get_by_user_id(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences by user ID"""
        result = await self.session.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, preferences: UserPreferences) -> UserPreferences:
        """Create new user preferences"""
        self.session.add(preferences)
        await self.session.flush()
        await self.session.refresh(preferences)
        return preferences

    async def update(self, preferences: UserPreferences) -> UserPreferences:
        """Update existing user preferences"""
        await self.session.flush()
        await self.session.refresh(preferences)
        return preferences

    async def increment_screening_quota(self, user_id: int) -> None:
        """Increment screening quota usage"""
        prefs = await self.get_by_user_id(user_id)
        if prefs:
            prefs.screening_quota_used += 1
            await self.session.flush()

    async def reset_screening_quota(self, user_id: int) -> None:
        """Reset screening quota (monthly reset)"""
        prefs = await self.get_by_user_id(user_id)
        if prefs:
            prefs.screening_quota_used = 0
            prefs.screening_quota_reset_at = datetime.now() + timedelta(days=30)
            await self.session.flush()
