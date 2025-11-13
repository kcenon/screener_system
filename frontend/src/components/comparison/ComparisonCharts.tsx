/**
 * ComparisonCharts Component
 * Container for all comparison chart visualizations with tab navigation
 */

import { useState } from 'react'
import { BarChart3, TrendingUp, Activity } from 'lucide-react'
import type { ComparisonStock } from '../../types/comparison'
import { RadarChartView } from './RadarChartView'
import { BarChartView } from './BarChartView'
import { PerformanceChart } from './PerformanceChart'

interface ComparisonChartsProps {
  /** Stocks to compare */
  stocks: ComparisonStock[]
  /** Optional className */
  className?: string
}

type ChartView = 'radar' | 'bar' | 'performance'

const CHART_TABS = [
  {
    id: 'radar' as const,
    label: 'Radar Overview',
    icon: Activity,
    description: 'Multi-metric comparison at a glance',
  },
  {
    id: 'bar' as const,
    label: 'Bar Comparison',
    icon: BarChart3,
    description: 'Detailed metric-by-metric view',
  },
  {
    id: 'performance' as const,
    label: 'Performance',
    icon: TrendingUp,
    description: 'Returns across time periods',
  },
]

export function ComparisonCharts({ stocks, className = '' }: ComparisonChartsProps) {
  const [activeView, setActiveView] = useState<ChartView>('radar')

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="bg-gray-50 border-b border-gray-200 px-6 py-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Visual Comparison Charts
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Interactive charts for comprehensive stock analysis
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <div className="flex overflow-x-auto">
          {CHART_TABS.map((tab) => {
            const Icon = tab.icon
            const isActive = activeView === tab.id

            return (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id)}
                className={`
                  flex items-center gap-2 px-6 py-4 border-b-2 transition-colors
                  whitespace-nowrap
                  ${
                    isActive
                      ? 'border-blue-600 text-blue-600 bg-blue-50'
                      : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <div className="text-left">
                  <div className="font-medium">{tab.label}</div>
                  <div className="text-xs text-gray-500">{tab.description}</div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Chart Content */}
      <div className="p-6">
        {activeView === 'radar' && <RadarChartView stocks={stocks} />}
        {activeView === 'bar' && <BarChartView stocks={stocks} />}
        {activeView === 'performance' && <PerformanceChart stocks={stocks} />}
      </div>

      {/* Footer Help Text */}
      <div className="bg-gray-50 border-t border-gray-200 px-6 py-3 text-sm text-gray-600">
        <p>
          <span className="font-medium">💡 Tip:</span> Switch between chart views to
          analyze stocks from different perspectives. Hover over data points for
          detailed values.
        </p>
      </div>
    </div>
  )
}
