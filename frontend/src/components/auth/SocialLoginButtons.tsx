/**
 * Social login buttons component for OAuth providers
 */

import { useState } from 'react'
import { oauthService } from '@/services/oauthService'
import type { OAuthProvider } from '@/types'

interface SocialLoginButtonsProps {
  mode?: 'login' | 'link'
  onError?: (error: Error) => void
  className?: string
}

interface ProviderConfig {
  name: string
  icon: React.ReactNode
  bgColor: string
  hoverBgColor: string
  textColor: string
}

const PROVIDER_CONFIGS: Record<OAuthProvider, ProviderConfig> = {
  google: {
    name: 'Google',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24">
        <path
          fill="currentColor"
          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        />
        <path
          fill="currentColor"
          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        />
        <path
          fill="currentColor"
          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        />
        <path
          fill="currentColor"
          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        />
      </svg>
    ),
    bgColor: 'bg-white',
    hoverBgColor: 'hover:bg-gray-50',
    textColor: 'text-gray-700',
  },
  kakao: {
    name: 'Kakao',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24">
        <path
          fill="currentColor"
          d="M12 3c5.799 0 10.5 3.664 10.5 8.185 0 4.52-4.701 8.184-10.5 8.184a13.5 13.5 0 01-1.727-.11l-4.408 2.883c-.501.265-.678.236-.472-.413l.892-3.678c-2.88-1.46-4.785-3.99-4.785-6.866C1.5 6.665 6.201 3 12 3zm5.907 8.06l1.47-1.424a.472.472 0 00-.656-.678l-1.928 1.866V9.282a.472.472 0 00-.944 0v2.557a.471.471 0 000 .222v2.218a.472.472 0 00.944 0v-1.58l.787-.79 1.39 2.194a.472.472 0 10.796-.505l-1.86-2.539zm-8.639-1.93c-.134 0-.248.087-.288.207-.164.495-1.05 3.283-1.156 3.602a.37.37 0 00.703.236l.249-.776h1.535l.247.774a.37.37 0 00.703-.236c-.105-.316-.988-3.097-1.152-3.6a.312.312 0 00-.29-.208h-.551zm-.023 1.267l.476 1.46h-.95l.474-1.46zm4.006 1.858v-2.91a.296.296 0 00-.593 0v3.316c0 .163.133.296.296.296h1.47a.296.296 0 000-.592h-1.173v-.11zm-2.72-2.91a.296.296 0 00-.296.296v3.316a.296.296 0 00.593 0v-3.316a.296.296 0 00-.297-.296z"
        />
      </svg>
    ),
    bgColor: 'bg-[#FEE500]',
    hoverBgColor: 'hover:bg-[#FADA0A]',
    textColor: 'text-[#191919]',
  },
  naver: {
    name: 'Naver',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24">
        <path
          fill="currentColor"
          d="M16.273 12.845L7.376 0H0v24h7.726V11.156L16.624 24H24V0h-7.727v12.845z"
        />
      </svg>
    ),
    bgColor: 'bg-[#03C75A]',
    hoverBgColor: 'hover:bg-[#02B351]',
    textColor: 'text-white',
  },
}

export default function SocialLoginButtons({
  mode = 'login',
  onError,
  className = '',
}: SocialLoginButtonsProps) {
  const [loadingProvider, setLoadingProvider] = useState<OAuthProvider | null>(null)

  const handleClick = async (provider: OAuthProvider) => {
    try {
      setLoadingProvider(provider)
      if (mode === 'login') {
        await oauthService.initiateLogin(provider)
      } else {
        await oauthService.initiateLink(provider)
      }
    } catch (error) {
      setLoadingProvider(null)
      onError?.(error as Error)
    }
  }

  const providers: OAuthProvider[] = ['google', 'kakao', 'naver']

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-300" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-gray-50 text-gray-500">
            {mode === 'login' ? 'Or continue with' : 'Link your account'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {providers.map((provider) => {
          const config = PROVIDER_CONFIGS[provider]
          const isLoading = loadingProvider === provider

          return (
            <button
              key={provider}
              type="button"
              onClick={() => handleClick(provider)}
              disabled={loadingProvider !== null}
              className={`
                flex items-center justify-center py-2.5 px-4
                border border-gray-300 rounded-md shadow-sm
                ${config.bgColor} ${config.hoverBgColor} ${config.textColor}
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-colors duration-200
              `}
              aria-label={`Sign in with ${config.name}`}
            >
              {isLoading ? (
                <svg
                  className="animate-spin h-5 w-5"
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
              ) : (
                config.icon
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
