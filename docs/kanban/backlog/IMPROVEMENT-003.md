# [IMPROVEMENT-003] Unified Market Dashboard - Tabbed Interface (Phase 2)

## Metadata
- **Status**: BACKLOG
- **Priority**: High
- **Assignee**: Frontend Team
- **Estimated Time**: 12-14 hours
- **Sprint**: Phase 3 Enhancement
- **Tags**: #frontend #ui-ux #navigation #tabs #layout #finviz
- **Dependencies**: IMPROVEMENT-002 (Global UI/UX Foundation) ✅
- **Blocks**: IMPROVEMENT-004
- **Related**: [UI/UX Improvements Document](../../improvements/finviz-inspired-ui-improvements.md)

## Description
Transform the fragmented navigation experience into a unified, tabbed market dashboard inspired by finviz.com's efficient layout. Combine Market Overview and Screener into a single page with instant tab switching, sticky navigation, and multi-column layouts to maximize screen real estate.

## Problem Statement
Current navigation structure has significant usability issues:
- ❌ **Context Loss**: Switching between Market Overview and Screener requires full page reload
- ❌ **Navigation Overhead**: 3-4 clicks to move between related views
- ❌ **Inefficient Layouts**: Vertical stacking wastes horizontal screen space
- ❌ **Filter Inaccessibility**: Screener filters disappear when scrolling
- ❌ **Slow Workflow**: Users spend 60% of time navigating, 40% analyzing

**Impact**: Users take 3x longer to complete analysis workflows

## Proposed Solution
Create a unified dashboard with five tabs, sticky navigation, and optimized layouts:

### 1. Unified Market Dashboard Page (6 hours)
**Component**: `frontend/src/pages/MarketDashboardPage.tsx`

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────┐
│ GlobalMarketBar (from Phase 1, sticky top)                  │ ← 40px
├─────────────────────────────────────────────────────────────┤
│ [개요] [스크리너] [히트맵] [상승/하락] [섹터분석]            │ ← 48px (sticky)
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    Active Tab Content                        │
│                    (Full width or split)                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Tab Navigation**:
- Horizontal tab bar (Radix UI Tabs)
- Keyboard shortcuts: Cmd+1-5 to switch tabs
- URL sync: `/market?tab=screener`
- Persist last viewed tab in localStorage
- Smooth transitions (no page reload)

**Tabs Definition**:

#### Tab 1: 개요 (Overview)
- Current MarketOverviewPage content
- 3-column grid for indices (compact from Phase 1)
- Market breadth inline (1 row)
- Top 5 movers preview (click to open Tab 4)
- Sector heatmap preview (click to open Tab 5)

#### Tab 2: 스크리너 (Screener)
- Current ScreenerPage content
- Collapsible filter sidebar (default: open)
- Results table (full width when sidebar collapsed)
- Quick filters bar at top (from Phase 3)
- Export button always visible

#### Tab 3: 히트맵 (Heat Map)
- Full-screen sector treemap
- Size = market cap, Color = performance %
- Click to filter screener by sector (switches to Tab 2)
- Zoom/pan controls
- Toggle between sectors and individual stocks

#### Tab 4: 상승/하락 (Movers)
- Expanded MarketMoversWidget
- Side-by-side: Gainers | Losers
- Full list (100+ stocks)
- Sortable by change %, volume, value
- Filter by market (KOSPI/KOSDAQ/ALL)
- Click stock → navigate to detail page

#### Tab 5: 섹터분석 (Sectors)
- Expanded SectorHeatmap
- Detailed sector breakdown
- Sector composition (top stocks)
- Historical performance charts (7D, 1M, 3M)
- Click sector → filter screener

### 2. Sticky Navigation System (3 hours)
**Implement z-index hierarchy**:
```css
GlobalMarketBar:  position: sticky, top: 0,    z-index: 50
TabNavigation:    position: sticky, top: 40px, z-index: 40
FilterPanel:      position: sticky, top: 88px, z-index: 30  (Screener tab only)
TableHeader:      position: sticky, top: 88px, z-index: 20  (Screener tab only)
```

**Features**:
- All navigation remains accessible while scrolling
- Shadow/border appears on scroll (visual feedback)
- Mobile: tabs become dropdown menu
- Smooth scroll-to-top button (appears after 200px scroll)

### 3. Multi-Column Layouts (5 hours)

#### Market Indices (3-Column Grid)
**Current** (Vertical):
```
┌──────────────┐
│ KOSPI        │  Height: ~400px
│ 2,500.12     │
│ +0.61%       │
│ [Sparkline]  │
└──────────────┘
┌──────────────┐
│ KOSDAQ       │
└──────────────┘
┌──────────────┐
│ KRX100       │
└──────────────┘
```

**Proposed** (Horizontal):
```
┌────────────┬────────────┬────────────┐
│ KOSPI      │ KOSDAQ     │ KRX100     │  Height: ~140px (-65%)
│ 2,500.12   │ 850.45     │ 5,234.67   │
│ ▲ +0.61%   │ ▼ -0.49%   │ ▲ +0.48%   │
│ [Sparkline]│ [Sparkline]│ [Sparkline]│
└────────────┴────────────┴────────────┘
```

#### Market Movers (Split View)
**Layout**:
```
┌─────────────────────────┬─────────────────────────┐
│  상위 상승 (Top 10)      │  상위 하락 (Top 10)      │
│  ─────────────────────  │  ─────────────────────  │
│  삼성전자  +5.2%         │  SK하이닉스  -3.1%       │
│  ...                    │  ...                    │
└─────────────────────────┴─────────────────────────┘
```

#### Screener Filter Panel (Collapsible)
**States**:
- **Expanded** (default): 280px width sidebar
- **Collapsed**: 48px icon bar (click to expand)
- **Mobile**: Slide-in drawer

**Component**: `FilterPanelCollapsible.tsx`

### 4. URL & State Management (2 hours)

**URL Structure**:
```
/market                         → Overview tab (default)
/market?tab=screener            → Screener tab
/market?tab=heatmap             → Heat Map tab
/market?tab=movers              → Movers tab
/market?tab=sectors             → Sectors tab
/market?tab=screener&sector=technology  → Screener filtered by sector
```

**State Persistence**:
- Tab selection: localStorage
- Filter panel collapsed state: localStorage
- Screener filters/sort: URL query params (existing)
- Restore on page reload

## Subtasks

### Phase 2A: Unified Dashboard Structure (4 hours)
- [ ] Create `MarketDashboardPage.tsx` component
- [ ] Integrate Radix UI Tabs component
- [ ] Set up 5 tab panels with routing
- [ ] Implement tab switching logic
- [ ] Add keyboard shortcuts (Cmd+1-5)
- [ ] URL synchronization for active tab
- [ ] localStorage persistence for last tab
- [ ] Update navigation config to point to `/market`

### Phase 2B: Sticky Navigation (3 hours)
- [ ] Implement sticky TabNavigation bar (z-40)
- [ ] Add scroll shadow effect to tab bar
- [ ] Make filter panel sticky (z-30) in Screener tab
- [ ] Make table header sticky (z-20) in Screener tab
- [ ] Add scroll-to-top FAB button
- [ ] Mobile: convert tabs to dropdown menu
- [ ] Test z-index hierarchy across all tabs

### Phase 2C: Multi-Column Layouts (5 hours)
- [ ] Redesign MarketIndicesWidget as 3-column grid
- [ ] Create split-view MarketMoversWidget
  - [ ] Left column: Top gainers
  - [ ] Right column: Top losers
  - [ ] Synchronized scrolling
- [ ] Create FilterPanelCollapsible component
  - [ ] Expanded state (280px)
  - [ ] Collapsed state (48px icon bar)
  - [ ] Smooth transition
  - [ ] Mobile drawer mode
- [ ] Update ResultsTable to use available width
- [ ] Responsive breakpoints (mobile/tablet/desktop)

### Phase 2D: Tab Content Migration (3 hours)
- [ ] Tab 1 (Overview): Use existing MarketOverviewPage content
- [ ] Tab 2 (Screener): Migrate ScreenerPage content
- [ ] Tab 3 (Heat Map): Create placeholder (enhanced in Phase 3)
- [ ] Tab 4 (Movers): Create expanded movers view
- [ ] Tab 5 (Sectors): Create expanded sectors view
- [ ] Test all tabs load correctly
- [ ] Verify data fetching works in each tab

### Phase 2E: State & Routing (2 hours)
- [ ] URL synchronization for tab selection
- [ ] localStorage for UI preferences
- [ ] Inter-tab navigation (e.g., heatmap → screener)
- [ ] Browser back/forward button support
- [ ] Deep linking support
- [ ] Test all navigation flows

### Phase 2F: Testing & Polish (2 hours)
- [ ] Mobile responsiveness testing
- [ ] Keyboard navigation testing
- [ ] Visual regression tests
- [ ] Performance testing (tab switching speed)
- [ ] Update documentation
- [ ] User acceptance testing

## Acceptance Criteria

- [x] **Unified Dashboard**
  - [ ] `/market` route shows tabbed dashboard
  - [ ] 5 tabs present and functional
  - [ ] Tab switching is instant (< 100ms)
  - [ ] Active tab highlighted visually
  - [ ] No full page reloads on tab switch

- [x] **Sticky Navigation**
  - [ ] GlobalMarketBar stays at top (z-50)
  - [ ] Tab bar stays below market bar (z-40)
  - [ ] Filter panel sticky in Screener tab (z-30)
  - [ ] Table headers sticky in all table views (z-20)
  - [ ] No z-index conflicts or overlaps

- [x] **Multi-Column Layouts**
  - [ ] Market indices in 3-column grid
  - [ ] Movers in split view (gainers | losers)
  - [ ] Filter panel collapsible with smooth animation
  - [ ] Results table uses full width when filters collapsed
  - [ ] All layouts responsive on mobile

- [x] **URL & State**
  - [ ] URL reflects active tab (`?tab=screener`)
  - [ ] Browser back/forward buttons work
  - [ ] Last tab restored on page reload
  - [ ] Deep links work (e.g., `/market?tab=movers`)
  - [ ] Filter panel state persisted

- [x] **Performance**
  - [ ] Tab switch < 100ms (perceived instant)
  - [ ] No layout shifts on scroll
  - [ ] Lighthouse Performance ≥ 90
  - [ ] Bundle size increase < 20KB

- [x] **Testing**
  - [ ] All existing tests pass
  - [ ] New tests for tab switching
  - [ ] Mobile tests (iOS/Android)
  - [ ] Keyboard navigation tests

## Performance Targets
- **Navigation Speed**: -60% clicks to reach target (measurable via analytics)
- **Tab Switch Time**: < 100ms (React Profiler)
- **Vertical Scrolling**: -50% scroll distance for common tasks
- **User Efficiency**: -40% time to complete screening workflow

## Technical Considerations

### Component Architecture
```
frontend/src/
├── pages/
│   ├── MarketDashboardPage.tsx      # NEW: Unified dashboard
│   ├── MarketOverviewPage.tsx       # DEPRECATED (content moved)
│   └── ScreenerPage.tsx             # DEPRECATED (content moved)
├── components/
│   ├── market/
│   │   ├── tabs/
│   │   │   ├── OverviewTab.tsx      # NEW: Tab 1 content
│   │   │   ├── ScreenerTab.tsx      # NEW: Tab 2 content
│   │   │   ├── HeatMapTab.tsx       # NEW: Tab 3 content
│   │   │   ├── MoversTab.tsx        # NEW: Tab 4 content
│   │   │   └── SectorsTab.tsx       # NEW: Tab 5 content
│   │   └── ...
│   └── screener/
│       └── FilterPanelCollapsible.tsx  # NEW: Collapsible filter panel
└── hooks/
    └── useTabState.ts               # NEW: Tab state management
```

### Libraries
- **Radix UI Tabs**: Accessible, unstyled tabs component
- **React Router**: URL synchronization
- **Zustand** (optional): Global UI state if needed

### Breaking Changes
- Old routes `/market-overview` and `/screener` redirect to `/market?tab=overview` and `/market?tab=screener`
- Navigation menu updated to point to unified dashboard
- Maintain backward compatibility for 2 releases

### Mobile Considerations
- Tabs become dropdown on < 768px
- Filter panel becomes full-screen drawer
- Tables become horizontally scrollable
- Touch-friendly targets (min 44px)

## Dependencies
- ✅ IMPROVEMENT-002 (Global UI/UX Foundation)
- ✅ Radix UI Tabs (install: `npm install @radix-ui/react-tabs`)
- ✅ Existing market APIs

## Testing Strategy

### Unit Tests
- Tab switching logic
- URL synchronization
- State persistence

### Integration Tests
- Navigation flows
- Inter-tab communication
- Filter panel collapse/expand

### E2E Tests
- Complete user workflows
- Browser back/forward
- Mobile drawer interactions

### Performance Tests
- Tab switch time measurement
- Scroll performance
- Bundle size analysis

## Rollout Plan
1. **Development**: Feature branch with tab dashboard
2. **Staging**: Team testing and feedback
3. **A/B Test**: 10% users see unified dashboard
4. **Gradual Rollout**: 25% → 50% → 100% over 1 week
5. **Deprecation**: Remove old pages after 2 releases

## Success Metrics
- [ ] -60% average clicks to complete task (analytics)
- [ ] +50% time spent on market analysis (engagement)
- [ ] -70% context switching friction (user survey)
- [ ] +30% mobile user retention
- [ ] 0 new bugs or regressions

## References
- [UI/UX Improvements Document](../../improvements/finviz-inspired-ui-improvements.md)
- [Radix UI Tabs](https://www.radix-ui.com/docs/primitives/components/tabs)
- [Finviz Navigation Patterns](https://finviz.com)

## Progress
**Current Status**: 0% (Not Started)

**Completion Checklist**:
- [ ] Phase 2A: Dashboard Structure (0/8 tasks)
- [ ] Phase 2B: Sticky Navigation (0/7 tasks)
- [ ] Phase 2C: Multi-Column Layouts (0/5 tasks)
- [ ] Phase 2D: Tab Content (0/7 tasks)
- [ ] Phase 2E: State & Routing (0/6 tasks)
- [ ] Phase 2F: Testing (0/6 tasks)

**Total**: 0/39 subtasks completed

## Notes
- This ticket unblocks IMPROVEMENT-004 (Advanced Features)
- User feedback from Phase 1 will inform tab priorities
- Consider feature flag for gradual rollout
- Heat map tab enhanced in IMPROVEMENT-004
- Monitor analytics to validate navigation improvements
