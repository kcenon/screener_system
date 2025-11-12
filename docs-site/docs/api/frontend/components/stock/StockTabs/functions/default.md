[**Stock Screening Platform - Frontend API v0.1.0**](../../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../../modules.md) / [components/stock/StockTabs](../README.md) / default

# Function: default()

> **default**(`__namedParameters`): `Element`

Defined in: [src/components/stock/StockTabs.tsx:32](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/components/stock/StockTabs.tsx#L32)

Stock Tabs Component

Tab-based navigation for stock detail content:
- Overview: Key metrics, scores, company info
- Financials: Income statement, balance sheet, cash flow
- Valuation: Valuation ratios and historical trends
- Technical: Price momentum, volume analysis, moving averages
- OrderBook: Real-time 10-level order book (FE-005)

## Parameters

### \_\_namedParameters

`StockTabsProps`

## Returns

`Element`

## Example

```tsx
<StockTabs stock={stockData} />
```
