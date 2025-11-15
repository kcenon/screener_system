/**
 * Quick Filters Bar Component (IMPROVEMENT-004 Phase 3B)
 *
 * One-click preset filters for common screening tasks:
 * - Top gainers/losers
 * - High volume
 * - 52-week highs
 * - High dividend
 * - Low P/E
 * - High growth
 * - Small/large caps
 * - New listings
 *
 * Features:
 * - Multiple filters can be combined
 * - Active state highlighting
 * - Tooltips explaining each preset
 * - "Clear All" functionality
 * - Mobile-responsive horizontal scrolling
 */

import { useState } from 'react'
import * as Tooltip from '@radix-ui/react-tooltip'
import type { ScreeningFilters } from '@/types/screening'

/**
 * Quick filter preset definition
 */
export interface QuickFilter {
  id: string
  label: string
  icon: string
  tooltip: string
  filters: Partial<ScreeningFilters>
}

/**
 * Preset filter definitions
 * Based on IMPROVEMENT-004 specification, adjusted for actual ScreeningFilters type
 */
const QUICK_FILTERS: QuickFilter[] = [
  {
    id: 'top-gainers',
    label: '상위상승',
    icon: '⬆',
    tooltip: '등락률 +5% 이상인 종목 (1일)',
    filters: {
      price_change_1d: { min: 5 },
    },
  },
  {
    id: 'top-losers',
    label: '상위하락',
    icon: '⬇',
    tooltip: '등락률 -5% 이하인 종목 (1일)',
    filters: {
      price_change_1d: { max: -5 },
    },
  },
  {
    id: 'high-volume',
    label: '고거래량',
    icon: '📊',
    tooltip: '거래량 급증 100% 이상',
    filters: {
      volume_surge_pct: { min: 100 },
    },
  },
  {
    id: '52w-high',
    label: '1년급등',
    icon: '🏔',
    tooltip: '1년 수익률 50% 이상',
    filters: {
      price_change_1y: { min: 50 },
    },
  },
  {
    id: 'high-dividend',
    label: '고배당',
    icon: '💰',
    tooltip: '배당수익률 4% 이상',
    filters: {
      dividend_yield: { min: 4 },
    },
  },
  {
    id: 'low-pe',
    label: '저PER',
    icon: '💎',
    tooltip: 'PER 10 이하 (저평가 가능)',
    filters: {
      per: { min: 0.1, max: 10 },
    },
  },
  {
    id: 'high-growth',
    label: '고성장',
    icon: '📈',
    tooltip: '매출성장률 20% 이상',
    filters: {
      revenue_growth_yoy: { min: 20 },
    },
  },
  {
    id: 'small-cap',
    label: '소형주',
    icon: '🐣',
    tooltip: '시가총액 1조 미만',
    filters: {
      market_cap: { max: 1000 }, // billion KRW
    },
  },
  {
    id: 'large-cap',
    label: '대형주',
    icon: '🦁',
    tooltip: '시가총액 10조 이상',
    filters: {
      market_cap: { min: 10000 }, // billion KRW
    },
  },
  {
    id: 'high-quality',
    label: '고품질',
    icon: '✨',
    tooltip: '전체 점수 80점 이상',
    filters: {
      overall_score: { min: 80 },
    },
  },
]

/**
 * Quick Filters Bar Props
 */
export interface QuickFiltersBarProps {
  /** Current filters */
  currentFilters: ScreeningFilters
  /** Callback when filters change */
  onFilterChange: (filters: Partial<ScreeningFilters>) => void
  /** Callback to clear all filters */
  onClearAll?: () => void
  /** Custom className */
  className?: string
}

/**
 * Quick Filters Bar Component
 *
 * @example
 * ```tsx
 * <QuickFiltersBar
 *   currentFilters={filters}
 *   onFilterChange={(newFilters) => setFilters({ ...filters, ...newFilters })}
 *   onClearAll={() => setFilters({ market: 'ALL' })}
 * />
 * ```
 */
export function QuickFiltersBar({
  currentFilters: _currentFilters,
  onFilterChange,
  onClearAll,
  className = '',
}: QuickFiltersBarProps) {
  const [activeFilters, setActiveFilters] = useState<Set<string>>(new Set())

  // Note: Filter activation is managed through state
  // Deep equality check for FilterRange objects would be needed for precise matching
  // For now, using simple state management
  // currentFilters could be used in future for syncing active state with URL params

  /**
   * Handle filter button click
   */
  const handleFilterClick = (filter: QuickFilter) => {
    const isActive = activeFilters.has(filter.id)

    if (isActive) {
      // Deactivate: remove filter
      const newActiveFilters = new Set(activeFilters)
      newActiveFilters.delete(filter.id)
      setActiveFilters(newActiveFilters)

      // Remove filter values
      const clearedFilters: Partial<ScreeningFilters> = {}
      Object.keys(filter.filters).forEach((key) => {
        clearedFilters[key as keyof ScreeningFilters] = undefined as any
      })
      onFilterChange(clearedFilters)
    } else {
      // Activate: apply filter
      const newActiveFilters = new Set(activeFilters)
      newActiveFilters.add(filter.id)
      setActiveFilters(newActiveFilters)

      onFilterChange(filter.filters)
    }
  }

  /**
   * Handle clear all button click
   */
  const handleClearAll = () => {
    setActiveFilters(new Set())
    if (onClearAll) {
      onClearAll()
    }
  }

  return (
    <Tooltip.Provider>
      <div className={`rounded-lg bg-white p-4 shadow-sm ${className}`}>
        {/* Header */}
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">
            인기 필터 <span className="text-xs font-normal text-gray-500">Quick Filters</span>
          </h3>

          {activeFilters.size > 0 && (
            <button
              onClick={handleClearAll}
              className="text-xs font-medium text-blue-600 hover:text-blue-700 hover:underline"
            >
              모두 지우기
            </button>
          )}
        </div>

        {/* Filter buttons - horizontal scrollable on mobile */}
        <div className="flex gap-2 overflow-x-auto pb-1">
          {QUICK_FILTERS.map((filter) => {
            const isActive = activeFilters.has(filter.id)

            return (
              <Tooltip.Root key={filter.id} delayDuration={300}>
                <Tooltip.Trigger asChild>
                  <button
                    onClick={() => handleFilterClick(filter)}
                    className={`
                      inline-flex items-center gap-1.5 whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium transition-all
                      ${
                        isActive
                          ? 'bg-blue-600 text-white shadow-sm hover:bg-blue-700'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:text-gray-900'
                      }
                    `}
                    aria-pressed={isActive}
                  >
                    <span>{filter.icon}</span>
                    <span>{filter.label}</span>
                  </button>
                </Tooltip.Trigger>

                <Tooltip.Portal>
                  <Tooltip.Content
                    className="z-50 max-w-xs rounded-lg bg-gray-900 px-3 py-2 text-sm text-white shadow-lg"
                    sideOffset={5}
                  >
                    {filter.tooltip}
                    <Tooltip.Arrow className="fill-gray-900" />
                  </Tooltip.Content>
                </Tooltip.Portal>
              </Tooltip.Root>
            )
          })}
        </div>

        {/* Active filters indicator */}
        {activeFilters.size > 0 && (
          <div className="mt-3 text-xs text-gray-600">
            {activeFilters.size}개 필터 활성화됨
          </div>
        )}
      </div>
    </Tooltip.Provider>
  )
}
