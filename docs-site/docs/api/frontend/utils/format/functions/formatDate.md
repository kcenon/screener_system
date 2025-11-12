[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [utils/format](../README.md) / formatDate

# Function: formatDate()

> **formatDate**(`date`, `format`): `string`

Defined in: [src/utils/format.ts:166](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/utils/format.ts#L166)

Format date

## Parameters

### date

Date string or Date object

`string` | `Date` | `null` | `undefined`

### format

Format type ('short', 'medium', 'long')

`"short"` | `"medium"` | `"long"`

## Returns

`string`

Formatted date string

## Example

```ts
formatDate('2024-01-15') // "2024-01-15"
formatDate('2024-01-15', 'medium') // "2024년 1월 15일"
```
