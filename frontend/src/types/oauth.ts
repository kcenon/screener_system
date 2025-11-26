/**
 * OAuth types for social login integration
 */

export type OAuthProvider = 'google' | 'kakao' | 'naver'

export interface OAuthAuthorizationResponse {
  authorization_url: string
  state: string
  provider: OAuthProvider
}

export interface OAuthCallbackRequest {
  code: string
  state: string
}

export interface SocialAccount {
  id: number
  provider: string
  provider_email: string | null
  provider_name: string | null
  provider_picture: string | null
  created_at: string
  updated_at: string
}

export interface SocialAccountsListResponse {
  accounts: SocialAccount[]
  total: number
}

export interface OAuthUnlinkResponse {
  success: boolean
  message: string
  provider: string
}

export interface OAuthProvidersResponse {
  providers: OAuthProvider[]
  total: number
}
