/**
 * Sectors Tab Component (IMPROVEMENT-003)
 *
 * Expanded sector analysis view:
 * - Detailed sector breakdown
 * - Sector composition (top stocks)
 * - Historical performance charts
 * - Click sector to filter screener
 */

import { SectorHeatmap } from '../SectorHeatmap'
import { MarketTrendChart } from '../MarketTrendChart'

interface SectorsTabProps {
  autoRefresh?: boolean
  onSectorClick?: (sector: string) => void
}

export function SectorsTab({ autoRefresh = true }: SectorsTabProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Sector Analysis</h2>
        <p className="mt-1 text-sm text-gray-600">
          Deep dive into sector performance and composition
        </p>
      </div>

      {/* Current Sector Performance */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Current Performance (Today)
        </h3>
        <SectorHeatmap
          defaultTimeframe="1D"
          autoRefresh={autoRefresh}
        />
      </div>

      {/* Historical Sector Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1 Week */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            7-Day Performance
          </h3>
          <SectorHeatmap
            defaultTimeframe="1W"
            autoRefresh={false}
          />
        </div>

        {/* 1 Month */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            1-Month Performance
          </h3>
          <SectorHeatmap
            defaultTimeframe="1M"
            autoRefresh={false}
          />
        </div>
      </div>

      {/* Market Trend Comparison */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Historical Market Trends (3 Months)
        </h3>
        <MarketTrendChart
          defaultTimeframe="3M"
          indices={['KOSPI', 'KOSDAQ', 'KRX100']}
          height={400}
        />
      </div>

      {/* Sector Composition Placeholder */}
      <div className="bg-gray-50 rounded-lg p-6 border-2 border-dashed border-gray-300">
        <h3 className="text-lg font-semibold text-gray-700 mb-2">
          🚀 Coming Soon: Sector Composition Details
        </h3>
        <p className="text-sm text-gray-600">
          Top stocks per sector, market cap distribution, and sector weight in indices
        </p>
      </div>

      {/* Info */}
      <div className="bg-blue-50 rounded-lg p-4">
        <p className="text-sm text-blue-900">
          💡 <strong>Tip:</strong> Click on a sector in any heatmap to filter the screener by that sector.
          Use the historical views to identify sector rotation and trends.
        </p>
      </div>
    </div>
  )
}
