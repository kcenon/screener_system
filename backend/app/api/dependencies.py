"""API dependencies for dependency injection"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.db.models import User
from app.db.session import get_db
from app.services import (
    AIService,
    AuthService,
    EmailVerificationService,
    OAuthService,
    PasswordResetService,
    StripeService,
    SubscriptionService,
)
from app.services.watchlist_service import WatchlistService

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthService:
    """Get AuthService instance with database session"""
    return AuthService(db)


async def get_watchlist_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WatchlistService:
    """Get WatchlistService instance with database session"""
    return WatchlistService(db)


async def get_email_verification_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EmailVerificationService:
    """Get EmailVerificationService instance with database session"""
    return EmailVerificationService(db)


async def get_password_reset_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PasswordResetService:
    """Get PasswordResetService instance with database session"""
    return PasswordResetService(db)


async def get_oauth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OAuthService:
    """Get OAuthService instance with database session"""
    return OAuthService(db)


async def get_stripe_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StripeService:
    """Get StripeService instance with database session"""
    return StripeService(db)


async def get_subscription_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SubscriptionService:
    """Get SubscriptionService instance with database session"""
    return SubscriptionService(db)


async def get_ai_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AIService:
    """Get AIService instance with database session"""
    return AIService()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token from Authorization header
        auth_service: AuthService instance

    Returns:
        Current authenticated user

    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    try:
        # Extract token from credentials
        token = credentials.credentials

        # Verify token and get user
        user = await auth_service.verify_access_token(token)

        return user

    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current active user (can add additional checks here)

    Args:
        current_user: Current authenticated user

    Returns:
        Current active user

    Raises:
        HTTPException 403: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return current_user


# Type aliases for cleaner endpoint signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
