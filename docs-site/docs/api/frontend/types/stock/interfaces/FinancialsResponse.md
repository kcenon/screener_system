[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [types/stock](../README.md) / FinancialsResponse

# Interface: FinancialsResponse

Defined in: [src/types/stock.ts:130](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/stock.ts#L130)

Financial statements response

## Properties

### stock\_code

> **stock\_code**: `string`

Defined in: [src/types/stock.ts:132](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/stock.ts#L132)

Stock code

***

### period\_type

> **period\_type**: [`FinancialPeriod`](../type-aliases/FinancialPeriod.md)

Defined in: [src/types/stock.ts:134](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/stock.ts#L134)

Period type (Q or Y)

***

### years

> **years**: `number`

Defined in: [src/types/stock.ts:136](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/stock.ts#L136)

Number of periods

***

### statements

> **statements**: [`FinancialStatement`](FinancialStatement.md)[]

Defined in: [src/types/stock.ts:138](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/types/stock.ts#L138)

Array of financial statements
