/**
 * Stock detail types for StockDetailPage (FE-004)
 */

import type { StockScreeningResult } from './screening'

/**
 * Time intervals for price history
 */
export type PriceInterval =
  | '1D'
  | '1W'
  | '1M'
  | '3M'
  | '6M'
  | '1Y'
  | '3Y'
  | '5Y'
  | 'ALL'

/**
 * Single candle in price history
 */
export interface PriceCandle {
  /** Trading date (ISO 8601) */
  date: string
  /** Opening price */
  open: number
  /** Highest price */
  high: number
  /** Lowest price */
  low: number
  /** Closing price */
  close: number
  /** Trading volume */
  volume: number
  /** Price change from previous close (%) */
  change_pct?: number
}

/**
 * Price history response
 */
export interface PriceHistoryResponse {
  /** Stock code */
  stock_code: string
  /** Array of price candles */
  candles: PriceCandle[]
  /** Start date */
  from_date: string
  /** End date */
  to_date: string
  /** Interval type */
  interval: string
  /** Number of candles */
  count: number
}

/**
 * Moving average data point
 */
export interface MovingAverage {
  /** Date */
  date: string
  /** MA value */
  value: number
}

/**
 * Financial period type
 */
export type FinancialPeriod = 'Q' | 'Y'

/**
 * Single financial statement entry
 */
export interface FinancialStatement {
  /** Period (e.g., '2023-Q4', '2023-Y') */
  period: string
  /** Period type (quarterly or yearly) */
  period_type: FinancialPeriod
  /** Fiscal year */
  fiscal_year: number
  /** Fiscal quarter (1-4, null for yearly) */
  fiscal_quarter?: number | null

  // Income Statement
  /** Total revenue (KRW) */
  revenue?: number | null
  /** Operating profit (KRW) */
  operating_profit?: number | null
  /** Net profit (KRW) */
  net_profit?: number | null
  /** Gross margin (%) */
  gross_margin?: number | null
  /** Operating margin (%) */
  operating_margin?: number | null
  /** Net margin (%) */
  net_margin?: number | null

  // Balance Sheet
  /** Total assets (KRW) */
  total_assets?: number | null
  /** Total liabilities (KRW) */
  total_liabilities?: number | null
  /** Total equity (KRW) */
  total_equity?: number | null
  /** Current assets (KRW) */
  current_assets?: number | null
  /** Current liabilities (KRW) */
  current_liabilities?: number | null

  // Cash Flow
  /** Operating cash flow (KRW) */
  operating_cash_flow?: number | null
  /** Investing cash flow (KRW) */
  investing_cash_flow?: number | null
  /** Financing cash flow (KRW) */
  financing_cash_flow?: number | null
  /** Free cash flow (KRW) */
  free_cash_flow?: number | null

  // Per Share
  /** Earnings per share (KRW) */
  eps?: number | null
  /** Book value per share (KRW) */
  bps?: number | null
  /** Dividend per share (KRW) */
  dps?: number | null

  // Shares
  /** Outstanding shares */
  shares_outstanding?: number | null
}

/**
 * Financial statements response
 */
export interface FinancialsResponse {
  /** Stock code */
  stock_code: string
  /** Period type (Q or Y) */
  period_type: FinancialPeriod
  /** Number of periods */
  years: number
  /** Array of financial statements */
  statements: FinancialStatement[]
}

/**
 * Stock detail metadata
 */
export interface StockMetadata {
  /** Company full name */
  company_name?: string
  /** English name */
  name_english?: string | null
  /** Website URL */
  website?: string | null
  /** Listing date (ISO 8601) */
  listing_date?: string | null
  /** CEO name */
  ceo?: string | null
  /** Employee count */
  employees?: number | null
  /** Description/business summary */
  description?: string | null
}

/**
 * Extended stock detail
 * Combines screening result with metadata
 */
export interface StockDetail extends StockScreeningResult {
  /** Additional metadata */
  metadata?: StockMetadata
}

/**
 * Tab identifiers for stock detail page
 */
export type StockTab = 'overview' | 'financials' | 'valuation' | 'technical'

/**
 * Chart timeframe for price chart
 */
export interface ChartTimeframe {
  /** Display label */
  label: string
  /** Value for API */
  value: PriceInterval
  /** Number of days to fetch */
  days?: number
}

/**
 * Common chart timeframes
 */
export const CHART_TIMEFRAMES: ChartTimeframe[] = [
  { label: '1D', value: '1D', days: 1 },
  { label: '1W', value: '1W', days: 7 },
  { label: '1M', value: '1M', days: 30 },
  { label: '3M', value: '3M', days: 90 },
  { label: '6M', value: '6M', days: 180 },
  { label: '1Y', value: '1Y', days: 365 },
  { label: '3Y', value: '3Y', days: 1095 },
  { label: '5Y', value: '5Y', days: 1825 },
  { label: 'ALL', value: 'ALL' },
]

/**
 * Price change statistics
 */
export interface PriceChange {
  /** Change value (absolute) */
  value: number
  /** Change percentage */
  percentage: number
  /** Is positive change */
  is_positive: boolean
}

/**
 * Order Book Types (FE-005)
 */

/**
 * Single order book level (bid or ask)
 */
export interface OrderBookLevel {
  /** Price at this level */
  price: number
  /** Volume at this price */
  volume: number
  /** Total (cumulative) volume up to this level */
  total: number
  /** Number of orders at this level (optional) */
  order_count?: number
}

/**
 * Complete order book data
 */
export interface OrderBookData {
  /** Stock code */
  stock_code: string
  /** Timestamp of the order book snapshot (ISO 8601) */
  timestamp: string
  /** Sequence number for ordering updates */
  sequence?: number
  /** Array of ask levels (매도, sell orders) - sorted from lowest to highest */
  asks: OrderBookLevel[]
  /** Array of bid levels (매수, buy orders) - sorted from highest to lowest */
  bids: OrderBookLevel[]
  /** Best ask price (lowest sell price) */
  best_ask?: number
  /** Best bid price (highest buy price) */
  best_bid?: number
  /** Spread (best_ask - best_bid) */
  spread?: number
  /** Spread percentage ((spread / mid_price) * 100) */
  spread_pct?: number
  /** Mid price ((best_ask + best_bid) / 2) */
  mid_price?: number
}

/**
 * Order book update message from WebSocket
 */
export interface OrderBookUpdate {
  /** Message type */
  type: 'orderbook_update'
  /** Order book data */
  data: OrderBookData
}

/**
 * Order imbalance indicator
 */
export interface OrderImbalance {
  /** Total bid volume */
  total_bid_volume: number
  /** Total ask volume */
  total_ask_volume: number
  /** Imbalance ratio (bid / (bid + ask)) */
  imbalance_ratio: number
  /** Direction ('buy' if more bids, 'sell' if more asks, 'neutral' if balanced) */
  direction: 'buy' | 'sell' | 'neutral'
}
