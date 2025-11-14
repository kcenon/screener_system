/**
 * Advanced Sector Heatmap Component (IMPROVEMENT-004 Phase 3A)
 *
 * Interactive treemap visualization with Recharts:
 * - Size = Market cap (proportional sizing)
 * - Color = Performance % (5-level color scale)
 * - Click to filter screener by sector
 * - Hover tooltip with detailed info
 * - Responsive design
 *
 * Future enhancement: Drill-down to top 3 stocks per sector
 */

import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Treemap, ResponsiveContainer, Tooltip } from 'recharts'
import { useSectorPerformance } from '../../hooks/useSectorPerformance'
import { componentSpacing, typography } from '../../config/theme'
import { formatCompactMarketCap } from '../../utils/formatNumber'
import type { SectorPerformance } from '../../types/market'

/**
 * 5-level performance color scale
 * Matches finviz-style color scheme
 */
function getPerformanceColor(changePct: number): string {
  if (changePct > 3) return '#166534'  // Dark Green
  if (changePct > 1) return '#16a34a'  // Green
  if (changePct > -1) return '#6b7280' // Gray
  if (changePct > -3) return '#dc2626' // Red
  return '#991b1b'                     // Dark Red
}

/**
 * Get text color for contrast
 */
function getTextColor(changePct: number): string {
  // White text for dark colors
  if (Math.abs(changePct) > 1) return '#ffffff'
  // Dark text for light gray
  return '#1f2937'
}

/**
 * Treemap data structure
 */
interface TreemapData {
  name: string
  value: number
  performance: number
  stockCount: number
  code: string
  fill?: string
}

/**
 * Custom treemap content component
 */
function CustomTreemapContent(props: any) {
  const { x, y, width, height, name, performance, stockCount } = props

  // Ensure all required props exist
  if (typeof x !== 'number' || typeof y !== 'number' ||
      typeof width !== 'number' || typeof height !== 'number') {
    return null
  }

  const isPositive = performance >= 0
  const textColor = getTextColor(performance)

  // Don't render if too small
  if (width < 60 || height < 40) {
    return null
  }

  return (
    <g>
      {/* Sector name */}
      <text
        x={x + width / 2}
        y={y + height / 2 - 12}
        textAnchor="middle"
        fill={textColor}
        fontSize={width > 120 ? 14 : 11}
        fontWeight="600"
      >
        {name}
      </text>

      {/* Performance % */}
      <text
        x={x + width / 2}
        y={y + height / 2 + 6}
        textAnchor="middle"
        fill={textColor}
        fontSize={width > 120 ? 20 : 16}
        fontWeight="700"
      >
        {isPositive ? '+' : ''}
        {performance.toFixed(2)}%
      </text>

      {/* Stock count */}
      <text
        x={x + width / 2}
        y={y + height / 2 + 24}
        textAnchor="middle"
        fill={textColor}
        fontSize={width > 120 ? 11 : 9}
        opacity={0.8}
      >
        {stockCount}개
      </text>
    </g>
  )
}

/**
 * Custom tooltip component
 */
function CustomTooltip({ active, payload }: {
  active?: boolean
  payload?: Array<{
    payload: TreemapData & {
      marketCap: number
    }
  }>
}) {
  if (!active || !payload || !payload[0]) {
    return null
  }

  const data = payload[0].payload
  const isPositive = data.performance >= 0

  return (
    <div className="rounded-lg bg-gray-900 px-3 py-2 text-white shadow-lg">
      <div className="mb-1 font-medium">{data.name}</div>
      <div className="text-sm">
        <div>
          변동률: <span className={isPositive ? 'text-green-400' : 'text-red-400'}>
            {isPositive ? '+' : ''}
            {data.performance.toFixed(2)}%
          </span>
        </div>
        <div>종목 수: {data.stockCount}개</div>
        {data.marketCap && (
          <div>시가총액: {formatCompactMarketCap(data.marketCap)}</div>
        )}
      </div>
      <div className="mt-1 text-xs text-gray-400">클릭하여 종목 보기 →</div>
    </div>
  )
}

/**
 * Advanced Sector Heatmap Props
 */
export interface SectorHeatmapAdvancedProps {
  /** Default timeframe */
  defaultTimeframe?: '1D' | '1W' | '1M' | '3M'
  /** Enable auto-refresh */
  autoRefresh?: boolean
  /** Height of the treemap */
  height?: number
  /** Class name for styling */
  className?: string
}

/**
 * Advanced Sector Heatmap Component with Treemap
 *
 * @example
 * ```tsx
 * <SectorHeatmapAdvanced
 *   defaultTimeframe="1D"
 *   autoRefresh={true}
 *   height={500}
 * />
 * ```
 */
export function SectorHeatmapAdvanced({
  defaultTimeframe = '1D',
  autoRefresh = false,
  height = 500,
  className = '',
}: SectorHeatmapAdvancedProps) {
  const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M' | '3M'>(defaultTimeframe)
  const navigate = useNavigate()

  const { data, isLoading, error } = useSectorPerformance({
    timeframe,
    refetchInterval: autoRefresh ? 60000 : undefined,
  })

  // Transform data for treemap
  const treemapData = useMemo(() => {
    if (!data?.sectors) return []

    return data.sectors.map((sector: SectorPerformance) => ({
      name: sector.name,
      value: sector.market_cap,
      performance: sector.change_percent,
      stockCount: sector.stock_count,
      code: sector.code,
      marketCap: sector.market_cap,
      fill: getPerformanceColor(sector.change_percent),
    }))
  }, [data])

  // Handle sector click
  const handleClick = (data: TreemapData) => {
    navigate(`/screener?sector=${data.code}`)
  }

  const timeframes = [
    { label: '1일', value: '1D' as const },
    { label: '1주', value: '1W' as const },
    { label: '1개월', value: '1M' as const },
    { label: '3개월', value: '3M' as const },
  ]

  return (
    <div className={`rounded-lg bg-white ${componentSpacing.widget} shadow-sm ${className}`}>
      {/* Header with timeframe selector */}
      <div className="mb-3 flex items-center justify-between">
        <h2 className={`${typography.h2} text-gray-900`}>
          섹터 성과 맵 <span className="text-xs font-normal text-gray-500">Sector Performance Map</span>
        </h2>

        {/* Timeframe selector */}
        <div className="flex gap-1.5">
          {timeframes.map((tf) => (
            <button
              key={tf.value}
              onClick={() => setTimeframe(tf.value)}
              className={`rounded px-2.5 py-1 text-xs font-medium transition-colors ${
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

      {/* Legend */}
      <div className="mb-3 flex flex-wrap items-center gap-3 text-xs">
        <div className="flex items-center gap-1">
          <div className="h-3 w-3 rounded" style={{ backgroundColor: '#166534' }}></div>
          <span>+3% 이상</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-3 w-3 rounded" style={{ backgroundColor: '#16a34a' }}></div>
          <span>+1% ~ +3%</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-3 w-3 rounded" style={{ backgroundColor: '#6b7280' }}></div>
          <span>-1% ~ +1%</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-3 w-3 rounded" style={{ backgroundColor: '#dc2626' }}></div>
          <span>-3% ~ -1%</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-3 w-3 rounded" style={{ backgroundColor: '#991b1b' }}></div>
          <span>-3% 이하</span>
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
        <div className="flex items-center justify-center" style={{ height }}>
          <div className="animate-pulse text-gray-400">Loading treemap...</div>
        </div>
      )}

      {/* Treemap Visualization */}
      {data && !isLoading && treemapData.length > 0 && (
        <div className="cursor-pointer">
          <ResponsiveContainer width="100%" height={height}>
            <Treemap
              data={treemapData}
              dataKey="value"
              aspectRatio={16 / 9}
              stroke="#fff"
              onClick={(data: any) => {
                if (data && data.code) {
                  handleClick(data)
                }
              }}
              content={<CustomTreemapContent />}
            >
              <Tooltip content={<CustomTooltip />} />
            </Treemap>
          </ResponsiveContainer>
        </div>
      )}

      {/* Help text */}
      <div className="mt-3 text-center text-xs text-gray-500">
        크기는 시가총액에 비례하며, 색상은 성과를 나타냅니다. 섹터를 클릭하면 해당 종목 목록을 볼 수 있습니다.
      </div>
    </div>
  )
}
