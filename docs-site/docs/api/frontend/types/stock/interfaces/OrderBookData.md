[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [types/stock](../README.md) / OrderBookData

# Interface: OrderBookData

Defined in: [src/types/stock.ts:235](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L235)

Complete order book data

## Properties

### stock\_code

> **stock\_code**: `string`

Defined in: [src/types/stock.ts:237](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L237)

Stock code

***

### timestamp

> **timestamp**: `string`

Defined in: [src/types/stock.ts:239](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L239)

Timestamp of the order book snapshot (ISO 8601)

***

### sequence?

> `optional` **sequence**: `number`

Defined in: [src/types/stock.ts:241](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L241)

Sequence number for ordering updates

***

### asks

> **asks**: [`OrderBookLevel`](OrderBookLevel.md)[]

Defined in: [src/types/stock.ts:243](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L243)

Array of ask levels (매도, sell orders) - sorted from lowest to highest

***

### bids

> **bids**: [`OrderBookLevel`](OrderBookLevel.md)[]

Defined in: [src/types/stock.ts:245](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L245)

Array of bid levels (매수, buy orders) - sorted from highest to lowest

***

### best\_ask?

> `optional` **best\_ask**: `number`

Defined in: [src/types/stock.ts:247](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L247)

Best ask price (lowest sell price)

***

### best\_bid?

> `optional` **best\_bid**: `number`

Defined in: [src/types/stock.ts:249](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L249)

Best bid price (highest buy price)

***

### spread?

> `optional` **spread**: `number`

Defined in: [src/types/stock.ts:251](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L251)

Spread (best_ask - best_bid)

***

### spread\_pct?

> `optional` **spread\_pct**: `number`

Defined in: [src/types/stock.ts:253](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L253)

Spread percentage ((spread / mid_price) * 100)

***

### mid\_price?

> `optional` **mid\_price**: `number`

Defined in: [src/types/stock.ts:255](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L255)

Mid price ((best_ask + best_bid) / 2)
