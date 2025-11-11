import { useState } from 'react'
import * as Accordion from '@radix-ui/react-accordion'
import type { ScreeningFilters } from '@/types/screening'
import type { FilterPreset } from '@/hooks/useFilterPresets'
import RangeFilter from './RangeFilter'
import SearchBar from './SearchBar'
import FilterPresetManager from './FilterPresetManager'

/**
 * Props for FilterPanel component
 */
interface FilterPanelProps {
  /** Current filter values */
  filters: ScreeningFilters
  /** Callback when filters change */
  onFiltersChange: (filters: ScreeningFilters) => void
  /** Callback when clear all button is clicked */
  onClearFilters: () => void
  /** List of saved filter presets */
  presets?: FilterPreset[]
  /** Callback when a preset is saved */
  onSavePreset?: (name: string, description?: string) => void
  /** Callback when a preset is deleted */
  onDeletePreset?: (id: string) => void
}

/**
 * FilterPanel component with collapsible filter sections
 *
 * Features:
 * - Market selector (KOSPI/KOSDAQ/ALL)
 * - Sector/Industry text inputs
 * - Collapsible filter sections using Radix Accordion
 * - Clear all button
 * - Responsive design
 */
export default function FilterPanel({
  filters,
  onFiltersChange,
  onClearFilters,
  presets = [],
  onSavePreset,
  onDeletePreset,
}: FilterPanelProps) {
  const [openSections, setOpenSections] = useState<string[]>(['basic'])

  const updateFilter = <K extends keyof ScreeningFilters>(
    key: K,
    value: ScreeningFilters[K]
  ) => {
    onFiltersChange({ ...filters, [key]: value })
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
        <button
          onClick={onClearFilters}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          Clear All
        </button>
      </div>

      {/* Filter Presets */}
      {onSavePreset && onDeletePreset && (
        <FilterPresetManager
          presets={presets}
          onLoadPreset={onFiltersChange}
          onSavePreset={onSavePreset}
          onDeletePreset={onDeletePreset}
        />
      )}

      {/* Divider */}
      {onSavePreset && onDeletePreset && <div className="border-t border-gray-200" />}

      {/* Search Bar */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">Search</label>
        <SearchBar
          value={filters.search || ''}
          onChange={(value) => updateFilter('search', value || null)}
          enableShortcut={true}
        />
      </div>

      {/* Market Selector */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">Market</label>
        <div className="flex space-x-2">
          {(['ALL', 'KOSPI', 'KOSDAQ'] as const).map((market) => (
            <button
              key={market}
              onClick={() => updateFilter('market', market)}
              className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                filters.market === market
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {market}
            </button>
          ))}
        </div>
      </div>

      {/* Sector/Industry */}
      <div className="space-y-3">
        <div>
          <label htmlFor="sector" className="block text-sm font-medium text-gray-700 mb-1">
            Sector
          </label>
          <input
            id="sector"
            type="text"
            value={filters.sector || ''}
            onChange={(e) => updateFilter('sector', e.target.value || null)}
            placeholder="e.g., Technology"
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <div>
          <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-1">
            Industry
          </label>
          <input
            id="industry"
            type="text"
            value={filters.industry || ''}
            onChange={(e) => updateFilter('industry', e.target.value || null)}
            placeholder="e.g., Semiconductors"
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Collapsible Filter Sections */}
      <Accordion.Root
        type="multiple"
        value={openSections}
        onValueChange={setOpenSections}
        className="space-y-2"
      >
        {/* Valuation Filters */}
        <Accordion.Item value="valuation" className="border border-gray-200 rounded-md">
          <Accordion.Header>
            <Accordion.Trigger className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium text-gray-900 hover:bg-gray-50">
              Valuation
              <svg
                className="h-4 w-4 transition-transform duration-200 data-[state=open]:rotate-180"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Content className="px-4 pb-4 space-y-3">
            <RangeFilter
              label="PER"
              value={filters.per}
              onChange={(value) => updateFilter('per', value)}
            />
            <RangeFilter
              label="PBR"
              value={filters.pbr}
              onChange={(value) => updateFilter('pbr', value)}
            />
            <RangeFilter
              label="PSR"
              value={filters.psr}
              onChange={(value) => updateFilter('psr', value)}
            />
            <RangeFilter
              label="Dividend Yield"
              value={filters.dividend_yield}
              onChange={(value) => updateFilter('dividend_yield', value)}
              unit="%"
            />
          </Accordion.Content>
        </Accordion.Item>

        {/* Profitability Filters */}
        <Accordion.Item value="profitability" className="border border-gray-200 rounded-md">
          <Accordion.Header>
            <Accordion.Trigger className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium text-gray-900 hover:bg-gray-50">
              Profitability
              <svg
                className="h-4 w-4 transition-transform duration-200 data-[state=open]:rotate-180"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Content className="px-4 pb-4 space-y-3">
            <RangeFilter
              label="ROE"
              value={filters.roe}
              onChange={(value) => updateFilter('roe', value)}
              unit="%"
            />
            <RangeFilter
              label="ROA"
              value={filters.roa}
              onChange={(value) => updateFilter('roa', value)}
              unit="%"
            />
            <RangeFilter
              label="ROIC"
              value={filters.roic}
              onChange={(value) => updateFilter('roic', value)}
              unit="%"
            />
            <RangeFilter
              label="Gross Margin"
              value={filters.gross_margin}
              onChange={(value) => updateFilter('gross_margin', value)}
              unit="%"
            />
            <RangeFilter
              label="Operating Margin"
              value={filters.operating_margin}
              onChange={(value) => updateFilter('operating_margin', value)}
              unit="%"
            />
            <RangeFilter
              label="Net Margin"
              value={filters.net_margin}
              onChange={(value) => updateFilter('net_margin', value)}
              unit="%"
            />
          </Accordion.Content>
        </Accordion.Item>

        {/* Growth Filters */}
        <Accordion.Item value="growth" className="border border-gray-200 rounded-md">
          <Accordion.Header>
            <Accordion.Trigger className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium text-gray-900 hover:bg-gray-50">
              Growth
              <svg
                className="h-4 w-4 transition-transform duration-200 data-[state=open]:rotate-180"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Content className="px-4 pb-4 space-y-3">
            <RangeFilter
              label="Revenue Growth YoY"
              value={filters.revenue_growth_yoy}
              onChange={(value) => updateFilter('revenue_growth_yoy', value)}
              unit="%"
            />
            <RangeFilter
              label="Profit Growth YoY"
              value={filters.profit_growth_yoy}
              onChange={(value) => updateFilter('profit_growth_yoy', value)}
              unit="%"
            />
            <RangeFilter
              label="EPS Growth YoY"
              value={filters.eps_growth_yoy}
              onChange={(value) => updateFilter('eps_growth_yoy', value)}
              unit="%"
            />
          </Accordion.Content>
        </Accordion.Item>

        {/* Stability Filters */}
        <Accordion.Item value="stability" className="border border-gray-200 rounded-md">
          <Accordion.Header>
            <Accordion.Trigger className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium text-gray-900 hover:bg-gray-50">
              Stability
              <svg
                className="h-4 w-4 transition-transform duration-200 data-[state=open]:rotate-180"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Content className="px-4 pb-4 space-y-3">
            <RangeFilter
              label="Debt-to-Equity"
              value={filters.debt_to_equity}
              onChange={(value) => updateFilter('debt_to_equity', value)}
            />
            <RangeFilter
              label="Current Ratio"
              value={filters.current_ratio}
              onChange={(value) => updateFilter('current_ratio', value)}
            />
            <RangeFilter
              label="Altman Z-Score"
              value={filters.altman_z_score}
              onChange={(value) => updateFilter('altman_z_score', value)}
            />
            <RangeFilter
              label="Piotroski F-Score"
              value={filters.piotroski_f_score}
              onChange={(value) => updateFilter('piotroski_f_score', value)}
              minPlaceholder="0"
              maxPlaceholder="9"
            />
          </Accordion.Content>
        </Accordion.Item>

        {/* Momentum Filters */}
        <Accordion.Item value="momentum" className="border border-gray-200 rounded-md">
          <Accordion.Header>
            <Accordion.Trigger className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium text-gray-900 hover:bg-gray-50">
              Momentum
              <svg
                className="h-4 w-4 transition-transform duration-200 data-[state=open]:rotate-180"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Content className="px-4 pb-4 space-y-3">
            <RangeFilter
              label="1-Day Change"
              value={filters.price_change_1d}
              onChange={(value) => updateFilter('price_change_1d', value)}
              unit="%"
            />
            <RangeFilter
              label="1-Week Change"
              value={filters.price_change_1w}
              onChange={(value) => updateFilter('price_change_1w', value)}
              unit="%"
            />
            <RangeFilter
              label="1-Month Change"
              value={filters.price_change_1m}
              onChange={(value) => updateFilter('price_change_1m', value)}
              unit="%"
            />
            <RangeFilter
              label="3-Month Change"
              value={filters.price_change_3m}
              onChange={(value) => updateFilter('price_change_3m', value)}
              unit="%"
            />
            <RangeFilter
              label="6-Month Change"
              value={filters.price_change_6m}
              onChange={(value) => updateFilter('price_change_6m', value)}
              unit="%"
            />
            <RangeFilter
              label="1-Year Change"
              value={filters.price_change_1y}
              onChange={(value) => updateFilter('price_change_1y', value)}
              unit="%"
            />
          </Accordion.Content>
        </Accordion.Item>

        {/* Scores */}
        <Accordion.Item value="scores" className="border border-gray-200 rounded-md">
          <Accordion.Header>
            <Accordion.Trigger className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium text-gray-900 hover:bg-gray-50">
              Composite Scores
              <svg
                className="h-4 w-4 transition-transform duration-200 data-[state=open]:rotate-180"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Content className="px-4 pb-4 space-y-3">
            <RangeFilter
              label="Quality Score"
              value={filters.quality_score}
              onChange={(value) => updateFilter('quality_score', value)}
              minPlaceholder="0"
              maxPlaceholder="100"
            />
            <RangeFilter
              label="Value Score"
              value={filters.value_score}
              onChange={(value) => updateFilter('value_score', value)}
              minPlaceholder="0"
              maxPlaceholder="100"
            />
            <RangeFilter
              label="Growth Score"
              value={filters.growth_score}
              onChange={(value) => updateFilter('growth_score', value)}
              minPlaceholder="0"
              maxPlaceholder="100"
            />
            <RangeFilter
              label="Momentum Score"
              value={filters.momentum_score}
              onChange={(value) => updateFilter('momentum_score', value)}
              minPlaceholder="0"
              maxPlaceholder="100"
            />
            <RangeFilter
              label="Overall Score"
              value={filters.overall_score}
              onChange={(value) => updateFilter('overall_score', value)}
              minPlaceholder="0"
              maxPlaceholder="100"
            />
          </Accordion.Content>
        </Accordion.Item>
      </Accordion.Root>
    </div>
  )
}
