[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [utils/format](../README.md) / formatNumber

# Function: formatNumber()

> **formatNumber**(`value`, `decimals`): `string`

Defined in: [src/utils/format.ts:18](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/utils/format.ts#L18)

Format number with thousand separators

## Parameters

### value

Number to format

`number` | `null` | `undefined`

### decimals

`number` = `0`

Number of decimal places (default: 0)

## Returns

`string`

Formatted string

## Example

```ts
formatNumber(1234567) // "1,234,567"
formatNumber(1234.567, 2) // "1,234.57"
```
