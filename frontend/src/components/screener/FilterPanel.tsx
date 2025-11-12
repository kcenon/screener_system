import { useState } from 'react'
import * as Accordion from '@radix-ui/react-accordion'
import type { ScreeningFilters } from '@/types/screening'
import type { FilterPreset } from '@/hooks/useFilterPresets'
import RangeFilter from './RangeFilter'
import SearchBar from './SearchBar'
import FilterPresetManager from './FilterPresetManager'

/**
 * Props for FilterPanel component.
 *
 * Controls the filter panel's behavior including current filter state,
 * filter change handlers, and preset management.
 *
 * @interface
 * @category Types
 */
interface FilterPanelProps {
  /**
   * Current filter values applied to the stock screening.
   * Contains all active filters including market, sector, valuations, etc.
   *
   * @see {@link ScreeningFilters} for complete filter structure
   */
  filters: ScreeningFilters

  /**
   * Callback invoked when any filter value changes.
   * Should update the parent component's filter state.
   *
   * @param filters - Updated filter object with new values
   *
   * @example
   * ```tsx
   * onFiltersChange({ ...currentFilters, market: 'KOSPI' })
   * ```
   */
  onFiltersChange: (filters: ScreeningFilters) => void

  /**
   * Callback invoked when "Clear All" button is clicked.
   * Should reset all filters to their default values.
   */
  onClearFilters: () => void

  /**
   * List of saved filter presets available to the user.
   * If provided, enables preset management functionality.
   *
   * @defaultValue []
   */
  presets?: FilterPreset[]

  /**
   * Callback invoked when user saves current filters as a new preset.
   *
   * @param name - User-provided name for the preset
   * @param description - Optional description of the preset
   */
  onSavePreset?: (name: string, description?: string) => void

  /**
   * Callback invoked when user deletes a saved preset.
   *
   * @param id - Unique identifier of the preset to delete
   */
  onDeletePreset?: (id: string) => void
}

/**
 * Comprehensive stock screening filter panel with collapsible sections.
 *
 * Provides an intuitive interface for filtering stocks by multiple criteria including
 * market, sector, valuation metrics, profitability ratios, growth indicators, and
 * technical signals. Uses Radix UI Accordion for organized, collapsible filter groups.
 *
 * ## Features
 *
 * - **Market Selection**: Filter by KOSPI, KOSDAQ, or all markets
 * - **Sector/Industry**: Text-based filtering for sector and industry
 * - **Search**: Real-time stock name/code search with keyboard shortcuts
 * - **Preset Management**: Save, load, and delete custom filter combinations
 * - **Collapsible Sections**: Organized filter groups for better UX
 *   - Valuation (PER, PBR, PSR, Dividend Yield)
 *   - Profitability (ROE, ROA, ROIC, Margins)
 *   - Growth (Revenue, Earnings, EPS growth)
 *   - Technical (RSI, MACD, Moving Averages)
 *   - Size & Volume (Market Cap, Trading Volume)
 * - **Clear All**: One-click filter reset functionality
 * - **Responsive Design**: Mobile-friendly interface
 *
 * ## Filter Organization
 *
 * Filters are organized into logical groups using Radix Accordion:
 * - Basic filters (Search, Market, Sector/Industry) always visible
 * - Advanced filters grouped by category in collapsible sections
 * - Default expanded sections for common use cases
 *
 * @component
 * @example
 * Basic usage with required props
 * ```tsx
 * const [filters, setFilters] = useState<ScreeningFilters>({ market: 'ALL' });
 *
 * <FilterPanel
 *   filters={filters}
 *   onFiltersChange={setFilters}
 *   onClearFilters={() => setFilters({ market: 'ALL' })}
 * />
 * ```
 *
 * @example
 * Advanced usage with preset management
 * ```tsx
 * const { filters, setFilters } = useScreening();
 * const { presets, savePreset, deletePreset } = useFilterPresets();
 *
 * <FilterPanel
 *   filters={filters}
 *   onFiltersChange={setFilters}
 *   onClearFilters={() => setFilters({ market: 'ALL' })}
 *   presets={presets}
 *   onSavePreset={(name, desc) => savePreset({ name, description: desc, filters })}
 *   onDeletePreset={deletePreset}
 * />
 * ```
 *
 * @example
 * Handling filter changes
 * ```tsx
 * const handleFiltersChange = (newFilters: ScreeningFilters) => {
 *   // Validate filters
 *   if (newFilters.per?.min < 0) {
 *     toast.error('PER minimum cannot be negative');
 *     return;
 *   }
 *
 *   // Update state (triggers screening query)
 *   setFilters(newFilters);
 *
 *   // Track analytics
 *   analytics.track('filters_changed', { filters: newFilters });
 * };
 * ```
 *
 * @param props - Component props
 * @param props.filters - Current filter state
 * @param props.onFiltersChange - Filter change handler
 * @param props.onClearFilters - Clear all handler
 * @param props.presets - Saved filter presets
 * @param props.onSavePreset - Save preset handler
 * @param props.onDeletePreset - Delete preset handler
 *
 * @returns React component rendering the complete filter panel
 *
 * @see {@link ScreeningFilters} for filter data structure
 * @see {@link FilterPreset} for preset data structure
 * @see {@link RangeFilter} for individual range filter component
 * @see {@link FilterPresetManager} for preset management UI
 * @see {@link SearchBar} for search functionality
 *
 * @category Components
 * @subcategory Screening
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
