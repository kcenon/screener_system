import { useState, useEffect } from 'react'
import { Download, X, Smartphone } from 'lucide-react'
import { usePWA } from '@/hooks/usePWA'

/**
 * Component that prompts users to install the PWA
 * Shows a banner when the app is installable but not yet installed
 */
export function PWAInstallPrompt() {
  const { isInstallable, isInstalled, install } = usePWA()
  const [isDismissed, setIsDismissed] = useState(false)
  const [isInstalling, setIsInstalling] = useState(false)

  // Check if user has previously dismissed
  useEffect(() => {
    const dismissed = localStorage.getItem('pwaInstallDismissed')
    if (dismissed) {
      const dismissedTime = new Date(dismissed)
      const daysSinceDismissed =
        (Date.now() - dismissedTime.getTime()) / (1000 * 60 * 60 * 24)
      // Show again after 7 days
      setIsDismissed(daysSinceDismissed < 7)
    }
  }, [])

  const handleDismiss = () => {
    setIsDismissed(true)
    localStorage.setItem('pwaInstallDismissed', new Date().toISOString())
  }

  const handleInstall = async () => {
    setIsInstalling(true)
    const success = await install()
    setIsInstalling(false)

    if (!success) {
      // Show manual install instructions for iOS
      handleDismiss()
    }
  }

  // Don't show if already installed, not installable, or dismissed
  if (isInstalled || !isInstallable || isDismissed) {
    return null
  }

  return (
    <div
      className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96
        bg-gradient-to-r from-green-500 to-green-600
        rounded-xl p-4 shadow-xl z-50"
      role="complementary"
      aria-label="Install app prompt"
    >
      <div className="flex items-start gap-3">
        <div className="p-2 bg-white/20 rounded-lg">
          <Smartphone className="w-6 h-6 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-white font-semibold">
            Install Stock Screener
          </h3>
          <p className="text-green-100 text-sm mt-1">
            Add to your home screen for quick access and offline support
          </p>
        </div>
        <button
          onClick={handleDismiss}
          className="p-1 rounded-md hover:bg-white/20 transition-colors"
          aria-label="Close install prompt"
        >
          <X className="w-5 h-5 text-white" />
        </button>
      </div>

      <div className="flex gap-2 mt-4">
        <button
          onClick={handleDismiss}
          className="flex-1 px-4 py-2 text-sm text-white
            bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
        >
          Not now
        </button>
        <button
          onClick={handleInstall}
          disabled={isInstalling}
          className="flex-1 px-4 py-2 text-sm text-green-600 bg-white
            rounded-lg hover:bg-green-50 transition-colors
            flex items-center justify-center gap-2 font-medium
            disabled:opacity-70 disabled:cursor-not-allowed"
        >
          <Download className="w-4 h-4" />
          {isInstalling ? 'Installing...' : 'Install'}
        </button>
      </div>
    </div>
  )
}

export default PWAInstallPrompt
