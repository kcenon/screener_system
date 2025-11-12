[**Stock Screening Platform - Frontend API v0.1.0**](../../../../README.md)

***

[Stock Screening Platform - Frontend API](../../../../modules.md) / [components/screener/FilterPanel](../README.md) / default

# Function: default()

> **default**(`props`): `Element`

Defined in: [src/components/screener/FilterPanel.tsx:165](https://github.com/kcenon/screener_system/blob/643ae632cbed4964dedc9f484332c05bc48a6285/frontend/src/components/screener/FilterPanel.tsx#L165)

Comprehensive stock screening filter panel with collapsible sections.

Provides an intuitive interface for filtering stocks by multiple criteria including
market, sector, valuation metrics, profitability ratios, growth indicators, and
technical signals. Uses Radix UI Accordion for organized, collapsible filter groups.

## Features

- **Market Selection**: Filter by KOSPI, KOSDAQ, or all markets
- **Sector/Industry**: Text-based filtering for sector and industry
- **Search**: Real-time stock name/code search with keyboard shortcuts
- **Preset Management**: Save, load, and delete custom filter combinations
- **Collapsible Sections**: Organized filter groups for better UX
  - Valuation (PER, PBR, PSR, Dividend Yield)
  - Profitability (ROE, ROA, ROIC, Margins)
  - Growth (Revenue, Earnings, EPS growth)
  - Technical (RSI, MACD, Moving Averages)
  - Size & Volume (Market Cap, Trading Volume)
- **Clear All**: One-click filter reset functionality
- **Responsive Design**: Mobile-friendly interface

## Filter Organization

Filters are organized into logical groups using Radix Accordion:
- Basic filters (Search, Market, Sector/Industry) always visible
- Advanced filters grouped by category in collapsible sections
- Default expanded sections for common use cases

## Parameters

### props

`FilterPanelProps`

Component props

## Returns

`Element`

React component rendering the complete filter panel

## Component

## Examples

Basic usage with required props
```tsx
const [filters, setFilters] = useState<ScreeningFilters>({ market: 'ALL' });

<FilterPanel
  filters={filters}
  onFiltersChange={setFilters}
  onClearFilters={() => setFilters({ market: 'ALL' })}
/>
```

Advanced usage with preset management
```tsx
const { filters, setFilters } = useScreening();
const { presets, savePreset, deletePreset } = useFilterPresets();

<FilterPanel
  filters={filters}
  onFiltersChange={setFilters}
  onClearFilters={() => setFilters({ market: 'ALL' })}
  presets={presets}
  onSavePreset={(name, desc) => savePreset({ name, description: desc, filters })}
  onDeletePreset={deletePreset}
/>
```

Handling filter changes
```tsx
const handleFiltersChange = (newFilters: ScreeningFilters) => {
  // Validate filters
  if (newFilters.per?.min < 0) {
    toast.error('PER minimum cannot be negative');
    return;
  }

  // Update state (triggers screening query)
  setFilters(newFilters);

  // Track analytics
  analytics.track('filters_changed', { filters: newFilters });
};
```

## See

 - [ScreeningFilters](../../../../types/screening/interfaces/ScreeningFilters.md) for filter data structure
 - [FilterPreset](../../../../hooks/useFilterPresets/interfaces/FilterPreset.md) for preset data structure
 - [RangeFilter](../../RangeFilter/functions/default.md) for individual range filter component
 - [FilterPresetManager](../../FilterPresetManager/functions/default.md) for preset management UI
 - [SearchBar](../../SearchBar/functions/default.md) for search functionality

## Subcategory

Screening
