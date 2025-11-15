import { useEffect, useRef, useState } from 'react'
import {
  createChart,
  ColorType,
  CrosshairMode,
  LineStyle,
  type IChartApi,
  type ISeriesApi,
  type CandlestickData,
  type HistogramData,
} from 'lightweight-charts'
import { useTheme } from '@/hooks/useTheme'
import type { PriceHistoryResponse, PriceInterval } from '@/types'

interface PriceChartProps {
  /** Price history data */
  data: PriceHistoryResponse | undefined
  /** Loading state */
  loading: boolean
  /** Current timeframe */
  timeframe: PriceInterval
  /** Timeframe change handler */
  onTimeframeChange: (timeframe: PriceInterval) => void
}

/**
 * Price Chart Component
 *
 * Features:
 * - TradingView Lightweight Charts
 * - Candlestick chart
 * - Volume bars
 * - Timeframe selector
 * - Crosshair with price/date display
 * - Responsive design
 *
 * @example
 * ```tsx
 * const { data, isLoading, timeframe, setTimeframe } = usePriceChart('005930')
 *
 * <PriceChart
 *   data={data}
 *   loading={isLoading}
 *   timeframe={timeframe}
 *   onTimeframeChange={setTimeframe}
 * />
 * ```
 */
export default function PriceChart({
  data,
  loading,
  timeframe,
  onTimeframeChange,
}: PriceChartProps) {
  const { resolvedTheme } = useTheme()
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const [chartReady, setChartReady] = useState(false)

  // Timeframe buttons
  const timeframes: Array<{ label: string; value: PriceInterval }> = [
    { label: '1D', value: '1D' },
    { label: '1W', value: '1W' },
    { label: '1M', value: '1M' },
    { label: '3M', value: '3M' },
    { label: '6M', value: '6M' },
    { label: '1Y', value: '1Y' },
    { label: '3Y', value: '3Y' },
    { label: '5Y', value: '5Y' },
  ]

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return

    // Theme-based colors
    const isDark = resolvedTheme === 'dark'
    const chartColors = {
      backgroundColor: isDark ? '#1f2937' : '#ffffff',
      textColor: isDark ? '#f3f4f6' : '#333',
      gridColor: isDark ? '#374151' : '#f0f0f0',
      borderColor: isDark ? '#4b5563' : '#e1e1e1',
    }

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: chartColors.backgroundColor },
        textColor: chartColors.textColor,
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      grid: {
        vertLines: { color: chartColors.gridColor, style: LineStyle.Solid },
        horzLines: { color: chartColors.gridColor, style: LineStyle.Solid },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          width: 1,
          color: '#9B7DFF',
          style: LineStyle.Dashed,
        },
        horzLine: {
          width: 1,
          color: '#9B7DFF',
          style: LineStyle.Dashed,
        },
      },
      rightPriceScale: {
        borderColor: chartColors.borderColor,
      },
      timeScale: {
        borderColor: chartColors.borderColor,
        timeVisible: true,
        secondsVisible: false,
      },
    })

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#ef5350',
      downColor: '#26a69a',
      borderVisible: false,
      wickUpColor: '#ef5350',
      wickDownColor: '#26a69a',
    })

    // Add volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: 'volume',
    })

    // Configure volume price scale
    chart.priceScale('volume').applyOptions({
      scaleMargins: {
        top: 0.8, // Volume at bottom 20%
        bottom: 0,
      },
    })

    chartRef.current = chart
    candlestickSeriesRef.current = candlestickSeries
    volumeSeriesRef.current = volumeSeries
    setChartReady(true)

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
      chartRef.current = null
      candlestickSeriesRef.current = null
      volumeSeriesRef.current = null
      setChartReady(false)
    }
  }, [resolvedTheme])

  // Update data when changed
  useEffect(() => {
    if (!chartReady || !data || !candlestickSeriesRef.current || !volumeSeriesRef.current) {
      return
    }

    // Transform data to chart format
    const candleData: CandlestickData[] = data.candles.map((candle) => ({
      time: candle.date,
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close,
    }))

    const volumeData: HistogramData[] = data.candles.map((candle, index) => {
      const prevClose = index > 0 ? data.candles[index - 1].close : candle.open
      const color = candle.close >= prevClose ? '#ef535080' : '#26a69a80'

      return {
        time: candle.date,
        value: candle.volume,
        color,
      }
    })

    // Set data
    candlestickSeriesRef.current.setData(candleData)
    volumeSeriesRef.current.setData(volumeData)

    // Fit content
    chartRef.current?.timeScale().fitContent()
  }, [data, chartReady])

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 transition-colors">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">가격 차트</h3>

        {/* Timeframe Selector */}
        <div className="inline-flex rounded-md shadow-sm" role="group">
          {timeframes.map((tf) => (
            <button
              key={tf.value}
              type="button"
              onClick={() => onTimeframeChange(tf.value)}
              className={`px-3 py-1.5 text-sm font-medium border first:rounded-l-md last:rounded-r-md transition-colors ${
                timeframe === tf.value
                  ? 'bg-blue-600 dark:bg-blue-500 text-white border-blue-600 dark:border-blue-500 z-10'
                  : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'
              }`}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Container */}
      {loading ? (
        <div className="flex items-center justify-center h-[400px] bg-gray-50 dark:bg-gray-700 rounded transition-colors">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-solid border-blue-600 dark:border-blue-400 border-r-transparent mb-2"></div>
            <p className="text-sm text-gray-600 dark:text-gray-300">차트 로딩 중...</p>
          </div>
        </div>
      ) : !data || data.candles.length === 0 ? (
        <div className="flex items-center justify-center h-[400px] bg-gray-50 dark:bg-gray-700 rounded transition-colors">
          <div className="text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">차트 데이터가 없습니다</p>
          </div>
        </div>
      ) : (
        <div ref={chartContainerRef} className="w-full" />
      )}

      {/* Chart Info */}
      {data && data.candles.length > 0 && (
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
          {data.from_date} ~ {data.to_date} ({data.count}개 데이터 포인트)
        </div>
      )}
    </div>
  )
}
