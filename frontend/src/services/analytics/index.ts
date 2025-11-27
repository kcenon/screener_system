/**
 * Analytics Module
 *
 * Provides user tracking, event analytics, and A/B testing functionality.
 *
 * @module analytics
 */

// Main service
export { analytics } from './analyticsService'

// Types and events
export { AnalyticsEvents } from './types'
export type {
  AnalyticsConfig,
  AnalyticsEvent,
  BaseEventProperties,
  ErrorProperties,
  EventProperties,
  ExperimentProperties,
  ExportProperties,
  FilterAppliedProperties,
  PageViewProperties,
  PerformanceProperties,
  PrivacySettings,
  SearchPerformedProperties,
  StockViewedProperties,
  UpgradeCTAProperties,
  UserTraits,
} from './types'

// Experiments (A/B testing)
export {
  experiments,
  COMPACT_TABLE_EXPERIMENT,
  SIMPLIFIED_FILTERS_EXPERIMENT,
  CTA_COLOR_EXPERIMENT,
  ONBOARDING_FLOW_EXPERIMENT,
  type Experiment,
} from './experiments'
