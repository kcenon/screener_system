import { api } from './api'
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  RefreshTokenRequest,
  User,
  EmailVerificationRequest,
  VerificationStatusResponse,
  PasswordResetRequest,
  PasswordResetConfirm,
  SuccessResponse,
} from '../types'

/**
 * Authentication service for managing user authentication operations
 */
class AuthService {
  private readonly AUTH_BASE_URL = '/auth'

  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>(`${this.AUTH_BASE_URL}/register`, data)
    return response.data
  }

  /**
   * Login with email and password
   */
  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>(`${this.AUTH_BASE_URL}/login`, data)
    return response.data
  }

  /**
   * Logout from current session
   */
  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (refreshToken) {
      try {
        await api.post(`${this.AUTH_BASE_URL}/logout`, { refresh_token: refreshToken })
      } catch (error) {
        // Ignore errors during logout
        console.error('Logout error:', error)
      }
    }
    this.clearTokens()
  }

  /**
   * Logout from all sessions
   */
  async logoutAll(): Promise<void> {
    try {
      await api.post(`${this.AUTH_BASE_URL}/logout-all`)
    } catch (error) {
      console.error('Logout all error:', error)
    }
    this.clearTokens()
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshToken(data: RefreshTokenRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>(`${this.AUTH_BASE_URL}/refresh`, data)
    return response.data
  }

  /**
   * Get current authenticated user
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>(`${this.AUTH_BASE_URL}/me`)
    return response.data
  }

  /**
   * Store tokens in localStorage
   */
  storeTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)
  }

  /**
   * Clear all stored tokens
   */
  clearTokens(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  /**
   * Get stored access token
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token')
  }

  /**
   * Get stored refresh token
   */
  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token')
  }

  /**
   * Check if user is authenticated (has access token)
   */
  isAuthenticated(): boolean {
    return !!this.getAccessToken()
  }

  /**
   * Verify email address with verification token
   */
  async verifyEmail(data: EmailVerificationRequest): Promise<SuccessResponse> {
    const response = await api.post<SuccessResponse>(
      `${this.AUTH_BASE_URL}/verify-email`,
      data
    )
    return response.data
  }

  /**
   * Resend verification email to current user
   */
  async resendVerificationEmail(): Promise<SuccessResponse> {
    const response = await api.post<SuccessResponse>(
      `${this.AUTH_BASE_URL}/resend-verification`
    )
    return response.data
  }

  /**
   * Get email verification status for current user
   */
  async getVerificationStatus(): Promise<VerificationStatusResponse> {
    const response = await api.get<VerificationStatusResponse>(
      `${this.AUTH_BASE_URL}/verification-status`
    )
    return response.data
  }

  /**
   * Request password reset for email address
   */
  async requestPasswordReset(data: PasswordResetRequest): Promise<SuccessResponse> {
    const response = await api.post<SuccessResponse>(
      `${this.AUTH_BASE_URL}/forgot-password`,
      data
    )
    return response.data
  }

  /**
   * Validate password reset token
   */
  async validateResetToken(token: string): Promise<SuccessResponse> {
    const response = await api.get<SuccessResponse>(
      `${this.AUTH_BASE_URL}/validate-reset-token`,
      { params: { token } }
    )
    return response.data
  }

  /**
   * Reset password with token and new password
   */
  async resetPassword(data: PasswordResetConfirm): Promise<SuccessResponse> {
    const response = await api.post<SuccessResponse>(
      `${this.AUTH_BASE_URL}/reset-password`,
      data
    )
    // Clear tokens after password reset (user is logged out)
    this.clearTokens()
    return response.data
  }
}

export const authService = new AuthService()
