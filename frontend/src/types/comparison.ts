/**
 * Stock Comparison Types for FE-010
 */

import type { StockDetail } from './stock'

/**
 * Comparison metric metadata
 */
export interface ComparisonMetric {
  /** Unique metric identifier */
  key: string
  /** Display label */
  label: string
  /** Category */
  category:
    | 'fundamental'
    | 'valuation'
    | 'financial_health'
    | 'profitability'
    | 'technical'
    | 'performance'
  /** Format type */
  format: 'currency' | 'percent' | 'number' | 'ratio'
  /** Whether higher value is better for highlighting */
  higher_is_better: boolean
  /** Tooltip description */
  description: string
}

/**
 * Stock data for comparison
 */
export interface ComparisonStock extends StockDetail {
  /** Loading state */
  isLoading?: boolean
  /** Error state */
  error?: string | null
}

/**
 * Comparison view mode
 */
export type ComparisonView = 'table' | 'charts'

/**
 * Chart type for comparison visualization
 */
export type ComparisonChartType = 'radar' | 'bar' | 'performance'

/**
 * Metric highlight type
 */
export type MetricHighlight = 'best' | 'worst' | 'neutral'

/**
 * Performance timeframe
 */
export type PerformanceTimeframe =
  | '1D'
  | '1W'
  | '1M'
  | '3M'
  | '6M'
  | '1Y'
  | '3Y'

/**
 * Comparison state
 */
export interface ComparisonState {
  /** Selected stock codes */
  stockCodes: string[]
  /** View mode */
  view: ComparisonView
  /** Selected chart type */
  chartType: ComparisonChartType
  /** Performance timeframe */
  timeframe: PerformanceTimeframe
}

/**
 * Maximum number of stocks allowed for comparison
 */
export const MAX_COMPARISON_STOCKS = 5

/**
 * Comparison metrics configuration
 */
export const COMPARISON_METRICS: ComparisonMetric[] = [
  // Fundamentals
  {
    key: 'market_cap',
    label: 'Market Cap',
    category: 'fundamental',
    format: 'currency',
    higher_is_better: true,
    description: 'Total market capitalization of the company',
  },
  {
    key: 'current_price',
    label: 'Current Price',
    category: 'fundamental',
    format: 'currency',
    higher_is_better: false,
    description: 'Current stock price',
  },
  {
    key: 'volume',
    label: 'Volume',
    category: 'fundamental',
    format: 'number',
    higher_is_better: false,
    description: 'Trading volume',
  },

  // Valuation
  {
    key: 'per',
    label: 'P/E Ratio',
    category: 'valuation',
    format: 'ratio',
    higher_is_better: false,
    description:
      'Price-to-Earnings Ratio - lower is generally better for value',
  },
  {
    key: 'pbr',
    label: 'P/B Ratio',
    category: 'valuation',
    format: 'ratio',
    higher_is_better: false,
    description: 'Price-to-Book Ratio - lower indicates undervaluation',
  },
  {
    key: 'psr',
    label: 'P/S Ratio',
    category: 'valuation',
    format: 'ratio',
    higher_is_better: false,
    description: 'Price-to-Sales Ratio',
  },
  {
    key: 'pcr',
    label: 'P/CF Ratio',
    category: 'valuation',
    format: 'ratio',
    higher_is_better: false,
    description: 'Price-to-Cash Flow Ratio',
  },
  {
    key: 'dividend_yield',
    label: 'Dividend Yield',
    category: 'valuation',
    format: 'percent',
    higher_is_better: true,
    description: 'Dividend yield percentage',
  },

  // Profitability
  {
    key: 'roe',
    label: 'ROE',
    category: 'profitability',
    format: 'percent',
    higher_is_better: true,
    description: 'Return on Equity - higher is better',
  },
  {
    key: 'roa',
    label: 'ROA',
    category: 'profitability',
    format: 'percent',
    higher_is_better: true,
    description: 'Return on Assets',
  },
  {
    key: 'roic',
    label: 'ROIC',
    category: 'profitability',
    format: 'percent',
    higher_is_better: true,
    description: 'Return on Invested Capital',
  },
  {
    key: 'gross_margin',
    label: 'Gross Margin',
    category: 'profitability',
    format: 'percent',
    higher_is_better: true,
    description: 'Gross profit margin',
  },
  {
    key: 'operating_margin',
    label: 'Operating Margin',
    category: 'profitability',
    format: 'percent',
    higher_is_better: true,
    description: 'Operating profit margin',
  },
  {
    key: 'net_margin',
    label: 'Net Margin',
    category: 'profitability',
    format: 'percent',
    higher_is_better: true,
    description: 'Net profit margin',
  },

  // Financial Health
  {
    key: 'debt_ratio',
    label: 'Debt Ratio',
    category: 'financial_health',
    format: 'percent',
    higher_is_better: false,
    description: 'Total debt to total assets - lower is better',
  },
  {
    key: 'current_ratio',
    label: 'Current Ratio',
    category: 'financial_health',
    format: 'ratio',
    higher_is_better: true,
    description: 'Current assets to current liabilities - higher is better',
  },
  {
    key: 'quick_ratio',
    label: 'Quick Ratio',
    category: 'financial_health',
    format: 'ratio',
    higher_is_better: true,
    description: 'Quick assets to current liabilities',
  },

  // Technical
  {
    key: 'rsi',
    label: 'RSI (14)',
    category: 'technical',
    format: 'number',
    higher_is_better: false,
    description: 'Relative Strength Index - 30-70 is neutral range',
  },
  {
    key: 'macd',
    label: 'MACD',
    category: 'technical',
    format: 'number',
    higher_is_better: true,
    description: 'Moving Average Convergence Divergence',
  },
  {
    key: 'ma_20',
    label: '20-Day MA',
    category: 'technical',
    format: 'currency',
    higher_is_better: false,
    description: '20-day moving average',
  },
  {
    key: 'ma_50',
    label: '50-Day MA',
    category: 'technical',
    format: 'currency',
    higher_is_better: false,
    description: '50-day moving average',
  },
  {
    key: 'ma_200',
    label: '200-Day MA',
    category: 'technical',
    format: 'currency',
    higher_is_better: false,
    description: '200-day moving average',
  },

  // Performance
  {
    key: 'change_1d',
    label: '1-Day Change',
    category: 'performance',
    format: 'percent',
    higher_is_better: true,
    description: '1-day price change percentage',
  },
  {
    key: 'change_1w',
    label: '1-Week Change',
    category: 'performance',
    format: 'percent',
    higher_is_better: true,
    description: '1-week price change percentage',
  },
  {
    key: 'change_1m',
    label: '1-Month Change',
    category: 'performance',
    format: 'percent',
    higher_is_better: true,
    description: '1-month price change percentage',
  },
  {
    key: 'change_3m',
    label: '3-Month Change',
    category: 'performance',
    format: 'percent',
    higher_is_better: true,
    description: '3-month price change percentage',
  },
  {
    key: 'change_6m',
    label: '6-Month Change',
    category: 'performance',
    format: 'percent',
    higher_is_better: true,
    description: '6-month price change percentage',
  },
  {
    key: 'change_1y',
    label: '1-Year Change',
    category: 'performance',
    format: 'percent',
    higher_is_better: true,
    description: '1-year price change percentage',
  },
]

/**
 * Get metrics by category
 */
export function getMetricsByCategory(
  category: ComparisonMetric['category'],
): ComparisonMetric[] {
  return COMPARISON_METRICS.filter(m => m.category === category)
}

/**
 * Get metric by key
 */
export function getMetric(key: string): ComparisonMetric | undefined {
  return COMPARISON_METRICS.find(m => m.key === key)
}
