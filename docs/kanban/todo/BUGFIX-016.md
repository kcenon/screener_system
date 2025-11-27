# BUGFIX-016: Fix Duplicate React Keys in ResultsTable Component

## Metadata
- **Status**: TODO
- **Priority**: Low
- **Assignee**: TBD
- **Estimated Time**: 1-2 hours
- **Sprint**: Phase 5 (Quality)
- **Tags**: frontend, react, bugfix, warning

## Description

The `ResultsTable` component generates React warnings about duplicate keys. This occurs when rendering table headers and can cause unpredictable behavior with component updates.

**Warning Messages:**
```
Warning: Encountered two children with the same key, `price_change_1d`.
Keys should be unique so that components maintain their identity across updates.

Warning: Encountered two children with the same key, `code`.
Keys should be unique so that components maintain their identity across updates.
```

**Location:** `frontend/src/components/screener/ResultsTable.tsx:114`

## Root Cause Analysis

The duplicate keys likely occur because:
1. Column definitions may have duplicate `id` or `key` properties
2. Dynamic column generation creates overlapping keys
3. Header cells and sortable columns share the same key namespace

## Subtasks

- [ ] Identify exact location of duplicate key generation
- [ ] Review column definition structure
- [ ] Implement unique key generation for all table elements
- [ ] Add prefix/namespace to differentiate header vs body keys
- [ ] Update unit tests to verify no duplicate keys
- [ ] Verify fix in all table usage scenarios
- [ ] Ensure sorting and filtering still work correctly

## Acceptance Criteria

1. No "duplicate key" warnings in console during any table operation
2. All table functionality preserved (sorting, pagination, etc.)
3. Unit tests pass without key-related warnings
4. Table re-renders correctly on data updates

## Technical Details

### Potential Fix Locations

**Column Definition (columns.ts or similar):**
```typescript
// Before - potential duplicate
const columns = [
  { id: 'code', header: 'Code' },
  { id: 'price_change_1d', header: '1D Change' },
  // ... might have duplicates
];

// After - ensure unique IDs
const columns = [
  { id: 'stock_code', header: 'Code' },
  { id: 'price_change_1d', header: '1D Change' },
  // ... verified unique
];
```

**Header Rendering (ResultsTable.tsx):**
```typescript
// Before
<thead>
  <tr>
    {columns.map((col) => (
      <th key={col.id}>{col.header}</th>
    ))}
  </tr>
</thead>

// After - with namespace prefix
<thead>
  <tr>
    {columns.map((col) => (
      <th key={`header-${col.id}`}>{col.header}</th>
    ))}
  </tr>
</thead>
```

### Files to Review

1. `frontend/src/components/screener/ResultsTable.tsx`
2. `frontend/src/components/screener/columns.ts` (if exists)
3. `frontend/src/hooks/useScreening.ts`
4. Related test files

## Dependencies
- None

## Blocks
- None

## Progress
- [ ] 0% - Not started

## Notes
- This is a warning-level issue, not a blocking bug
- May indicate deeper issues with column configuration
- React strict mode helps catch these issues early
- Consider adding ESLint rule for key uniqueness

## Testing

```typescript
// Add test to verify no duplicate keys
describe('ResultsTable', () => {
  it('should not have duplicate keys in rendered elements', () => {
    const { container } = render(<ResultsTable data={mockData} />);
    const keys = new Set();
    container.querySelectorAll('[data-key]').forEach((el) => {
      const key = el.getAttribute('data-key');
      expect(keys.has(key)).toBe(false);
      keys.add(key);
    });
  });
});
```
