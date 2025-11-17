/**
 * Alert Service - API client for alert management
 *
 * Provides TypeScript interfaces and API methods for:
 * - Alert CRUD operations
 * - Alert activation/deactivation
 * - Alert type definitions
 * - Alert statistics
 *
 * @module services/alertService
 * @category Services
 */

import { api } from './api'

// ============================================================================
// ENUMS
// ============================================================================

/**
 * Alert type enumeration
 */
export enum AlertType {
  PRICE_ABOVE = 'PRICE_ABOVE',
  PRICE_BELOW = 'PRICE_BELOW',
  VOLUME_SPIKE = 'VOLUME_SPIKE',
  CHANGE_PERCENT_ABOVE = 'CHANGE_PERCENT_ABOVE',
  CHANGE_PERCENT_BELOW = 'CHANGE_PERCENT_BELOW',
}

// ============================================================================
// ALERT TYPES
// ============================================================================

/**
 * Stock information (minimal)
 */
export interface StockInfo {
  code: string
  name_kr: string | null
  name_en: string | null
}

/**
 * Alert entity from backend
 */
export interface Alert {
  id: number
  user_id: number
  stock_code: string
  alert_type: AlertType
  condition_value: number
  is_active: boolean
  is_recurring: boolean
  triggered_at: string | null // ISO datetime
  created_at: string // ISO datetime
  updated_at: string // ISO datetime
  stock: StockInfo | null
}

/**
 * Alert creation request
 */
export interface AlertCreate {
  stock_code: string
  alert_type: AlertType
  condition_value: number
  is_recurring?: boolean
}

/**
 * Alert update request
 */
export interface AlertUpdate {
  alert_type?: AlertType
  condition_value?: number
  is_recurring?: boolean
}

/**
 * Paginated alert list response
 */
export interface AlertListResponse {
  items: Alert[]
  total: number
  skip: number
  limit: number
}

/**
 * Alert toggle response
 */
export interface AlertToggleResponse {
  alert: Alert
  message: string
}

// ============================================================================
// SERVICE
// ============================================================================

/**
 * Alert Service singleton
 */
class AlertService {
  private readonly basePath = '/api/v1/alerts'

  /**
   * Get all alerts for current user
   *
   * @param params - Query parameters
   * @returns List of alerts
   *
   * @example
   * ```typescript
   * const alerts = await alertService.getAlerts();
   * ```
   */
  async getAlerts(params?: {
    skip?: number
    limit?: number
    alert_type?: AlertType
    is_active?: boolean
  }): Promise<Alert[]> {
    const response = await api.get<AlertListResponse>(this.basePath, { params })
    return response.items
  }

  /**
   * Get single alert by ID
   *
   * @param id - Alert ID
   * @returns Alert details
   *
   * @example
   * ```typescript
   * const alert = await alertService.getAlert(123);
   * ```
   */
  async getAlert(id: number): Promise<Alert> {
    return api.get<Alert>(`${this.basePath}/${id}`)
  }

  /**
   * Create new alert
   *
   * @param data - Alert creation data
   * @returns Created alert
   *
   * @example
   * ```typescript
   * const alert = await alertService.createAlert({
   *   stock_code: '005930',
   *   alert_type: AlertType.PRICE_ABOVE,
   *   condition_value: 70000,
   *   is_recurring: false,
   * });
   * ```
   */
  async createAlert(data: AlertCreate): Promise<Alert> {
    return api.post<Alert>(this.basePath, data)
  }

  /**
   * Update existing alert
   *
   * @param id - Alert ID
   * @param data - Alert update data
   * @returns Updated alert
   *
   * @example
   * ```typescript
   * const alert = await alertService.updateAlert(123, {
   *   condition_value: 75000,
   * });
   * ```
   */
  async updateAlert(id: number, data: AlertUpdate): Promise<Alert> {
    return api.put<Alert>(`${this.basePath}/${id}`, data)
  }

  /**
   * Delete alert
   *
   * @param id - Alert ID
   *
   * @example
   * ```typescript
   * await alertService.deleteAlert(123);
   * ```
   */
  async deleteAlert(id: number): Promise<void> {
    await api.delete(`${this.basePath}/${id}`)
  }

  /**
   * Toggle alert active status
   *
   * @param id - Alert ID
   * @returns Updated alert with toggle message
   *
   * @example
   * ```typescript
   * const result = await alertService.toggleAlert(123);
   * console.log(result.message); // "Alert activated" or "Alert deactivated"
   * ```
   */
  async toggleAlert(id: number): Promise<Alert> {
    const response = await api.post<AlertToggleResponse>(`${this.basePath}/${id}/toggle`)
    return response.alert
  }

  /**
   * Get alert type display name
   *
   * @param alertType - Alert type enum value
   * @returns Human-readable alert type
   *
   * @example
   * ```typescript
   * const displayName = alertService.getAlertTypeDisplay(AlertType.PRICE_ABOVE);
   * // Returns: "Price Above"
   * ```
   */
  getAlertTypeDisplay(alertType: AlertType): string {
    const displayNames: Record<AlertType, string> = {
      [AlertType.PRICE_ABOVE]: 'Price Above',
      [AlertType.PRICE_BELOW]: 'Price Below',
      [AlertType.VOLUME_SPIKE]: 'Volume Spike',
      [AlertType.CHANGE_PERCENT_ABOVE]: 'Price Up',
      [AlertType.CHANGE_PERCENT_BELOW]: 'Price Down',
    }
    return displayNames[alertType] || alertType
  }

  /**
   * Format alert condition for display
   *
   * @param alert - Alert object
   * @returns Formatted condition string
   *
   * @example
   * ```typescript
   * const condition = alertService.formatCondition(alert);
   * // For PRICE_ABOVE: "₩70,000 or higher"
   * // For VOLUME_SPIKE: "2.0x average volume"
   * ```
   */
  formatCondition(alert: Alert): string {
    const value = alert.condition_value

    switch (alert.alert_type) {
      case AlertType.PRICE_ABOVE:
        return `₩${value.toLocaleString()} or higher`
      case AlertType.PRICE_BELOW:
        return `₩${value.toLocaleString()} or lower`
      case AlertType.VOLUME_SPIKE:
        return `${value}x average volume`
      case AlertType.CHANGE_PERCENT_ABOVE:
        return `+${value}% or more`
      case AlertType.CHANGE_PERCENT_BELOW:
        return `-${Math.abs(value)}% or less`
      default:
        return value.toString()
    }
  }
}

// Export singleton instance
export const alertService = new AlertService()
