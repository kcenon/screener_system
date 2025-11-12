[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [types/stock](../README.md) / OrderImbalance

# Interface: OrderImbalance

Defined in: [src/types/stock.ts:271](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L271)

Order imbalance indicator

## Properties

### total\_bid\_volume

> **total\_bid\_volume**: `number`

Defined in: [src/types/stock.ts:273](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L273)

Total bid volume

***

### total\_ask\_volume

> **total\_ask\_volume**: `number`

Defined in: [src/types/stock.ts:275](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L275)

Total ask volume

***

### imbalance\_ratio

> **imbalance\_ratio**: `number`

Defined in: [src/types/stock.ts:277](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L277)

Imbalance ratio (bid / (bid + ask))

***

### direction

> **direction**: `"buy"` \| `"sell"` \| `"neutral"`

Defined in: [src/types/stock.ts:279](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L279)

Direction ('buy' if more bids, 'sell' if more asks, 'neutral' if balanced)
