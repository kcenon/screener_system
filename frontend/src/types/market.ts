/**
 * Market Overview types for MarketOverviewPage (FE-009)
 *
 * Types for market indices, sector performance, market breadth,
 * top movers, and market trend data.
 */

/**
 * Market index code
 */
export type MarketIndexCode = 'KOSPI' | 'KOSDAQ' | 'KRX100'

/**
 * Market index data
 */
export interface MarketIndex {
  /** Index code */
  code: MarketIndexCode
  /** Index name */
  name: string
  /** Current index value */
  current: number
  /** Absolute change from previous close */
  change: number
  /** Percentage change from previous close */
  change_percent: number
  /** Day high */
  high: number
  /** Day low */
  low: number
  /** Total trading volume */
  volume: number
  /** Total trading value (KRW) */
  value?: number
  /** Timestamp of the data */
  timestamp: string
  /** Sparkline data (last 30 data points) */
  sparkline: number[]
}

/**
 * Market indices response
 */
export interface MarketIndicesResponse {
  /** Array of market indices */
  indices: MarketIndex[]
  /** Last update timestamp */
  updated_at: string
}

/**
 * Market type filter
 */
export type MarketType = 'ALL' | 'KOSPI' | 'KOSDAQ'

/**
 * Market sentiment
 */
export type MarketSentiment = 'bullish' | 'neutral' | 'bearish'

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
  /** Total number of stocks */
  total: number
  /** Advance/Decline ratio */
  ad_ratio: number
  /** Market sentiment indicator */
  sentiment: MarketSentiment
  /** Market type (ALL, KOSPI, KOSDAQ) */
  market: MarketType
  /** Timestamp of the data */
  timestamp: string
}

/**
 * Sector code
 */
export type SectorCode =
  | 'technology'
  | 'finance'
  | 'healthcare'
  | 'consumer'
  | 'materials'
  | 'industrial'
  | 'energy'
  | 'utilities'
  | 'telecom'
  | 'real_estate'

/**
 * Sector performance data
 */
export interface SectorPerformance {
  /** Sector code */
  code: SectorCode
  /** Sector name (Korean) */
  name: string
  /** Percentage change */
  change_percent: number
  /** Total market cap of sector (KRW) */
  market_cap: number
  /** Number of stocks in sector */
  stock_count: number
  /** Advancing stocks count */
  advancing?: number
  /** Declining stocks count */
  declining?: number
  /** Average volume (shares) */
  avg_volume?: number
}

/**
 * Sectors performance response
 */
export interface SectorsPerformanceResponse {
  /** Array of sector performances */
  sectors: SectorPerformance[]
  /** Timeframe for performance calculation */
  timeframe: '1D' | '1W' | '1M' | '3M'
  /** Last update timestamp */
  updated_at: string
}

/**
 * Market mover (top gainer/loser)
 */
export interface MarketMover {
  /** Stock code */
  code: string
  /** Stock name (Korean) */
  name: string
  /** Market (KOSPI or KOSDAQ) */
  market: 'KOSPI' | 'KOSDAQ'
  /** Current price (KRW) */
  current_price: number
  /** Percentage change */
  change_percent: number
  /** Absolute change (KRW) */
  change?: number
  /** Trading volume */
  volume: number
  /** Trading value (KRW) */
  value?: number
  /** Market cap (KRW) */
  market_cap?: number
}

/**
 * Market movers response
 */
export interface MarketMoversResponse {
  /** Top gaining stocks */
  gainers: MarketMover[]
  /** Top losing stocks */
  losers: MarketMover[]
  /** Market filter applied */
  market: MarketType
  /** Number of results per category */
  limit: number
  /** Last update timestamp */
  updated_at: string
}

/**
 * Most active stock (by volume)
 */
export interface MostActiveStock {
  /** Stock code */
  code: string
  /** Stock name (Korean) */
  name: string
  /** Market (KOSPI or KOSDAQ) */
  market: 'KOSPI' | 'KOSDAQ'
  /** Current price (KRW) */
  current_price: number
  /** Percentage change */
  change_percent: number
  /** Absolute change (KRW) */
  change?: number
  /** Trading volume */
  volume: number
  /** Trading value (KRW) */
  value: number
  /** Volume change from average (%) */
  volume_change_pct?: number
}

/**
 * Most active stocks response
 */
export interface MostActiveResponse {
  /** Array of most active stocks */
  stocks: MostActiveStock[]
  /** Market filter applied */
  market: MarketType
  /** Number of results */
  limit: number
  /** Last update timestamp */
  updated_at: string
}

/**
 * Historical market trend timeframe
 */
export type TrendTimeframe = '1D' | '5D' | '1M' | '3M' | '6M' | '1Y'

/**
 * Single data point in market trend
 */
export interface TrendDataPoint {
  /** Trading date (ISO 8601) */
  date: string
  /** Index value */
  value: number
  /** Volume (optional) */
  volume?: number
}

/**
 * Market trend data for a single index
 */
export interface MarketTrendData {
  /** Index code */
  code: MarketIndexCode
  /** Index name */
  name: string
  /** Array of trend data points */
  data: TrendDataPoint[]
  /** Start date */
  from_date: string
  /** End date */
  to_date: string
  /** Timeframe */
  timeframe: TrendTimeframe
}

/**
 * Market trend response (multiple indices)
 */
export interface MarketTrendResponse {
  /** Array of market trend data for different indices */
  trends: MarketTrendData[]
  /** Timeframe for all trends */
  timeframe: TrendTimeframe
  /** Last update timestamp */
  updated_at: string
}

/**
 * Timeframe options for UI
 */
export interface TimeframeOption {
  /** Display label */
  label: string
  /** API value */
  value: TrendTimeframe
  /** Number of days (for calculation) */
  days?: number
}

/**
 * Available timeframe options
 */
export const TREND_TIMEFRAMES: TimeframeOption[] = [
  { label: '1D', value: '1D', days: 1 },
  { label: '5D', value: '5D', days: 5 },
  { label: '1M', value: '1M', days: 30 },
  { label: '3M', value: '3M', days: 90 },
  { label: '6M', value: '6M', days: 180 },
  { label: '1Y', value: '1Y', days: 365 },
]

/**
 * Market overview page state
 */
export interface MarketOverviewState {
  /** Selected market filter for breadth */
  selectedMarket: MarketType
  /** Selected timeframe for sector performance */
  selectedSectorTimeframe: '1D' | '1W' | '1M' | '3M'
  /** Selected timeframe for market trend */
  selectedTrendTimeframe: TrendTimeframe
  /** Auto-refresh enabled */
  autoRefresh: boolean
  /** Last refresh timestamp */
  lastRefresh?: string
}
