// Common types
export interface User {
  id: string
  email: string
  username: string
  is_active: boolean
  created_at: string
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
