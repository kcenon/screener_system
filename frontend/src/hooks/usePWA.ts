import { useState, useEffect, useCallback } from 'react'
import { pwaService } from '@/services/pwa'

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

interface PWAState {
  isInstallable: boolean
  isInstalled: boolean
  needsUpdate: boolean
  isOfflineReady: boolean
}

interface UsePWAReturn extends PWAState {
  install: () => Promise<boolean>
  update: () => Promise<void>
  dismissUpdate: () => void
}

/**
 * Hook for managing PWA installation and updates
 *
 * @example
 * ```tsx
 * const { isInstallable, install, needsUpdate, update } = usePWA()
 *
 * return (
 *   <>
 *     {isInstallable && <button onClick={install}>Install App</button>}
 *     {needsUpdate && <button onClick={update}>Update Available</button>}
 *   </>
 * )
 * ```
 */
export function usePWA(): UsePWAReturn {
  const [state, setState] = useState<PWAState>({
    isInstallable: false,
    isInstalled: pwaService.isStandalone(),
    needsUpdate: false,
    isOfflineReady: false,
  })

  const [deferredPrompt, setDeferredPrompt] =
    useState<BeforeInstallPromptEvent | null>(null)

  // Initialize PWA service
  useEffect(() => {
    pwaService.init({
      onNeedRefresh: () => {
        setState(prev => ({ ...prev, needsUpdate: true }))
      },
      onOfflineReady: () => {
        setState(prev => ({ ...prev, isOfflineReady: true }))
      },
    })
  }, [])

  // Listen for install prompt
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault()
      setDeferredPrompt(e as BeforeInstallPromptEvent)
      setState(prev => ({ ...prev, isInstallable: true }))
    }

    const handleAppInstalled = () => {
      setDeferredPrompt(null)
      setState(prev => ({
        ...prev,
        isInstallable: false,
        isInstalled: true,
      }))
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    window.addEventListener('appinstalled', handleAppInstalled)

    return () => {
      window.removeEventListener(
        'beforeinstallprompt',
        handleBeforeInstallPrompt,
      )
      window.removeEventListener('appinstalled', handleAppInstalled)
    }
  }, [])

  // Check standalone mode changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(display-mode: standalone)')
    const handleChange = (e: MediaQueryListEvent) => {
      setState(prev => ({ ...prev, isInstalled: e.matches }))
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  const install = useCallback(async (): Promise<boolean> => {
    if (!deferredPrompt) return false

    try {
      await deferredPrompt.prompt()
      const { outcome } = await deferredPrompt.userChoice

      if (outcome === 'accepted') {
        setDeferredPrompt(null)
        setState(prev => ({ ...prev, isInstallable: false }))
        return true
      }
    } catch (error) {
      console.error('Install prompt error:', error)
    }

    return false
  }, [deferredPrompt])

  const update = useCallback(async () => {
    await pwaService.update()
    setState(prev => ({ ...prev, needsUpdate: false }))
  }, [])

  const dismissUpdate = useCallback(() => {
    setState(prev => ({ ...prev, needsUpdate: false }))
  }, [])

  return {
    ...state,
    install,
    update,
    dismissUpdate,
  }
}

export default usePWA
