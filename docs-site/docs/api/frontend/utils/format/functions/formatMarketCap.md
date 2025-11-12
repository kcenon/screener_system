[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [utils/format](../README.md) / formatMarketCap

# Function: formatMarketCap()

> **formatMarketCap**(`value`): `string`

Defined in: [src/utils/format.ts:129](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/utils/format.ts#L129)

Format market cap in Korean units (억원, 조원)

## Parameters

### value

Market cap in KRW

`number` | `null` | `undefined`

## Returns

`string`

Formatted market cap string

## Example

```ts
formatMarketCap(1234567890000) // "1.23조원"
formatMarketCap(123456789000) // "1,235억원"
```
