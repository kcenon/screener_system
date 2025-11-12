[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [types/stock](../README.md) / PriceCandle

# Interface: PriceCandle

Defined in: [src/types/stock.ts:15](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L15)

Single candle in price history

## Properties

### date

> **date**: `string`

Defined in: [src/types/stock.ts:17](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L17)

Trading date (ISO 8601)

***

### open

> **open**: `number`

Defined in: [src/types/stock.ts:19](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L19)

Opening price

***

### high

> **high**: `number`

Defined in: [src/types/stock.ts:21](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L21)

Highest price

***

### low

> **low**: `number`

Defined in: [src/types/stock.ts:23](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L23)

Lowest price

***

### close

> **close**: `number`

Defined in: [src/types/stock.ts:25](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L25)

Closing price

***

### volume

> **volume**: `number`

Defined in: [src/types/stock.ts:27](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L27)

Trading volume

***

### change\_pct?

> `optional` **change\_pct**: `number`

Defined in: [src/types/stock.ts:29](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/types/stock.ts#L29)

Price change from previous close (%)
