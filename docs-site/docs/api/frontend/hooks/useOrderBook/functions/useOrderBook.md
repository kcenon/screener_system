[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [hooks/useOrderBook](../README.md) / useOrderBook

# Function: useOrderBook()

> **useOrderBook**(`stockCode`, `enabled`): [`UseOrderBookReturn`](../interfaces/UseOrderBookReturn.md)

Defined in: [src/hooks/useOrderBook.ts:114](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/hooks/useOrderBook.ts#L114)

Order Book Hook

## Parameters

### stockCode

Stock code to subscribe to (e.g., '005930')

`string` | `undefined`

### enabled

`boolean` = `true`

Whether to enable the hook (default: true)

## Returns

[`UseOrderBookReturn`](../interfaces/UseOrderBookReturn.md)

Order book data and controls

## Example

```tsx
const { orderBook, imbalance, connectionState, frozen, toggleFreeze } = useOrderBook('005930')

if (connectionState !== 'connected') {
  return <div>Connecting...</div>
}

return (
  <div>
    <button onClick={toggleFreeze}>{frozen ? 'Unfreeze' : 'Freeze'}</button>
    <OrderBook data={orderBook} imbalance={imbalance} />
  </div>
)
```
