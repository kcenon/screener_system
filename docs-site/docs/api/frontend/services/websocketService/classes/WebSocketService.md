[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [services/websocketService](../README.md) / WebSocketService

# Class: WebSocketService

Defined in: [src/services/websocketService.ts:125](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/services/websocketService.ts#L125)

WebSocket Service Class

Manages WebSocket connection lifecycle and subscriptions

## Constructors

### Constructor

> **new WebSocketService**(`config`): `WebSocketService`

Defined in: [src/services/websocketService.ts:137](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/services/websocketService.ts#L137)

#### Parameters

##### config

`WSServiceConfig`

#### Returns

`WebSocketService`

## Methods

### connect()

> **connect**(): `void`

Defined in: [src/services/websocketService.ts:151](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/services/websocketService.ts#L151)

Connect to WebSocket server

#### Returns

`void`

***

### disconnect()

> **disconnect**(): `void`

Defined in: [src/services/websocketService.ts:185](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/services/websocketService.ts#L185)

Disconnect from WebSocket server

#### Returns

`void`

***

### subscribe()

> **subscribe**(`type`, `identifier`): `void`

Defined in: [src/services/websocketService.ts:201](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/services/websocketService.ts#L201)

Subscribe to stock updates

#### Parameters

##### type

[`SubscriptionType`](../type-aliases/SubscriptionType.md)

##### identifier

`string`

#### Returns

`void`

***

### unsubscribe()

> **unsubscribe**(`type`, `identifier`): `void`

Defined in: [src/services/websocketService.ts:223](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/services/websocketService.ts#L223)

Unsubscribe from stock updates

#### Parameters

##### type

[`SubscriptionType`](../type-aliases/SubscriptionType.md)

##### identifier

`string`

#### Returns

`void`

***

### onMessage()

> **onMessage**(`handler`): () => `void`

Defined in: [src/services/websocketService.ts:245](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/services/websocketService.ts#L245)

Add message handler

#### Parameters

##### handler

`MessageHandler`

#### Returns

> (): `void`

##### Returns

`void`

***

### onStateChange()

> **onStateChange**(`handler`): () => `void`

Defined in: [src/services/websocketService.ts:257](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/services/websocketService.ts#L257)

Add state change handler

#### Parameters

##### handler

`StateChangeHandler`

#### Returns

> (): `void`

##### Returns

`void`

***

### getState()

> **getState**(): [`WSConnectionState`](../type-aliases/WSConnectionState.md)

Defined in: [src/services/websocketService.ts:269](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/services/websocketService.ts#L269)

Get current connection state

#### Returns

[`WSConnectionState`](../type-aliases/WSConnectionState.md)

***

### isConnected()

> **isConnected**(): `boolean`

Defined in: [src/services/websocketService.ts:276](https://github.com/kcenon/screener_system/blob/4c55f6de748e382859e70b16429f6387e4cb3ab4/frontend/src/services/websocketService.ts#L276)

Check if connected

#### Returns

`boolean`
