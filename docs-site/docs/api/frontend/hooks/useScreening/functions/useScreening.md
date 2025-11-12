[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [hooks/useScreening](../README.md) / useScreening

# Function: useScreening()

> **useScreening**(): `object`

Defined in: [src/hooks/useScreening.ts:167](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/hooks/useScreening.ts#L167)

React Query hook for stock screening with advanced filtering capabilities.

Provides a complete screening experience with automatic debouncing, caching,
and state management for filters, sorting, and pagination. Uses React Query
for efficient data fetching with background refetching and cache management.

## Features

- **Automatic Debouncing**: Filter changes are debounced by 500ms to reduce API calls
- **React Query Integration**: Automatic caching (5min), background refetching, and error handling
- **Pagination Management**: Offset-based pagination with automatic page reset on filter changes
- **Sort Management**: Configurable sorting by any screening field
- **Type Safety**: Full TypeScript support with type inference

## Query Caching

- Stale Time: 5 minutes (data considered fresh for 5 minutes)
- Garbage Collection: 10 minutes (cached data kept for 10 minutes)
- Window Focus Refetching: Disabled (manual refetch required)

## Returns

`object`

Screening state and control functions

### data

> **data**: [`ScreeningResponse`](../../../types/screening/interfaces/ScreeningResponse.md) \| `undefined`

### isLoading

> **isLoading**: `boolean`

### error

> **error**: `Error` \| `null`

### filters

> **filters**: [`ScreeningFilters`](../../../types/screening/interfaces/ScreeningFilters.md)

### sort

> **sort**: `SortState`

### pagination

> **pagination**: `PaginationState`

### setFilters

> **setFilters**: `Dispatch`\<`SetStateAction`\<[`ScreeningFilters`](../../../types/screening/interfaces/ScreeningFilters.md)\>\>

### setSort

> **setSort**: `Dispatch`\<`SetStateAction`\<`SortState`\>\>

### setPagination

> **setPagination**: `Dispatch`\<`SetStateAction`\<`PaginationState`\>\>

### refetch()

> **refetch**: (`options?`) => `Promise`\<`QueryObserverResult`\<[`ScreeningResponse`](../../../types/screening/interfaces/ScreeningResponse.md), `Error`\>\>

#### Parameters

##### options?

`RefetchOptions`

#### Returns

`Promise`\<`QueryObserverResult`\<[`ScreeningResponse`](../../../types/screening/interfaces/ScreeningResponse.md), `Error`\>\>

## Hook

## Examples

Basic usage with default filters
```tsx
const {
  data,
  isLoading,
  error,
  setFilters,
  pagination,
  setPagination
} = useScreening();

if (isLoading) return <Spinner />;
if (error) return <ErrorAlert error={error} />;

return (
  <StockTable
    stocks={data.items}
    total={data.meta.total}
    onPageChange={(page) => setPagination({ offset: page * 50, limit: 50 })}
  />
);
```

Advanced usage with filters and sorting
```tsx
const { data, setFilters, setSort } = useScreening();

// Apply filters (debounced automatically)
setFilters({
  market: 'KOSPI',
  per: { min: 0, max: 20 },
  pbr: { min: 0, max: 1.5 },
  roe: { min: 10 }
});

// Change sort order
setSort({ sortBy: 'market_cap', order: 'desc' });

// Manual refetch
refetch();
```

Pagination control
```tsx
const { pagination, setPagination, data } = useScreening();

const goToPage = (pageNumber: number) => {
  setPagination({
    offset: pageNumber * pagination.limit,
    limit: pagination.limit
  });
};

const changePageSize = (newSize: number) => {
  setPagination({ offset: 0, limit: newSize });
};
```

## See

 - [ScreeningFilters](../../../types/screening/interfaces/ScreeningFilters.md) for available filter options
 - [ScreeningResponse](../../../types/screening/interfaces/ScreeningResponse.md) for response data structure
 - stockService.screenStocks for underlying API call

## Subcategory

Data Fetching
