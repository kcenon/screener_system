[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [hooks/useStockData](../README.md) / useStockData

# Function: useStockData()

> **useStockData**(`code`): `UseQueryResult`\<[`StockDetail`](../../../types/stock/interfaces/StockDetail.md), `Error`\>

Defined in: [src/hooks/useStockData.ts:26](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/hooks/useStockData.ts#L26)

Hook for fetching and caching stock detail data

Features:
- Automatic caching with 5-minute stale time
- Auto-refetch on window focus
- Error handling
- Loading states

## Parameters

### code

Stock code (e.g., '005930')

`string` | `undefined`

## Returns

`UseQueryResult`\<[`StockDetail`](../../../types/stock/interfaces/StockDetail.md), `Error`\>

Query result with stock data, loading state, and error

## Example

```tsx
const { data, isLoading, error } = useStockData('005930')

if (isLoading) return <div>Loading...</div>
if (error) return <div>Error: {error.message}</div>
if (data) return <div>{data.name}</div>
```
