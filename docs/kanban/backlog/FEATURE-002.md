# FEATURE-002: Portfolio Management System

**Type**: FEATURE
**Priority**: P0
**Status**: TODO
**Created**: 2025-11-16
**Effort**: 40-60 hours
**Phase**: Post-MVP - P0 Features

---

## Description

Implement comprehensive portfolio management system allowing users to track their stock holdings, monitor performance, and analyze portfolio allocation. This is a P0 feature from the PRD that is currently 0% implemented.

## Current Status

- **Implementation**: 0% (not started)
- **Missing Components**:
  - Backend: Models, services, API endpoints (0%)
  - Frontend: Pages, components, hooks (0%)
  - Database: Portfolio schema, transactions (0%)

## Feature Requirements

### 1. Backend Implementation (20-25h)

#### Database Schema (5h)
```sql
-- Portfolio table
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Holdings table
CREATE TABLE holdings (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    stock_symbol VARCHAR(20) NOT NULL REFERENCES stocks(symbol),
    shares DECIMAL(18, 8) NOT NULL,
    average_cost DECIMAL(18, 2) NOT NULL,
    first_purchase_date DATE,
    last_update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    stock_symbol VARCHAR(20) NOT NULL REFERENCES stocks(symbol),
    transaction_type VARCHAR(10) NOT NULL, -- BUY, SELL
    shares DECIMAL(18, 8) NOT NULL,
    price DECIMAL(18, 2) NOT NULL,
    commission DECIMAL(18, 2) DEFAULT 0,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Indexes
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX idx_holdings_portfolio_id ON holdings(portfolio_id);
CREATE INDEX idx_holdings_stock_symbol ON holdings(stock_symbol);
CREATE INDEX idx_transactions_portfolio_id ON transactions(portfolio_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
```

#### Models (3h)
- Portfolio model with relationships
- Holding model with calculated fields
- Transaction model with validation

#### Services (8h)
- PortfolioService:
  - Create/update/delete portfolios
  - Add/remove holdings
  - Calculate portfolio value and performance
  - Generate performance metrics (returns, gains/losses)
- TransactionService:
  - Record buy/sell transactions
  - Update holdings based on transactions
  - Transaction history and filtering

#### API Endpoints (4h)
```python
# Portfolio endpoints
GET    /api/v1/portfolios/                    # List user portfolios
POST   /api/v1/portfolios/                    # Create portfolio
GET    /api/v1/portfolios/{id}                # Get portfolio details
PUT    /api/v1/portfolios/{id}                # Update portfolio
DELETE /api/v1/portfolios/{id}                # Delete portfolio
GET    /api/v1/portfolios/{id}/performance    # Get performance metrics
GET    /api/v1/portfolios/{id}/allocation     # Get allocation breakdown

# Holdings endpoints
GET    /api/v1/portfolios/{id}/holdings       # List holdings
POST   /api/v1/portfolios/{id}/holdings       # Add holding
PUT    /api/v1/portfolios/{id}/holdings/{id}  # Update holding
DELETE /api/v1/portfolios/{id}/holdings/{id}  # Remove holding

# Transactions endpoints
GET    /api/v1/portfolios/{id}/transactions   # List transactions
POST   /api/v1/portfolios/{id}/transactions   # Record transaction
DELETE /api/v1/portfolios/{id}/transactions/{id} # Delete transaction
```

### 2. Frontend Implementation (15-20h)

#### Pages (8h)
- **PortfolioListPage**: Display all user portfolios with summary
- **PortfolioDetailPage**: Detailed view of single portfolio
- **PortfolioEditPage**: Create/edit portfolio form
- **TransactionHistoryPage**: View and manage transactions

#### Components (7h)
- **PortfolioCard**: Summary card for portfolio list
- **HoldingsTable**: Table of stock holdings with current value
- **PerformanceChart**: Line chart showing portfolio performance over time
- **AllocationChart**: Pie/donut chart showing sector/stock allocation
- **TransactionForm**: Add buy/sell transaction
- **TransactionTable**: Table of transaction history
- **PortfolioMetrics**: Dashboard with key metrics (total value, day change, total return)

#### Hooks (5h)
- **usePortfolios**: Fetch and manage portfolios
- **usePortfolioDetail**: Fetch single portfolio with holdings
- **usePortfolioPerformance**: Fetch performance data
- **useTransactions**: Manage transactions
- **usePortfolioAllocation**: Calculate allocation breakdown

### 3. Business Logic (5-10h)

#### Performance Calculations
```python
def calculate_portfolio_performance(portfolio_id: int):
    """
    Calculate portfolio performance metrics:
    - Total value (current market value)
    - Total cost (total invested)
    - Total gain/loss (value - cost)
    - Total return % ((value - cost) / cost * 100)
    - Day change (today's value change)
    - Day change % (today's percentage change)
    """

def calculate_holding_performance(holding):
    """
    Calculate individual holding performance:
    - Current value (shares * current_price)
    - Total cost (shares * average_cost)
    - Unrealized gain/loss (current_value - total_cost)
    - Return % ((current_price - average_cost) / average_cost * 100)
    """

def calculate_allocation(portfolio_id: int):
    """
    Calculate portfolio allocation:
    - By stock (% of total value per stock)
    - By sector (% of total value per sector)
    - By market cap (large/mid/small cap distribution)
    """
```

#### Transaction Processing
```python
def process_buy_transaction(portfolio_id, stock_symbol, shares, price, commission):
    """
    Process buy transaction:
    1. Create transaction record
    2. Update or create holding
    3. Recalculate average cost using weighted average
    4. Update portfolio last_update_date
    """

def process_sell_transaction(portfolio_id, stock_symbol, shares, price, commission):
    """
    Process sell transaction:
    1. Validate sufficient shares in holding
    2. Create transaction record
    3. Update holding (reduce shares)
    4. If shares = 0, optionally remove holding
    5. Calculate realized gain/loss
    """
```

## Acceptance Criteria

### Backend
- [ ] Database schema created with migrations
- [ ] Portfolio, Holding, Transaction models implemented
- [ ] All CRUD operations for portfolios working
- [ ] Transaction processing correctly updates holdings
- [ ] Performance calculations accurate (verified with test data)
- [ ] Allocation calculations accurate
- [ ] All API endpoints tested (>80% coverage)
- [ ] Authorization enforced (users can only access their portfolios)

### Frontend
- [ ] Portfolio list page displays all portfolios
- [ ] Portfolio detail page shows holdings and performance
- [ ] Transaction form allows adding buy/sell transactions
- [ ] Performance chart visualizes portfolio value over time
- [ ] Allocation charts show sector and stock breakdown
- [ ] Real-time price updates for holdings
- [ ] Mobile responsive design

### Business Logic
- [ ] Average cost calculated correctly using weighted average
- [ ] Total return and day change calculated correctly
- [ ] Allocation percentages sum to 100%
- [ ] Realized vs unrealized gains tracked separately
- [ ] Commission costs included in calculations

## Dependencies

- Stock price data (from existing stocks API)
- User authentication (from existing auth system)
- Real-time price updates (from WebSocket system)

## Testing Strategy

1. **Unit Tests**: Test all service methods and calculations
2. **Integration Tests**: Test API endpoints with test database
3. **Component Tests**: Test all React components
4. **E2E Tests**: Test complete user flows (create portfolio, add transaction, view performance)
5. **Edge Cases**: Empty portfolio, fractional shares, negative returns, commission edge cases

## Related Files

- Backend:
  - `backend/app/models/portfolio.py` (new)
  - `backend/app/services/portfolio_service.py` (new)
  - `backend/app/api/v1/endpoints/portfolios.py` (new)
  - `backend/alembic/versions/xxx_create_portfolio_tables.py` (new migration)
- Frontend:
  - `frontend/src/pages/PortfolioListPage.tsx` (new)
  - `frontend/src/pages/PortfolioDetailPage.tsx` (new)
  - `frontend/src/hooks/usePortfolios.ts` (new)
  - `frontend/src/components/portfolio/` (new directory)

## Notes

- Consider importing transactions from CSV (future enhancement)
- Consider supporting multiple currencies (future enhancement)
- Consider dividend tracking (future enhancement)
- Performance optimization: Cache portfolio values, recalculate only on price updates
- Security: Ensure users cannot access other users' portfolios
- Validation: Prevent selling more shares than owned

## User Stories

1. **As a user**, I want to create multiple portfolios to track different investment strategies
2. **As a user**, I want to add buy/sell transactions to track my holdings
3. **As a user**, I want to see my portfolio performance (total return, day change)
4. **As a user**, I want to see how my portfolio is allocated across sectors and stocks
5. **As a user**, I want to see a history of all my transactions
6. **As a user**, I want to see real-time updates of my portfolio value

---

**References**:
- PRD Section 4.3: Portfolio Management
- TEST_IMPROVEMENT_PLAN.md - Missing P0 Features
