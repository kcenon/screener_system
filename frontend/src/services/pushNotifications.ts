import { pwaService } from './pwa'

interface PushSubscriptionData {
  endpoint: string
  keys: {
    p256dh: string
    auth: string
  }
}

export type NotificationType =
  | 'price_alert'
  | 'watchlist'
  | 'market'
  | 'portfolio'

interface NotificationPreferences {
  priceAlerts: boolean
  watchlistUpdates: boolean
  marketNews: boolean
  portfolioUpdates: boolean
}

/**
 * Service for managing push notifications
 */
class PushNotificationService {
  private subscription: PushSubscription | null = null
  private preferences: NotificationPreferences = {
    priceAlerts: true,
    watchlistUpdates: true,
    marketNews: false,
    portfolioUpdates: true,
  }

  /**
   * Check if push notifications are supported
   */
  isSupported(): boolean {
    return (
      'serviceWorker' in navigator &&
      'PushManager' in window &&
      'Notification' in window
    )
  }

  /**
   * Get current notification permission status
   */
  getPermissionStatus(): NotificationPermission | 'unsupported' {
    if (!this.isSupported()) return 'unsupported'
    return Notification.permission
  }

  /**
   * Request notification permission
   */
  async requestPermission(): Promise<NotificationPermission> {
    if (!this.isSupported()) {
      throw new Error('Push notifications not supported')
    }

    const permission = await Notification.requestPermission()
    return permission
  }

  /**
   * Subscribe to push notifications
   */
  async subscribe(
    vapidPublicKey: string,
  ): Promise<PushSubscriptionData | null> {
    if (!this.isSupported()) {
      console.warn('Push notifications not supported')
      return null
    }

    const permission = await this.requestPermission()
    if (permission !== 'granted') {
      console.warn('Notification permission denied')
      return null
    }

    const registration = pwaService.getRegistration()
    if (!registration) {
      console.warn('Service worker not registered')
      return null
    }

    try {
      const applicationServerKey = this.urlBase64ToUint8Array(vapidPublicKey)
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: applicationServerKey.buffer as ArrayBuffer,
      })

      this.subscription = subscription

      // Extract subscription data
      const p256dh = subscription.getKey('p256dh')
      const auth = subscription.getKey('auth')

      if (!p256dh || !auth) {
        throw new Error('Failed to get push subscription keys')
      }

      return {
        endpoint: subscription.endpoint,
        keys: {
          p256dh: this.arrayBufferToBase64(p256dh),
          auth: this.arrayBufferToBase64(auth),
        },
      }
    } catch (error) {
      console.error('Failed to subscribe to push:', error)
      return null
    }
  }

  /**
   * Unsubscribe from push notifications
   */
  async unsubscribe(): Promise<boolean> {
    if (this.subscription) {
      try {
        await this.subscription.unsubscribe()
        this.subscription = null
        return true
      } catch (error) {
        console.error('Failed to unsubscribe:', error)
        return false
      }
    }
    return true
  }

  /**
   * Get notification preferences
   */
  getPreferences(): NotificationPreferences {
    const saved = localStorage.getItem('notificationPreferences')
    if (saved) {
      try {
        return JSON.parse(saved)
      } catch {
        return this.preferences
      }
    }
    return this.preferences
  }

  /**
   * Update notification preferences
   */
  setPreferences(preferences: Partial<NotificationPreferences>): void {
    this.preferences = { ...this.preferences, ...preferences }
    localStorage.setItem(
      'notificationPreferences',
      JSON.stringify(this.preferences),
    )
  }

  /**
   * Show a local notification (for testing or offline scenarios)
   */
  async showLocalNotification(
    title: string,
    options?: NotificationOptions,
  ): Promise<void> {
    if (!this.isSupported()) return

    const permission = this.getPermissionStatus()
    if (permission !== 'granted') return

    const registration = pwaService.getRegistration()
    if (!registration) return

    await registration.showNotification(title, {
      icon: '/icons/icon-192.png',
      badge: '/icons/icon-72.png',
      ...options,
    })
  }

  /**
   * Convert VAPID public key from base64 to Uint8Array
   */
  private urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/')

    const rawData = window.atob(base64)
    const outputArray = new Uint8Array(rawData.length)

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i)
    }

    return outputArray
  }

  /**
   * Convert ArrayBuffer to base64 string
   */
  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer)
    let binary = ''
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    return window.btoa(binary)
  }
}

export const pushNotificationService = new PushNotificationService()
export default pushNotificationService
