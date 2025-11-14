import { useRef } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import type { StockScreeningResult, ScreeningSortField, SortOrder } from '@/types/screening'
import { AddToWatchlistButton } from '@/components/watchlist'
import { formatCompactPrice } from '@/utils/formatNumber'

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
  key: ScreeningSortField
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
 * Format percentage with null handling
 */
const formatPercent = (value: string | number | null | undefined): string => {
  if (value === null || value === undefined || typeof value === 'string') return '-'
  const formatted = value.toFixed(2)
  return value > 0 ? `+${formatted}%` : `${formatted}%`
}

/**
 * Format large numbers (market cap, price) - use compact format
 */
const formatPrice = (value: string | number | null | undefined): string => {
  if (value === null || value === undefined || typeof value === 'string') return '-'
  return formatCompactPrice(value)
}

/**
 * Column definitions
 */
const columns: Column[] = [
  { key: 'code', label: 'Code', sortable: true, align: 'left' },
  { key: 'name', label: 'Name', sortable: true, align: 'left' },
  {
    key: 'current_price',
    label: 'Price',
    sortable: true,
    align: 'right',
    format: formatPrice,
  },
  {
    key: 'price_change_1d',
    label: 'Change%',
    sortable: true,
    align: 'right',
    format: formatPercent,
  },
  { key: 'per', label: 'PER', sortable: true, align: 'right', format: formatNumber },
  { key: 'pbr', label: 'PBR', sortable: true, align: 'right', format: formatNumber },
  {
    key: 'roe',
    label: 'ROE%',
    sortable: true,
    align: 'right',
    format: (v) => formatNumber(v, 1),
  },
  {
    key: 'dividend_yield',
    label: 'Div%',
    sortable: true,
    align: 'right',
    format: (v) => formatNumber(v, 2),
  },
  {
    key: 'quality_score',
    label: 'Quality',
    sortable: true,
    align: 'right',
    format: (v) => formatNumber(v, 0),
  },
  {
    key: 'code' as ScreeningSortField, // Non-sortable actions column
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
    estimateSize: () => 36, // Row height in pixels (compact)
    overscan: 5,
  })

  // Loading skeleton
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-3">
        <div className="animate-pulse space-y-3">
          <div className="h-8 bg-gray-200 rounded" />
          {[...Array(10)].map((_, i) => (
            <div key={i} className="h-9 bg-gray-100 rounded" />
          ))}
        </div>
      </div>
    )
  }

  // Empty state
  if (data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
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
          <h3 className="mt-2 text-sm font-medium text-gray-900">No results found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your filters to see more results.
          </p>
        </div>
      </div>
    )
  }

  // Render sort icon
  const renderSortIcon = (columnKey: ScreeningSortField) => {
    if (currentSort.field !== columnKey) {
      return (
        <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
      <svg className="h-4 w-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
    ) : (
      <svg className="h-4 w-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto" ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50 sticky top-0 z-20">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  scope="col"
                  className={`px-3 py-2 text-xs font-medium text-gray-700 uppercase tracking-wider ${
                    column.align === 'right'
                      ? 'text-right'
                      : column.align === 'center'
                      ? 'text-center'
                      : 'text-left'
                  }`}
                >
                  {column.sortable ? (
                    <button
                      onClick={() => onSort(column.key)}
                      className="flex items-center space-x-1 hover:text-gray-900 transition-colors group w-full justify-between"
                    >
                      <span>{column.label}</span>
                      {renderSortIcon(column.key)}
                    </button>
                  ) : (
                    <span>{column.label}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            <tr style={{ height: `${rowVirtualizer.getTotalSize()}px` }}>
              <td></td>
            </tr>
            {rowVirtualizer.getVirtualItems().map((virtualRow) => {
              const stock = data[virtualRow.index]
              return (
                <tr
                  key={stock.code}
                  onClick={() => onRowClick?.(stock)}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
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
                          className="px-3 py-2 text-center whitespace-nowrap"
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

                    const value = stock[column.key as keyof StockScreeningResult]
                    const formattedValue = column.format ? column.format(value) : value

                    // Special styling for change%
                    let cellClassName = 'px-3 py-2 text-xs text-gray-900 whitespace-nowrap'
                    if (column.key === 'price_change_1d' && typeof value === 'number') {
                      cellClassName += value > 0 ? ' text-green-600' : value < 0 ? ' text-red-600' : ''
                    }
                    if (column.align === 'right') cellClassName += ' text-right'
                    if (column.align === 'center') cellClassName += ' text-center'

                    return (
                      <td key={column.key} className={cellClassName}>
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
