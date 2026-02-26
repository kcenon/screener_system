/**
 * HTTP Client Configuration and Interceptors.
 *
 * Provides a pre-configured Axios instance with automatic JWT token management,
 * request/response interceptors, and token refresh logic. Handles authentication
 * errors gracefully with automatic retry and request queueing.
 *
 * @module services/api
 * @category Services
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

/**
 * Base URL for all API requests.
 *
 * Determined by VITE_API_BASE_URL environment variable or falls back
 * to localhost development server.
 *
 * @constant
 * @defaultValue 'http://localhost:8000/v1'
 */
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/v1'

/**
 * Pre-configured Axios instance for API communication.
 *
 * Features:
 * - Automatic JWT token injection via request interceptor
 * - Automatic token refresh on 401 responses
 * - Request queueing during token refresh
 * - 10-second timeout for all requests
 * - JSON content type by default
 *
 * @example
 * Basic GET request
 * ```typescript
 * import { api } from '@/services/api';
 *
 * const response = await api.get('/stocks');
 * console.log(response.data);
 * ```
 *
 * @example
 * POST request with data
 * ```typescript
 * const response = await api.post('/auth/login', {
 *   username: 'user',
 *   password: 'pass'
 * });
 * ```
 *
 * @see {@link https://axios-http.com/docs/instance} Axios Instance Documentation
 *
 * @category Services
 */
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Flag indicating if token refresh is currently in progress.
 *
 * Prevents multiple concurrent token refresh attempts when
 * multiple requests receive 401 responses simultaneously.
 *
 * @internal
 */
let isRefreshing = false

/**
 * Queue of pending requests waiting for token refresh to complete.
 *
 * When a 401 response triggers token refresh, subsequent failing requests
 * are queued here and retried once new tokens are obtained.
 *
 * @internal
 */
let failedQueue: Array<{
  resolve: (value?: unknown) => void
  reject: (reason?: unknown) => void
}> = []

/**
 * Processes queued requests after token refresh completes.
 *
 * Resolves or rejects all queued requests based on token refresh outcome.
 * On success, queued requests are retried with new token. On failure, all
 * are rejected and user is logged out.
 *
 * @param error - Error from token refresh attempt, null if successful
 * @param token - New access token if refresh succeeded, null otherwise
 *
 * @internal
 */
const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })

  failedQueue = []
}

// Request interceptor for adding auth token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  },
)

// Response interceptor for handling errors and token refresh
api.interceptors.response.use(
  response => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    // If error is not 401 or request already retried, reject immediately
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error)
    }

    // Don't retry for auth endpoints
    if (originalRequest.url?.includes('/auth/')) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    if (isRefreshing) {
      // If token is being refreshed, queue this request
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      })
        .then(token => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`
          }
          return api(originalRequest)
        })
        .catch(err => {
          return Promise.reject(err)
        })
    }

    originalRequest._retry = true
    isRefreshing = true

    const refreshToken = localStorage.getItem('refresh_token')

    if (!refreshToken) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    try {
      // Attempt to refresh the token
      const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
        refresh_token: refreshToken,
      })

      const { access_token, refresh_token: newRefreshToken } = response.data

      // Store new tokens
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', newRefreshToken)

      // Update Authorization header
      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${access_token}`
      }

      // Process queued requests
      processQueue(null, access_token)

      // Retry original request
      return api(originalRequest)
    } catch (refreshError) {
      // Refresh failed, logout user
      processQueue(refreshError as Error, null)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  },
)
