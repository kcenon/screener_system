[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [utils/format](../README.md) / formatPercentage

# Function: formatPercentage()

> **formatPercentage**(`value`, `decimals`, `asDecimal`, `showSign`): `string`

Defined in: [src/utils/format.ts:103](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/utils/format.ts#L103)

Format percentage

## Parameters

### value

Percentage value (0-100 or 0-1 based on asDecimal)

`number` | `null` | `undefined`

### decimals

`number` = `2`

Number of decimal places (default: 2)

### asDecimal

`boolean` = `false`

Whether input is decimal (0-1) vs percentage (0-100) (default: false)

### showSign

`boolean` = `true`

Show + sign for positive values (default: true)

## Returns

`string`

Formatted percentage string

## Example

```ts
formatPercentage(12.34) // "+12.34%"
formatPercentage(-5.67) // "-5.67%"
formatPercentage(0.1234, 2, true) // "+12.34%"
```
