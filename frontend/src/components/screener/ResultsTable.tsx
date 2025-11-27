import { useRef } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import type { StockScreeningResult, ScreeningSortField, SortOrder } from '@/types/screening'
import { AddToWatchlistButton } from '@/components/watchlist'
import {
  formatCompactPrice,
  formatCompactVolume,
  formatCompactMarketCap,
  formatChangePercentage,
} from '@/utils/formatNumber'
import { InCellSparkline } from './InCellSparkline'
import { VolumeBar } from './VolumeBar'
// RangeIndicator is available but requires 52-week high/low data from backend
// import { RangeIndicator } from './RangeIndicator'
import { TrendBadge } from './TrendBadge'

/**
 * Sort configuration
 */
interface SortConfig {
  field: ScreeningSortField | null
  order: SortOrder
}

/**
 * Props for ResultsTable component
 */
interface ResultsTableProps {
  /** Stock data to display */
  data: StockScreeningResult[]
  /** Loading state */
  loading: boolean
  /** Current sort configuration */
  currentSort: SortConfig
  /** Callback when sort is requested */
  onSort: (field: ScreeningSortField) => void
  /** Callback when row is clicked */
  onRowClick?: (stock: StockScreeningResult) => void
}

/**
 * Column definition
 */
interface Column {
  /** Unique identifier for React key (must be unique across all columns) */
  id: string
  /** Field name used for sorting */
  sortField: ScreeningSortField
  label: string
  sortable: boolean
  align?: 'left' | 'right' | 'center'
  format?: (value: string | number | null | undefined) => string
}

/**
 * Format number with null handling
 */
const formatNumber = (value: string | number | null | undefined, decimals = 2): string => {
  if (value === null || value === undefined || typeof value === 'string') return '-'
  return value.toFixed(decimals)
}

/**
 * Format percentage with null handling and icon indicator
 */
const formatPercent = (value: string | number | null | undefined): string => {
  if (value === null || value === undefined || typeof value === 'string') return '-'
  return formatChangePercentage(value)
}

/**
 * Get change indicator icon
 */
const getChangeIcon = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '→'
  if (value > 0) return '↑'
  if (value < 0) return '↓'
  return '→'
}

/**
 * Format volume with high volume indicator
 * High volume threshold: 1M shares (can be adjusted based on market)
 */
const formatVolumeWithIcon = (volume: string | number | null | undefined): string => {
  if (volume === null || volume === undefined || typeof volume === 'string') return '-'
  const HIGH_VOLUME_THRESHOLD = 1_000_000 // 1 million shares
  const isHighVolume = volume > HIGH_VOLUME_THRESHOLD
  return `${formatCompactVolume(volume)}${isHighVolume ? ' 🔥' : ''}`
}

/**
 * Format market cap
 */
const formatMarketCapValue = (value: string | number | null | undefined): string => {
  if (value === null || value === undefined || typeof value === 'string') return '-'
  return formatCompactMarketCap(value)
}

/**
 * Format large numbers (market cap, price) - use compact format
 */
const formatPrice = (value: string | number | null | undefined): string => {
  if (value === null || value === undefined || typeof value === 'string') return '-'
  return formatCompactPrice(value)
}

/**
 * Column definitions with visual analytics columns
 * Note: 'id' must be unique for React keys, 'sortField' is used for sorting
 */
const columns: Column[] = [
  { id: 'col-code', sortField: 'code', label: 'Code', sortable: true, align: 'left' },
  { id: 'col-name', sortField: 'name', label: 'Name', sortable: true, align: 'left' },
  {
    id: 'col-price',
    sortField: 'current_price',
    label: 'Price',
    sortable: true,
    align: 'right',
    format: formatPrice,
  },
  {
    id: 'col-trend',
    sortField: 'price_change_1d',
    label: 'Trend',
    sortable: true,
    align: 'center',
  },
  {
    id: 'col-change',
    sortField: 'price_change_1d',
    label: 'Change%',
    sortable: true,
    align: 'right',
    format: formatPercent,
  },
  {
    id: 'col-volume',
    sortField: 'current_volume' as ScreeningSortField,
    label: 'Volume',
    sortable: true,
    align: 'right',
  },
  {
    id: 'col-market-cap',
    sortField: 'market_cap',
    label: 'Market Cap',
    sortable: true,
    align: 'right',
    format: formatMarketCapValue,
  },
  { id: 'col-per', sortField: 'per', label: 'PER', sortable: true, align: 'right', format: formatNumber },
  { id: 'col-pbr', sortField: 'pbr', label: 'PBR', sortable: true, align: 'right', format: formatNumber },
  {
    id: 'col-roe',
    sortField: 'roe',
    label: 'ROE%',
    sortable: true,
    align: 'right',
    format: (v) => formatNumber(v, 1),
  },
  {
    id: 'col-dividend',
    sortField: 'dividend_yield',
    label: 'Div%',
    sortable: true,
    align: 'right',
    format: (v) => formatNumber(v, 2),
  },
  {
    id: 'col-quality',
    sortField: 'quality_score',
    label: 'Quality',
    sortable: true,
    align: 'right',
    format: (v) => formatNumber(v, 0),
  },
  {
    id: 'col-actions',
    sortField: 'code', // Not used for sorting
    label: 'Actions',
    sortable: false,
    align: 'center',
  },
]

/**
 * ResultsTable component with sorting and virtualization
 *
 * Features:
 * - Sortable columns
 * - Virtual scrolling for performance
 * - Loading skeleton state
 * - Empty state
 * - Responsive design with horizontal scroll
 */
export default function ResultsTable({
  data,
  loading,
  currentSort,
  onSort,
  onRowClick,
}: ResultsTableProps) {
  const parentRef = useRef<HTMLDivElement>(null)

  // Virtualization for large datasets
  const rowVirtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 32, // Row height in pixels (ultra-compact)
    overscan: 5,
  })

  // Loading skeleton
  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-3 transition-colors">
        <div className="animate-pulse space-y-3">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded" />
          {[...Array(10)].map((_, i) => (
            <div key={i} className="h-9 bg-gray-100 dark:bg-gray-800 rounded" />
          ))}
        </div>
      </div>
    )
  }

  // Empty state
  if (data.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-12 transition-colors">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100 transition-colors">No results found</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 transition-colors">
            Try adjusting your filters to see more results.
          </p>
        </div>
      </div>
    )
  }

  // Render sort icon
  const renderSortIcon = (sortField: ScreeningSortField) => {
    if (currentSort.field !== sortField) {
      return (
        <svg className="h-4 w-4 text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 9l4-4 4 4m0 6l-4 4-4-4"
          />
        </svg>
      )
    }

    return currentSort.order === 'asc' ? (
      <svg className="h-4 w-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
    ) : (
      <svg className="h-4 w-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden transition-colors">
      <div className="overflow-x-auto" ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-800 sticky top-0 z-20 transition-colors">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.id}
                  scope="col"
                  className={`px-2.5 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider transition-colors ${
                    column.align === 'right'
                      ? 'text-right'
                      : column.align === 'center'
                      ? 'text-center'
                      : 'text-left'
                  }`}
                >
                  {column.sortable ? (
                    <button
                      onClick={() => onSort(column.sortField)}
                      className="flex items-center space-x-1 hover:text-gray-900 dark:hover:text-gray-100 transition-colors group w-full justify-between"
                    >
                      <span>{column.label}</span>
                      {renderSortIcon(column.sortField)}
                    </button>
                  ) : (
                    <span>{column.label}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800 transition-colors">
            <tr style={{ height: `${rowVirtualizer.getTotalSize()}px` }}>
              <td></td>
            </tr>
            {rowVirtualizer.getVirtualItems().map((virtualRow) => {
              const stock = data[virtualRow.index]
              return (
                <tr
                  key={stock.code}
                  onClick={() => onRowClick?.(stock)}
                  className="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: `${virtualRow.size}px`,
                    transform: `translateY(${virtualRow.start}px)`,
                  }}
                >
                  {columns.map((column) => {
                    // Special handling for Actions column
                    if (column.label === 'Actions') {
                      return (
                        <td
                          key="actions"
                          className="px-2.5 py-1 text-center whitespace-nowrap"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <AddToWatchlistButton
                            stock={{
                              code: stock.code,
                              name: stock.name,
                              market: stock.market as 'KOSPI' | 'KOSDAQ',
                              current_price: stock.current_price || undefined,
                              change_percent: stock.price_change_1d || undefined,
                              volume: stock.current_volume || undefined,
                            }}
                            variant="icon"
                            size="sm"
                          />
                        </td>
                      )
                    }

                    // Trend column with TrendBadge and optional Sparkline
                    if (column.label === 'Trend') {
                      return (
                        <td
                          key={column.id}
                          className="px-2.5 py-1 whitespace-nowrap text-center"
                        >
                          <div className="flex items-center justify-center gap-1">
                            {/* Sparkline (if price history available) */}
                            {stock.price_history_7d && stock.price_history_7d.length >= 2 && (
                              <InCellSparkline
                                data={stock.price_history_7d}
                                width={36}
                                height={16}
                                color="auto"
                              />
                            )}
                            {/* Trend Badge */}
                            <TrendBadge
                              shortTermChange={stock.price_change_1w}
                              longTermChange={stock.price_change_1m}
                              size="sm"
                            />
                          </div>
                        </td>
                      )
                    }

                    // Price column with optional sparkline
                    if (column.label === 'Price') {
                      return (
                        <td
                          key={column.id}
                          className="px-2.5 py-1 text-xs text-gray-900 dark:text-gray-100 whitespace-nowrap text-right transition-colors"
                        >
                          <div className="flex items-center justify-end gap-1">
                            <span>{formatPrice(stock.current_price)}</span>
                          </div>
                        </td>
                      )
                    }

                    // Volume column with VolumeBar
                    if (column.label === 'Volume') {
                      const volume = stock.current_volume
                      const avgVolume = stock.average_volume
                      const volumeSurge = stock.volume_surge_pct

                      // If we have volume surge percentage, calculate implied average
                      const impliedAvgVolume = volumeSurge && volume
                        ? volume / (1 + volumeSurge / 100)
                        : avgVolume

                      return (
                        <td
                          key={column.id}
                          className="px-2.5 py-1 text-xs text-gray-900 dark:text-gray-100 whitespace-nowrap text-right transition-colors"
                        >
                          <div className="flex items-center justify-end gap-1">
                            {impliedAvgVolume ? (
                              <VolumeBar
                                volume={volume}
                                averageVolume={impliedAvgVolume}
                                maxWidth={40}
                                height={10}
                                showRatio={false}
                              />
                            ) : null}
                            <span>{formatVolumeWithIcon(volume)}</span>
                          </div>
                        </td>
                      )
                    }

                    const value = stock[column.sortField as keyof StockScreeningResult]
                    // Skip array values (like price_history_7d) for text formatting
                    const displayValue = Array.isArray(value) ? null : value
                    let formattedValue: string | number | null | undefined = column.format
                      ? column.format(displayValue as string | number | null | undefined)
                      : displayValue

                    // Add change icon for Change% column
                    if (column.label === 'Change%' && typeof value === 'number') {
                      const icon = getChangeIcon(value)
                      formattedValue = `${icon} ${formattedValue}`
                    }

                    // Add value indicator for PER
                    if (column.sortField === 'per' && typeof value === 'number') {
                      if (value > 0 && value < 10) {
                        formattedValue = `${formattedValue} 💎` // Low P/E indicator
                      }
                    }

                    // Special styling for Change%
                    let cellClassName = 'px-2.5 py-1 text-xs text-gray-900 dark:text-gray-100 whitespace-nowrap transition-colors'
                    if (column.label === 'Change%' && typeof value === 'number') {
                      cellClassName += value > 0 ? ' text-green-600 dark:text-green-400' : value < 0 ? ' text-red-600 dark:text-red-400' : ''
                    }

                    // Conditional formatting: bold for top/bottom performers
                    if (column.label === 'Change%' && typeof value === 'number') {
                      if (Math.abs(value) > 5) {
                        cellClassName += ' font-bold'
                      }
                    }

                    // Fade low volume stocks (less than 100K shares)
                    const currentVolume = stock.current_volume
                    const LOW_VOLUME_THRESHOLD = 100_000 // 100K shares
                    if (currentVolume && typeof currentVolume === 'number' && currentVolume < LOW_VOLUME_THRESHOLD) {
                      cellClassName += ' opacity-70'
                    }

                    if (column.align === 'right') cellClassName += ' text-right'
                    if (column.align === 'center') cellClassName += ' text-center'

                    return (
                      <td key={column.id} className={cellClassName}>
                        {formattedValue}
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
