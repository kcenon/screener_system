/**
 * Alert Form Component
 *
 * Form for creating and editing stock price alerts.
 * Supports all alert types with dynamic condition inputs.
 */

import React, { useState } from 'react'
import { AlertType, type AlertCreate } from '../../services/alertService'

interface AlertFormProps {
  initialData?: Partial<AlertCreate>
  onSubmit: (data: AlertCreate) => Promise<void>
  onCancel?: () => void
  isSubmitting?: boolean
}

export const AlertForm: React.FC<AlertFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting = false,
}) => {
  const [stockCode, setStockCode] = useState(initialData?.stock_code || '')
  const [alertType, setAlertType] = useState<AlertType>(
    initialData?.alert_type || AlertType.PRICE_ABOVE
  )
  const [conditionValue, setConditionValue] = useState(
    initialData?.condition_value?.toString() || ''
  )
  const [isRecurring, setIsRecurring] = useState(initialData?.is_recurring || false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const data: AlertCreate = {
      stock_code: stockCode.trim(),
      alert_type: alertType,
      condition_value: parseFloat(conditionValue),
      is_recurring: isRecurring,
    }

    await onSubmit(data)
  }

  const getConditionLabel = () => {
    switch (alertType) {
      case AlertType.PRICE_ABOVE:
      case AlertType.PRICE_BELOW:
        return 'Target Price (₩)'
      case AlertType.VOLUME_SPIKE:
        return 'Volume Multiplier (e.g., 2.0)'
      case AlertType.CHANGE_PERCENT_ABOVE:
      case AlertType.CHANGE_PERCENT_BELOW:
        return 'Percentage (%)'
      default:
        return 'Condition Value'
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Stock Code */}
      <div>
        <label
          htmlFor="stock_code"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
        >
          Stock Code *
        </label>
        <input
          id="stock_code"
          type="text"
          value={stockCode}
          onChange={(e) => setStockCode(e.target.value)}
          placeholder="e.g., 005930"
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          required
        />
      </div>

      {/* Alert Type */}
      <div>
        <label
          htmlFor="alert_type"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
        >
          Alert Type *
        </label>
        <select
          id="alert_type"
          value={alertType}
          onChange={(e) => setAlertType(e.target.value as AlertType)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          required
        >
          <option value={AlertType.PRICE_ABOVE}>Price Above</option>
          <option value={AlertType.PRICE_BELOW}>Price Below</option>
          <option value={AlertType.VOLUME_SPIKE}>Volume Spike</option>
          <option value={AlertType.CHANGE_PERCENT_ABOVE}>Price Up (%)</option>
          <option value={AlertType.CHANGE_PERCENT_BELOW}>Price Down (%)</option>
        </select>
      </div>

      {/* Condition Value */}
      <div>
        <label
          htmlFor="condition_value"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
        >
          {getConditionLabel()} *
        </label>
        <input
          id="condition_value"
          type="number"
          step="any"
          value={conditionValue}
          onChange={(e) => setConditionValue(e.target.value)}
          placeholder={alertType === AlertType.VOLUME_SPIKE ? '2.0' : '70000'}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          required
        />
      </div>

      {/* Recurring Option */}
      <div className="flex items-center">
        <input
          id="is_recurring"
          type="checkbox"
          checked={isRecurring}
          onChange={(e) => setIsRecurring(e.target.checked)}
          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
        />
        <label
          htmlFor="is_recurring"
          className="ml-2 text-sm text-gray-700 dark:text-gray-300"
        >
          Recurring alert (reactivate after trigger)
        </label>
      </div>

      {/* Buttons */}
      <div className="flex space-x-3 pt-4">
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {isSubmitting ? 'Creating...' : 'Create Alert'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}
