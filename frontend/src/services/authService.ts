import { api } from './api'
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
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
    const response = await api.post<TokenResponse>(
      `${this.AUTH_BASE_URL}/register`,
      data,
    )
    return response.data
  }

  /**
   * Login with email and password
   */
  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>(
      `${this.AUTH_BASE_URL}/login`,
      data,
    )
    return response.data
  }

  /**
   * Logout from current session
   */
  async logout(): Promise<void> {
    try {
      // No body needed — refresh_token cookie is sent automatically
      await api.post(`${this.AUTH_BASE_URL}/logout`)
    } catch (error) {
      // Ignore errors during logout — cookies will be cleared by backend
      console.error('Logout error:', error)
    }
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
  }

  /**
   * Refresh access token using refresh token cookie
   */
  async refreshToken(): Promise<TokenResponse> {
    // No body needed — refresh_token HttpOnly cookie is sent automatically
    const response = await api.post<TokenResponse>(
      `${this.AUTH_BASE_URL}/refresh`,
      null,
    )
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
   * Verify email address with verification token
   */
  async verifyEmail(data: EmailVerificationRequest): Promise<SuccessResponse> {
    const response = await api.post<SuccessResponse>(
      `${this.AUTH_BASE_URL}/verify-email`,
      data,
    )
    return response.data
  }

  /**
   * Resend verification email to current user
   */
  async resendVerificationEmail(): Promise<SuccessResponse> {
    const response = await api.post<SuccessResponse>(
      `${this.AUTH_BASE_URL}/resend-verification`,
    )
    return response.data
  }

  /**
   * Get email verification status for current user
   */
  async getVerificationStatus(): Promise<VerificationStatusResponse> {
    const response = await api.get<VerificationStatusResponse>(
      `${this.AUTH_BASE_URL}/verification-status`,
    )
    return response.data
  }

  /**
   * Request password reset for email address
   */
  async requestPasswordReset(
    data: PasswordResetRequest,
  ): Promise<SuccessResponse> {
    const response = await api.post<SuccessResponse>(
      `${this.AUTH_BASE_URL}/forgot-password`,
      data,
    )
    return response.data
  }

  /**
   * Validate password reset token
   */
  async validateResetToken(token: string): Promise<SuccessResponse> {
    const response = await api.get<SuccessResponse>(
      `${this.AUTH_BASE_URL}/validate-reset-token`,
      { params: { token } },
    )
    return response.data
  }

  /**
   * Reset password with token and new password
   */
  async resetPassword(data: PasswordResetConfirm): Promise<SuccessResponse> {
    const response = await api.post<SuccessResponse>(
      `${this.AUTH_BASE_URL}/reset-password`,
      data,
    )
    return response.data
  }
}

export const authService = new AuthService()
