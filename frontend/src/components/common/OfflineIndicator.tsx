import { useOnlineStatus } from '@/hooks/useOnlineStatus'
import { WifiOff, RefreshCw, CheckCircle } from 'lucide-react'
import { useState, useEffect } from 'react'

interface OfflineIndicatorProps {
  className?: string
}

/**
 * Component that displays offline status and reconnection state
 *
 * Shows a banner when the app goes offline and indicates when
 * connection is restored.
 */
export function OfflineIndicator({ className = '' }: OfflineIndicatorProps) {
  const { isOnline, wasOffline, checkConnection } = useOnlineStatus()
  const [showReconnected, setShowReconnected] = useState(false)
  const [isChecking, setIsChecking] = useState(false)

  // Show "reconnected" message briefly when coming back online
  useEffect(() => {
    if (isOnline && wasOffline) {
      setShowReconnected(true)
      const timer = setTimeout(() => {
        setShowReconnected(false)
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [isOnline, wasOffline])

  const handleRetry = async () => {
    setIsChecking(true)
    await checkConnection()
    setIsChecking(false)
  }

  // Show reconnected message
  if (showReconnected && isOnline) {
    return (
      <div
        className={`fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-80
          bg-green-50 border border-green-200 rounded-lg p-3
          flex items-center gap-3 z-50 shadow-lg animate-slide-up ${className}`}
        role="status"
        aria-live="polite"
      >
        <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
        <span className="text-green-800 text-sm font-medium">
          Connection restored
        </span>
      </div>
    )
  }

  // Hide when online
  if (isOnline) {
    return null
  }

  return (
    <div
      className={`fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-80
        bg-amber-50 border border-amber-300 rounded-lg p-3
        flex items-center gap-3 z-50 shadow-lg ${className}`}
      role="alert"
      aria-live="assertive"
    >
      <WifiOff className="w-5 h-5 text-amber-600 flex-shrink-0" />
      <div className="flex-1">
        <p className="text-amber-800 text-sm font-medium">
          You're offline
        </p>
        <p className="text-amber-700 text-xs mt-0.5">
          Showing cached data
        </p>
      </div>
      <button
        onClick={handleRetry}
        disabled={isChecking}
        className="p-2 rounded-md hover:bg-amber-100 transition-colors
          disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Retry connection"
      >
        <RefreshCw
          className={`w-4 h-4 text-amber-600 ${isChecking ? 'animate-spin' : ''}`}
        />
      </button>
    </div>
  )
}

export default OfflineIndicator
