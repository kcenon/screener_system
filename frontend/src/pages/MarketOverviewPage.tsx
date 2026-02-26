/**
 * Market Overview Page (FE-009)
 *
 * Comprehensive market overview dashboard showing:
 * - Market indices (KOSPI, KOSDAQ, KRX100)
 * - Market breadth indicators
 * - Sector performance heatmap
 * - Top gainers and losers
 * - Most active stocks by volume
 * - Historical market trends
 */

import { useState } from 'react'
import { MarketIndicesWidget } from '../components/market/MarketIndicesWidget'
import { MarketBreadthWidget } from '../components/market/MarketBreadthWidget'
import { SectorHeatmap } from '../components/market/SectorHeatmap'
import { MarketMoversWidget } from '../components/market/MarketMoversWidget'
import { MostActiveWidget } from '../components/market/MostActiveWidget'
import { MarketTrendChart } from '../components/market/MarketTrendChart'

/**
 * Market Overview Page Component
 */
export function MarketOverviewPage() {
  const [autoRefresh, setAutoRefresh] = useState(true)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <div className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">시장 현황</h1>
              <p className="mt-1 text-sm text-gray-600">
                한국 주식 시장의 실시간 현황과 섹터 분석을 한눈에 확인하세요
              </p>
            </div>

            {/* Auto-refresh toggle */}
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={e => setAutoRefresh(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">자동 새로고침</span>
              </label>
              {autoRefresh && (
                <span className="text-xs text-gray-500">(1분마다)</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-6">
        <div className="space-y-6">
          {/* Row 1: Market Indices */}
          <MarketIndicesWidget
            autoRefresh={autoRefresh}
            refreshInterval={60000}
          />

          {/* Row 2: Market Breadth */}
          <MarketBreadthWidget
            autoRefresh={autoRefresh}
            refreshInterval={60000}
          />

          {/* Row 3: Sector Heatmap */}
          <SectorHeatmap defaultTimeframe="1D" autoRefresh={autoRefresh} />

          {/* Row 4: Market Movers */}
          <MarketMoversWidget
            defaultMarket="ALL"
            limit={10}
            autoRefresh={autoRefresh}
          />

          {/* Row 5: Most Active Stocks */}
          <MostActiveWidget
            defaultMarket="ALL"
            limit={20}
            autoRefresh={autoRefresh}
          />

          {/* Row 6: Market Trend Chart */}
          <MarketTrendChart
            defaultTimeframe="3M"
            indices={['KOSPI', 'KOSDAQ']}
            height={400}
          />
        </div>
      </div>

      {/* Footer info */}
      <div className="container mx-auto px-4 py-6">
        <div className="rounded-lg bg-blue-50 p-4 text-center">
          <p className="text-sm text-blue-800">
            💡 <strong>Tip:</strong> 섹터를 클릭하면 해당 섹터의 종목 목록을
            확인할 수 있으며, 종목명을 클릭하면 상세 정보를 볼 수 있습니다.
          </p>
        </div>
      </div>
    </div>
  )
}

export default MarketOverviewPage
