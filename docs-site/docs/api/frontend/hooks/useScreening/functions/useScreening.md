[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [hooks/useScreening](../README.md) / useScreening

# Function: useScreening()

> **useScreening**(): `object`

Defined in: [src/hooks/useScreening.ts:37](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/hooks/useScreening.ts#L37)

Custom hook for stock screening with filters, sorting, and pagination

Features:
- Automatic debouncing of filter changes (500ms)
- React Query caching and automatic refetching
- Separate state management for filters, sorting, and pagination

## Returns

`object`

Object containing screening data, loading state, error, and state setters

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
