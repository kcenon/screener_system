# TEST-009: StockDetailPage Component Tests

**Type**: TEST
**Priority**: P0
**Status**: TODO
**Created**: 2025-11-16
**Effort**: 3 hours
**Phase**: Phase 1 - Critical Tests

---

## Description

Implement comprehensive tests for the StockDetailPage component. This page displays detailed stock information, charts, and watchlist actions - a critical user feature.

## Current Status

- **Test File**: `frontend/src/pages/StockDetailPage.test.tsx` does not exist
- **Component**: `frontend/src/pages/StockDetailPage.tsx` (exists, untested)
- **Coverage Impact**: Critical stock detail view with 0% test coverage

## Test Requirements

### 1. Component Rendering (1h)

```typescript
describe('StockDetailPage Rendering', () => {
  test('renders stock header with symbol and name', async () => {
    // Test stock header information
  });

  test('renders current price and change', async () => {
    // Test price display
  });

  test('renders price chart', async () => {
    // Test chart component rendered
  });

  test('renders financial metrics section', async () => {
    // Test key metrics displayed
  });

  test('renders company description', async () => {
    // Test company info section
  });

  test('renders loading state during data fetch', () => {
    // Test loading skeleton
  });

  test('renders error state for invalid symbol', async () => {
    // Test 404 error state
  });
});
```

### 2. Stock Data Display (1h)

```typescript
describe('StockDetailPage Data Display', () => {
  test('displays all key financial metrics', async () => {
    // Test PE ratio, market cap, volume, etc.
  });

  test('displays positive price change in green', async () => {
    // Test color coding for gains
  });

  test('displays negative price change in red', async () => {
    // Test color coding for losses
  });

  test('formats large numbers correctly', async () => {
    // Test number formatting (1.2B, 500M, etc.)
  });

  test('shows percentage change with + or - sign', async () => {
    // Test change percentage formatting
  });

  test('updates data when symbol changes', async () => {
    // Test route param change handling
  });
});
```

### 3. Chart Rendering (0.5h)

```typescript
describe('StockDetailPage Chart', () => {
  test('renders price chart with historical data', async () => {
    // Test chart displays price data
  });

  test('changes timeframe when period button clicked', async () => {
    // Test 1D, 1W, 1M, 3M, 1Y, 5Y buttons
  });

  test('loads appropriate data for selected timeframe', async () => {
    // Test API called with correct date range
  });

  test('shows chart loading state', async () => {
    // Test chart skeleton/spinner
  });
});
```

### 4. Watchlist Actions (0.5h)

```typescript
describe('StockDetailPage Watchlist', () => {
  test('shows "Add to Watchlist" button when not in watchlist', async () => {
    // Test button state for unwatched stock
  });

  test('shows "Remove from Watchlist" button when in watchlist', async () => {
    // Test button state for watched stock
  });

  test('adds stock to watchlist on button click', async () => {
    // Test add to watchlist flow
  });

  test('removes stock from watchlist on button click', async () => {
    // Test remove from watchlist flow
  });

  test('shows success message after watchlist action', async () => {
    // Test toast/notification
  });

  test('handles watchlist action errors', async () => {
    // Test error handling
  });
});
```

## Acceptance Criteria

- [ ] All rendering tests pass (header, chart, metrics, company info)
- [ ] Data display tested (formatting, colors, updates)
- [ ] Chart functionality tested (timeframe selection, data loading)
- [ ] Watchlist actions tested (add, remove, success/error states)
- [ ] Loading and error states tested
- [ ] Navigation tested (URL param changes)
- [ ] Test coverage for StockDetailPage reaches >85%
- [ ] All tests pass in CI/CD pipeline

## Dependencies

- @testing-library/react
- @testing-library/user-event
- @testing-library/jest-dom
- MSW (Mock Service Worker) for API mocking
- React Router (for URL params)
- Chart testing utilities (if needed)

## Testing Strategy

1. **Component Tests**: Render and interaction tests
2. **Integration Tests**: Test with mocked API responses
3. **User Flow Tests**: Complete view + watchlist workflow
4. **Route Tests**: Test symbol param changes

## Related Files

- Component: `frontend/src/pages/StockDetailPage.tsx`
- Test: `frontend/src/pages/StockDetailPage.test.tsx` (to be created)
- Hook: `frontend/src/hooks/useStockData.ts`
- Hook: `frontend/src/hooks/useWatchlist.ts`
- API: `frontend/src/services/stocks.ts`
- Components: StockHeader, PriceChart, FinancialMetrics, etc.

## Mock Data Requirements

```typescript
// Mock stock detail data
const mockStockDetail = {
  symbol: 'AAPL',
  name: 'Apple Inc.',
  current_price: 175.43,
  change: 3.78,
  change_percent: 2.15,
  market_cap: 2800000000000,
  pe_ratio: 28.5,
  volume: 52000000,
  avg_volume: 55000000,
  week_52_high: 198.23,
  week_52_low: 124.17,
  description: 'Apple Inc. designs, manufactures...'
};

// Mock price history data
const mockPriceHistory = [
  { date: '2024-01-01', close: 170.00, open: 169.50, high: 171.00, low: 169.00 },
  // ... more data points
];
```

## Notes

- Test with various symbols via route params
- Verify chart library integration (recharts, etc.)
- Test real-time price updates if implemented
- Test responsive layout if applicable
- Verify number formatting functions
- Test accessibility (keyboard navigation, ARIA labels)

---

**References**: TEST_IMPROVEMENT_PLAN.md - Phase 1, Item #9
