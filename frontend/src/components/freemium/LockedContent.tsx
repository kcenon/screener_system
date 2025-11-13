/**
 * Locked content overlay component.
 *
 * Displays a blurred content area with an upgrade prompt overlay.
 * Used to tease premium features while encouraging user registration.
 *
 * @module components/freemium/LockedContent
 * @category Components
 */

import { Link } from 'react-router-dom'

export interface LockedContentProps {
  /** Name of the locked feature */
  feature: string
  /** Optional description of what the feature provides */
  description?: string
  /** Height of the locked content area */
  height?: string | number
}

/**
 * Locked content component with upgrade prompt.
 *
 * Shows a blurred placeholder with an attractive overlay prompting users
 * to sign up to access the feature.
 *
 * ## Features
 *
 * - **Blurred Content**: Visual preview of locked content
 * - **Clear CTA**: Prominent sign-up and login buttons
 * - **Responsive**: Works on mobile and desktop
 * - **Accessible**: Proper ARIA labels and keyboard navigation
 *
 * @example
 * ```tsx
 * // Financial statements tab
 * {canViewFinancials ? (
 *   <FinancialsTab />
 * ) : (
 *   <LockedContent
 *     feature="Financial Statements"
 *     description="View detailed income statements, balance sheets, and cash flow data"
 *   />
 * )}
 * ```
 *
 * @example
 * ```tsx
 * // Technical indicators
 * {canViewAllTechnicals ? (
 *   <TechnicalIndicators indicators={allIndicators} />
 * ) : (
 *   <LockedContent
 *     feature="Advanced Technical Indicators"
 *     height="400px"
 *   />
 * )}
 * ```
 *
 * @category Components
 */
export default function LockedContent({
  feature,
  description,
  height = 'auto',
}: LockedContentProps) {
  return (
    <div className="relative" style={{ minHeight: typeof height === 'number' ? `${height}px` : height }}>
      {/* Blurred content placeholder */}
      <div className="filter blur-md pointer-events-none select-none" aria-hidden="true">
        <div
          className="bg-gradient-to-b from-gray-100 to-gray-200 rounded-lg"
          style={{ height: typeof height === 'number' ? `${height}px` : height || '320px' }}
        >
          {/* Simulated content bars */}
          <div className="p-6 space-y-4">
            <div className="h-8 bg-gray-300/50 rounded w-3/4"></div>
            <div className="h-4 bg-gray-300/50 rounded w-full"></div>
            <div className="h-4 bg-gray-300/50 rounded w-5/6"></div>
            <div className="h-4 bg-gray-300/50 rounded w-full"></div>
            <div className="h-4 bg-gray-300/50 rounded w-4/5"></div>
          </div>
        </div>
      </div>

      {/* Overlay with upgrade prompt */}
      <div className="absolute inset-0 flex items-center justify-center bg-black/10 backdrop-blur-sm rounded-lg">
        <div className="text-center bg-white rounded-lg shadow-2xl p-6 md:p-8 max-w-md mx-4">
          {/* Lock icon */}
          <div className="text-5xl mb-4" role="img" aria-label="Locked">
            🔒
          </div>

          {/* Feature name */}
          <h3 className="text-xl md:text-2xl font-bold text-gray-900 mb-2">
            {feature}
          </h3>

          {/* Description */}
          <p className="text-gray-600 mb-6">
            {description || `Sign up for free to unlock ${feature.toLowerCase()} and access full stock analysis`}
          </p>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              to="/register"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-md"
            >
              Sign Up Free
            </Link>
            <Link
              to="/login"
              className="inline-block bg-gray-200 text-gray-800 px-6 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
            >
              Login
            </Link>
          </div>

          {/* Benefit list */}
          <div className="mt-6 text-left text-sm text-gray-600">
            <p className="font-semibold mb-2">Free account benefits:</p>
            <ul className="space-y-1">
              <li>✅ Unlimited stock searches</li>
              <li>✅ Full financial data access</li>
              <li>✅ Save custom filters</li>
              <li>✅ Create watchlists</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
