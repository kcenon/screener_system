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
import { useTranslation } from 'react-i18next'
import * as Tooltip from '@radix-ui/react-tooltip'
import type { ScreeningFilters } from '@/types/screening'

/**
 * Quick filter preset definition
 */
export interface QuickFilter {
  id: string
  labelKey: string
  icon: string
  tooltipKey: string
  filters: Partial<ScreeningFilters>
}

/**
 * Preset filter definitions
 * Based on IMPROVEMENT-004 specification, adjusted for actual ScreeningFilters type
 * Uses i18n keys for labels and tooltips
 */
const QUICK_FILTERS: QuickFilter[] = [
  {
    id: 'top-gainers',
    labelKey: 'filters.top_gainers',
    icon: '⬆',
    tooltipKey: 'filters.top_gainers_tooltip',
    filters: {
      price_change_1d: { min: 5 },
    },
  },
  {
    id: 'top-losers',
    labelKey: 'filters.top_losers',
    icon: '⬇',
    tooltipKey: 'filters.top_losers_tooltip',
    filters: {
      price_change_1d: { max: -5 },
    },
  },
  {
    id: 'high-volume',
    labelKey: 'filters.high_volume',
    icon: '📊',
    tooltipKey: 'filters.high_volume_tooltip',
    filters: {
      volume_surge_pct: { min: 100 },
    },
  },
  {
    id: '52w-high',
    labelKey: 'filters.one_year_high',
    icon: '🏔',
    tooltipKey: 'filters.one_year_high_tooltip',
    filters: {
      price_change_1y: { min: 50 },
    },
  },
  {
    id: 'high-dividend',
    labelKey: 'filters.high_dividend',
    icon: '💰',
    tooltipKey: 'filters.high_dividend_tooltip',
    filters: {
      dividend_yield: { min: 4 },
    },
  },
  {
    id: 'low-pe',
    labelKey: 'filters.low_pe',
    icon: '💎',
    tooltipKey: 'filters.low_pe_tooltip',
    filters: {
      per: { min: 0.1, max: 10 },
    },
  },
  {
    id: 'high-growth',
    labelKey: 'filters.high_growth',
    icon: '📈',
    tooltipKey: 'filters.high_growth_tooltip',
    filters: {
      revenue_growth_yoy: { min: 20 },
    },
  },
  {
    id: 'small-cap',
    labelKey: 'filters.small_cap',
    icon: '🐣',
    tooltipKey: 'filters.small_cap_tooltip',
    filters: {
      market_cap: { max: 1000 }, // billion KRW
    },
  },
  {
    id: 'large-cap',
    labelKey: 'filters.large_cap',
    icon: '🦁',
    tooltipKey: 'filters.large_cap_tooltip',
    filters: {
      market_cap: { min: 10000 }, // billion KRW
    },
  },
  {
    id: 'high-quality',
    labelKey: 'filters.high_quality',
    icon: '✨',
    tooltipKey: 'filters.high_quality_tooltip',
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
  const { t } = useTranslation('screener')
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
      <div className={`rounded-lg bg-white dark:bg-gray-900 p-4 shadow-sm border border-gray-200 dark:border-gray-700 transition-colors ${className}`}>
        {/* Header */}
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 transition-colors">
            {t('popular_filters')} <span className="text-xs font-normal text-gray-500 dark:text-gray-400">{t('quick_filters')}</span>
          </h3>

          {activeFilters.size > 0 && (
            <button
              onClick={handleClearAll}
              className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:underline transition-colors"
            >
              {t('actions.clear_all', { ns: 'common' })}
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
                          ? 'bg-blue-600 dark:bg-blue-500 text-white shadow-sm hover:bg-blue-700 dark:hover:bg-blue-600'
                          : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'
                      }
                    `}
                    aria-pressed={isActive}
                  >
                    <span>{filter.icon}</span>
                    <span>{t(filter.labelKey)}</span>
                  </button>
                </Tooltip.Trigger>

                <Tooltip.Portal>
                  <Tooltip.Content
                    className="z-50 max-w-xs rounded-lg bg-gray-900 dark:bg-gray-950 px-3 py-2 text-sm text-white shadow-lg"
                    sideOffset={5}
                  >
                    {t(filter.tooltipKey)}
                    <Tooltip.Arrow className="fill-gray-900 dark:fill-gray-950" />
                  </Tooltip.Content>
                </Tooltip.Portal>
              </Tooltip.Root>
            )
          })}
        </div>

        {/* Active filters indicator */}
        {activeFilters.size > 0 && (
          <div className="mt-3 text-xs text-gray-600 dark:text-gray-400 transition-colors">
            {t('filters_active', { count: activeFilters.size })}
          </div>
        )}
      </div>
    </Tooltip.Provider>
  )
}
