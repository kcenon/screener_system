[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [hooks/useURLSync](../README.md) / useURLSync

# Function: useURLSync()

> **useURLSync**(`filters`, `setFilters`, `sort`, `setSort`, `pagination`, `setPagination`): `void`

Defined in: [src/hooks/useURLSync.ts:96](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/hooks/useURLSync.ts#L96)

Hook for synchronizing filters, sort, and pagination with URL

Features:
- Automatic URL update when state changes
- State initialization from URL on mount
- Browser back/forward support
- URL sharing support

## Parameters

### filters

[`ScreeningFilters`](../../../types/screening/interfaces/ScreeningFilters.md)

### setFilters

(`filters`) => `void`

### sort

#### sortBy

[`ScreeningSortField`](../../../types/screening/type-aliases/ScreeningSortField.md)

#### order

[`SortOrder`](../../../types/screening/type-aliases/SortOrder.md)

### setSort

(`sort`) => `void`

### pagination

#### offset

`number`

#### limit

`number`

### setPagination

(`pagination`) => `void`

## Returns

`void`
