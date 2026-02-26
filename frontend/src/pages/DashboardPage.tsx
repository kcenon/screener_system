/**
 * User Dashboard Page
 *
 * Main landing page for authenticated users showing:
 * - Market summary with indices
 * - User's watchlists
 * - Recent screening activity
 * - Quick action buttons
 * - Personalized insights
 */

import { useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { useDashboard } from '../hooks/useDashboard'
import MarketSummaryWidget from '../components/dashboard/MarketSummaryWidget'
import WatchlistWidget from '../components/dashboard/WatchlistWidget'
import RecentActivityWidget from '../components/dashboard/RecentActivityWidget'
import QuickActionsWidget from '../components/dashboard/QuickActionsWidget'
import PlatformStatsWidget from '../components/dashboard/PlatformStatsWidget'
import { RecommendationList } from '../components/recommendations/RecommendationList'
import { AlertCircle } from 'lucide-react'

/**
 * Error Message Component
 */
function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
      <div>
        <h3 className="font-semibold text-red-900">Error loading dashboard</h3>
        <p className="text-sm text-red-700 mt-1">{message}</p>
      </div>
    </div>
  )
}

/**
 * DashboardPage Component
 *
 * Provides a comprehensive overview of user's activity, watchlists,
 * and market insights in a single, organized dashboard view.
 */
export default function DashboardPage() {
  const { user, isAuthenticated } = useAuthStore()
  const { data, isLoading, error } = useDashboard()

  // Set page title - must be called before any conditional returns
  useEffect(() => {
    document.title = 'Dashboard | Stock Screener'
  }, [])

  // Redirect to login if not authenticated
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user.name}!
          </h1>
          <p className="mt-2 text-gray-600">
            Here's what's happening with your portfolio and the market today.
          </p>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Error State */}
        {error && (
          <div className="mb-8">
            <ErrorMessage
              message={
                error instanceof Error
                  ? error.message
                  : 'Failed to load dashboard data'
              }
            />
          </div>
        )}

        {/* Market Summary Section */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Market Overview
          </h2>
          <div className="bg-white rounded-lg shadow p-6">
            <MarketSummaryWidget
              kospi={data?.market_indices.kospi}
              kosdaq={data?.market_indices.kosdaq}
              isLoading={isLoading}
            />
          </div>
        </section>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column (2/3 width on large screens) */}
          <div className="lg:col-span-2 space-y-8">
            {/* Recommendations Section */}
            <section>
              <RecommendationList />
            </section>

            {/* Watchlist Widget */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                My Watchlists
              </h2>
              <div className="bg-white rounded-lg shadow p-6">
                <WatchlistWidget
                  watchlists={data?.watchlists || []}
                  isLoading={isLoading}
                />
              </div>
            </section>

            {/* Recent Activity Widget */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Recent Activity
              </h2>
              <div className="bg-white rounded-lg shadow p-6">
                <RecentActivityWidget
                  activities={data?.recent_activities || []}
                  isLoading={isLoading}
                />
              </div>
            </section>
          </div>

          {/* Right Column (1/3 width on large screens) */}
          <div className="space-y-8">
            {/* Quick Actions Widget */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Quick Actions
              </h2>
              <div className="bg-white rounded-lg shadow p-6">
                <QuickActionsWidget />
              </div>
            </section>

            {/* Platform Stats Widget */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Your Stats
              </h2>
              <div className="bg-white rounded-lg shadow p-6">
                <PlatformStatsWidget
                  screeningCount={data?.user_stats.screening_count || 0}
                  totalWatchlistStocks={
                    data?.user_stats.total_watchlist_stocks || 0
                  }
                  lastLogin={data?.user_stats.last_login}
                  isLoading={isLoading}
                />
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}
