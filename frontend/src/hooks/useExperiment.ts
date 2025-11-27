/**
 * A/B Testing Hook
 *
 * React hook for using experiments (A/B tests) in components.
 * Provides variant assignment and conversion tracking.
 */

import { useCallback, useMemo } from 'react'
import {
  experiments,
  COMPACT_TABLE_EXPERIMENT,
  SIMPLIFIED_FILTERS_EXPERIMENT,
  CTA_COLOR_EXPERIMENT,
  ONBOARDING_FLOW_EXPERIMENT,
  type Experiment,
} from '../services/analytics'

// ============================================================================
// Main Hook
// ============================================================================

/**
 * Hook for getting the assigned variant for an experiment
 *
 * @param experiment - The experiment definition
 * @returns The assigned variant and helper functions
 *
 * @example
 * ```tsx
 * function ResultsTable() {
 *   const { variant, isVariant, trackConversion } = useExperiment(COMPACT_TABLE_EXPERIMENT)
 *
 *   // Check specific variant
 *   if (isVariant('compact')) {
 *     return <CompactTable onExport={() => trackConversion('export')} />
 *   }
 *
 *   return <StandardTable onExport={() => trackConversion('export')} />
 * }
 * ```
 */
export function useExperiment(experiment: Experiment) {
  // Get variant (memoized to prevent re-assignment)
  const variant = useMemo(() => {
    return experiments.getVariant(experiment)
  }, [experiment.id])

  // Check if user is in a specific variant
  const isVariant = useCallback(
    (checkVariant: string): boolean => {
      return variant === checkVariant
    },
    [variant],
  )

  // Track conversion for this experiment
  const trackConversion = useCallback(
    (conversionType?: string) => {
      experiments.trackConversion(experiment, conversionType)
    },
    [experiment],
  )

  return {
    /** The assigned variant name */
    variant,
    /** Check if user is in a specific variant */
    isVariant,
    /** Track a conversion for this experiment */
    trackConversion,
    /** The experiment definition */
    experiment,
  }
}

// ============================================================================
// Convenience Hooks for Predefined Experiments
// ============================================================================

/**
 * Hook for the Compact Table experiment
 *
 * @example
 * ```tsx
 * function DataTable() {
 *   const { isCompact, trackConversion } = useCompactTableExperiment()
 *   return isCompact ? <CompactTable /> : <StandardTable />
 * }
 * ```
 */
export function useCompactTableExperiment() {
  const { variant, isVariant, trackConversion } = useExperiment(COMPACT_TABLE_EXPERIMENT)

  return {
    variant,
    isCompact: isVariant('compact'),
    isControl: isVariant('control'),
    trackConversion,
  }
}

/**
 * Hook for the Simplified Filters experiment
 *
 * @example
 * ```tsx
 * function FilterPanel() {
 *   const { isSimplified } = useSimplifiedFiltersExperiment()
 *   return isSimplified ? <SimpleFilters /> : <AdvancedFilters />
 * }
 * ```
 */
export function useSimplifiedFiltersExperiment() {
  const { variant, isVariant, trackConversion } = useExperiment(SIMPLIFIED_FILTERS_EXPERIMENT)

  return {
    variant,
    isSimplified: isVariant('simplified'),
    isControl: isVariant('control'),
    trackConversion,
  }
}

/**
 * Hook for the CTA Color experiment
 *
 * @example
 * ```tsx
 * function UpgradeButton() {
 *   const { ctaColor, trackConversion } = useCTAColorExperiment()
 *   return (
 *     <Button color={ctaColor} onClick={trackConversion}>
 *       Upgrade Now
 *     </Button>
 *   )
 * }
 * ```
 */
export function useCTAColorExperiment() {
  const { variant, trackConversion } = useExperiment(CTA_COLOR_EXPERIMENT)

  const colorMap: Record<string, string> = {
    blue: 'bg-blue-600 hover:bg-blue-700',
    green: 'bg-green-600 hover:bg-green-700',
    orange: 'bg-orange-600 hover:bg-orange-700',
  }

  return {
    variant,
    ctaColor: variant as 'blue' | 'green' | 'orange',
    ctaClassName: colorMap[variant] || colorMap.blue,
    trackConversion,
  }
}

/**
 * Hook for the Onboarding Flow experiment
 *
 * @example
 * ```tsx
 * function OnboardingModal() {
 *   const { flowType, trackConversion } = useOnboardingExperiment()
 *
 *   switch (flowType) {
 *     case 'guided_tour':
 *       return <GuidedTour onComplete={trackConversion} />
 *     case 'video':
 *       return <VideoOnboarding onComplete={trackConversion} />
 *     default:
 *       return <StandardOnboarding onComplete={trackConversion} />
 *   }
 * }
 * ```
 */
export function useOnboardingExperiment() {
  const { variant, isVariant, trackConversion } = useExperiment(ONBOARDING_FLOW_EXPERIMENT)

  return {
    variant,
    flowType: variant as 'control' | 'guided_tour' | 'video',
    isGuidedTour: isVariant('guided_tour'),
    isVideo: isVariant('video'),
    isControl: isVariant('control'),
    trackConversion,
  }
}

// ============================================================================
// Debug Hook
// ============================================================================

/**
 * Hook for debugging experiments (development only)
 *
 * @example
 * ```tsx
 * function DevTools() {
 *   const { allAssignments, clearAll, setVariant } = useExperimentDebug()
 *
 *   return (
 *     <div>
 *       <pre>{JSON.stringify(allAssignments, null, 2)}</pre>
 *       <button onClick={clearAll}>Reset All</button>
 *     </div>
 *   )
 * }
 * ```
 */
export function useExperimentDebug() {
  const allAssignments = useMemo(() => {
    return experiments.getAssignments()
  }, [])

  const clearAll = useCallback(() => {
    experiments.clearAssignments()
    window.location.reload()
  }, [])

  const setVariant = useCallback((experimentId: string, variant: string) => {
    experiments.setVariant(experimentId, variant)
    window.location.reload()
  }, [])

  return {
    allAssignments,
    clearAll,
    setVariant,
  }
}

// ============================================================================
// Re-export predefined experiments for convenience
// ============================================================================

export {
  COMPACT_TABLE_EXPERIMENT,
  SIMPLIFIED_FILTERS_EXPERIMENT,
  CTA_COLOR_EXPERIMENT,
  ONBOARDING_FLOW_EXPERIMENT,
}
export type { Experiment }
