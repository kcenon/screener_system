/**
 * Market Trend Chart Component (FE-009 Phase 6)
 *
 * Historical market trend visualization:
 * - TradingView Lightweight Charts integration
 * - Historical data for market indices
 * - Timeframe selector (1D, 5D, 1M, 3M, 6M, 1Y)
 * - Multiple series overlay (KOSPI, KOSDAQ)
 * - Tooltips and crosshair
 */

import { useEffect, useRef, useState } from 'react'
import {
  createChart,
  ColorType,
  type IChartApi,
  type ISeriesApi,
  type LineData,
} from 'lightweight-charts'
import { useMarketTrend } from '../../hooks/useMarketTrend'
import type { TrendTimeframe } from '../../types/market'
import { TREND_TIMEFRAMES } from '../../types/market'

/**
 * Market Trend Chart Props
 */
export interface MarketTrendChartProps {
  /** Default timeframe */
  defaultTimeframe?: TrendTimeframe
  /** Indices to display */
  indices?: string[]
  /** Chart height in pixels */
  height?: number
  /** Class name for styling */
  className?: string
}

/**
 * Market Trend Chart Component
 *
 * @example
 * ```tsx
 * <MarketTrendChart
 *   defaultTimeframe="3M"
 *   indices={['KOSPI', 'KOSDAQ']}
 *   height={400}
 * />
 * ```
 */
export function MarketTrendChart({
  defaultTimeframe = '3M',
  indices = ['KOSPI', 'KOSDAQ'],
  height = 400,
  className = '',
}: MarketTrendChartProps) {
  const [timeframe, setTimeframe] = useState<TrendTimeframe>(defaultTimeframe)
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRefs = useRef<Map<string, ISeriesApi<'Line'>>>(new Map())

  const { data, isLoading, error } = useMarketTrend({
    timeframe,
    indices,
  })

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height,
      layout: {
        background: { type: ColorType.Solid, color: 'white' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      crosshair: {
        mode: 1, // Normal crosshair mode
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: '#ddd',
      },
      rightPriceScale: {
        borderColor: '#ddd',
      },
    })

    chartRef.current = chart

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
      chartRef.current = null
      seriesRefs.current.clear()
    }
  }, [height])

  // Update chart data
  useEffect(() => {
    if (!chartRef.current || !data) return

    // Clear existing series
    seriesRefs.current.forEach((series) => {
      chartRef.current?.removeSeries(series)
    })
    seriesRefs.current.clear()

    // Color mapping for different indices
    const colors: Record<string, string> = {
      KOSPI: '#2563eb', // Blue
      KOSDAQ: '#dc2626', // Red
      KRX100: '#16a34a', // Green
    }

    // Create series for each index
    data.trends.forEach((trend) => {
      if (!chartRef.current) return

      const series = chartRef.current.addLineSeries({
        color: colors[trend.code] || '#6b7280',
        lineWidth: 2,
        title: trend.name,
        priceFormat: {
          type: 'price',
          precision: 2,
          minMove: 0.01,
        },
      })

      // Convert data to chart format
      const chartData: LineData[] = trend.data.map((point) => ({
        time: Math.floor(new Date(point.date).getTime() / 1000) as any, // Convert to seconds (Unix timestamp)
        value: point.value,
      }))

      series.setData(chartData)
      seriesRefs.current.set(trend.code, series)
    })

    // Fit content
    chartRef.current.timeScale().fitContent()
  }, [data])

  return (
    <div className={`rounded-lg bg-white p-6 shadow-sm ${className}`}>
      {/* Header with timeframe selector */}
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          시장 추세 <span className="text-sm font-normal text-gray-500">Market Trend</span>
        </h2>

        {/* Timeframe selector */}
        <div className="flex gap-2">
          {TREND_TIMEFRAMES.map((tf) => (
            <button
              key={tf.value}
              onClick={() => setTimeframe(tf.value)}
              className={`rounded px-3 py-1 text-sm font-medium transition-colors ${
                timeframe === tf.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-center">
          <p className="text-sm text-red-600">데이터를 불러오는 중 오류가 발생했습니다.</p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div
          className="flex items-center justify-center rounded-lg bg-gray-100"
          style={{ height: `${height}px` }}
        >
          <div className="text-sm text-gray-500">차트 로딩 중...</div>
        </div>
      )}

      {/* Chart */}
      {!isLoading && (
        <div ref={chartContainerRef} className="relative" />
      )}

      {/* Legend */}
      {data && (
        <div className="mt-4 flex justify-center gap-6">
          {data.trends.map((trend) => (
            <div key={trend.code} className="flex items-center gap-2">
              <div
                className="h-3 w-3 rounded-full"
                style={{
                  backgroundColor:
                    trend.code === 'KOSPI'
                      ? '#2563eb'
                      : trend.code === 'KOSDAQ'
                        ? '#dc2626'
                        : '#16a34a',
                }}
              ></div>
              <span className="text-sm text-gray-700">{trend.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
