/**
 * Analytics Service Tests
 *
 * Note: The analytics service is a singleton that may already be initialized.
 * Tests focus on verifying tracking behavior rather than initialization.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { analytics } from '../analyticsService'
import { AnalyticsEvents } from '../types'

// Mock mixpanel
vi.mock('mixpanel-browser', () => ({
  default: {
    init: vi.fn(),
    identify: vi.fn(),
    track: vi.fn(),
    people: {
      set: vi.fn(),
      increment: vi.fn(),
    },
    register: vi.fn(),
    reset: vi.fn(),
    opt_in_tracking: vi.fn(),
    opt_out_tracking: vi.fn(),
    track_links: vi.fn(),
  },
}))

describe('AnalyticsService', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    vi.clearAllMocks()
    // Initialize analytics in mock mode for all tests
    analytics.init({ token: '', debug: true })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('track', () => {
    it('should log events with properties', () => {
      const consoleSpy = vi.spyOn(console, 'info').mockImplementation(() => {})

      analytics.track(AnalyticsEvents.FILTER_APPLIED, {
        filter_type: 'market_cap',
        filter_value: 1000000,
      })

      expect(consoleSpy).toHaveBeenCalledWith(
        '[Analytics] track:',
        expect.objectContaining({
          event: AnalyticsEvents.FILTER_APPLIED,
        }),
      )
      consoleSpy.mockRestore()
    })

    it('should include timestamp in event properties', () => {
      const consoleSpy = vi.spyOn(console, 'info').mockImplementation(() => {})

      analytics.track('Test Event', {})

      const callArgs = consoleSpy.mock.calls.find((call) => call[0] === '[Analytics] track:')
      expect(callArgs).toBeTruthy()
      expect(callArgs![1].properties.timestamp).toBeTruthy()
      consoleSpy.mockRestore()
    })
  })

  describe('page', () => {
    it('should track page views with page name', () => {
      const consoleSpy = vi.spyOn(console, 'info').mockImplementation(() => {})

      analytics.page('Home')

      expect(consoleSpy).toHaveBeenCalledWith(
        '[Analytics] page:',
        expect.objectContaining({
          page_name: 'Home',
        }),
      )
      consoleSpy.mockRestore()
    })
  })

  describe('identify', () => {
    it('should identify users with traits', () => {
      const consoleSpy = vi.spyOn(console, 'info').mockImplementation(() => {})

      analytics.identify('user-123', {
        email: 'test@example.com',
        tier: 'premium',
      })

      expect(consoleSpy).toHaveBeenCalledWith(
        '[Analytics] identify:',
        expect.objectContaining({
          userId: 'user-123',
        }),
      )
      consoleSpy.mockRestore()
    })
  })

  describe('privacy', () => {
    it('should strip password fields from events', () => {
      const consoleSpy = vi.spyOn(console, 'info').mockImplementation(() => {})

      analytics.track('Test Event', {
        password: 'secret123',
        username: 'john',
      })

      const callArgs = consoleSpy.mock.calls.find((call) => call[0] === '[Analytics] track:')
      expect(callArgs![1].properties.password).toBeUndefined()
      expect(callArgs![1].properties.username).toBe('john')
      consoleSpy.mockRestore()
    })

    it('should truncate long string values', () => {
      const consoleSpy = vi.spyOn(console, 'info').mockImplementation(() => {})
      const longString = 'a'.repeat(300)

      analytics.track('Test Event', { description: longString })

      const callArgs = consoleSpy.mock.calls.find((call) => call[0] === '[Analytics] track:')
      expect(callArgs![1].properties.description.length).toBeLessThanOrEqual(258)
      consoleSpy.mockRestore()
    })
  })

  describe('consent', () => {
    it('should track opt-in status', () => {
      const consoleSpy = vi.spyOn(console, 'info').mockImplementation(() => {})

      analytics.optIn()

      expect(analytics.hasConsent()).toBe(true)
      consoleSpy.mockRestore()
    })

    it('should track opt-out status', () => {
      analytics.optIn() // First opt in
      analytics.optOut()

      expect(analytics.hasConsent()).toBe(false)
    })

    it('should persist consent to localStorage', () => {
      analytics.optIn()

      const stored = localStorage.getItem('analytics_consent')
      expect(stored).toBeTruthy()
      expect(JSON.parse(stored!).analyticsConsent).toBe(true)
    })
  })

  describe('reset', () => {
    it('should log reset action', () => {
      const consoleSpy = vi.spyOn(console, 'info').mockImplementation(() => {})

      analytics.reset()

      expect(consoleSpy).toHaveBeenCalledWith('[Analytics] reset')
      consoleSpy.mockRestore()
    })
  })

  describe('timing', () => {
    it('should track timing events', () => {
      const consoleSpy = vi.spyOn(console, 'info').mockImplementation(() => {})

      analytics.timing('PageLoad', 'render', 1234, 'initial_load')

      expect(consoleSpy).toHaveBeenCalledWith(
        '[Analytics] timing:',
        expect.objectContaining({
          timing_category: 'PageLoad',
          timing_variable: 'render',
          timing_value: 1234,
        }),
      )
      consoleSpy.mockRestore()
    })
  })

  describe('setUserProperties', () => {
    it('should set user properties', () => {
      const consoleSpy = vi.spyOn(console, 'info').mockImplementation(() => {})

      analytics.setUserProperties({ plan: 'premium', region: 'kr' })

      expect(consoleSpy).toHaveBeenCalledWith(
        '[Analytics] setUserProperties:',
        expect.objectContaining({
          plan: 'premium',
          region: 'kr',
        }),
      )
      consoleSpy.mockRestore()
    })
  })
})
