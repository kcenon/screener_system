/**
 * useStockComparison Hook
 * Manages stock comparison state with URL synchronization
 */

import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { MAX_COMPARISON_STOCKS } from '../types/comparison'

export function useStockComparison() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [stockCodes, setStockCodes] = useState<string[]>([])

  // Initialize from URL params
  useEffect(() => {
    const codesParam = searchParams.get('stocks')
    if (codesParam) {
      const codes = codesParam
        .split(',')
        .filter(code => code.trim())
        .slice(0, MAX_COMPARISON_STOCKS)
      setStockCodes(codes)
    }
  }, [])

  // Update URL when stock codes change
  useEffect(() => {
    if (stockCodes.length > 0) {
      setSearchParams({ stocks: stockCodes.join(',') })
    } else {
      setSearchParams({})
    }
  }, [stockCodes, setSearchParams])

  // Add stock
  const addStock = useCallback(
    (code: string) => {
      if (
        stockCodes.length < MAX_COMPARISON_STOCKS &&
        !stockCodes.includes(code)
      ) {
        setStockCodes(prev => [...prev, code])
      }
    },
    [stockCodes],
  )

  // Remove stock
  const removeStock = useCallback((code: string) => {
    setStockCodes(prev => prev.filter(c => c !== code))
  }, [])

  // Clear all stocks
  const clearAll = useCallback(() => {
    setStockCodes([])
  }, [])

  // Reorder stocks (for drag-and-drop in future)
  const reorderStocks = useCallback((newOrder: string[]) => {
    setStockCodes(newOrder)
  }, [])

  return {
    stockCodes,
    addStock,
    removeStock,
    clearAll,
    reorderStocks,
    isMaxReached: stockCodes.length >= MAX_COMPARISON_STOCKS,
    canAddMore: stockCodes.length < MAX_COMPARISON_STOCKS,
  }
}
