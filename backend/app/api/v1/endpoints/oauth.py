"""OAuth authentication endpoints for social login"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from app.api.dependencies import (CurrentActiveUser, get_oauth_service)
from app.core.config import settings
from app.core.exceptions import BadRequestException, NotFoundException
from app.schemas import TokenResponse
from app.schemas.oauth import (
    OAuthAuthorizationResponse,
    OAuthCallbackRequest,
    OAuthUnlinkResponse,
    SocialAccountResponse,
    SocialAccountsListResponse,
)
from app.services import OAuthService

router = APIRouter(prefix="/auth/oauth", tags=["OAuth"])


@router.get(
    "/{provider}/login",
    response_model=OAuthAuthorizationResponse,
    summary="Get OAuth authorization URL",
    description="Generate OAuth authorization URL for the specified provider",
)
async def get_oauth_login_url(
    provider: str,
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    redirect_url: Optional[str] = Query(
        None, description="URL to redirect after OAuth (optional)"
    ),
) -> OAuthAuthorizationResponse:
    """
    Get OAuth authorization URL for login/signup.

    Args:
        provider: OAuth provider (google, kakao, naver)
        redirect_url: Optional redirect URL after OAuth
        oauth_service: OAuthService dependency

    Returns:
        OAuthAuthorizationResponse with authorization URL

    Raises:
        400: Provider not configured or not supported
    """
    try:
        return await oauth_service.get_authorization_url(
            provider=provider,
            redirect_url=redirect_url,
        )
    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/{provider}/callback",
    response_model=TokenResponse,
    summary="Handle OAuth callback",
    description="Process OAuth callback and return authentication tokens",
)
async def handle_oauth_callback(
    provider: str,
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: str = Query(..., description="State token for CSRF validation"),
    request: Request = None,
) -> TokenResponse:
    """
    Handle OAuth callback from provider.

    This endpoint processes the OAuth callback, exchanges the authorization
    code for tokens, and either logs in an existing user or creates a new one.

    Args:
        provider: OAuth provider (google, kakao, naver)
        code: Authorization code from provider
        state: State token for CSRF validation
        request: FastAPI request object
        oauth_service: OAuthService dependency

    Returns:
        TokenResponse with access/refresh tokens and user data

    Raises:
        400: Invalid state, OAuth failure, or provider error
    """
    try:
        # Extract client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        token_response, redirect_url = await oauth_service.handle_callback(
            provider=provider,
            code=code,
            state=state,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return token_response

    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/{provider}/callback/redirect",
    summary="Handle OAuth callback with redirect",
    description="Process OAuth callback and redirect to frontend with tokens",
)
async def handle_oauth_callback_redirect(
    provider: str,
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: str = Query(..., description="State token for CSRF validation"),
    request: Request = None,
) -> RedirectResponse:
    """
    Handle OAuth callback and redirect to frontend.

    This endpoint is used when the OAuth flow should redirect the user
    to the frontend with tokens in the URL fragment.

    Args:
        provider: OAuth provider (google, kakao, naver)
        code: Authorization code from provider
        state: State token for CSRF validation
        request: FastAPI request object
        oauth_service: OAuthService dependency

    Returns:
        RedirectResponse to frontend with tokens

    Raises:
        400: Invalid state, OAuth failure, or provider error
    """
    try:
        # Extract client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        token_response, redirect_url = await oauth_service.handle_callback(
            provider=provider,
            code=code,
            state=state,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Build redirect URL with tokens
        frontend_url = redirect_url or settings.OAUTH_FRONTEND_CALLBACK_URL
        redirect_params = (
            f"?access_token={token_response.access_token}"
            f"&refresh_token={token_response.refresh_token}"
            f"&provider={provider}"
        )

        return RedirectResponse(
            url=f"{frontend_url}{redirect_params}",
            status_code=status.HTTP_302_FOUND,
        )

    except BadRequestException as e:
        # Redirect to frontend with error
        frontend_url = settings.OAUTH_FRONTEND_CALLBACK_URL
        error_url = f"{frontend_url}?error={str(e)}&provider={provider}"
        return RedirectResponse(
            url=error_url,
            status_code=status.HTTP_302_FOUND,
        )


@router.get(
    "/{provider}/link",
    response_model=OAuthAuthorizationResponse,
    summary="Get OAuth URL for account linking",
    description=(
        "Generate OAuth authorization URL to link social account to existing user"
    ),
)
async def get_oauth_link_url(
    provider: str,
    current_user: CurrentActiveUser,
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    redirect_url: Optional[str] = Query(
        None, description="URL to redirect after linking (optional)"
    ),
) -> OAuthAuthorizationResponse:
    """
    Get OAuth authorization URL for linking social account.

    Requires authentication. The returned URL will link the social
    account to the currently authenticated user.

    Args:
        provider: OAuth provider (google, kakao, naver)
        current_user: Currently authenticated user
        redirect_url: Optional redirect URL after linking
        oauth_service: OAuthService dependency

    Returns:
        OAuthAuthorizationResponse with authorization URL

    Raises:
        400: Provider not configured or not supported
    """
    try:
        return await oauth_service.get_authorization_url(
            provider=provider,
            redirect_url=redirect_url,
            user_id=current_user.id,
        )
    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/{provider}/link",
    response_model=SocialAccountResponse,
    summary="Link social account",
    description="Link a social account to the authenticated user",
)
async def link_social_account(
    provider: str,
    callback_data: OAuthCallbackRequest,
    current_user: CurrentActiveUser,
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
) -> SocialAccountResponse:
    """
    Link a social account to the current user.

    Requires authentication. Exchange the OAuth code and link the
    social account to the currently authenticated user.

    Args:
        provider: OAuth provider (google, kakao, naver)
        callback_data: OAuth callback data with code and state
        current_user: Currently authenticated user
        oauth_service: OAuthService dependency

    Returns:
        SocialAccountResponse with linked account details

    Raises:
        400: Account already linked, OAuth failure, or invalid state
        401: Not authenticated
        404: User not found
    """
    try:
        return await oauth_service.link_account(
            user_id=current_user.id,
            provider=provider,
            code=callback_data.code,
            state=callback_data.state,
        )
    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete(
    "/{provider}/unlink",
    response_model=OAuthUnlinkResponse,
    summary="Unlink social account",
    description="Unlink a social account from the authenticated user",
)
async def unlink_social_account(
    provider: str,
    current_user: CurrentActiveUser,
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
) -> OAuthUnlinkResponse:
    """
    Unlink a social account from the current user.

    Requires authentication. Cannot unlink if this is the only login
    method (user must have password or another social account linked).

    Args:
        provider: OAuth provider (google, kakao, naver)
        current_user: Currently authenticated user
        oauth_service: OAuthService dependency

    Returns:
        OAuthUnlinkResponse confirming the unlink

    Raises:
        400: Cannot unlink only login method
        401: Not authenticated
        404: Social account not found
    """
    try:
        await oauth_service.unlink_account(
            user_id=current_user.id,
            provider=provider,
        )
        return OAuthUnlinkResponse(
            success=True,
            message=f"Successfully unlinked {provider.upper()} account",
            provider=provider.upper(),
        )
    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get(
    "/accounts",
    response_model=SocialAccountsListResponse,
    summary="List linked social accounts",
    description="Get all social accounts linked to the authenticated user",
)
async def list_linked_accounts(
    current_user: CurrentActiveUser,
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
) -> SocialAccountsListResponse:
    """
    Get all social accounts linked to the current user.

    Requires authentication.

    Args:
        current_user: Currently authenticated user
        oauth_service: OAuthService dependency

    Returns:
        SocialAccountsListResponse with list of linked accounts

    Raises:
        401: Not authenticated
    """
    return await oauth_service.get_linked_accounts(current_user.id)


@router.get(
    "/providers",
    summary="List available OAuth providers",
    description="Get list of configured OAuth providers",
)
async def list_available_providers() -> dict:
    """
    Get list of available OAuth providers.

    Returns providers that are properly configured with credentials.

    Returns:
        Dictionary with list of available providers
    """
    from app.services.oauth_providers import is_provider_configured

    providers = []
    for provider in ["google", "kakao", "naver"]:
        if is_provider_configured(provider):
            providers.append(provider)

    return {
        "providers": providers,
        "total": len(providers),
    }
