import { useState } from 'react'
import * as Tabs from '@radix-ui/react-tabs'
import type { StockDetail } from '@/types'
import OverviewTab from './OverviewTab'
import FinancialsTab from './FinancialsTab'
import ValuationTab from './ValuationTab'
import TechnicalTab from './TechnicalTab'
import OrderBook from './OrderBook'
import { useOrderBook } from '@/hooks/useOrderBook'
import { LockedContent } from '@/components/freemium'

interface StockTabsProps {
  stock: StockDetail
  /** Whether user can view financial statements (freemium) */
  canViewFinancials?: boolean
  /** Whether user can view all technical indicators (freemium) */
  canViewAllTechnicals?: boolean
}

type TabValue =
  | 'overview'
  | 'financials'
  | 'valuation'
  | 'technical'
  | 'orderbook'

/**
 * Stock Tabs Component
 *
 * Tab-based navigation for stock detail content:
 * - Overview: Key metrics, scores, company info
 * - Financials: Income statement, balance sheet, cash flow
 * - Valuation: Valuation ratios and historical trends
 * - Technical: Price momentum, volume analysis, moving averages
 * - OrderBook: Real-time 10-level order book (FE-005)
 *
 * @example
 * ```tsx
 * <StockTabs stock={stockData} />
 * ```
 */
export default function StockTabs({
  stock,
  canViewFinancials = true,
  canViewAllTechnicals = true,
}: StockTabsProps) {
  const [activeTab, setActiveTab] = useState<TabValue>('overview')

  // OrderBook data (only fetch when orderbook tab is active)
  const {
    orderBook,
    imbalance,
    isLoading: orderBookLoading,
    error: orderBookError,
    frozen,
    toggleFreeze,
  } = useOrderBook(stock.code, activeTab === 'orderbook')

  const tabs: Array<{ value: TabValue; label: string }> = [
    { value: 'overview', label: '개요' },
    { value: 'financials', label: '재무' },
    { value: 'valuation', label: '밸류에이션' },
    { value: 'technical', label: '기술적 지표' },
    { value: 'orderbook', label: '호가' },
  ]

  return (
    <Tabs.Root
      value={activeTab}
      onValueChange={value => setActiveTab(value as TabValue)}
      className="w-full"
    >
      {/* Tab List */}
      <Tabs.List className="flex border-b border-gray-200 mb-6">
        {tabs.map(tab => (
          <Tabs.Trigger
            key={tab.value}
            value={tab.value}
            className={`px-4 py-3 text-sm font-medium transition-colors relative ${
              activeTab === tab.value
                ? 'text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
            {activeTab === tab.value && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600" />
            )}
          </Tabs.Trigger>
        ))}
      </Tabs.List>

      {/* Tab Content */}
      <Tabs.Content value="overview" className="outline-none">
        <OverviewTab stock={stock} />
      </Tabs.Content>

      <Tabs.Content value="financials" className="outline-none">
        {canViewFinancials ? (
          <FinancialsTab stock={stock} />
        ) : (
          <LockedContent
            feature="재무제표"
            description="손익계산서, 재무상태표, 현금흐름표 등 상세 재무 데이터를 확인하세요"
            height={400}
          />
        )}
      </Tabs.Content>

      <Tabs.Content value="valuation" className="outline-none">
        <ValuationTab stock={stock} />
      </Tabs.Content>

      <Tabs.Content value="technical" className="outline-none">
        {canViewAllTechnicals ? (
          <TechnicalTab stock={stock} />
        ) : (
          <LockedContent
            feature="기술적 지표"
            description="이동평균선, RSI, MACD 등 고급 기술적 분석 지표를 확인하세요"
            height={400}
          />
        )}
      </Tabs.Content>

      <Tabs.Content value="orderbook" className="outline-none">
        {orderBookError ? (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <div className="text-red-600 mb-2">
              <svg
                className="w-12 h-12 mx-auto"
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
            </div>
            <p className="text-sm text-gray-600 mb-4">{orderBookError}</p>
            <p className="text-xs text-gray-500">
              실시간 호가 데이터를 사용하려면 로그인이 필요합니다.
            </p>
          </div>
        ) : (
          <OrderBook
            data={orderBook}
            imbalance={imbalance}
            isLoading={orderBookLoading}
            frozen={frozen}
            onToggleFreeze={toggleFreeze}
          />
        )}
      </Tabs.Content>
    </Tabs.Root>
  )
}
