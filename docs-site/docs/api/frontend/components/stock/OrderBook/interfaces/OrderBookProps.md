[**Stock Screening Platform - Frontend API v0.1.0**](../../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../../modules.md) / [components/stock/OrderBook](../README.md) / OrderBookProps

# Interface: OrderBookProps

Defined in: [src/components/stock/OrderBook.tsx:25](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/components/stock/OrderBook.tsx#L25)

OrderBook Component Props

## Properties

### data

> **data**: [`OrderBookData`](../../../../types/stock/interfaces/OrderBookData.md) \| `null`

Defined in: [src/components/stock/OrderBook.tsx:27](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/components/stock/OrderBook.tsx#L27)

Order book data

***

### imbalance

> **imbalance**: [`OrderImbalance`](../../../../types/stock/interfaces/OrderImbalance.md) \| `null`

Defined in: [src/components/stock/OrderBook.tsx:29](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/components/stock/OrderBook.tsx#L29)

Order imbalance indicator

***

### isLoading?

> `optional` **isLoading**: `boolean`

Defined in: [src/components/stock/OrderBook.tsx:31](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/components/stock/OrderBook.tsx#L31)

Loading state

***

### frozen?

> `optional` **frozen**: `boolean`

Defined in: [src/components/stock/OrderBook.tsx:33](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/components/stock/OrderBook.tsx#L33)

Frozen state (no updates)

***

### onToggleFreeze()?

> `optional` **onToggleFreeze**: () => `void`

Defined in: [src/components/stock/OrderBook.tsx:35](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/components/stock/OrderBook.tsx#L35)

Freeze toggle callback

#### Returns

`void`

***

### levels?

> `optional` **levels**: `number`

Defined in: [src/components/stock/OrderBook.tsx:37](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/components/stock/OrderBook.tsx#L37)

Number of levels to display (default: 10)

***

### detailed?

> `optional` **detailed**: `boolean`

Defined in: [src/components/stock/OrderBook.tsx:39](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/components/stock/OrderBook.tsx#L39)

Show detailed view

***

### mobile?

> `optional` **mobile**: `boolean`

Defined in: [src/components/stock/OrderBook.tsx:41](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/components/stock/OrderBook.tsx#L41)

Mobile view
