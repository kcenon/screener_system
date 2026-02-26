/**
 * Chart Types and Configuration
 *
 * Type definitions for the advanced charting system.
 */

import type { OHLCV } from '@/utils/indicators'

export type ChartType = 'candlestick' | 'ohlc' | 'line' | 'area' | 'heikin-ashi'

export type IndicatorType =
  | 'sma'
  | 'ema'
  | 'bollinger'
  | 'volume'
  | 'rsi'
  | 'macd'
  | 'stochastic'

export type DrawingTool =
  | 'none'
  | 'trendline'
  | 'horizontal'
  | 'fibonacci'
  | 'rectangle'
  | 'text'

export interface IndicatorConfig {
  id: string
  type: IndicatorType
  params: Record<string, number>
  color: string
  visible: boolean
}

export interface Drawing {
  id: string
  type: DrawingTool
  points: { time: string; price: number }[]
  color: string
  lineWidth: number
  label?: string
}

export interface ChartTheme {
  backgroundColor: string
  textColor: string
  gridColor: string
  borderColor: string
  crosshairColor: string
  upColor: string
  downColor: string
}

export interface AdvancedChartProps {
  /** Stock symbol/code */
  symbol: string
  /** OHLCV data for the chart */
  data: OHLCV[]
  /** Chart height in pixels */
  height?: number
  /** Chart type to display */
  chartType?: ChartType
  /** Theme mode */
  theme?: 'light' | 'dark'
  /** Active indicators */
  indicators?: IndicatorConfig[]
  /** Show volume pane */
  showVolume?: boolean
  /** Enable drawing tools */
  enableDrawing?: boolean
  /** Comparison symbols */
  comparison?: { symbol: string; color: string }[]
  /** Callback when chart settings change */
  onSettingsChange?: (settings: ChartSettings) => void
  /** Loading state */
  loading?: boolean
}

export interface ChartSettings {
  chartType: ChartType
  indicators: IndicatorConfig[]
  showVolume: boolean
  showGrid: boolean
  crosshairMode: 'normal' | 'magnet'
}

export const DEFAULT_INDICATOR_COLORS: Record<IndicatorType, string> = {
  sma: '#2196F3',
  ema: '#FF9800',
  bollinger: '#9C27B0',
  volume: '#607D8B',
  rsi: '#4CAF50',
  macd: '#E91E63',
  stochastic: '#00BCD4',
}

export const DEFAULT_INDICATOR_PARAMS: Record<
  IndicatorType,
  Record<string, number>
> = {
  sma: { period: 20 },
  ema: { period: 12 },
  bollinger: { period: 20, stdDev: 2 },
  volume: {},
  rsi: { period: 14 },
  macd: { fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 },
  stochastic: { kPeriod: 14, dPeriod: 3 },
}

export const INDICATOR_LABELS: Record<IndicatorType, string> = {
  sma: 'SMA',
  ema: 'EMA',
  bollinger: 'Bollinger Bands',
  volume: 'Volume',
  rsi: 'RSI',
  macd: 'MACD',
  stochastic: 'Stochastic',
}

export const CHART_TYPE_LABELS: Record<ChartType, string> = {
  candlestick: '캔들스틱',
  ohlc: 'OHLC',
  line: '라인',
  area: '영역',
  'heikin-ashi': '하이킨아시',
}

export const DRAWING_TOOL_LABELS: Record<DrawingTool, string> = {
  none: '선택',
  trendline: '추세선',
  horizontal: '수평선',
  fibonacci: '피보나치',
  rectangle: '사각형',
  text: '텍스트',
}
