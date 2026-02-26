"""OAuth repository for database operations"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OAuthState, SocialAccount


class SocialAccountRepository:
    """Repository for SocialAccount database operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def get_by_id(self, account_id: int) -> Optional[SocialAccount]:
        """Get social account by ID"""
        result = await self.session.execute(
            select(SocialAccount).where(SocialAccount.id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_by_provider_user_id(
        self, provider: str, provider_user_id: str
    ) -> Optional[SocialAccount]:
        """Get social account by provider and provider user ID"""
        result = await self.session.execute(
            select(SocialAccount).where(
                and_(
                    SocialAccount.provider == provider.upper(),
                    SocialAccount.provider_user_id == provider_user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_provider(
        self, user_id: int, provider: str
    ) -> Optional[SocialAccount]:
        """Get social account by user ID and provider"""
        result = await self.session.execute(
            select(SocialAccount).where(
                and_(
                    SocialAccount.user_id == user_id,
                    SocialAccount.provider == provider.upper(),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: int) -> List[SocialAccount]:
        """Get all social accounts for a user"""
        result = await self.session.execute(
            select(SocialAccount)
            .where(SocialAccount.user_id == user_id)
            .order_by(SocialAccount.created_at)
        )
        return list(result.scalars().all())

    async def create(self, social_account: SocialAccount) -> SocialAccount:
        """Create new social account"""
        self.session.add(social_account)
        await self.session.flush()
        await self.session.refresh(social_account)
        return social_account

    async def update(self, social_account: SocialAccount) -> SocialAccount:
        """Update existing social account"""
        await self.session.flush()
        await self.session.refresh(social_account)
        return social_account

    async def delete(self, social_account: SocialAccount) -> None:
        """Delete social account"""
        await self.session.delete(social_account)
        await self.session.flush()

    async def delete_by_user_and_provider(self, user_id: int, provider: str) -> bool:
        """Delete social account by user ID and provider"""
        result = await self.session.execute(
            delete(SocialAccount).where(
                and_(
                    SocialAccount.user_id == user_id,
                    SocialAccount.provider == provider.upper(),
                )
            )
        )
        await self.session.flush()
        return result.rowcount > 0

    async def count_by_user(self, user_id: int) -> int:
        """Count social accounts for a user"""
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count(SocialAccount.id)).where(SocialAccount.user_id == user_id)
        )
        return result.scalar_one()


class OAuthStateRepository:
    """Repository for OAuthState database operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def get_by_state(self, state: str) -> Optional[OAuthState]:
        """Get OAuth state by state token"""
        result = await self.session.execute(
            select(OAuthState).where(OAuthState.state == state)
        )
        return result.scalar_one_or_none()

    async def create(self, oauth_state: OAuthState) -> OAuthState:
        """Create new OAuth state"""
        self.session.add(oauth_state)
        await self.session.flush()
        await self.session.refresh(oauth_state)
        return oauth_state

    async def delete(self, oauth_state: OAuthState) -> None:
        """Delete OAuth state"""
        await self.session.delete(oauth_state)
        await self.session.flush()

    async def delete_by_state(self, state: str) -> bool:
        """Delete OAuth state by state token"""
        result = await self.session.execute(
            delete(OAuthState).where(OAuthState.state == state)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def cleanup_expired(self) -> int:
        """Delete all expired OAuth states"""
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            delete(OAuthState).where(OAuthState.expires_at < now)
        )
        await self.session.flush()
        return result.rowcount

    async def validate_and_consume(self, state: str) -> Optional[OAuthState]:
        """
        Validate state token and consume it (delete after use).

        Args:
            state: State token to validate

        Returns:
            OAuthState if valid and not expired, None otherwise
        """
        oauth_state = await self.get_by_state(state)

        if oauth_state is None:
            return None

        if oauth_state.is_expired:
            await self.delete(oauth_state)
            return None

        # Consume the state (one-time use)
        await self.delete(oauth_state)
        return oauth_state
