[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [types/stock](../README.md) / FinancialStatement

# Interface: FinancialStatement

Defined in: [src/types/stock.ts:68](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L68)

Single financial statement entry

## Properties

### period

> **period**: `string`

Defined in: [src/types/stock.ts:70](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L70)

Period (e.g., '2023-Q4', '2023-Y')

***

### period\_type

> **period\_type**: [`FinancialPeriod`](../type-aliases/FinancialPeriod.md)

Defined in: [src/types/stock.ts:72](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L72)

Period type (quarterly or yearly)

***

### fiscal\_year

> **fiscal\_year**: `number`

Defined in: [src/types/stock.ts:74](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L74)

Fiscal year

***

### fiscal\_quarter?

> `optional` **fiscal\_quarter**: `number` \| `null`

Defined in: [src/types/stock.ts:76](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L76)

Fiscal quarter (1-4, null for yearly)

***

### revenue?

> `optional` **revenue**: `number` \| `null`

Defined in: [src/types/stock.ts:80](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L80)

Total revenue (KRW)

***

### operating\_profit?

> `optional` **operating\_profit**: `number` \| `null`

Defined in: [src/types/stock.ts:82](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L82)

Operating profit (KRW)

***

### net\_profit?

> `optional` **net\_profit**: `number` \| `null`

Defined in: [src/types/stock.ts:84](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L84)

Net profit (KRW)

***

### gross\_margin?

> `optional` **gross\_margin**: `number` \| `null`

Defined in: [src/types/stock.ts:86](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L86)

Gross margin (%)

***

### operating\_margin?

> `optional` **operating\_margin**: `number` \| `null`

Defined in: [src/types/stock.ts:88](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L88)

Operating margin (%)

***

### net\_margin?

> `optional` **net\_margin**: `number` \| `null`

Defined in: [src/types/stock.ts:90](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L90)

Net margin (%)

***

### total\_assets?

> `optional` **total\_assets**: `number` \| `null`

Defined in: [src/types/stock.ts:94](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L94)

Total assets (KRW)

***

### total\_liabilities?

> `optional` **total\_liabilities**: `number` \| `null`

Defined in: [src/types/stock.ts:96](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L96)

Total liabilities (KRW)

***

### total\_equity?

> `optional` **total\_equity**: `number` \| `null`

Defined in: [src/types/stock.ts:98](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L98)

Total equity (KRW)

***

### current\_assets?

> `optional` **current\_assets**: `number` \| `null`

Defined in: [src/types/stock.ts:100](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L100)

Current assets (KRW)

***

### current\_liabilities?

> `optional` **current\_liabilities**: `number` \| `null`

Defined in: [src/types/stock.ts:102](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L102)

Current liabilities (KRW)

***

### operating\_cash\_flow?

> `optional` **operating\_cash\_flow**: `number` \| `null`

Defined in: [src/types/stock.ts:106](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L106)

Operating cash flow (KRW)

***

### investing\_cash\_flow?

> `optional` **investing\_cash\_flow**: `number` \| `null`

Defined in: [src/types/stock.ts:108](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L108)

Investing cash flow (KRW)

***

### financing\_cash\_flow?

> `optional` **financing\_cash\_flow**: `number` \| `null`

Defined in: [src/types/stock.ts:110](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L110)

Financing cash flow (KRW)

***

### free\_cash\_flow?

> `optional` **free\_cash\_flow**: `number` \| `null`

Defined in: [src/types/stock.ts:112](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L112)

Free cash flow (KRW)

***

### eps?

> `optional` **eps**: `number` \| `null`

Defined in: [src/types/stock.ts:116](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L116)

Earnings per share (KRW)

***

### bps?

> `optional` **bps**: `number` \| `null`

Defined in: [src/types/stock.ts:118](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L118)

Book value per share (KRW)

***

### dps?

> `optional` **dps**: `number` \| `null`

Defined in: [src/types/stock.ts:120](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L120)

Dividend per share (KRW)

***

### shares\_outstanding?

> `optional` **shares\_outstanding**: `number` \| `null`

Defined in: [src/types/stock.ts:124](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/types/stock.ts#L124)

Outstanding shares
