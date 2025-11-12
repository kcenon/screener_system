[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [types/stock](../README.md) / OrderBookUpdate

# Interface: OrderBookUpdate

Defined in: [src/types/stock.ts:261](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L261)

Order book update message from WebSocket

## Properties

### type

> **type**: `"orderbook_update"`

Defined in: [src/types/stock.ts:263](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L263)

Message type

***

### data

> **data**: [`OrderBookData`](OrderBookData.md)

Defined in: [src/types/stock.ts:265](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L265)

Order book data
