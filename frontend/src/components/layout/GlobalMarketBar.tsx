/**
 * Global Market Status Bar
 *
 * Persistent market overview displayed at the top of every page.
 * Shows key indices (KOSPI, KOSDAQ), market sentiment, and current time.
 *
 * Features:
 * - Auto-refresh every 30 seconds
 * - Sticky positioning (always visible)
 * - Color-coded performance indicators
 * - Responsive layout (stacks on mobile)
 */

import { useEffect, useState } from 'react'
import { useMarketIndices } from '../../hooks/useMarketIndices'
import { useMarketBreadth } from '../../hooks/useMarketBreadth'
import { getMarketColor, getChangeArrow, getMarketSentiment } from '../../config/theme'
import { formatChangePercentage } from '../../utils/formatNumber'
import type { MarketIndex } from '../../types/market'

/**
 * GlobalMarketBar Component
 *
 * Displays real-time market overview with auto-refresh
 */
export function GlobalMarketBar() {
  // Fetch market indices (30 second refresh)
  const { data: indicesData, isLoading: isLoadingIndices } = useMarketIndices({
    refetchInterval: 30000, // 30 seconds
  })

  // Fetch market breadth for sentiment (60 second refresh)
  const { data: breadthData } = useMarketBreadth({
    market: 'ALL',
    refetchInterval: 60000, // 60 seconds
  })

  // Current time (KST)
  const [currentTime, setCurrentTime] = useState(new Date())

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  // Format time as HH:MM:SS KST
  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    })
  }

  // Get market sentiment display
  const getSentimentDisplay = () => {
    if (!breadthData) return { text: '로딩중', icon: '⏳', color: 'text-gray-600' }

    const sentiment = breadthData.sentiment
    const colors = getMarketSentiment(sentiment)

    const sentimentMap = {
      bullish: { text: '강세', icon: colors.icon },
      neutral: { text: '중립', icon: colors.icon },
      bearish: { text: '약세', icon: colors.icon },
    }

    return {
      ...sentimentMap[sentiment],
      color: colors.text,
    }
  }

  // Render individual index
  const renderIndex = (index: MarketIndex) => {
    const color = getMarketColor(index.change_percent)
    const arrow = getChangeArrow(index.change_percent)

    return (
      <div key={index.code} className="flex items-center gap-2">
        <span className="font-semibold text-gray-700 dark:text-gray-300">{index.code}</span>
        <span className="font-bold dark:text-white">{index.current.toLocaleString('ko-KR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
        <span className={`${color.text} font-medium flex items-center gap-1`}>
          <span>{arrow}</span>
          <span>{formatChangePercentage(index.change_percent)}</span>
        </span>
      </div>
    )
  }

  const sentiment = getSentimentDisplay()

  // Loading state
  if (isLoadingIndices) {
    return (
      <div className="sticky top-0 z-50 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm transition-colors">
        <div className="container mx-auto px-4 py-2">
          <div className="flex items-center justify-center text-sm text-gray-500 dark:text-gray-400">
            시장 데이터 로딩중...
          </div>
        </div>
      </div>
    )
  }

  // No data state
  if (!indicesData || !indicesData.indices || indicesData.indices.length === 0) {
    return (
      <div className="sticky top-0 z-50 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm transition-colors">
        <div className="container mx-auto px-4 py-2">
          <div className="flex items-center justify-center text-sm text-gray-500 dark:text-gray-400">
            시장 데이터 없음
          </div>
        </div>
      </div>
    )
  }

  const kospi = indicesData.indices.find((idx) => idx.code === 'KOSPI')
  const kosdaq = indicesData.indices.find((idx) => idx.code === 'KOSDAQ')

  return (
    <div className="sticky top-0 z-50 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm transition-colors">
      <div className="container mx-auto px-4 py-2">
        {/* Desktop Layout: Horizontal */}
        <div className="hidden md:flex items-center justify-between text-sm">
          {/* Left: Indices */}
          <div className="flex items-center gap-6">
            {kospi && renderIndex(kospi)}
            {kosdaq && renderIndex(kosdaq)}
          </div>

          {/* Right: Sentiment & Time */}
          <div className="flex items-center gap-6">
            {/* Market Sentiment */}
            <div className="flex items-center gap-2">
              <span className="text-gray-600 dark:text-gray-400">시장심리:</span>
              <span className={`${sentiment.color} font-medium flex items-center gap-1`}>
                <span>{sentiment.icon}</span>
                <span>{sentiment.text}</span>
              </span>
            </div>

            {/* Current Time (KST) */}
            <div className="flex items-center gap-1 text-gray-600 dark:text-gray-400">
              <span>{formatTime(currentTime)}</span>
              <span className="text-xs">KST</span>
            </div>
          </div>
        </div>

        {/* Mobile Layout: Stacked */}
        <div className="md:hidden space-y-2 text-xs">
          {/* Row 1: Indices */}
          <div className="flex items-center justify-between">
            {kospi && renderIndex(kospi)}
            {kosdaq && renderIndex(kosdaq)}
          </div>

          {/* Row 2: Sentiment & Time */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-gray-600 dark:text-gray-400">심리:</span>
              <span className={`${sentiment.color} font-medium flex items-center gap-1`}>
                <span>{sentiment.icon}</span>
                <span>{sentiment.text}</span>
              </span>
            </div>

            <div className="flex items-center gap-1 text-gray-600 dark:text-gray-400">
              <span>{formatTime(currentTime)}</span>
              <span className="text-xs">KST</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GlobalMarketBar
