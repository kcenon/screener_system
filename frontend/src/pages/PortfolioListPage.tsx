/**
 * Portfolio List Page
 *
 * Displays all user portfolios with summary metrics.
 * Provides create, delete, and navigate to detail actions.
 *
 * @module pages/PortfolioListPage
 * @category Pages
 */

import { useEffect, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { usePortfolios } from '../hooks/usePortfolios'
import { PortfolioCreate } from '../services/portfolioService'
import { Plus, AlertCircle, TrendingUp, TrendingDown, Wallet } from 'lucide-react'

/**
 * Create Portfolio Modal Component
 */
function CreatePortfolioModal({
  isOpen,
  onClose,
  onCreate,
}: {
  isOpen: boolean
  onClose: () => void
  onCreate: (data: PortfolioCreate) => Promise<void>
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await onCreate({ name, description: description || null })
      setName('')
      setDescription('')
      onClose()
    } catch (error) {
      console.error('Failed to create portfolio:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Create New Portfolio</h2>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Portfolio Name *
            </label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Growth Stocks"
            />
          </div>

          <div className="mb-6">
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description (optional)
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Describe your investment strategy..."
            />
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating...' : 'Create Portfolio'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

/**
 * Portfolio Card Component
 */
function PortfolioCard({
  portfolio,
  onClick,
  onDelete,
}: {
  portfolio: any
  onClick: () => void
  onDelete: () => void
}) {
  const totalValue = parseFloat(portfolio.total_value || '0')
  const dayChange = parseFloat(portfolio.day_change || '0')
  const dayChangePercent = parseFloat(portfolio.day_change_percent || '0')
  const returnPercent = parseFloat(portfolio.return_percent || '0')

  const isPositive = dayChange >= 0
  const isPositiveReturn = returnPercent >= 0

  return (
    <div
      onClick={onClick}
      className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">{portfolio.name}</h3>
          {portfolio.description && (
            <p className="text-sm text-gray-600 mt-1">{portfolio.description}</p>
          )}
        </div>
        {portfolio.is_default && (
          <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded">
            Default
          </span>
        )}
      </div>

      {/* Metrics */}
      <div className="space-y-3">
        {/* Total Value */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Total Value</span>
          <span className="text-lg font-semibold text-gray-900">
            ₩{totalValue.toLocaleString()}
          </span>
        </div>

        {/* Day Change */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Today</span>
          <div className="flex items-center gap-1">
            {isPositive ? (
              <TrendingUp className="w-4 h-4 text-green-600" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-600" />
            )}
            <span className={isPositive ? 'text-green-600' : 'text-red-600'}>
              {isPositive ? '+' : ''}₩{dayChange.toLocaleString()} ({dayChangePercent.toFixed(2)}%)
            </span>
          </div>
        </div>

        {/* Total Return */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Total Return</span>
          <span className={isPositiveReturn ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
            {isPositiveReturn ? '+' : ''}{returnPercent.toFixed(2)}%
          </span>
        </div>

        {/* Holdings Count */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <span className="text-sm text-gray-600">Holdings</span>
          <span className="text-sm font-medium text-gray-900">{portfolio.holding_count}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="mt-4 pt-4 border-t border-gray-100 flex gap-2">
        <button
          onClick={(e) => {
            e.stopPropagation()
            onDelete()
          }}
          className="text-sm text-red-600 hover:text-red-700 font-medium"
        >
          Delete
        </button>
      </div>
    </div>
  )
}

/**
 * Portfolio List Page Component
 */
export default function PortfolioListPage() {
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuthStore()
  const { portfolios, isLoading, isError, error, createPortfolio, deletePortfolio, refetch } = usePortfolios()

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

  // Set page title - must be called before any conditional returns
  useEffect(() => {
    document.title = 'Portfolios | Stock Screener'
  }, [])

  // Redirect if not authenticated
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />
  }

  const handleCreatePortfolio = async (data: PortfolioCreate) => {
    await createPortfolio.mutateAsync(data)
    refetch()
  }

  const handleDeletePortfolio = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this portfolio?')) {
      await deletePortfolio.mutateAsync(id)
      refetch()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <Wallet className="w-8 h-8" />
                My Portfolios
              </h1>
              <p className="mt-2 text-gray-600">
                Track your holdings and monitor performance across multiple portfolios
              </p>
            </div>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-5 h-5" />
              New Portfolio
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Error State */}
        {isError && (
          <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900">Error loading portfolios</h3>
              <p className="text-sm text-red-700 mt-1">
                {error instanceof Error ? error.message : 'Failed to load portfolios'}
              </p>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white border border-gray-200 rounded-lg p-6 animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && portfolios.length === 0 && (
          <div className="text-center py-12">
            <Wallet className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No portfolios yet</h3>
            <p className="text-gray-600 mb-6">
              Create your first portfolio to start tracking your investments
            </p>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-5 h-5" />
              Create Portfolio
            </button>
          </div>
        )}

        {/* Portfolio Grid */}
        {!isLoading && portfolios.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {portfolios.map((portfolio) => (
              <PortfolioCard
                key={portfolio.id}
                portfolio={portfolio}
                onClick={() => navigate(`/portfolios/${portfolio.id}`)}
                onDelete={() => handleDeletePortfolio(portfolio.id)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      <CreatePortfolioModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreate={handleCreatePortfolio}
      />
    </div>
  )
}
