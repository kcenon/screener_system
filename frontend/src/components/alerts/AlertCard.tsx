/**
 * Alert Card Component
 *
 * Displays single alert with toggle and delete actions.
 * Shows alert status, type, condition, and stock information.
 */

import React from 'react'
import { alertService, type Alert } from '../../services/alertService'

interface AlertCardProps {
  alert: Alert
  onToggle: (id: number) => Promise<void>
  onDelete: (id: number) => Promise<void>
  isToggling?: boolean
  isDeleting?: boolean
}

export const AlertCard: React.FC<AlertCardProps> = ({
  alert,
  onToggle,
  onDelete,
  isToggling,
  isDeleting,
}) => {
  const handleToggle = () => onToggle(alert.id)
  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this alert?')) {
      onDelete(alert.id)
    }
  }

  const typeDisplay = alertService.getAlertTypeDisplay(alert.alert_type)
  const conditionDisplay = alertService.formatCondition(alert)

  const statusBadge = alert.triggered_at ? (
    <span className="px-2 py-1 text-xs font-semibold text-green-800 bg-green-100 dark:bg-green-900 dark:text-green-200 rounded">
      Triggered
    </span>
  ) : alert.is_active ? (
    <span className="px-2 py-1 text-xs font-semibold text-blue-800 bg-blue-100 dark:bg-blue-900 dark:text-blue-200 rounded">
      Active
    </span>
  ) : (
    <span className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 dark:bg-gray-700 dark:text-gray-300 rounded">
      Inactive
    </span>
  )

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        {/* Left Side - Alert Info */}
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {alert.stock_code}
            </h3>
            {statusBadge}
            {alert.is_recurring && (
              <span className="px-2 py-1 text-xs font-semibold text-purple-800 bg-purple-100 dark:bg-purple-900 dark:text-purple-200 rounded">
                Recurring
              </span>
            )}
          </div>

          <p className="text-sm text-gray-600 dark:text-gray-400">
            <span className="font-medium">{typeDisplay}:</span> {conditionDisplay}
          </p>

          {alert.triggered_at && (
            <p className="text-xs text-green-600 dark:text-green-400 mt-1">
              Triggered on {new Date(alert.triggered_at).toLocaleString()}
            </p>
          )}

          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
            Created {new Date(alert.created_at).toLocaleDateString()}
          </p>
        </div>

        {/* Right Side - Actions */}
        <div className="flex items-center space-x-2 ml-4">
          {/* Toggle Active */}
          <button
            onClick={handleToggle}
            disabled={isToggling || isDeleting}
            className={`
              p-2 rounded-lg transition-colors
              ${
                alert.is_active
                  ? 'text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-900/30'
                  : 'text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
              }
              disabled:opacity-50 disabled:cursor-not-allowed
            `}
            title={alert.is_active ? 'Deactivate' : 'Activate'}
          >
            {alert.is_active ? (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M13.477 14.89A6 6 0 015.11 6.524l8.367 8.368zm1.414-1.414L6.524 5.11a6 6 0 018.367 8.367zM18 10a8 8 0 11-16 0 8 8 0 0116 0z"
                  clipRule="evenodd"
                />
              </svg>
            )}
          </button>

          {/* Delete */}
          <button
            onClick={handleDelete}
            disabled={isToggling || isDeleting}
            className="p-2 text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/30 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Delete alert"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
