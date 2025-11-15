# TEST-008: ScreenerPage Component Tests

**Type**: TEST
**Priority**: P0
**Status**: TODO
**Created**: 2025-11-16
**Effort**: 4 hours
**Phase**: Phase 1 - Critical Tests

---

## Description

Implement comprehensive tests for the ScreenerPage component. This is the core feature of the platform - the stock screening interface with filters, results, and export functionality.

## Current Status

- **Test File**: `frontend/src/pages/ScreenerPage.test.tsx` does not exist
- **Component**: `frontend/src/pages/ScreenerPage.tsx` (exists, untested)
- **Coverage Impact**: Core platform feature with 0% test coverage

## Test Requirements

### 1. Component Rendering (0.5h)

```typescript
describe('ScreenerPage Rendering', () => {
  test('renders filter panel', () => {
    // Test filter controls are present
  });

  test('renders results table', () => {
    // Test stock results table rendered
  });

  test('renders empty state when no results', () => {
    // Test empty state message
  });

  test('renders loading state during data fetch', () => {
    // Test loading skeleton/spinner
  });

  test('renders export button', () => {
    // Test export functionality button
  });
});
```

### 2. Filter Application (2h)

```typescript
describe('ScreenerPage Filters', () => {
  test('applies market cap filter', async () => {
    // Test market cap range filter
  });

  test('applies sector filter', async () => {
    // Test sector dropdown filter
  });

  test('applies price range filter', async () => {
    // Test price min/max filter
  });

  test('applies volume filter', async () => {
    // Test volume threshold filter
  });

  test('applies PE ratio filter', async () => {
    // Test PE ratio range filter
  });

  test('applies multiple filters simultaneously', async () => {
    // Test combining multiple filters
  });

  test('resets all filters', async () => {
    // Test "Clear All" functionality
  });

  test('updates URL query parameters with filters', async () => {
    // Test filters reflected in URL
  });

  test('loads filters from URL on mount', () => {
    // Test initial filters from query params
  });
});
```

### 3. Results Rendering (1h)

```typescript
describe('ScreenerPage Results', () => {
  test('renders stock list with correct data', async () => {
    // Test stocks displayed with correct fields
  });

  test('renders pagination controls', async () => {
    // Test page numbers and navigation
  });

  test('changes page when pagination clicked', async () => {
    // Test page navigation
  });

  test('sorts results by column', async () => {
    // Test column header sorting
  });

  test('updates sort direction', async () => {
    // Test ascending/descending toggle
  });

  test('shows row count and total stocks', async () => {
    // Test result count display
  });

  test('navigates to stock detail on row click', async () => {
    // Test clicking stock row
  });
});
```

### 4. Export Functionality (0.5h)

```typescript
describe('ScreenerPage Export', () => {
  test('exports results to CSV', async () => {
    // Test CSV download functionality
  });

  test('exports filtered results only', async () => {
    // Test export includes only filtered stocks
  });

  test('exports with correct column headers', async () => {
    // Test CSV headers match table columns
  });

  test('disables export when no results', () => {
    // Test export disabled for empty results
  });
});
```

## Acceptance Criteria

- [ ] All rendering tests pass (filters, table, empty states)
- [ ] All filter types tested (market cap, sector, price, volume, PE ratio)
- [ ] Filter combinations tested
- [ ] Results rendering tested (pagination, sorting, navigation)
- [ ] Export functionality tested (CSV download)
- [ ] URL state management tested (filters in query params)
- [ ] Test coverage for ScreenerPage reaches >80%
- [ ] All tests pass in CI/CD pipeline

## Dependencies

- @testing-library/react
- @testing-library/user-event
- @testing-library/jest-dom
- MSW (Mock Service Worker) for API mocking
- React Router (for URL params and navigation)

## Testing Strategy

1. **Component Tests**: Render and interaction tests
2. **Integration Tests**: Test with mocked API responses
3. **User Flow Tests**: Complete filtering workflow
4. **State Tests**: Verify filter state management

## Related Files

- Component: `frontend/src/pages/ScreenerPage.tsx`
- Test: `frontend/src/pages/ScreenerPage.test.tsx` (to be created)
- Hook: `frontend/src/hooks/useScreening.ts`
- API: `frontend/src/services/stocks.ts`
- Components: Various filter components

## Mock Data Requirements

```typescript
// Mock stock screening results
const mockScreeningResults = {
  stocks: [
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      price: 175.43,
      change_percent: 2.15,
      market_cap: 2800000000000,
      sector: 'Technology',
      pe_ratio: 28.5,
      volume: 52000000
    },
    // ... more stocks
  ],
  total: 150,
  page: 1,
  page_size: 20
};
```

## Notes

- Test with various filter combinations
- Verify API calls include correct query parameters
- Test debouncing for filter inputs (if implemented)
- Test keyboard navigation in filter inputs
- Verify CSV export downloads correctly
- Test responsive layout if applicable
- Test with large result sets (performance)

---

**References**: TEST_IMPROVEMENT_PLAN.md - Phase 1, Item #8
