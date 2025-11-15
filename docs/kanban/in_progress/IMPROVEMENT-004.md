# [IMPROVEMENT-004] Advanced Features & Finalization - Heat Map, Quick Filters, Compact Tables (Phase 3)

## Metadata
- **Status**: IN_PROGRESS
- **Priority**: Medium
- **Assignee**: Frontend Team
- **Estimated Time**: 10-12 hours
- **Started**: 2025-11-15
- **Sprint**: Phase 3 Enhancement
- **Tags**: #frontend #ui-ux #visualization #heatmap #filters #tables #finviz
- **Dependencies**: IMPROVEMENT-002 ✅, IMPROVEMENT-003 ✅
- **Blocks**: None
- **Related**: [UI/UX Improvements Document](../../improvements/finviz-inspired-ui-improvements.md)

## Description
Implement advanced finviz-inspired features to complete the UI/UX transformation: interactive sector heat map with treemap visualization, quick filter shortcuts for common screening tasks, and ultra-compact table design for maximum information density.

## Problem Statement
Despite improvements from Phase 1 and 2, several advanced usability features are still missing:
- ❌ **Limited Sector Visualization**: Current heatmap is grid-based, not proportional to market cap
- ❌ **Filter Friction**: Common filters require multiple clicks to apply
- ❌ **Suboptimal Table Density**: Tables still waste space with large cells
- ❌ **No Drill-Down**: Cannot explore market hierarchy (sector → industry → stock)
- ❌ **Manual Pagination**: No infinite scroll or smart loading

**Impact**: Power users still require too many interactions to reach insights

## Proposed Solution
Implement three advanced features:

### 1. Enhanced Sector Heat Map with Treemap (5 hours)
**Component**: `frontend/src/components/market/SectorHeatmapAdvanced.tsx`

**Visualization**:
- Use **Recharts Treemap** component
- 3-level hierarchy:
  1. **Sector** (10 sectors, e.g., "Technology")
  2. **Industry** (optional drill-down, e.g., "Semiconductors")
  3. **Top 3 Stocks** per sector (e.g., "삼성전자")

**Features**:
```tsx
┌─────────────────────────────────────────────────────────┐
│                    Sector Heat Map                      │
│  ┌─────────────┬──────┬─────────────┬────────────────┐ │
│  │  Technology │ Fin  │  Healthcare │    Consumer    │ │
│  │             │ance  │             │                │ │
│  │  +2.3%      │-0.5% │  +1.8%      │    +0.4%       │ │
│  │  ┌──┬──┬──┐ │ ┌──┐ │  ┌───┬───┐  │  ┌──┬──┬────┐ │ │
│  │  │삼│SK│.│ │ │  │  │  │   │   │  │  │  │  │    │ │ │
│  │  └──┴──┴──┘ │ └──┘ │  └───┴───┘  │  └──┴──┴────┘ │ │
│  └─────────────┴──────┴─────────────┴────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Color Scale** (5-level):
| Performance | Color       | Hex Code |
|-------------|-------------|----------|
| > +3%       | Dark Green  | #166534  |
| +1% to +3%  | Green       | #16a34a  |
| -1% to +1%  | Gray        | #6b7280  |
| -3% to -1%  | Red         | #dc2626  |
| < -3%       | Dark Red    | #991b1b  |

**Interactions**:
- **Hover**: Tooltip shows sector name, change %, market cap, stock count
- **Click Sector**: Opens screener filtered by that sector (Tab 2)
- **Click Stock**: Navigates to stock detail page
- **Zoom/Pan**: Optional (for very large displays)
- **Toggle View**: Switch between sector-only and stock-drilldown

**Data Structure**:
```typescript
interface TreemapData {
  name: string              // "Technology"
  value: number             // Market cap (for size)
  performance: number       // Change % (for color)
  children?: TreemapData[]  // Nested stocks
}
```

**API Integration**:
- Use existing `useSectorPerformance` hook
- Fetch top 3 stocks per sector from backend
- Calculate aggregated market cap for sizing

### 2. Quick Filter Shortcuts Bar (3 hours)
**Component**: `frontend/src/components/screener/QuickFiltersBar.tsx`

**Layout** (above Results Table in Screener tab):
```tsx
┌────────────────────────────────────────────────────────────┐
│ 인기 필터:                                                  │
│ [상위상승⬆] [상위하락⬇] [고거래량📊] [52주신고가🏔] [배당💰] │
│ [저PER💎] [고성장📈] [소형주🐣] [대형주🦁] [신규상장✨]     │
└────────────────────────────────────────────────────────────┘
```

**Preset Filters**:

| Button | Label | Filter Criteria | Icon |
|--------|-------|-----------------|------|
| 1 | 상위 상승 | `change_percent > 5` | ⬆ |
| 2 | 상위 하락 | `change_percent < -5` | ⬇ |
| 3 | 고거래량 | `volume > avg_volume * 2` | 📊 |
| 4 | 52주 신고가 | `close_price >= week_52_high * 0.99` | 🏔 |
| 5 | 고배당 | `dividend_yield > 4` | 💰 |
| 6 | 저PER | `pe_ratio > 0 AND pe_ratio < 10` | 💎 |
| 7 | 고성장 | `sales_growth_1y > 20` | 📈 |
| 8 | 소형주 | `market_cap < 1000억` | 🐣 |
| 9 | 대형주 | `market_cap > 10조` | 🦁 |
| 10 | 신규상장 | `listing_date > now() - 90 days` | ✨ |

**Behavior**:
- Click = Apply preset filter (adds to existing filters)
- Active state highlighted (blue background)
- Multiple presets can be combined
- "Clear All" button to reset
- Tooltips explain each preset
- Mobile: scrollable horizontal row

**Implementation**:
```typescript
const quickFilters: QuickFilter[] = [
  {
    id: 'top-gainers',
    label: '상위상승',
    icon: '⬆',
    filters: { change_percent_min: 5 }
  },
  // ... more presets
]

function QuickFiltersBar({ onFilterApply }) {
  const [active, setActive] = useState<string[]>([])

  const handleClick = (filter: QuickFilter) => {
    if (active.includes(filter.id)) {
      // Deactivate
      setActive(active.filter(id => id !== filter.id))
      onFilterApply({}) // Clear filters
    } else {
      // Activate
      setActive([...active, filter.id])
      onFilterApply(filter.filters)
    }
  }

  return (/* render buttons */)
}
```

### 3. Ultra-Compact Table Design (4 hours)
**Component**: Update `frontend/src/components/screener/ResultsTable.tsx`

**Current vs. Proposed**:

| Aspect | Current | Proposed | Change |
|--------|---------|----------|--------|
| Row Height | 48px | 32px | -33% |
| Font Size | 14px | 12px | -14% |
| Cell Padding | 12px 16px | 6px 10px | -50% |
| Number Format | 1,500,000 | 1.5M | -60% chars |
| Visible Rows (1080p) | ~15 | ~25 | +67% |

**Enhanced Features**:

1. **In-Cell Sparklines**:
   - Mini price chart (30px × 20px) in "Price" column
   - Shows 7-day price trend
   - Green/red line color

2. **Icon Indicators**:
   - ↑ Green arrow for positive change
   - ↓ Red arrow for negative change
   - → Gray for neutral
   - 🔥 Fire icon for high volume (> 2x avg)
   - 💎 Diamond for value stocks (low P/E)

3. **Conditional Formatting**:
   - Bold text for top/bottom 10%
   - Fade out low-volume stocks (opacity: 0.7)
   - Highlight rows on hover (bg-gray-50)

4. **Compact Number Formatting**:
```typescript
// frontend/src/utils/formatNumber.ts (update)
export function formatTableNumber(num: number, type: 'price' | 'volume' | 'marketcap'): string {
  if (type === 'price') {
    return num.toLocaleString('ko-KR', { maximumFractionDigits: 0 })
  }
  if (type === 'volume') {
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`
    if (num >= 1e3) return `${(num / 1e3).toFixed(0)}K`
    return num.toString()
  }
  if (type === 'marketcap') {
    if (num >= 1e12) return `${(num / 1e12).toFixed(1)}조` // Trillion
    if (num >= 1e8) return `${(num / 1e8).toFixed(0)}억`  // Hundred million
    return `${(num / 1e4).toFixed(0)}만`                  // Ten thousand
  }
  return num.toString()
}
```

5. **Virtual Scrolling** (optional optimization):
   - Use `react-window` or `@tanstack/react-virtual`
   - Render only visible rows
   - Supports 10,000+ results smoothly

**Updated Table Structure**:
```tsx
<table className="w-full text-xs">  {/* Reduced font size */}
  <thead className="bg-gray-50 sticky top-0">
    <tr className="h-8">  {/* Reduced header height */}
      <th className="px-3 py-1">종목코드</th>  {/* Reduced padding */}
      <th>이름</th>
      <th>가격</th>
      <th>등락률 <span className="text-gray-400">▼</span></th>
      <th>거래량</th>
      <th>시가총액</th>
      <th>PER</th>
    </tr>
  </thead>
  <tbody>
    <tr className="h-8 border-b hover:bg-gray-50">  {/* Compact rows */}
      <td className="px-3 py-1 text-gray-600">005930</td>
      <td className="font-medium">삼성전자</td>
      <td>71,000</td>
      <td className="text-green-600">
        ↑ +2.3%  {/* Icon + percentage */}
      </td>
      <td className="flex items-center gap-1">
        12.5M 🔥  {/* Compact + icon */}
      </td>
      <td>425조</td>  {/* Korean format */}
      <td>18.5</td>
    </tr>
    {/* More rows... */}
  </tbody>
</table>
```

### 4. Smart Pagination Enhancements (2 hours)
**Component**: Update `frontend/src/components/common/Pagination.tsx`

**New Features**:

1. **Infinite Scroll Mode**:
   - Toggle button: [Pagination] / [Infinite Scroll]
   - Loads 50 more rows when scrolling near bottom
   - "Load More" button as fallback
   - Persist mode in localStorage

2. **Virtual Scrolling**:
   - For 500+ results
   - Render only visible rows (+10 buffer)
   - Maintain scroll position on filter change

3. **Scroll-to-Top FAB**:
   - Floating action button (bottom-right)
   - Appears after scrolling 200px
   - Smooth scroll animation

**Implementation**:
```typescript
function useInfiniteScroll(fetchMore: () => void) {
  const [isFetching, setIsFetching] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
        if (!isFetching) {
          setIsFetching(true)
          fetchMore()
        }
      }
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [isFetching, fetchMore])

  return { isFetching, setIsFetching }
}
```

## Subtasks

### Phase 3A: Enhanced Heat Map (5 hours) ✅
- [x] Install Recharts treemap (`npm install recharts`)
- [x] Create `SectorHeatmapAdvanced.tsx` component
- [x] Implement treemap with sector-level visualization
- [x] Define 5-level color scale (dark green to dark red)
- [x] Add hover tooltip with sector details
- [x] Click handler to filter screener by sector
- [x] Toggle between grid and treemap views in HeatMapTab
- [x] Responsive sizing with ResponsiveContainer
- [x] Performance optimization (useMemo for data transformation)
- [x] Integrate into Heat Map tab with view toggle

### Phase 3B: Quick Filters Bar (3 hours) ✅
- [x] Create `QuickFiltersBar.tsx` component
- [x] Define 10 preset filters with criteria
- [x] Implement filter activation/deactivation logic
- [x] Active state highlighting (blue background)
- [x] Multiple filter combination support
- [x] "Clear All" button functionality
- [x] Tooltips for each preset filter (Radix UI Tooltip)
- [x] Mobile horizontal scrolling
- [x] Add to Screener page (above results table)
- [x] Integrated with existing filtering system

### Phase 3C: Compact Table Design (4 hours)
- [ ] Update ResultsTable row height to 32px
- [ ] Reduce font size to 12px
- [ ] Reduce cell padding to 6px 10px
- [ ] Implement compact number formatting
  - [ ] Volume: 1.5M format
  - [ ] Market cap: 425조 format
- [ ] Add in-cell sparklines for price
- [ ] Add icon indicators (↑↓→ 🔥 💎)
- [ ] Conditional formatting (bold, fade, highlight)
- [ ] Test with 100+ rows for visual density
- [ ] Mobile: horizontal scroll for table

### Phase 3D: Smart Pagination (2 hours)
- [ ] Add infinite scroll toggle button
- [ ] Implement `useInfiniteScroll` hook
- [ ] "Load More" button (loads 50 rows)
- [ ] Scroll-to-top FAB (floating action button)
- [ ] localStorage persistence for scroll mode
- [ ] Virtual scrolling for 500+ results (optional)
- [ ] Maintain scroll position on filter change
- [ ] Test with large datasets (1000+ stocks)

### Phase 3E: Testing & Documentation (2 hours)
- [ ] Visual regression tests
- [ ] Interaction tests (click, hover, scroll)
- [ ] Performance tests (treemap rendering, infinite scroll)
- [ ] Mobile responsiveness tests
- [ ] Accessibility tests (keyboard, screen reader)
- [ ] Update documentation
- [ ] Create demo video/GIF

### Phase 3F: Analytics & Optimization (1 hour)
- [ ] Add analytics tracking for quick filters
- [ ] Track heat map interactions
- [ ] Monitor table scroll performance
- [ ] A/B test compact vs. spacious table
- [ ] Collect user feedback
- [ ] Create performance dashboard

## Acceptance Criteria

- [x] **Enhanced Heat Map**
  - [ ] Treemap displays all 10 sectors proportional to market cap
  - [ ] Color scale matches performance (-3% to +3%)
  - [ ] Hover shows detailed tooltip
  - [ ] Click filters screener by sector
  - [ ] Drill-down to top 3 stocks works
  - [ ] Responsive on mobile (vertical list)

- [x] **Quick Filters**
  - [ ] 10 preset filters implemented
  - [ ] One-click application works
  - [ ] Active state visually clear
  - [ ] Multiple filters can combine
  - [ ] Clear All button resets filters
  - [ ] Tooltips explain each preset
  - [ ] Mobile: scrollable horizontally

- [x] **Compact Table**
  - [ ] Row height reduced to 32px
  - [ ] Font size 12px readable
  - [ ] Numbers formatted compactly (1.5M, 425조)
  - [ ] Sparklines visible in price column
  - [ ] Icon indicators show correctly
  - [ ] +67% more rows visible (15 → 25 on 1080p)
  - [ ] No layout breaks or overlaps

- [x] **Smart Pagination**
  - [ ] Infinite scroll mode works
  - [ ] Load More button functional
  - [ ] Scroll-to-top FAB appears at 200px
  - [ ] Mode persisted in localStorage
  - [ ] Virtual scrolling for 500+ results (if implemented)
  - [ ] Smooth scrolling performance

- [x] **Performance**
  - [ ] Treemap renders < 500ms
  - [ ] Table scroll at 60fps
  - [ ] Infinite scroll no lag
  - [ ] Bundle size increase < 30KB (Recharts gzip)
  - [ ] Lighthouse score ≥ 90

- [x] **Testing**
  - [ ] All tests pass
  - [ ] No regressions
  - [ ] Mobile tests pass
  - [ ] Accessibility tests pass

## Performance Targets
- **Information Density**: +67% rows visible (15 → 25)
- **Filter Speed**: -80% time for common filters (click vs. manual)
- **Heat Map Insights**: -90% time to identify hot/cold sectors
- **Scroll Performance**: 60fps maintained with 1000+ rows

## Technical Considerations

### New Dependencies
```json
{
  "dependencies": {
    "recharts": "^2.10.0",           // Treemap visualization
    "@tanstack/react-virtual": "^3.0.0"  // Virtual scrolling (optional)
  }
}
```

### Bundle Size Impact
- Recharts: ~80KB gzip (treemap only, tree-shaking)
- React Virtual: ~5KB gzip
- Total increase: ~85KB (acceptable for advanced features)

### Component Architecture
```
frontend/src/
├── components/
│   ├── market/
│   │   ├── SectorHeatmapAdvanced.tsx  # NEW: Treemap
│   │   └── SectorHeatmap.tsx          # OLD: Keep for fallback
│   ├── screener/
│   │   ├── QuickFiltersBar.tsx        # NEW: Preset filters
│   │   ├── ResultsTable.tsx           # UPDATED: Compact
│   │   └── InCellSparkline.tsx        # NEW: Mini chart
│   └── common/
│       ├── Pagination.tsx             # UPDATED: Infinite scroll
│       └── ScrollToTopFAB.tsx         # NEW: Floating button
└── hooks/
    ├── useInfiniteScroll.ts           # NEW: Infinite scroll logic
    └── useVirtualScroll.ts            # NEW: Virtual scrolling (optional)
```

### Performance Optimization
- **Treemap**: Use `useMemo` for data transformation
- **Table**: Virtual scrolling for 500+ rows
- **Sparklines**: Canvas-based rendering (faster than SVG)
- **Icons**: Use Unicode characters (no image loading)

### Accessibility
- Heat map: ARIA labels for sectors
- Quick filters: Keyboard shortcuts (Alt+1-9)
- Table: Arrow key navigation
- Infinite scroll: "Load More" fallback

## Dependencies
- ✅ IMPROVEMENT-002 (Global UI/UX Foundation)
- ✅ IMPROVEMENT-003 (Unified Dashboard)
- 📦 Recharts library
- 📦 React Virtual (optional)

## Testing Strategy

### Unit Tests
- Quick filter logic
- Number formatting utilities
- Infinite scroll hook

### Integration Tests
- Heat map click → screener filter
- Quick filter application
- Table sorting with virtual scroll

### Visual Tests
- Treemap rendering
- Color scale accuracy
- Table density verification

### Performance Tests
- Treemap render time
- Table scroll FPS
- Infinite scroll smoothness
- Bundle size analysis

## Rollout Plan
1. **Development**: Feature branch
2. **Staging**: Team review
3. **A/B Test**: 10% users (heat map and quick filters)
4. **Gradual Rollout**: 25% → 50% → 100%
5. **Monitor**: Engagement metrics, performance

## Success Metrics
- [ ] +90% faster sector identification (heat map)
- [ ] -80% filter application time (quick filters)
- [ ] +67% table information density
- [ ] +40% user engagement (time on screener)
- [ ] +25% conversion rate (insights → actions)
- [ ] 0 performance regressions

## References
- [UI/UX Improvements Document](../../improvements/finviz-inspired-ui-improvements.md)
- [Recharts Treemap](https://recharts.org/en-US/api/Treemap)
- [React Virtual](https://tanstack.com/virtual/latest)
- [Finviz Heat Map](https://finviz.com/map.ashx)

## Progress
**Current Status**: 40% (Phase 3A & 3B Complete)

**Completion Checklist**:
- [x] Phase 3A: Heat Map (10/10 tasks) ✅
- [x] Phase 3B: Quick Filters (10/10 tasks) ✅
- [ ] Phase 3C: Compact Table (0/9 tasks)
- [ ] Phase 3D: Smart Pagination (0/8 tasks)
- [ ] Phase 3E: Testing (0/7 tasks)
- [ ] Phase 3F: Analytics (0/6 tasks)

**Total**: 20/50 subtasks completed

### Phase 3A Completion Notes:
- Implemented Recharts treemap with market cap-based sizing
- 5-level color scale matches finviz design
- Sector-only visualization (drill-down to stocks deferred)
- Grid/Treemap toggle in HeatMapTab
- Comprehensive unit tests (7 tests passing)
- TypeScript type-safe implementation
- Build successful with no errors

### Phase 3B Completion Notes:
- Created QuickFiltersBar component with 10 preset filters
- Filters mapped to actual ScreeningFilters API (FilterRange objects)
- Radix UI Tooltip integration for explanatory hover text
- Active state management with visual highlighting
- Multiple filter combination support
- Mobile-responsive horizontal scrolling
- Integrated into ScreenerPage above results table
- TypeScript type-safe with all checks passing

## Notes
- Final phase of finviz-inspired improvements
- Focus on power user features
- Consider user feedback from Phase 1 and 2
- Heat map can be rolled out independently
- Quick filters have high user demand
- Compact table may need A/B testing (readability concerns)
- Monitor analytics to validate effectiveness
