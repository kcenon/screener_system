/**
 * Analytics Hooks
 *
 * React hooks for integrating analytics tracking into components.
 * Provides convenient methods for tracking events, page views, and user interactions.
 */

import { useCallback, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { analytics, AnalyticsEvents } from '../services/analytics'

// ============================================================================
// Page Tracking Hook
// ============================================================================

/**
 * Hook that automatically tracks page views when the route changes
 *
 * @example
 * ```tsx
 * // In your App or layout component
 * function AppLayout() {
 *   usePageTracking()
 *   return <Outlet />
 * }
 * ```
 */
export function usePageTracking(): void {
  const location = useLocation()
  const isFirstRender = useRef(true)

  useEffect(() => {
    // Skip first render to avoid double tracking with strict mode
    if (isFirstRender.current) {
      isFirstRender.current = false
      // Still track the initial page view
    }

    const pageName = getPageNameFromPath(location.pathname)

    analytics.page(pageName, {
      search: location.search,
      hash: location.hash,
      referrer: document.referrer,
    })
  }, [location.pathname, location.search])
}

/**
 * Convert URL path to human-readable page name
 */
function getPageNameFromPath(path: string): string {
  // Remove leading/trailing slashes and split
  const segments = path.replace(/^\/|\/$/g, '').split('/')

  if (segments.length === 0 || segments[0] === '') {
    return 'Home'
  }

  // Map common routes to readable names
  const routeNames: Record<string, string> = {
    screener: 'Screener',
    stocks: 'Stock Detail',
    portfolio: 'Portfolio',
    portfolios: 'Portfolio List',
    watchlist: 'Watchlist',
    alerts: 'Alerts',
    settings: 'Settings',
    profile: 'Profile',
    login: 'Login',
    register: 'Register',
    'forgot-password': 'Forgot Password',
    'reset-password': 'Reset Password',
    pricing: 'Pricing',
    checkout: 'Checkout',
    billing: 'Billing',
    verify: 'Email Verification',
  }

  const basePath = segments[0]
  const baseName = routeNames[basePath] || capitalizeFirst(basePath)

  // Add detail identifier if present (e.g., /stocks/005930 -> "Stock Detail: 005930")
  if (segments.length > 1) {
    return `${baseName}: ${segments[1]}`
  }

  return baseName
}

function capitalizeFirst(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1).replace(/-/g, ' ')
}

// ============================================================================
// Event Tracking Hook
// ============================================================================

/**
 * Hook that provides event tracking methods
 *
 * @example
 * ```tsx
 * function FilterPanel() {
 *   const { trackFilter, trackSearch, trackConversion } = useEventTracking()
 *
 *   const handleFilterChange = (type, value) => {
 *     trackFilter(type, value, activeFiltersCount)
 *     applyFilter(type, value)
 *   }
 *
 *   return <FilterControls onChange={handleFilterChange} />
 * }
 * ```
 */
export function useEventTracking() {
  const trackFilter = useCallback(
    (
      filterType: string,
      value: string | number | boolean,
      filtersCount: number,
      resultsCount?: number,
    ) => {
      analytics.track(AnalyticsEvents.FILTER_APPLIED, {
        filter_type: filterType,
        filter_value: String(value),
        filters_count: filtersCount,
        results_count: resultsCount,
      })
    },
    [],
  )

  const trackFilterCleared = useCallback((filterType?: string) => {
    analytics.track(AnalyticsEvents.FILTER_CLEARED, {
      filter_type: filterType || 'all',
    })
  }, [])

  const trackStockView = useCallback(
    (
      code: string,
      name: string,
      source: 'screener' | 'search' | 'watchlist' | 'portfolio' | 'direct' | 'alert',
    ) => {
      analytics.track(AnalyticsEvents.STOCK_VIEWED, {
        stock_code: code,
        stock_name: name,
        source,
      })
    },
    [],
  )

  const trackSearch = useCallback(
    (query: string, resultsCount: number, searchType: 'stock' | 'filter' | 'global') => {
      analytics.track(AnalyticsEvents.SEARCH_PERFORMED, {
        query,
        results_count: resultsCount,
        search_type: searchType,
      })
    },
    [],
  )

  const trackExport = useCallback(
    (
      format: 'csv' | 'json' | 'excel',
      itemsCount: number,
      exportType: 'screener' | 'portfolio' | 'watchlist',
    ) => {
      analytics.track(AnalyticsEvents.RESULTS_EXPORTED, {
        export_format: format,
        items_count: itemsCount,
        export_type: exportType,
      })
    },
    [],
  )

  const trackConversion = useCallback(
    (
      ctaLocation: string,
      options?: {
        ctaText?: string
        featureBlocked?: string
        currentTier?: 'public' | 'free' | 'premium'
      },
    ) => {
      analytics.track(AnalyticsEvents.UPGRADE_CTA_CLICKED, {
        cta_location: ctaLocation,
        cta_text: options?.ctaText,
        feature_blocked: options?.featureBlocked,
        current_tier: options?.currentTier,
      })
    },
    [],
  )

  const trackError = useCallback(
    (
      errorType: string,
      message: string,
      options?: {
        errorCode?: string
        component?: string
        action?: string
      },
    ) => {
      analytics.track(AnalyticsEvents.ERROR_OCCURRED, {
        error_type: errorType,
        error_message: message,
        error_code: options?.errorCode,
        component: options?.component,
        action: options?.action,
      })
    },
    [],
  )

  const trackSort = useCallback((column: string, direction: 'asc' | 'desc') => {
    analytics.track(AnalyticsEvents.RESULTS_SORTED, {
      sort_column: column,
      sort_direction: direction,
    })
  }, [])

  const trackPagination = useCallback((page: number, pageSize: number, totalItems: number) => {
    analytics.track(AnalyticsEvents.RESULTS_PAGINATED, {
      page_number: page,
      page_size: pageSize,
      total_items: totalItems,
    })
  }, [])

  const trackTabSwitch = useCallback((tabName: string, tabIndex: number) => {
    analytics.track(AnalyticsEvents.TAB_SWITCHED, {
      tab_name: tabName,
      tab_index: tabIndex,
    })
  }, [])

  const trackModal = useCallback((modalName: string, action: 'opened' | 'closed') => {
    const event =
      action === 'opened' ? AnalyticsEvents.MODAL_OPENED : AnalyticsEvents.MODAL_CLOSED
    analytics.track(event, {
      modal_name: modalName,
    })
  }, [])

  const trackThemeChange = useCallback((theme: 'light' | 'dark' | 'system') => {
    analytics.track(AnalyticsEvents.THEME_CHANGED, {
      theme,
    })
  }, [])

  const trackCustom = useCallback((event: string, properties?: Record<string, unknown>) => {
    analytics.track(event, properties)
  }, [])

  return {
    trackFilter,
    trackFilterCleared,
    trackStockView,
    trackSearch,
    trackExport,
    trackConversion,
    trackError,
    trackSort,
    trackPagination,
    trackTabSwitch,
    trackModal,
    trackThemeChange,
    trackCustom,
  }
}

// ============================================================================
// Timing Hook
// ============================================================================

/**
 * Hook for tracking component render/load times
 *
 * @example
 * ```tsx
 * function HeavyComponent() {
 *   const { startTiming, endTiming } = useTiming('HeavyComponent')
 *
 *   useEffect(() => {
 *     startTiming()
 *     loadData().then(() => {
 *       endTiming('data_loaded')
 *     })
 *   }, [])
 *
 *   return <div>...</div>
 * }
 * ```
 */
export function useTiming(componentName: string) {
  const startTimeRef = useRef<number | null>(null)

  const startTiming = useCallback(() => {
    startTimeRef.current = performance.now()
  }, [])

  const endTiming = useCallback(
    (label?: string) => {
      if (startTimeRef.current === null) {
        console.warn(`[useTiming] startTiming() was not called for ${componentName}`)
        return
      }

      const duration = Math.round(performance.now() - startTimeRef.current)
      analytics.timing(componentName, 'render', duration, label)
      startTimeRef.current = null

      return duration
    },
    [componentName],
  )

  // Automatically track mount time
  useEffect(() => {
    const mountTime = performance.now()

    return () => {
      const unmountTime = performance.now()
      const duration = Math.round(unmountTime - mountTime)
      analytics.timing(componentName, 'lifetime', duration, 'component_unmount')
    }
  }, [componentName])

  return { startTiming, endTiming }
}

// ============================================================================
// Auth Tracking Hook
// ============================================================================

/**
 * Hook for tracking authentication events
 *
 * @example
 * ```tsx
 * function LoginForm() {
 *   const { trackLogin, trackLogout } = useAuthTracking()
 *
 *   const handleLogin = async (credentials) => {
 *     const user = await login(credentials)
 *     trackLogin(user.id, { tier: user.tier })
 *   }
 * }
 * ```
 */
export function useAuthTracking() {
  const trackSignup = useCallback(
    (userId: string, traits?: { tier?: 'free' | 'premium' | 'pro'; source?: string }) => {
      analytics.identify(userId, traits)
      analytics.track(AnalyticsEvents.USER_SIGNED_UP, {
        signup_source: traits?.source,
      })
    },
    [],
  )

  const trackLogin = useCallback(
    (
      userId: string,
      traits?: {
        tier?: 'free' | 'premium' | 'pro'
        email_verified?: boolean
        oauth_provider?: string
      },
    ) => {
      analytics.identify(userId, traits)
      analytics.track(AnalyticsEvents.USER_LOGGED_IN, {
        login_method: traits?.oauth_provider || 'email',
      })
    },
    [],
  )

  const trackLogout = useCallback(() => {
    analytics.track(AnalyticsEvents.USER_LOGGED_OUT)
    analytics.reset()
  }, [])

  const trackOAuthInitiated = useCallback((provider: string) => {
    analytics.track(AnalyticsEvents.OAUTH_LOGIN_INITIATED, {
      oauth_provider: provider,
    })
  }, [])

  const trackOAuthCompleted = useCallback((provider: string, success: boolean) => {
    analytics.track(AnalyticsEvents.OAUTH_LOGIN_COMPLETED, {
      oauth_provider: provider,
      success,
    })
  }, [])

  const trackEmailVerified = useCallback(() => {
    analytics.track(AnalyticsEvents.USER_VERIFIED_EMAIL)
    analytics.setUserProperties({ email_verified: true })
  }, [])

  const trackPasswordResetRequested = useCallback(() => {
    analytics.track(AnalyticsEvents.PASSWORD_RESET_REQUESTED)
  }, [])

  return {
    trackSignup,
    trackLogin,
    trackLogout,
    trackOAuthInitiated,
    trackOAuthCompleted,
    trackEmailVerified,
    trackPasswordResetRequested,
  }
}

// ============================================================================
// Consent Hook
// ============================================================================

/**
 * Hook for managing analytics consent
 *
 * @example
 * ```tsx
 * function CookieBanner() {
 *   const { hasConsent, acceptAnalytics, declineAnalytics } = useAnalyticsConsent()
 *
 *   if (hasConsent !== null) return null // Already consented
 *
 *   return (
 *     <Banner>
 *       <Button onClick={acceptAnalytics}>Accept</Button>
 *       <Button onClick={declineAnalytics}>Decline</Button>
 *     </Banner>
 *   )
 * }
 * ```
 */
export function useAnalyticsConsent() {
  const hasConsent = analytics.hasConsent()

  const acceptAnalytics = useCallback(() => {
    analytics.optIn()
  }, [])

  const declineAnalytics = useCallback(() => {
    analytics.optOut()
  }, [])

  return {
    hasConsent,
    acceptAnalytics,
    declineAnalytics,
  }
}
