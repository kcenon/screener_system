"""User session repository for refresh token management"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from app.db.models import UserSession
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserSessionRepository:
    """Repository for UserSession database operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def get_by_id(self, session_id: UUID) -> Optional[UserSession]:
        """Get session by UUID"""
        result = await self.session.execute(
            select(UserSession).where(UserSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_by_refresh_token(self, refresh_token: str) -> Optional[UserSession]:
        """Get session by refresh token"""
        result = await self.session.execute(
            select(UserSession).where(
                UserSession.refresh_token == refresh_token,
                UserSession.is_active == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def get_active_sessions_by_user_id(
        self, user_id: int, limit: int = 10
    ) -> list[UserSession]:
        """Get active (non-revoked, non-expired) sessions for a user"""
        from app.db.base import utc_now

        now = utc_now()
        result = await self.session.execute(
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.revoked == False,  # noqa: E712
                UserSession.expires_at > now,
            )
            .order_by(UserSession.last_accessed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, user_session: UserSession) -> UserSession:
        """Create new session"""
        self.session.add(user_session)
        await self.session.flush()
        await self.session.refresh(user_session)
        return user_session

    async def revoke(self, user_session: UserSession) -> UserSession:
        """Revoke a session"""
        user_session.revoke()
        await self.session.flush()
        await self.session.refresh(user_session)
        return user_session

    async def revoke_by_refresh_token(self, refresh_token: str) -> bool:
        """
        Revoke session by refresh token.
        Returns True if session was found and revoked.
        """
        user_session = await self.get_by_refresh_token(refresh_token)
        if user_session:
            await self.revoke(user_session)
            return True
        return False

    async def revoke_all_user_sessions(self, user_id: int) -> int:
        """Revoke all sessions for a user. Returns count of revoked sessions."""
        sessions = await self.get_active_sessions_by_user_id(user_id, limit=100)
        for session in sessions:
            await self.revoke(session)
        return len(sessions)

    async def delete_expired_sessions(self, before: Optional[datetime] = None) -> int:
        """Delete expired sessions. Returns count of deleted sessions."""
        from app.db.base import utc_now
        from sqlalchemy import delete

        cutoff = before or utc_now()
        result = await self.session.execute(
            delete(UserSession).where(UserSession.expires_at < cutoff)
        )
        await self.session.flush()
        return result.rowcount  # type: ignore
