/**
 * OAuth service for social login integration
 */

import { api } from './api'
import { authService } from './authService'
import type {
  OAuthAuthorizationResponse,
  OAuthCallbackRequest,
  SocialAccount,
  SocialAccountsListResponse,
  OAuthUnlinkResponse,
  OAuthProvidersResponse,
  OAuthProvider,
  TokenResponse,
} from '../types'

/**
 * OAuth service for managing social login operations
 */
class OAuthService {
  private readonly OAUTH_BASE_URL = '/auth/oauth'

  /**
   * Get OAuth authorization URL for login/signup
   */
  async getAuthorizationUrl(
    provider: OAuthProvider,
    redirectUrl?: string
  ): Promise<OAuthAuthorizationResponse> {
    const params = new URLSearchParams()
    if (redirectUrl) {
      params.append('redirect_url', redirectUrl)
    }

    const response = await api.get<OAuthAuthorizationResponse>(
      `${this.OAUTH_BASE_URL}/${provider}/login`,
      { params }
    )
    return response.data
  }

  /**
   * Handle OAuth callback (exchange code for tokens)
   */
  async handleCallback(
    provider: OAuthProvider,
    code: string,
    state: string
  ): Promise<TokenResponse> {
    const response = await api.get<TokenResponse>(
      `${this.OAUTH_BASE_URL}/${provider}/callback`,
      { params: { code, state } }
    )

    // Store tokens
    const { access_token, refresh_token } = response.data
    authService.storeTokens(access_token, refresh_token)

    return response.data
  }

  /**
   * Get OAuth authorization URL for linking account
   */
  async getLinkUrl(
    provider: OAuthProvider,
    redirectUrl?: string
  ): Promise<OAuthAuthorizationResponse> {
    const params = new URLSearchParams()
    if (redirectUrl) {
      params.append('redirect_url', redirectUrl)
    }

    const response = await api.get<OAuthAuthorizationResponse>(
      `${this.OAUTH_BASE_URL}/${provider}/link`,
      { params }
    )
    return response.data
  }

  /**
   * Link social account to current user
   */
  async linkAccount(
    provider: OAuthProvider,
    data: OAuthCallbackRequest
  ): Promise<SocialAccount> {
    const response = await api.post<SocialAccount>(
      `${this.OAUTH_BASE_URL}/${provider}/link`,
      data
    )
    return response.data
  }

  /**
   * Unlink social account from current user
   */
  async unlinkAccount(provider: OAuthProvider): Promise<OAuthUnlinkResponse> {
    const response = await api.delete<OAuthUnlinkResponse>(
      `${this.OAUTH_BASE_URL}/${provider}/unlink`
    )
    return response.data
  }

  /**
   * Get all linked social accounts for current user
   */
  async getLinkedAccounts(): Promise<SocialAccountsListResponse> {
    const response = await api.get<SocialAccountsListResponse>(
      `${this.OAUTH_BASE_URL}/accounts`
    )
    return response.data
  }

  /**
   * Get list of available OAuth providers
   */
  async getAvailableProviders(): Promise<OAuthProvidersResponse> {
    const response = await api.get<OAuthProvidersResponse>(
      `${this.OAUTH_BASE_URL}/providers`
    )
    return response.data
  }

  /**
   * Initiate OAuth login flow by redirecting to provider
   */
  async initiateLogin(provider: OAuthProvider): Promise<void> {
    const { authorization_url } = await this.getAuthorizationUrl(provider)
    window.location.href = authorization_url
  }

  /**
   * Initiate OAuth account linking flow by redirecting to provider
   */
  async initiateLink(provider: OAuthProvider): Promise<void> {
    const { authorization_url } = await this.getLinkUrl(provider)
    window.location.href = authorization_url
  }
}

export const oauthService = new OAuthService()
