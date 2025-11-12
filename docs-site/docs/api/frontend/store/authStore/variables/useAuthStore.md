[**Stock Screening Platform - Frontend API v0.1.0**](../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../modules.md) / [store/authStore](../README.md) / useAuthStore

# Variable: useAuthStore

> `const` **useAuthStore**: `UseBoundStore`\<`WithPersist`\<`StoreApi`\<`AuthState`\>, `AuthState`\>\>

Defined in: [src/store/authStore.ts:159](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/store/authStore.ts#L159)

Global authentication store hook.

Provides access to authentication state and actions throughout the application.
Uses Zustand for simple, performant state management with automatic persistence.

## Features

- **Persistent Storage**: Auth state persists across page refreshes
- **Token Management**: Automatic token storage and retrieval
- **Type Safety**: Full TypeScript support
- **Reactive Updates**: Components re-render on auth state changes

## Examples

Access auth state
```typescript
const { user, isAuthenticated } = useAuthStore();

if (!isAuthenticated) {
  return <Navigate to="/login" />;
}

return <div>Welcome, {user.username}!</div>;
```

Use auth actions
```typescript
const { login, logout } = useAuthStore();

const handleLogin = async (email, password) => {
  const response = await authService.login(email, password);
  login(response.user, response.access_token, response.refresh_token);
};
```

Selective subscription (performance optimization)
```typescript
// Only re-render when isAuthenticated changes
const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
```

## Returns

Authentication store state and actions

## See

 - [User](../../../types/interfaces/User.md) for user profile structure
 - [authService](../../../services/authService/variables/authService.md) for authentication API calls
