/**
 * Freemium tier configuration and limits.
 *
 * Defines feature access and usage limits for different user tiers:
 * - Public (not authenticated)
 * - Free (registered users)
 * - Premium (future paid tier)
 *
 * @module utils/freemiumConfig
 * @category Utils
 */

/**
 * Freemium tier limits configuration.
 *
 * Centralized configuration for all freemium-related limits across tiers.
 * Use -1 to indicate unlimited access.
 *
 * @category Types
 */
export const FREEMIUM_LIMITS = {
  /**
   * Public tier (unauthenticated users)
   */
  public: {
    /** Maximum number of results shown in screening (vs. full results) */
    maxScreeningResults: 20,
    /** Daily limit for screening operations */
    dailyScreeningLimit: 10,
    /** Maximum number of stocks that can be compared simultaneously */
    maxCompareStocks: 2,
    /** Available chart timeframes for price charts */
    chartTimeframes: ['1D', '1W', '1M'] as const,
    /** Number of technical indicators available */
    technicalIndicators: 3,
    /** Can save filter presets */
    canSavePresets: false,
    /** Can export results to CSV */
    canExportResults: false,
    /** Can view financial statements */
    canViewFinancials: false,
    /** Can view all technical indicators */
    canViewAllTechnicals: false,
    /** Can add stocks to watchlist */
    canAddToWatchlist: false,
    /** Maximum number of watchlists */
    maxWatchlists: 0,
    /** Maximum stocks per watchlist */
    maxStocksPerWatchlist: 0,
  },

  /**
   * Free tier (registered users)
   */
  free: {
    /** Maximum number of results shown in screening (-1 = unlimited) */
    maxScreeningResults: -1,
    /** Daily limit for screening operations (-1 = unlimited) */
    dailyScreeningLimit: -1,
    /** Maximum number of stocks that can be compared simultaneously */
    maxCompareStocks: 5,
    /** Available chart timeframes for price charts */
    chartTimeframes: ['1D', '1W', '1M', '3M', '6M', '1Y', '3Y'] as const,
    /** Number of technical indicators available (-1 = all) */
    technicalIndicators: -1,
    /** Can save filter presets */
    canSavePresets: true,
    /** Can export results to CSV */
    canExportResults: true,
    /** Can view financial statements */
    canViewFinancials: true,
    /** Can view all technical indicators */
    canViewAllTechnicals: true,
    /** Can add stocks to watchlist */
    canAddToWatchlist: true,
    /** Maximum number of watchlists */
    maxWatchlists: 10,
    /** Maximum stocks per watchlist */
    maxStocksPerWatchlist: 100,
  },

  /**
   * Premium tier (future paid subscription)
   */
  premium: {
    /** Maximum number of results shown in screening (-1 = unlimited) */
    maxScreeningResults: -1,
    /** Daily limit for screening operations (-1 = unlimited) */
    dailyScreeningLimit: -1,
    /** Maximum number of stocks that can be compared simultaneously */
    maxCompareStocks: 10,
    /** Available chart timeframes for price charts */
    chartTimeframes: ['1D', '1W', '1M', '3M', '6M', '1Y', '3Y', '5Y'] as const,
    /** Number of technical indicators available (-1 = all) */
    technicalIndicators: -1,
    /** Can save filter presets */
    canSavePresets: true,
    /** Can export results to CSV */
    canExportResults: true,
    /** Can view financial statements */
    canViewFinancials: true,
    /** Can view all technical indicators */
    canViewAllTechnicals: true,
    /** Can add stocks to watchlist */
    canAddToWatchlist: true,
    /** Maximum number of watchlists (-1 = unlimited) */
    maxWatchlists: -1,
    /** Maximum stocks per watchlist (-1 = unlimited) */
    maxStocksPerWatchlist: -1,
    /** AI-powered stock recommendations */
    aiRecommendations: true,
    /** API access enabled */
    apiAccess: true,
    /** Price alerts enabled */
    priceAlerts: true,
  },
} as const

/**
 * User tier types.
 */
export type FreemiumTier = 'public' | 'free' | 'premium'

/**
 * Get limits for a specific tier.
 *
 * @param tier - The freemium tier
 * @returns Configuration object for the specified tier
 *
 * @example
 * ```typescript
 * const limits = getTierLimits('free')
 * console.log(limits.maxScreeningResults) // -1 (unlimited)
 * ```
 */
export function getTierLimits(tier: FreemiumTier) {
  return FREEMIUM_LIMITS[tier]
}

/**
 * Check if a feature is available for a tier.
 *
 * @param tier - The freemium tier
 * @param feature - The feature name
 * @returns True if feature is available for this tier
 *
 * @example
 * ```typescript
 * const canExport = isFeatureAvailable('public', 'canExportResults')
 * console.log(canExport) // false
 * ```
 */
export function isFeatureAvailable(
  tier: FreemiumTier,
  feature: keyof typeof FREEMIUM_LIMITS.public,
): boolean {
  const limits = getTierLimits(tier)
  const value = limits[feature as keyof typeof limits]

  if (typeof value === 'boolean') {
    return value
  }

  if (typeof value === 'number') {
    return value !== 0
  }

  if (Array.isArray(value)) {
    return value.length > 0
  }

  return true
}
