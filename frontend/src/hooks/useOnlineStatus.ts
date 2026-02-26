import { useState, useEffect, useCallback } from 'react'

interface OnlineStatusState {
  isOnline: boolean
  wasOffline: boolean
  lastOnlineAt: Date | null
}

/**
 * Hook to track online/offline status with additional context
 *
 * @returns Online status state and utilities
 *
 * @example
 * ```tsx
 * const { isOnline, wasOffline } = useOnlineStatus()
 *
 * if (!isOnline) {
 *   return <OfflineIndicator />
 * }
 * ```
 */
export function useOnlineStatus(): OnlineStatusState & {
  checkConnection: () => Promise<boolean>
} {
  const [state, setState] = useState<OnlineStatusState>({
    isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
    wasOffline: false,
    lastOnlineAt: null,
  })

  const checkConnection = useCallback(async (): Promise<boolean> => {
    try {
      // Attempt to fetch a small resource to verify actual connectivity
      const response = await fetch('/manifest.json', {
        method: 'HEAD',
        cache: 'no-store',
      })
      return response.ok
    } catch {
      return false
    }
  }, [])

  useEffect(() => {
    const handleOnline = () => {
      setState(prev => ({
        isOnline: true,
        wasOffline: !prev.isOnline || prev.wasOffline,
        lastOnlineAt: new Date(),
      }))
    }

    const handleOffline = () => {
      setState(prev => ({
        ...prev,
        isOnline: false,
      }))
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Initial connection check
    checkConnection().then(isActuallyOnline => {
      if (!isActuallyOnline && state.isOnline) {
        setState(prev => ({ ...prev, isOnline: false }))
      }
    })

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [checkConnection, state.isOnline])

  return {
    ...state,
    checkConnection,
  }
}

export default useOnlineStatus
