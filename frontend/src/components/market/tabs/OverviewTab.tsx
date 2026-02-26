/**
 * Overview Tab Component (IMPROVEMENT-003)
 *
 * Market Overview tab showing:
 * - Market indices (3-column compact layout)
 * - Market breadth
 * - Sector heatmap preview
 * - Top movers preview
 */

import { MarketIndicesWidget } from '../MarketIndicesWidget'
import { MarketBreadthWidget } from '../MarketBreadthWidget'
import { SectorHeatmap } from '../SectorHeatmap'
import { MarketMoversWidget } from '../MarketMoversWidget'
import { MostActiveWidget } from '../MostActiveWidget'

interface OverviewTabProps {
  autoRefresh?: boolean
  refreshInterval?: number
  onSwitchToMovers?: () => void
  onSwitchToSectors?: () => void
}

export function OverviewTab({
  autoRefresh = true,
  refreshInterval = 60000,
  onSwitchToMovers,
  onSwitchToSectors,
}: OverviewTabProps) {
  return (
    <div className="space-y-6">
      {/* Market Indices - 3 column layout (from Phase 1) */}
      <MarketIndicesWidget
        autoRefresh={autoRefresh}
        refreshInterval={refreshInterval}
      />

      {/* Market Breadth - Inline 1 row */}
      <MarketBreadthWidget
        autoRefresh={autoRefresh}
        refreshInterval={refreshInterval}
      />

      {/* Sector Heatmap Preview */}
      <div className="relative">
        <SectorHeatmap defaultTimeframe="1D" autoRefresh={autoRefresh} />
        {onSwitchToSectors && (
          <button
            onClick={onSwitchToSectors}
            className="absolute top-4 right-4 px-3 py-1.5 text-sm font-medium text-blue-600 bg-white border border-blue-200 rounded-md hover:bg-blue-50 transition-colors"
          >
            View Full Analysis →
          </button>
        )}
      </div>

      {/* Top Movers Preview */}
      <div className="relative">
        <MarketMoversWidget
          defaultMarket="ALL"
          limit={5}
          autoRefresh={autoRefresh}
        />
        {onSwitchToMovers && (
          <button
            onClick={onSwitchToMovers}
            className="absolute top-4 right-4 px-3 py-1.5 text-sm font-medium text-blue-600 bg-white border border-blue-200 rounded-md hover:bg-blue-50 transition-colors"
          >
            View All Movers →
          </button>
        )}
      </div>

      {/* Most Active Preview */}
      <MostActiveWidget
        defaultMarket="ALL"
        limit={10}
        autoRefresh={autoRefresh}
      />
    </div>
  )
}
