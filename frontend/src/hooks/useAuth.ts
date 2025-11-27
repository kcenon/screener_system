import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { authService } from '@/services/authService'
import { useAuthStore } from '@/store/authStore'
import { analytics, AnalyticsEvents } from '@/services/analytics'
import type { LoginRequest, RegisterRequest } from '@/types'

/**
 * Hook for user login
 */
export function useLogin() {
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)

  return useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),
    onSuccess: (response) => {
      // Track successful login
      analytics.identify(String(response.user.id), {
        email: response.user.email,
        tier: (response.user.tier as 'free' | 'premium' | 'pro') || 'free',
        email_verified: response.user.email_verified,
      })
      analytics.track(AnalyticsEvents.USER_LOGGED_IN, {
        login_method: 'email',
      })

      login(response.user, response.access_token, response.refresh_token)
      navigate('/')
    },
    onError: (error) => {
      analytics.track(AnalyticsEvents.ERROR_OCCURRED, {
        error_type: 'login_failed',
        error_message: error.message || 'Login failed',
        component: 'LoginPage',
      })
    },
  })
}

/**
 * Hook for user registration
 */
export function useRegister() {
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)

  return useMutation({
    mutationFn: (data: RegisterRequest) => authService.register(data),
    onSuccess: (response) => {
      // Track successful signup
      analytics.identify(String(response.user.id), {
        email: response.user.email,
        tier: 'free',
        created_at: new Date().toISOString(),
      })
      analytics.track(AnalyticsEvents.USER_SIGNED_UP, {
        signup_source: 'email',
      })

      login(response.user, response.access_token, response.refresh_token)
      navigate('/')
    },
    onError: (error) => {
      analytics.track(AnalyticsEvents.ERROR_OCCURRED, {
        error_type: 'signup_failed',
        error_message: error.message || 'Signup failed',
        component: 'RegisterPage',
      })
    },
  })
}

/**
 * Hook for user logout
 */
export function useLogout() {
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      // Track logout
      analytics.track(AnalyticsEvents.USER_LOGGED_OUT)
      analytics.reset()

      logout()
      queryClient.clear()
      navigate('/login')
    },
  })
}

/**
 * Hook for logout from all sessions
 */
export function useLogoutAll() {
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => authService.logoutAll(),
    onSuccess: () => {
      logout()
      queryClient.clear()
      navigate('/login')
    },
  })
}

/**
 * Hook for fetching current user
 */
export function useCurrentUser() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const setUser = useAuthStore((state) => state.setUser)

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const user = await authService.getCurrentUser()
      setUser(user)
      return user
    },
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

/**
 * Hook for refreshing access token
 */
export function useRefreshToken() {
  const refreshToken = useAuthStore((state) => state.refreshToken)
  const updateTokens = useAuthStore((state) => state.updateTokens)
  const logout = useAuthStore((state) => state.logout)

  return useMutation({
    mutationFn: () => {
      if (!refreshToken) {
        throw new Error('No refresh token available')
      }
      return authService.refreshToken({ refresh_token: refreshToken })
    },
    onSuccess: (response) => {
      updateTokens(response.access_token, response.refresh_token)
    },
    onError: () => {
      // If refresh fails, logout user
      logout()
    },
  })
}

/**
 * Hook for getting auth status
 */
export function useAuthStatus() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const user = useAuthStore((state) => state.user)

  return {
    isAuthenticated,
    user,
  }
}
