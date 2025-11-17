// Common types
export interface User {
  id: string
  email: string
  name: string
  tier: 'free' | 'basic' | 'premium'
  is_active: boolean
  created_at: string
}

// Authentication types
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface RefreshTokenRequest {
  refresh_token: string
}

// Email verification types
export interface EmailVerificationRequest {
  token: string
}

export interface VerificationStatusResponse {
  email_verified: boolean
  email_verified_at: string | null
  pending_tokens_count: number
  can_resend: boolean
}

// Password reset types
export interface PasswordResetRequest {
  email: string
}

export interface PasswordResetConfirm {
  token: string
  new_password: string
}

export interface SuccessResponse {
  message: string
}

export interface Stock {
  code: string
  name: string
  market: 'KOSPI' | 'KOSDAQ'
  sector: string
  listing_date: string
  delisting_date: string | null
  is_active: boolean
}

export interface DailyPrice {
  stock_code: string
  trade_date: string
  open_price: number
  high_price: number
  low_price: number
  close_price: number
  volume: number
  trading_value: number
  market_cap: number | null
}

export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface ApiError {
  detail: string
  status_code?: number
}

// Screening types
export * from './screening'

// Stock detail types
export * from './stock'

// Comparison types
export * from './comparison'

// Watchlist types
export * from './watchlist'

// Dashboard types
export * from './dashboard'
