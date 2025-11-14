import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'

export interface SearchResult {
  code: string
  name: string
  market: 'KOSPI' | 'KOSDAQ'
  current_price?: number
}

export const useGlobalSearch = () => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isOpen, setIsOpen] = useState(false)

  const search = useCallback(async (searchTerm: string) => {
    if (searchTerm.length < 2) {
      setResults([])
      return
    }

    setIsLoading(true)
    try {
      const response = await axios.get('/api/v1/stocks', {
        params: {
          search: searchTerm,
          limit: 10,
        },
      })
      setResults(response.data.items || [])
    } catch (error) {
      console.error('Search error:', error)
      setResults([])
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      search(query)
    }, 300)

    return () => clearTimeout(timeoutId)
  }, [query, search])

  const clearSearch = useCallback(() => {
    setQuery('')
    setResults([])
    setIsOpen(false)
  }, [])

  return {
    query,
    setQuery,
    results,
    isLoading,
    isOpen,
    setIsOpen,
    clearSearch,
  }
}
