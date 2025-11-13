import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useScreening } from '@/hooks/useScreening'
import { useFilterPresets } from '@/hooks/useFilterPresets'
import { useURLSync } from '@/hooks/useURLSync'
import { useFreemiumAccess } from '@/hooks/useFreemiumAccess'
import { trackScreening, canPerformScreening } from '@/utils/usageTracker'
import FilterPanel from '@/components/screener/FilterPanel'
import ResultsTable from '@/components/screener/ResultsTable'
import Pagination from '@/components/common/Pagination'
import ExportButton from '@/components/screener/ExportButton'
import { FreemiumBanner, LimitReachedModal } from '@/components/freemium'
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

  const { presets, savePreset, deletePreset } = useFilterPresets()
  const {
    isAuthenticated,
    maxScreeningResults,
    dailyScreeningLimit,
    screeningsToday,
    screeningsRemaining,
    canExportResults,
    canSavePresets,
  } = useFreemiumAccess()

  const [showLimitModal, setShowLimitModal] = useState(false)

  // Sync filters/sort/pagination with URL
  useURLSync(filters, setFilters, sort, setSort, pagination, setPagination)

  // Check usage limit before screening
  const checkUsageLimit = (): boolean => {
    if (isAuthenticated) return true

    if (!canPerformScreening(dailyScreeningLimit)) {
      setShowLimitModal(true)
      return false
    }

    trackScreening()
    return true
  }

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

  // Apply freemium limits to results
  const displayedStocks = !isAuthenticated && data?.stocks && maxScreeningResults > 0
    ? data.stocks.slice(0, maxScreeningResults)
    : data?.stocks || []

  const isResultsLimited = !isAuthenticated && (data?.stocks?.length || 0) > maxScreeningResults

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

        {/* Freemium Banner */}
        {!isAuthenticated && (
          <FreemiumBanner
            type="screener"
            message={`🎁 Sign up for unlimited searches! (${screeningsToday}/${dailyScreeningLimit} used today)`}
          />
        )}

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
                presets={presets}
                onSavePreset={(name, description) => savePreset(name, filters, description)}
                onDeletePreset={deletePreset}
              />
            </div>
          </div>

          {/* Right column - Results (3/4 width on large screens) */}
          <div className="lg:col-span-3 space-y-4">
            {/* Results count and export */}
            {!isLoading && data && (
              <div className="flex items-center justify-between flex-wrap gap-2">
                <p className="text-sm text-gray-700">
                  {isResultsLimited ? (
                    <>
                      Showing <span className="font-semibold">{maxScreeningResults}</span> of{' '}
                      <span className="font-semibold">{data.meta.total}</span> stocks{' '}
                      <span className="text-blue-600 font-medium">(Sign up for full results)</span>
                    </>
                  ) : (
                    <>
                      Found <span className="font-semibold">{data.meta.total}</span> stocks
                    </>
                  )}
                  {data.query_time_ms && (
                    <span className="text-gray-500 ml-2">
                      ({data.query_time_ms}ms)
                    </span>
                  )}
                </p>
                {canExportResults && <ExportButton data={data.stocks} />}
                {!canExportResults && (
                  <button
                    disabled
                    className="px-4 py-2 text-sm font-medium text-gray-400 bg-gray-100 rounded-md cursor-not-allowed"
                    title="Sign up to export results"
                  >
                    Export (Sign up required)
                  </button>
                )}
              </div>
            )}

            {/* Results Table */}
            <ResultsTable
              data={displayedStocks}
              loading={isLoading}
              currentSort={{ field: sort.sortBy, order: sort.order }}
              onSort={handleSort}
              onRowClick={handleRowClick}
            />

            {/* Limited results notice */}
            {isResultsLimited && (
              <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 text-center">
                <p className="text-blue-900 font-medium mb-2">
                  📊 {data!.meta.total - maxScreeningResults} more stocks match your criteria
                </p>
                <p className="text-blue-700 text-sm mb-3">
                  Sign up for free to view all {data!.meta.total} results and unlock unlimited searches
                </p>
                <div className="flex gap-2 justify-center">
                  <button
                    onClick={() => navigate('/register')}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                  >
                    Sign Up Free
                  </button>
                  <button
                    onClick={() => navigate('/login')}
                    className="bg-white text-blue-600 border-2 border-blue-600 px-6 py-2 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
                  >
                    Login
                  </button>
                </div>
              </div>
            )}

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

        {/* Limit Reached Modal */}
        <LimitReachedModal
          open={showLimitModal}
          onClose={() => setShowLimitModal(false)}
          actionsUsed={screeningsToday}
          dailyLimit={dailyScreeningLimit}
        />
      </div>
    </div>
  )
}
