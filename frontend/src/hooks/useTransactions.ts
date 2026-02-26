/**
 * Portfolio Transactions Hook.
 *
 * Manages portfolio transaction history with CRUD operations.
 * Provides automatic caching and mutation handling for buy/sell transactions.
 *
 * @module hooks/useTransactions
 * @category Hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { portfolioService } from '../services/portfolioService'
import type { TransactionCreate } from '../services/portfolioService'
import { portfolioDetailQueryKey } from './usePortfolioDetail'

/**
 * Hook for managing portfolio transactions.
 *
 * Provides:
 * - Transaction history with pagination
 * - Add transaction (buy/sell)
 * - Delete transaction
 * - Automatic cache invalidation
 * - Error handling
 *
 * ## Query Caching
 *
 * - Stale Time: 1 minute (data considered fresh)
 * - Cache Time: 5 minutes (unused data kept in cache)
 *
 * ## Side Effects
 *
 * Adding or deleting transactions automatically:
 * - Invalidates transaction list
 * - Invalidates portfolio details
 * - Invalidates performance metrics
 * - Refreshes holdings
 *
 * @example
 * Basic usage:
 * ```typescript
 * const {
 *   transactions,
 *   addTransaction,
 *   deleteTransaction,
 *   isLoading
 * } = useTransactions(portfolioId);
 *
 * // Add buy transaction
 * await addTransaction.mutateAsync({
 *   stock_symbol: "005930",
 *   transaction_type: TransactionType.BUY,
 *   shares: 10,
 *   price: 70000,
 *   commission: 500,
 *   transaction_date: new Date().toISOString(),
 * });
 * ```
 *
 * @example
 * With error handling:
 * ```typescript
 * const { addTransaction } = useTransactions(portfolioId);
 *
 * try {
 *   await addTransaction.mutateAsync(data);
 *   toast.success('Transaction added');
 * } catch (error) {
 *   toast.error('Failed to add transaction');
 * }
 * ```
 *
 * @param portfolioId - Portfolio ID to fetch transactions for (undefined to skip query)
 * @param skip - Number of items to skip for pagination (default: 0)
 * @param limit - Maximum number of items to return (default: 50)
 * @returns Transaction history and mutation operations
 */
export function useTransactions(
  portfolioId: number | undefined,
  skip: number = 0,
  limit: number = 50,
) {
  const queryClient = useQueryClient()

  // Fetch transaction history
  const query = useQuery({
    queryKey: ['portfolio', portfolioId, 'transactions', skip, limit],
    queryFn: async () => {
      const response = await portfolioService.getTransactions(
        portfolioId!,
        skip,
        limit,
      )
      return response.data
    },
    enabled: !!portfolioId,
    staleTime: 1 * 60 * 1000, // 1 minute
    gcTime: 5 * 60 * 1000, // 5 minutes
  })

  // Add transaction mutation
  const addTransaction = useMutation({
    mutationFn: async (data: TransactionCreate) => {
      const response = await portfolioService.addTransaction(portfolioId!, data)
      return response.data
    },
    onSuccess: () => {
      // Invalidate all related queries
      queryClient.invalidateQueries({
        queryKey: ['portfolio', portfolioId, 'transactions'],
      })
      queryClient.invalidateQueries({
        queryKey: portfolioDetailQueryKey(portfolioId!),
      })
      queryClient.invalidateQueries({
        queryKey: ['portfolio', portfolioId, 'holdings'],
      })
      queryClient.invalidateQueries({
        queryKey: ['portfolio', portfolioId, 'performance'],
      })
      queryClient.invalidateQueries({
        queryKey: ['portfolio', portfolioId, 'allocation'],
      })
    },
  })

  // Delete transaction mutation
  const deleteTransaction = useMutation({
    mutationFn: async (transactionId: number) => {
      await portfolioService.deleteTransaction(portfolioId!, transactionId)
      return transactionId
    },
    onSuccess: () => {
      // Invalidate all related queries
      queryClient.invalidateQueries({
        queryKey: ['portfolio', portfolioId, 'transactions'],
      })
      queryClient.invalidateQueries({
        queryKey: portfolioDetailQueryKey(portfolioId!),
      })
      queryClient.invalidateQueries({
        queryKey: ['portfolio', portfolioId, 'holdings'],
      })
      queryClient.invalidateQueries({
        queryKey: ['portfolio', portfolioId, 'performance'],
      })
      queryClient.invalidateQueries({
        queryKey: ['portfolio', portfolioId, 'allocation'],
      })
    },
  })

  return {
    // Query data
    transactions: query.data?.items || [],
    total: query.data?.total || 0,

    // Pagination info
    skip: query.data?.skip || 0,
    limit: query.data?.limit || 50,

    // Query state
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,

    // Mutations
    addTransaction,
    deleteTransaction,

    // Refetch function
    refetch: query.refetch,
  }
}

export default useTransactions
