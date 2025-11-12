[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [hooks/usePriceChart](../README.md) / usePriceChart

# Function: usePriceChart()

> **usePriceChart**(`code`, `initialTimeframe`): \{ `timeframe`: [`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md); `setTimeframe`: `Dispatch`\<`SetStateAction`\<[`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md)\>\>; `fromDate`: `string`; `toDate`: `string`; \} \| \{ `timeframe`: [`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md); `setTimeframe`: `Dispatch`\<`SetStateAction`\<[`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md)\>\>; `fromDate`: `string`; `toDate`: `string`; \} \| \{ `timeframe`: [`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md); `setTimeframe`: `Dispatch`\<`SetStateAction`\<[`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md)\>\>; `fromDate`: `string`; `toDate`: `string`; \} \| \{ `timeframe`: [`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md); `setTimeframe`: `Dispatch`\<`SetStateAction`\<[`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md)\>\>; `fromDate`: `string`; `toDate`: `string`; \} \| \{ `timeframe`: [`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md); `setTimeframe`: `Dispatch`\<`SetStateAction`\<[`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md)\>\>; `fromDate`: `string`; `toDate`: `string`; \} \| \{ `timeframe`: [`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md); `setTimeframe`: `Dispatch`\<`SetStateAction`\<[`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md)\>\>; `fromDate`: `string`; `toDate`: `string`; \}

Defined in: [src/hooks/usePriceChart.ts:33](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/hooks/usePriceChart.ts#L33)

Hook for managing price chart data and timeframe

Features:
- Timeframe selection (1D, 1W, 1M, 3M, 6M, 1Y, 3Y, 5Y, ALL)
- Automatic date range calculation
- Data caching per timeframe
- Loading and error states

## Parameters

### code

Stock code

`string` | `undefined`

### initialTimeframe

[`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md) = `'1M'`

Initial timeframe (default: '1M')

## Returns

\{ `timeframe`: [`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md); `setTimeframe`: `Dispatch`\<`SetStateAction`\<[`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md)\>\>; `fromDate`: `string`; `toDate`: `string`; \} \| \{ `timeframe`: [`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md); `setTimeframe`: `Dispatch`\<`SetStateAction`\<[`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md)\>\>; `fromDate`: `string`; `toDate`: `string`; \} \| \{ `timeframe`: [`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md); `setTimeframe`: `Dispatch`\<`SetStateAction`\<[`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md)\>\>; `fromDate`: `string`; `toDate`: `string`; \} \| \{ `timeframe`: [`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md); `setTimeframe`: `Dispatch`\<`SetStateAction`\<[`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md)\>\>; `fromDate`: `string`; `toDate`: `string`; \} \| \{ `timeframe`: [`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md); `setTimeframe`: `Dispatch`\<`SetStateAction`\<[`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md)\>\>; `fromDate`: `string`; `toDate`: `string`; \} \| \{ `timeframe`: [`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md); `setTimeframe`: `Dispatch`\<`SetStateAction`\<[`PriceInterval`](../../../types/stock/type-aliases/PriceInterval.md)\>\>; `fromDate`: `string`; `toDate`: `string`; \}

Chart data, timeframe state, and controls

## Example

```tsx
const { data, isLoading, timeframe, setTimeframe } = usePriceChart('005930')

return (
  <div>
    <button onClick={() => setTimeframe('1M')}>1M</button>
    <button onClick={() => setTimeframe('1Y')}>1Y</button>
    <PriceChart data={data} loading={isLoading} />
  </div>
)
```
