/**
 * StockComparisonPage Component
 * Main page for comparing multiple stocks side-by-side
 */

import { BarChart3, Share2, Download, RefreshCw } from 'lucide-react'
import { useStockComparison } from '../hooks/useStockComparison'
import { useComparisonData } from '../hooks/useComparisonData'
import {
  StockChip,
  ComparisonTable,
  ComparisonCharts,
} from '../components/comparison'
import { StockSelector } from '../components/comparison/StockSelector'
import { MAX_COMPARISON_STOCKS, COMPARISON_METRICS } from '../types/comparison'
import { exportToCSV, downloadBlob } from '../utils/comparison'

export default function StockComparisonPage() {
  const { stockCodes, addStock, removeStock, clearAll, isMaxReached } =
    useStockComparison()

  const { stocks, isLoading, errors, refetch } = useComparisonData(stockCodes)

  const handleExport = () => {
    const metricKeys = COMPARISON_METRICS.map((m) => m.key)
    const blob = exportToCSV(stocks, metricKeys)
    const timestamp = new Date().toISOString().split('T')[0]
    downloadBlob(blob, `stock-comparison-${timestamp}.csv`)
  }

  const handleShare = () => {
    // Copy URL to clipboard
    navigator.clipboard.writeText(window.location.href)
    alert('Comparison URL copied to clipboard!')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <BarChart3 className="w-8 h-8 text-blue-600" />
                Stock Comparison
              </h1>
              <p className="mt-2 text-gray-600">
                Compare up to {MAX_COMPARISON_STOCKS} stocks side-by-side
              </p>
            </div>

            {stockCodes.length >= 2 && (
              <div className="flex items-center gap-3">
                <button
                  onClick={refetch}
                  disabled={isLoading}
                  className="
                    px-4 py-2 rounded-lg
                    text-gray-700 bg-white border border-gray-300
                    hover:bg-gray-50
                    disabled:opacity-50 disabled:cursor-not-allowed
                    flex items-center gap-2
                  "
                >
                  <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
                <button
                  onClick={handleShare}
                  className="
                    px-4 py-2 rounded-lg
                    text-gray-700 bg-white border border-gray-300
                    hover:bg-gray-50
                    flex items-center gap-2
                  "
                >
                  <Share2 className="w-4 h-4" />
                  Share
                </button>
                <button
                  onClick={handleExport}
                  disabled={isLoading}
                  className="
                    px-4 py-2 rounded-lg
                    text-gray-700 bg-white border border-gray-300
                    hover:bg-gray-50
                    disabled:opacity-50 disabled:cursor-not-allowed
                    flex items-center gap-2
                  "
                >
                  <Download className="w-4 h-4" />
                  Export CSV
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stock Selection Area */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex-shrink-0">
              Select Stocks
            </h2>
            <div className="flex-1 w-full sm:w-auto">
              <StockSelector
                selectedCodes={stockCodes}
                onAddStock={addStock}
                maxStocks={MAX_COMPARISON_STOCKS}
              />
            </div>
            {stockCodes.length > 0 && (
              <button
                onClick={clearAll}
                className="
                  text-sm text-red-600 hover:text-red-700
                  underline flex-shrink-0
                "
              >
                Clear All
              </button>
            )}
          </div>

          {/* Selected Stocks */}
          {stockCodes.length > 0 && (
            <div className="flex flex-wrap gap-3">
              {stocks.map((stock) => (
                <StockChip
                  key={stock.code}
                  code={stock.code}
                  name={stock.name || 'Loading...'}
                  market={stock.market}
                  onRemove={removeStock}
                />
              ))}
            </div>
          )}

          {/* Max Limit Info */}
          <div className="mt-4 flex items-center gap-2 text-sm">
            <div className="flex items-center gap-1">
              {[...Array(MAX_COMPARISON_STOCKS)].map((_, i) => (
                <div
                  key={i}
                  className={`
                    w-3 h-3 rounded-full
                    ${i < stockCodes.length ? 'bg-blue-500' : 'bg-gray-300'}
                  `}
                />
              ))}
            </div>
            <span className="text-gray-600">
              {stockCodes.length} / {MAX_COMPARISON_STOCKS} stocks selected
            </span>
            {isMaxReached && (
              <span className="text-orange-600 font-medium">
                (Maximum reached)
              </span>
            )}
          </div>
        </div>

        {/* Empty State */}
        {stockCodes.length === 0 && (
          <div className="bg-white rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
            <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Start Comparing Stocks
            </h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Search and add stocks above to begin your comparison. You can
              compare up to {MAX_COMPARISON_STOCKS} stocks at once.
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              <button
                onClick={() => addStock('005930')}
                className="
                  px-4 py-2 rounded-lg
                  text-white bg-blue-600 hover:bg-blue-700
                "
              >
                Try Samsung (005930)
              </button>
              <button
                onClick={() => addStock('000660')}
                className="
                  px-4 py-2 rounded-lg
                  text-gray-700 bg-white border border-gray-300
                  hover:bg-gray-50
                "
              >
                Try SK Hynix (000660)
              </button>
            </div>
          </div>
        )}

        {/* Comparison Table */}
        {stockCodes.length >= 2 && (
          <>
            {/* Error Messages */}
            {errors.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <h4 className="text-red-900 font-semibold mb-2">
                  Failed to load some stocks:
                </h4>
                <ul className="text-sm text-red-700 list-disc list-inside">
                  {errors.map(({ code, error }) => (
                    <li key={code}>
                      {code}: {String(error)}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Comparison Table */}
            <ComparisonTable stocks={stocks} />

            {/* Comparison Charts */}
            <ComparisonCharts stocks={stocks} className="mt-6" />
          </>
        )}

        {/* Single Stock Info */}
        {stockCodes.length === 1 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <p className="text-blue-900 font-medium">
              Add at least one more stock to start comparing
            </p>
            <p className="text-blue-700 text-sm mt-1">
              You need minimum 2 stocks for comparison
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
