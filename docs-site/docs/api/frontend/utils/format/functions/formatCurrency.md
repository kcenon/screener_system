[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [utils/format](../README.md) / formatCurrency

# Function: formatCurrency()

> **formatCurrency**(`value`, `compact`): `string`

Defined in: [src/utils/format.ts:69](https://github.com/kcenon/screener_system/blob/9a2d6f9db285c87b739af1754b1456d58585fb13/frontend/src/utils/format.ts#L69)

Format currency in KRW

## Parameters

### value

Amount in KRW

`number` | `null` | `undefined`

### compact

`boolean` = `false`

Use compact notation for large numbers (default: false)

## Returns

`string`

Formatted currency string

## Example

```ts
formatCurrency(1000000) // "₩1,000,000"
formatCurrency(1000000, true) // "₩1.0M"
```
