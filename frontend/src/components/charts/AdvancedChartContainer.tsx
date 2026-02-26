/**
 * Advanced Chart Container
 *
 * Main wrapper component that integrates:
 * - AdvancedChart (core chart rendering)
 * - ChartToolbar (controls)
 * - IndicatorPanel (indicator management)
 * - DrawingTools (drawing management)
 *
 * Provides a complete TradingView-style charting experience.
 */

import { useState, useCallback, useRef } from 'react'
import { useTheme } from '@/hooks/useTheme'
import type { PriceHistoryResponse, PriceInterval } from '@/types'
import type { ChartType, IndicatorConfig, DrawingTool, Drawing } from './types'
import AdvancedChart from './AdvancedChart'
import ChartToolbar from './ChartToolbar'
import IndicatorPanel from './IndicatorPanel'
import DrawingTools, { useDrawings } from './DrawingTools'
import type { OHLCV } from '@/utils/indicators'

interface AdvancedChartContainerProps {
  /** Stock symbol/code */
  symbol: string
  /** Price history data from API */
  data: PriceHistoryResponse | undefined
  /** Loading state */
  loading: boolean
  /** Current timeframe */
  timeframe: PriceInterval
  /** Timeframe change handler */
  onTimeframeChange: (timeframe: PriceInterval) => void
  /** Chart height */
  height?: number
}

export default function AdvancedChartContainer({
  symbol,
  data,
  loading,
  timeframe,
  onTimeframeChange,
  height = 500,
}: AdvancedChartContainerProps) {
  const { resolvedTheme } = useTheme()
  const chartContainerRef = useRef<HTMLDivElement>(null)

  // Chart state
  const [chartType, setChartType] = useState<ChartType>('candlestick')
  const [showVolume, setShowVolume] = useState(true)
  const [showIndicatorPanel, setShowIndicatorPanel] = useState(false)
  const [indicators, setIndicators] = useState<IndicatorConfig[]>([])
  const [drawingTool, setDrawingTool] = useState<DrawingTool>('none')

  // Drawing state
  const { drawings, addDrawing, clearAll } = useDrawings(symbol)

  // Transform API data to OHLCV format
  const chartData: OHLCV[] =
    data?.candles.map(candle => ({
      time: candle.date,
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close,
      volume: candle.volume,
    })) || []

  // Indicator handlers
  const handleAddIndicator = useCallback((indicator: IndicatorConfig) => {
    setIndicators(prev => [...prev, indicator])
  }, [])

  const handleRemoveIndicator = useCallback((id: string) => {
    setIndicators(prev => prev.filter(i => i.id !== id))
  }, [])

  const handleUpdateIndicator = useCallback(
    (id: string, updates: Partial<IndicatorConfig>) => {
      setIndicators(prev =>
        prev.map(i => (i.id === id ? { ...i, ...updates } : i)),
      )
    },
    [],
  )

  // Zoom handlers (placeholder - actual implementation requires chart ref)
  const handleZoomIn = useCallback(() => {
    // Chart zoom is handled internally by lightweight-charts
    console.log('Zoom in')
  }, [])

  const handleZoomOut = useCallback(() => {
    console.log('Zoom out')
  }, [])

  const handleResetZoom = useCallback(() => {
    console.log('Reset zoom')
  }, [])

  // Export handler
  const handleExport = useCallback(() => {
    if (!chartContainerRef.current) return

    // Find the canvas element
    const canvas = chartContainerRef.current.querySelector('canvas')
    if (!canvas) return

    // Create download link
    const link = document.createElement('a')
    link.download = `${symbol}-chart-${new Date().toISOString().split('T')[0]}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  }, [symbol])

  // Fullscreen handler
  const handleFullscreen = useCallback(() => {
    if (!chartContainerRef.current) return

    if (document.fullscreenElement) {
      document.exitFullscreen()
    } else {
      chartContainerRef.current.requestFullscreen()
    }
  }, [])

  // Drawing change handler
  const handleDrawingsChange = useCallback(
    (newDrawings: Drawing[]) => {
      // Sync with localStorage-backed state
      clearAll()
      newDrawings.forEach(addDrawing)
    },
    [clearAll, addDrawing],
  )

  return (
    <div
      ref={chartContainerRef}
      className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden transition-colors"
    >
      {/* Chart Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          고급 차트
        </h3>
        {data && data.candles.length > 0 && (
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {data.from_date} ~ {data.to_date} ({data.count}개)
          </span>
        )}
      </div>

      {/* Toolbar */}
      <ChartToolbar
        chartType={chartType}
        onChartTypeChange={setChartType}
        timeframe={timeframe}
        onTimeframeChange={onTimeframeChange}
        drawingTool={drawingTool}
        onDrawingToolChange={setDrawingTool}
        showIndicatorPanel={showIndicatorPanel}
        onToggleIndicatorPanel={() =>
          setShowIndicatorPanel(!showIndicatorPanel)
        }
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        onResetZoom={handleResetZoom}
        onExport={handleExport}
        onFullscreen={handleFullscreen}
      />

      {/* Chart Area */}
      <div className="flex">
        {/* Main Chart */}
        <div className="flex-1 relative">
          <AdvancedChart
            symbol={symbol}
            data={chartData}
            height={height}
            chartType={chartType}
            theme={resolvedTheme as 'light' | 'dark'}
            indicators={indicators}
            showVolume={showVolume}
            loading={loading}
          />

          {/* Drawing Tools Overlay */}
          {drawings.length > 0 && (
            <DrawingTools
              drawings={drawings}
              onDrawingsChange={handleDrawingsChange}
            />
          )}
        </div>

        {/* Indicator Panel */}
        {showIndicatorPanel && (
          <IndicatorPanel
            indicators={indicators}
            onAddIndicator={handleAddIndicator}
            onRemoveIndicator={handleRemoveIndicator}
            onUpdateIndicator={handleUpdateIndicator}
            onClose={() => setShowIndicatorPanel(false)}
          />
        )}
      </div>

      {/* Volume Toggle & Quick Actions */}
      <div className="flex items-center justify-between px-4 py-2 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
        <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <input
            type="checkbox"
            checked={showVolume}
            onChange={e => setShowVolume(e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          거래량 표시
        </label>

        <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
          <span>활성 지표: {indicators.filter(i => i.visible).length}</span>
          <span>•</span>
          <span>그리기: {drawings.length}</span>
        </div>
      </div>
    </div>
  )
}
