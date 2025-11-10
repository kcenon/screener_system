import { useState } from 'react'
import * as Tabs from '@radix-ui/react-tabs'
import type { StockDetail } from '@/types'
import OverviewTab from './OverviewTab'
import FinancialsTab from './FinancialsTab'
import ValuationTab from './ValuationTab'
import TechnicalTab from './TechnicalTab'

interface StockTabsProps {
  stock: StockDetail
}

type TabValue = 'overview' | 'financials' | 'valuation' | 'technical'

/**
 * Stock Tabs Component
 *
 * Tab-based navigation for stock detail content:
 * - Overview: Key metrics, scores, company info
 * - Financials: Income statement, balance sheet, cash flow
 * - Valuation: Valuation ratios and historical trends
 * - Technical: Price momentum, volume analysis, moving averages
 *
 * @example
 * ```tsx
 * <StockTabs stock={stockData} />
 * ```
 */
export default function StockTabs({ stock }: StockTabsProps) {
  const [activeTab, setActiveTab] = useState<TabValue>('overview')

  const tabs: Array<{ value: TabValue; label: string }> = [
    { value: 'overview', label: '개요' },
    { value: 'financials', label: '재무' },
    { value: 'valuation', label: '밸류에이션' },
    { value: 'technical', label: '기술적 지표' },
  ]

  return (
    <Tabs.Root
      value={activeTab}
      onValueChange={(value) => setActiveTab(value as TabValue)}
      className="w-full"
    >
      {/* Tab List */}
      <Tabs.List className="flex border-b border-gray-200 mb-6">
        {tabs.map((tab) => (
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
        <FinancialsTab stock={stock} />
      </Tabs.Content>

      <Tabs.Content value="valuation" className="outline-none">
        <ValuationTab stock={stock} />
      </Tabs.Content>

      <Tabs.Content value="technical" className="outline-none">
        <TechnicalTab stock={stock} />
      </Tabs.Content>
    </Tabs.Root>
  )
}
