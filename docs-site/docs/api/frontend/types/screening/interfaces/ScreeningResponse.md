[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [types/screening](../README.md) / ScreeningResponse

# Interface: ScreeningResponse

Defined in: [src/types/screening.ts:226](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/screening.ts#L226)

Stock screening response

## Properties

### stocks

> **stocks**: [`StockScreeningResult`](StockScreeningResult.md)[]

Defined in: [src/types/screening.ts:228](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/screening.ts#L228)

List of matching stocks

***

### meta

> **meta**: [`ScreeningMetadata`](ScreeningMetadata.md)

Defined in: [src/types/screening.ts:230](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/screening.ts#L230)

Pagination metadata

***

### query\_time\_ms

> **query\_time\_ms**: `number`

Defined in: [src/types/screening.ts:232](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/screening.ts#L232)

Query execution time (ms)

***

### filters\_applied

> **filters\_applied**: `Record`\<`string`, `unknown`\>

Defined in: [src/types/screening.ts:234](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/screening.ts#L234)

Applied filters summary
