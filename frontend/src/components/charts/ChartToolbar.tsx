/**
 * Chart Toolbar Component
 *
 * Controls for:
 * - Chart type selection
 * - Timeframe selection
 * - Drawing tools
 * - Indicator panel toggle
 * - Chart settings
 */

import { useState } from 'react'
import {
  CandlestickChart,
  LineChart,
  AreaChart,
  BarChart3,
  TrendingUp,
  Settings,
  Download,
  ZoomIn,
  ZoomOut,
  RefreshCw,
  Maximize2,
} from 'lucide-react'
import type { ChartType, DrawingTool } from './types'
import { CHART_TYPE_LABELS, DRAWING_TOOL_LABELS } from './types'
import type { PriceInterval } from '@/types'

interface ChartToolbarProps {
  chartType: ChartType
  onChartTypeChange: (type: ChartType) => void
  timeframe: PriceInterval
  onTimeframeChange: (timeframe: PriceInterval) => void
  drawingTool: DrawingTool
  onDrawingToolChange: (tool: DrawingTool) => void
  showIndicatorPanel: boolean
  onToggleIndicatorPanel: () => void
  onZoomIn: () => void
  onZoomOut: () => void
  onResetZoom: () => void
  onExport: () => void
  onFullscreen?: () => void
}

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

const chartTypeIcons: Record<ChartType, React.ReactNode> = {
  candlestick: <CandlestickChart className="w-4 h-4" />,
  ohlc: <BarChart3 className="w-4 h-4" />,
  line: <LineChart className="w-4 h-4" />,
  area: <AreaChart className="w-4 h-4" />,
  'heikin-ashi': <CandlestickChart className="w-4 h-4" />,
}

export default function ChartToolbar({
  chartType,
  onChartTypeChange,
  timeframe,
  onTimeframeChange,
  drawingTool,
  onDrawingToolChange,
  showIndicatorPanel,
  onToggleIndicatorPanel,
  onZoomIn,
  onZoomOut,
  onResetZoom,
  onExport,
  onFullscreen,
}: ChartToolbarProps) {
  const [showChartTypeMenu, setShowChartTypeMenu] = useState(false)
  const [showDrawingMenu, setShowDrawingMenu] = useState(false)

  return (
    <div className="flex flex-wrap items-center gap-2 p-2 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      {/* Chart Type Selector */}
      <div className="relative">
        <button
          onClick={() => setShowChartTypeMenu(!showChartTypeMenu)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600"
          title="차트 타입"
        >
          {chartTypeIcons[chartType]}
          <span className="hidden sm:inline">
            {CHART_TYPE_LABELS[chartType]}
          </span>
        </button>

        {showChartTypeMenu && (
          <div className="absolute top-full left-0 mt-1 w-40 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-md shadow-lg z-50">
            {(Object.keys(CHART_TYPE_LABELS) as ChartType[]).map(type => (
              <button
                key={type}
                onClick={() => {
                  onChartTypeChange(type)
                  setShowChartTypeMenu(false)
                }}
                className={`w-full flex items-center gap-2 px-3 py-2 text-sm text-left hover:bg-gray-100 dark:hover:bg-gray-600 ${
                  chartType === type
                    ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                    : 'text-gray-700 dark:text-gray-300'
                }`}
              >
                {chartTypeIcons[type]}
                {CHART_TYPE_LABELS[type]}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Divider */}
      <div className="h-6 w-px bg-gray-300 dark:bg-gray-600" />

      {/* Timeframe Selector */}
      <div className="inline-flex rounded-md shadow-sm" role="group">
        {timeframes.map(tf => (
          <button
            key={tf.value}
            type="button"
            onClick={() => onTimeframeChange(tf.value)}
            className={`px-2.5 py-1.5 text-xs font-medium border first:rounded-l-md last:rounded-r-md transition-colors ${
              timeframe === tf.value
                ? 'bg-blue-600 dark:bg-blue-500 text-white border-blue-600 dark:border-blue-500 z-10'
                : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'
            }`}
          >
            {tf.label}
          </button>
        ))}
      </div>

      {/* Divider */}
      <div className="h-6 w-px bg-gray-300 dark:bg-gray-600" />

      {/* Drawing Tools */}
      <div className="relative">
        <button
          onClick={() => setShowDrawingMenu(!showDrawingMenu)}
          className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md border transition-colors ${
            drawingTool !== 'none'
              ? 'bg-blue-600 dark:bg-blue-500 text-white border-blue-600 dark:border-blue-500'
              : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
          }`}
          title="그리기 도구"
        >
          <TrendingUp className="w-4 h-4" />
          <span className="hidden sm:inline">
            {DRAWING_TOOL_LABELS[drawingTool]}
          </span>
        </button>

        {showDrawingMenu && (
          <div className="absolute top-full left-0 mt-1 w-36 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-md shadow-lg z-50">
            {(Object.keys(DRAWING_TOOL_LABELS) as DrawingTool[]).map(tool => (
              <button
                key={tool}
                onClick={() => {
                  onDrawingToolChange(tool)
                  setShowDrawingMenu(false)
                }}
                className={`w-full px-3 py-2 text-sm text-left hover:bg-gray-100 dark:hover:bg-gray-600 ${
                  drawingTool === tool
                    ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                    : 'text-gray-700 dark:text-gray-300'
                }`}
              >
                {DRAWING_TOOL_LABELS[tool]}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Indicator Panel Toggle */}
      <button
        onClick={onToggleIndicatorPanel}
        className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md border transition-colors ${
          showIndicatorPanel
            ? 'bg-blue-600 dark:bg-blue-500 text-white border-blue-600 dark:border-blue-500'
            : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
        }`}
        title="지표"
      >
        <Settings className="w-4 h-4" />
        <span className="hidden sm:inline">지표</span>
      </button>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Zoom Controls */}
      <div className="inline-flex items-center gap-1">
        <button
          onClick={onZoomIn}
          className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-400"
          title="확대"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={onZoomOut}
          className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-400"
          title="축소"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={onResetZoom}
          className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-400"
          title="초기화"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Divider */}
      <div className="h-6 w-px bg-gray-300 dark:bg-gray-600" />

      {/* Export & Fullscreen */}
      <button
        onClick={onExport}
        className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-400"
        title="내보내기"
      >
        <Download className="w-4 h-4" />
      </button>
      {onFullscreen && (
        <button
          onClick={onFullscreen}
          className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-400"
          title="전체화면"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      )}
    </div>
  )
}
