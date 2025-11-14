/**
 * Sector Heatmap Component (FE-009 Phase 3)
 *
 * Interactive heatmap visualization of sector performance:
 * - Color-coded tiles based on performance
 * - Tooltip on hover with detailed info
 * - Click to drill down into sector stocks
 * - Timeframe selector (1D, 1W, 1M, 3M)
 * - Responsive grid layout
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSectorPerformance } from '../../hooks/useSectorPerformance'
import type { SectorPerformance } from '../../types/market'

/**
 * Get background color based on performance
 */
function getPerformanceColor(changePct: number): string {
  if (changePct >= 2) return 'bg-green-600 text-white'
  if (changePct >= 1) return 'bg-green-500 text-white'
  if (changePct >= 0) return 'bg-green-100 text-green-800'
  if (changePct >= -1) return 'bg-red-100 text-red-800'
  if (changePct >= -2) return 'bg-red-500 text-white'
  return 'bg-red-600 text-white'
}

/**
 * Single sector tile component
 */
function SectorTile({ sector }: { sector: SectorPerformance }) {
  const navigate = useNavigate()
  const colorClass = getPerformanceColor(sector.change_percent)
  const isPositive = sector.change_percent >= 0

  const handleClick = () => {
    // Navigate to screener page with sector filter
    navigate(`/screener?sector=${sector.code}`)
  }

  return (
    <button
      onClick={handleClick}
      className={`group relative flex flex-col items-center justify-center rounded-lg p-4 transition-all hover:scale-105 hover:shadow-lg ${colorClass}`}
      title={`${sector.name}: ${isPositive ? '+' : ''}${sector.change_percent.toFixed(2)}%`}
    >
      {/* Sector name */}
      <div className="mb-2 text-center text-sm font-medium">
        {sector.name}
      </div>

      {/* Change percentage */}
      <div className="text-2xl font-bold">
        {isPositive ? '+' : ''}
        {sector.change_percent.toFixed(2)}%
      </div>

      {/* Stock count */}
      <div className="mt-2 text-xs opacity-80">
        {sector.stock_count}개 종목
      </div>

      {/* Tooltip on hover */}
      <div className="absolute bottom-full left-1/2 z-10 mb-2 hidden -translate-x-1/2 rounded-lg bg-gray-900 px-3 py-2 text-xs text-white shadow-lg group-hover:block">
        <div className="mb-1 font-medium">{sector.name}</div>
        <div>변동률: {isPositive ? '+' : ''}{sector.change_percent.toFixed(2)}%</div>
        <div>종목 수: {sector.stock_count}개</div>
        {sector.market_cap && (
          <div>시가총액: {(sector.market_cap / 1_000_000_000_000).toFixed(1)}조원</div>
        )}
        <div className="mt-1 text-gray-400">클릭하여 종목 보기 →</div>
        {/* Arrow */}
        <div className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
      </div>
    </button>
  )
}

/**
 * Sector Heatmap Props
 */
export interface SectorHeatmapProps {
  /** Default timeframe */
  defaultTimeframe?: '1D' | '1W' | '1M' | '3M'
  /** Enable auto-refresh */
  autoRefresh?: boolean
  /** Class name for styling */
  className?: string
}

/**
 * Sector Heatmap Component
 *
 * @example
 * ```tsx
 * <SectorHeatmap defaultTimeframe="1D" autoRefresh={true} />
 * ```
 */
export function SectorHeatmap({
  defaultTimeframe = '1D',
  autoRefresh = false,
  className = '',
}: SectorHeatmapProps) {
  const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M' | '3M'>(defaultTimeframe)

  const { data, isLoading, error } = useSectorPerformance({
    timeframe,
    refetchInterval: autoRefresh ? 60000 : undefined,
  })

  const timeframes = [
    { label: '1일', value: '1D' as const },
    { label: '1주', value: '1W' as const },
    { label: '1개월', value: '1M' as const },
    { label: '3개월', value: '3M' as const },
  ]

  return (
    <div className={`rounded-lg bg-white p-6 shadow-sm ${className}`}>
      {/* Header with timeframe selector */}
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          섹터 성과 <span className="text-sm font-normal text-gray-500">Sector Performance</span>
        </h2>

        {/* Timeframe selector */}
        <div className="flex gap-2">
          {timeframes.map((tf) => (
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

      {/* Legend */}
      <div className="mb-4 flex flex-wrap items-center gap-4 text-xs">
        <div className="flex items-center gap-1">
          <div className="h-4 w-4 rounded bg-green-600"></div>
          <span>+2% 이상</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-4 w-4 rounded bg-green-500"></div>
          <span>+1% ~ +2%</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-4 w-4 rounded bg-green-100 border border-green-300"></div>
          <span>0% ~ +1%</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-4 w-4 rounded bg-red-100 border border-red-300"></div>
          <span>-1% ~ 0%</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-4 w-4 rounded bg-red-500"></div>
          <span>-2% ~ -1%</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-4 w-4 rounded bg-red-600"></div>
          <span>-2% 이하</span>
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
        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-lg bg-gray-200"></div>
          ))}
        </div>
      )}

      {/* Data State */}
      {data && !isLoading && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
          {data.sectors.map((sector) => (
            <SectorTile key={sector.code} sector={sector} />
          ))}
        </div>
      )}

      {/* Help text */}
      <div className="mt-4 text-center text-xs text-gray-500">
        섹터를 클릭하면 해당 섹터의 종목 목록을 볼 수 있습니다
      </div>
    </div>
  )
}
