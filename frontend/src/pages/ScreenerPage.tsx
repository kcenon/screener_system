import { useNavigate } from 'react-router-dom'
import { useScreening } from '@/hooks/useScreening'
import FilterPanel from '@/components/screener/FilterPanel'
import ResultsTable from '@/components/screener/ResultsTable'
import Pagination from '@/components/common/Pagination'
import type { ScreeningSortField, StockScreeningResult } from '@/types/screening'

/**
 * Main Stock Screener Page
 *
 * Features:
 * - Two-column layout (filters left, results right)
 * - Responsive design (stacks on mobile)
 * - Connected to useScreening hook
 * - Handles loading/error states
 * - Pagination support
 * - Sort functionality
 * - Navigate to stock detail on row click
 */
export default function ScreenerPage() {
  const navigate = useNavigate()
  const {
    data,
    isLoading,
    error,
    filters,
    sort,
    pagination,
    setFilters,
    setSort,
    setPagination,
  } = useScreening()

  // Handle sort column click
  const handleSort = (field: ScreeningSortField) => {
    if (sort.sortBy === field) {
      // Toggle order if same field
      setSort({ sortBy: field, order: sort.order === 'asc' ? 'desc' : 'asc' })
    } else {
      // Default to descending for new field
      setSort({ sortBy: field, order: 'desc' })
    }
  }

  // Handle page change
  const handlePageChange = (page: number) => {
    setPagination({ ...pagination, offset: (page - 1) * pagination.limit })
  }

  // Handle page size change
  const handlePageSizeChange = (pageSize: number) => {
    setPagination({ offset: 0, limit: pageSize })
  }

  // Handle clear all filters
  const handleClearFilters = () => {
    setFilters({ market: 'ALL' })
  }

  // Handle row click - navigate to stock detail
  const handleRowClick = (stock: StockScreeningResult) => {
    navigate(`/stocks/${stock.code}`)
  }

  // Calculate current page (1-indexed)
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Stock Screener</h1>
          <p className="mt-2 text-sm text-gray-600">
            Filter and analyze Korean stocks based on fundamental and technical indicators
          </p>
        </div>

        {/* Error state */}
        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error loading data</h3>
                <p className="mt-1 text-sm text-red-700">{error.message}</p>
              </div>
            </div>
          </div>
        )}

        {/* Main content - Two column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left column - Filters (1/4 width on large screens) */}
          <div className="lg:col-span-1">
            <div className="sticky top-6">
              <FilterPanel
                filters={filters}
                onFiltersChange={setFilters}
                onClearFilters={handleClearFilters}
              />
            </div>
          </div>

          {/* Right column - Results (3/4 width on large screens) */}
          <div className="lg:col-span-3 space-y-4">
            {/* Results count */}
            {!isLoading && data && (
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-700">
                  Found <span className="font-semibold">{data.meta.total}</span> stocks
                  {data.query_time_ms && (
                    <span className="text-gray-500 ml-2">
                      ({data.query_time_ms}ms)
                    </span>
                  )}
                </p>
              </div>
            )}

            {/* Results Table */}
            <ResultsTable
              data={data?.stocks || []}
              loading={isLoading}
              currentSort={{ field: sort.sortBy, order: sort.order }}
              onSort={handleSort}
              onRowClick={handleRowClick}
            />

            {/* Pagination */}
            {!isLoading && data && data.meta.total > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                <Pagination
                  currentPage={currentPage}
                  totalPages={data.meta.total_pages}
                  totalResults={data.meta.total}
                  pageSize={pagination.limit}
                  onPageChange={handlePageChange}
                  onPageSizeChange={handlePageSizeChange}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
