/**
 * Dashboard Types
 *
 * Type definitions for the user dashboard feature, including market summary,
 * user activity, and dashboard widgets.
 */

import { WatchlistStock } from './watchlist'

/**
 * Market index information
 */
export interface MarketIndex {
  /** Index code (e.g., 'KOSPI', 'KOSDAQ', 'KRX100') */
  code: string

  /** Index name */
  name: string

  /** Current index value */
  current: number

  /** Absolute change from previous close */
  change: number

  /** Percentage change from previous close */
  change_percent: number

  /** Today's high */
  high: number

  /** Today's low */
  low: number

  /** Trading volume */
  volume: number

  /** Timestamp of the data */
  timestamp: string

  /** Historical sparkline data (last 30 data points) */
  sparkline?: number[]
}

/**
 * Market breadth indicators
 */
export interface MarketBreadth {
  /** Number of advancing stocks */
  advancing: number

  /** Number of declining stocks */
  declining: number

  /** Number of unchanged stocks */
  unchanged: number

  /** Advance/Decline ratio */
  ad_ratio: number

  /** Market sentiment */
  sentiment: 'bullish' | 'neutral' | 'bearish'

  /** Timestamp of the data */
  timestamp: string
}

/**
 * User activity log entry
 */
export interface UserActivity {
  /** Activity ID */
  id: string

  /** Activity type */
  activity_type:
    | 'screening'
    | 'watchlist_create'
    | 'watchlist_update'
    | 'watchlist_delete'
    | 'stock_add'
    | 'stock_remove'
    | 'stock_view'
    | 'login'
    | 'logout'

  /** Activity description */
  description: string

  /** Additional metadata about the activity */
  activity_metadata?: Record<string, unknown>

  /** Timestamp when activity occurred */
  created_at: string
}

/**
 * Recent activity response
 */
export interface RecentActivityResponse {
  /** List of activities */
  activities: UserActivity[]

  /** Total number of activities */
  total: number

  /** Current page */
  page: number

  /** Items per page */
  limit: number
}

/**
 * Watchlist summary for dashboard
 */
export interface WatchlistSummary {
  /** Watchlist ID */
  id: string

  /** Watchlist name */
  name: string

  /** Optional description */
  description?: string

  /** Number of stocks in watchlist */
  stock_count: number

  /** Last stock added timestamp */
  last_stock_added?: string | null

  /** Creation timestamp */
  created_at: string

  /** Last update timestamp */
  updated_at: string
}

/**
 * Watchlist with stocks for dashboard display
 */
export interface DashboardWatchlist {
  /** Watchlist ID */
  id: string

  /** Watchlist name */
  name: string

  /** Stocks in the watchlist */
  stocks: WatchlistStock[]

  /** Watchlist statistics */
  stats: {
    /** Total number of stocks */
    total: number

    /** Number of gainers */
    gainers: number

    /** Number of losers */
    losers: number

    /** Average change percentage */
    avg_change: number
  }
}

/**
 * Dashboard summary data
 */
export interface DashboardSummary {
  /** Market indices */
  market_indices: {
    /** KOSPI index */
    kospi: MarketIndex

    /** KOSDAQ index */
    kosdaq: MarketIndex
  }

  /** Market breadth indicators */
  market_breadth: MarketBreadth

  /** User's watchlists summary */
  watchlists: WatchlistSummary[]

  /** Recent user activities */
  recent_activities: UserActivity[]

  /** Platform usage statistics */
  user_stats: {
    /** Number of screenings this month */
    screening_count: number

    /** Total stocks in all watchlists */
    total_watchlist_stocks: number

    /** Last login timestamp */
    last_login?: string
  }
}

/**
 * Quick action item
 */
export interface QuickAction {
  /** Action ID */
  id: string

  /** Action title */
  title: string

  /** Action description */
  description: string

  /** Icon name (Lucide icon) */
  icon: string

  /** Link to navigate to */
  href: string

  /** Action category */
  category: 'screening' | 'watchlist' | 'analysis' | 'reports'
}
