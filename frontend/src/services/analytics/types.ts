/**
 * Analytics Event and Type Definitions
 *
 * This module defines all tracked events and their property schemas.
 * Events are organized by category for easier maintenance.
 */

// ============================================================================
// Event Names
// ============================================================================

/**
 * Core analytics events organized by category
 */
export const AnalyticsEvents = {
  // Authentication Events
  USER_SIGNED_UP: 'User Signed Up',
  USER_LOGGED_IN: 'User Logged In',
  USER_LOGGED_OUT: 'User Logged Out',
  USER_VERIFIED_EMAIL: 'User Verified Email',
  PASSWORD_RESET_REQUESTED: 'Password Reset Requested',
  OAUTH_LOGIN_INITIATED: 'OAuth Login Initiated',
  OAUTH_LOGIN_COMPLETED: 'OAuth Login Completed',

  // Navigation Events
  PAGE_VIEWED: 'Page Viewed',
  TAB_SWITCHED: 'Tab Switched',
  MODAL_OPENED: 'Modal Opened',
  MODAL_CLOSED: 'Modal Closed',

  // Screener Events
  FILTER_APPLIED: 'Filter Applied',
  FILTER_CLEARED: 'Filter Cleared',
  FILTER_PRESET_SAVED: 'Filter Preset Saved',
  FILTER_PRESET_LOADED: 'Filter Preset Loaded',
  QUICK_FILTER_USED: 'Quick Filter Used',
  RESULTS_SORTED: 'Results Sorted',
  RESULTS_EXPORTED: 'Results Exported',
  RESULTS_PAGINATED: 'Results Paginated',

  // Stock Events
  STOCK_VIEWED: 'Stock Viewed',
  STOCK_SEARCHED: 'Stock Searched',
  STOCK_COMPARED: 'Stock Compared',
  CHART_INTERACTED: 'Chart Interacted',
  INDICATOR_ADDED: 'Indicator Added',
  INDICATOR_REMOVED: 'Indicator Removed',
  TIMEFRAME_CHANGED: 'Timeframe Changed',

  // Watchlist Events
  WATCHLIST_CREATED: 'Watchlist Created',
  STOCK_ADDED_TO_WATCHLIST: 'Stock Added to Watchlist',
  STOCK_REMOVED_FROM_WATCHLIST: 'Stock Removed from Watchlist',
  WATCHLIST_SHARED: 'Watchlist Shared',

  // Portfolio Events
  PORTFOLIO_CREATED: 'Portfolio Created',
  PORTFOLIO_UPDATED: 'Portfolio Updated',
  HOLDING_ADDED: 'Holding Added',
  HOLDING_REMOVED: 'Holding Removed',
  TRANSACTION_RECORDED: 'Transaction Recorded',
  PORTFOLIO_EXPORTED: 'Portfolio Exported',

  // Alert Events
  ALERT_CREATED: 'Alert Created',
  ALERT_TRIGGERED: 'Alert Triggered',
  ALERT_DELETED: 'Alert Deleted',
  NOTIFICATION_CLICKED: 'Notification Clicked',
  NOTIFICATION_DISMISSED: 'Notification Dismissed',

  // Conversion Events
  UPGRADE_CTA_CLICKED: 'Upgrade CTA Clicked',
  PRICING_VIEWED: 'Pricing Viewed',
  SUBSCRIPTION_STARTED: 'Subscription Started',
  SUBSCRIPTION_CANCELLED: 'Subscription Cancelled',
  TRIAL_STARTED: 'Trial Started',
  TRIAL_CONVERTED: 'Trial Converted',
  FEATURE_LIMIT_REACHED: 'Feature Limit Reached',

  // Engagement Events
  SEARCH_PERFORMED: 'Search Performed',
  SHARE_CLICKED: 'Share Clicked',
  FEEDBACK_SUBMITTED: 'Feedback Submitted',
  HELP_ACCESSED: 'Help Accessed',
  THEME_CHANGED: 'Theme Changed',
  LANGUAGE_CHANGED: 'Language Changed',

  // Performance Events
  PAGE_LOAD_TIME: 'Page Load Time',
  API_LATENCY: 'API Latency',
  ERROR_OCCURRED: 'Error Occurred',

  // Experiment Events
  EXPERIMENT_ASSIGNED: 'Experiment Assigned',
  EXPERIMENT_CONVERTED: 'Experiment Converted',
} as const

export type AnalyticsEvent =
  (typeof AnalyticsEvents)[keyof typeof AnalyticsEvents]

// ============================================================================
// Event Property Types
// ============================================================================

/**
 * Base properties included with every event
 */
export interface BaseEventProperties {
  timestamp: string
  path: string
  referrer?: string
  session_id?: string
  user_tier?: 'public' | 'free' | 'premium' | 'pro'
  /** Allow additional properties */
  [key: string]: unknown
}

/**
 * User traits for identification
 */
export interface UserTraits {
  email?: string
  name?: string
  tier?: 'free' | 'premium' | 'pro'
  created_at?: string
  email_verified?: boolean
  oauth_provider?: string
  preferred_language?: string
  /** Allow additional properties */
  [key: string]: unknown
}

/**
 * Page view event properties
 */
export interface PageViewProperties extends BaseEventProperties {
  page_name: string
  page_title?: string
  query_params?: Record<string, string>
}

/**
 * Filter applied event properties
 */
export interface FilterAppliedProperties extends BaseEventProperties {
  filter_type: string
  filter_value: string | number | boolean
  filters_count: number
  results_count?: number
}

/**
 * Stock viewed event properties
 */
export interface StockViewedProperties extends BaseEventProperties {
  stock_code: string
  stock_name: string
  source: 'screener' | 'search' | 'watchlist' | 'portfolio' | 'direct' | 'alert'
  market?: string
}

/**
 * Search performed event properties
 */
export interface SearchPerformedProperties extends BaseEventProperties {
  query: string
  results_count: number
  search_type: 'stock' | 'filter' | 'global'
  search_time_ms?: number
}

/**
 * Upgrade CTA clicked event properties
 */
export interface UpgradeCTAProperties extends BaseEventProperties {
  cta_location: string
  cta_text?: string
  feature_blocked?: string
  current_tier: 'public' | 'free' | 'premium'
}

/**
 * Export event properties
 */
export interface ExportProperties extends BaseEventProperties {
  export_format: 'csv' | 'json' | 'excel'
  items_count: number
  export_type: 'screener' | 'portfolio' | 'watchlist'
}

/**
 * Error event properties
 */
export interface ErrorProperties extends BaseEventProperties {
  error_type: string
  error_message: string
  error_code?: string
  component?: string
  action?: string
}

/**
 * Experiment assignment properties
 */
export interface ExperimentProperties extends BaseEventProperties {
  experiment_id: string
  experiment_name: string
  variant: string
  user_segment?: string
}

/**
 * Performance event properties
 */
export interface PerformanceProperties extends BaseEventProperties {
  metric_name: string
  metric_value: number
  metric_unit: 'ms' | 's' | 'bytes' | 'count'
}

// ============================================================================
// Analytics Configuration
// ============================================================================

/**
 * Analytics configuration options
 */
export interface AnalyticsConfig {
  /** Mixpanel project token */
  token: string
  /** Enable debug mode (logs events to console) */
  debug?: boolean
  /** Track pageviews automatically */
  trackPageviews?: boolean
  /** Persistence mechanism */
  persistence?: 'localStorage' | 'cookie' | 'none'
  /** Respect Do Not Track browser setting */
  respectDoNotTrack?: boolean
  /** Disable tracking entirely */
  disabled?: boolean
  /** API host for self-hosted or proxy */
  apiHost?: string
}

/**
 * Privacy settings for analytics
 */
export interface PrivacySettings {
  /** User has consented to analytics */
  analyticsConsent: boolean
  /** User has consented to marketing tracking */
  marketingConsent: boolean
  /** Timestamp of consent */
  consentTimestamp?: string
}

// ============================================================================
// Helper Types
// ============================================================================

/**
 * Generic event properties map
 */
export type EventPropertiesMap = {
  [AnalyticsEvents.PAGE_VIEWED]: PageViewProperties
  [AnalyticsEvents.FILTER_APPLIED]: FilterAppliedProperties
  [AnalyticsEvents.STOCK_VIEWED]: StockViewedProperties
  [AnalyticsEvents.SEARCH_PERFORMED]: SearchPerformedProperties
  [AnalyticsEvents.UPGRADE_CTA_CLICKED]: UpgradeCTAProperties
  [AnalyticsEvents.RESULTS_EXPORTED]: ExportProperties
  [AnalyticsEvents.ERROR_OCCURRED]: ErrorProperties
  [AnalyticsEvents.EXPERIMENT_ASSIGNED]: ExperimentProperties
  [AnalyticsEvents.PAGE_LOAD_TIME]: PerformanceProperties
  [AnalyticsEvents.API_LATENCY]: PerformanceProperties
  // Add more as needed, default to Record<string, unknown>
}

/**
 * Get the property type for a specific event
 */
export type EventProperties<E extends AnalyticsEvent> =
  E extends keyof EventPropertiesMap
    ? EventPropertiesMap[E]
    : BaseEventProperties & Record<string, unknown>
