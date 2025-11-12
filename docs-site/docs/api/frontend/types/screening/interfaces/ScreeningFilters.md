[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [types/screening](../README.md) / ScreeningFilters

# Interface: ScreeningFilters

Defined in: [src/types/screening.ts:18](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L18)

All available screening filters

## Properties

### search?

> `optional` **search**: `string` \| `null`

Defined in: [src/types/screening.ts:21](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L21)

Search by stock code or name

***

### market?

> `optional` **market**: `"KOSPI"` \| `"KOSDAQ"` \| `"ALL"`

Defined in: [src/types/screening.ts:25](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L25)

Market filter

***

### sector?

> `optional` **sector**: `string` \| `null`

Defined in: [src/types/screening.ts:27](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L27)

Sector filter

***

### industry?

> `optional` **industry**: `string` \| `null`

Defined in: [src/types/screening.ts:29](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L29)

Industry filter

***

### per?

> `optional` **per**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:33](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L33)

Price-to-Earnings Ratio

***

### pbr?

> `optional` **pbr**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:35](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L35)

Price-to-Book Ratio

***

### psr?

> `optional` **psr**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:37](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L37)

Price-to-Sales Ratio

***

### pcr?

> `optional` **pcr**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:39](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L39)

Price-to-Cash Flow Ratio

***

### dividend\_yield?

> `optional` **dividend\_yield**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:41](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L41)

Dividend Yield (%)

***

### roe?

> `optional` **roe**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:45](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L45)

Return on Equity (%)

***

### roa?

> `optional` **roa**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:47](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L47)

Return on Assets (%)

***

### roic?

> `optional` **roic**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:49](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L49)

Return on Invested Capital (%)

***

### gross\_margin?

> `optional` **gross\_margin**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:51](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L51)

Gross Margin (%)

***

### operating\_margin?

> `optional` **operating\_margin**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:53](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L53)

Operating Margin (%)

***

### net\_margin?

> `optional` **net\_margin**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:55](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L55)

Net Margin (%)

***

### revenue\_growth\_yoy?

> `optional` **revenue\_growth\_yoy**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:59](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L59)

Revenue Growth YoY (%)

***

### profit\_growth\_yoy?

> `optional` **profit\_growth\_yoy**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:61](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L61)

Profit Growth YoY (%)

***

### eps\_growth\_yoy?

> `optional` **eps\_growth\_yoy**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:63](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L63)

EPS Growth YoY (%)

***

### debt\_to\_equity?

> `optional` **debt\_to\_equity**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:67](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L67)

Debt-to-Equity Ratio

***

### current\_ratio?

> `optional` **current\_ratio**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:69](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L69)

Current Ratio

***

### altman\_z\_score?

> `optional` **altman\_z\_score**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:71](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L71)

Altman Z-Score (bankruptcy risk)

***

### piotroski\_f\_score?

> `optional` **piotroski\_f\_score**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:73](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L73)

Piotroski F-Score (0-9)

***

### price\_change\_1d?

> `optional` **price\_change\_1d**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:77](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L77)

1-Day Price Change (%)

***

### price\_change\_1w?

> `optional` **price\_change\_1w**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:79](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L79)

1-Week Price Change (%)

***

### price\_change\_1m?

> `optional` **price\_change\_1m**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:81](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L81)

1-Month Price Change (%)

***

### price\_change\_3m?

> `optional` **price\_change\_3m**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:83](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L83)

3-Month Price Change (%)

***

### price\_change\_6m?

> `optional` **price\_change\_6m**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:85](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L85)

6-Month Price Change (%)

***

### price\_change\_1y?

> `optional` **price\_change\_1y**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:87](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L87)

1-Year Price Change (%)

***

### volume\_surge\_pct?

> `optional` **volume\_surge\_pct**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:91](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L91)

Volume Surge (%)

***

### quality\_score?

> `optional` **quality\_score**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:95](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L95)

Quality Score (0-100)

***

### value\_score?

> `optional` **value\_score**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:97](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L97)

Value Score (0-100)

***

### growth\_score?

> `optional` **growth\_score**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:99](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L99)

Growth Score (0-100)

***

### momentum\_score?

> `optional` **momentum\_score**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:101](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L101)

Momentum Score (0-100)

***

### overall\_score?

> `optional` **overall\_score**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:103](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L103)

Overall Score (0-100)

***

### current\_price?

> `optional` **current\_price**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:107](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L107)

Current Price (KRW)

***

### market\_cap?

> `optional` **market\_cap**: [`FilterRange`](FilterRange.md) \| `null`

Defined in: [src/types/screening.ts:109](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L109)

Market Capitalization (KRW billion)
