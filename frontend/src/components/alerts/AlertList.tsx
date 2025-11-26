/**
 * Alert List Component
 *
 * Displays list of user alerts with filtering and actions.
 * Shows empty state when no alerts exist.
 */

import React from 'react'
import { useAlerts } from '../../hooks/useAlerts'
import { AlertCard } from './AlertCard'

export const AlertList: React.FC = () => {
  const {
    alerts,
    isLoading,
    deleteAlert,
    toggleAlert,
    isDeleting,
    isToggling,
  } = useAlerts()

  // Wrapper to match AlertCard's expected signature
  const handleToggle = async (id: number): Promise<void> => {
    await toggleAlert(id)
  }

  if (isLoading) {
    return (
      <div className="p-8 text-center">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
        <p className="mt-2 text-gray-500 dark:text-gray-400">Loading alerts...</p>
      </div>
    )
  }

  if (alerts.length === 0) {
    return (
      <div className="p-8 text-center">
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
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>
        <p className="text-lg font-medium text-gray-900 dark:text-white">No alerts yet</p>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Create your first alert to get notified about price changes
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {alerts.map((alert) => (
        <AlertCard
          key={alert.id}
          alert={alert}
          onToggle={handleToggle}
          onDelete={deleteAlert}
          isToggling={isToggling}
          isDeleting={isDeleting}
        />
      ))}
    </div>
  )
}
