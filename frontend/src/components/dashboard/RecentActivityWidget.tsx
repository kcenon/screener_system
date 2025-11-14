/**
 * Recent Activity Widget
 *
 * Displays user's recent activities including screenings, watchlist updates,
 * and stock views.
 */

import {
  Search,
  Eye,
  Plus,
  Trash,
  Edit,
  LogIn,
  LogOut,
  Clock,
} from 'lucide-react'
import type { UserActivity } from '../../types'

interface RecentActivityWidgetProps {
  /** List of recent activities */
  activities: UserActivity[]
  /** Loading state */
  isLoading?: boolean
}

/**
 * Get icon for activity type
 */
function getActivityIcon(type: UserActivity['activity_type']) {
  const iconMap = {
    screening: Search,
    watchlist_create: Plus,
    watchlist_update: Edit,
    watchlist_delete: Trash,
    stock_add: Plus,
    stock_remove: Trash,
    stock_view: Eye,
    login: LogIn,
    logout: LogOut,
  }

  return iconMap[type] || Clock
}

/**
 * Get color for activity type
 */
function getActivityColor(type: UserActivity['activity_type']): string {
  const colorMap = {
    screening: 'bg-blue-100 text-blue-600',
    watchlist_create: 'bg-green-100 text-green-600',
    watchlist_update: 'bg-yellow-100 text-yellow-600',
    watchlist_delete: 'bg-red-100 text-red-600',
    stock_add: 'bg-green-100 text-green-600',
    stock_remove: 'bg-red-100 text-red-600',
    stock_view: 'bg-gray-100 text-gray-600',
    login: 'bg-purple-100 text-purple-600',
    logout: 'bg-gray-100 text-gray-600',
  }

  return colorMap[type] || 'bg-gray-100 text-gray-600'
}

/**
 * Format timestamp to relative time
 */
function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`

  return date.toLocaleDateString('ko-KR')
}

/**
 * Activity Item Component
 */
function ActivityItem({ activity }: { activity: UserActivity }) {
  const Icon = getActivityIcon(activity.activity_type)
  const colorClass = getActivityColor(activity.activity_type)

  return (
    <div className="flex items-start gap-3 py-3">
      <div className={`p-2 rounded-lg ${colorClass} flex-shrink-0`}>
        <Icon className="w-4 h-4" />
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-900">{activity.description}</p>
        <p className="text-xs text-gray-500 mt-1">
          {formatRelativeTime(activity.created_at)}
        </p>
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
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="flex items-start gap-3 py-3 animate-pulse">
          <div className="w-10 h-10 bg-gray-200 rounded-lg flex-shrink-0"></div>
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-20"></div>
          </div>
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
        <Clock className="w-8 h-8 text-gray-400" />
      </div>
      <p className="text-gray-600">No recent activity</p>
    </div>
  )
}

/**
 * RecentActivityWidget Component
 */
export default function RecentActivityWidget({
  activities,
  isLoading = false,
}: RecentActivityWidgetProps) {
  if (isLoading) {
    return <LoadingSkeleton />
  }

  if (activities.length === 0) {
    return <EmptyState />
  }

  return (
    <div className="divide-y divide-gray-100">
      {activities.slice(0, 10).map((activity) => (
        <ActivityItem key={activity.id} activity={activity} />
      ))}
    </div>
  )
}
