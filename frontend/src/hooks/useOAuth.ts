/**
 * Custom hooks for OAuth operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { oauthService } from '@/services/oauthService'
import type { OAuthProvider, SocialAccount } from '@/types'

/**
 * Hook for initiating OAuth login
 */
export function useOAuthLogin() {
  return useMutation({
    mutationFn: (provider: OAuthProvider) => oauthService.initiateLogin(provider),
  })
}

/**
 * Hook for handling OAuth callback
 */
export function useOAuthCallback() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      provider,
      code,
      state,
    }: {
      provider: OAuthProvider
      code: string
      state: string
    }) => oauthService.handleCallback(provider, code, state),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user'] })
      navigate('/dashboard', { replace: true })
    },
  })
}

/**
 * Hook for linking social account
 */
export function useLinkAccount() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (provider: OAuthProvider) => oauthService.initiateLink(provider),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['linkedAccounts'] })
    },
  })
}

/**
 * Hook for unlinking social account
 */
export function useUnlinkAccount() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (provider: OAuthProvider) => oauthService.unlinkAccount(provider),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['linkedAccounts'] })
    },
  })
}

/**
 * Hook for fetching linked social accounts
 */
export function useLinkedAccounts() {
  return useQuery({
    queryKey: ['linkedAccounts'],
    queryFn: () => oauthService.getLinkedAccounts(),
    select: (data) => data.accounts,
  })
}

/**
 * Hook for fetching available OAuth providers
 */
export function useAvailableProviders() {
  return useQuery({
    queryKey: ['oauthProviders'],
    queryFn: () => oauthService.getAvailableProviders(),
    select: (data) => data.providers,
  })
}

/**
 * Check if a provider is linked
 */
export function useIsProviderLinked(provider: OAuthProvider) {
  const { data: accounts = [] } = useLinkedAccounts()
  return accounts.some((account: SocialAccount) => account.provider === provider)
}
