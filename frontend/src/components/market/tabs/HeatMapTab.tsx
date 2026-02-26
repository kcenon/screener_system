/**
 * Heat Map Tab Component (IMPROVEMENT-003 & IMPROVEMENT-004 Phase 3A)
 *
 * Full-screen sector visualization with two modes:
 * - Grid mode: Simple grid-based heatmap
 * - Treemap mode: Advanced treemap with market cap sizing
 *
 * Features:
 * - Size = market cap (treemap mode)
 * - Color = performance %
 * - Click to filter screener by sector
 * - Toggle between grid and treemap views
 */

import { useState } from 'react'
import { SectorHeatmap } from '../SectorHeatmap'
import { SectorHeatmapAdvanced } from '../SectorHeatmapAdvanced'

interface HeatMapTabProps {
  autoRefresh?: boolean
  onSectorClick?: (sector: string) => void
}

export function HeatMapTab({ autoRefresh = true }: HeatMapTabProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'treemap'>('treemap')

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

        {/* View mode toggle */}
        <div className="flex gap-1.5 rounded-lg bg-gray-100 p-1">
          <button
            onClick={() => setViewMode('treemap')}
            className={`rounded px-3 py-1.5 text-sm font-medium transition-colors ${
              viewMode === 'treemap'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            📊 Treemap
          </button>
          <button
            onClick={() => setViewMode('grid')}
            className={`rounded px-3 py-1.5 text-sm font-medium transition-colors ${
              viewMode === 'grid'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            ▦ Grid
          </button>
        </div>
      </div>

      {/* Treemap view */}
      {viewMode === 'treemap' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <SectorHeatmapAdvanced
            defaultTimeframe="1D"
            autoRefresh={autoRefresh}
            height={500}
          />
        </div>
      )}

      {/* Grid view */}
      {viewMode === 'grid' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <SectorHeatmap defaultTimeframe="1D" autoRefresh={autoRefresh} />
        </div>
      )}

      {/* Info card */}
      <div className="bg-blue-50 rounded-lg p-4">
        <p className="text-sm text-blue-900">
          💡 <strong>How to use:</strong> Click on a sector to filter the
          screener by that sector.
          {viewMode === 'treemap' && (
            <span> Treemap size is proportional to market capitalization.</span>
          )}{' '}
          Colors represent performance: green for gains, red for losses.
        </p>
      </div>
    </div>
  )
}
