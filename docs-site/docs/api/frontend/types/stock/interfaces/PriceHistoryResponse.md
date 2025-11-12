[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [types/stock](../README.md) / PriceHistoryResponse

# Interface: PriceHistoryResponse

Defined in: [src/types/stock.ts:35](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L35)

Price history response

## Properties

### stock\_code

> **stock\_code**: `string`

Defined in: [src/types/stock.ts:37](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L37)

Stock code

***

### candles

> **candles**: [`PriceCandle`](PriceCandle.md)[]

Defined in: [src/types/stock.ts:39](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L39)

Array of price candles

***

### from\_date

> **from\_date**: `string`

Defined in: [src/types/stock.ts:41](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L41)

Start date

***

### to\_date

> **to\_date**: `string`

Defined in: [src/types/stock.ts:43](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L43)

End date

***

### interval

> **interval**: `string`

Defined in: [src/types/stock.ts:45](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L45)

Interval type

***

### count

> **count**: `number`

Defined in: [src/types/stock.ts:47](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L47)

Number of candles
