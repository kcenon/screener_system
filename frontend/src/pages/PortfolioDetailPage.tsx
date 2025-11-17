/**
 * Portfolio Detail Page
 *
 * Displays detailed portfolio information including:
 * - Portfolio header with name and description
 * - Performance metrics dashboard
 * - Holdings table with current values
 * - Transaction history
 * - Quick add transaction form
 *
 * @module pages/PortfolioDetailPage
 * @category Pages
 */

import { useEffect, useState } from 'react'
import { Navigate, useParams, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { usePortfolioDetail } from '../hooks/usePortfolioDetail'
import { usePortfolioPerformance } from '../hooks/usePortfolioPerformance'
import { useTransactions } from '../hooks/useTransactions'
import { TransactionType } from '../services/portfolioService'
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Plus,
  AlertCircle,
  DollarSign,
  Package,
} from 'lucide-react'

/**
 * Performance Metrics Card Component
 */
function PerformanceMetrics({ performance }: { performance: any }) {
  if (!performance) return null

  const totalValue = parseFloat(performance.total_value || '0')
  const totalCost = parseFloat(performance.total_cost || '0')
  const totalGain = parseFloat(performance.total_gain || '0')
  const totalReturnPercent = parseFloat(performance.total_return_percent || '0')
  const dayChange = parseFloat(performance.day_change || '0')
  const dayChangePercent = parseFloat(performance.day_change_percent || '0')

  const isPositiveReturn = totalGain >= 0
  const isPositiveDay = dayChange >= 0

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Total Value */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Total Value</span>
          <DollarSign className="w-4 h-4 text-gray-400" />
        </div>
        <div className="text-2xl font-bold text-gray-900">₩{totalValue.toLocaleString()}</div>
        <div className="text-xs text-gray-500 mt-1">Cost: ₩{totalCost.toLocaleString()}</div>
      </div>

      {/* Total Gain/Loss */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Total Gain/Loss</span>
          {isPositiveReturn ? (
            <TrendingUp className="w-4 h-4 text-green-600" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-600" />
          )}
        </div>
        <div className={`text-2xl font-bold ${isPositiveReturn ? 'text-green-600' : 'text-red-600'}`}>
          {isPositiveReturn ? '+' : ''}₩{totalGain.toLocaleString()}
        </div>
        <div className={`text-xs mt-1 ${isPositiveReturn ? 'text-green-600' : 'text-red-600'}`}>
          {isPositiveReturn ? '+' : ''}{totalReturnPercent.toFixed(2)}%
        </div>
      </div>

      {/* Day Change */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Today's Change</span>
          {isPositiveDay ? (
            <TrendingUp className="w-4 h-4 text-green-600" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-600" />
          )}
        </div>
        <div className={`text-2xl font-bold ${isPositiveDay ? 'text-green-600' : 'text-red-600'}`}>
          {isPositiveDay ? '+' : ''}₩{dayChange.toLocaleString()}
        </div>
        <div className={`text-xs mt-1 ${isPositiveDay ? 'text-green-600' : 'text-red-600'}`}>
          {isPositiveDay ? '+' : ''}{dayChangePercent.toFixed(2)}%
        </div>
      </div>

      {/* Holdings Count */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Holdings</span>
          <Package className="w-4 h-4 text-gray-400" />
        </div>
        <div className="text-2xl font-bold text-gray-900">{performance.holding_count || 0}</div>
        <div className="text-xs text-gray-500 mt-1">Total positions</div>
      </div>
    </div>
  )
}

/**
 * Holdings Table Component
 */
function HoldingsTable({ holdings }: { holdings: any[] }) {
  if (holdings.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Package className="w-12 h-12 text-gray-400 mx-auto mb-2" />
        <p>No holdings yet. Add a transaction to get started.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Symbol</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Name</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-600 uppercase">Shares</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-600 uppercase">Avg Cost</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-600 uppercase">Current</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-600 uppercase">Value</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-600 uppercase">Gain/Loss</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-600 uppercase">Return %</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {holdings.map((holding) => {
            const gain = parseFloat(holding.unrealized_gain || '0')
            const gainPercent = parseFloat(holding.unrealized_gain_percent || '0')
            const isPositive = gain >= 0

            return (
              <tr key={holding.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-gray-900">{holding.stock_symbol}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{holding.stock_name || '-'}</td>
                <td className="px-4 py-3 text-sm text-right text-gray-900">{parseFloat(holding.shares).toLocaleString()}</td>
                <td className="px-4 py-3 text-sm text-right text-gray-900">₩{parseFloat(holding.average_cost).toLocaleString()}</td>
                <td className="px-4 py-3 text-sm text-right text-gray-900">₩{parseFloat(holding.current_price || '0').toLocaleString()}</td>
                <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">₩{parseFloat(holding.current_value || '0').toLocaleString()}</td>
                <td className={`px-4 py-3 text-sm text-right font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                  {isPositive ? '+' : ''}₩{gain.toLocaleString()}
                </td>
                <td className={`px-4 py-3 text-sm text-right font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                  {isPositive ? '+' : ''}{gainPercent.toFixed(2)}%
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

/**
 * Add Transaction Form Component
 */
function AddTransactionForm({
  portfolioId,
  onSuccess,
}: {
  portfolioId: number
  onSuccess: () => void
}) {
  const { addTransaction } = useTransactions(portfolioId)
  const [formData, setFormData] = useState({
    stock_symbol: '',
    transaction_type: TransactionType.BUY,
    shares: '',
    price: '',
    commission: '0',
    notes: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await addTransaction.mutateAsync({
        stock_symbol: formData.stock_symbol,
        transaction_type: formData.transaction_type,
        shares: parseFloat(formData.shares),
        price: parseFloat(formData.price),
        commission: parseFloat(formData.commission),
        transaction_date: new Date().toISOString(),
        notes: formData.notes || null,
      })
      setFormData({
        stock_symbol: '',
        transaction_type: TransactionType.BUY,
        shares: '',
        price: '',
        commission: '0',
        notes: '',
      })
      onSuccess()
    } catch (error) {
      console.error('Failed to add transaction:', error)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Transaction</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select
            value={formData.transaction_type}
            onChange={(e) => setFormData({ ...formData, transaction_type: e.target.value as TransactionType })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
          >
            <option value={TransactionType.BUY}>Buy</option>
            <option value={TransactionType.SELL}>Sell</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Symbol</label>
          <input
            type="text"
            value={formData.stock_symbol}
            onChange={(e) => setFormData({ ...formData, stock_symbol: e.target.value })}
            placeholder="e.g., 005930"
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Shares</label>
          <input
            type="number"
            step="0.01"
            value={formData.shares}
            onChange={(e) => setFormData({ ...formData, shares: e.target.value })}
            placeholder="10"
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Price</label>
          <input
            type="number"
            step="0.01"
            value={formData.price}
            onChange={(e) => setFormData({ ...formData, price: e.target.value })}
            placeholder="70000"
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Commission (₩)</label>
          <input
            type="number"
            step="0.01"
            value={formData.commission}
            onChange={(e) => setFormData({ ...formData, commission: e.target.value })}
            placeholder="500"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div className="md:col-span-2 lg:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
          <input
            type="text"
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            placeholder="Add notes..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div className="flex items-end">
          <button
            type="submit"
            disabled={addTransaction.isPending}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Plus className="w-4 h-4" />
            {addTransaction.isPending ? 'Adding...' : 'Add Transaction'}
          </button>
        </div>
      </div>
    </form>
  )
}

/**
 * Portfolio Detail Page Component
 */
export default function PortfolioDetailPage() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const portfolioId = id ? parseInt(id, 10) : undefined

  const { user, isAuthenticated } = useAuthStore()
  const { portfolio, holdings, isLoading, isError, error, refresh } = usePortfolioDetail(portfolioId)
  const { performance, isLoading: isPerfLoading } = usePortfolioPerformance(portfolioId)
  const { transactions, isLoading: isTransLoading } = useTransactions(portfolioId, 0, 10)

  // Redirect if not authenticated
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />
  }

  useEffect(() => {
    if (portfolio) {
      document.title = `${portfolio.name} | Stock Screener`
    }
  }, [portfolio])

  if (isLoading || isPerfLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading portfolio...</p>
        </div>
      </div>
    )
  }

  if (isError || !portfolio) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-red-900 text-center mb-2">Error</h2>
          <p className="text-red-700 text-center">
            {error instanceof Error ? error.message : 'Failed to load portfolio'}
          </p>
          <button
            onClick={() => navigate('/portfolios')}
            className="mt-4 w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Back to Portfolios
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-6">
          <button
            onClick={() => navigate('/portfolios')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Portfolios
          </button>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{portfolio.name}</h1>
              {portfolio.description && (
                <p className="mt-2 text-gray-600">{portfolio.description}</p>
              )}
            </div>
            {portfolio.is_default && (
              <span className="px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded">
                Default Portfolio
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* Performance Metrics */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Performance</h2>
          <PerformanceMetrics performance={performance} />
        </section>

        {/* Add Transaction Form */}
        <section>
          <AddTransactionForm portfolioId={portfolioId!} onSuccess={refresh} />
        </section>

        {/* Holdings Table */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Holdings</h2>
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <HoldingsTable holdings={holdings} />
          </div>
        </section>

        {/* Recent Transactions */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Transactions</h2>
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            {isTransLoading ? (
              <p className="text-center text-gray-500">Loading transactions...</p>
            ) : transactions.length === 0 ? (
              <p className="text-center text-gray-500">No transactions yet</p>
            ) : (
              <div className="space-y-3">
                {transactions.slice(0, 5).map((tx) => (
                  <div key={tx.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        tx.transaction_type === TransactionType.BUY
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {tx.transaction_type}
                      </span>
                      <span className="font-medium text-gray-900">{tx.stock_symbol}</span>
                      <span className="text-sm text-gray-600">
                        {parseFloat(tx.shares).toLocaleString()} shares @ ₩{parseFloat(tx.price).toLocaleString()}
                      </span>
                    </div>
                    <span className="text-sm text-gray-500">
                      {new Date(tx.transaction_date).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}
