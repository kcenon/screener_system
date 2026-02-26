/**
 * WebSocket Service for Real-time Stock Data (FE-005)
 *
 * Connects to backend WebSocket endpoint (BE-006) for real-time updates:
 * - Price updates
 * - Order book updates
 * - Market alerts
 *
 * Features:
 * - Automatic reconnection with exponential backoff
 * - JWT authentication
 * - Heartbeat/ping-pong
 * - Subscription management
 * - Message sequencing
 */

import { OrderBookData } from '@/types/stock'

/**
 * WebSocket connection state
 */
export type WSConnectionState =
  | 'connecting'
  | 'connected'
  | 'disconnecting'
  | 'disconnected'
  | 'error'

/**
 * Subscription types supported by backend
 */
export type SubscriptionType = 'stock' | 'market' | 'sector' | 'watchlist'

/**
 * WebSocket message types from backend (BE-006)
 */
export type WSMessageType =
  | 'connected'
  | 'subscribed'
  | 'unsubscribed'
  | 'price_update'
  | 'orderbook_update'
  | 'market_status'
  | 'alert'
  | 'error'
  | 'pong'

/**
 * Base WebSocket message structure
 */
interface WSMessage {
  type: WSMessageType
  timestamp: string
  sequence?: number
}

/**
 * Price update message
 */
interface PriceUpdateMessage extends WSMessage {
  type: 'price_update'
  data: {
    stock_code: string
    price: number
    change: number
    change_pct: number
    volume: number
  }
}

/**
 * Order book update message
 */
interface OrderBookUpdateMessage extends WSMessage {
  type: 'orderbook_update'
  data: OrderBookData
}

/**
 * Error message
 */
interface ErrorMessage extends WSMessage {
  type: 'error'
  error: {
    code: string
    message: string
  }
}

/**
 * Union type for all possible messages
 */
type WSIncomingMessage =
  | PriceUpdateMessage
  | OrderBookUpdateMessage
  | ErrorMessage
  | WSMessage

/**
 * Message handler callback type
 */
type MessageHandler = (message: WSIncomingMessage) => void

/**
 * Connection state change callback type
 */
type StateChangeHandler = (state: WSConnectionState) => void

/**
 * WebSocket Service Configuration
 */
interface WSServiceConfig {
  /** WebSocket endpoint URL */
  url: string
  /** JWT access token */
  token: string
  /** Auto-reconnect on disconnect */
  autoReconnect?: boolean
  /** Max reconnection attempts (0 = infinite) */
  maxReconnectAttempts?: number
  /** Initial reconnect delay (ms) */
  reconnectDelay?: number
  /** Max reconnect delay (ms) */
  maxReconnectDelay?: number
  /** Heartbeat interval (ms) */
  heartbeatInterval?: number
}

/**
 * WebSocket Service Class
 *
 * Manages WebSocket connection lifecycle and subscriptions
 */
export class WebSocketService {
  private ws: WebSocket | null = null
  private config: WSServiceConfig
  private state: WSConnectionState = 'disconnected'
  private messageHandlers: Set<MessageHandler> = new Set()
  private stateHandlers: Set<StateChangeHandler> = new Set()
  private reconnectAttempts = 0
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null
  private subscriptions: Set<string> = new Set()
  private sessionId: string | null = null

  constructor(config: WSServiceConfig) {
    this.config = {
      autoReconnect: true,
      maxReconnectAttempts: 10,
      reconnectDelay: 1000,
      maxReconnectDelay: 30000,
      heartbeatInterval: 30000,
      ...config,
    }
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.state === 'connected' || this.state === 'connecting') {
      console.warn('WebSocket is already connected or connecting')
      return
    }

    this.setState('connecting')

    try {
      // Build WebSocket URL with JWT token
      const url = new URL(this.config.url)
      url.searchParams.set('token', this.config.token)

      // Add session_id for reconnection if available
      if (this.sessionId) {
        url.searchParams.set('session_id', this.sessionId)
      }

      this.ws = new WebSocket(url.toString())

      this.ws.onopen = this.handleOpen.bind(this)
      this.ws.onmessage = this.handleMessage.bind(this)
      this.ws.onerror = this.handleError.bind(this)
      this.ws.onclose = this.handleClose.bind(this)
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      this.setState('error')
      this.attemptReconnect()
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.setState('disconnecting')
    this.stopHeartbeat()
    this.clearReconnectTimer()

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }

    this.setState('disconnected')
  }

  /**
   * Subscribe to stock updates
   */
  subscribe(type: SubscriptionType, identifier: string): void {
    const key = `${type}:${identifier}`

    if (this.subscriptions.has(key)) {
      console.warn(`Already subscribed to ${key}`)
      return
    }

    this.subscriptions.add(key)

    if (this.state === 'connected') {
      this.send({
        action: 'subscribe',
        subscription_type: type,
        identifier,
      })
    }
  }

  /**
   * Unsubscribe from stock updates
   */
  unsubscribe(type: SubscriptionType, identifier: string): void {
    const key = `${type}:${identifier}`

    if (!this.subscriptions.has(key)) {
      console.warn(`Not subscribed to ${key}`)
      return
    }

    this.subscriptions.delete(key)

    if (this.state === 'connected') {
      this.send({
        action: 'unsubscribe',
        subscription_type: type,
        identifier,
      })
    }
  }

  /**
   * Add message handler
   */
  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler)

    // Return cleanup function
    return () => {
      this.messageHandlers.delete(handler)
    }
  }

  /**
   * Add state change handler
   */
  onStateChange(handler: StateChangeHandler): () => void {
    this.stateHandlers.add(handler)

    // Return cleanup function
    return () => {
      this.stateHandlers.delete(handler)
    }
  }

  /**
   * Get current connection state
   */
  getState(): WSConnectionState {
    return this.state
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.state === 'connected'
  }

  /**
   * Handle WebSocket open event
   */
  private handleOpen(): void {
    console.log('WebSocket connected')
    this.setState('connected')
    this.reconnectAttempts = 0
    this.startHeartbeat()

    // Re-subscribe to all previous subscriptions
    this.subscriptions.forEach(key => {
      const [type, identifier] = key.split(':')
      this.send({
        action: 'subscribe',
        subscription_type: type as SubscriptionType,
        identifier,
      })
    })
  }

  /**
   * Handle WebSocket message event
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WSIncomingMessage = JSON.parse(event.data)

      // Handle connected message with session_id
      if (message.type === 'connected' && 'session_id' in message) {
        this.sessionId = (message as any).session_id
      }

      // Notify all handlers
      this.messageHandlers.forEach(handler => {
        try {
          handler(message)
        } catch (error) {
          console.error('Message handler error:', error)
        }
      })
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error)
    }
  }

  /**
   * Handle WebSocket error event
   */
  private handleError(event: Event): void {
    console.error('WebSocket error:', event)
    this.setState('error')
  }

  /**
   * Handle WebSocket close event
   */
  private handleClose(event: CloseEvent): void {
    console.log('WebSocket closed:', event.code, event.reason)
    this.stopHeartbeat()

    if (this.state !== 'disconnecting') {
      this.setState('disconnected')
      this.attemptReconnect()
    } else {
      this.setState('disconnected')
    }
  }

  /**
   * Send message to server
   */
  private send(data: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('Cannot send message: WebSocket not connected')
      return
    }

    try {
      this.ws.send(JSON.stringify(data))
    } catch (error) {
      console.error('Failed to send WebSocket message:', error)
    }
  }

  /**
   * Start heartbeat timer
   */
  private startHeartbeat(): void {
    this.stopHeartbeat()

    this.heartbeatTimer = setInterval(() => {
      this.send({ action: 'ping' })
    }, this.config.heartbeatInterval)
  }

  /**
   * Stop heartbeat timer
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(): void {
    if (!this.config.autoReconnect) {
      return
    }

    if (
      this.config.maxReconnectAttempts! > 0 &&
      this.reconnectAttempts >= this.config.maxReconnectAttempts!
    ) {
      console.error('Max reconnection attempts reached')
      this.setState('error')
      return
    }

    this.reconnectAttempts++

    // Exponential backoff: delay * 2^attempts, capped at maxReconnectDelay
    const delay = Math.min(
      this.config.reconnectDelay! * Math.pow(2, this.reconnectAttempts - 1),
      this.config.maxReconnectDelay!,
    )

    console.log(
      `Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})...`,
    )

    this.reconnectTimer = setTimeout(() => {
      this.connect()
    }, delay)
  }

  /**
   * Clear reconnection timer
   */
  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  /**
   * Update connection state and notify handlers
   */
  private setState(newState: WSConnectionState): void {
    if (this.state === newState) {
      return
    }

    console.log(`WebSocket state: ${this.state} -> ${newState}`)
    this.state = newState

    this.stateHandlers.forEach(handler => {
      try {
        handler(newState)
      } catch (error) {
        console.error('State handler error:', error)
      }
    })
  }
}

/**
 * Create WebSocket service instance
 */
export function createWebSocketService(token: string): WebSocketService {
  const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/v1/ws'

  return new WebSocketService({
    url: wsUrl,
    token,
  })
}
