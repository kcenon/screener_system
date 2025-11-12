[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [utils/format](../README.md) / formatChange

# Function: formatChange()

> **formatChange**(`value`, `formatFn`): `object`

Defined in: [src/utils/format.ts:215](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/utils/format.ts#L215)

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
