/**
 * Notifications Page
 *
 * Full page view for user notifications.
 * Displays all notifications with filtering options.
 */

import { useNotifications } from '../hooks/useNotifications'
import { NotificationList } from '../components/notifications'

export default function NotificationsPage() {
  const { markAllAsRead, unreadCount, total, isMarkingAllAsRead } = useNotifications()

  const handleMarkAllAsRead = async () => {
    if (unreadCount > 0) {
      await markAllAsRead()
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Notifications
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            {unreadCount > 0
              ? `${unreadCount} unread notification${unreadCount > 1 ? 's' : ''}`
              : 'All caught up!'}
          </p>
        </div>
        {unreadCount > 0 && (
          <button
            onClick={handleMarkAllAsRead}
            disabled={isMarkingAllAsRead}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            Mark All as Read
          </button>
        )}
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-600 dark:text-gray-400">Total Notifications</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {total}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-600 dark:text-gray-400">Unread</p>
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">
            {unreadCount}
          </p>
        </div>
      </div>

      {/* Notification List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <NotificationList />
      </div>
    </div>
  )
}
