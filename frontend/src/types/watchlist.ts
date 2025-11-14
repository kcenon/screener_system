/**
 * Watchlist Management Types
 *
 * Type definitions for the watchlist feature, including watchlist entities,
 * stocks within watchlists, and related DTOs for API operations.
 */

/**
 * Represents a single stock within a watchlist
 */
export interface WatchlistStock {
  /** Stock code (e.g., '005930' for Samsung) */
  code: string

  /** Company name */
  name: string

  /** Market classification */
  market: 'KOSPI' | 'KOSDAQ'

  /** Current stock price */
  current_price: number

  /** Price change percentage (e.g., 1.5 for +1.5%) */
  change_percent: number

  /** Trading volume */
  volume: number

  /** Timestamp when stock was added to watchlist */
  added_at: string

  /** Market capitalization (optional) */
  market_cap?: number

  /** 52-week high price (optional) */
  week_52_high?: number

  /** 52-week low price (optional) */
  week_52_low?: number
}

/**
 * Main watchlist entity
 */
export interface Watchlist {
  /** Unique watchlist identifier */
  id: string

  /** Watchlist name (e.g., "My Favorites", "Tech Stocks") */
  name: string

  /** Optional description */
  description?: string

  /** User ID who owns this watchlist */
  user_id: string

  /** Array of stocks in this watchlist */
  stocks: WatchlistStock[]

  /** Creation timestamp */
  created_at: string

  /** Last update timestamp */
  updated_at: string

  /** Optional icon/emoji for visual identification */
  icon?: string

  /** Optional color tag for organization */
  color?: string
}

/**
 * DTO for creating a new watchlist
 */
export interface CreateWatchlistDto {
  /** Watchlist name (required) */
  name: string

  /** Optional description */
  description?: string

  /** Optional icon */
  icon?: string

  /** Optional color */
  color?: string
}

/**
 * DTO for updating an existing watchlist
 */
export interface UpdateWatchlistDto {
  /** New name (optional) */
  name?: string

  /** New description (optional) */
  description?: string

  /** New icon (optional) */
  icon?: string

  /** New color (optional) */
  color?: string
}

/**
 * DTO for adding a stock to a watchlist
 */
export interface AddStockDto {
  /** Stock code to add */
  stock_code: string
}

/**
 * Sort options for watchlist stocks
 */
export type WatchlistSortField =
  | 'name'
  | 'code'
  | 'price'
  | 'change_percent'
  | 'volume'
  | 'market_cap'
  | 'added_at'

/**
 * Sort direction
 */
export type SortDirection = 'asc' | 'desc'

/**
 * Watchlist sort configuration
 */
export interface WatchlistSort {
  field: WatchlistSortField
  direction: SortDirection
}

/**
 * Filter options for watchlist stocks
 */
export interface WatchlistFilter {
  /** Filter by market */
  market?: 'KOSPI' | 'KOSDAQ'

  /** Search query (matches code or name) */
  search?: string

  /** Minimum price change percentage */
  min_change?: number

  /** Maximum price change percentage */
  max_change?: number
}

/**
 * Watchlist statistics
 */
export interface WatchlistStats {
  /** Total number of stocks */
  total_stocks: number

  /** Number of stocks with positive change */
  gainers: number

  /** Number of stocks with negative change */
  losers: number

  /** Number of unchanged stocks */
  unchanged: number

  /** Average change percentage across all stocks */
  avg_change: number

  /** Total market cap of all stocks (if available) */
  total_market_cap?: number
}

/**
 * Error type for watchlist operations
 */
export interface WatchlistError {
  /** Error code */
  code: 'NOT_FOUND' | 'DUPLICATE' | 'LIMIT_EXCEEDED' | 'INVALID_INPUT' | 'SERVER_ERROR'

  /** Human-readable error message */
  message: string

  /** Additional error details */
  details?: Record<string, unknown>
}
