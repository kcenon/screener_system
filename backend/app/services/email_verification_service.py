"""Email verification service for user registration"""

import secrets


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.db.models import EmailVerificationToken
from app.repositories import UserRepository


class EmailVerificationService:
    """Service for email verification operations"""

    def __init__(self, session: AsyncSession):
        """Initialize service with database session"""
        self.session = session
        self.user_repo = UserRepository(session)

    async def send_verification_email(
        self, user_id: int, email: str
    ) -> EmailVerificationToken:
        """
        Generate verification token and prepare for email sending

        Args:
            user_id: User ID to verify
            email: Email address to send verification to

        Returns:
            EmailVerificationToken with generated token

        Raises:
            NotFoundException: If user not found
            BadRequestException: If email already verified or rate limit exceeded
        """
        # Get user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        # Check if email already verified
        if user.email_verified:
            raise BadRequestException("Email already verified")

        # Check rate limiting (max 3 tokens per hour)
        recent_tokens = await self._count_recent_tokens(user_id, hours=1)
        if recent_tokens >= 3:
            raise BadRequestException(
                "Too many verification emails sent. Please try again later."
            )

        # Invalidate old tokens
        await self._invalidate_old_tokens(user_id)

        # Generate secure token
        token = self._generate_secure_token()

        # Create verification token
        verification_token = EmailVerificationToken(
            user_id=user_id,
            token=token,
            expires_at=EmailVerificationToken.calculate_expiry(hours=24),
        )

        self.session.add(verification_token)
        await self.session.commit()
        await self.session.refresh(verification_token)

        # TODO: Send actual email (implement email service integration)
        # For now, return token for manual verification in development
        return verification_token

    async def verify_email(self, token: str) -> bool:
        """
        Verify email using verification token

        Args:
            token: Verification token from email link

        Returns:
            True if verification successful

        Raises:
            BadRequestException: If token invalid, expired, or already used
        """
        # Get token from database
        stmt = select(EmailVerificationToken).where(
            EmailVerificationToken.token == token
        )
        result = await self.session.execute(stmt)
        verification_token = result.scalar_one_or_none()

        if not verification_token:
            raise BadRequestException("Invalid verification token")

        # Check if token is valid
        if not verification_token.is_valid:
            if verification_token.is_used:
                raise BadRequestException("Verification token already used")
            if verification_token.is_expired:
                raise BadRequestException("Verification token has expired")
            raise BadRequestException("Invalid verification token")

        # Mark token as used
        verification_token.mark_as_used()

        # Update user email verification status
        user = await self.user_repo.get_by_id(verification_token.user_id)
        if not user:
            raise NotFoundException("User not found")

        user.email_verified = True
        user.email_verified_at = verification_token.used_at

        await self.session.commit()

        return True

    async def resend_verification_email(self, user_id: int) -> EmailVerificationToken:
        """
        Resend verification email to user

        Args:
            user_id: User ID to resend verification to

        Returns:
            New EmailVerificationToken

        Raises:
            NotFoundException: If user not found
            BadRequestException: If email already verified or rate limit exceeded
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        return await self.send_verification_email(user_id, user.email)

    async def get_verification_status(self, user_id: int) -> dict:
        """
        Get email verification status for user

        Args:
            user_id: User ID to check

        Returns:
            Dictionary with verification status and details

        Raises:
            NotFoundException: If user not found
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        # Get pending tokens count
        stmt = (
            select(EmailVerificationToken)
            .where(EmailVerificationToken.user_id == user_id)
            .where(EmailVerificationToken.used_at.is_(None))
        )
        result = await self.session.execute(stmt)
        pending_tokens = result.scalars().all()

        return {
            "email_verified": user.email_verified,
            "email_verified_at": (
                user.email_verified_at.isoformat() if user.email_verified_at else None
            ),
            "pending_tokens_count": len(pending_tokens),
            "can_resend": len(
                [t for t in pending_tokens if not t.is_expired]
            )
            < 3,  # Rate limit check
        }

    async def _count_recent_tokens(self, user_id: int, hours: int = 1) -> int:
        """Count verification tokens created in last N hours"""
        from app.db.base import utc_now

        cutoff_time = utc_now()
        cutoff_time = cutoff_time.replace(
            hour=cutoff_time.hour - hours if cutoff_time.hour >= hours else 0
        )

        stmt = (
            select(EmailVerificationToken)
            .where(EmailVerificationToken.user_id == user_id)
            .where(EmailVerificationToken.created_at >= cutoff_time)
        )
        result = await self.session.execute(stmt)
        tokens = result.scalars().all()
        return len(tokens)

    async def _invalidate_old_tokens(self, user_id: int) -> None:
        """Invalidate all old verification tokens for user"""
        from app.db.base import utc_now

        stmt = (
            select(EmailVerificationToken)
            .where(EmailVerificationToken.user_id == user_id)
            .where(EmailVerificationToken.used_at.is_(None))
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
