/**
 * Platform Stats Widget
 *
 * Displays user's platform usage statistics such as
 * screening count, watchlist stocks, last login, etc.
 */

import { Search, Eye, Clock } from 'lucide-react'

interface PlatformStatsWidgetProps {
  /** Number of screenings this month */
  screeningCount: number
  /** Total stocks in all watchlists */
  totalWatchlistStocks: number
  /** Last login timestamp */
  lastLogin?: string
  /** Loading state */
  isLoading?: boolean
}

/**
 * Format timestamp to readable format
 */
function formatDateTime(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Stat Item Component
 */
function StatItem({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: typeof Search
  label: string
  value: string | number
  color: string
}) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
  }[color]

  return (
    <div className="flex items-start gap-3 py-3">
      <div className={`p-2 rounded-lg ${colorClasses} flex-shrink-0`}>
        <Icon className="w-4 h-4" />
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-600">{label}</p>
        <p className="text-lg font-semibold text-gray-900 mt-1">{value}</p>
      </div>
    </div>
  )
}

/**
 * Loading Skeleton Component
 */
function LoadingSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex items-start gap-3 py-3 animate-pulse">
          <div className="w-10 h-10 bg-gray-200 rounded-lg flex-shrink-0"></div>
          <div className="flex-1">
            <div className="h-3 bg-gray-200 rounded w-24 mb-2"></div>
            <div className="h-5 bg-gray-200 rounded w-16"></div>
          </div>
        </div>
      ))}
    </div>
  )
}

/**
 * PlatformStatsWidget Component
 */
export default function PlatformStatsWidget({
  screeningCount,
  totalWatchlistStocks,
  lastLogin,
  isLoading = false,
}: PlatformStatsWidgetProps) {
  if (isLoading) {
    return <LoadingSkeleton />
  }

  return (
    <div className="divide-y divide-gray-100">
      <StatItem
        icon={Search}
        label="Screenings this month"
        value={screeningCount}
        color="blue"
      />

      <StatItem
        icon={Eye}
        label="Stocks in watchlists"
        value={totalWatchlistStocks}
        color="green"
      />

      {lastLogin && (
        <StatItem
          icon={Clock}
          label="Last login"
          value={formatDateTime(lastLogin)}
          color="purple"
        />
      )}
    </div>
  )
}
