/**
 * Experiments Service Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  experiments,
  COMPACT_TABLE_EXPERIMENT,
  SIMPLIFIED_FILTERS_EXPERIMENT,
  type Experiment,
} from '../experiments'
import { analytics } from '../analyticsService'

// Mock analytics
vi.mock('../analyticsService', () => ({
  analytics: {
    init: vi.fn(),
    track: vi.fn(),
  },
}))

describe('ExperimentService', () => {
  beforeEach(() => {
    // Clear localStorage
    localStorage.clear()
    // Clear experiment assignments
    experiments.clearAssignments()
    vi.clearAllMocks()
  })

  describe('getVariant', () => {
    it('should return a valid variant', () => {
      const variant = experiments.getVariant(COMPACT_TABLE_EXPERIMENT)

      expect(COMPACT_TABLE_EXPERIMENT.variants).toContain(variant)
    })

    it('should return consistent variant for same experiment', () => {
      const variant1 = experiments.getVariant(COMPACT_TABLE_EXPERIMENT)
      const variant2 = experiments.getVariant(COMPACT_TABLE_EXPERIMENT)

      expect(variant1).toBe(variant2)
    })

    it('should persist variant across instances', () => {
      const variant1 = experiments.getVariant(COMPACT_TABLE_EXPERIMENT)

      // Simulate page reload by clearing and reloading assignments
      const stored = localStorage.getItem('ab_experiments')
      expect(stored).toBeTruthy()

      // Create new service would load from localStorage
      const storedAssignments = JSON.parse(stored!)
      const storedVariant = storedAssignments.find(
        (a: { experimentId: string }) => a.experimentId === COMPACT_TABLE_EXPERIMENT.id,
      )

      expect(storedVariant?.variant).toBe(variant1)
    })

    it('should return control variant for inactive experiments', () => {
      const inactiveExperiment: Experiment = {
        id: 'inactive_test',
        name: 'Inactive Test',
        variants: ['control', 'treatment'],
        active: false,
      }

      const variant = experiments.getVariant(inactiveExperiment)
      expect(variant).toBe('control')
    })

    it('should track experiment assignment', () => {
      analytics.init({ token: '' })

      experiments.getVariant(COMPACT_TABLE_EXPERIMENT)

      expect(analytics.track).toHaveBeenCalledWith(
        'Experiment Assigned',
        expect.objectContaining({
          experiment_id: COMPACT_TABLE_EXPERIMENT.id,
          experiment_name: COMPACT_TABLE_EXPERIMENT.name,
          variant: expect.any(String),
        }),
      )
    })
  })

  describe('setVariant', () => {
    it('should allow manual variant override', () => {
      experiments.setVariant(COMPACT_TABLE_EXPERIMENT.id, 'compact')

      const variant = experiments.getVariant(COMPACT_TABLE_EXPERIMENT)
      expect(variant).toBe('compact')
    })
  })

  describe('trackConversion', () => {
    it('should track conversion event', () => {
      analytics.init({ token: '' })

      // First get a variant to establish assignment
      experiments.getVariant(COMPACT_TABLE_EXPERIMENT)
      vi.clearAllMocks()

      experiments.trackConversion(COMPACT_TABLE_EXPERIMENT, 'export')

      expect(analytics.track).toHaveBeenCalledWith(
        'Experiment Converted',
        expect.objectContaining({
          experiment_id: COMPACT_TABLE_EXPERIMENT.id,
          experiment_name: COMPACT_TABLE_EXPERIMENT.name,
          variant: expect.any(String),
          conversion_type: 'export',
        }),
      )
    })
  })

  describe('getAssignments', () => {
    it('should return all current assignments', () => {
      experiments.getVariant(COMPACT_TABLE_EXPERIMENT)
      experiments.getVariant(SIMPLIFIED_FILTERS_EXPERIMENT)

      const assignments = experiments.getAssignments()

      expect(assignments[COMPACT_TABLE_EXPERIMENT.id]).toBeTruthy()
      expect(assignments[SIMPLIFIED_FILTERS_EXPERIMENT.id]).toBeTruthy()
    })
  })

  describe('clearAssignments', () => {
    it('should clear all assignments', () => {
      experiments.getVariant(COMPACT_TABLE_EXPERIMENT)
      experiments.clearAssignments()

      const assignments = experiments.getAssignments()
      expect(Object.keys(assignments).length).toBe(0)
    })
  })

  describe('isInVariant', () => {
    it('should check if user is in specific variant', () => {
      experiments.setVariant(COMPACT_TABLE_EXPERIMENT.id, 'compact')

      expect(experiments.isInVariant(COMPACT_TABLE_EXPERIMENT, 'compact')).toBe(true)
      expect(experiments.isInVariant(COMPACT_TABLE_EXPERIMENT, 'control')).toBe(false)
    })
  })

  describe('weight distribution', () => {
    it('should respect custom weights', () => {
      const customExperiment: Experiment = {
        id: 'custom_weights_test',
        name: 'Custom Weights Test',
        variants: ['a', 'b'],
        weights: [0.9, 0.1], // 90% A, 10% B
        active: true,
      }

      // Run many iterations to verify distribution
      const iterations = 1000
      const results: Record<string, number> = { a: 0, b: 0 }

      for (let i = 0; i < iterations; i++) {
        localStorage.removeItem('ab_experiments')
        experiments.clearAssignments()

        const variant = experiments.getVariant(customExperiment)
        results[variant]++
      }

      // With 90/10 split, A should be significantly more common
      // Allow for statistical variance
      expect(results.a).toBeGreaterThan(results.b)
    })
  })
})
