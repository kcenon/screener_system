import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { useAuthStore } from '@/store/authStore'
import { authService } from '@/services/authService'

/**
 * Banner prompting unverified users to verify their email address
 *
 * Displays a dismissible banner for logged-in users who haven't verified
 * their email. Includes a link to resend verification email.
 */
export default function EmailVerificationBanner() {
  const user = useAuthStore((state) => state.user)
  const [isDismissed, setIsDismissed] = useState(false)

  const resendMutation = useMutation({
    mutationFn: () => authService.resendVerificationEmail(),
    onSuccess: () => {
      // Show success message or toast
    },
  })

  // Don't show banner if:
  // - User is not logged in
  // - Email is already verified
  // - Banner has been dismissed
  if (!user || user.email_verified || isDismissed) {
    return null
  }

  return (
    <div className="bg-yellow-50 border-b border-yellow-200">
      <div className="max-w-7xl mx-auto py-3 px-3 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between flex-wrap">
          <div className="w-0 flex-1 flex items-center">
            <span className="flex p-2 rounded-lg bg-yellow-100">
              <svg
                className="h-6 w-6 text-yellow-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </span>
            <p className="ml-3 font-medium text-yellow-800 truncate">
              <span className="md:hidden">Please verify your email</span>
              <span className="hidden md:inline">
                Please verify your email address to access all features
              </span>
            </p>
          </div>
          <div className="order-3 mt-2 flex-shrink-0 w-full sm:order-2 sm:mt-0 sm:w-auto">
            <button
              onClick={() => resendMutation.mutate()}
              disabled={resendMutation.isPending}
              className="flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-yellow-600 bg-white hover:bg-yellow-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {resendMutation.isPending ? 'Sending...' : 'Resend Verification Email'}
            </button>
            {resendMutation.isSuccess && (
              <span className="ml-2 text-sm text-yellow-700">Email sent!</span>
            )}
            {resendMutation.isError && (
              <span className="ml-2 text-sm text-red-600">
                {(resendMutation.error as Error)?.message || 'Failed to send'}
              </span>
            )}
          </div>
          <div className="order-2 flex-shrink-0 sm:order-3 sm:ml-3">
            <button
              type="button"
              onClick={() => setIsDismissed(true)}
              className="-mr-1 flex p-2 rounded-md hover:bg-yellow-100 focus:outline-none focus:ring-2 focus:ring-yellow-600 sm:-mr-2"
            >
              <span className="sr-only">Dismiss</span>
              <svg
                className="h-6 w-6 text-yellow-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
