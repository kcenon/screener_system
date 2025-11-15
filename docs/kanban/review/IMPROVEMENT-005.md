# IMPROVEMENT-005: Implement Dark Mode Theme System

## Metadata
- **Type**: Feature / UI Enhancement
- **Priority**: P0 (Critical)
- **Status**: IN_PROGRESS
- **Created**: 2025-11-15
- **Updated**: 2025-11-15
- **Parent**: UI/UX Improvement Proposal
- **Estimated Time**: 40 hours
- **Actual Time**: 3 hours (Phase 1 & 2)
- **Progress**: Phase 1 & 2 Complete (40% done)
- **Labels**: frontend, ui, dark-mode, theme
- **Branch**: feature/improvement-005-dark-mode
- **Commits**: 2 (139919f, e8d847f)

## Problem Statement

The current platform only supports light mode, which:
- Feels dated compared to modern trading platforms (Finviz, Bloomberg, Robinhood all have dark mode)
- Causes eye strain during extended use
- Doesn't meet user expectations (60%+ of users prefer dark mode)
- Lacks professional polish

## Proposed Solution

Implement a complete dark mode theme system with:
1. System preference detection
2. Manual theme toggle in navbar
3. Persistent theme selection (localStorage)
4. Smooth transition animations
5. Dark-optimized chart colors
6. Both light and dark theme tokens

## Technical Implementation

### Step 1: Create Theme Configuration

**File**: `src/config/theme.ts`

```typescript
export const lightTheme = {
  // Backgrounds
  background: {
    primary: 'bg-white',
    secondary: 'bg-gray-50',
    tertiary: 'bg-gray-100',
  },
  // Surfaces (cards, panels)
  surface: {
    primary: 'bg-white',
    elevated: 'bg-white',
    overlay: 'bg-white/95',
  },
  // Text
  text: {
    primary: 'text-gray-900',
    secondary: 'text-gray-600',
    tertiary: 'text-gray-500',
    inverse: 'text-white',
  },
  // Borders
  border: {
    default: 'border-gray-200',
    strong: 'border-gray-300',
    subtle: 'border-gray-100',
  },
  // Market colors (keep same for both themes)
  market: {
    gain: 'text-green-600',
    loss: 'text-red-600',
    neutral: 'text-gray-600',
  },
}

export const darkTheme = {
  background: {
    primary: 'bg-gray-900',
    secondary: 'bg-gray-800',
    tertiary: 'bg-gray-700',
  },
  surface: {
    primary: 'bg-gray-800',
    elevated: 'bg-gray-750', // Custom color
    overlay: 'bg-gray-800/95',
  },
  text: {
    primary: 'text-gray-100',
    secondary: 'text-gray-400',
    tertiary: 'text-gray-500',
    inverse: 'text-gray-900',
  },
  border: {
    default: 'border-gray-700',
    strong: 'border-gray-600',
    subtle: 'border-gray-800',
  },
  market: {
    gain: 'text-green-400', // Brighter for dark background
    loss: 'text-red-400',
    neutral: 'text-gray-400',
  },
}
```

### Step 2: Create Theme Hook

**File**: `src/hooks/useTheme.ts`

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type Theme = 'light' | 'dark' | 'system'

interface ThemeStore {
  theme: Theme
  resolvedTheme: 'light' | 'dark'
  setTheme: (theme: Theme) => void
}

export const useTheme = create<ThemeStore>()(
  persist(
    (set, get) => ({
      theme: 'system',
      resolvedTheme: 'light',

      setTheme: (theme) => {
        set({ theme })

        // Resolve actual theme
        const resolved = theme === 'system'
          ? window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light'
          : theme

        set({ resolvedTheme: resolved })

        // Apply to DOM
        document.documentElement.classList.remove('light', 'dark')
        document.documentElement.classList.add(resolved)
      },
    }),
    {
      name: 'theme-preference',
    }
  )
)
```

### Step 3: Theme Toggle Component

**File**: `src/components/common/ThemeToggle.tsx`

```typescript
import { Moon, Sun, Monitor } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <div className="flex items-center gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg">
      <button
        onClick={() => setTheme('light')}
        className={`p-2 rounded ${theme === 'light' ? 'bg-white dark:bg-gray-700 shadow' : ''}`}
        aria-label="Light mode"
      >
        <Sun className="w-4 h-4" />
      </button>
      <button
        onClick={() => setTheme('system')}
        className={`p-2 rounded ${theme === 'system' ? 'bg-white dark:bg-gray-700 shadow' : ''}`}
        aria-label="System theme"
      >
        <Monitor className="w-4 h-4" />
      </button>
      <button
        onClick={() => setTheme('dark')}
        className={`p-2 rounded ${theme === 'dark' ? 'bg-white dark:bg-gray-700 shadow' : ''}`}
        aria-label="Dark mode"
      >
        <Moon className="w-4 h-4" />
      </button>
    </div>
  )
}
```

### Step 4: Update Tailwind Config

**File**: `tailwind.config.js`

```javascript
module.exports = {
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        gray: {
          750: '#2d3748', // Custom gray for elevated surfaces
        },
      },
    },
  },
}
```

### Step 5: Chart Color Adaptation

**File**: `src/components/charts/PriceChart.tsx`

```typescript
const chartColors = {
  light: {
    upColor: '#10B981',
    downColor: '#EF4444',
    backgroundColor: '#FFFFFF',
    textColor: '#111827',
    gridColor: '#E5E7EB',
  },
  dark: {
    upColor: '#34D399', // Brighter green
    downColor: '#F87171', // Brighter red
    backgroundColor: '#1F2937',
    textColor: '#F3F4F6',
    gridColor: '#374151',
  },
}

// Apply theme-specific colors
chart.applyOptions({
  layout: {
    background: { color: chartColors[resolvedTheme].backgroundColor },
    textColor: chartColors[resolvedTheme].textColor,
  },
  grid: {
    vertLines: { color: chartColors[resolvedTheme].gridColor },
    horzLines: { color: chartColors[resolvedTheme].gridColor },
  },
})
```

## Component Updates Required

### Components to Update with Dark Mode Classes

1. **Navigation Components** (`src/components/navigation/`)
   - [ ] Navbar.tsx
   - [ ] NavMenu.tsx
   - [ ] MobileMenu.tsx
   - [ ] Breadcrumb.tsx

2. **Layout Components** (`src/components/layout/`)
   - [ ] GlobalMarketBar.tsx

3. **Screener Components** (`src/components/screener/`)
   - [ ] FilterPanel.tsx
   - [ ] ResultsTable.tsx
   - [ ] QuickFiltersBar.tsx

4. **Landing Components** (`src/components/landing/`)
   - [ ] HeroSection.tsx
   - [ ] MarketSummary.tsx
   - [ ] FeatureShowcase.tsx
   - [ ] Footer.tsx

5. **Chart Components** (`src/components/charts/`)
   - [ ] PriceChart.tsx
   - [ ] ComparisonCharts.tsx
   - [ ] SectorHeatmap.tsx

6. **Common Components** (`src/components/common/`)
   - [ ] Card.tsx
   - [ ] Modal.tsx
   - [ ] Table.tsx
   - [ ] Button.tsx (if exists)

## Testing Checklist

### Functional Tests
- [ ] Theme persists after page reload
- [ ] System preference detection works correctly
- [ ] Manual theme toggle works for all 3 modes (light/dark/system)
- [ ] Theme changes update all components instantly
- [ ] No flash of unstyled content (FOUC)

### Visual Tests
- [ ] All text is readable in both themes
- [ ] Market colors (green/red) have sufficient contrast
- [ ] Charts render correctly in both themes
- [ ] Hover states work in both themes
- [ ] Focus indicators visible in both themes
- [ ] No white flashes during theme transition

### Cross-Browser Tests
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Accessibility Tests
- [ ] Color contrast ratios meet WCAG AA (4.5:1 for text)
- [ ] Theme toggle is keyboard accessible
- [ ] Screen reader announces theme changes
- [ ] High contrast mode compatible

## Success Criteria

- [ ] Dark mode toggle visible in navbar
- [ ] Theme preference persists across sessions
- [ ] All 50+ components render correctly in dark mode
- [ ] Charts adapt colors for dark background
- [ ] No visual regressions in light mode
- [ ] Performance impact < 50ms for theme switch
- [ ] User preference saved to localStorage

## Performance Considerations

- Use CSS classes instead of inline styles (faster)
- Minimize re-renders (only update necessary components)
- Lazy load theme assets
- Use `prefers-color-scheme` media query for initial state

## Migration Path

1. Phase 1: Core theme infrastructure (hooks, store)
2. Phase 2: Update layout and navigation components
3. Phase 3: Update page components
4. Phase 4: Update charts and visualizations
5. Phase 5: Final polish and testing

## Related Issues

- UI/UX Improvement Proposal (parent document)
- Color system enhancement (IMPROVEMENT-006)

## References

- [TailwindCSS Dark Mode](https://tailwindcss.com/docs/dark-mode)
- [Next.js Themes](https://github.com/pacocoursey/next-themes)
- [Zustand Persist](https://docs.pmnd.rs/zustand/integrations/persisting-store-data)

---

## Progress Summary

### Phase 1: Core Infrastructure ✅ COMPLETE
**Completed**: 2025-11-15
**Commit**: 139919f

- [x] Extended `theme.ts` with `lightTheme` and `darkTheme` configurations
- [x] Created `useTheme` hook with Zustand
  - System preference detection via `matchMedia`
  - Manual theme override (light/dark/system)
  - Persistent storage in localStorage
  - Automatic DOM class updates
- [x] Created `ThemeToggle` component
  - Three-button layout (Sun/Monitor/Moon icons)
  - Visual feedback for current selection
  - Keyboard accessible with aria-labels
- [x] Enabled Tailwind `darkMode: 'class'`
  - Added custom `gray-750` color
- [x] Initialized theme in `App.tsx`
- [x] Integrated `ThemeToggle` into `Navbar`

**Tests Passed**:
- TypeScript type check: ✅
- Production build: ✅ (1.95s)

---

### Phase 2: Layout & Navigation ✅ COMPLETE
**Completed**: 2025-11-15
**Commit**: e8d847f

- [x] Updated `NavLink` component
  - Active state: `blue-900/30` bg, `blue-400` text
  - Hover state: `gray-700` bg, `white` text
- [x] Updated `MobileMenu` component
  - Hamburger button with dark mode hover
  - Dark backdrop (`bg-opacity-70`)
  - Menu panel: `gray-800` background
  - All navigation links with proper contrast
  - User section with adjusted colors
- [x] Updated `Breadcrumb` component
  - `gray-800` background, `gray-700` border
  - Chevron and link colors for readability
- [x] Updated `GlobalMarketBar` component
  - `gray-800` background with `gray-700` border
  - Market indices with proper text contrast
  - Sentiment indicators remain vibrant
  - Time display with `gray-400` text

**Common Patterns Applied**:
- `transition-colors` for smooth theme switching
- Proper WCAG contrast ratios
- Consistent color palette usage

**Tests Passed**:
- TypeScript type check: ✅

---

### Phase 3: Page Components 🚧 TODO
**Status**: Not started
**Components to Update**: ~20 page components

Components in scope:
- Landing page components (HeroSection, MarketSummary, FeatureShowcase, Footer)
- Screener components (FilterPanel, ResultsTable, QuickFiltersBar)
- Dashboard components
- Stock detail page components
- Comparison page components

---

### Phase 4: Charts & Visualizations 🚧 TODO
**Status**: Not started
**Components to Update**: Chart components

Components in scope:
- PriceChart
- ComparisonCharts
- SectorHeatmap

**Special Considerations**:
- Chart colors need dark-optimized palettes
- Background colors for chart canvas
- Grid line colors
- Text label colors

---

### Phase 5: Final Polish & Testing 🚧 TODO
**Status**: Not started

Tasks:
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Accessibility audit (WCAG AA compliance)
- [ ] Performance testing (theme switch < 50ms)
- [ ] Visual regression testing
- [ ] Documentation update
- [ ] User acceptance testing

---

## Next Steps

1. **Continue with Phase 3** (Page Components)
   - Start with landing page for maximum user impact
   - Then screener components (most used feature)

2. **Create incremental PRs**
   - Phase 1 & 2: Ready for review (this PR)
   - Phase 3: Separate PR for page components
   - Phase 4 & 5: Final PR with charts and polish

3. **Consider breaking IMPROVEMENT-006**
   - Color system enhancement depends on this ticket
   - Can start color system work once Phase 1 & 2 are merged
