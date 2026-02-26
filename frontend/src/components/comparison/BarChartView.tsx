/**
 * BarChartView Component
 * Displays metric comparison using grouped bar charts
 */

import { useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { ComparisonStock } from '../../types/comparison'
import { COMPARISON_METRICS } from '../../types/comparison'
import { getMetricValue, formatMetricValue } from '../../utils/comparison'

interface BarChartViewProps {
  /** Stocks to compare */
  stocks: ComparisonStock[]
  /** Optional className */
  className?: string
}

// Color palette for up to 5 stocks
const STOCK_COLORS = [
  '#3b82f6', // blue-500
  '#ef4444', // red-500
  '#10b981', // green-500
  '#f59e0b', // amber-500
  '#8b5cf6', // violet-500
]

// Metric categories for tab selection
const METRIC_CATEGORIES = [
  { id: 'valuation', label: 'Valuation' },
  { id: 'profitability', label: 'Profitability' },
  { id: 'financial_health', label: 'Financial Health' },
  { id: 'performance', label: 'Performance' },
] as const

type CategoryId = (typeof METRIC_CATEGORIES)[number]['id']

export function BarChartView({ stocks, className = '' }: BarChartViewProps) {
  const [selectedCategory, setSelectedCategory] =
    useState<CategoryId>('valuation')

  // Get metrics for selected category (limit to 5 for readability)
  const categoryMetrics = COMPARISON_METRICS.filter(
    m => m.category === selectedCategory,
  ).slice(0, 5)

  // Prepare bar chart data
  const barData = categoryMetrics.map(metric => {
    const dataPoint: any = {
      metric: metric.label,
      metricKey: metric.key,
      format: metric.format,
    }

    stocks.forEach(stock => {
      const value = getMetricValue(stock, metric.key)
      dataPoint[stock.code] = value ?? 0
    })

    return dataPoint
  })

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || payload.length === 0) return null

    const format = payload[0]?.payload?.format || 'number'

    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
        <p className="font-semibold text-gray-900 mb-2">{label}</p>
        {payload.map((entry: any, index: number) => {
          const formattedValue = formatMetricValue(entry.value, format)

          return (
            <div key={index} className="flex items-center gap-2 text-sm">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: entry.fill }}
              />
              <span className="text-gray-700">{entry.dataKey}:</span>
              <span className="font-medium">{formattedValue}</span>
            </div>
          )
        })}
      </div>
    )
  }

  if (stocks.length === 0) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <p className="text-gray-500">No stocks selected</p>
      </div>
    )
  }

  return (
    <div className={className}>
      {/* Category tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {METRIC_CATEGORIES.map(category => (
          <button
            key={category.id}
            onClick={() => setSelectedCategory(category.id)}
            className={`
              px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap
              transition-colors
              ${
                selectedCategory === category.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
            `}
          >
            {category.label}
          </button>
        ))}
      </div>

      {/* Bar chart */}
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={barData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="metric"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            angle={-15}
            textAnchor="end"
            height={80}
          />
          <YAxis tick={{ fill: '#6b7280', fontSize: 12 }} />

          {stocks.map((stock, index) => (
            <Bar
              key={stock.code}
              dataKey={stock.code}
              fill={STOCK_COLORS[index]}
              name={`${stock.code} (${stock.name})`}
              radius={[4, 4, 0, 0]}
            />
          ))}

          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: '10px' }}
            iconType="circle"
            formatter={(value: string) => (
              <span className="text-sm text-gray-700">{value}</span>
            )}
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Info */}
      <div className="mt-4 text-sm text-gray-600 text-center">
        <p>
          Grouped bar chart comparing {categoryMetrics.length} key{' '}
          {selectedCategory} metrics
        </p>
      </div>
    </div>
  )
}
