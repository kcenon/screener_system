/**
 * RadarChartView Component
 * Displays valuation metrics comparison using radar chart
 */

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts'
import type { ComparisonStock } from '../../types/comparison'
import { getMetricValue, formatMetricValue } from '../../utils/comparison'

interface RadarChartViewProps {
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

// Radar chart metrics (valuation & profitability)
const RADAR_METRICS = [
  { key: 'per', label: 'P/E', format: 'ratio' as const, inverse: true },
  { key: 'pbr', label: 'P/B', format: 'ratio' as const, inverse: true },
  { key: 'roe', label: 'ROE', format: 'percent' as const, inverse: false },
  { key: 'roa', label: 'ROA', format: 'percent' as const, inverse: false },
  {
    key: 'operating_margin',
    label: 'Op Margin',
    format: 'percent' as const,
    inverse: false,
  },
  { key: 'debt_ratio', label: 'Debt', format: 'percent' as const, inverse: true },
]

/**
 * Normalize value to 0-100 scale for radar chart
 * Handles inverse metrics (lower is better)
 */
function normalizeValue(
  value: number | null,
  allValues: (number | null)[],
  inverse: boolean
): number {
  if (value === null) return 0

  const validValues = allValues.filter((v) => v !== null) as number[]
  if (validValues.length === 0) return 0

  const min = Math.min(...validValues)
  const max = Math.max(...validValues)

  // Avoid division by zero
  if (min === max) return 50

  // Normalize to 0-100
  const normalized = ((value - min) / (max - min)) * 100

  // Invert if lower is better (e.g., P/E, Debt Ratio)
  return inverse ? 100 - normalized : normalized
}

export function RadarChartView({ stocks, className = '' }: RadarChartViewProps) {
  // Prepare radar chart data
  const radarData = RADAR_METRICS.map((metric) => {
    const dataPoint: any = {
      metric: metric.label,
      fullName: metric.label,
    }

    stocks.forEach((stock, index) => {
      const value = getMetricValue(stock, metric.key)
      const allValues = stocks.map((s) => getMetricValue(s, metric.key))

      // Normalized value for radar display
      dataPoint[stock.code] = normalizeValue(value, allValues, metric.inverse)

      // Store original value for tooltip
      dataPoint[`${stock.code}_original`] = value
      dataPoint[`${stock.code}_format`] = metric.format
    })

    return dataPoint
  })

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || payload.length === 0) return null

    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
        <p className="font-semibold text-gray-900 mb-2">
          {payload[0]?.payload?.fullName}
        </p>
        {payload.map((entry: any, index: number) => {
          const stockCode = entry.dataKey
          const originalValue = entry.payload[`${stockCode}_original`]
          const format = entry.payload[`${stockCode}_format`]
          const formattedValue = formatMetricValue(originalValue, format)

          return (
            <div key={index} className="flex items-center gap-2 text-sm">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: entry.stroke }}
              />
              <span className="text-gray-700">{stockCode}:</span>
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
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={radarData}>
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis
            dataKey="metric"
            tick={{ fill: '#6b7280', fontSize: 12 }}
          />
          <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} />

          {stocks.map((stock, index) => (
            <Radar
              key={stock.code}
              name={`${stock.code} (${stock.name})`}
              dataKey={stock.code}
              stroke={STOCK_COLORS[index]}
              fill={STOCK_COLORS[index]}
              fillOpacity={0.2}
              strokeWidth={2}
            />
          ))}

          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="circle"
            formatter={(value: string) => (
              <span className="text-sm text-gray-700">{value}</span>
            )}
          />
        </RadarChart>
      </ResponsiveContainer>

      {/* Legend explanation */}
      <div className="mt-4 text-sm text-gray-600 text-center">
        <p>
          Radar chart shows normalized comparison (0-100 scale) across key metrics
        </p>
        <p className="text-xs mt-1">
          Larger area = Better overall performance
        </p>
      </div>
    </div>
  )
}
