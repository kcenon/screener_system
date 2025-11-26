/**
 * OAuth callback page - handles redirect from OAuth providers
 */

import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { oauthService } from '@/services/oauthService'
import type { OAuthProvider } from '@/types'

type CallbackStatus = 'processing' | 'success' | 'error'

export default function OAuthCallbackPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState<CallbackStatus>('processing')
  const [errorMessage, setErrorMessage] = useState<string>('')

  useEffect(() => {
    const handleCallback = async () => {
      // Check for error from OAuth provider
      const error = searchParams.get('error')
      if (error) {
        setStatus('error')
        setErrorMessage(decodeURIComponent(error))
        return
      }

      // Get callback parameters
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const providerParam = searchParams.get('provider')

      // Also check URL path for provider (e.g., /oauth/callback/google)
      const pathSegments = window.location.pathname.split('/')
      const provider = (providerParam || pathSegments[pathSegments.length - 1]) as OAuthProvider

      if (!code || !state) {
        setStatus('error')
        setErrorMessage('Missing authorization code or state parameter')
        return
      }

      if (!provider || !['google', 'kakao', 'naver'].includes(provider)) {
        setStatus('error')
        setErrorMessage('Invalid or missing OAuth provider')
        return
      }

      try {
        await oauthService.handleCallback(provider, code, state)
        setStatus('success')

        // Redirect to dashboard after successful login
        setTimeout(() => {
          navigate('/dashboard', { replace: true })
        }, 1500)
      } catch (err) {
        setStatus('error')
        setErrorMessage(err instanceof Error ? err.message : 'OAuth authentication failed')
      }
    }

    handleCallback()
  }, [searchParams, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 text-center">
        {status === 'processing' && (
          <>
            <div className="flex justify-center">
              <svg
                className="animate-spin h-12 w-12 text-blue-600"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
            <h2 className="mt-6 text-2xl font-bold text-gray-900">
              Completing sign in...
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Please wait while we verify your credentials
            </p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="flex justify-center">
              <div className="rounded-full bg-green-100 p-3">
                <svg
                  className="h-12 w-12 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
            </div>
            <h2 className="mt-6 text-2xl font-bold text-gray-900">
              Sign in successful!
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Redirecting to dashboard...
            </p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="flex justify-center">
              <div className="rounded-full bg-red-100 p-3">
                <svg
                  className="h-12 w-12 text-red-600"
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
              </div>
            </div>
            <h2 className="mt-6 text-2xl font-bold text-gray-900">
              Sign in failed
            </h2>
            <p className="mt-2 text-sm text-red-600">{errorMessage}</p>
            <div className="mt-6">
              <button
                onClick={() => navigate('/login', { replace: true })}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Return to login
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
