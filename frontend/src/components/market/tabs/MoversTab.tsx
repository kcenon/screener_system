/**
 * Movers Tab Component (IMPROVEMENT-003)
 *
 * Expanded market movers view:
 * - Side-by-side: Top Gainers | Top Losers
 * - Full list (100+ stocks)
 * - Sortable by change %, volume, value
 * - Filter by market (KOSPI/KOSDAQ/ALL)
 */

import { useState } from 'react'
import { MarketMoversWidget } from '../MarketMoversWidget'

type MarketFilter = 'ALL' | 'KOSPI' | 'KOSDAQ'

interface MoversTabProps {
  autoRefresh?: boolean
}

export function MoversTab({ autoRefresh = true }: MoversTabProps) {
  const [market, setMarket] = useState<MarketFilter>('ALL')

  return (
    <div className="space-y-4">
      {/* Header with market filter */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Top Movers</h2>
          <p className="mt-1 text-sm text-gray-600">
            Stocks with the highest price changes today
          </p>
        </div>

        {/* Market filter */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Market:</span>
          <div className="flex bg-gray-100 rounded-md p-1">
            {(['ALL', 'KOSPI', 'KOSDAQ'] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMarket(m)}
                className={`px-3 py-1.5 text-sm font-medium rounded transition-colors ${
                  market === m
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {m}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Expanded market movers (already shows gainers and losers side-by-side) */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <MarketMoversWidget
          defaultMarket={market}
          limit={50}
          autoRefresh={autoRefresh}
        />
      </div>

      {/* Info */}
      <div className="bg-blue-50 rounded-lg p-4">
        <p className="text-sm text-blue-900">
          💡 <strong>Tip:</strong> Click on any stock to view detailed information and technical analysis.
          Data updates every minute when auto-refresh is enabled.
        </p>
      </div>
    </div>
  )
}
