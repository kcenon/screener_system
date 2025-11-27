/**
 * Stock screening types based on backend/app/schemas/screening.py
 */

/**
 * Range filter with min/max values
 */
export interface FilterRange {
  /** Minimum value (inclusive) */
  min?: number | null
  /** Maximum value (inclusive) */
  max?: number | null
}

/**
 * All available screening filters
 */
export interface ScreeningFilters {
  // Search filter
  /** Search by stock code or name */
  search?: string | null

  // Market filters
  /** Market filter */
  market?: 'KOSPI' | 'KOSDAQ' | 'ALL'
  /** Sector filter */
  sector?: string | null
  /** Industry filter */
  industry?: string | null

  // Valuation filters
  /** Price-to-Earnings Ratio */
  per?: FilterRange | null
  /** Price-to-Book Ratio */
  pbr?: FilterRange | null
  /** Price-to-Sales Ratio */
  psr?: FilterRange | null
  /** Price-to-Cash Flow Ratio */
  pcr?: FilterRange | null
  /** Dividend Yield (%) */
  dividend_yield?: FilterRange | null

  // Profitability filters
  /** Return on Equity (%) */
  roe?: FilterRange | null
  /** Return on Assets (%) */
  roa?: FilterRange | null
  /** Return on Invested Capital (%) */
  roic?: FilterRange | null
  /** Gross Margin (%) */
  gross_margin?: FilterRange | null
  /** Operating Margin (%) */
  operating_margin?: FilterRange | null
  /** Net Margin (%) */
  net_margin?: FilterRange | null

  // Growth filters
  /** Revenue Growth YoY (%) */
  revenue_growth_yoy?: FilterRange | null
  /** Profit Growth YoY (%) */
  profit_growth_yoy?: FilterRange | null
  /** EPS Growth YoY (%) */
  eps_growth_yoy?: FilterRange | null

  // Stability filters
  /** Debt-to-Equity Ratio */
  debt_to_equity?: FilterRange | null
  /** Current Ratio */
  current_ratio?: FilterRange | null
  /** Altman Z-Score (bankruptcy risk) */
  altman_z_score?: FilterRange | null
  /** Piotroski F-Score (0-9) */
  piotroski_f_score?: FilterRange | null

  // Price momentum filters
  /** 1-Day Price Change (%) */
  price_change_1d?: FilterRange | null
  /** 1-Week Price Change (%) */
  price_change_1w?: FilterRange | null
  /** 1-Month Price Change (%) */
  price_change_1m?: FilterRange | null
  /** 3-Month Price Change (%) */
  price_change_3m?: FilterRange | null
  /** 6-Month Price Change (%) */
  price_change_6m?: FilterRange | null
  /** 1-Year Price Change (%) */
  price_change_1y?: FilterRange | null

  // Volume filter
  /** Volume Surge (%) */
  volume_surge_pct?: FilterRange | null

  // Composite score filters
  /** Quality Score (0-100) */
  quality_score?: FilterRange | null
  /** Value Score (0-100) */
  value_score?: FilterRange | null
  /** Growth Score (0-100) */
  growth_score?: FilterRange | null
  /** Momentum Score (0-100) */
  momentum_score?: FilterRange | null
  /** Overall Score (0-100) */
  overall_score?: FilterRange | null

  // Price and market cap filters
  /** Current Price (KRW) */
  current_price?: FilterRange | null
  /** Market Capitalization (KRW billion) */
  market_cap?: FilterRange | null
}

/**
 * Sort order for screening results
 */
export type SortOrder = 'asc' | 'desc'

/**
 * Valid fields for sorting screening results
 */
export type ScreeningSortField =
  | 'code'
  | 'name'
  | 'market'
  | 'sector'
  | 'current_price'
  | 'market_cap'
  | 'per'
  | 'pbr'
  | 'psr'
  | 'dividend_yield'
  | 'roe'
  | 'roa'
  | 'roic'
  | 'gross_margin'
  | 'operating_margin'
  | 'net_margin'
  | 'revenue_growth_yoy'
  | 'profit_growth_yoy'
  | 'eps_growth_yoy'
  | 'debt_to_equity'
  | 'current_ratio'
  | 'altman_z_score'
  | 'piotroski_f_score'
  | 'price_change_1d'
  | 'price_change_1w'
  | 'price_change_1m'
  | 'price_change_3m'
  | 'price_change_6m'
  | 'price_change_1y'
  | 'volume_surge_pct'
  | 'quality_score'
  | 'value_score'
  | 'growth_score'
  | 'momentum_score'
  | 'overall_score'

/**
 * Single stock in screening results
 */
export interface StockScreeningResult {
  // Stock info
  code: string
  name: string
  name_english?: string | null
  market: string
  sector?: string | null
  industry?: string | null

  // Latest price
  last_trade_date?: string | null
  current_price?: number | null
  current_volume?: number | null
  market_cap?: number | null

  // Indicators (Optional - may be NULL for some stocks)
  indicators_date?: string | null
  per?: number | null
  pbr?: number | null
  psr?: number | null
  pcr?: number | null
  dividend_yield?: number | null
  roe?: number | null
  roa?: number | null
  roic?: number | null
  gross_margin?: number | null
  operating_margin?: number | null
  net_margin?: number | null
  revenue_growth_yoy?: number | null
  profit_growth_yoy?: number | null
  eps_growth_yoy?: number | null
  debt_to_equity?: number | null
  current_ratio?: number | null
  altman_z_score?: number | null
  piotroski_f_score?: number | null
  price_change_1d?: number | null
  price_change_1w?: number | null
  price_change_1m?: number | null
  price_change_3m?: number | null
  price_change_6m?: number | null
  price_change_1y?: number | null
  volume_surge_pct?: number | null
  average_volume?: number | null

  // 52-week range (for RangeIndicator)
  high_52w?: number | null
  low_52w?: number | null

  // Price history for sparklines (7 data points recommended)
  price_history_7d?: number[] | null

  quality_score?: number | null
  value_score?: number | null
  growth_score?: number | null
  momentum_score?: number | null
  overall_score?: number | null
}

/**
 * Screening response metadata
 */
export interface ScreeningMetadata {
  /** Total number of matching stocks */
  total: number
  /** Current page number */
  page: number
  /** Results per page */
  per_page: number
  /** Total number of pages */
  total_pages: number
}

/**
 * Stock screening response
 */
export interface ScreeningResponse {
  /** List of matching stocks */
  stocks: StockScreeningResult[]
  /** Pagination metadata */
  meta: ScreeningMetadata
  /** Query execution time (ms) */
  query_time_ms: number
  /** Applied filters summary */
  filters_applied: Record<string, unknown>
}

/**
 * Screening request parameters
 */
export interface ScreeningRequest {
  /** Screening filters */
  filters?: ScreeningFilters
  /** Field to sort by */
  sort_by?: ScreeningSortField
  /** Sort order */
  order?: SortOrder
  /** Page number (1-indexed) */
  page?: number
  /** Results per page */
  per_page?: number
}

/**
 * Predefined screening template
 */
export interface ScreeningTemplate {
  /** Template ID */
  id: string
  /** Template display name */
  name: string
  /** Template description */
  description: string
  /** Predefined filters */
  filters: ScreeningFilters
  /** Default sort field */
  sort_by: ScreeningSortField
  /** Default sort order */
  order: SortOrder
}

/**
 * List of available screening templates
 */
export interface ScreeningTemplateList {
  /** Available templates */
  templates: ScreeningTemplate[]
}
