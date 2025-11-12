[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [utils/format](../README.md) / formatChange

# Function: formatChange()

> **formatChange**(`value`, `formatFn`): `object`

Defined in: [src/utils/format.ts:215](https://github.com/kcenon/screener_system/blob/d044d1d2aa4ff785068489ad5946f0ac8c432792/frontend/src/utils/format.ts#L215)

Format change value with color indicator

## Parameters

### value

Change value

`number` | `null` | `undefined`

### formatFn

(`v`) => `string`

Formatting function to apply (default: formatNumber)

## Returns

`object`

Object with formatted value and color class

### text

> **text**: `string`

### className

> **className**: `string`

## Example

```ts
const { text, className } = formatChange(1234)
// { text: "+1,234", className: "text-red-600" }
```
