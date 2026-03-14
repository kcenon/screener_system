"""Authentication endpoints"""

from typing import Annotated, Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status

from app.api.dependencies import (
    CurrentActiveUser,
    get_auth_service,
    get_email_verification_service,
    get_password_reset_service,
)
from app.core.config import settings
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    UnauthorizedException,
)
from app.schemas import (
    EmailVerificationRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    SuccessResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    VerificationStatusResponse,
)
from app.services import AuthService, EmailVerificationService, PasswordResetService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_auth_cookies(
    response: Response, access_token: str, refresh_token: str
) -> None:
    """Set HttpOnly auth cookies in the response."""
    is_production = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/v1/auth/refresh",
    )


def _clear_auth_cookies(response: Response) -> None:
    """Clear auth cookies from the response."""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/v1/auth/refresh")


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
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """
    Register a new user account

    Args:
        user_data: User registration data (email, password, name)
        request: FastAPI request object
        response: FastAPI response object for setting cookies
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

        # Set HttpOnly cookies
        _set_auth_cookies(
            response, token_response.access_token, token_response.refresh_token
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
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """
    Authenticate user and return tokens

    Args:
        credentials: User login credentials (email, password)
        request: FastAPI request object
        response: FastAPI response object for setting cookies
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

        # Set HttpOnly cookies
        _set_auth_cookies(
            response, token_response.access_token, token_response.refresh_token
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
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_data: Optional[RefreshTokenRequest] = None,
    refresh_token_cookie: Optional[str] = Cookie(default=None, alias="refresh_token"),
) -> TokenResponse:
    """
    Refresh access token using refresh token

    Accepts refresh token from HttpOnly cookie (preferred) or request body (fallback).

    Args:
        request: FastAPI request object
        response: FastAPI response object for setting cookies
        auth_service: AuthService dependency
        refresh_data: Optional refresh token in request body (backward compatibility)
        refresh_token_cookie: Refresh token from HttpOnly cookie

    Returns:
        TokenResponse with new access token and user data

    Raises:
        401: Invalid or expired refresh token, or no token provided
    """
    # Cookie takes precedence; fall back to request body
    token = refresh_token_cookie or (
        refresh_data.refresh_token if refresh_data else None
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    try:
        # Refresh access token
        access_token, user = await auth_service.refresh_access_token(token)

        # Set new access token cookie (keep same refresh token)
        _set_auth_cookies(response, access_token, token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=token,
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
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_data: Optional[RefreshTokenRequest] = None,
    refresh_token_cookie: Optional[str] = Cookie(default=None, alias="refresh_token"),
) -> None:
    """
    Logout user by revoking refresh token and clearing cookies

    Accepts refresh token from HttpOnly cookie (preferred) or request body (fallback).

    Args:
        response: FastAPI response object for clearing cookies
        auth_service: AuthService dependency
        refresh_data: Optional refresh token in request body (backward compatibility)
        refresh_token_cookie: Refresh token from HttpOnly cookie

    Raises:
        404: Token not found
    """
    token = refresh_token_cookie or (
        refresh_data.refresh_token if refresh_data else None
    )

    if token:
        success = await auth_service.logout(token)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Refresh token not found",
            )

    # Always clear cookies regardless of token presence
    _clear_auth_cookies(response)


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


# Email Verification Endpoints


@router.post(
    "/verify-email",
    response_model=SuccessResponse,
    summary="Verify email address",
    description="Verify user email using verification token from email",
)
async def verify_email(
    request: EmailVerificationRequest,
    verification_service: Annotated[
        EmailVerificationService, Depends(get_email_verification_service)
    ],
) -> SuccessResponse:
    """
    Verify user email address

    Args:
        request: Email verification request with token
        verification_service: EmailVerificationService dependency

    Returns:
        Success response

    Raises:
        400: Invalid, expired, or already used token
    """
    try:
        await verification_service.verify_email(request.token)
        return SuccessResponse(success=True, message="Email verified successfully")

    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/resend-verification",
    response_model=SuccessResponse,
    summary="Resend verification email",
    description="Resend email verification link to authenticated user",
)
async def resend_verification(
    current_user: CurrentActiveUser,
    verification_service: Annotated[
        EmailVerificationService, Depends(get_email_verification_service)
    ],
) -> SuccessResponse:
    """
    Resend email verification to current user

    Args:
        current_user: Current authenticated user
        verification_service: EmailVerificationService dependency

    Returns:
        Success response

    Raises:
        400: Email already verified or rate limit exceeded
        404: User not found
    """
    try:
        await verification_service.resend_verification_email(current_user.id)
        return SuccessResponse(
            success=True,
            message="Verification email sent successfully",
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
    "/verification-status",
    response_model=VerificationStatusResponse,
    summary="Get email verification status",
    description="Check email verification status for authenticated user",
)
async def get_verification_status(
    current_user: CurrentActiveUser,
    verification_service: Annotated[
        EmailVerificationService, Depends(get_email_verification_service)
    ],
) -> VerificationStatusResponse:
    """
    Get email verification status

    Args:
        current_user: Current authenticated user
        verification_service: EmailVerificationService dependency

    Returns:
        Verification status information

    Raises:
        404: User not found
    """
    try:
        status_data = await verification_service.get_verification_status(
            current_user.id
        )
        return VerificationStatusResponse(**status_data)

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


# Password Reset Endpoints


@router.post(
    "/forgot-password",
    response_model=SuccessResponse,
    summary="Request password reset",
    description="Request password reset link via email",
)
async def forgot_password(
    request: PasswordResetRequest,
    reset_service: Annotated[PasswordResetService, Depends(get_password_reset_service)],
) -> SuccessResponse:
    """
    Request password reset

    Args:
        request: Password reset request with email
        reset_service: PasswordResetService dependency

    Returns:
        Success response (always, to prevent user enumeration)

    Note:
        Always returns success even if email doesn't exist
        to prevent user enumeration attacks
    """
    try:
        await reset_service.request_password_reset(request.email)
        return SuccessResponse(
            success=True,
            message="If the email exists, a password reset link has been sent",
        )

    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/validate-reset-token",
    response_model=SuccessResponse,
    summary="Validate password reset token",
    description="Check if password reset token is valid",
)
async def validate_reset_token(
    token: str,
    reset_service: Annotated[PasswordResetService, Depends(get_password_reset_service)],
) -> SuccessResponse:
    """
    Validate password reset token

    Args:
        token: Password reset token (query parameter)
        reset_service: PasswordResetService dependency

    Returns:
        Success response if token is valid

    Raises:
        400: Token is invalid or expired
    """
    is_valid = await reset_service.validate_reset_token(token)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        )

    return SuccessResponse(success=True, message="Token is valid")


@router.post(
    "/reset-password",
    response_model=SuccessResponse,
    summary="Reset password",
    description="Reset user password using reset token",
)
async def reset_password(
    request: PasswordResetConfirm,
    reset_service: Annotated[PasswordResetService, Depends(get_password_reset_service)],
) -> SuccessResponse:
    """
    Reset user password

    Args:
        request: Password reset confirmation with token and new password
        reset_service: PasswordResetService dependency

    Returns:
        Success response

    Raises:
        400: Invalid token, expired token, or weak password
        404: User not found
    """
    try:
        await reset_service.reset_password(request.token, request.new_password)
        return SuccessResponse(
            success=True,
            message="Password reset successfully. All sessions have been logged out.",
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
