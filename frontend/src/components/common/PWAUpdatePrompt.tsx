import { RefreshCw, X } from 'lucide-react'
import { usePWA } from '@/hooks/usePWA'

/**
 * Component that prompts users when a new PWA version is available
 */
export function PWAUpdatePrompt() {
  const { needsUpdate, update, dismissUpdate } = usePWA()

  if (!needsUpdate) return null

  return (
    <div
      className="fixed bottom-20 left-4 right-4 md:left-auto md:right-4 md:w-80
        bg-blue-50 border border-blue-200 rounded-lg p-4
        flex flex-col gap-3 z-50 shadow-lg"
      role="alert"
    >
      <div className="flex items-start gap-3">
        <RefreshCw className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-blue-800 font-medium text-sm">
            Update Available
          </p>
          <p className="text-blue-700 text-xs mt-1">
            A new version of the app is ready. Refresh to update.
          </p>
        </div>
        <button
          onClick={dismissUpdate}
          className="p-1 rounded-md hover:bg-blue-100 transition-colors"
          aria-label="Dismiss update notification"
        >
          <X className="w-4 h-4 text-blue-600" />
        </button>
      </div>
      <div className="flex gap-2">
        <button
          onClick={dismissUpdate}
          className="flex-1 px-3 py-1.5 text-sm text-blue-700 bg-white
            border border-blue-200 rounded-md hover:bg-blue-50 transition-colors"
        >
          Later
        </button>
        <button
          onClick={update}
          className="flex-1 px-3 py-1.5 text-sm text-white bg-blue-600
            rounded-md hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>
    </div>
  )
}

export default PWAUpdatePrompt
