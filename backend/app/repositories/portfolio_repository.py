"""Portfolio repository for database operations"""

from typing import Optional

from app.db.models import Holding, Portfolio, Transaction
from sqlalchemy import delete as sql_delete
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class PortfolioRepository:
    """Repository for Portfolio database operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def get_by_id(
        self, portfolio_id: int, user_id: int, load_holdings: bool = True
    ) -> Optional[Portfolio]:
        """
        Get portfolio by ID (only if owned by user)

        Args:
            portfolio_id: Portfolio ID
            user_id: User ID (for ownership check)
            load_holdings: Whether to load associated holdings

        Returns:
            Portfolio if found and owned by user, None otherwise
        """
        query = select(Portfolio).where(
            Portfolio.id == portfolio_id, Portfolio.user_id == user_id
        )

        if load_holdings:
            query = query.options(selectinload(Portfolio.holdings))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_portfolios(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        load_holdings: bool = False,
    ) -> list[Portfolio]:
        """
        Get all portfolios for a user

        Args:
            user_id: User ID
            skip: Number of portfolios to skip (pagination)
            limit: Maximum number of portfolios to return
            load_holdings: Whether to load associated holdings

        Returns:
            List of portfolios
        """
        query = (
            select(Portfolio)
            .where(Portfolio.user_id == user_id)
            .order_by(Portfolio.is_default.desc(), Portfolio.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        if load_holdings:
            query = query.options(selectinload(Portfolio.holdings))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_user_portfolios(self, user_id: int) -> int:
        """Count portfolios owned by user"""
        result = await self.session.execute(
            select(func.count(Portfolio.id)).where(Portfolio.user_id == user_id)
        )
        return result.scalar_one()

    async def get_default_portfolio(self, user_id: int) -> Optional[Portfolio]:
        """Get user's default portfolio"""
        query = select(Portfolio).where(
            Portfolio.user_id == user_id, Portfolio.is_default.is_(True)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, portfolio: Portfolio) -> Portfolio:
        """Create new portfolio"""
        self.session.add(portfolio)
        await self.session.flush()
        await self.session.refresh(portfolio)
        return portfolio

    async def update(self, portfolio: Portfolio) -> Portfolio:
        """Update existing portfolio"""
        await self.session.flush()
        await self.session.refresh(portfolio)
        return portfolio

    async def delete(self, portfolio: Portfolio) -> None:
        """Delete portfolio (cascades to holdings and transactions)"""
        await self.session.execute(
            sql_delete(Portfolio).where(Portfolio.id == portfolio.id)
        )
        await self.session.flush()

    async def get_by_name(self, user_id: int, name: str) -> Optional[Portfolio]:
        """Get portfolio by name (for duplicate check)"""
        query = select(Portfolio).where(
            Portfolio.user_id == user_id, Portfolio.name == name
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def clear_default_flag(
        self, user_id: int, exclude_id: Optional[int] = None
    ) -> None:
        """Clear is_default flag for all user portfolios except excluded one"""
        query = select(Portfolio).where(
            Portfolio.user_id == user_id, Portfolio.is_default.is_(True)
        )
        if exclude_id:
            query = query.where(Portfolio.id != exclude_id)

        result = await self.session.execute(query)
        portfolios = result.scalars().all()

        for portfolio in portfolios:
            portfolio.is_default = False

        await self.session.flush()


class HoldingRepository:
    """Repository for Holding database operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def get_by_id(self, holding_id: int) -> Optional[Holding]:
        """Get holding by ID"""
        result = await self.session.execute(
            select(Holding).where(Holding.id == holding_id)
        )
        return result.scalar_one_or_none()

    async def get_portfolio_holdings(
        self, portfolio_id: int, active_only: bool = True
    ) -> list[Holding]:
        """
        Get all holdings for a portfolio

        Args:
            portfolio_id: Portfolio ID
            active_only: If True, only return holdings with shares > 0

        Returns:
            List of holdings
        """
        query = select(Holding).where(Holding.portfolio_id == portfolio_id)

        if active_only:
            query = query.where(Holding.shares > 0)

        query = query.order_by(Holding.last_update_date.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_stock(
        self, portfolio_id: int, stock_symbol: str
    ) -> Optional[Holding]:
        """Get holding for specific stock in portfolio"""
        result = await self.session.execute(
            select(Holding).where(
                Holding.portfolio_id == portfolio_id,
                Holding.stock_symbol == stock_symbol,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, holding: Holding) -> Holding:
        """Create new holding"""
        self.session.add(holding)
        await self.session.flush()
        await self.session.refresh(holding)
        return holding

    async def update(self, holding: Holding) -> Holding:
        """Update existing holding"""
        await self.session.flush()
        await self.session.refresh(holding)
        return holding

    async def delete(self, holding: Holding) -> None:
        """Delete holding"""
        await self.session.delete(holding)
        await self.session.flush()


class TransactionRepository:
    """Repository for Transaction database operations"""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session"""
        self.session = session

    async def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID"""
        result = await self.session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def get_portfolio_transactions(
        self,
        portfolio_id: int,
        skip: int = 0,
        limit: int = 100,
        stock_symbol: Optional[str] = None,
    ) -> list[Transaction]:
        """
        Get transactions for a portfolio

        Args:
            portfolio_id: Portfolio ID
            skip: Number to skip (pagination)
            limit: Maximum results
            stock_symbol: Optional filter by stock symbol

        Returns:
            List of transactions
        """
        query = select(Transaction).where(Transaction.portfolio_id == portfolio_id)

        if stock_symbol:
            query = query.where(Transaction.stock_symbol == stock_symbol)

        query = (
            query.order_by(Transaction.transaction_date.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_portfolio_transactions(
        self, portfolio_id: int, stock_symbol: Optional[str] = None
    ) -> int:
        """Count transactions for portfolio"""
        query = select(func.count(Transaction.id)).where(
            Transaction.portfolio_id == portfolio_id
        )
        if stock_symbol:
            query = query.where(Transaction.stock_symbol == stock_symbol)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def create(self, transaction: Transaction) -> Transaction:
        """Create new transaction"""
        self.session.add(transaction)
        await self.session.flush()
        await self.session.refresh(transaction)
        return transaction

    async def delete(self, transaction: Transaction) -> None:
        """Delete transaction"""
        await self.session.delete(transaction)
        await self.session.flush()
