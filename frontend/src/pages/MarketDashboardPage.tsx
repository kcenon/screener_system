/**
 * Unified Market Dashboard Page (IMPROVEMENT-003)
 *
 * Features:
 * - 5 tabs: Overview, Screener, Heat Map, Movers, Sectors
 * - URL synchronization (?tab=screener)
 * - Keyboard shortcuts (Cmd+1-5)
 * - Sticky navigation
 * - Tab state persistence in localStorage
 * - Instant tab switching (no page reload)
 */

import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import * as Tabs from '@radix-ui/react-tabs'
import { OverviewTab } from '@/components/market/tabs/OverviewTab'
import { ScreenerTab } from '@/components/market/tabs/ScreenerTab'
import { HeatMapTab } from '@/components/market/tabs/HeatMapTab'
import { MoversTab } from '@/components/market/tabs/MoversTab'
import { SectorsTab } from '@/components/market/tabs/SectorsTab'
import { ScrollToTopButton } from '@/components/common/ScrollToTopButton'

type TabValue = 'overview' | 'screener' | 'heatmap' | 'movers' | 'sectors'

const TAB_CONFIG = [
  { value: 'overview', label: '개요', kbd: '1' },
  { value: 'screener', label: '스크리너', kbd: '2' },
  { value: 'heatmap', label: '히트맵', kbd: '3' },
  { value: 'movers', label: '상승/하락', kbd: '4' },
  { value: 'sectors', label: '섹터분석', kbd: '5' },
] as const

const LAST_TAB_KEY = 'market_dashboard_last_tab'

export function MarketDashboardPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [showScrollShadow, setShowScrollShadow] = useState(false)
  const [sectorFilter, setSectorFilter] = useState<string | null>(null)

  // Get initial tab from URL or localStorage
  const getInitialTab = (): TabValue => {
    const urlTab = searchParams.get('tab') as TabValue | null
    if (urlTab && TAB_CONFIG.find(t => t.value === urlTab)) {
      return urlTab
    }
    const lastTab = localStorage.getItem(LAST_TAB_KEY) as TabValue | null
    if (lastTab && TAB_CONFIG.find(t => t.value === lastTab)) {
      return lastTab
    }
    return 'overview'
  }

  const [activeTab, setActiveTab] = useState<TabValue>(getInitialTab())

  // Update URL when tab changes
  const handleTabChange = useCallback((value: string) => {
    const newTab = value as TabValue
    setActiveTab(newTab)
    setSearchParams({ tab: newTab }, { replace: true })
    localStorage.setItem(LAST_TAB_KEY, newTab)
  }, [setSearchParams])

  // Tab switching shortcuts (from other tabs)
  const switchToTab = useCallback((tab: TabValue) => {
    handleTabChange(tab)
  }, [handleTabChange])

  // Switch to screener with sector filter
  const switchToScreenerWithSector = useCallback((sector: string) => {
    setSectorFilter(sector)
    handleTabChange('screener')
  }, [handleTabChange])

  // Keyboard shortcuts: Cmd/Ctrl + 1-5
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key >= '1' && e.key <= '5') {
        e.preventDefault()
        const index = parseInt(e.key) - 1
        const tab = TAB_CONFIG[index]
        if (tab) {
          handleTabChange(tab.value)
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleTabChange])

  // Scroll shadow effect for tab navigation
  useEffect(() => {
    const handleScroll = () => {
      setShowScrollShadow(window.scrollY > 10)
    }

    window.addEventListener('scroll', handleScroll)
    handleScroll() // Check initial state
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Market Dashboard
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Comprehensive market analysis and stock screening platform
              </p>
            </div>

            {/* Auto-refresh toggle */}
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Auto-refresh</span>
              </label>
              {autoRefresh && (
                <span className="text-xs text-gray-500">(1 min)</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Container */}
      <Tabs.Root value={activeTab} onValueChange={handleTabChange}>
        {/* Tab Navigation (Sticky) */}
        <div
          className={`sticky top-0 z-40 bg-white border-b border-gray-200 transition-shadow ${
            showScrollShadow ? 'shadow-md' : 'shadow-sm'
          }`}
        >
          <div className="container mx-auto px-4">
            <Tabs.List className="flex gap-1">
              {TAB_CONFIG.map((tab) => (
                <Tabs.Trigger
                  key={tab.value}
                  value={tab.value}
                  className="px-6 py-3 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 border-b-2 border-transparent data-[state=active]:text-blue-600 data-[state=active]:border-blue-600 transition-colors"
                >
                  {tab.label}
                  <kbd className="ml-2 hidden sm:inline-block px-1.5 py-0.5 text-xs font-mono text-gray-500 bg-gray-100 rounded">
                    ⌘{tab.kbd}
                  </kbd>
                </Tabs.Trigger>
              ))}
            </Tabs.List>
          </div>
        </div>

        {/* Tab Content */}
        <div className="container mx-auto px-4 py-6">
          <Tabs.Content value="overview" className="focus:outline-none">
            <OverviewTab
              autoRefresh={autoRefresh}
              refreshInterval={60000}
              onSwitchToMovers={() => switchToTab('movers')}
              onSwitchToSectors={() => switchToTab('sectors')}
            />
          </Tabs.Content>

          <Tabs.Content value="screener" className="focus:outline-none">
            <ScreenerTab
              initialFilters={sectorFilter ? { sector: sectorFilter } : undefined}
            />
          </Tabs.Content>

          <Tabs.Content value="heatmap" className="focus:outline-none">
            <HeatMapTab
              autoRefresh={autoRefresh}
              onSectorClick={switchToScreenerWithSector}
            />
          </Tabs.Content>

          <Tabs.Content value="movers" className="focus:outline-none">
            <MoversTab autoRefresh={autoRefresh} />
          </Tabs.Content>

          <Tabs.Content value="sectors" className="focus:outline-none">
            <SectorsTab
              autoRefresh={autoRefresh}
              onSectorClick={switchToScreenerWithSector}
            />
          </Tabs.Content>
        </div>
      </Tabs.Root>

      {/* Footer info */}
      <div className="container mx-auto px-4 py-6">
        <div className="rounded-lg bg-blue-50 p-4 text-center">
          <p className="text-sm text-blue-800">
            💡 <strong>Keyboard Shortcuts:</strong> Press Cmd/Ctrl + 1-5 to quickly switch between tabs.
            Click on sectors or stocks to drill down into detailed analysis.
          </p>
        </div>
      </div>

      {/* Scroll to top button */}
      <ScrollToTopButton />
    </div>
  )
}

export default MarketDashboardPage
