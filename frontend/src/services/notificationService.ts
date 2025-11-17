/**
 * Notification Service - API client for notification management
 *
 * Provides TypeScript interfaces and API methods for:
 * - Notification listing and pagination
 * - Mark as read operations
 * - Notification preferences
 * - Unread count tracking
 *
 * @module services/notificationService
 * @category Services
 */

import { api } from './api'

// ============================================================================
// ENUMS
// ============================================================================

/**
 * Notification type enumeration
 */
export enum NotificationType {
  ALERT = 'ALERT',
  MARKET_EVENT = 'MARKET_EVENT',
  SYSTEM = 'SYSTEM',
  PORTFOLIO = 'PORTFOLIO',
}

/**
 * Notification priority enumeration
 */
export enum NotificationPriority {
  LOW = 'LOW',
  NORMAL = 'NORMAL',
  HIGH = 'HIGH',
  URGENT = 'URGENT',
}

// ============================================================================
// NOTIFICATION TYPES
// ============================================================================

/**
 * Notification entity from backend
 */
export interface Notification {
  id: number
  user_id: number
  alert_id: number | null
  notification_type: NotificationType
  title: string
  message: string
  priority: NotificationPriority
  is_read: boolean
  read_at: string | null // ISO datetime
  created_at: string // ISO datetime
}

/**
 * Paginated notification list response
 */
export interface NotificationListResponse {
  items: Notification[]
  total: number
  unread_count: number
  skip: number
  limit: number
}

/**
 * Unread count response
 */
export interface UnreadCountResponse {
  unread_count: number
}

/**
 * Notification preferences entity
 */
export interface NotificationPreference {
  id: number
  user_id: number
  email_enabled: boolean
  push_enabled: boolean
  in_app_enabled: boolean
  alert_email: boolean
  market_event_email: boolean
  system_email: boolean
  portfolio_email: boolean
  quiet_hours_enabled: boolean
  quiet_hours_start: string | null // HH:MM format
  quiet_hours_end: string | null // HH:MM format
  created_at: string
  updated_at: string
}

/**
 * Notification preferences update request
 */
export interface NotificationPreferenceUpdate {
  email_enabled?: boolean
  push_enabled?: boolean
  in_app_enabled?: boolean
  alert_email?: boolean
  market_event_email?: boolean
  system_email?: boolean
  portfolio_email?: boolean
  quiet_hours_enabled?: boolean
  quiet_hours_start?: string | null
  quiet_hours_end?: string | null
}

// ============================================================================
// SERVICE
// ============================================================================

/**
 * Notification Service singleton
 */
class NotificationService {
  private readonly basePath = '/api/v1/notifications'

  /**
   * Get paginated list of notifications
   *
   * @param params - Query parameters
   * @returns Paginated notification list
   *
   * @example
   * ```typescript
   * const result = await notificationService.getNotifications({
   *   page: 1,
   *   page_size: 20,
   *   is_read: false,
   * });
   * ```
   */
  async getNotifications(params?: {
    page?: number
    page_size?: number
    notification_type?: NotificationType
    is_read?: boolean
    priority?: NotificationPriority
  }): Promise<NotificationListResponse> {
    const response = await api.get<NotificationListResponse>(this.basePath, { params })
    return response.data
  }

  /**
   * Get unread notification count
   *
   * @returns Unread count
   *
   * @example
   * ```typescript
   * const { unread_count } = await notificationService.getUnreadCount();
   * ```
   */
  async getUnreadCount(): Promise<number> {
    const response = await api.get<UnreadCountResponse>(`${this.basePath}/unread`)
    return response.data.unread_count
  }

  /**
   * Mark notification as read
   *
   * @param id - Notification ID
   *
   * @example
   * ```typescript
   * await notificationService.markAsRead(123);
   * ```
   */
  async markAsRead(id: number): Promise<void> {
    await api.post(`${this.basePath}/${id}/read`)
  }

  /**
   * Mark all notifications as read
   *
   * @returns Number of notifications marked as read
   *
   * @example
   * ```typescript
   * const { marked_count } = await notificationService.markAllAsRead();
   * ```
   */
  async markAllAsRead(): Promise<number> {
    const response = await api.post<{ marked_count: number }>(`${this.basePath}/read-all`)
    return response.data.marked_count
  }

  /**
   * Delete notification
   *
   * @param id - Notification ID
   *
   * @example
   * ```typescript
   * await notificationService.deleteNotification(123);
   * ```
   */
  async deleteNotification(id: number): Promise<void> {
    await api.delete(`${this.basePath}/${id}`)
  }

  /**
   * Get notification preferences
   *
   * @returns User's notification preferences
   *
   * @example
   * ```typescript
   * const preferences = await notificationService.getPreferences();
   * ```
   */
  async getPreferences(): Promise<NotificationPreference> {
    const response = await api.get<NotificationPreference>(`${this.basePath}/preferences`)
    return response.data
  }

  /**
   * Update notification preferences
   *
   * @param data - Preference updates
   * @returns Updated preferences
   *
   * @example
   * ```typescript
   * const updated = await notificationService.updatePreferences({
   *   email_enabled: true,
   *   alert_email: true,
   * });
   * ```
   */
  async updatePreferences(data: NotificationPreferenceUpdate): Promise<NotificationPreference> {
    const response = await api.put<NotificationPreference>(`${this.basePath}/preferences`, data)
    return response.data
  }

  /**
   * Get notification type icon name
   *
   * @param type - Notification type
   * @returns Icon name for display
   *
   * @example
   * ```typescript
   * const icon = notificationService.getTypeIcon(NotificationType.ALERT);
   * // Returns: "bell"
   * ```
   */
  getTypeIcon(type: NotificationType): string {
    const icons: Record<NotificationType, string> = {
      [NotificationType.ALERT]: 'bell',
      [NotificationType.MARKET_EVENT]: 'trending-up',
      [NotificationType.SYSTEM]: 'info',
      [NotificationType.PORTFOLIO]: 'briefcase',
    }
    return icons[type] || 'bell'
  }

  /**
   * Get notification priority color
   *
   * @param priority - Notification priority
   * @returns Tailwind color class
   *
   * @example
   * ```typescript
   * const color = notificationService.getPriorityColor(NotificationPriority.HIGH);
   * // Returns: "text-red-600"
   * ```
   */
  getPriorityColor(priority: NotificationPriority): string {
    const colors: Record<NotificationPriority, string> = {
      [NotificationPriority.LOW]: 'text-gray-600',
      [NotificationPriority.NORMAL]: 'text-blue-600',
      [NotificationPriority.HIGH]: 'text-orange-600',
      [NotificationPriority.URGENT]: 'text-red-600',
    }
    return colors[priority] || 'text-gray-600'
  }

  /**
   * Format notification time (relative)
   *
   * @param createdAt - ISO datetime string
   * @returns Relative time string
   *
   * @example
   * ```typescript
   * const timeAgo = notificationService.formatTimeAgo('2024-11-17T10:00:00Z');
   * // Returns: "2 hours ago" or "just now"
   * ```
   */
  formatTimeAgo(createdAt: string): string {
    const now = new Date()
    const created = new Date(createdAt)
    const diffMs = now.getTime() - created.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`

    return created.toLocaleDateString()
  }
}

// Export singleton instance
export const notificationService = new NotificationService()
