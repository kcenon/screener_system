/**
 * WatchlistStockTable Component
 * Displays stocks in a watchlist with sorting and filtering
 */

import { useState, useMemo } from 'react'
import { TrendingUp, TrendingDown, Minus, Trash2, ArrowUpDown, ExternalLink } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { WatchlistStock, WatchlistSortField, SortDirection } from '@/types/watchlist'

interface WatchlistStockTableProps {
  stocks: WatchlistStock[]
  onRemoveStock: (stockCode: string) => void
  isLoading?: boolean
}

export function WatchlistStockTable({
  stocks,
  onRemoveStock,
  isLoading = false,
}: WatchlistStockTableProps) {
  const [sortField, setSortField] = useState<WatchlistSortField>('change_percent')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [searchQuery, setSearchQuery] = useState('')

  // Handle sort
  const handleSort = (field: WatchlistSortField) => {
    if (sortField === field) {
      // Toggle direction if same field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      // Default to descending for new field
      setSortField(field)
      setSortDirection('desc')
    }
  }

  // Filtered and sorted stocks
  const processedStocks = useMemo(() => {
    let result = [...stocks]

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      result = result.filter(
        (stock) =>
          stock.code.toLowerCase().includes(query) ||
          stock.name.toLowerCase().includes(query)
      )
    }

    // Sort
    result.sort((a, b) => {
      let aVal: number | string
      let bVal: number | string

      switch (sortField) {
        case 'name':
        case 'code':
          aVal = a[sortField]
          bVal = b[sortField]
          break
        case 'price':
          aVal = a.current_price
          bVal = b.current_price
          break
        case 'change_percent':
          aVal = a.change_percent
          bVal = b.change_percent
          break
        case 'volume':
          aVal = a.volume
          bVal = b.volume
          break
        case 'market_cap':
          aVal = a.market_cap || 0
          bVal = b.market_cap || 0
          break
        case 'added_at':
          aVal = new Date(a.added_at).getTime()
          bVal = new Date(b.added_at).getTime()
          break
        default:
          return 0
      }

      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDirection === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal)
      }

      return sortDirection === 'asc'
        ? (aVal as number) - (bVal as number)
        : (bVal as number) - (aVal as number)
    })

    return result
  }, [stocks, sortField, sortDirection, searchQuery])

  // Format number to Korean Won
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0,
    }).format(price)
  }

  // Format volume
  const formatVolume = (volume: number) => {
    if (volume >= 1_000_000) {
      return `${(volume / 1_000_000).toFixed(1)}M`
    }
    if (volume >= 1_000) {
      return `${(volume / 1_000).toFixed(1)}K`
    }
    return volume.toString()
  }

  // Format market cap
  const formatMarketCap = (marketCap?: number) => {
    if (!marketCap) return 'N/A'
    if (marketCap >= 1_000_000_000_000) {
      return `₩${(marketCap / 1_000_000_000_000).toFixed(1)}T`
    }
    if (marketCap >= 1_000_000_000) {
      return `₩${(marketCap / 1_000_000_000).toFixed(1)}B`
    }
    return `₩${(marketCap / 1_000_000).toFixed(1)}M`
  }

  const SortButton = ({ field, children }: { field: WatchlistSortField; children: React.ReactNode }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center gap-1 hover:text-gray-900 transition-colors"
    >
      {children}
      <ArrowUpDown
        className={`w-3 h-3 ${
          sortField === field ? 'text-blue-600' : 'text-gray-400'
        }`}
      />
    </button>
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (stocks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <TrendingUp className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No stocks in this watchlist
        </h3>
        <p className="text-gray-500">
          Add stocks from the screener or stock detail pages
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Search Bar */}
      <div className="p-4 border-b border-gray-200">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by code or name..."
          className="
            w-full px-4 py-2 rounded-lg
            border border-gray-300
            focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none
          "
        />
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full">
          <thead className="bg-gray-50 sticky top-0">
            <tr className="text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
              <th className="px-4 py-3">
                <SortButton field="code">Code</SortButton>
              </th>
              <th className="px-4 py-3">
                <SortButton field="name">Name</SortButton>
              </th>
              <th className="px-4 py-3 text-right">
                <SortButton field="price">Price</SortButton>
              </th>
              <th className="px-4 py-3 text-right">
                <SortButton field="change_percent">Change</SortButton>
              </th>
              <th className="px-4 py-3 text-right">
                <SortButton field="volume">Volume</SortButton>
              </th>
              <th className="px-4 py-3 text-right">
                <SortButton field="market_cap">Market Cap</SortButton>
              </th>
              <th className="px-4 py-3 text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {processedStocks.map((stock) => {
              const changeColor =
                stock.change_percent > 0
                  ? 'text-red-600'
                  : stock.change_percent < 0
                    ? 'text-blue-600'
                    : 'text-gray-600'

              const ChangeIcon =
                stock.change_percent > 0
                  ? TrendingUp
                  : stock.change_percent < 0
                    ? TrendingDown
                    : Minus

              return (
                <tr
                  key={stock.code}
                  className="hover:bg-gray-50 transition-colors"
                >
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {stock.code}
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      to={`/stocks/${stock.code}`}
                      className="text-sm text-gray-900 hover:text-blue-600 flex items-center gap-1"
                    >
                      {stock.name}
                      <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100" />
                    </Link>
                    <div className="text-xs text-gray-500">{stock.market}</div>
                  </td>
                  <td className="px-4 py-3 text-sm text-right font-medium">
                    {formatPrice(stock.current_price)}
                  </td>
                  <td className={`px-4 py-3 text-sm text-right font-medium ${changeColor}`}>
                    <div className="flex items-center justify-end gap-1">
                      <ChangeIcon className="w-4 h-4" />
                      {stock.change_percent > 0 ? '+' : ''}
                      {stock.change_percent.toFixed(2)}%
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-right text-gray-600">
                    {formatVolume(stock.volume)}
                  </td>
                  <td className="px-4 py-3 text-sm text-right text-gray-600">
                    {formatMarketCap(stock.market_cap)}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => {
                        if (window.confirm(`Remove ${stock.name} from watchlist?`)) {
                          onRemoveStock(stock.code)
                        }
                      }}
                      className="
                        p-1.5 rounded
                        text-gray-400 hover:text-red-600 hover:bg-red-50
                        transition-colors
                      "
                      title="Remove from watchlist"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Footer with Stats */}
      <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">
            {processedStocks.length} stock{processedStocks.length !== 1 ? 's' : ''}
            {searchQuery && ` (filtered from ${stocks.length})`}
          </span>
          <div className="flex items-center gap-4 text-xs">
            <span className="flex items-center gap-1 text-red-600">
              <TrendingUp className="w-3 h-3" />
              {stocks.filter((s) => s.change_percent > 0).length} up
            </span>
            <span className="flex items-center gap-1 text-blue-600">
              <TrendingDown className="w-3 h-3" />
              {stocks.filter((s) => s.change_percent < 0).length} down
            </span>
            <span className="flex items-center gap-1 text-gray-600">
              <Minus className="w-3 h-3" />
              {stocks.filter((s) => s.change_percent === 0).length} unchanged
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
