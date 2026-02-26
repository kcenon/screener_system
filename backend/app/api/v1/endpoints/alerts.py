"""Alert management endpoints for creating, updating, and managing stock alerts.

This module provides REST API endpoints for managing user-defined stock alerts
including price alerts, volume spikes, and percentage change alerts.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.models import Alert, User
from app.db.session import get_db
from app.schemas.alert import (AlertCreate, AlertListResponse, AlertResponse,
                               AlertToggleResponse, AlertUpdate)

# from sqlalchemy.orm import joinedload  # Unused
# from sqlalchemy.orm import Session  # Unused


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["alerts"])


# ============================================================================
# Alert Management Endpoints
# ============================================================================


@router.post(
    "",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new alert",
    description="""
    Create a new stock alert for the authenticated user.

    **Alert Types:**
    - `PRICE_ABOVE`: Trigger when price rises above threshold
    - `PRICE_BELOW`: Trigger when price falls below threshold
    - `VOLUME_SPIKE`: Trigger when volume exceeds X times average volume
    - `CHANGE_PERCENT_ABOVE`: Trigger when day change exceeds +X%
    - `CHANGE_PERCENT_BELOW`: Trigger when day change falls below -X%

    **Rate Limits:**
    - Maximum 50 alerts per user
    - Free tier: 10 alerts
    - Premium tier: 20 alerts
    - Pro tier: Unlimited

    **Examples:**
    ```json
    {
      "stock_code": "005930",
      "alert_type": "PRICE_ABOVE",
      "condition_value": 70000,
      "is_recurring": false
    }
    ```
    """,
)
async def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AlertResponse:
    """Create a new alert for the current user."""
    # Check alert limit for user tier
    result = await db.execute(
        select(func.count(Alert.id)).where(
            Alert.user_id == current_user.id,
        )
    )
    alert_count = result.scalar_one()

    # TODO: Get tier from user subscription
    max_alerts = 50  # Default limit

    if alert_count >= max_alerts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum alert limit reached ({max_alerts} alerts)",
        )

    # Verify stock exists
    from app.db.models import Stock

    result = await db.execute(select(Stock).where(Stock.code == alert_data.stock_code))
    stock = result.scalar_one_or_none()

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock {alert_data.stock_code} not found",
        )

    # Create alert
    alert = Alert(
        user_id=current_user.id,
        stock_code=alert_data.stock_code,
        alert_type=alert_data.alert_type,
        condition_value=alert_data.condition_value,
        is_recurring=alert_data.is_recurring,
        is_active=True,
    )

    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    logger.info(
        f"Alert {alert.id} created for user {current_user.id}: "
        f"{alert.alert_type} on {alert.stock_code}"
    )

    return AlertResponse.model_validate(alert)


@router.get(
    "",
    response_model=AlertListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user alerts",
    description="""
    Get paginated list of alerts for the authenticated user.

    **Filters:**
    - `stock_code`: Filter by specific stock
    - `alert_type`: Filter by alert type
    - `is_active`: Filter by active status

    **Sorting:**
    - `created_at`: Sort by creation date (default)
    - `triggered_at`: Sort by last trigger date

    **Pagination:**
    - Default page size: 20
    - Maximum page size: 100
    """,
)
async def list_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    stock_code: Optional[str] = Query(None, description="Filter by stock code"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
) -> AlertListResponse:
    """Get paginated list of user alerts."""
    # Build query
    query = select(Alert).where(Alert.user_id == current_user.id)

    # Apply filters
    if stock_code:
        query = query.where(Alert.stock_code == stock_code)
    if alert_type:
        query = query.where(Alert.alert_type == alert_type)
    if is_active is not None:
        query = query.where(Alert.is_active == is_active)

    # Get total count
    count_query = select(func.count(Alert.id)).where(Alert.user_id == current_user.id)
    if stock_code:
        count_query = count_query.where(Alert.stock_code == stock_code)
    if alert_type:
        count_query = count_query.where(Alert.alert_type == alert_type)
    if is_active is not None:
        count_query = count_query.where(Alert.is_active == is_active)

    result = await db.execute(count_query)
    total = result.scalar_one()

    # Get paginated results
    query = query.order_by(Alert.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    alerts = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return AlertListResponse(
        items=[AlertResponse.model_validate(alert) for alert in alerts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Get alert details",
    description="Get detailed information about a specific alert.",
)
async def get_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AlertResponse:
    """Get alert details by ID."""
    result = await db.execute(
        select(Alert).where(
            Alert.id == alert_id,
            Alert.user_id == current_user.id,
        )
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )

    return AlertResponse.model_validate(alert)


@router.put(
    "/{alert_id}",
    response_model=AlertResponse,
    status_code=status.HTTP_200_OK,
    summary="Update alert",
    description="""
    Update an existing alert's configuration.

    **Updatable Fields:**
    - `alert_type`: Change alert type
    - `condition_value`: Change threshold value
    - `is_recurring`: Change recurring setting

    **Note:** Cannot update stock_code. Create a new alert instead.
    """,
)
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AlertResponse:
    """Update alert configuration."""
    result = await db.execute(
        select(Alert).where(
            Alert.id == alert_id,
            Alert.user_id == current_user.id,
        )
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )

    # Update fields
    if alert_data.alert_type is not None:
        alert.alert_type = alert_data.alert_type
    if alert_data.condition_value is not None:
        alert.condition_value = alert_data.condition_value
    if alert_data.is_recurring is not None:
        alert.is_recurring = alert_data.is_recurring

    # Reset triggered state if configuration changed
    if alert_data.alert_type or alert_data.condition_value:
        alert.reset()

    await db.commit()
    await db.refresh(alert)

    logger.info(f"Alert {alert.id} updated for user {current_user.id}")

    return AlertResponse.model_validate(alert)


@router.delete(
    "/{alert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete alert",
    description="Delete an alert. This action cannot be undone.",
)
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an alert."""
    result = await db.execute(
        select(Alert).where(
            Alert.id == alert_id,
            Alert.user_id == current_user.id,
        )
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )

    await db.delete(alert)
    await db.commit()

    logger.info(f"Alert {alert.id} deleted for user {current_user.id}")


@router.post(
    "/{alert_id}/toggle",
    response_model=AlertToggleResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle alert active status",
    description="""
    Toggle alert between active and inactive states.

    **Use Cases:**
    - Temporarily disable alert without deleting
    - Re-enable previously disabled alert
    - Pause alerts during market volatility
    """,
)
async def toggle_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AlertToggleResponse:
    """Toggle alert active status."""
    result = await db.execute(
        select(Alert).where(
            Alert.id == alert_id,
            Alert.user_id == current_user.id,
        )
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )

    # Toggle active status
    alert.toggle_active()

    await db.commit()

    status_text = "activated" if alert.is_active else "deactivated"
    logger.info(f"Alert {alert.id} {status_text} for user {current_user.id}")

    return AlertToggleResponse(
        id=alert.id,
        is_active=alert.is_active,
        message=f"Alert {status_text} successfully",
    )
