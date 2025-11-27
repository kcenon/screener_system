# IMPROVEMENT-012: Implement Code Splitting for Large Bundle Optimization

## Metadata
- **Status**: TODO
- **Priority**: Low
- **Assignee**: TBD
- **Estimated Time**: 4-6 hours
- **Sprint**: Phase 5 (Performance)
- **Tags**: frontend, performance, optimization, bundle-size

## Description

The production build generates large JavaScript bundles that exceed the recommended 500KB limit. This affects initial page load time and user experience, especially on slower connections.

**Current Bundle Sizes:**
| File | Size | Gzipped |
|------|------|---------|
| index.js | 1,073.64 KB | 304.76 KB |
| charts.js | 573.70 KB | 169.54 KB |
| vendor.js | 225.32 KB | 73.98 KB |

**Build Warning:**
```
Some chunks are larger than 500 kB after minification. Consider:
- Using dynamic import() to code-split the application
- Use build.rollupOptions.output.manualChunks to improve chunking
```

## Subtasks

- [ ] Analyze bundle composition with `vite-bundle-analyzer`
- [ ] Identify lazy-loadable routes and components
- [ ] Implement route-based code splitting with React.lazy()
- [ ] Implement component-based code splitting for heavy components
- [ ] Configure manual chunks in Vite for vendor libraries
- [ ] Split chart libraries (Recharts, Lightweight Charts) into separate chunks
- [ ] Add loading states/suspense boundaries for lazy components
- [ ] Verify all routes still function correctly
- [ ] Measure and document performance improvements
- [ ] Update build configuration

## Acceptance Criteria

1. No single chunk exceeds 500KB after minification
2. Initial page load time improved by at least 20%
3. All lazy-loaded routes display appropriate loading states
4. No functionality regression
5. Lighthouse performance score maintained or improved
6. Build warning resolved

## Technical Details

### Route-Based Code Splitting

```typescript
// Before
import { ScreenerPage } from './pages/ScreenerPage';
import { PortfolioListPage } from './pages/PortfolioListPage';

// After
import { lazy, Suspense } from 'react';

const ScreenerPage = lazy(() => import('./pages/ScreenerPage'));
const PortfolioListPage = lazy(() => import('./pages/PortfolioListPage'));
const StockDetailPage = lazy(() => import('./pages/StockDetailPage'));
const StockComparisonPage = lazy(() => import('./pages/StockComparisonPage'));

// Usage with Suspense
<Suspense fallback={<PageLoader />}>
  <Routes>
    <Route path="/screener" element={<ScreenerPage />} />
    <Route path="/portfolio" element={<PortfolioListPage />} />
  </Routes>
</Suspense>
```

### Manual Chunks Configuration (vite.config.ts)

```typescript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-query': ['@tanstack/react-query'],
          'vendor-charts': ['recharts', 'lightweight-charts'],
          'vendor-ui': ['@radix-ui/react-dialog', '@radix-ui/react-select'],
          'vendor-i18n': ['i18next', 'react-i18next'],
        },
      },
    },
  },
});
```

### Heavy Components to Lazy Load

1. `AdvancedChart` - Lightweight Charts integration
2. `SectorHeatmap` - Complex visualization
3. `PortfolioCharts` - Recharts components
4. `OrderBook` - Real-time data visualization
5. `StockComparisonPage` - Heavy comparison logic

## Dependencies
- None

## Blocks
- None

## Progress
- [ ] 0% - Not started

## Notes
- Consider prefetching critical routes on hover for better UX
- Use named exports for better tree-shaking
- Monitor bundle size in CI/CD to prevent regression
- Target: Main bundle < 300KB gzipped

## Expected Impact
- **Initial Load Time**: -30% to -40%
- **Time to Interactive**: -25%
- **Lighthouse Performance**: +5-10 points
