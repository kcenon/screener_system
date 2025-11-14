"""User portfolio endpoints (watchlists, dashboard, activities)"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import CurrentActiveUser, get_watchlist_service
from app.schemas.watchlist import (
    DashboardSummary,
    UserActivityListResponse,
    WatchlistCreate,
    WatchlistListResponse,
    WatchlistResponse,
    WatchlistSummary,
    WatchlistUpdate,
)
from app.services.watchlist_service import WatchlistService

router = APIRouter(prefix="/users", tags=["Users"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


async def build_watchlist_response(
    watchlist, watchlist_service: WatchlistService, load_stocks: bool = True
) -> WatchlistResponse:
    """
    Build WatchlistResponse from Watchlist model

    Args:
        watchlist: Watchlist model instance
        watchlist_service: WatchlistService instance for database access
        load_stocks: Whether to load stock details

    Returns:
        WatchlistResponse with all stock data loaded
    """
    from app.db.models import WatchlistStock
    from app.db.models.stock import Stock
    from app.repositories.watchlist_repository import WatchlistRepository
    from sqlalchemy import select

    stock_responses = []
    stock_count = 0

    if load_stocks:
        # Get stocks using repository
        watchlist_repo = WatchlistRepository(watchlist_service.session)
        watchlist_stocks = await watchlist_repo.get_watchlist_stocks(watchlist.id)
        stock_count = len(watchlist_stocks)

        # Load Stock data for each WatchlistStock
        for ws in watchlist_stocks:
            stock_query = select(Stock).where(Stock.code == ws.stock_code)
            stock_result = await watchlist_service.session.execute(stock_query)
            stock = stock_result.scalar_one_or_none()

            stock_responses.append(
                {
                    "stock_code": ws.stock_code,
                    "notes": ws.notes,
                    "added_at": ws.added_at,
                    "stock_name": stock.name if stock else None,
                    "current_price": None,
                    "change_percent": None,
                    "volume": None,
                }
            )

    return WatchlistResponse(
        id=watchlist.id,
        user_id=watchlist.user_id,
        name=watchlist.name,
        description=watchlist.description,
        stock_count=stock_count,
        created_at=watchlist.created_at,
        updated_at=watchlist.updated_at,
        stocks=stock_responses,
    )


# ============================================================================
# WATCHLIST ENDPOINTS
# ============================================================================


@router.get(
    "/watchlists",
    response_model=WatchlistListResponse,
    summary="List user watchlists",
    description="Get all watchlists for the current user with pagination",
)
async def list_watchlists(
    current_user: CurrentActiveUser,
    watchlist_service: Annotated[WatchlistService, Depends(get_watchlist_service)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
) -> WatchlistListResponse:
    """
    Get all watchlists for the current user

    Args:
        current_user: Current authenticated user
        watchlist_service: WatchlistService dependency
        page: Page number (starts from 1)
        limit: Number of watchlists per page

    Returns:
        WatchlistListResponse with pagination info

    Raises:
        401: Unauthorized
    """
    skip = (page - 1) * limit
    watchlists, total = await watchlist_service.get_user_watchlists(
        user_id=current_user.id, skip=skip, limit=limit, load_stocks=False
    )

    # Convert to summary format
    watchlist_summaries = [
        WatchlistSummary(
            id=w.id,
            name=w.name,
            description=w.description,
            stock_count=w.stock_count,
            last_stock_added=None,  # TODO: Add this to query
            created_at=w.created_at,
            updated_at=w.updated_at,
        )
        for w in watchlists
    ]

    return WatchlistListResponse(
        total=total,
        page=page,
        limit=limit,
        watchlists=watchlist_summaries,
    )


@router.post(
    "/watchlists",
    response_model=WatchlistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create watchlist",
    description="Create a new watchlist with optional initial stocks",
)
async def create_watchlist(
    current_user: CurrentActiveUser,
    watchlist_data: WatchlistCreate,
    watchlist_service: Annotated[WatchlistService, Depends(get_watchlist_service)],
) -> WatchlistResponse:
    """
    Create new watchlist

    Args:
        current_user: Current authenticated user
        watchlist_data: Watchlist creation data
        watchlist_service: WatchlistService dependency

    Returns:
        Created watchlist

    Raises:
        400: Watchlist limit reached or invalid stock codes
        401: Unauthorized
    """
    try:
        watchlist = await watchlist_service.create_watchlist(
            user_id=current_user.id, data=watchlist_data
        )

        return await build_watchlist_response(
            watchlist, watchlist_service, load_stocks=True
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/watchlists/{watchlist_id}",
    response_model=WatchlistResponse,
    summary="Get watchlist",
    description="Get watchlist by ID with all stocks",
)
async def get_watchlist(
    current_user: CurrentActiveUser,
    watchlist_id: UUID,
    watchlist_service: Annotated[WatchlistService, Depends(get_watchlist_service)],
) -> WatchlistResponse:
    """
    Get watchlist by ID

    Args:
        current_user: Current authenticated user
        watchlist_id: Watchlist UUID
        watchlist_service: WatchlistService dependency

    Returns:
        Watchlist with all stocks

    Raises:
        404: Watchlist not found or access denied
        401: Unauthorized
    """
    watchlist = await watchlist_service.get_watchlist_by_id(
        watchlist_id=watchlist_id, user_id=current_user.id, load_stocks=False
    )

    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found or access denied",
        )

    return await build_watchlist_response(watchlist, watchlist_service, load_stocks=True)


@router.put(
    "/watchlists/{watchlist_id}",
    response_model=WatchlistResponse,
    summary="Update watchlist",
    description="Update watchlist name, description, or stocks",
)
async def update_watchlist(
    current_user: CurrentActiveUser,
    watchlist_id: UUID,
    watchlist_data: WatchlistUpdate,
    watchlist_service: Annotated[WatchlistService, Depends(get_watchlist_service)],
) -> WatchlistResponse:
    """
    Update watchlist

    Args:
        current_user: Current authenticated user
        watchlist_id: Watchlist UUID
        watchlist_data: Update data
        watchlist_service: WatchlistService dependency

    Returns:
        Updated watchlist

    Raises:
        404: Watchlist not found or access denied
        400: Invalid stock codes
        401: Unauthorized
    """
    try:
        watchlist = await watchlist_service.update_watchlist(
            watchlist_id=watchlist_id, user_id=current_user.id, data=watchlist_data
        )

        return await build_watchlist_response(
            watchlist, watchlist_service, load_stocks=True
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/watchlists/{watchlist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete watchlist",
    description="Delete watchlist and all associated stocks",
)
async def delete_watchlist(
    current_user: CurrentActiveUser,
    watchlist_id: UUID,
    watchlist_service: Annotated[WatchlistService, Depends(get_watchlist_service)],
) -> None:
    """
    Delete watchlist

    Args:
        current_user: Current authenticated user
        watchlist_id: Watchlist UUID
        watchlist_service: WatchlistService dependency

    Raises:
        404: Watchlist not found or access denied
        401: Unauthorized
    """
    try:
        await watchlist_service.delete_watchlist(
            watchlist_id=watchlist_id, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


# ============================================================================
# ACTIVITY ENDPOINTS
# ============================================================================


@router.get(
    "/recent-activity",
    response_model=UserActivityListResponse,
    summary="Get recent activity",
    description="Get user's recent activities (screenings, watchlist changes, etc.)",
)
async def get_recent_activity(
    current_user: CurrentActiveUser,
    watchlist_service: Annotated[WatchlistService, Depends(get_watchlist_service)],
    limit: int = Query(10, ge=1, le=50, description="Number of activities"),
    activity_type: str | None = Query(None, description="Filter by activity type"),
) -> UserActivityListResponse:
    """
    Get recent user activities

    Args:
        current_user: Current authenticated user
        watchlist_service: WatchlistService dependency
        limit: Maximum number of activities
        activity_type: Optional filter by type

    Returns:
        List of recent activities

    Raises:
        401: Unauthorized
    """
    activities, total = await watchlist_service.get_recent_activities(
        user_id=current_user.id, limit=limit, activity_type=activity_type
    )

    return UserActivityListResponse(
        total=total,
        activities=activities,
    )


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================


@router.get(
    "/dashboard",
    response_model=DashboardSummary,
    summary="Get dashboard summary",
    description="Get user dashboard summary with stats and quota info",
)
async def get_dashboard_summary(
    current_user: CurrentActiveUser,
    watchlist_service: Annotated[WatchlistService, Depends(get_watchlist_service)],
) -> DashboardSummary:
    """
    Get dashboard summary

    Args:
        current_user: Current authenticated user
        watchlist_service: WatchlistService dependency

    Returns:
        Dashboard summary with statistics

    Raises:
        401: Unauthorized
    """
    summary = await watchlist_service.get_dashboard_summary(
        user_id=current_user.id, user_tier=current_user.subscription_tier
    )

    return summary
