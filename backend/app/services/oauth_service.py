"""OAuth service for social login authentication"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.security import create_access_token, create_refresh_token
from app.db.models import OAuthState, SocialAccount, User, UserSession
from app.repositories import (
    OAuthStateRepository,
    SocialAccountRepository,
    UserRepository,
    UserSessionRepository,
)
from app.schemas import TokenResponse, UserResponse
from app.schemas.oauth import (
    OAuthAuthorizationResponse,
    OAuthProviderEnum,
    OAuthUserInfo,
    SocialAccountResponse,
    SocialAccountsListResponse,
)
from app.services.oauth_providers import get_oauth_provider, is_provider_configured


class OAuthService:
    """
    Service for OAuth authentication operations.

    Handles:
    - Authorization URL generation
    - OAuth callback processing (login/signup)
    - Social account linking/unlinking
    - Linked accounts management
    """

    def __init__(self, session: AsyncSession):
        """Initialize service with database session"""
        self.session = session
        self.user_repo = UserRepository(session)
        self.session_repo = UserSessionRepository(session)
        self.social_account_repo = SocialAccountRepository(session)
        self.oauth_state_repo = OAuthStateRepository(session)

    async def get_authorization_url(
        self,
        provider: str,
        redirect_url: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> OAuthAuthorizationResponse:
        """
        Generate OAuth authorization URL.

        Args:
            provider: OAuth provider name (google, kakao, naver)
            redirect_url: Optional URL to redirect after OAuth
            user_id: Optional user ID for account linking flow

        Returns:
            OAuthAuthorizationResponse with authorization URL and state

        Raises:
            BadRequestException: If provider is not configured
        """
        provider = provider.lower()

        if not is_provider_configured(provider):
            raise BadRequestException(
                f"OAuth provider '{provider}' is not configured"
            )

        oauth_provider = get_oauth_provider(provider)
        if not oauth_provider:
            raise BadRequestException(f"OAuth provider '{provider}' is not available")

        # Generate random state token for CSRF protection
        state = secrets.token_urlsafe(32)

        # Store state in database
        oauth_state = OAuthState.create_state(
            state=state,
            provider=provider.upper(),
            redirect_url=redirect_url or settings.OAUTH_FRONTEND_CALLBACK_URL,
            user_id=user_id,
            expiry_minutes=settings.OAUTH_STATE_EXPIRY_MINUTES,
        )
        await self.oauth_state_repo.create(oauth_state)
        await self.session.commit()

        # Generate authorization URL
        authorization_url = oauth_provider.get_authorization_url(state)

        return OAuthAuthorizationResponse(
            authorization_url=authorization_url,
            state=state,
            provider=OAuthProviderEnum(provider),
        )

    async def handle_callback(
        self,
        provider: str,
        code: str,
        state: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[TokenResponse, Optional[str]]:
        """
        Handle OAuth callback for login/signup.

        Args:
            provider: OAuth provider name
            code: Authorization code from provider
            state: State token for CSRF validation
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Tuple of (TokenResponse, redirect_url)

        Raises:
            BadRequestException: If state is invalid or OAuth fails
        """
        provider = provider.lower()

        # Validate and consume state token
        oauth_state = await self.oauth_state_repo.validate_and_consume(state)
        if not oauth_state:
            raise BadRequestException("Invalid or expired OAuth state token")

        # Get OAuth provider
        oauth_provider = get_oauth_provider(provider)
        if not oauth_provider:
            raise BadRequestException(f"OAuth provider '{provider}' is not available")

        try:
            # Exchange code for token
            token_response = await oauth_provider.exchange_code_for_token(code)

            # Get user info from provider
            user_info = await oauth_provider.get_user_info(token_response.access_token)
        except Exception as e:
            raise BadRequestException(f"OAuth authentication failed: {str(e)}") from e
        finally:
            await oauth_provider.close()

        # Check if this is account linking flow
        if oauth_state.user_id:
            # Link account to existing user
            await self._link_social_account(
                user_id=oauth_state.user_id,
                user_info=user_info,
                access_token=token_response.access_token,
                refresh_token=token_response.refresh_token,
                expires_in=token_response.expires_in,
            )
            # Get user for token response
            user = await self.user_repo.get_by_id(oauth_state.user_id)
        else:
            # Login or signup flow
            user = await self._find_or_create_user(
                user_info=user_info,
                access_token=token_response.access_token,
                refresh_token=token_response.refresh_token,
                expires_in=token_response.expires_in,
            )

        # Update last login
        user.update_last_login()
        await self.user_repo.update(user)

        # Create session tokens
        auth_response = await self._create_user_session(
            user, ip_address=ip_address, user_agent=user_agent
        )

        await self.session.commit()

        return auth_response, oauth_state.redirect_url

    async def link_account(
        self,
        user_id: int,
        provider: str,
        code: str,
        state: str,
    ) -> SocialAccountResponse:
        """
        Link a social account to an existing user.

        Args:
            user_id: ID of the user to link account to
            provider: OAuth provider name
            code: Authorization code from provider
            state: State token for CSRF validation

        Returns:
            SocialAccountResponse with linked account details

        Raises:
            BadRequestException: If account is already linked or OAuth fails
            NotFoundException: If user not found
        """
        provider = provider.lower()

        # Validate state
        oauth_state = await self.oauth_state_repo.validate_and_consume(state)
        if not oauth_state:
            raise BadRequestException("Invalid or expired OAuth state token")

        # Verify user exists
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        # Check if user already has this provider linked
        existing = await self.social_account_repo.get_by_user_and_provider(
            user_id, provider
        )
        if existing:
            raise BadRequestException(
                f"User already has a {provider.upper()} account linked"
            )

        # Get OAuth provider
        oauth_provider = get_oauth_provider(provider)
        if not oauth_provider:
            raise BadRequestException(f"OAuth provider '{provider}' is not available")

        try:
            # Exchange code for token
            token_response = await oauth_provider.exchange_code_for_token(code)

            # Get user info from provider
            user_info = await oauth_provider.get_user_info(token_response.access_token)
        except Exception as e:
            raise BadRequestException(f"OAuth authentication failed: {str(e)}") from e
        finally:
            await oauth_provider.close()

        # Check if this social account is already linked to another user
        existing_account = await self.social_account_repo.get_by_provider_user_id(
            provider.upper(), user_info.provider_user_id
        )
        if existing_account:
            raise BadRequestException(
                f"This {provider.upper()} account is already linked to another user"
            )

        # Link the account
        social_account = await self._link_social_account(
            user_id=user_id,
            user_info=user_info,
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token,
            expires_in=token_response.expires_in,
        )

        await self.session.commit()

        return SocialAccountResponse.model_validate(social_account)

    async def unlink_account(self, user_id: int, provider: str) -> bool:
        """
        Unlink a social account from a user.

        Args:
            user_id: ID of the user
            provider: OAuth provider to unlink

        Returns:
            True if account was unlinked

        Raises:
            BadRequestException: If this is the only login method
            NotFoundException: If account not found
        """
        provider = provider.lower()

        # Get user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        # Check if user has this provider linked
        social_account = await self.social_account_repo.get_by_user_and_provider(
            user_id, provider
        )
        if not social_account:
            raise NotFoundException(
                f"No {provider.upper()} account linked to this user"
            )

        # Check if user has password or other social accounts
        has_password = user.password_hash is not None
        social_count = await self.social_account_repo.count_by_user(user_id)

        if not has_password and social_count <= 1:
            raise BadRequestException(
                "Cannot unlink the only login method. "
                "Please set a password or link another social account first."
            )

        # Unlink the account
        await self.social_account_repo.delete(social_account)
        await self.session.commit()

        return True

    async def get_linked_accounts(self, user_id: int) -> SocialAccountsListResponse:
        """
        Get all social accounts linked to a user.

        Args:
            user_id: ID of the user

        Returns:
            SocialAccountsListResponse with list of linked accounts
        """
        accounts = await self.social_account_repo.get_all_by_user(user_id)

        return SocialAccountsListResponse(
            accounts=[
                SocialAccountResponse.model_validate(account)
                for account in accounts
            ],
            total=len(accounts),
        )

    async def _find_or_create_user(
        self,
        user_info: OAuthUserInfo,
        access_token: str,
        refresh_token: Optional[str],
        expires_in: Optional[int],
    ) -> User:
        """
        Find existing user or create new one from OAuth info.

        First checks for existing social account link,
        then checks for user with same email,
        finally creates new user.
        """
        provider = user_info.provider.value.upper()

        # Check if social account already exists
        social_account = await self.social_account_repo.get_by_provider_user_id(
            provider, user_info.provider_user_id
        )

        if social_account:
            # Update tokens
            social_account.update_tokens(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=self._calculate_token_expiry(expires_in),
            )
            await self.social_account_repo.update(social_account)

            # Return existing user
            return await self.user_repo.get_by_id(social_account.user_id)

        # Check if user with same email exists
        user = None
        if user_info.email:
            user = await self.user_repo.get_by_email(user_info.email)

        if user:
            # Link social account to existing user
            await self._link_social_account(
                user_id=user.id,
                user_info=user_info,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
            )
            # Auto-verify email if provider confirms it
            if not user.email_verified:
                user.email_verified = True
                await self.user_repo.update(user)
            return user

        # Create new user
        user = User(
            email=user_info.email or f"{provider.lower()}_{user_info.provider_user_id}@oauth.local",
            password_hash=None,  # OAuth-only user
            name=user_info.name,
            email_verified=True if user_info.email else False,  # Auto-verify if email from provider
        )
        await self.user_repo.create(user)

        # Link social account
        await self._link_social_account(
            user_id=user.id,
            user_info=user_info,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )

        return user

    async def _link_social_account(
        self,
        user_id: int,
        user_info: OAuthUserInfo,
        access_token: str,
        refresh_token: Optional[str],
        expires_in: Optional[int],
    ) -> SocialAccount:
        """Create or update social account link"""
        provider = user_info.provider.value.upper()

        # Check if already linked
        existing = await self.social_account_repo.get_by_user_and_provider(
            user_id, provider
        )

        if existing:
            # Update existing
            existing.provider_email = user_info.email
            existing.provider_name = user_info.name
            existing.provider_picture = user_info.picture
            existing.update_tokens(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=self._calculate_token_expiry(expires_in),
            )
            return await self.social_account_repo.update(existing)

        # Create new
        social_account = SocialAccount(
            user_id=user_id,
            provider=provider,
            provider_user_id=user_info.provider_user_id,
            provider_email=user_info.email,
            provider_name=user_info.name,
            provider_picture=user_info.picture,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=self._calculate_token_expiry(expires_in),
        )
        return await self.social_account_repo.create(social_account)

    def _calculate_token_expiry(
        self, expires_in: Optional[int]
    ) -> Optional[datetime]:
        """Calculate token expiration datetime"""
        if expires_in is None:
            return None
        return datetime.now(timezone.utc) + timedelta(seconds=expires_in)

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

        # Create response
        user_response = UserResponse.model_validate(user)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_response,
        )
