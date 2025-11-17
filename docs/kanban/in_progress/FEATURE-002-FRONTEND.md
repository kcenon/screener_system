# FEATURE-002-FRONTEND: Portfolio Management System - Frontend Implementation

**Type**: FEATURE
**Priority**: P0
**Status**: IN_PROGRESS
**Parent Ticket**: FEATURE-002
**Created**: 2025-11-17
**Started**: 2025-11-17
**Effort**: 15-20 hours
**Phase**: Post-MVP - P0 Features (Part 2)

---

## Description

Implement the frontend UI for the Portfolio Management System. The backend API (PR #144) is already complete and provides 15 REST endpoints for portfolio, holdings, and transaction management. This ticket focuses exclusively on building the React frontend to consume these APIs.

## Current Status

- **Backend**: ✅ 100% Complete (PR #144 merged)
- **Frontend**: 🚧 85% → Near Complete
- **Overall Progress**: 60% → 92% (target: 100%)

### Backend API Available (✅ Complete)
- Portfolio CRUD (7 endpoints)
- Holdings management (4 endpoints)
- Transaction management (4 endpoints)
- Performance calculations
- Allocation calculations

### Frontend Implementation (✅ Mostly Complete)
- [x] Custom hooks for API integration (100%)
  - [x] usePortfolios.ts
  - [x] usePortfolioDetail.ts
  - [x] usePortfolioPerformance.ts (includes allocation)
  - [x] useTransactions.ts
- [x] Core pages (100%)
  - [x] PortfolioListPage.tsx
  - [x] PortfolioDetailPage.tsx
- [x] Charts (100%)
  - [x] PerformanceChart.tsx (bar chart)
  - [x] AllocationChart.tsx (pie/donut charts)
- [ ] Testing (0%)
  - [ ] Component tests
  - [ ] Integration tests
- [ ] Documentation updates (0%)

---

## Implementation Plan

### Phase 1: API Integration & Custom Hooks (5h)

#### 1.1 API Client Setup (1h)
Create `/frontend/src/services/portfolioService.ts`:
```typescript
import api from './api';

export interface Portfolio {
  id: number;
  name: string;
  description: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface Holding {
  id: number;
  portfolio_id: number;
  stock_symbol: string;
  shares: number;
  average_cost: number;
  current_price: number;
  current_value: number;
  total_cost: number;
  unrealized_gain: number;
  unrealized_gain_percent: number;
}

export interface Transaction {
  id: number;
  portfolio_id: number;
  stock_symbol: string;
  transaction_type: 'BUY' | 'SELL';
  shares: number;
  price: number;
  commission: number;
  transaction_date: string;
  notes: string;
}

export interface PerformanceMetrics {
  total_value: number;
  total_cost: number;
  total_gain: number;
  total_return_percent: number;
  day_change: number;
  day_change_percent: number;
}

export const portfolioService = {
  // Portfolio endpoints
  list: () => api.get<Portfolio[]>('/api/v1/portfolios'),
  create: (data: Partial<Portfolio>) => api.post('/api/v1/portfolios', data),
  get: (id: number) => api.get(`/api/v1/portfolios/${id}`),
  update: (id: number, data: Partial<Portfolio>) => api.put(`/api/v1/portfolios/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/portfolios/${id}`),
  getPerformance: (id: number) => api.get<PerformanceMetrics>(`/api/v1/portfolios/${id}/performance`),
  getAllocation: (id: number) => api.get(`/api/v1/portfolios/${id}/allocation`),

  // Holdings endpoints
  getHoldings: (id: number) => api.get<Holding[]>(`/api/v1/portfolios/${id}/holdings`),
  addHolding: (id: number, data: any) => api.post(`/api/v1/portfolios/${id}/holdings`, data),
  updateHolding: (portfolioId: number, holdingId: number, data: any) =>
    api.put(`/api/v1/portfolios/${portfolioId}/holdings/${holdingId}`, data),
  deleteHolding: (portfolioId: number, holdingId: number) =>
    api.delete(`/api/v1/portfolios/${portfolioId}/holdings/${holdingId}`),

  // Transactions endpoints
  getTransactions: (id: number) => api.get<Transaction[]>(`/api/v1/portfolios/${id}/transactions`),
  addTransaction: (id: number, data: Partial<Transaction>) =>
    api.post(`/api/v1/portfolios/${id}/transactions`, data),
  deleteTransaction: (portfolioId: number, transactionId: number) =>
    api.delete(`/api/v1/portfolios/${portfolioId}/transactions/${transactionId}`),
};
```

#### 1.2 Custom Hooks (4h)
- `usePortfolios.ts` (1h): List, create, delete portfolios
- `usePortfolioDetail.ts` (1h): Single portfolio with holdings
- `usePortfolioPerformance.ts` (1h): Performance metrics with refresh
- `useTransactions.ts` (1h): Transaction history and CRUD

### Phase 2: Core Pages & Components (8h)

#### 2.1 Portfolio List Page (2h)
`/frontend/src/pages/PortfolioListPage.tsx`:
- Display all portfolios in grid layout
- Show summary metrics for each (total value, day change, return %)
- Create new portfolio button
- Delete portfolio action
- Navigation to detail page

#### 2.2 Portfolio Detail Page (3h)
`/frontend/src/pages/PortfolioDetailPage.tsx`:
- Portfolio header with name, description, edit button
- Performance metrics dashboard
- Holdings table with current values
- Quick add transaction button
- Performance chart (simple line chart)
- Allocation pie chart

#### 2.3 Transaction Form & History (3h)
`/frontend/src/components/portfolio/TransactionForm.tsx`:
- Buy/Sell toggle
- Stock symbol autocomplete
- Shares, price, commission inputs
- Date picker
- Notes textarea

`/frontend/src/components/portfolio/TransactionTable.tsx`:
- Sortable transaction table
- Filter by stock symbol
- Filter by date range
- Delete transaction action

### Phase 3: Charts & Visualizations (4h)

#### 3.1 Performance Chart (2h)
`/frontend/src/components/portfolio/PerformanceChart.tsx`:
- Line chart showing portfolio value over time
- Use Recharts or Chart.js
- Time range selector (1W, 1M, 3M, 1Y, ALL)
- Tooltip with date and value

#### 3.2 Allocation Charts (2h)
`/frontend/src/components/portfolio/AllocationChart.tsx`:
- Pie chart for stock allocation
- Donut chart for sector allocation
- Legend with percentages
- Hover tooltips

### Phase 4: Testing & Polish (3-5h)

#### 4.1 Component Tests (2h)
- Test PortfolioCard rendering
- Test TransactionForm submission
- Test HoldingsTable calculations

#### 4.2 Integration Tests (1-2h)
- Test portfolio creation flow
- Test transaction addition flow
- Test portfolio deletion

#### 4.3 Mobile Responsive (1h)
- Ensure all pages work on mobile
- Responsive tables (horizontal scroll or cards)
- Touch-friendly buttons

---

## File Structure

```
frontend/src/
├── services/
│   └── portfolioService.ts         (NEW - API client)
├── hooks/
│   ├── usePortfolios.ts            (NEW)
│   ├── usePortfolioDetail.ts       (NEW)
│   ├── usePortfolioPerformance.ts  (NEW)
│   └── useTransactions.ts          (NEW)
├── pages/
│   ├── PortfolioListPage.tsx       (NEW)
│   ├── PortfolioDetailPage.tsx     (NEW)
│   └── PortfolioEditPage.tsx       (NEW - optional)
└── components/
    └── portfolio/
        ├── PortfolioCard.tsx       (NEW)
        ├── PortfolioMetrics.tsx    (NEW)
        ├── HoldingsTable.tsx       (NEW)
        ├── TransactionForm.tsx     (NEW)
        ├── TransactionTable.tsx    (NEW)
        ├── PerformanceChart.tsx    (NEW)
        └── AllocationChart.tsx     (NEW)
```

---

## Acceptance Criteria

### Functionality
- [ ] Users can view list of all their portfolios
- [ ] Users can create a new portfolio with name and description
- [ ] Users can view portfolio details with holdings and performance
- [ ] Users can add buy/sell transactions
- [ ] Users can delete transactions
- [ ] Users can delete portfolios
- [ ] Performance metrics calculate correctly (total value, gain/loss, return %)
- [ ] Charts display portfolio performance over time
- [ ] Allocation charts show stock and sector breakdown

### UI/UX
- [ ] Mobile responsive on all pages
- [ ] Loading states for all async operations
- [ ] Error messages for failed API calls
- [ ] Confirmation dialog for delete operations
- [ ] Success toast notifications for actions

### Testing
- [ ] All custom hooks tested (4 hooks)
- [ ] All pages render without errors (3 pages)
- [ ] Transaction form validation works
- [ ] Integration tests for main user flows

### Code Quality
- [ ] TypeScript types for all API responses
- [ ] Consistent styling with existing pages
- [ ] Reusable components extracted
- [ ] No console errors or warnings

---

## Dependencies

- ✅ Backend API (PR #144 merged)
- ✅ Authentication system (existing)
- ✅ Stock data API (for autocomplete)
- ⏸️ Chart library (Recharts - to be installed)

---

## Testing Strategy

1. **Unit Tests**: Test custom hooks with mock API responses
2. **Component Tests**: Test rendering and user interactions
3. **Integration Tests**: Test complete flows (create → add transaction → view)
4. **Manual Testing**: Test on desktop and mobile browsers

---

## Related PRs

- Parent: PR #144 (FEATURE-002 Backend - Merged)
- This ticket: TBD (FEATURE-002-FRONTEND)

---

## Notes

- Backend provides real-time price updates via holdings endpoint
- Commission costs are included in backend calculations
- Average cost uses weighted average (implemented in backend)
- Frontend focuses on UI/UX, business logic is in backend

---

## Progress Tracking

- [x] Phase 1: API Integration & Hooks (5h) - 100% ✅
  - [x] portfolioService.ts (API client)
  - [x] usePortfolios.ts
  - [x] usePortfolioDetail.ts
  - [x] usePortfolioPerformance.ts (includes allocation)
  - [x] useTransactions.ts
- [x] Phase 2: Core Pages & Components (8h) - 100% ✅
  - [x] PortfolioListPage.tsx (with grid layout, metrics)
  - [x] PortfolioDetailPage.tsx (with inline components)
  - [x] Performance metrics display
  - [x] Holdings table
  - [x] Transaction form & history
- [x] Phase 3: Charts & Visualizations (4h) - 100% ✅
  - [x] PerformanceChart.tsx (bar chart with metrics)
  - [x] AllocationChart.tsx (pie/donut charts)
  - [x] Integrated into PortfolioDetailPage
- [ ] Phase 4: Testing & Polish (3-5h) - 0%
  - [ ] Component tests
  - [ ] Integration tests
  - [ ] Mobile responsive testing

**Total Progress**: 17h completed / 20h estimated (85% complete)
**Commits**: 4 commits (API client, hooks, pages, charts)
