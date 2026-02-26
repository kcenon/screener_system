/**
 * Allocation Chart Component
 *
 * Displays portfolio allocation breakdown using:
 * - Pie chart for stock allocation
 * - Donut chart for sector allocation
 * - Interactive tooltips with percentages
 *
 * @module components/portfolio/AllocationChart
 * @category Components
 */

import { useMemo } from 'react'
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts'
import {
  PortfolioAllocation,
  AllocationItem,
} from '../../services/portfolioService'

/**
 * Color palette for allocation charts
 */
const COLORS = [
  '#3B82F6', // blue-500
  '#10B981', // green-500
  '#F59E0B', // amber-500
  '#EF4444', // red-500
  '#8B5CF6', // purple-500
  '#EC4899', // pink-500
  '#06B6D4', // cyan-500
  '#84CC16', // lime-500
  '#F97316', // orange-500
  '#6366F1', // indigo-500
]

/**
 * Props for AllocationChart component
 */
interface AllocationChartProps {
  /** Allocation data from backend */
  allocation: PortfolioAllocation | null | undefined
  /** Chart type: 'stock' or 'sector' */
  type: 'stock' | 'sector'
  /** Optional title */
  title?: string
}

/**
 * Custom tooltip for pie charts
 */
function CustomTooltip({ active, payload }: any) {
  if (!active || !payload || !payload[0]) return null

  const data = payload[0].payload
  const value = parseFloat(data.value || '0')
  const weight = parseFloat(data.weight_percent || '0')
  const gain = parseFloat(data.gain || '0')
  const gainPercent = parseFloat(data.gain_percent || '0')

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
      <p className="font-medium text-gray-900">{data.label}</p>
      <p className="text-sm text-gray-600 mt-1">
        Value: ₩{value.toLocaleString()}
      </p>
      <p className="text-sm text-gray-600">Weight: {weight.toFixed(2)}%</p>
      <p
        className={`text-sm mt-1 ${
          gain >= 0 ? 'text-green-600' : 'text-red-600'
        }`}
      >
        Gain: {gain >= 0 ? '+' : ''}₩{gain.toLocaleString()} (
        {gain >= 0 ? '+' : ''}
        {gainPercent.toFixed(2)}%)
      </p>
    </div>
  )
}

/**
 * Custom legend renderer
 */
function CustomLegend({ payload }: any) {
  return (
    <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
      {payload.map((entry: any, index: number) => (
        <div key={`legend-${index}`} className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full flex-shrink-0"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-gray-700 truncate" title={entry.value}>
            {entry.value}
          </span>
        </div>
      ))}
    </div>
  )
}

/**
 * Allocation Chart Component
 *
 * Renders pie/donut charts for portfolio allocation by stock or sector.
 *
 * @example
 * ```tsx
 * <AllocationChart
 *   allocation={allocationData}
 *   type="stock"
 *   title="Stock Allocation"
 * />
 * ```
 */
export default function AllocationChart({
  allocation,
  type,
  title,
}: AllocationChartProps) {
  // Select data based on type
  const chartData = useMemo(() => {
    if (!allocation) return []

    const items = type === 'stock' ? allocation.by_stock : allocation.by_sector

    // Convert to chart format and limit to top 10
    return items.slice(0, 10).map((item: AllocationItem) => ({
      label: item.label,
      value: parseFloat(item.value || '0'),
      weight_percent: parseFloat(item.weight_percent || '0'),
      gain: parseFloat(item.gain || '0'),
      gain_percent: parseFloat(item.gain_percent || '0'),
    }))
  }, [allocation, type])

  // Show empty state if no data
  if (!allocation || chartData.length === 0) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        {title && (
          <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        )}
        <div className="flex items-center justify-center h-64 text-gray-500">
          <div className="text-center">
            <p>No {type} allocation data available</p>
            <p className="text-sm mt-1">
              Add some holdings to see the breakdown
            </p>
          </div>
        </div>
      </div>
    )
  }

  const isDonut = type === 'sector'

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      )}

      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={(props: any) => {
              const { label, weight_percent } = props
              const weight = parseFloat(weight_percent)
              // Only show label if weight > 5%
              if (weight < 5) return null
              return `${label} (${weight.toFixed(1)}%)`
            }}
            outerRadius={isDonut ? 100 : 120}
            innerRadius={isDonut ? 60 : 0}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((_entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend content={<CustomLegend />} />
        </PieChart>
      </ResponsiveContainer>

      {/* Summary */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Total Value:</span>
          <span className="font-medium text-gray-900">
            ₩{parseFloat(allocation.total_value || '0').toLocaleString()}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm mt-1">
          <span className="text-gray-600">
            {type === 'stock' ? 'Stocks' : 'Sectors'}:
          </span>
          <span className="font-medium text-gray-900">
            {chartData.length} {chartData.length > 10 && '(top 10 shown)'}
          </span>
        </div>
      </div>
    </div>
  )
}
