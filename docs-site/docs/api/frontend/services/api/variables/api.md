[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [services/api](../README.md) / api

# Variable: api

> `const` **api**: `AxiosInstance`

Defined in: [src/services/api.ts:57](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/services/api.ts#L57)

Pre-configured Axios instance for API communication.

Features:
- Automatic JWT token injection via request interceptor
- Automatic token refresh on 401 responses
- Request queueing during token refresh
- 10-second timeout for all requests
- JSON content type by default

## Examples

Basic GET request
```typescript
import { api } from '@/services/api';

const response = await api.get('/stocks');
console.log(response.data);
```

POST request with data
```typescript
const response = await api.post('/auth/login', {
  username: 'user',
  password: 'pass'
});
```

## See

[https://axios-http.com/docs/instance](https://axios-http.com/docs/instance) Axios Instance Documentation
