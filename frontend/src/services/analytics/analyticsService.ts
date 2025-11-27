/**
 * Analytics Service
 *
 * Provides a unified interface for tracking user events and behavior.
 * Uses Mixpanel as the default provider with support for mock mode in development.
 *
 * Features:
 * - User identification and trait management
 * - Event tracking with typed properties
 * - Automatic page view tracking
 * - Privacy-first design with consent management
 * - Development mode with console logging
 */

import mixpanel from 'mixpanel-browser'
import type {
  AnalyticsConfig,
  AnalyticsEvent,
  BaseEventProperties,
  PrivacySettings,
  UserTraits,
} from './types'
import { AnalyticsEvents } from './types'

// ============================================================================
// Constants
// ============================================================================

const CONSENT_STORAGE_KEY = 'analytics_consent'
const SESSION_ID_KEY = 'analytics_session_id'

/**
 * Properties that should never be tracked (PII protection)
 */
const PII_FIELDS = [
  'password',
  'creditCard',
  'ssn',
  'socialSecurityNumber',
  'cardNumber',
  'cvv',
  'pin',
]

// ============================================================================
// Analytics Service Class
// ============================================================================

class AnalyticsService {
  private initialized = false
  private config: AnalyticsConfig | null = null
  private sessionId: string | null = null
  private mockMode = false
  private consentGiven = false

  /**
   * Initialize the analytics service
   */
  init(config: AnalyticsConfig): void {
    if (this.initialized) {
      console.warn('[Analytics] Already initialized')
      return
    }

    this.config = config

    // Check if analytics should be disabled
    if (config.disabled) {
      console.info('[Analytics] Analytics disabled by configuration')
      this.mockMode = true
      this.initialized = true
      return
    }

    // Check for Do Not Track
    if (config.respectDoNotTrack && navigator.doNotTrack === '1') {
      console.info('[Analytics] Do Not Track enabled, using mock mode')
      this.mockMode = true
      this.initialized = true
      return
    }

    // Check for consent
    const consent = this.loadConsentSettings()
    this.consentGiven = consent.analyticsConsent

    // If no token provided, use mock mode
    if (!config.token || config.token === 'mock' || config.token === '') {
      console.info('[Analytics] No token provided, using mock mode')
      this.mockMode = true
      this.initialized = true
      return
    }

    try {
      // Initialize Mixpanel
      mixpanel.init(config.token, {
        debug: config.debug ?? false,
        track_pageview: false, // We handle this manually
        persistence: config.persistence === 'none' ? 'localStorage' : config.persistence,
        api_host: config.apiHost,
        ignore_dnt: !config.respectDoNotTrack,
        opt_out_tracking_by_default: !this.consentGiven,
      })

      this.initialized = true
      this.sessionId = this.getOrCreateSessionId()

      if (config.debug) {
        console.info('[Analytics] Initialized successfully', {
          token: config.token.substring(0, 8) + '...',
          debug: config.debug,
          consentGiven: this.consentGiven,
        })
      }
    } catch (error) {
      console.error('[Analytics] Failed to initialize Mixpanel:', error)
      this.mockMode = true
      this.initialized = true
    }
  }

  /**
   * Identify a user (call after login)
   */
  identify(userId: string, traits?: UserTraits): void {
    if (!this.canTrack()) return

    const sanitizedTraits = traits ? this.sanitizeProperties(traits) : undefined

    if (this.mockMode || this.config?.debug) {
      console.info('[Analytics] identify:', { userId, traits: sanitizedTraits })
    }

    if (!this.mockMode) {
      mixpanel.identify(userId)
      if (sanitizedTraits) {
        mixpanel.people.set(sanitizedTraits)
      }
    }
  }

  /**
   * Set user properties (super properties that persist across events)
   */
  setUserProperties(properties: Record<string, unknown>): void {
    if (!this.canTrack()) return

    const sanitized = this.sanitizeProperties(properties)

    if (this.mockMode || this.config?.debug) {
      console.info('[Analytics] setUserProperties:', sanitized)
    }

    if (!this.mockMode) {
      mixpanel.people.set(sanitized)
    }
  }

  /**
   * Track an event
   */
  track(event: AnalyticsEvent | string, properties?: Record<string, unknown>): void {
    if (!this.canTrack()) return

    const eventProperties = this.buildEventProperties(properties)

    if (this.mockMode || this.config?.debug) {
      console.info('[Analytics] track:', { event, properties: eventProperties })
    }

    if (!this.mockMode) {
      mixpanel.track(event, eventProperties)
    }
  }

  /**
   * Track a page view
   */
  page(pageName: string, properties?: Record<string, unknown>): void {
    if (!this.canTrack()) return

    const pageProperties = {
      page_name: pageName,
      page_title: document.title,
      ...this.buildEventProperties(properties),
    }

    if (this.mockMode || this.config?.debug) {
      console.info('[Analytics] page:', pageProperties)
    }

    if (!this.mockMode) {
      mixpanel.track(AnalyticsEvents.PAGE_VIEWED, pageProperties)
    }
  }

  /**
   * Track a timing event (for performance monitoring)
   */
  timing(category: string, variable: string, value: number, label?: string): void {
    if (!this.canTrack()) return

    const timingProperties = {
      timing_category: category,
      timing_variable: variable,
      timing_value: value,
      timing_label: label,
      ...this.buildEventProperties(),
    }

    if (this.mockMode || this.config?.debug) {
      console.info('[Analytics] timing:', timingProperties)
    }

    if (!this.mockMode) {
      mixpanel.track('Timing', timingProperties)
    }
  }

  /**
   * Reset user identity (call on logout)
   */
  reset(): void {
    if (this.mockMode || this.config?.debug) {
      console.info('[Analytics] reset')
    }

    if (!this.mockMode && this.initialized) {
      mixpanel.reset()
    }

    // Generate new session ID
    this.sessionId = this.generateSessionId()
    sessionStorage.setItem(SESSION_ID_KEY, this.sessionId)
  }

  /**
   * Opt in to tracking (after user consent)
   */
  optIn(): void {
    this.consentGiven = true
    this.saveConsentSettings({ analyticsConsent: true, marketingConsent: false })

    if (!this.mockMode && this.initialized) {
      mixpanel.opt_in_tracking()
    }

    if (this.config?.debug) {
      console.info('[Analytics] User opted in to tracking')
    }
  }

  /**
   * Opt out of tracking
   */
  optOut(): void {
    this.consentGiven = false
    this.saveConsentSettings({ analyticsConsent: false, marketingConsent: false })

    if (!this.mockMode && this.initialized) {
      mixpanel.opt_out_tracking()
    }

    if (this.config?.debug) {
      console.info('[Analytics] User opted out of tracking')
    }
  }

  /**
   * Check if user has consented to tracking
   */
  hasConsent(): boolean {
    return this.consentGiven
  }

  /**
   * Register super properties (included with every event)
   */
  registerSuperProperties(properties: Record<string, unknown>): void {
    if (!this.canTrack()) return

    const sanitized = this.sanitizeProperties(properties)

    if (this.mockMode || this.config?.debug) {
      console.info('[Analytics] registerSuperProperties:', sanitized)
    }

    if (!this.mockMode) {
      mixpanel.register(sanitized)
    }
  }

  /**
   * Track link click (useful for external links)
   */
  trackLink(element: HTMLElement, event: string, properties?: Record<string, unknown>): void {
    if (!this.canTrack()) return

    if (this.mockMode || this.config?.debug) {
      console.info('[Analytics] trackLink:', { event, properties })
    }

    if (!this.mockMode) {
      mixpanel.track_links(element, event, this.buildEventProperties(properties))
    }
  }

  /**
   * Increment a user property (for counters)
   */
  incrementUserProperty(property: string, value = 1): void {
    if (!this.canTrack()) return

    if (this.mockMode || this.config?.debug) {
      console.info('[Analytics] increment:', { property, value })
    }

    if (!this.mockMode) {
      mixpanel.people.increment(property, value)
    }
  }

  // ============================================================================
  // Private Methods
  // ============================================================================

  private canTrack(): boolean {
    if (!this.initialized) {
      console.warn('[Analytics] Not initialized. Call init() first.')
      return false
    }

    // In mock mode, we still "track" (log to console) but don't send to Mixpanel
    return true
  }

  private buildEventProperties(
    properties?: Record<string, unknown>,
  ): BaseEventProperties & Record<string, unknown> {
    const base: BaseEventProperties = {
      timestamp: new Date().toISOString(),
      path: window.location.pathname,
      referrer: document.referrer || undefined,
      session_id: this.sessionId || undefined,
    }

    if (properties) {
      return { ...base, ...this.sanitizeProperties(properties) }
    }

    return base
  }

  private sanitizeProperties(properties: Record<string, unknown>): Record<string, unknown> {
    const sanitized: Record<string, unknown> = {}

    for (const [key, value] of Object.entries(properties)) {
      // Skip PII fields
      const lowerKey = key.toLowerCase()
      if (PII_FIELDS.some((pii) => lowerKey.includes(pii.toLowerCase()))) {
        continue
      }

      // Truncate long strings
      if (typeof value === 'string' && value.length > 255) {
        sanitized[key] = value.substring(0, 255) + '...'
      } else {
        sanitized[key] = value
      }
    }

    return sanitized
  }

  private getOrCreateSessionId(): string {
    let sessionId = sessionStorage.getItem(SESSION_ID_KEY)
    if (!sessionId) {
      sessionId = this.generateSessionId()
      sessionStorage.setItem(SESSION_ID_KEY, sessionId)
    }
    return sessionId
  }

  private generateSessionId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`
  }

  private loadConsentSettings(): PrivacySettings {
    try {
      const stored = localStorage.getItem(CONSENT_STORAGE_KEY)
      if (stored) {
        return JSON.parse(stored)
      }
    } catch {
      // Ignore parse errors
    }
    return { analyticsConsent: false, marketingConsent: false }
  }

  private saveConsentSettings(settings: PrivacySettings): void {
    try {
      const toSave: PrivacySettings = {
        ...settings,
        consentTimestamp: new Date().toISOString(),
      }
      localStorage.setItem(CONSENT_STORAGE_KEY, JSON.stringify(toSave))
    } catch {
      // Ignore storage errors
    }
  }
}

// ============================================================================
// Singleton Export
// ============================================================================

/**
 * Global analytics instance
 *
 * Usage:
 * ```typescript
 * import { analytics } from '@/services/analytics'
 *
 * // Initialize (once at app startup)
 * analytics.init({ token: 'your-mixpanel-token' })
 *
 * // Track events
 * analytics.track('Button Clicked', { button_name: 'signup' })
 *
 * // Track page views
 * analytics.page('Home')
 *
 * // Identify users
 * analytics.identify('user-123', { email: 'user@example.com' })
 * ```
 */
export const analytics = new AnalyticsService()
