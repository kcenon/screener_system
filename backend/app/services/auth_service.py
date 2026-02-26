"""Authentication service for user registration, login, and token management"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
    verify_token_type,
)
from app.db.models import User, UserSession
from app.repositories import UserRepository, UserSessionRepository
from app.schemas import TokenResponse, UserCreate, UserLogin, UserResponse


class AuthService:
    """Service for authentication operations"""

    def __init__(self, session: AsyncSession):
        """Initialize service with database session"""
        self.session = session
        self.user_repo = UserRepository(session)
        self.session_repo = UserSessionRepository(session)

    async def register_user(
        self,
        user_data: UserCreate,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """
        Register new user and return authentication tokens

        Args:
            user_data: User registration data
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            TokenResponse with access/refresh tokens and user data

        Raises:
            ValueError: If email already exists
        """
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise ValueError(f"Email {user_data.email} is already registered")

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            name=user_data.name,
            subscription_tier="free",
        )

        await self.user_repo.create(new_user)
        await self.session.commit()

        # Create tokens and session
        return await self._create_user_session(
            new_user, ip_address=ip_address, user_agent=user_agent
        )

    async def authenticate_user(
        self,
        credentials: UserLogin,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """
        Authenticate user with email and password

        Args:
            credentials: User login credentials
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            TokenResponse with access/refresh tokens and user data

        Raises:
            UnauthorizedException: If credentials are invalid
        """
        # Get user by email
        user = await self.user_repo.get_by_email(credentials.email)
        if not user:
            raise UnauthorizedException("Invalid email or password")

        # Verify password
        if not verify_password(credentials.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        # Check if account is suspended
        if not user.is_active:
            raise UnauthorizedException("Account is suspended")

        # Update last login
        user.update_last_login()
        await self.user_repo.update(user)
        await self.session.commit()

        # Create tokens and session
        return await self._create_user_session(
            user, ip_address=ip_address, user_agent=user_agent
        )

    async def refresh_access_token(
        self, refresh_token: str
    ) -> Tuple[str, UserResponse]:
        """
        Refresh access token using valid refresh token

        Args:
            refresh_token: JWT refresh token

        Returns:
            Tuple of (new access token, user data)

        Raises:
            UnauthorizedException: If refresh token is invalid or expired
        """
        # Verify token type
        if not verify_token_type(refresh_token, "refresh"):
            raise UnauthorizedException("Invalid refresh token type")

        # Get session from database
        user_session = await self.session_repo.get_by_refresh_token(refresh_token)
        if not user_session:
            raise UnauthorizedException("Invalid refresh token")

        # Check if session is valid
        if not user_session.is_valid:
            raise UnauthorizedException("Refresh token has been revoked or expired")

        # Get user
        user = await self.user_repo.get_by_id(user_session.user_id)
        if not user:
            raise UnauthorizedException("User not found")

        # Check if account is suspended
        if not user.is_active:
            raise UnauthorizedException("Account is suspended")

        # Update session last accessed
        user_session.update_last_accessed()
        await self.session_repo.create(user_session)
        await self.session.commit()

        # Create new access token
        access_token = create_access_token(user.id)
        user_response = UserResponse.model_validate(user)

        return access_token, user_response

    async def logout(self, refresh_token: str) -> bool:
        """
        Logout user by revoking refresh token

        Args:
            refresh_token: JWT refresh token to revoke

        Returns:
            True if token was revoked, False if not found
        """
        success = await self.session_repo.revoke_by_refresh_token(refresh_token)
        if success:
            await self.session.commit()
        return success

    async def logout_all_sessions(self, user_id: int) -> int:
        """
        Logout user from all devices by revoking all sessions

        Args:
            user_id: User ID

        Returns:
            Number of sessions revoked
        """
        count = await self.session_repo.revoke_all_user_sessions(user_id)
        await self.session.commit()
        return count

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return await self.user_repo.get_by_id(user_id)

    async def verify_access_token(self, token: str) -> User:
        """
        Verify access token and return user

        Args:
            token: JWT access token

        Returns:
            User object

        Raises:
            UnauthorizedException: If token is invalid or user not found
        """
        try:
            # Decode and verify token
            payload = decode_token(token)

            # Verify token type
            if payload.get("type") != "access":
                raise UnauthorizedException("Invalid token type")

            # Extract user ID
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise UnauthorizedException("Invalid token payload")

            user_id = int(user_id_str)

            # Get user from database
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise UnauthorizedException("User not found")

            # Check if account is suspended
            if not user.is_active:
                raise UnauthorizedException("Account is suspended")

            return user

        except JWTError as e:
            raise UnauthorizedException(f"Invalid token: {str(e)}") from e
        except ValueError as e:
            raise UnauthorizedException(f"Invalid user ID: {str(e)}") from e

    async def suspend_user(self, user_id: int, reason: str) -> User:
        """
        Suspend a user account and invalidate all sessions

        Args:
            user_id: ID of the user to suspend
            reason: Reason for suspension

        Returns:
            Updated user object

        Raises:
            ValueError: If user not found or already suspended
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        if user.is_suspended:
            raise ValueError("User is already suspended")

        user.is_suspended = True
        user.suspended_at = datetime.now(timezone.utc)
        user.suspension_reason = reason

        await self.user_repo.update(user)

        # Invalidate all existing sessions
        await self.session_repo.revoke_all_user_sessions(user_id)
        await self.session.commit()

        return user

    async def unsuspend_user(self, user_id: int) -> User:
        """
        Unsuspend a user account

        Args:
            user_id: ID of the user to unsuspend

        Returns:
            Updated user object

        Raises:
            ValueError: If user not found or not suspended
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        if not user.is_suspended:
            raise ValueError("User is not suspended")

        user.is_suspended = False
        user.suspended_at = None
        user.suspension_reason = None

        await self.user_repo.update(user)
        await self.session.commit()

        return user

    async def _create_user_session(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Create new session with tokens for user"""
        # Create tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Create session in database
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        user_session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

        await self.session_repo.create(user_session)
        await self.session.commit()

        # Create response
        user_response = UserResponse.model_validate(user)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_response,
        )
