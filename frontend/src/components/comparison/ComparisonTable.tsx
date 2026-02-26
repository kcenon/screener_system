/**
 * ComparisonTable Component
 * Displays stock comparison in table format with highlighting
 */

import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import type { ComparisonStock, ComparisonMetric } from '../../types/comparison'
import { getMetricsByCategory } from '../../types/comparison'
import {
  getMetricValue,
  formatMetricValue,
  highlightBestWorst,
  getHighlightClass,
} from '../../utils/comparison'
import { MetricTooltip } from './MetricTooltip'

interface ComparisonTableProps {
  /** Stocks to compare */
  stocks: ComparisonStock[]
  /** Optional className */
  className?: string
}

type CategoryName = ComparisonMetric['category']

const CATEGORY_LABELS: Record<CategoryName, string> = {
  fundamental: 'Fundamentals',
  valuation: 'Valuation',
  profitability: 'Profitability',
  financial_health: 'Financial Health',
  technical: 'Technical Indicators',
  performance: 'Performance',
}

export function ComparisonTable({
  stocks,
  className = '',
}: ComparisonTableProps) {
  const [expandedCategories, setExpandedCategories] = useState<
    Set<CategoryName>
  >(new Set(['valuation', 'profitability']))

  const toggleCategory = (category: CategoryName) => {
    setExpandedCategories(prev => {
      const next = new Set(prev)
      if (next.has(category)) {
        next.delete(category)
      } else {
        next.add(category)
      }
      return next
    })
  }

  const categories: CategoryName[] = [
    'fundamental',
    'valuation',
    'profitability',
    'financial_health',
    'technical',
    'performance',
  ]

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="bg-gray-50 border-b border-gray-200 px-6 py-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Comparison Table
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Click category to expand • Best values highlighted in green • Worst in
          red
        </p>
      </div>

      {/* Table Container with Horizontal Scroll */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-100 border-b border-gray-200 sticky top-0">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900 min-w-[200px]">
                Metric
              </th>
              {stocks.map(stock => (
                <th
                  key={stock.code}
                  className="px-4 py-3 text-center text-sm font-semibold text-gray-900 min-w-[150px]"
                >
                  <div className="flex flex-col items-center">
                    <span className="text-base">{stock.code}</span>
                    <span className="text-xs text-gray-600 font-normal truncate max-w-[140px]">
                      {stock.name}
                    </span>
                    {stock.isLoading && (
                      <span className="text-xs text-blue-600 mt-1">
                        Loading...
                      </span>
                    )}
                    {stock.error && (
                      <span className="text-xs text-red-600 mt-1">Error</span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {categories.map(category => {
              const metrics = getMetricsByCategory(category)
              const isExpanded = expandedCategories.has(category)

              return (
                <React.Fragment key={category}>
                  {/* Category Header */}
                  <tr className="bg-gray-50 border-t border-gray-200">
                    <td colSpan={stocks.length + 1} className="px-6 py-3">
                      <button
                        onClick={() => toggleCategory(category)}
                        className="
                          flex items-center gap-2 w-full
                          text-left font-semibold text-gray-900
                          hover:text-blue-600 transition-colors
                        "
                      >
                        {isExpanded ? (
                          <ChevronDown className="w-5 h-5" />
                        ) : (
                          <ChevronRight className="w-5 h-5" />
                        )}
                        {CATEGORY_LABELS[category]}
                        <span className="text-sm text-gray-500 font-normal">
                          ({metrics.length} metrics)
                        </span>
                      </button>
                    </td>
                  </tr>

                  {/* Metrics Rows */}
                  {isExpanded &&
                    metrics.map(metric => {
                      const values = stocks.map(stock =>
                        getMetricValue(stock, metric.key),
                      )
                      const highlights = highlightBestWorst(
                        values,
                        metric.higher_is_better,
                      )

                      return (
                        <tr
                          key={metric.key}
                          className="border-b border-gray-100 hover:bg-gray-50"
                        >
                          <td className="px-6 py-3 text-sm text-gray-900">
                            <div className="flex items-center gap-2">
                              <span>{metric.label}</span>
                              <MetricTooltip description={metric.description} />
                            </div>
                          </td>
                          {stocks.map((stock, index) => {
                            const value = values[index]
                            const highlight = highlights[index]
                            const formattedValue = formatMetricValue(
                              value,
                              metric.format,
                            )

                            return (
                              <td
                                key={stock.code}
                                className={`
                                  px-4 py-3 text-sm text-center
                                  ${getHighlightClass(highlight)}
                                `}
                              >
                                {stock.isLoading ? (
                                  <div className="flex justify-center">
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
                                  </div>
                                ) : stock.error ? (
                                  <span className="text-gray-400">—</span>
                                ) : (
                                  formattedValue
                                )}
                              </td>
                            )
                          })}
                        </tr>
                      )
                    })}
                </React.Fragment>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="bg-gray-50 border-t border-gray-200 px-6 py-3 text-sm text-gray-600">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-50 border border-green-200 rounded" />
            <span>Best value</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-50 border border-red-200 rounded" />
            <span>Worst value</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Add React import at top
import React from 'react'
