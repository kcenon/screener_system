"""Portfolio endpoints for managing portfolios, holdings, and transactions"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser
from app.db.session import get_db
from app.schemas.portfolio import (
    HoldingCreate,
    HoldingListResponse,
    HoldingResponse,
    HoldingUpdate,
    PortfolioAllocation,
    PortfolioCreate,
    PortfolioListResponse,
    PortfolioPerformance,
    PortfolioResponse,
    PortfolioSummary,
    PortfolioUpdate,
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
)
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


def get_portfolio_service(db: AsyncSession = Depends(get_db)) -> PortfolioService:
    """Dependency to get portfolio service instance"""
    return PortfolioService(db)


def get_user_tier(current_user: CurrentUser) -> str:
    """Get user subscription tier"""
    # TODO: Implement subscription tier logic when subscription system is ready
    # For now, return 'free' for all users
    return getattr(current_user, "subscription_tier", "free")


# ============================================================================
# Portfolio CRUD Endpoints
# ============================================================================


@router.get("/", response_model=PortfolioListResponse, status_code=status.HTTP_200_OK)
async def list_portfolios(
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of items to return"),
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioListResponse:
    """
    List all portfolios for the current user

    **Permissions:** Requires authentication

    **Query Parameters:**
    - skip: Number of portfolios to skip (for pagination)
    - limit: Maximum number of portfolios to return (1-100)

    **Returns:**
    - List of portfolios with summary information
    - Total count for pagination
    """
    portfolios, total = await service.get_user_portfolios(
        user_id=current_user.id, skip=skip, limit=limit, load_holdings=False
    )

    # Convert to response schema
    items = []
    for portfolio in portfolios:
        items.append(
            PortfolioResponse(
                id=portfolio.id,
                user_id=portfolio.user_id,
                name=portfolio.name,
                description=portfolio.description,
                is_default=portfolio.is_default,
                holding_count=portfolio.holding_count,
                total_cost=portfolio.total_cost,
                created_at=portfolio.created_at,
                updated_at=portfolio.updated_at,
            )
        )

    return PortfolioListResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    data: PortfolioCreate,
    current_user: CurrentUser,
    user_tier: str = Depends(get_user_tier),
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioResponse:
    """
    Create a new portfolio

    **Permissions:** Requires authentication

    **Request Body:**
    - name: Portfolio name (required, 1-100 characters)
    - description: Optional description (max 500 characters)
    - is_default: Whether this is the default portfolio

    **Returns:**
    - Created portfolio

    **Errors:**
    - 400: Portfolio limit reached for user tier
    - 400: Portfolio name already exists
    """
    try:
        portfolio = await service.create_portfolio(
            user_id=current_user.id, user_tier=user_tier, data=data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return PortfolioResponse(
        id=portfolio.id,
        user_id=portfolio.user_id,
        name=portfolio.name,
        description=portfolio.description,
        is_default=portfolio.is_default,
        holding_count=portfolio.holding_count,
        total_cost=portfolio.total_cost,
        created_at=portfolio.created_at,
        updated_at=portfolio.updated_at,
    )


@router.get("/{portfolio_id}", response_model=PortfolioSummary, status_code=status.HTTP_200_OK)
async def get_portfolio(
    portfolio_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioSummary:
    """
    Get portfolio details with holdings and performance

    **Permissions:** Requires authentication, must own portfolio

    **Path Parameters:**
    - portfolio_id: Portfolio ID

    **Returns:**
    - Portfolio with holdings, performance metrics, and recent transactions

    **Errors:**
    - 404: Portfolio not found or not owned by user
    """
    portfolio = await service.get_portfolio_by_id(
        portfolio_id=portfolio_id, user_id=current_user.id, load_holdings=True
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found",
        )

    # Get holdings with current prices
    holdings = await service.get_portfolio_holdings(portfolio_id=portfolio_id)

    # Get performance metrics
    performance = await service.get_portfolio_performance(portfolio_id=portfolio_id)

    # Get allocation
    allocation = await service.get_portfolio_allocation(portfolio_id=portfolio_id)

    # Get recent transactions (last 10)
    recent_txns, _ = await service.get_portfolio_transactions(
        portfolio_id=portfolio_id, skip=0, limit=10
    )

    return PortfolioSummary(
        portfolio=PortfolioResponse(
            id=portfolio.id,
            user_id=portfolio.user_id,
            name=portfolio.name,
            description=portfolio.description,
            is_default=portfolio.is_default,
            holding_count=portfolio.holding_count,
            total_cost=portfolio.total_cost,
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at,
        ),
        holdings=holdings,
        performance=performance,
        allocation=allocation,
        recent_transactions=[
            TransactionResponse(
                id=txn.id,
                portfolio_id=txn.portfolio_id,
                stock_symbol=txn.stock_symbol,
                transaction_type=txn.transaction_type,
                shares=txn.shares,
                price=txn.price,
                commission=txn.commission,
                notes=txn.notes,
                transaction_value=txn.transaction_value,
                total_amount=txn.total_amount,
                transaction_date=txn.transaction_date,
                created_at=txn.created_at,
            )
            for txn in recent_txns
        ],
    )


@router.put("/{portfolio_id}", response_model=PortfolioResponse, status_code=status.HTTP_200_OK)
async def update_portfolio(
    portfolio_id: Annotated[int, Path(gt=0)],
    data: PortfolioUpdate,
    current_user: CurrentUser,
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioResponse:
    """
    Update portfolio information

    **Permissions:** Requires authentication, must own portfolio

    **Path Parameters:**
    - portfolio_id: Portfolio ID

    **Request Body:**
    - name: New portfolio name (optional)
    - description: New description (optional)
    - is_default: Whether this is the default portfolio (optional)

    **Returns:**
    - Updated portfolio

    **Errors:**
    - 404: Portfolio not found or not owned by user
    - 400: Portfolio name already exists
    """
    try:
        portfolio = await service.update_portfolio(
            portfolio_id=portfolio_id, user_id=current_user.id, data=data
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found",
        )

    return PortfolioResponse(
        id=portfolio.id,
        user_id=portfolio.user_id,
        name=portfolio.name,
        description=portfolio.description,
        is_default=portfolio.is_default,
        holding_count=portfolio.holding_count,
        total_cost=portfolio.total_cost,
        created_at=portfolio.created_at,
        updated_at=portfolio.updated_at,
    )


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    service: PortfolioService = Depends(get_portfolio_service),
) -> None:
    """
    Delete a portfolio

    **Permissions:** Requires authentication, must own portfolio

    **Path Parameters:**
    - portfolio_id: Portfolio ID

    **Note:** This will also delete all holdings and transactions in the portfolio

    **Errors:**
    - 404: Portfolio not found or not owned by user
    """
    success = await service.delete_portfolio(portfolio_id=portfolio_id, user_id=current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found",
        )


# ============================================================================
# Portfolio Performance & Allocation Endpoints
# ============================================================================


@router.get(
    "/{portfolio_id}/performance",
    response_model=PortfolioPerformance,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_performance(
    portfolio_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioPerformance:
    """
    Get portfolio performance metrics

    **Permissions:** Requires authentication, must own portfolio

    **Path Parameters:**
    - portfolio_id: Portfolio ID

    **Returns:**
    - Performance metrics including:
      - Total cost, value, gain/loss
      - Return percentage
      - Day change and percentage
      - Best and worst performing holdings

    **Errors:**
    - 404: Portfolio not found or not owned by user
    """
    # Verify ownership
    portfolio = await service.get_portfolio_by_id(
        portfolio_id=portfolio_id, user_id=current_user.id, load_holdings=False
    )
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found",
        )

    performance = await service.get_portfolio_performance(portfolio_id=portfolio_id)

    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance data not available",
        )

    return performance


@router.get(
    "/{portfolio_id}/allocation",
    response_model=PortfolioAllocation,
    status_code=status.HTTP_200_OK,
)
async def get_portfolio_allocation(
    portfolio_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioAllocation:
    """
    Get portfolio allocation breakdown

    **Permissions:** Requires authentication, must own portfolio

    **Path Parameters:**
    - portfolio_id: Portfolio ID

    **Returns:**
    - Allocation breakdown by:
      - Stock (symbol, value, percentage)
      - Sector (sector, value, percentage)
      - Market cap (large/mid/small cap distribution)

    **Errors:**
    - 404: Portfolio not found or not owned by user
    """
    # Verify ownership
    portfolio = await service.get_portfolio_by_id(
        portfolio_id=portfolio_id, user_id=current_user.id, load_holdings=False
    )
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found",
        )

    allocation = await service.get_portfolio_allocation(portfolio_id=portfolio_id)

    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allocation data not available",
        )

    return allocation


# ============================================================================
# Holdings Endpoints
# ============================================================================


@router.get(
    "/{portfolio_id}/holdings",
    response_model=HoldingListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_holdings(
    portfolio_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    service: PortfolioService = Depends(get_portfolio_service),
) -> HoldingListResponse:
    """
    List all holdings in a portfolio

    **Permissions:** Requires authentication, must own portfolio

    **Path Parameters:**
    - portfolio_id: Portfolio ID

    **Returns:**
    - List of holdings with current prices and performance
    - Total cost and value

    **Errors:**
    - 404: Portfolio not found or not owned by user
    """
    # Verify ownership
    portfolio = await service.get_portfolio_by_id(
        portfolio_id=portfolio_id, user_id=current_user.id, load_holdings=False
    )
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found",
        )

    holdings = await service.get_portfolio_holdings(portfolio_id=portfolio_id)

    total_cost = sum(h.total_cost for h in holdings)
    total_value = sum(h.current_value for h in holdings if h.current_value) if holdings else None
    total_gain = (total_value - total_cost) if total_value else None

    return HoldingListResponse(
        items=holdings,
        total=len(holdings),
        total_cost=total_cost,
        total_value=total_value,
        total_gain=total_gain,
    )


@router.post(
    "/{portfolio_id}/holdings",
    response_model=HoldingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_holding(
    portfolio_id: Annotated[int, Path(gt=0)],
    data: HoldingCreate,
    current_user: CurrentUser,
    user_tier: str = Depends(get_user_tier),
    service: PortfolioService = Depends(get_portfolio_service),
) -> HoldingResponse:
    """
    Add a holding to portfolio (manual entry)

    **Permissions:** Requires authentication, must own portfolio

    **Path Parameters:**
    - portfolio_id: Portfolio ID

    **Request Body:**
    - stock_symbol: Stock symbol (6-digit code)
    - shares: Number of shares
    - average_cost: Average cost per share
    - first_purchase_date: Optional purchase date

    **Returns:**
    - Created holding

    **Errors:**
    - 404: Portfolio not found or not owned by user
    - 400: Stock not found or holding limit reached
    """
    try:
        holding = await service.add_holding(
            portfolio_id=portfolio_id,
            user_id=current_user.id,
            user_tier=user_tier,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Get holding with current price
    holding_response = await service.get_holding_with_price(holding.id)

    return holding_response


@router.put(
    "/{portfolio_id}/holdings/{holding_id}",
    response_model=HoldingResponse,
    status_code=status.HTTP_200_OK,
)
async def update_holding(
    portfolio_id: Annotated[int, Path(gt=0)],
    holding_id: Annotated[int, Path(gt=0)],
    data: HoldingUpdate,
    current_user: CurrentUser,
    service: PortfolioService = Depends(get_portfolio_service),
) -> HoldingResponse:
    """
    Update a holding

    **Permissions:** Requires authentication, must own portfolio

    **Path Parameters:**
    - portfolio_id: Portfolio ID
    - holding_id: Holding ID

    **Request Body:**
    - shares: New number of shares (optional)
    - average_cost: New average cost (optional)

    **Returns:**
    - Updated holding

    **Errors:**
    - 404: Portfolio or holding not found or not owned by user
    """
    try:
        holding = await service.update_holding(
            holding_id=holding_id,
            portfolio_id=portfolio_id,
            user_id=current_user.id,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding {holding_id} not found",
        )

    # Get holding with current price
    holding_response = await service.get_holding_with_price(holding.id)

    return holding_response


@router.delete("/{portfolio_id}/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holding(
    portfolio_id: Annotated[int, Path(gt=0)],
    holding_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    service: PortfolioService = Depends(get_portfolio_service),
) -> None:
    """
    Delete a holding

    **Permissions:** Requires authentication, must own portfolio

    **Path Parameters:**
    - portfolio_id: Portfolio ID
    - holding_id: Holding ID

    **Errors:**
    - 404: Portfolio or holding not found or not owned by user
    """
    success = await service.delete_holding(
        holding_id=holding_id, portfolio_id=portfolio_id, user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding {holding_id} not found",
        )


# ============================================================================
# Transactions Endpoints
# ============================================================================


@router.get(
    "/{portfolio_id}/transactions",
    response_model=TransactionListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_transactions(
    portfolio_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: PortfolioService = Depends(get_portfolio_service),
) -> TransactionListResponse:
    """
    List transactions for a portfolio

    **Permissions:** Requires authentication, must own portfolio

    **Path Parameters:**
    - portfolio_id: Portfolio ID

    **Query Parameters:**
    - skip: Number of transactions to skip
    - limit: Maximum number of transactions to return

    **Returns:**
    - List of transactions ordered by date (newest first)

    **Errors:**
    - 404: Portfolio not found or not owned by user
    """
    # Verify ownership
    portfolio = await service.get_portfolio_by_id(
        portfolio_id=portfolio_id, user_id=current_user.id, load_holdings=False
    )
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found",
        )

    transactions, total = await service.get_portfolio_transactions(
        portfolio_id=portfolio_id, skip=skip, limit=limit
    )

    items = [
        TransactionResponse(
            id=txn.id,
            portfolio_id=txn.portfolio_id,
            stock_symbol=txn.stock_symbol,
            transaction_type=txn.transaction_type,
            shares=txn.shares,
            price=txn.price,
            commission=txn.commission,
            notes=txn.notes,
            transaction_value=txn.transaction_value,
            total_amount=txn.total_amount,
            transaction_date=txn.transaction_date,
            created_at=txn.created_at,
        )
        for txn in transactions
    ]

    return TransactionListResponse(items=items, total=total, skip=skip, limit=limit)


@router.post(
    "/{portfolio_id}/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_transaction(
    portfolio_id: Annotated[int, Path(gt=0)],
    data: TransactionCreate,
    current_user: CurrentUser,
    user_tier: str = Depends(get_user_tier),
    service: PortfolioService = Depends(get_portfolio_service),
) -> TransactionResponse:
    """
    Record a buy/sell transaction

    **Permissions:** Requires authentication, must own portfolio

    **Path Parameters:**
    - portfolio_id: Portfolio ID

    **Request Body:**
    - stock_symbol: Stock symbol (6-digit code)
    - transaction_type: BUY or SELL
    - shares: Number of shares
    - price: Price per share
    - commission: Optional commission (default: 0)
    - notes: Optional notes
    - transaction_date: Optional date (default: now)

    **Returns:**
    - Created transaction

    **Errors:**
    - 404: Portfolio not found or not owned by user
    - 400: Insufficient shares for SELL transaction
    - 400: Stock not found
    """
    try:
        transaction = await service.record_transaction(
            portfolio_id=portfolio_id,
            user_id=current_user.id,
            user_tier=user_tier,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return TransactionResponse(
        id=transaction.id,
        portfolio_id=transaction.portfolio_id,
        stock_symbol=transaction.stock_symbol,
        transaction_type=transaction.transaction_type,
        shares=transaction.shares,
        price=transaction.price,
        commission=transaction.commission,
        notes=transaction.notes,
        transaction_value=transaction.transaction_value,
        total_amount=transaction.total_amount,
        transaction_date=transaction.transaction_date,
        created_at=transaction.created_at,
    )


@router.delete(
    "/{portfolio_id}/transactions/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_transaction(
    portfolio_id: Annotated[int, Path(gt=0)],
    transaction_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    service: PortfolioService = Depends(get_portfolio_service),
) -> None:
    """
    Delete a transaction

    **Permissions:** Requires authentication, must own portfolio

    **Path Parameters:**
    - portfolio_id: Portfolio ID
    - transaction_id: Transaction ID

    **Warning:** Deleting a transaction will recalculate holdings.
    This may affect average cost and total shares.

    **Errors:**
    - 404: Portfolio or transaction not found or not owned by user
    """
    success = await service.delete_transaction(
        transaction_id=transaction_id, portfolio_id=portfolio_id, user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found",
        )
