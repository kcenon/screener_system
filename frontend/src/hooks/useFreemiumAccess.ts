/**
 * Freemium access control hook.
 *
 * Provides feature access control and usage limits based on user authentication
 * status and subscription tier. Automatically tracks usage for public users.
 *
 * @module hooks/useFreemiumAccess
 * @category Hooks
 */

import { useMemo } from 'react'
import { useAuthStore } from '@/store/authStore'
import { FREEMIUM_LIMITS, type FreemiumTier } from '@/utils/freemiumConfig'
import { getUsageCount } from '@/utils/usageTracker'

/**
 * Freemium access limits and permissions.
 *
 * Contains all feature flags and usage limits for the current user's tier.
 *
 * @interface
 * @category Types
 */
export interface FreemiumLimits {
  /** Whether user is authenticated */
  isAuthenticated: boolean

  /** User's freemium tier */
  tier: FreemiumTier

  // Screener limits
  /** Maximum number of results to show in screening (-1 = unlimited) */
  maxScreeningResults: number
  /** Daily limit for screening operations (-1 = unlimited) */
  dailyScreeningLimit: number
  /** Number of screenings performed today */
  screeningsToday: number
  /** Number of screenings remaining today */
  screeningsRemaining: number
  /** Whether user can save filter presets */
  canSavePresets: boolean
  /** Whether user can export results to CSV */
  canExportResults: boolean

  // Stock detail limits
  /** Whether user can view financial statements */
  canViewFinancials: boolean
  /** Whether user can view all technical indicators */
  canViewAllTechnicals: boolean
  /** Number of technical indicators available */
  technicalIndicators: number
  /** Whether user can add stocks to watchlist */
  canAddToWatchlist: boolean

  // Comparison limits
  /** Maximum number of stocks that can be compared */
  maxCompareStocks: number

  // Watchlist limits
  /** Maximum number of watchlists user can create */
  maxWatchlists: number
  /** Maximum stocks per watchlist */
  maxStocksPerWatchlist: number

  // Chart limits
  /** Available chart timeframes */
  chartTimeframes: readonly string[]

  // Premium features (future)
  /** Whether AI recommendations are available */
  aiRecommendations?: boolean
  /** Whether API access is enabled */
  apiAccess?: boolean
  /** Whether price alerts are available */
  priceAlerts?: boolean
}

/**
 * Hook for accessing freemium limits and permissions.
 *
 * Determines user's tier (public/free/premium) and returns appropriate
 * feature access limits. For public users, tracks daily usage.
 *
 * ## Features
 *
 * - **Automatic Tier Detection**: Based on authentication status
 * - **Usage Tracking**: Tracks daily actions for public users
 * - **Type-Safe**: Full TypeScript support
 * - **Reactive**: Updates when auth state changes
 *
 * @returns Freemium limits object with all permissions and usage data
 *
 * @example
 * Basic usage
 * ```typescript
 * const { isAuthenticated, canSavePresets, maxScreeningResults } = useFreemiumAccess()
 *
 * if (!isAuthenticated && results.length > maxScreeningResults) {
 *   // Show upgrade prompt
 *   return <FreemiumBanner />
 * }
 * ```
 *
 * @example
 * Check daily limit
 * ```typescript
 * const { screeningsToday, dailyScreeningLimit, screeningsRemaining } = useFreemiumAccess()
 *
 * if (screeningsRemaining === 0) {
 *   showLimitReachedModal()
 *   return
 * }
 *
 * console.log(`${screeningsRemaining} searches remaining`)
 * ```
 *
 * @example
 * Feature gating
 * ```typescript
 * const { canViewFinancials, canAddToWatchlist } = useFreemiumAccess()
 *
 * return (
 *   <div>
 *     {canViewFinancials ? (
 *       <FinancialsTab />
 *     ) : (
 *       <LockedContent feature="Financial Statements" />
 *     )}
 *
 *     {canAddToWatchlist ? (
 *       <AddToWatchlistButton />
 *     ) : (
 *       <Button onClick={() => navigate('/login')}>
 *         Login to use watchlist
 *       </Button>
 *     )}
 *   </div>
 * )
 * ```
 *
 * @category Hooks
 */
export function useFreemiumAccess(): FreemiumLimits {
  const { user, isAuthenticated } = useAuthStore()

  return useMemo(() => {
    // Determine user tier
    let tier: FreemiumTier = 'public'
    if (isAuthenticated && user) {
      // Map User.tier to FreemiumTier
      // 'basic' users get 'free' tier features
      const userTier = user.tier
      if (userTier === 'premium') {
        tier = 'premium'
      } else {
        // 'free' and 'basic' both map to 'free' tier
        tier = 'free'
      }
    }

    // Get limits for tier
    const limits = FREEMIUM_LIMITS[tier]

    // Track usage for public users
    const screeningsToday = !isAuthenticated ? getUsageCount() : 0
    const screeningsRemaining =
      !isAuthenticated && limits.dailyScreeningLimit !== -1
        ? Math.max(0, limits.dailyScreeningLimit - screeningsToday)
        : -1

    return {
      isAuthenticated,
      tier,
      maxScreeningResults: limits.maxScreeningResults,
      dailyScreeningLimit: limits.dailyScreeningLimit,
      screeningsToday,
      screeningsRemaining,
      canSavePresets: limits.canSavePresets,
      canExportResults: limits.canExportResults,
      canViewFinancials: limits.canViewFinancials,
      canViewAllTechnicals: limits.canViewAllTechnicals,
      technicalIndicators: limits.technicalIndicators,
      canAddToWatchlist: limits.canAddToWatchlist,
      maxCompareStocks: limits.maxCompareStocks,
      maxWatchlists: limits.maxWatchlists,
      maxStocksPerWatchlist: limits.maxStocksPerWatchlist,
      chartTimeframes: limits.chartTimeframes,
      aiRecommendations:
        'aiRecommendations' in limits ? limits.aiRecommendations : false,
      apiAccess: 'apiAccess' in limits ? limits.apiAccess : false,
      priceAlerts: 'priceAlerts' in limits ? limits.priceAlerts : false,
    }
  }, [isAuthenticated, user])
}
