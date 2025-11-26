# BUGFIX-014: Complete Freemium Integration for Stock Detail Pages (FE-012)

## Metadata

- **Status**: TODO
- **Priority**: High
- **Assignee**: TBD
- **Estimated Time**: 3 hours
- **Sprint**: Post-MVP
- **Tags**: frontend, freemium, stock-detail, feature-gating

## Description

FE-012 (Freemium Access Model) was implemented with full infrastructure (components, hooks, utilities), but the Stock Detail pages were never integrated with the freemium system. This means public users can access ALL stock data including Financials and Technical indicators, bypassing the intended tier restrictions.

### Current State (40% Complete)
- **Implemented**: FreemiumBanner, LockedContent, LimitReachedModal components
- **Implemented**: useFreemiumAccess hook with tier logic
- **Implemented**: usageTracker utility with localStorage
- **Implemented**: ScreenerPage freemium integration
- **NOT Implemented**: StockDetailPage freemium integration
- **NOT Implemented**: FinancialsTab, TechnicalTab, ValuationTab gating

### Business Impact
- Public users can view premium content without restrictions
- No upgrade prompts on stock detail pages
- Revenue leakage from ungated premium features
- Inconsistent user experience (screener has limits, stock detail doesn't)

## Subtasks

### Phase 1: StockDetailPage Integration (1h)
- [ ] Import `useFreemiumAccess` hook in StockDetailPage.tsx
- [ ] Pass freemium limits to StockTabs component
- [ ] Add FreemiumBanner for unauthenticated users
- [ ] Track page views for usage limiting

### Phase 2: Tab Content Gating (1.5h)
- [ ] Gate FinancialsTab with `canViewFinancials` check
- [ ] Gate TechnicalTab with `canViewAllTechnicals` check
- [ ] Use `<LockedContent>` component for locked tabs
- [ ] Show upgrade prompt with feature description
- [ ] Ensure smooth UX transition between tabs

### Phase 3: Testing & Polish (0.5h)
- [ ] Test public user sees locked content
- [ ] Test free user sees all content
- [ ] Test premium indicators (if applicable)
- [ ] Verify mobile responsive behavior
- [ ] Update FE-012.md to mark Stock Detail as complete

## Acceptance Criteria

### Functionality
- [ ] Public users see LockedContent on Financials tab
- [ ] Public users see limited indicators on Technical tab
- [ ] Free/authenticated users see all content
- [ ] FreemiumBanner displays on Stock Detail for public users
- [ ] Upgrade prompts are clear and actionable

### UX
- [ ] Locked content shows descriptive message
- [ ] Tab switching is smooth (no layout shift)
- [ ] Mobile responsive design maintained
- [ ] Consistent with Screener page freemium UX

### Technical
- [ ] No TypeScript errors
- [ ] No console warnings
- [ ] useFreemiumAccess hook reused (no duplication)

## Dependencies

- **Depends On**: FE-012 (Partially complete - infrastructure done)
- **Blocks**: None

## References

- FE-012.md - Original freemium ticket
- `/frontend/src/components/freemium/` - Freemium components
- `/frontend/src/hooks/useFreemiumAccess.ts` - Access control hook
- `/frontend/src/pages/StockDetailPage.tsx` - Target page
- `/frontend/src/pages/ScreenerPage.tsx` - Reference implementation

## Implementation Pattern

```tsx
// Example implementation for StockDetailPage
import { useFreemiumAccess } from '@/hooks/useFreemiumAccess';
import { FreemiumBanner, LockedContent } from '@/components/freemium';

const StockDetailPage = () => {
  const { canViewFinancials, canViewAllTechnicals, isAuthenticated } = useFreemiumAccess();

  return (
    <>
      {!isAuthenticated && <FreemiumBanner pageType="stock-detail" />}
      <StockTabs
        canViewFinancials={canViewFinancials}
        canViewAllTechnicals={canViewAllTechnicals}
      />
    </>
  );
};

// In StockTabs component
<Tabs.Content value="financials">
  {canViewFinancials ? (
    <FinancialsTab stock={stock} />
  ) : (
    <LockedContent
      feature="Financial Statements"
      description="View income statements, balance sheets, and cash flow"
    />
  )}
</Tabs.Content>
```

## Progress

**0%** - Not started

## Notes

- All freemium components already exist and are tested
- ScreenerPage provides reference implementation pattern
- Estimated 2-3 hours to complete based on infrastructure readiness
- Consider A/B testing upgrade prompt variations
