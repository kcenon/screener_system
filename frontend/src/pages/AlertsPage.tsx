/**
 * Alerts Page
 *
 * Page for managing user alerts.
 * Displays alert list and creation form.
 */

import { useState } from 'react'
import { useAlerts } from '../hooks/useAlerts'
import { AlertForm, AlertList } from '../components/alerts'
import type { AlertCreate } from '../services/alertService'

export default function AlertsPage() {
  const { createAlert, isCreating, totalAlerts, activeAlerts } = useAlerts()
  const [showForm, setShowForm] = useState(false)

  const handleCreateAlert = async (data: AlertCreate) => {
    await createAlert(data)
    setShowForm(false)
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Price Alerts
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Get notified when stocks reach your target prices
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
        >
          {showForm ? 'Cancel' : 'Create Alert'}
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Total Alerts
          </p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {totalAlerts}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-600 dark:text-gray-400">Active</p>
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">
            {activeAlerts}
          </p>
        </div>
      </div>

      {/* Create Form */}
      {showForm && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Create New Alert
          </h2>
          <AlertForm
            onSubmit={handleCreateAlert}
            onCancel={() => setShowForm(false)}
            isSubmitting={isCreating}
          />
        </div>
      )}

      {/* Alert List */}
      <AlertList />
    </div>
  )
}
