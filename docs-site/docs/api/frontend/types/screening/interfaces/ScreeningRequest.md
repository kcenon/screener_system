[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [types/screening](../README.md) / ScreeningRequest

# Interface: ScreeningRequest

Defined in: [src/types/screening.ts:240](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L240)

Screening request parameters

## Properties

### filters?

> `optional` **filters**: [`ScreeningFilters`](ScreeningFilters.md)

Defined in: [src/types/screening.ts:242](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L242)

Screening filters

***

### sort\_by?

> `optional` **sort\_by**: [`ScreeningSortField`](../type-aliases/ScreeningSortField.md)

Defined in: [src/types/screening.ts:244](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L244)

Field to sort by

***

### order?

> `optional` **order**: [`SortOrder`](../type-aliases/SortOrder.md)

Defined in: [src/types/screening.ts:246](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L246)

Sort order

***

### page?

> `optional` **page**: `number`

Defined in: [src/types/screening.ts:248](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L248)

Page number (1-indexed)

***

### per\_page?

> `optional` **per\_page**: `number`

Defined in: [src/types/screening.ts:250](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/types/screening.ts#L250)

Results per page
