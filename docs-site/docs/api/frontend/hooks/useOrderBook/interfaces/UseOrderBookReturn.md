[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [hooks/useOrderBook](../README.md) / UseOrderBookReturn

# Interface: UseOrderBookReturn

Defined in: [src/hooks/useOrderBook.ts:20](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/hooks/useOrderBook.ts#L20)

Order book hook return type

## Properties

### orderBook

> **orderBook**: [`OrderBookData`](../../../types/stock/interfaces/OrderBookData.md) \| `null`

Defined in: [src/hooks/useOrderBook.ts:22](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/hooks/useOrderBook.ts#L22)

Current order book data

***

### imbalance

> **imbalance**: [`OrderImbalance`](../../../types/stock/interfaces/OrderImbalance.md) \| `null`

Defined in: [src/hooks/useOrderBook.ts:24](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/hooks/useOrderBook.ts#L24)

Order imbalance indicator

***

### connectionState

> **connectionState**: [`WSConnectionState`](../../../services/websocketService/type-aliases/WSConnectionState.md)

Defined in: [src/hooks/useOrderBook.ts:26](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/hooks/useOrderBook.ts#L26)

WebSocket connection state

***

### isLoading

> **isLoading**: `boolean`

Defined in: [src/hooks/useOrderBook.ts:28](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/hooks/useOrderBook.ts#L28)

Loading state

***

### error

> **error**: `string` \| `null`

Defined in: [src/hooks/useOrderBook.ts:30](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/hooks/useOrderBook.ts#L30)

Error state

***

### refresh()

> **refresh**: () => `void`

Defined in: [src/hooks/useOrderBook.ts:32](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/hooks/useOrderBook.ts#L32)

Manually refresh order book

#### Returns

`void`

***

### frozen

> **frozen**: `boolean`

Defined in: [src/hooks/useOrderBook.ts:34](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/hooks/useOrderBook.ts#L34)

Freeze/unfreeze updates

***

### toggleFreeze()

> **toggleFreeze**: () => `void`

Defined in: [src/hooks/useOrderBook.ts:36](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/hooks/useOrderBook.ts#L36)

Toggle freeze state

#### Returns

`void`
