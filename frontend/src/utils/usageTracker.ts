/**
 * Usage tracking utilities for freemium tier limits.
 *
 * Tracks user actions (like screening searches) for unauthenticated users
 * using localStorage. Resets daily to enforce fair usage limits.
 *
 * @module utils/usageTracker
 * @category Utils
 */

/**
 * Storage key for usage tracking data.
 */
const STORAGE_KEY = 'screening_usage'

/**
 * Usage tracking data structure.
 */
interface UsageData {
  /** Date string (YYYY-MM-DD) when tracking started */
  date: string
  /** Number of actions performed */
  count: number
}

/**
 * Get today's date as a string (YYYY-MM-DD).
 *
 * @returns Date string in YYYY-MM-DD format
 */
function getTodayString(): string {
  return new Date().toISOString().split('T')[0]
}

/**
 * Get current usage data from localStorage.
 *
 * Returns usage count for today, or 0 if no data exists or data is from previous day.
 *
 * @returns Current usage count
 *
 * @example
 * ```typescript
 * const count = getUsageCount()
 * console.log(`You've performed ${count} searches today`)
 * ```
 */
export function getUsageCount(): number {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return 0

    const data: UsageData = JSON.parse(stored)
    const today = getTodayString()

    // Reset if data is from a previous day
    if (data.date !== today) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ date: today, count: 0 }))
      return 0
    }

    return data.count
  } catch (error) {
    console.error('Error reading usage count:', error)
    return 0
  }
}

/**
 * Increment usage count for today.
 *
 * Tracks a new action (e.g., screening search). Automatically
 * resets counter if it's a new day.
 *
 * @returns New usage count after increment
 *
 * @example
 * ```typescript
 * const handleSearch = () => {
 *   const newCount = trackScreening()
 *   console.log(`Search count: ${newCount}`)
 * }
 * ```
 */
export function trackScreening(): number {
  try {
    const today = getTodayString()
    const stored = localStorage.getItem(STORAGE_KEY)

    if (stored) {
      const data: UsageData = JSON.parse(stored)

      // If same day, increment count
      if (data.date === today) {
        const newCount = data.count + 1
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ date: today, count: newCount }))
        return newCount
      }
    }

    // First action of the day or no previous data
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ date: today, count: 1 }))
    return 1
  } catch (error) {
    console.error('Error tracking screening:', error)
    return 0
  }
}

/**
 * Check if user can perform another action based on daily limit.
 *
 * @param dailyLimit - Maximum allowed actions per day
 * @returns True if user has not exceeded daily limit
 *
 * @example
 * ```typescript
 * if (!canPerformScreening(10)) {
 *   showLimitReachedModal()
 *   return
 * }
 *
 * // Proceed with screening
 * performScreening()
 * trackScreening()
 * ```
 */
export function canPerformScreening(dailyLimit: number): boolean {
  const currentCount = getUsageCount()
  return currentCount < dailyLimit
}

/**
 * Reset usage counter (for testing purposes).
 *
 * Clears all usage tracking data from localStorage.
 * Should only be used in development/testing.
 *
 * @internal
 */
export function resetUsageCounter(): void {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch (error) {
    console.error('Error resetting usage counter:', error)
  }
}

/**
 * Get remaining actions for today.
 *
 * @param dailyLimit - Maximum allowed actions per day
 * @returns Number of remaining actions (0 if limit reached)
 *
 * @example
 * ```typescript
 * const remaining = getRemainingActions(10)
 * console.log(`${remaining} searches remaining today`)
 * ```
 */
export function getRemainingActions(dailyLimit: number): number {
  const currentCount = getUsageCount()
  const remaining = dailyLimit - currentCount
  return Math.max(0, remaining)
}
