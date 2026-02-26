/**
 * A/B Testing / Experiments Service
 *
 * Provides a simple framework for running controlled experiments.
 * Features:
 * - Consistent variant assignment per user
 * - Weighted distribution support
 * - Persistent assignments across sessions
 * - Conversion tracking
 */

import { analytics } from './analyticsService'
import { AnalyticsEvents } from './types'

// ============================================================================
// Types
// ============================================================================

/**
 * Experiment definition
 */
export interface Experiment {
  /** Unique identifier for the experiment */
  id: string
  /** Human-readable name */
  name: string
  /** Available variants */
  variants: string[]
  /** Distribution weights (must sum to 1.0, defaults to equal distribution) */
  weights?: number[]
  /** Whether the experiment is active */
  active?: boolean
  /** Description of the experiment */
  description?: string
}

/**
 * Stored experiment assignment
 */
interface ExperimentAssignment {
  experimentId: string
  variant: string
  assignedAt: string
}

// ============================================================================
// Constants
// ============================================================================

const STORAGE_KEY = 'ab_experiments'

// ============================================================================
// Predefined Experiments
// ============================================================================

/**
 * Compact Table Design Experiment
 * Tests whether a more compact table design improves engagement
 */
export const COMPACT_TABLE_EXPERIMENT: Experiment = {
  id: 'compact_table_v1',
  name: 'Compact Table Design',
  variants: ['control', 'compact'],
  weights: [0.5, 0.5],
  active: true,
  description: 'Tests compact table layout vs standard layout',
}

/**
 * Simplified Filters Experiment
 * Tests whether simplified filters improve conversion
 */
export const SIMPLIFIED_FILTERS_EXPERIMENT: Experiment = {
  id: 'simplified_filters_v1',
  name: 'Simplified Filters',
  variants: ['control', 'simplified'],
  weights: [0.5, 0.5],
  active: true,
  description: 'Tests simplified filter UI vs full filter UI',
}

/**
 * CTA Button Color Experiment
 * Tests which CTA color drives more upgrades
 */
export const CTA_COLOR_EXPERIMENT: Experiment = {
  id: 'cta_color_v1',
  name: 'CTA Button Color',
  variants: ['blue', 'green', 'orange'],
  weights: [0.34, 0.33, 0.33],
  active: false,
  description: 'Tests different CTA button colors for upgrade conversion',
}

/**
 * Onboarding Flow Experiment
 * Tests different onboarding experiences
 */
export const ONBOARDING_FLOW_EXPERIMENT: Experiment = {
  id: 'onboarding_v1',
  name: 'Onboarding Flow',
  variants: ['control', 'guided_tour', 'video'],
  weights: [0.34, 0.33, 0.33],
  active: false,
  description: 'Tests different onboarding experiences for new users',
}

// ============================================================================
// Experiment Service
// ============================================================================

class ExperimentService {
  private assignments: Map<string, ExperimentAssignment> = new Map()
  private loaded = false

  constructor() {
    this.loadAssignments()
  }

  /**
   * Get the variant assignment for an experiment
   * Assigns a variant if not already assigned
   */
  getVariant(experiment: Experiment): string {
    // Check if experiment is active
    if (experiment.active === false) {
      return experiment.variants[0] // Return control variant
    }

    // Ensure assignments are loaded
    if (!this.loaded) {
      this.loadAssignments()
    }

    // Check for existing assignment
    const existing = this.assignments.get(experiment.id)
    if (existing) {
      // Verify the variant still exists in the experiment
      if (experiment.variants.includes(existing.variant)) {
        return existing.variant
      }
      // Variant was removed, reassign
    }

    // Assign new variant
    const variant = this.assignVariant(experiment)
    return variant
  }

  /**
   * Force a specific variant (useful for testing or override)
   */
  setVariant(experimentId: string, variant: string): void {
    const assignment: ExperimentAssignment = {
      experimentId,
      variant,
      assignedAt: new Date().toISOString(),
    }
    this.assignments.set(experimentId, assignment)
    this.saveAssignments()
  }

  /**
   * Track a conversion for an experiment
   */
  trackConversion(experiment: Experiment, conversionType?: string): void {
    const variant = this.getVariant(experiment)

    analytics.track(AnalyticsEvents.EXPERIMENT_CONVERTED, {
      experiment_id: experiment.id,
      experiment_name: experiment.name,
      variant,
      conversion_type: conversionType || 'default',
    })
  }

  /**
   * Get all current assignments (for debugging)
   */
  getAssignments(): Record<string, string> {
    const result: Record<string, string> = {}
    this.assignments.forEach(assignment => {
      result[assignment.experimentId] = assignment.variant
    })
    return result
  }

  /**
   * Clear all assignments (useful for testing)
   */
  clearAssignments(): void {
    this.assignments.clear()
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch {
      // Ignore storage errors
    }
  }

  /**
   * Check if user is in a specific variant
   */
  isInVariant(experiment: Experiment, variant: string): boolean {
    return this.getVariant(experiment) === variant
  }

  // ============================================================================
  // Private Methods
  // ============================================================================

  private assignVariant(experiment: Experiment): string {
    const weights =
      experiment.weights || this.equalWeights(experiment.variants.length)

    // Validate weights
    const totalWeight = weights.reduce((sum, w) => sum + w, 0)
    if (Math.abs(totalWeight - 1) > 0.01) {
      console.warn(
        `[Experiments] Weights for ${experiment.id} don't sum to 1.0, normalizing`,
      )
    }

    // Random assignment based on weights
    const random = Math.random()
    let cumulative = 0

    for (let i = 0; i < weights.length; i++) {
      cumulative += weights[i] / totalWeight // Normalize
      if (random < cumulative) {
        const variant = experiment.variants[i]
        this.recordAssignment(experiment, variant)
        return variant
      }
    }

    // Fallback to last variant (shouldn't happen)
    const variant = experiment.variants[experiment.variants.length - 1]
    this.recordAssignment(experiment, variant)
    return variant
  }

  private recordAssignment(experiment: Experiment, variant: string): void {
    const assignment: ExperimentAssignment = {
      experimentId: experiment.id,
      variant,
      assignedAt: new Date().toISOString(),
    }

    this.assignments.set(experiment.id, assignment)
    this.saveAssignments()

    // Track the assignment
    analytics.track(AnalyticsEvents.EXPERIMENT_ASSIGNED, {
      experiment_id: experiment.id,
      experiment_name: experiment.name,
      variant,
    })
  }

  private equalWeights(count: number): number[] {
    return Array(count).fill(1 / count)
  }

  private loadAssignments(): void {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const data = JSON.parse(stored) as ExperimentAssignment[]
        data.forEach(assignment => {
          this.assignments.set(assignment.experimentId, assignment)
        })
      }
    } catch {
      // Ignore parse errors
    }
    this.loaded = true
  }

  private saveAssignments(): void {
    try {
      const data = Array.from(this.assignments.values())
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    } catch {
      // Ignore storage errors
    }
  }
}

// ============================================================================
// Singleton Export
// ============================================================================

/**
 * Global experiments instance
 *
 * Usage:
 * ```typescript
 * import { experiments, COMPACT_TABLE_EXPERIMENT } from '@/services/analytics'
 *
 * // Get variant assignment
 * const variant = experiments.getVariant(COMPACT_TABLE_EXPERIMENT)
 *
 * // Use in component
 * if (variant === 'compact') {
 *   return <CompactTable />
 * }
 * return <StandardTable />
 *
 * // Track conversion
 * experiments.trackConversion(COMPACT_TABLE_EXPERIMENT, 'export')
 * ```
 */
export const experiments = new ExperimentService()
