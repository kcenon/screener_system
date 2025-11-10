"""Authentication endpoints"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.dependencies import CurrentActiveUser, get_auth_service
from app.core.exceptions import UnauthorizedException
from app.schemas import (RefreshTokenRequest, TokenResponse, UserCreate,
                         UserLogin, UserResponse)
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password",
)
async def register(
    user_data: UserCreate,
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """
    Register a new user account

    Args:
        user_data: User registration data (email, password, name)
        request: FastAPI request object
        auth_service: AuthService dependency

    Returns:
        TokenResponse with access token, refresh token, and user data

    Raises:
        409: Email already registered
        400: Invalid data or weak password
    """
    try:
        # Extract client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Register user
        token_response = await auth_service.register_user(
            user_data=user_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return token_response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user with email and password, returns JWT tokens",
)
async def login(
    credentials: UserLogin,
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """
    Authenticate user and return tokens

    Args:
        credentials: User login credentials (email, password)
        request: FastAPI request object
        auth_service: AuthService dependency

    Returns:
        TokenResponse with access token, refresh token, and user data

    Raises:
        401: Invalid credentials
    """
    try:
        # Extract client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Authenticate user
        token_response = await auth_service.authenticate_user(
            credentials=credentials,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return token_response

    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get new access token using valid refresh token",
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """
    Refresh access token using refresh token

    Args:
        refresh_data: Refresh token request data
        auth_service: AuthService dependency

    Returns:
        TokenResponse with new access token and user data

    Raises:
        401: Invalid or expired refresh token
    """
    try:
        # Refresh access token
        access_token, user = await auth_service.refresh_access_token(
            refresh_data.refresh_token
        )

        # Return response (keep same refresh token)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_data.refresh_token,
            user=user,
        )

    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
    description="Revoke refresh token to logout user from current device",
)
async def logout(
    refresh_data: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    """
    Logout user by revoking refresh token

    Args:
        refresh_data: Refresh token to revoke
        auth_service: AuthService dependency

    Raises:
        404: Token not found
    """
    success = await auth_service.logout(refresh_data.refresh_token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found",
        )


@router.post(
    "/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout from all devices",
    description="Revoke all refresh tokens to logout user from all devices",
)
async def logout_all(
    current_user: CurrentActiveUser,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    """
    Logout user from all devices

    Args:
        current_user: Current authenticated user
        auth_service: AuthService dependency
    """
    await auth_service.logout_all_sessions(current_user.id)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about currently authenticated user",
)
async def get_current_user_info(current_user: CurrentActiveUser) -> UserResponse:
    """
    Get current user information

    Args:
        current_user: Current authenticated user

    Returns:
        User data
    """
    return UserResponse.model_validate(current_user)
