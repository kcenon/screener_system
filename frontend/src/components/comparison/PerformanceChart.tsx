/**
 * PerformanceChart Component
 * Displays performance returns comparison across different timeframes
 */

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import type { ComparisonStock } from '../../types/comparison'
import { getMetricValue } from '../../utils/comparison'

interface PerformanceChartProps {
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

// Performance timeframes
const PERFORMANCE_PERIODS = [
  { key: 'return_1d', label: '1D' },
  { key: 'return_1w', label: '1W' },
  { key: 'return_1m', label: '1M' },
  { key: 'return_3m', label: '3M' },
  { key: 'return_6m', label: '6M' },
  { key: 'return_1y', label: '1Y' },
]

export function PerformanceChart({
  stocks,
  className = '',
}: PerformanceChartProps) {
  // Prepare line chart data
  const performanceData = PERFORMANCE_PERIODS.map(period => {
    const dataPoint: any = {
      period: period.label,
    }

    stocks.forEach(stock => {
      const value = getMetricValue(stock, period.key)
      dataPoint[stock.code] = value !== null ? value : null
    })

    return dataPoint
  })

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || payload.length === 0) return null

    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
        <p className="font-semibold text-gray-900 mb-2">Period: {label}</p>
        {payload.map((entry: any, index: number) => {
          const value = entry.value
          const formattedValue =
            value !== null && value !== undefined
              ? `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
              : 'N/A'

          return (
            <div key={index} className="flex items-center gap-2 text-sm">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: entry.stroke }}
              />
              <span className="text-gray-700">{entry.dataKey}:</span>
              <span
                className={`font-medium ${
                  value > 0
                    ? 'text-green-600'
                    : value < 0
                      ? 'text-red-600'
                      : 'text-gray-900'
                }`}
              >
                {formattedValue}
              </span>
            </div>
          )
        })}
      </div>
    )
  }

  // Custom Y-axis tick formatter
  const formatYAxis = (value: number) => {
    return `${value > 0 ? '+' : ''}${value}%`
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
        <LineChart
          data={performanceData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="period"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            label={{
              value: 'Time Period',
              position: 'insideBottom',
              offset: -5,
              style: { fill: '#6b7280', fontSize: 12 },
            }}
          />
          <YAxis
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickFormatter={formatYAxis}
            label={{
              value: 'Return (%)',
              angle: -90,
              position: 'insideLeft',
              style: { fill: '#6b7280', fontSize: 12 },
            }}
          />

          {/* Zero reference line */}
          <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />

          {stocks.map((stock, index) => (
            <Line
              key={stock.code}
              type="monotone"
              dataKey={stock.code}
              name={`${stock.code} (${stock.name})`}
              stroke={STOCK_COLORS[index]}
              strokeWidth={2}
              dot={{ r: 4, fill: STOCK_COLORS[index] }}
              activeDot={{ r: 6 }}
              connectNulls
            />
          ))}

          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: '10px' }}
            iconType="line"
            formatter={(value: string) => (
              <span className="text-sm text-gray-700">{value}</span>
            )}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Info */}
      <div className="mt-4 text-sm text-gray-600 text-center">
        <p>Performance returns across different time periods</p>
        <p className="text-xs mt-1">
          Positive returns in green • Negative returns in red
        </p>
      </div>
    </div>
  )
}
