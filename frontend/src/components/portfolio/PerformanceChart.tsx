/**
 * Performance Chart Component
 *
 * Displays portfolio performance metrics visualization:
 * - Bar chart showing total value, cost, and gain
 * - Percentage gain/loss indicator
 * - Day change comparison
 *
 * Note: Full historical line chart will be implemented when
 * backend provides historical performance data API.
 *
 * @module components/portfolio/PerformanceChart
 * @category Components
 */

import { useMemo } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { PerformanceMetrics } from '../../services/portfolioService'
import { TrendingUp, TrendingDown } from 'lucide-react'

/**
 * Props for PerformanceChart component
 */
interface PerformanceChartProps {
  /** Performance metrics from backend */
  performance: PerformanceMetrics | null | undefined
  /** Optional title */
  title?: string
}

/**
 * Custom tooltip for performance chart
 */
function CustomTooltip({ active, payload }: any) {
  if (!active || !payload || !payload[0]) return null

  const data = payload[0].payload
  const value = data.value

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
      <p className="font-medium text-gray-900">{data.name}</p>
      <p className="text-sm text-gray-600 mt-1">₩{value.toLocaleString()}</p>
    </div>
  )
}

/**
 * Performance Chart Component
 *
 * Displays current portfolio performance metrics as a bar chart.
 * Shows total value, total cost, and gain/loss.
 *
 * @example
 * ```tsx
 * <PerformanceChart
 *   performance={performanceMetrics}
 *   title="Performance Overview"
 * />
 * ```
 */
export default function PerformanceChart({
  performance,
  title = 'Performance Overview',
}: PerformanceChartProps) {
  // Prepare chart data
  const chartData = useMemo(() => {
    if (!performance) return []

    const totalValue = parseFloat(performance.total_value || '0')
    const totalCost = parseFloat(performance.total_cost || '0')
    const totalGain = parseFloat(performance.total_gain || '0')

    return [
      {
        name: 'Total Cost',
        value: totalCost,
        color: '#6B7280', // gray-500
      },
      {
        name: 'Current Value',
        value: totalValue,
        color: totalGain >= 0 ? '#10B981' : '#EF4444', // green-500 or red-500
      },
      {
        name: 'Gain/Loss',
        value: Math.abs(totalGain),
        color: totalGain >= 0 ? '#34D399' : '#F87171', // green-400 or red-400
      },
    ]
  }, [performance])

  // Calculate metrics
  const metrics = useMemo(() => {
    if (!performance) return null

    const totalValue = parseFloat(performance.total_value || '0')
    const totalCost = parseFloat(performance.total_cost || '0')
    const totalGain = parseFloat(performance.total_gain || '0')
    const totalReturnPercent = parseFloat(
      performance.total_return_percent || '0',
    )
    const dayChange = parseFloat(performance.day_change || '0')
    const dayChangePercent = parseFloat(performance.day_change_percent || '0')

    return {
      totalValue,
      totalCost,
      totalGain,
      totalReturnPercent,
      dayChange,
      dayChangePercent,
      isPositive: totalGain >= 0,
      isDayPositive: dayChange >= 0,
    }
  }, [performance])

  // Show empty state if no data
  if (!performance || chartData.length === 0) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        {title && (
          <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        )}
        <div className="flex items-center justify-center h-64 text-gray-500">
          <div className="text-center">
            <p>No performance data available</p>
            <p className="text-sm mt-1">
              Add some holdings to track performance
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (!metrics) return null

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      )}

      {/* Performance Summary Cards */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Total Return */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Total Return</span>
            {metrics.isPositive ? (
              <TrendingUp className="w-4 h-4 text-green-600" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-600" />
            )}
          </div>
          <div
            className={`text-xl font-bold ${
              metrics.isPositive ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {metrics.isPositive ? '+' : ''}₩{metrics.totalGain.toLocaleString()}
          </div>
          <div
            className={`text-sm ${
              metrics.isPositive ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {metrics.isPositive ? '+' : ''}
            {metrics.totalReturnPercent.toFixed(2)}%
          </div>
        </div>

        {/* Day Change */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Today's Change</span>
            {metrics.isDayPositive ? (
              <TrendingUp className="w-4 h-4 text-green-600" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-600" />
            )}
          </div>
          <div
            className={`text-xl font-bold ${
              metrics.isDayPositive ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {metrics.isDayPositive ? '+' : ''}₩
            {metrics.dayChange.toLocaleString()}
          </div>
          <div
            className={`text-sm ${
              metrics.isDayPositive ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {metrics.isDayPositive ? '+' : ''}
            {metrics.dayChangePercent.toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Bar Chart */}
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis
            dataKey="name"
            tick={{ fill: '#6B7280', fontSize: 12 }}
            axisLine={{ stroke: '#D1D5DB' }}
          />
          <YAxis
            tick={{ fill: '#6B7280', fontSize: 12 }}
            axisLine={{ stroke: '#D1D5DB' }}
            tickFormatter={value => `₩${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="value" radius={[8, 8, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Historical Note */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          💡 Historical performance tracking will be available soon. Currently
          showing current snapshot.
        </p>
      </div>
    </div>
  )
}
