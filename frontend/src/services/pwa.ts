import { registerSW } from 'virtual:pwa-register'

interface PWAUpdateCallback {
  onNeedRefresh?: () => void
  onOfflineReady?: () => void
  onRegistered?: (registration: ServiceWorkerRegistration) => void
  onRegisterError?: (error: Error) => void
}

/**
 * PWA Service for managing service worker registration and updates
 */
class PWAService {
  private updateSW: ((reloadPage?: boolean) => Promise<void>) | null = null
  private registration: ServiceWorkerRegistration | null = null

  /**
   * Initialize the PWA service worker
   */
  init(callbacks: PWAUpdateCallback = {}): void {
    if (typeof window === 'undefined') return

    this.updateSW = registerSW({
      immediate: true,
      onNeedRefresh: () => {
        callbacks.onNeedRefresh?.()
      },
      onOfflineReady: () => {
        callbacks.onOfflineReady?.()
      },
      onRegistered: r => {
        if (r) {
          this.registration = r
          callbacks.onRegistered?.(r)

          // Check for updates periodically (every hour)
          setInterval(
            () => {
              r.update()
            },
            60 * 60 * 1000,
          )
        }
      },
      onRegisterError: error => {
        console.error('SW registration error:', error)
        callbacks.onRegisterError?.(error as Error)
      },
    })
  }

  /**
   * Update to the latest service worker version
   */
  async update(): Promise<void> {
    if (this.updateSW) {
      await this.updateSW(true)
    }
  }

  /**
   * Get the current service worker registration
   */
  getRegistration(): ServiceWorkerRegistration | null {
    return this.registration
  }

  /**
   * Check if app is running as installed PWA
   */
  isStandalone(): boolean {
    if (typeof window === 'undefined') return false

    return (
      window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as unknown as { standalone?: boolean }).standalone ===
        true ||
      document.referrer.includes('android-app://')
    )
  }

  /**
   * Check if app can be installed
   */
  canInstall(): boolean {
    return 'BeforeInstallPromptEvent' in window
  }
}

export const pwaService = new PWAService()
export default pwaService
