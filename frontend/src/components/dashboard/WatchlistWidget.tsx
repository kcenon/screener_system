/**
 * Watchlist Widget
 *
 * Displays user's watchlists with stock counts and quick links.
 */

import { Link } from 'react-router-dom'
import { Eye, TrendingUp, TrendingDown, Plus } from 'lucide-react'
import type { WatchlistSummary } from '../../types'

interface WatchlistWidgetProps {
  /** List of watchlists */
  watchlists: WatchlistSummary[]
  /** Loading state */
  isLoading?: boolean
}

/**
 * Format date to relative time
 */
function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 30) return `${diffDays}d ago`

  return date.toLocaleDateString('ko-KR')
}

/**
 * Watchlist Card Component
 */
function WatchlistCard({ watchlist }: { watchlist: WatchlistSummary }) {
  return (
    <Link
      to={`/watchlists?id=${watchlist.id}`}
      className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">{watchlist.name}</h3>
          {watchlist.description && (
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
              {watchlist.description}
            </p>
          )}
        </div>
        <Eye className="w-4 h-4 text-gray-400 ml-2" />
      </div>

      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">{watchlist.stock_count} stocks</span>
        <span className="text-gray-500">{formatRelativeTime(watchlist.updated_at)}</span>
      </div>
    </Link>
  )
}

/**
 * Loading Skeleton Component
 */
function LoadingSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="animate-pulse p-4 bg-gray-50 rounded-lg">
          <div className="h-5 bg-gray-200 rounded w-32 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-24"></div>
        </div>
      ))}
    </div>
  )
}

/**
 * Empty State Component
 */
function EmptyState() {
  return (
    <div className="text-center py-8">
      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <Eye className="w-8 h-8 text-gray-400" />
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">No Watchlists Yet</h3>
      <p className="text-gray-600 mb-4">
        Create your first watchlist to track your favorite stocks
      </p>
      <Link
        to="/watchlists"
        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        <Plus className="w-4 h-4" />
        Create Watchlist
      </Link>
    </div>
  )
}

/**
 * WatchlistWidget Component
 */
export default function WatchlistWidget({ watchlists, isLoading = false }: WatchlistWidgetProps) {
  if (isLoading) {
    return <LoadingSkeleton />
  }

  if (watchlists.length === 0) {
    return <EmptyState />
  }

  return (
    <div className="space-y-3">
      {watchlists.slice(0, 5).map((watchlist) => (
        <WatchlistCard key={watchlist.id} watchlist={watchlist} />
      ))}

      {watchlists.length > 5 && (
        <Link
          to="/watchlists"
          className="block text-center py-2 text-blue-600 hover:text-blue-700 font-medium text-sm"
        >
          View all {watchlists.length} watchlists →
        </Link>
      )}
    </div>
  )
}
