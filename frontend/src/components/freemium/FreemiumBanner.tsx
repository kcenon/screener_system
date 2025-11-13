/**
 * Freemium upgrade banner component.
 *
 * Displays an attractive banner encouraging users to sign up for full access.
 * Shown to unauthenticated users on pages with limited features.
 *
 * @module components/freemium/FreemiumBanner
 * @category Components
 */

import { Link } from 'react-router-dom'

export interface FreemiumBannerProps {
  /** Type of page showing the banner */
  type?: 'screener' | 'stock-detail' | 'comparison' | 'general'
  /** Custom message to display */
  message?: string
  /** Show close button */
  dismissible?: boolean
  /** Callback when banner is dismissed */
  onDismiss?: () => void
}

/**
 * Freemium banner component for encouraging user registration.
 *
 * Displays a prominent banner with call-to-action buttons to encourage
 * unauthenticated users to sign up for full access.
 *
 * @example
 * ```tsx
 * // Screener page with usage count
 * <FreemiumBanner
 *   type="screener"
 *   message={`Sign up for unlimited searches! (${screeningsToday}/${dailyScreeningLimit} today)`}
 * />
 * ```
 *
 * @example
 * ```tsx
 * // Stock detail page
 * <FreemiumBanner
 *   type="stock-detail"
 *   message="Sign up to view full financial data and add to watchlist"
 * />
 * ```
 *
 * @category Components
 */
export default function FreemiumBanner({
  type = 'general',
  message,
  dismissible = false,
  onDismiss,
}: FreemiumBannerProps) {
  // Default messages by type
  const defaultMessages = {
    screener: 'Sign up for unlimited stock screening and save your custom filters!',
    'stock-detail': 'Sign up to view full financial data, technical indicators, and add to watchlist',
    comparison: 'Sign up to compare more stocks and save your comparisons',
    general: 'Sign up for free to unlock all features!',
  }

  const displayMessage = message || defaultMessages[type]

  return (
    <div className="relative bg-gradient-to-r from-blue-500 via-blue-600 to-purple-600 text-white p-4 rounded-lg mb-6 shadow-lg">
      {/* Close button */}
      {dismissible && onDismiss && (
        <button
          onClick={onDismiss}
          className="absolute top-2 right-2 text-white/80 hover:text-white transition-colors"
          aria-label="Dismiss banner"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      )}

      <div className="flex items-center justify-between gap-4 flex-wrap">
        {/* Icon and message */}
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <span className="text-3xl flex-shrink-0" role="img" aria-label="Gift">
            🎁
          </span>
          <p className="font-medium text-sm md:text-base">{displayMessage}</p>
        </div>

        {/* CTA buttons */}
        <div className="flex gap-2 flex-shrink-0">
          <Link
            to="/register"
            className="bg-white text-blue-600 px-4 md:px-6 py-2 rounded-full font-semibold text-sm md:text-base hover:bg-gray-100 transition-colors shadow-md"
          >
            Sign Up Free
          </Link>
          <Link
            to="/login"
            className="border-2 border-white text-white px-4 md:px-6 py-2 rounded-full font-semibold text-sm md:text-base hover:bg-white/10 transition-colors"
          >
            Login
          </Link>
        </div>
      </div>
    </div>
  )
}
