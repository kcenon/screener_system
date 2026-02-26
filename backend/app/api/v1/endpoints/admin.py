"""Admin endpoints for user account management"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import CurrentAdminUser, get_auth_service
from app.schemas import SuccessResponse, UserAdminResponse, UserSuspendRequest
from app.services import AuthService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post(
    "/users/{user_id}/suspend",
    response_model=UserAdminResponse,
    summary="Suspend user account",
    description="Suspend a user account and invalidate all active sessions",
)
async def suspend_user(
    user_id: int,
    suspend_data: UserSuspendRequest,
    admin_user: CurrentAdminUser,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserAdminResponse:
    """
    Suspend a user account

    Args:
        user_id: ID of the user to suspend
        suspend_data: Suspension reason
        admin_user: Current admin user (authorization)
        auth_service: AuthService dependency

    Returns:
        Updated user data

    Raises:
        400: User already suspended or is an admin
        404: User not found
    """
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot suspend your own account",
        )

    try:
        user = await auth_service.suspend_user(
            user_id=user_id, reason=suspend_data.reason
        )
        return UserAdminResponse.model_validate(user)

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        ) from e


@router.post(
    "/users/{user_id}/unsuspend",
    response_model=UserAdminResponse,
    summary="Unsuspend user account",
    description="Reactivate a suspended user account",
)
async def unsuspend_user(
    user_id: int,
    admin_user: CurrentAdminUser,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserAdminResponse:
    """
    Unsuspend a user account

    Args:
        user_id: ID of the user to unsuspend
        admin_user: Current admin user (authorization)
        auth_service: AuthService dependency

    Returns:
        Updated user data

    Raises:
        400: User not suspended
        404: User not found
    """
    try:
        user = await auth_service.unsuspend_user(user_id=user_id)
        return UserAdminResponse.model_validate(user)

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        ) from e


@router.get(
    "/users/{user_id}",
    response_model=UserAdminResponse,
    summary="Get user details (admin)",
    description="Get detailed user information including suspension status",
)
async def get_user_detail(
    user_id: int,
    admin_user: CurrentAdminUser,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserAdminResponse:
    """
    Get user details for admin

    Args:
        user_id: ID of the user
        admin_user: Current admin user (authorization)
        auth_service: AuthService dependency

    Returns:
        User data with admin-level details

    Raises:
        404: User not found
    """
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return UserAdminResponse.model_validate(user)
