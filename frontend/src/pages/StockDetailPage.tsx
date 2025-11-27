import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useStockData } from '@/hooks/useStockData'
import { usePriceChart } from '@/hooks/usePriceChart'
import { useFreemiumAccess } from '@/hooks/useFreemiumAccess'
import StockHeader from '@/components/stock/StockHeader'
import PriceChart from '@/components/stock/PriceChart'
import { AdvancedChartContainer } from '@/components/charts'
import StockTabs from '@/components/stock/StockTabs'
import { FreemiumBanner } from '@/components/freemium'

/**
 * Stock Detail Page
 *
 * Comprehensive stock detail page with:
 * - Stock header (name, code, price, change)
 * - Price chart (TradingView Lightweight Charts)
 * - Tabbed content (Overview, Financials, Valuation, Technical)
 *
 * Route: /stocks/:code
 *
 * @example
 * Navigate to /stocks/005930 for Samsung Electronics
 */
export default function StockDetailPage() {
  const { code } = useParams<{ code: string }>()
  const navigate = useNavigate()

  // Chart mode state (basic or advanced)
  const [useAdvancedChart, setUseAdvancedChart] = useState(true)

  // Fetch stock data
  const {
    data: stock,
    isLoading: stockLoading,
    error: stockError,
  } = useStockData(code)

  // Fetch price chart data
  const {
    data: priceData,
    isLoading: chartLoading,
    timeframe,
    setTimeframe,
  } = usePriceChart(code, '1M')

  // Freemium access control
  const { isAuthenticated, canViewFinancials, canViewAllTechnicals } = useFreemiumAccess()

  // Loading state
  if (stockLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-solid border-blue-600 border-r-transparent mb-4"></div>
          <p className="text-lg text-gray-600">주식 정보를 불러오는 중...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (stockError) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-red-100 rounded-full">
            <svg
              className="w-6 h-6 text-red-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 text-center mb-2">
            주식 정보를 불러올 수 없습니다
          </h2>
          <p className="text-sm text-gray-600 text-center mb-6">
            {stockError.message || '알 수 없는 오류가 발생했습니다.'}
          </p>
          <button
            onClick={() => navigate('/screener')}
            className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            스크리너로 돌아가기
          </button>
        </div>
      </div>
    )
  }

  // No data state
  if (!stock) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-yellow-100 rounded-full">
            <svg
              className="w-6 h-6 text-yellow-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 text-center mb-2">
            주식 정보가 없습니다
          </h2>
          <p className="text-sm text-gray-600 text-center mb-6">
            종목 코드: {code}
          </p>
          <button
            onClick={() => navigate('/screener')}
            className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            스크리너로 돌아가기
          </button>
        </div>
      </div>
    )
  }

  // Main content
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Stock Header */}
      <StockHeader stock={stock} />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Freemium Banner for unauthenticated users */}
        {!isAuthenticated && (
          <FreemiumBanner type="stock-detail" />
        )}

        {/* Breadcrumb */}
        <nav className="flex" aria-label="Breadcrumb">
          <ol className="inline-flex items-center space-x-1 md:space-x-3">
            <li className="inline-flex items-center">
              <button
                onClick={() => navigate('/')}
                className="inline-flex items-center text-sm font-medium text-gray-700 hover:text-blue-600"
              >
                <svg
                  className="w-4 h-4 mr-2"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                </svg>
                홈
              </button>
            </li>
            <li>
              <div className="flex items-center">
                <svg
                  className="w-6 h-6 text-gray-400"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
                <button
                  onClick={() => navigate('/screener')}
                  className="ml-1 text-sm font-medium text-gray-700 hover:text-blue-600 md:ml-2"
                >
                  스크리너
                </button>
              </div>
            </li>
            <li aria-current="page">
              <div className="flex items-center">
                <svg
                  className="w-6 h-6 text-gray-400"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="ml-1 text-sm font-medium text-gray-500 md:ml-2">
                  {stock.name}
                </span>
              </div>
            </li>
          </ol>
        </nav>

        {/* Chart Mode Toggle */}
        <div className="flex items-center justify-end gap-2">
          <span className="text-sm text-gray-600 dark:text-gray-400">차트 모드:</span>
          <button
            onClick={() => setUseAdvancedChart(false)}
            className={`px-3 py-1 text-sm rounded-l-md border ${
              !useAdvancedChart
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'
            }`}
          >
            기본
          </button>
          <button
            onClick={() => setUseAdvancedChart(true)}
            className={`px-3 py-1 text-sm rounded-r-md border-t border-b border-r ${
              useAdvancedChart
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'
            }`}
          >
            고급
          </button>
        </div>

        {/* Price Chart */}
        {useAdvancedChart ? (
          <AdvancedChartContainer
            symbol={code || ''}
            data={priceData}
            loading={chartLoading}
            timeframe={timeframe}
            onTimeframeChange={setTimeframe}
            height={500}
          />
        ) : (
          <PriceChart
            data={priceData}
            loading={chartLoading}
            timeframe={timeframe}
            onTimeframeChange={setTimeframe}
          />
        )}

        {/* Stock Tabs */}
        <StockTabs
          stock={stock}
          canViewFinancials={canViewFinancials}
          canViewAllTechnicals={canViewAllTechnicals}
        />
      </div>
    </div>
  )
}
