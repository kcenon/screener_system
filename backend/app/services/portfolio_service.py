"""Portfolio service for managing portfolios, holdings, and transactions"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Holding, Portfolio, Transaction
from app.repositories import HoldingRepository, PortfolioRepository, TransactionRepository
from app.repositories.stock_repository import StockRepository
from app.schemas.portfolio import (
    HoldingCreate,
    PortfolioCreate,
    PortfolioUpdate,
    TransactionCreate,
    TransactionType,
)


class PortfolioService:
    """Service for portfolio operations"""

    # Subscription tier limits
    MAX_PORTFOLIOS = {
        "free": 0,
        "premium": 3,
        "pro": 999,  # Unlimited
    }

    MAX_HOLDINGS_PER_PORTFOLIO = {
        "free": 0,
        "premium": 100,
        "pro": 9999,  # Unlimited
    }

    def __init__(self, session: AsyncSession):
        """Initialize service with database session"""
        self.session = session
        self.portfolio_repo = PortfolioRepository(session)
        self.holding_repo = HoldingRepository(session)
        self.transaction_repo = TransactionRepository(session)
        self.stock_repo = StockRepository(session)

    async def get_user_portfolios(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        load_holdings: bool = False,
    ) -> tuple[list[Portfolio], int]:
        """
        Get user portfolios with pagination

        Args:
            user_id: User ID
            skip: Number to skip
            limit: Maximum results
            load_holdings: Whether to load holdings

        Returns:
            Tuple of (portfolios, total_count)
        """
        portfolios = await self.portfolio_repo.get_user_portfolios(
            user_id=user_id, skip=skip, limit=limit, load_holdings=load_holdings
        )
        total = await self.portfolio_repo.count_user_portfolios(user_id)
        return portfolios, total

    async def get_portfolio_by_id(
        self, portfolio_id: int, user_id: int, load_holdings: bool = True
    ) -> Optional[Portfolio]:
        """Get portfolio by ID (ownership check)"""
        return await self.portfolio_repo.get_by_id(
            portfolio_id=portfolio_id, user_id=user_id, load_holdings=load_holdings
        )

    async def create_portfolio(
        self, user_id: int, user_tier: str, data: PortfolioCreate
    ) -> Portfolio:
        """
        Create new portfolio

        Args:
            user_id: User ID
            user_tier: User subscription tier (free, premium, pro)
            data: Portfolio creation data

        Returns:
            Created portfolio

        Raises:
            ValueError: If portfolio limit reached or name already exists
        """
        # Check portfolio limit
        count = await self.portfolio_repo.count_user_portfolios(user_id)
        max_portfolios = self.MAX_PORTFOLIOS.get(user_tier, 0)
        if count >= max_portfolios:
            raise ValueError(
                f"Portfolio limit reached for {user_tier} tier (max {max_portfolios})"
            )

        # Check for duplicate name
        existing = await self.portfolio_repo.get_by_name(user_id, data.name)
        if existing:
            raise ValueError(f"Portfolio with name '{data.name}' already exists")

        # If setting as default, clear other defaults
        if data.is_default:
            await self.portfolio_repo.clear_default_flag(user_id)

        # Create portfolio
        portfolio = Portfolio(
            user_id=user_id,
            name=data.name,
            description=data.description,
            is_default=data.is_default,
        )

        return await self.portfolio_repo.create(portfolio)

    async def update_portfolio(
        self, portfolio_id: int, user_id: int, data: PortfolioUpdate
    ) -> Portfolio:
        """
        Update portfolio

        Args:
            portfolio_id: Portfolio ID
            user_id: User ID (for ownership check)
            data: Update data

        Returns:
            Updated portfolio

        Raises:
            ValueError: If portfolio not found or name already exists
        """
        portfolio = await self.get_portfolio_by_id(portfolio_id, user_id, load_holdings=False)
        if not portfolio:
            raise ValueError("Portfolio not found")

        # Check for duplicate name if changing name
        if data.name and data.name != portfolio.name:
            existing = await self.portfolio_repo.get_by_name(user_id, data.name)
            if existing:
                raise ValueError(f"Portfolio with name '{data.name}' already exists")
            portfolio.name = data.name

        # Update description
        if data.description is not None:
            portfolio.description = data.description

        # Handle is_default flag
        if data.is_default is not None and data.is_default != portfolio.is_default:
            if data.is_default:
                # Clear other defaults before setting this one
                await self.portfolio_repo.clear_default_flag(user_id, exclude_id=portfolio_id)
            portfolio.is_default = data.is_default

        return await self.portfolio_repo.update(portfolio)

    async def delete_portfolio(self, portfolio_id: int, user_id: int) -> None:
        """
        Delete portfolio (cascades to holdings and transactions)

        Args:
            portfolio_id: Portfolio ID
            user_id: User ID (for ownership check)

        Raises:
            ValueError: If portfolio not found
        """
        portfolio = await self.get_portfolio_by_id(portfolio_id, user_id, load_holdings=False)
        if not portfolio:
            raise ValueError("Portfolio not found")

        await self.portfolio_repo.delete(portfolio)

    async def add_manual_holding(
        self, portfolio_id: int, user_id: int, user_tier: str, data: HoldingCreate
    ) -> Holding:
        """
        Add holding manually (without transaction record)

        Args:
            portfolio_id: Portfolio ID
            user_id: User ID (for ownership check)
            user_tier: User subscription tier
            data: Holding data

        Returns:
            Created holding

        Raises:
            ValueError: If portfolio not found, stock invalid, or limits exceeded
        """
        # Check portfolio ownership
        portfolio = await self.get_portfolio_by_id(portfolio_id, user_id, load_holdings=True)
        if not portfolio:
            raise ValueError("Portfolio not found")

        # Check holding limit
        max_holdings = self.MAX_HOLDINGS_PER_PORTFOLIO.get(user_tier, 0)
        if portfolio.holding_count >= max_holdings:
            raise ValueError(
                f"Holding limit reached for {user_tier} tier (max {max_holdings})"
            )

        # Validate stock exists
        stock = await self.stock_repo.get_by_code(data.stock_symbol)
        if not stock:
            raise ValueError(f"Stock {data.stock_symbol} does not exist")

        # Check if holding already exists
        existing = await self.holding_repo.get_by_stock(portfolio_id, data.stock_symbol)
        if existing:
            raise ValueError(f"Holding for {data.stock_symbol} already exists in this portfolio")

        # Create holding
        holding = Holding(
            portfolio_id=portfolio_id,
            stock_symbol=data.stock_symbol,
            shares=data.shares,
            average_cost=data.average_cost,
            first_purchase_date=data.first_purchase_date or datetime.now().date(),
            last_update_date=datetime.now(),
        )

        return await self.holding_repo.create(holding)

    async def remove_holding(self, holding_id: int, user_id: int) -> None:
        """
        Remove holding from portfolio

        Args:
            holding_id: Holding ID
            user_id: User ID (for ownership check)

        Raises:
            ValueError: If holding not found or not owned by user
        """
        holding = await self.holding_repo.get_by_id(holding_id)
        if not holding:
            raise ValueError("Holding not found")

        # Check ownership through portfolio
        portfolio = await self.portfolio_repo.get_by_id(holding.portfolio_id, user_id, load_holdings=False)
        if not portfolio:
            raise ValueError("Holding not found or not owned by user")

        await self.holding_repo.delete(holding)

    async def get_portfolio_holdings(
        self, portfolio_id: int, user_id: int, active_only: bool = True
    ) -> list[Holding]:
        """
        Get all holdings for a portfolio

        Args:
            portfolio_id: Portfolio ID
            user_id: User ID (for ownership check)
            active_only: If True, only return holdings with shares > 0

        Returns:
            List of holdings

        Raises:
            ValueError: If portfolio not found
        """
        # Check ownership
        portfolio = await self.get_portfolio_by_id(portfolio_id, user_id, load_holdings=False)
        if not portfolio:
            raise ValueError("Portfolio not found")

        return await self.holding_repo.get_portfolio_holdings(portfolio_id, active_only)


class TransactionService:
    """Service for transaction operations"""

    def __init__(self, session: AsyncSession):
        """Initialize service with database session"""
        self.session = session
        self.portfolio_repo = PortfolioRepository(session)
        self.holding_repo = HoldingRepository(session)
        self.transaction_repo = TransactionRepository(session)
        self.stock_repo = StockRepository(session)

    async def record_transaction(
        self, portfolio_id: int, user_id: int, data: TransactionCreate
    ) -> tuple[Transaction, Holding]:
        """
        Record a buy or sell transaction and update holdings

        Args:
            portfolio_id: Portfolio ID
            user_id: User ID (for ownership check)
            data: Transaction data

        Returns:
            Tuple of (created transaction, updated/created holding)

        Raises:
            ValueError: If validation fails or insufficient shares for sell
        """
        # Check portfolio ownership
        portfolio = await self.portfolio_repo.get_by_id(
            portfolio_id, user_id, load_holdings=False
        )
        if not portfolio:
            raise ValueError("Portfolio not found")

        # Validate stock exists
        stock = await self.stock_repo.get_by_code(data.stock_symbol)
        if not stock:
            raise ValueError(f"Stock {data.stock_symbol} does not exist")

        # Get or create holding
        holding = await self.holding_repo.get_by_stock(portfolio_id, data.stock_symbol)

        # Process transaction based on type
        if data.transaction_type == TransactionType.BUY:
            holding = await self._process_buy(portfolio_id, holding, data)
        else:  # SELL
            holding = await self._process_sell(holding, data)

        # Create transaction record
        transaction = Transaction(
            portfolio_id=portfolio_id,
            stock_symbol=data.stock_symbol,
            transaction_type=data.transaction_type.value,
            shares=data.shares,
            price=data.price,
            commission=data.commission,
            transaction_date=data.transaction_date or datetime.now(),
            notes=data.notes,
        )
        transaction = await self.transaction_repo.create(transaction)

        await self.session.commit()

        return transaction, holding

    async def _process_buy(
        self, portfolio_id: int, holding: Optional[Holding], data: TransactionCreate
    ) -> Holding:
        """Process buy transaction"""
        if holding is None:
            # Create new holding
            holding = Holding(
                portfolio_id=portfolio_id,
                stock_symbol=data.stock_symbol,
                shares=data.shares,
                average_cost=data.price,
                first_purchase_date=data.transaction_date.date() if data.transaction_date else datetime.now().date(),
                last_update_date=datetime.now(),
            )
            holding = await self.holding_repo.create(holding)
        else:
            # Update existing holding with weighted average cost
            holding.update_average_cost(data.shares, data.price)
            holding.last_update_date = datetime.now()
            holding = await self.holding_repo.update(holding)

        return holding

    async def _process_sell(
        self, holding: Optional[Holding], data: TransactionCreate
    ) -> Holding:
        """Process sell transaction"""
        if holding is None:
            raise ValueError(f"No holdings found for {data.stock_symbol}")

        if Decimal(str(holding.shares)) < data.shares:
            raise ValueError(
                f"Insufficient shares: have {holding.shares}, trying to sell {data.shares}"
            )

        # Reduce shares
        holding.reduce_shares(data.shares)
        holding.last_update_date = datetime.now()
        holding = await self.holding_repo.update(holding)

        return holding

    async def get_portfolio_transactions(
        self,
        portfolio_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        stock_symbol: Optional[str] = None,
    ) -> tuple[list[Transaction], int]:
        """
        Get transactions for a portfolio

        Args:
            portfolio_id: Portfolio ID
            user_id: User ID (for ownership check)
            skip: Number to skip (pagination)
            limit: Maximum results
            stock_symbol: Optional filter by stock

        Returns:
            Tuple of (transactions, total_count)

        Raises:
            ValueError: If portfolio not found
        """
        # Check ownership
        portfolio = await self.portfolio_repo.get_by_id(
            portfolio_id, user_id, load_holdings=False
        )
        if not portfolio:
            raise ValueError("Portfolio not found")

        transactions = await self.transaction_repo.get_portfolio_transactions(
            portfolio_id, skip, limit, stock_symbol
        )
        total = await self.transaction_repo.count_portfolio_transactions(
            portfolio_id, stock_symbol
        )

        return transactions, total

    async def delete_transaction(
        self, transaction_id: int, user_id: int
    ) -> None:
        """
        Delete transaction (WARNING: Does not reverse holding changes)

        Args:
            transaction_id: Transaction ID
            user_id: User ID (for ownership check)

        Raises:
            ValueError: If transaction not found

        Note:
            This only deletes the transaction record. It does NOT reverse the
            changes made to holdings. Manual adjustment of holdings required.
        """
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")

        # Check ownership through portfolio
        portfolio = await self.portfolio_repo.get_by_id(
            transaction.portfolio_id, user_id, load_holdings=False
        )
        if not portfolio:
            raise ValueError("Transaction not found or not owned by user")

        await self.transaction_repo.delete(transaction)
        await self.session.commit()
