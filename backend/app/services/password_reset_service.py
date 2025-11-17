"""Password reset service for account recovery"""

import secrets
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.security import get_password_hash
from app.db.models import PasswordResetToken, User
from app.repositories import UserRepository, UserSessionRepository


class PasswordResetService:
    """Service for password reset operations"""

    def __init__(self, session: AsyncSession):
        """Initialize service with database session"""
        self.session = session
        self.user_repo = UserRepository(session)
        self.session_repo = UserSessionRepository(session)

    async def request_password_reset(self, email: str) -> Optional[PasswordResetToken]:
        """
        Request password reset for user email

        Args:
            email: User email address

        Returns:
            PasswordResetToken if user exists, None otherwise
            (Don't reveal if user exists for security)

        Note:
            Always returns success to prevent user enumeration attacks
        """
        # Get user by email
        user = await self.user_repo.get_by_email(email)

        # Don't reveal if user exists
        if not user:
            return None

        # Check rate limiting (max 3 tokens per hour)
        recent_tokens = await self._count_recent_tokens(user.id, hours=1)
        if recent_tokens >= 3:
            raise BadRequestException(
                "Too many password reset requests. Please try again later."
            )

        # Invalidate old tokens
        await self._invalidate_old_tokens(user.id)

        # Generate secure token
        token = self._generate_secure_token()

        # Create reset token
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=PasswordResetToken.calculate_expiry(hours=1),
        )

        self.session.add(reset_token)
        await self.session.commit()
        await self.session.refresh(reset_token)

        # TODO: Send actual email (implement email service integration)
        # For now, return token for manual testing in development
        return reset_token

    async def validate_reset_token(self, token: str) -> bool:
        """
        Validate password reset token

        Args:
            token: Password reset token

        Returns:
            True if token is valid, False otherwise
        """
        # Get token from database
        stmt = select(PasswordResetToken).where(PasswordResetToken.token == token)
        result = await self.session.execute(stmt)
        reset_token = result.scalar_one_or_none()

        if not reset_token:
            return False

        return reset_token.is_valid

    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset user password using reset token

        Args:
            token: Password reset token
            new_password: New password (plain text, will be hashed)

        Returns:
            True if password reset successful

        Raises:
            BadRequestException: If token invalid, expired, or already used
        """
        # Get token from database
        stmt = select(PasswordResetToken).where(PasswordResetToken.token == token)
        result = await self.session.execute(stmt)
        reset_token = result.scalar_one_or_none()

        if not reset_token:
            raise BadRequestException("Invalid password reset token")

        # Check if token is valid
        if not reset_token.is_valid:
            if reset_token.is_used:
                raise BadRequestException("Password reset token already used")
            if reset_token.is_expired:
                raise BadRequestException("Password reset token has expired")
            raise BadRequestException("Invalid password reset token")

        # Get user
        user = await self.user_repo.get_by_id(reset_token.user_id)
        if not user:
            raise NotFoundException("User not found")

        # Validate password strength (basic validation)
        self._validate_password_strength(new_password)

        # Mark token as used
        reset_token.mark_as_used()

        # Update user password
        user.password_hash = get_password_hash(new_password)
        user.updated_at = reset_token.used_at

        # Invalidate all user sessions (logout from all devices)
        await self.session_repo.revoke_all_user_sessions(user.id)

        await self.session.commit()

        # TODO: Send password changed confirmation email
        return True

    async def _count_recent_tokens(self, user_id: int, hours: int = 1) -> int:
        """Count reset tokens created in last N hours"""
        from app.db.base import utc_now

        cutoff_time = utc_now()
        cutoff_time = cutoff_time.replace(
            hour=cutoff_time.hour - hours if cutoff_time.hour >= hours else 0
        )

        stmt = (
            select(PasswordResetToken)
            .where(PasswordResetToken.user_id == user_id)
            .where(PasswordResetToken.created_at >= cutoff_time)
        )
        result = await self.session.execute(stmt)
        tokens = result.scalars().all()
        return len(tokens)

    async def _invalidate_old_tokens(self, user_id: int) -> None:
        """Invalidate all old reset tokens for user"""
        from app.db.base import utc_now

        stmt = (
            select(PasswordResetToken)
            .where(PasswordResetToken.user_id == user_id)
            .where(PasswordResetToken.used_at.is_(None))
        )
        result = await self.session.execute(stmt)
        old_tokens = result.scalars().all()

        for token in old_tokens:
            token.mark_as_used(timestamp=utc_now())

    @staticmethod
    def _generate_secure_token() -> str:
        """
        Generate cryptographically secure random token

        Returns:
            URL-safe random token string (43 characters)
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def _validate_password_strength(password: str) -> None:
        """
        Validate password meets minimum security requirements

        Args:
            password: Plain text password

        Raises:
            BadRequestException: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise BadRequestException("Password must be at least 8 characters long")

        # Check for at least one uppercase letter
        if not any(c.isupper() for c in password):
            raise BadRequestException(
                "Password must contain at least one uppercase letter"
            )

        # Check for at least one lowercase letter
        if not any(c.islower() for c in password):
            raise BadRequestException(
                "Password must contain at least one lowercase letter"
            )

        # Check for at least one digit
        if not any(c.isdigit() for c in password):
            raise BadRequestException("Password must contain at least one digit")

        # Check for at least one special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            raise BadRequestException(
                "Password must contain at least one special character"
            )
