/**
 * Notification List Component
 *
 * Displays list of notifications with infinite scroll.
 * Supports filtering and mark as read operations.
 */

import React from 'react'
import { useNotifications } from '../../hooks/useNotifications'
import { notificationService } from '../../services/notificationService'
import type { Notification } from '../../services/notificationService'

interface NotificationListProps {
  compact?: boolean
  limit?: number
  onNotificationClick?: () => void
}

export const NotificationList: React.FC<NotificationListProps> = ({
  compact = false,
  limit,
  onNotificationClick,
}) => {
  const { notifications, isLoading, hasMore, loadMore, markAsRead } =
    useNotifications()

  const displayNotifications = limit
    ? notifications.slice(0, limit)
    : notifications

  if (isLoading && notifications.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500 dark:text-gray-400">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
        <p className="mt-2">Loading notifications...</p>
      </div>
    )
  }

  if (notifications.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500 dark:text-gray-400">
        <svg
          className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
          />
        </svg>
        <p className="text-lg font-medium">No notifications yet</p>
        <p className="text-sm mt-1">
          We'll notify you when something important happens
        </p>
      </div>
    )
  }

  return (
    <div>
      {displayNotifications.map(notification => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          compact={compact}
          onMarkAsRead={markAsRead}
          onClick={onNotificationClick}
        />
      ))}

      {!compact && !limit && hasMore && (
        <div className="p-4 text-center">
          <button
            onClick={() => loadMore()}
            className="px-4 py-2 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
          >
            Load More
          </button>
        </div>
      )}
    </div>
  )
}

interface NotificationItemProps {
  notification: Notification
  compact?: boolean
  onMarkAsRead: (id: number) => Promise<void>
  onClick?: () => void
}

const NotificationItem: React.FC<NotificationItemProps> = ({
  notification,
  compact,
  onMarkAsRead,
  onClick,
}) => {
  const handleClick = async () => {
    if (!notification.is_read) {
      await onMarkAsRead(notification.id)
    }
    onClick?.()
  }

  const priorityColor = notificationService.getPriorityColor(
    notification.priority,
  )
  const timeAgo = notificationService.formatTimeAgo(notification.created_at)

  return (
    <div
      onClick={handleClick}
      className={`
        p-4 border-b border-gray-200 dark:border-gray-700 cursor-pointer transition-colors
        ${notification.is_read ? 'bg-white dark:bg-gray-800' : 'bg-blue-50 dark:bg-gray-700'}
        hover:bg-gray-50 dark:hover:bg-gray-750
      `}
    >
      <div className="flex items-start space-x-3">
        {/* Icon */}
        <div className={`flex-shrink-0 ${priorityColor}`}>
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            {notification.title}
          </p>
          {!compact && (
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              {notification.message}
            </p>
          )}
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-500">
            {timeAgo}
          </p>
        </div>

        {/* Unread Indicator */}
        {!notification.is_read && (
          <div className="flex-shrink-0">
            <div className="w-2 h-2 bg-blue-600 rounded-full" />
          </div>
        )}
      </div>
    </div>
  )
}
