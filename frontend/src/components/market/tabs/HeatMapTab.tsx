/**
 * Heat Map Tab Component (IMPROVEMENT-003)
 *
 * Full-screen sector treemap showing:
 * - Size = market cap
 * - Color = performance %
 * - Click to filter screener by sector
 *
 * Note: Enhanced treemap will be implemented in IMPROVEMENT-004 (Phase 3)
 */

import { SectorHeatmap } from '../SectorHeatmap'

interface HeatMapTabProps {
  autoRefresh?: boolean
  onSectorClick?: (sector: string) => void
}

export function HeatMapTab({ autoRefresh = true }: HeatMapTabProps) {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Sector Heat Map</h2>
          <p className="mt-1 text-sm text-gray-600">
            Visualize market performance by sector
          </p>
        </div>

        {/* Timeframe selector (integrated into SectorHeatmap) */}
      </div>

      {/* Full-screen heatmap */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <SectorHeatmap
          defaultTimeframe="1D"
          autoRefresh={autoRefresh}
        />
      </div>

      {/* Info card */}
      <div className="bg-blue-50 rounded-lg p-4">
        <p className="text-sm text-blue-900">
          💡 <strong>How to use:</strong> Click on a sector to filter the screener by that sector.
          Colors represent performance: green for gains, red for losses.
        </p>
      </div>

      {/* Placeholder for Phase 3 enhanced treemap */}
      <div className="bg-gray-50 rounded-lg p-6 border-2 border-dashed border-gray-300 text-center">
        <p className="text-gray-600 font-medium mb-2">
          🚀 Enhanced Treemap Coming in Phase 3
        </p>
        <p className="text-sm text-gray-500">
          Interactive sector visualization with drill-down to top stocks, market cap sizing, and performance coloring
        </p>
      </div>
    </div>
  )
}
