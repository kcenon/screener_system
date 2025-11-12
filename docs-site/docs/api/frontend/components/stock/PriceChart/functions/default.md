[**Stock Screening Platform - Frontend API v0.1.0**](../../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../../modules.md) / [components/stock/PriceChart](../README.md) / default

# Function: default()

> **default**(`__namedParameters`): `Element`

Defined in: [src/components/stock/PriceChart.tsx:48](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/components/stock/PriceChart.tsx#L48)

Price Chart Component

Features:
- TradingView Lightweight Charts
- Candlestick chart
- Volume bars
- Timeframe selector
- Crosshair with price/date display
- Responsive design

## Parameters

### \_\_namedParameters

`PriceChartProps`

## Returns

`Element`

## Example

```tsx
const { data, isLoading, timeframe, setTimeframe } = usePriceChart('005930')

<PriceChart
  data={data}
  loading={isLoading}
  timeframe={timeframe}
  onTimeframeChange={setTimeframe}
/>
```
