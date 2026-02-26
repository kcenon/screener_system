/**
 * Daily limit reached modal component.
 *
 * Displays a modal when user reaches their daily usage limit,
 * encouraging them to sign up for unlimited access.
 *
 * @module components/freemium/LimitReachedModal
 * @category Components
 */

import { Link } from 'react-router-dom'
import * as Dialog from '@radix-ui/react-dialog'

export interface LimitReachedModalProps {
  /** Whether modal is open */
  open: boolean
  /** Callback when modal should close */
  onClose: () => void
  /** Modal title */
  title?: string
  /** Main message to display */
  message?: string
  /** Number of actions used today */
  actionsUsed?: number
  /** Daily limit */
  dailyLimit?: number
}

/**
 * Limit reached modal component.
 *
 * Shows when user exceeds daily usage limits, with attractive upgrade prompts
 * and clear benefits of signing up.
 *
 * ## Features
 *
 * - **Clear Messaging**: Explains why access is limited
 * - **Benefit Highlights**: Shows what user gets by signing up
 * - **Multiple CTAs**: Sign up, login, or maybe later options
 * - **Accessible**: Proper ARIA labels and keyboard navigation
 *
 * @example
 * ```tsx
 * const [showLimitModal, setShowLimitModal] = useState(false)
 *
 * // Check limit before action
 * const handleSearch = () => {
 *   if (!canPerformScreening(dailyScreeningLimit)) {
 *     setShowLimitModal(true)
 *     return
 *   }
 *   // Perform screening
 * }
 *
 * return (
 *   <>
 *     <SearchButton onClick={handleSearch} />
 *
 *     <LimitReachedModal
 *       open={showLimitModal}
 *       onClose={() => setShowLimitModal(false)}
 *       actionsUsed={screeningsToday}
 *       dailyLimit={dailyScreeningLimit}
 *     />
 *   </>
 * )
 * ```
 *
 * @category Components
 */
export default function LimitReachedModal({
  open,
  onClose,
  title = 'Daily Limit Reached',
  message,
  actionsUsed,
  dailyLimit,
}: LimitReachedModalProps) {
  const defaultMessage =
    actionsUsed !== undefined && dailyLimit !== undefined
      ? `You've used all ${dailyLimit} of your free searches today. Sign up for unlimited access!`
      : "You've reached the daily limit. Sign up for unlimited access!"

  return (
    <Dialog.Root open={open} onOpenChange={onClose}>
      <Dialog.Portal>
        {/* Overlay */}
        <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm animate-fadeIn" />

        {/* Content */}
        <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg shadow-2xl p-6 md:p-8 max-w-md w-full mx-4 animate-scaleIn">
          {/* Header */}
          <div className="text-center mb-6">
            {/* Warning icon */}
            <div
              className="text-5xl md:text-6xl mb-4"
              role="img"
              aria-label="Warning"
            >
              ⚠️
            </div>

            <Dialog.Title className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
              {title}
            </Dialog.Title>

            <Dialog.Description className="text-gray-600 text-base">
              {message || defaultMessage}
            </Dialog.Description>
          </div>

          {/* Benefits section */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h4 className="font-semibold text-blue-900 mb-3">
              Free Account Benefits:
            </h4>
            <ul className="space-y-2 text-blue-800 text-sm">
              <li className="flex items-start gap-2">
                <span className="flex-shrink-0 mt-0.5">✅</span>
                <span>Unlimited stock searches</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="flex-shrink-0 mt-0.5">✅</span>
                <span>Save filter presets</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="flex-shrink-0 mt-0.5">✅</span>
                <span>Export results to CSV</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="flex-shrink-0 mt-0.5">✅</span>
                <span>Create watchlists</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="flex-shrink-0 mt-0.5">✅</span>
                <span>Full financial data access</span>
              </li>
            </ul>
          </div>

          {/* CTA buttons */}
          <div className="flex flex-col gap-3">
            <Link
              to="/register"
              onClick={onClose}
              className="block text-center bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-md"
            >
              Sign Up Free
            </Link>

            <Link
              to="/login"
              onClick={onClose}
              className="block text-center bg-gray-200 text-gray-800 px-6 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
            >
              Login
            </Link>

            <button
              onClick={onClose}
              className="text-gray-600 hover:text-gray-800 py-2 font-medium transition-colors"
            >
              Maybe Later
            </button>
          </div>

          {/* Close button */}
          <Dialog.Close asChild>
            <button
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Close"
            >
              <svg
                className="w-6 h-6"
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
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
