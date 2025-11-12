[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [utils/format](../README.md) / formatPrice

# Function: formatPrice()

> **formatPrice**(`value`): `string`

Defined in: [src/utils/format.ts:39](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/utils/format.ts#L39)

Format price (stock price) with appropriate decimal places

## Parameters

### value

Price to format

`number` | `null` | `undefined`

## Returns

`string`

Formatted price string

## Example

```ts
formatPrice(55000) // "55,000"
formatPrice(1250.5) // "1,250.5"
```
