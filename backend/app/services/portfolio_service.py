"""Portfolio service for managing portfolios, holdings, and transactions"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Holding, Portfolio, Transaction
from app.repositories import (
    HoldingRepository,
    PortfolioRepository,
    TransactionRepository,
)
from app.repositories.stock_repository import StockRepository
from app.schemas.portfolio import (
    HoldingCreate,
    HoldingUpdate,
    PortfolioCreate,
    PortfolioUpdate,
    TransactionCreate,
    TransactionType,
)

# Market cap thresholds (KRW)
_LARGE_CAP_THRESHOLD = 1_000_000_000_000  # 1 trillion KRW
_MID_CAP_THRESHOLD = 100_000_000_000  # 100 billion KRW


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
        portfolio = await self.get_portfolio_by_id(
            portfolio_id, user_id, load_holdings=False
        )
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
                await self.portfolio_repo.clear_default_flag(
                    user_id, exclude_id=portfolio_id
                )
            portfolio.is_default = data.is_default

        return await self.portfolio_repo.update(portfolio)

    async def delete_portfolio(self, portfolio_id: int, user_id: int) -> bool:
        """
        Delete portfolio (cascades to holdings and transactions)

        Args:
            portfolio_id: Portfolio ID
            user_id: User ID (for ownership check)

        Returns:
            True if deleted, False if not found
        """
        portfolio = await self.get_portfolio_by_id(
            portfolio_id, user_id, load_holdings=False
        )
        if not portfolio:
            return False

        await self.portfolio_repo.delete(portfolio)
        return True

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
        portfolio = await self.get_portfolio_by_id(
            portfolio_id, user_id, load_holdings=True
        )
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
            raise ValueError(
                f"Holding for {data.stock_symbol} already exists in this portfolio"
            )

        # Create holding
        holding = Holding(
            portfolio_id=portfolio_id,
            stock_code=data.stock_symbol,
            shares=int(data.shares),
            average_price=float(data.average_cost),
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
        portfolio = await self.portfolio_repo.get_by_id(
            holding.portfolio_id, user_id, load_holdings=False
        )
        if not portfolio:
            raise ValueError("Holding not found or not owned by user")

        await self.holding_repo.delete(holding)

    async def get_portfolio_holdings(
        self, portfolio_id: int, user_id: Optional[int] = None, active_only: bool = True
    ) -> list[Holding]:
        """
        Get all holdings for a portfolio

        Args:
            portfolio_id: Portfolio ID
            user_id: User ID (for ownership check, optional)
            active_only: If True, only return holdings with shares > 0

        Returns:
            List of holdings

        Raises:
            ValueError: If portfolio not found
        """
        # Check ownership if user_id provided
        if user_id:
            portfolio = await self.get_portfolio_by_id(
                portfolio_id, user_id, load_holdings=False
            )
            if not portfolio:
                raise ValueError("Portfolio not found")

        holdings = await self.holding_repo.get_portfolio_holdings(
            portfolio_id, active_only
        )
        return holdings

    async def add_holding(
        self, portfolio_id: int, user_id: int, user_tier: str, data: HoldingCreate
    ) -> Holding:
        """Alias for add_manual_holding for API consistency"""
        return await self.add_manual_holding(portfolio_id, user_id, user_tier, data)

    async def update_holding(
        self, holding_id: int, portfolio_id: int, user_id: int, data: HoldingUpdate
    ) -> Optional[Holding]:
        """
        Update a holding

        Args:
            holding_id: Holding ID
            portfolio_id: Portfolio ID
            user_id: User ID (for ownership check)
            data: Update data

        Returns:
            Updated holding or None if not found
        """
        holding = await self.holding_repo.get_by_id(holding_id)
        if not holding or holding.portfolio_id != portfolio_id:
            return None

        # Check ownership
        portfolio = await self.get_portfolio_by_id(
            portfolio_id, user_id, load_holdings=False
        )
        if not portfolio:
            return None

        # Update fields
        if data.shares is not None:
            holding.shares = int(data.shares)
        if data.average_cost is not None:
            holding.average_price = float(data.average_cost)

        return await self.holding_repo.update(holding)

    async def delete_holding(
        self, holding_id: int, portfolio_id: int, user_id: int
    ) -> bool:
        """
        Delete a holding

        Args:
            holding_id: Holding ID
            portfolio_id: Portfolio ID
            user_id: User ID (for ownership check)

        Returns:
            True if deleted, False if not found
        """
        holding = await self.holding_repo.get_by_id(holding_id)
        if not holding or holding.portfolio_id != portfolio_id:
            return False

        # Check ownership
        portfolio = await self.get_portfolio_by_id(
            portfolio_id, user_id, load_holdings=False
        )
        if not portfolio:
            return False

        await self.holding_repo.delete(holding)
        return True

    async def get_holding_with_price(self, holding_id: int):
        """
        Get holding with current price

        Args:
            holding_id: Holding ID

        Returns:
            HoldingResponse with current price
        """
        from app.schemas.portfolio import HoldingResponse

        holding = await self.holding_repo.get_by_id(holding_id)
        if not holding:
            return None

        stock = await self.stock_repo.get_by_code(holding.stock_code)
        latest_price = await self.stock_repo.get_latest_price(holding.stock_code)
        current_price = (
            Decimal(str(latest_price.close_price)) if latest_price else None
        )

        cost = holding.total_cost
        current_value = (
            Decimal(str(holding.shares)) * current_price if current_price else None
        )
        unrealized_gain = (current_value - cost) if current_value is not None else None
        return_percent = (
            (unrealized_gain / cost * 100)
            if unrealized_gain is not None and cost > 0
            else None
        )

        return HoldingResponse(
            id=holding.id,
            portfolio_id=holding.portfolio_id,
            stock_symbol=holding.stock_code,
            stock_name=stock.name if stock else None,
            sector=stock.sector if stock else None,
            shares=Decimal(str(holding.shares)),
            average_cost=Decimal(str(holding.average_price)),
            current_price=current_price,
            total_cost=cost,
            current_value=current_value,
            unrealized_gain=unrealized_gain,
            return_percent=return_percent,
            first_purchase_date=None,
            last_update_date=holding.updated_at,
            created_at=holding.created_at,
            updated_at=holding.updated_at,
        )

    async def get_portfolio_performance(self, portfolio_id: int):
        """
        Get portfolio performance metrics

        Args:
            portfolio_id: Portfolio ID

        Returns:
            PortfolioPerformance or None
        """
        from app.schemas.portfolio import PortfolioPerformance

        holdings = await self.holding_repo.get_portfolio_holdings(
            portfolio_id, active_only=True
        )
        if not holdings:
            return None

        total_cost = Decimal("0")
        total_value = Decimal("0")
        day_change = Decimal("0")
        prev_total_value = Decimal("0")

        best_performer = None
        worst_performer = None
        best_return = Decimal("-999999")
        worst_return = Decimal("999999")

        for holding in holdings:
            stock = await self.stock_repo.get_by_code(holding.stock_code)
            prices = await self.stock_repo.get_price_history(
                holding.stock_code, limit=2
            )
            if not stock or not prices:
                continue

            current_price = Decimal(str(prices[0].close_price))
            cost = holding.total_cost
            value = Decimal(str(holding.shares)) * current_price
            return_pct = ((value - cost) / cost * 100) if cost > 0 else Decimal("0")

            total_cost += cost
            total_value += value

            # Day change: compare latest close vs previous close
            if len(prices) >= 2:
                prev_price = Decimal(str(prices[1].close_price))
                holding_shares = Decimal(str(holding.shares))
                day_change += (current_price - prev_price) * holding_shares
                prev_total_value += prev_price * holding_shares

            if return_pct > best_return:
                best_return = return_pct
                best_performer = {
                    "symbol": holding.stock_code,
                    "name": stock.name,
                    "return_percent": float(return_pct),
                }

            if return_pct < worst_return:
                worst_return = return_pct
                worst_performer = {
                    "symbol": holding.stock_code,
                    "name": stock.name,
                    "return_percent": float(return_pct),
                }

        if total_cost == 0:
            return None

        unrealized_gain = total_value - total_cost
        return_percent = unrealized_gain / total_cost * 100
        day_change_percent = (
            day_change / prev_total_value * 100
            if prev_total_value > 0
            else Decimal("0")
        )

        realized_gain = await self._calculate_realized_gain(portfolio_id)

        return PortfolioPerformance(
            portfolio_id=portfolio_id,
            total_cost=total_cost,
            total_value=total_value,
            unrealized_gain=unrealized_gain,
            return_percent=return_percent,
            day_change=day_change,
            day_change_percent=day_change_percent,
            realized_gain=realized_gain,
            best_performer=best_performer,
            worst_performer=worst_performer,
        )

    async def _calculate_realized_gain(self, portfolio_id: int) -> Decimal:
        """
        Calculate realized gain using the average cost method.

        Processes all BUY/SELL transactions chronologically.
        For each SELL: realized_gain += (sell_price - avg_cost) * qty - commission
        """
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.portfolio_id == portfolio_id)
            .order_by(asc(Transaction.transaction_date))
        )
        transactions = result.scalars().all()

        avg_costs: dict[str, Decimal] = {}
        qty_held: dict[str, Decimal] = {}
        realized_gain = Decimal("0")

        for tx in transactions:
            code = tx.stock_code
            qty = Decimal(str(tx.quantity))
            price = Decimal(str(tx.price))
            commission = Decimal(str(tx.commission or 0))

            if tx.transaction_type == "BUY":
                current_qty = qty_held.get(code, Decimal("0"))
                current_cost = avg_costs.get(code, Decimal("0"))
                new_qty = current_qty + qty
                avg_costs[code] = (current_qty * current_cost + qty * price) / new_qty
                qty_held[code] = new_qty
            elif tx.transaction_type == "SELL":
                avg_cost = avg_costs.get(code, price)
                realized_gain += (price - avg_cost) * qty - commission
                qty_held[code] = max(
                    Decimal("0"), qty_held.get(code, qty) - qty
                )

        return realized_gain

    async def get_portfolio_allocation(self, portfolio_id: int):
        """
        Get portfolio allocation breakdown

        Args:
            portfolio_id: Portfolio ID

        Returns:
            PortfolioAllocation or None
        """
        from collections import defaultdict

        from app.schemas.portfolio import PortfolioAllocation

        holdings = await self.holding_repo.get_portfolio_holdings(
            portfolio_id, active_only=True
        )
        if not holdings:
            return None

        total_value = Decimal("0")
        by_stock = []
        by_sector: dict[str, Decimal] = defaultdict(Decimal)
        large_cap_value = Decimal("0")
        mid_cap_value = Decimal("0")
        small_cap_value = Decimal("0")

        for holding in holdings:
            stock = await self.stock_repo.get_by_code(holding.stock_code)
            latest_price = await self.stock_repo.get_latest_price(holding.stock_code)
            if not stock or not latest_price:
                continue

            current_price = latest_price.close_price
            value = Decimal(str(holding.shares)) * Decimal(str(current_price))
            total_value += value

            by_stock.append(
                {
                    "symbol": holding.stock_code,
                    "name": stock.name,
                    "value": float(value),
                    "percent": 0,  # Will calculate after total
                }
            )

            sector = stock.sector or "Unknown"
            by_sector[sector] += value

            # Market cap classification
            market_cap = stock.get_market_cap(current_price)
            if market_cap is not None and market_cap >= _LARGE_CAP_THRESHOLD:
                large_cap_value += value
            elif market_cap is not None and market_cap >= _MID_CAP_THRESHOLD:
                mid_cap_value += value
            else:
                small_cap_value += value

        if total_value > 0:
            for item in by_stock:
                item["percent"] = float(
                    Decimal(str(item["value"])) / total_value * 100
                )

        by_sector_list = [
            {
                "sector": sector,
                "value": float(value),
                "percent": float(value / total_value * 100) if total_value > 0 else 0,
            }
            for sector, value in by_sector.items()
        ]

        by_market_cap = {
            "large": float(large_cap_value / total_value * 100)
            if total_value > 0
            else 0,
            "mid": float(mid_cap_value / total_value * 100)
            if total_value > 0
            else 0,
            "small": float(small_cap_value / total_value * 100)
            if total_value > 0
            else 0,
        }

        return PortfolioAllocation(
            portfolio_id=portfolio_id,
            by_stock=by_stock,
            by_sector=by_sector_list,
            by_market_cap=by_market_cap,
        )

    async def get_portfolio_transactions(
        self, portfolio_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[Transaction], int]:
        """
        Get portfolio transactions (wrapper for consistency)

        Args:
            portfolio_id: Portfolio ID
            skip: Number to skip
            limit: Maximum results

        Returns:
            Tuple of (transactions, total_count)
        """
        transactions = await self.transaction_repo.get_portfolio_transactions(
            portfolio_id, skip, limit, stock_symbol=None
        )
        total = await self.transaction_repo.count_portfolio_transactions(
            portfolio_id, stock_symbol=None
        )
        return transactions, total

    async def record_transaction(
        self, portfolio_id: int, user_id: int, user_tier: str, data: TransactionCreate
    ) -> Transaction:
        """
        Record a transaction (wrapper using TransactionService)

        Args:
            portfolio_id: Portfolio ID
            user_id: User ID
            user_tier: User tier (for limits)
            data: Transaction data

        Returns:
            Created transaction
        """
        # Check portfolio ownership
        portfolio = await self.get_portfolio_by_id(
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
            holding = await self._process_buy_transaction(portfolio_id, holding, data)
        else:  # SELL
            holding = await self._process_sell_transaction(holding, data)

        # Create transaction record
        transaction = Transaction(
            portfolio_id=portfolio_id,
            stock_code=data.stock_symbol,
            transaction_type=data.transaction_type.value,
            quantity=int(data.shares),
            price=float(data.price),
            amount=float(data.shares * data.price),
            commission=float(data.commission),
            transaction_date=data.transaction_date or datetime.now(),
            notes=data.notes,
        )
        transaction = await self.transaction_repo.create(transaction)

        await self.session.commit()

        return transaction

    async def _process_buy_transaction(
        self, portfolio_id: int, holding: Optional[Holding], data: TransactionCreate
    ) -> Holding:
        """Process buy transaction"""
        if holding is None:
            # Create new holding
            holding = Holding(
                portfolio_id=portfolio_id,
                stock_code=data.stock_symbol,
                shares=int(data.shares),
                average_price=float(data.price),
            )
            holding = await self.holding_repo.create(holding)
        else:
            # Update existing holding with weighted average price
            total_shares = Decimal(str(holding.shares)) + data.shares
            total_cost = (
                Decimal(str(holding.shares)) * Decimal(str(holding.average_price))
            ) + (data.shares * data.price)
            holding.shares = int(total_shares)
            holding.average_price = float(total_cost / total_shares)
            holding = await self.holding_repo.update(holding)

        return holding

    async def _process_sell_transaction(
        self, holding: Optional[Holding], data: TransactionCreate
    ) -> Holding:
        """Process sell transaction"""
        if holding is None:
            raise ValueError(f"No holdings found for {data.stock_symbol}")

        if Decimal(str(holding.shares)) < data.shares:
            raise ValueError(
                f"Insufficient shares: have {holding.shares}, "
                f"trying to sell {data.shares}"
            )

        # Reduce shares
        holding.shares = int(Decimal(str(holding.shares)) - data.shares)
        holding = await self.holding_repo.update(holding)

        return holding

    async def delete_transaction(
        self, transaction_id: int, portfolio_id: int, user_id: int
    ) -> bool:
        """
        Delete a transaction

        Args:
            transaction_id: Transaction ID
            portfolio_id: Portfolio ID
            user_id: User ID (for ownership check)

        Returns:
            True if deleted, False if not found
        """
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        if not transaction or transaction.portfolio_id != portfolio_id:
            return False

        # Check ownership
        portfolio = await self.get_portfolio_by_id(
            portfolio_id, user_id, load_holdings=False
        )
        if not portfolio:
            return False

        await self.transaction_repo.delete(transaction)
        await self.session.commit()
        return True
