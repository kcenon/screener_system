[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [types/stock](../README.md) / OrderBookLevel

# Interface: OrderBookLevel

Defined in: [src/types/stock.ts:221](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/stock.ts#L221)

Single order book level (bid or ask)

## Properties

### price

> **price**: `number`

Defined in: [src/types/stock.ts:223](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/stock.ts#L223)

Price at this level

***

### volume

> **volume**: `number`

Defined in: [src/types/stock.ts:225](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/stock.ts#L225)

Volume at this price

***

### total

> **total**: `number`

Defined in: [src/types/stock.ts:227](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/stock.ts#L227)

Total (cumulative) volume up to this level

***

### order\_count?

> `optional` **order\_count**: `number`

Defined in: [src/types/stock.ts:229](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/stock.ts#L229)

Number of orders at this level (optional)
