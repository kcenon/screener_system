# [IMPROVEMENT-011] User Analytics & A/B Testing Infrastructure

## Metadata
- **Status**: TODO
- **Priority**: Medium
- **Assignee**: Frontend Team + DevOps
- **Estimated Time**: 10-12 hours
- **Sprint**: Phase 4 Enhancement
- **Tags**: #analytics #a-b-testing #tracking #metrics #optimization
- **Dependencies**: None
- **Blocks**: None
- **Related**: README.md Future Enhancements (Analytics)

## Description
Implement comprehensive user analytics and A/B testing infrastructure to enable data-driven product decisions. This includes event tracking, user journey analysis, conversion funnels, and a framework for running controlled experiments on new features.

## Problem Statement
Current limitations:
- ❌ **No User Tracking**: Cannot measure user engagement or behavior
- ❌ **Blind Feature Releases**: No way to test feature impact before full rollout
- ❌ **Missing Funnel Data**: Cannot identify conversion bottlenecks
- ❌ **No Segmentation**: Cannot analyze different user cohorts
- ❌ **Guesswork Optimization**: UI/UX decisions not backed by data

**Impact**: Making product decisions without data leads to ~40% feature misses

## Proposed Solution

### 1. Analytics Provider Integration (3 hours)
**Options**:
1. **Mixpanel** (Recommended) - Best for product analytics
2. **Amplitude** - Strong for retention analysis
3. **PostHog** (Self-hosted option) - Privacy-focused, open-source
4. **Google Analytics 4** - Basic, free tier

**Implementation with Mixpanel**:
```typescript
// frontend/src/services/analytics.ts
import mixpanel from 'mixpanel-browser'

class Analytics {
  private initialized = false

  init(token: string) {
    if (this.initialized) return
    mixpanel.init(token, {
      debug: process.env.NODE_ENV === 'development',
      track_pageview: true,
      persistence: 'localStorage',
    })
    this.initialized = true
  }

  identify(userId: string, traits?: Record<string, any>) {
    mixpanel.identify(userId)
    if (traits) mixpanel.people.set(traits)
  }

  track(event: string, properties?: Record<string, any>) {
    mixpanel.track(event, {
      ...properties,
      timestamp: new Date().toISOString(),
      path: window.location.pathname,
    })
  }

  page(name: string, properties?: Record<string, any>) {
    mixpanel.track('Page View', {
      page_name: name,
      ...properties,
    })
  }

  reset() {
    mixpanel.reset()
  }
}

export const analytics = new Analytics()
```

### 2. Event Tracking Schema (2 hours)
**Core Events**:
```typescript
// frontend/src/services/events.ts
export const Events = {
  // Authentication
  USER_SIGNED_UP: 'User Signed Up',
  USER_LOGGED_IN: 'User Logged In',
  USER_LOGGED_OUT: 'User Logged Out',

  // Navigation
  PAGE_VIEWED: 'Page Viewed',
  TAB_SWITCHED: 'Tab Switched',

  // Screener
  FILTER_APPLIED: 'Filter Applied',
  FILTER_CLEARED: 'Filter Cleared',
  QUICK_FILTER_USED: 'Quick Filter Used',
  RESULTS_SORTED: 'Results Sorted',
  RESULTS_EXPORTED: 'Results Exported',

  // Stock
  STOCK_VIEWED: 'Stock Viewed',
  STOCK_ADDED_TO_WATCHLIST: 'Stock Added to Watchlist',
  STOCK_REMOVED_FROM_WATCHLIST: 'Stock Removed from Watchlist',
  CHART_INTERACTED: 'Chart Interacted',
  INDICATOR_ADDED: 'Indicator Added',

  // Portfolio
  PORTFOLIO_CREATED: 'Portfolio Created',
  HOLDING_ADDED: 'Holding Added',
  TRANSACTION_RECORDED: 'Transaction Recorded',

  // Conversion
  UPGRADE_CTA_CLICKED: 'Upgrade CTA Clicked',
  SUBSCRIPTION_STARTED: 'Subscription Started',
  TRIAL_STARTED: 'Trial Started',

  // Engagement
  SEARCH_PERFORMED: 'Search Performed',
  ALERT_CREATED: 'Alert Created',
  NOTIFICATION_CLICKED: 'Notification Clicked',
} as const

// Event properties schema
interface FilterAppliedEvent {
  filter_type: string
  filter_value: string | number
  filters_count: number
  results_count: number
}

interface StockViewedEvent {
  stock_code: string
  stock_name: string
  source: 'screener' | 'search' | 'watchlist' | 'direct'
}
```

### 3. React Hooks for Tracking (2 hours)
**Analytics Hooks**:
```typescript
// frontend/src/hooks/useAnalytics.ts
import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { analytics, Events } from '@/services/analytics'

// Auto-track page views
export function usePageTracking() {
  const location = useLocation()

  useEffect(() => {
    analytics.page(location.pathname, {
      referrer: document.referrer,
      search: location.search,
    })
  }, [location])
}

// Track component render time
export function useRenderTracking(componentName: string) {
  useEffect(() => {
    const startTime = performance.now()

    return () => {
      const renderTime = performance.now() - startTime
      analytics.track('Component Rendered', {
        component: componentName,
        render_time_ms: Math.round(renderTime),
      })
    }
  }, [componentName])
}

// Track user interactions
export function useEventTracking() {
  return {
    trackFilter: (filterType: string, value: any) => {
      analytics.track(Events.FILTER_APPLIED, {
        filter_type: filterType,
        filter_value: value,
      })
    },
    trackStockView: (code: string, name: string, source: string) => {
      analytics.track(Events.STOCK_VIEWED, {
        stock_code: code,
        stock_name: name,
        source,
      })
    },
    trackConversion: (step: string) => {
      analytics.track(Events.UPGRADE_CTA_CLICKED, { step })
    },
  }
}
```

### 4. A/B Testing Framework (3 hours)
**Component**: `frontend/src/services/experiments.ts`

```typescript
// A/B Testing with feature flags
import { useEffect, useState } from 'react'

interface Experiment {
  id: string
  name: string
  variants: string[]
  weights?: number[]
}

class ExperimentService {
  private assignments: Map<string, string> = new Map()

  constructor() {
    // Load saved assignments
    const saved = localStorage.getItem('experiments')
    if (saved) {
      this.assignments = new Map(JSON.parse(saved))
    }
  }

  getVariant(experiment: Experiment): string {
    // Check for existing assignment
    if (this.assignments.has(experiment.id)) {
      return this.assignments.get(experiment.id)!
    }

    // Assign randomly based on weights
    const weights = experiment.weights || experiment.variants.map(() => 1 / experiment.variants.length)
    const random = Math.random()
    let cumulative = 0

    for (let i = 0; i < weights.length; i++) {
      cumulative += weights[i]
      if (random < cumulative) {
        const variant = experiment.variants[i]
        this.assignments.set(experiment.id, variant)
        this.save()

        // Track assignment
        analytics.track('Experiment Assigned', {
          experiment_id: experiment.id,
          experiment_name: experiment.name,
          variant,
        })

        return variant
      }
    }

    return experiment.variants[0]
  }

  private save() {
    localStorage.setItem('experiments', JSON.stringify([...this.assignments]))
  }
}

export const experiments = new ExperimentService()

// React hook for experiments
export function useExperiment(experiment: Experiment): string {
  const [variant, setVariant] = useState<string>(() =>
    experiments.getVariant(experiment)
  )

  return variant
}

// Example usage
const COMPACT_TABLE_EXPERIMENT: Experiment = {
  id: 'compact_table_v1',
  name: 'Compact Table Design',
  variants: ['control', 'compact'],
  weights: [0.5, 0.5],
}

// In component
function ResultsTable() {
  const variant = useExperiment(COMPACT_TABLE_EXPERIMENT)

  return variant === 'compact'
    ? <CompactTable />
    : <StandardTable />
}
```

### 5. Analytics Dashboard Integration (2 hours)
**Mixpanel Dashboard Setup**:
- User Engagement Dashboard
- Conversion Funnel
- Retention Analysis
- Feature Usage Heatmap

**Custom Events Dashboard**:
```typescript
// Key metrics to track
const DASHBOARDS = {
  engagement: {
    metrics: [
      'Daily Active Users (DAU)',
      'Weekly Active Users (WAU)',
      'Sessions per User',
      'Average Session Duration',
      'Pages per Session',
    ],
  },
  conversion: {
    funnels: [
      ['Page View', 'Sign Up', 'Email Verified', 'Premium Upgrade'],
      ['Screener View', 'Filter Applied', 'Stock Clicked', 'Watchlist Added'],
    ],
  },
  features: {
    metrics: [
      'Screener Usage Rate',
      'Portfolio Creation Rate',
      'Alert Setup Rate',
      'Export Feature Usage',
    ],
  },
}
```

## Subtasks

### Phase A: Analytics Setup (3 hours)
- [ ] Choose and sign up for analytics provider (Mixpanel recommended)
- [ ] Install analytics SDK
- [ ] Create analytics service singleton
- [ ] Implement identify/track/page methods
- [ ] Add analytics provider to App
- [ ] Configure environment variables
- [ ] Test in development mode

### Phase B: Event Schema & Tracking (2 hours)
- [ ] Define event taxonomy
- [ ] Create event constants and types
- [ ] Implement tracking hooks
- [ ] Add page view tracking
- [ ] Track core user actions (auth, navigation)
- [ ] Track screener events
- [ ] Track stock detail events
- [ ] Track conversion events

### Phase C: Component Integration (2 hours)
- [ ] Add tracking to Navbar
- [ ] Add tracking to Screener filters
- [ ] Add tracking to Results table
- [ ] Add tracking to Stock detail
- [ ] Add tracking to Auth forms
- [ ] Add tracking to Upgrade CTAs
- [ ] Verify events in analytics dashboard

### Phase D: A/B Testing (3 hours)
- [ ] Create experiment service
- [ ] Implement variant assignment logic
- [ ] Create useExperiment hook
- [ ] Set up experiment tracking
- [ ] Create first experiment (compact table)
- [ ] Add experiment assignment to analytics
- [ ] Document experiment creation process

### Phase E: Dashboards & Reporting (2 hours)
- [ ] Set up Mixpanel dashboards
- [ ] Create conversion funnel
- [ ] Create retention analysis
- [ ] Set up weekly email reports
- [ ] Document key metrics
- [ ] Train team on analytics usage

## Acceptance Criteria

- [ ] **Analytics**
  - [ ] All page views tracked
  - [ ] User identification working
  - [ ] Key events tracked accurately
  - [ ] Event properties captured correctly
  - [ ] No PII leakage in events

- [ ] **A/B Testing**
  - [ ] Variant assignment consistent per user
  - [ ] 50/50 split achieved statistically
  - [ ] Assignment persists across sessions
  - [ ] Conversion tracked per variant
  - [ ] Easy to create new experiments

- [ ] **Dashboard**
  - [ ] DAU/WAU/MAU visible
  - [ ] Conversion funnel accurate
  - [ ] Feature usage tracked
  - [ ] Real-time data available

- [ ] **Privacy**
  - [ ] Consent banner implemented (if required)
  - [ ] No personal data in events
  - [ ] User can opt out
  - [ ] GDPR compliant

## Technical Considerations

### Privacy & Consent
- Implement cookie consent banner (GDPR)
- Anonymize IP addresses
- Don't track PII (passwords, financial data)
- Provide opt-out mechanism

### Performance
- Load analytics SDK asynchronously
- Batch events (don't fire on every keystroke)
- Use requestIdleCallback for non-critical tracking

### Data Quality
- Validate event properties
- Use TypeScript for event schemas
- Monitor for tracking errors

## Dependencies
- 📦 `mixpanel-browser` ^2.47.0 (or chosen provider)
- ✅ No backend changes required for basic tracking

## Testing Strategy

### Unit Tests
- Analytics service methods
- Experiment assignment logic
- Event property validation

### Integration Tests
- Track events actually fire
- Experiment persistence
- Analytics initialization

### Manual Verification
- Check Mixpanel live view
- Verify funnel accuracy
- Test A/B assignment distribution

## Rollout Plan
1. **Development**: Set up analytics, add basic tracking
2. **Staging**: Full event tracking, verify in dashboard
3. **Production**: Enable with consent banner
4. **Iteration**: Add more events based on needs
5. **Experiments**: Start first A/B test after baseline

## Success Metrics
- [ ] 95% of key user actions tracked
- [ ] A/B tests can detect 5% lift with 80% power
- [ ] Dashboard used weekly by team
- [ ] Data-driven decisions increase by 50%

## Progress
**Current Status**: 0% (Not Started)

## Notes
- Start with Mixpanel free tier (1000 monthly tracked users)
- Consider PostHog for self-hosted option
- Don't over-track - focus on actionable events
- Create naming convention for experiments
- Document all tracked events in wiki

## References
- [Mixpanel Documentation](https://developer.mixpanel.com/)
- [A/B Testing Best Practices](https://www.optimizely.com/optimization-glossary/ab-testing/)
- [GDPR Analytics Compliance](https://gdpr.eu/cookies/)
