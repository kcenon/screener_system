---
id: srs-requirements
title: SRS - Requirements & Features
description: Functional requirements, external interfaces, and system features
sidebar_label: Requirements
sidebar_position: 2
tags:
  - specification
  - requirements
  - software
---

:::info Navigation
- [Introduction](introduction.md)
- [Requirements](requirements.md) (Current)
- [Non-Functional](nonfunctional-other.md)
:::

# Software Requirements Specification - Requirements

## 3. Specific Requirements

### 3.1 Functional Requirements

#### 3.1.1 User Authentication & Authorization

**REQ-AUTH-001: User Registration**
- **Description**: System shall allow users to register with email and password
- **Priority**: Critical
- **Inputs**: Email address, password (min 8 characters), name
- **Processing**:
  - Validate email format and uniqueness
  - Hash password using bcrypt (cost factor 12)
  - Send email verification link
  - Create user record in database
- **Outputs**: User account created, verification email sent
- **Error Handling**: Return error if email already exists or password too weak
- **Performance**: Registration must complete in < 2 seconds

**REQ-AUTH-002: Email Verification**
- **Description**: System shall verify user email addresses
- **Priority**: Critical
- **Inputs**: Verification token from email link
- **Processing**: Validate token, mark email as verified
- **Outputs**: Account activated, user can login
- **Error Handling**: Return error if token expired (24 hours) or invalid

**REQ-AUTH-003: User Login**
- **Description**: System shall authenticate users with email/password
- **Priority**: Critical
- **Inputs**: Email, password
- **Processing**:
  - Verify credentials against database
  - Generate JWT access token (15-minute expiry)
  - Generate refresh token (30-day expiry)
  - Log login event
- **Outputs**: Access token, refresh token, user profile
- **Error Handling**: Return 401 Unauthorized if credentials invalid, implement rate limiting (5 attempts/15 minutes)

**REQ-AUTH-004: OAuth Login**
- **Description**: System shall support OAuth login (Kakao, Naver, Google)
- **Priority**: High
- **Inputs**: OAuth provider, authorization code
- **Processing**: Exchange code for access token, fetch user profile, create/update user
- **Outputs**: JWT tokens, user profile
- **Error Handling**: Handle OAuth errors gracefully with user-friendly messages

**REQ-AUTH-005: Token Refresh**
- **Description**: System shall refresh expired access tokens
- **Priority**: Critical
- **Inputs**: Valid refresh token
- **Processing**: Validate refresh token, issue new access token
- **Outputs**: New access token
- **Error Handling**: Return 401 if refresh token invalid/revoked

**REQ-AUTH-006: Logout**
- **Description**: System shall revoke refresh tokens on logout
- **Priority**: Medium
- **Inputs**: Refresh token
- **Processing**: Revoke token in database
- **Outputs**: Success confirmation
- **Error Handling**: None (logout always succeeds)

**REQ-AUTH-007: Password Reset**
- **Description**: System shall allow password reset via email
- **Priority**: High
- **Inputs**: Email address
- **Processing**: Generate reset token, send email with reset link
- **Outputs**: Email sent confirmation
- **Error Handling**: Don't reveal if email exists (security)

**REQ-AUTH-008: Role-Based Access Control**
- **Description**: System shall enforce subscription tier permissions
- **Priority**: Critical
- **Inputs**: User subscription tier (free, basic, pro)
- **Processing**: Check permissions before allowing access to features
- **Outputs**: Access granted or 403 Forbidden
- **Error Handling**: Return clear message about required tier

#### 3.1.2 Stock Data Management

**REQ-STOCK-001: Stock Listing**
- **Description**: System shall provide paginated list of all stocks
- **Priority**: Critical
- **Inputs**: Market filter (KOSPI/KOSDAQ/ALL), sector filter, page, per_page
- **Processing**: Query stocks table with filters, apply pagination
- **Outputs**: Array of stocks with basic info, pagination metadata
- **Performance**: < 100ms response time
- **Error Handling**: Return empty array if no matches

**REQ-STOCK-002: Stock Detail**
- **Description**: System shall provide detailed information for individual stocks
- **Priority**: Critical
- **Inputs**: Stock code (6 digits)
- **Processing**:
  - Fetch stock from database
  - Retrieve latest price from daily_prices
  - Retrieve latest indicators from calculated_indicators
  - Aggregate data into response
- **Outputs**: Stock details with current price and indicators
- **Performance**: < 150ms response time
- **Error Handling**: Return 404 if stock code not found

**REQ-STOCK-003: Historical Prices**
- **Description**: System shall provide historical OHLCV data
- **Priority**: High
- **Inputs**: Stock code, from_date, to_date, interval (daily/weekly/monthly)
- **Processing**:
  - Validate date range (max 10 years)
  - Query daily_prices or aggregated views
  - Format data for charting
- **Outputs**: Array of price data points
- **Performance**: < 300ms for 1 year daily data
- **Error Handling**: Return error if date range invalid

**REQ-STOCK-004: Financial Statements**
- **Description**: System shall provide financial statement history
- **Priority**: High
- **Inputs**: Stock code, period_type (quarterly/annual), years (default 5)
- **Processing**: Query financial_statements table, order by fiscal_year DESC
- **Outputs**: Array of financial statements
- **Performance**: < 200ms
- **Error Handling**: Return empty array if no data available

**REQ-STOCK-005: Stock Search**
- **Description**: System shall support fuzzy search by stock name or code
- **Priority**: High
- **Inputs**: Search query string
- **Processing**: Use trigram similarity search (pg_trgm), return top 10 matches
- **Outputs**: Array of matching stocks
- **Performance**: < 100ms autocomplete response
- **Error Handling**: Return empty array if no matches

#### 3.1.3 Stock Screening

**REQ-SCREEN-001: Basic Screening**
- **Description**: System shall filter stocks using custom criteria
- **Priority**: Critical
- **Inputs**:
  - Market (KOSPI/KOSDAQ/ALL)
  - Filters object (key-value pairs with min/max)
  - Sort field and order
  - Pagination parameters
- **Processing**:
  - Query stock_screening_view (materialized view)
  - Apply filters dynamically
  - Sort results
  - Paginate
- **Outputs**: Filtered stock list with metadata
- **Performance**: < 500ms (p99) for complex queries
- **Error Handling**: Return error if invalid filter field

**REQ-SCREEN-002: Template-Based Screening**
- **Description**: System shall provide pre-built screening templates
- **Priority**: High
- **Inputs**: Template ID or category
- **Processing**: Load template filter configuration, execute screening
- **Outputs**: Template info and screening results
- **Performance**: Same as REQ-SCREEN-001
- **Error Handling**: Return 404 if template not found

**REQ-SCREEN-003: Custom Screen Saving**
- **Description**: Authenticated users shall save custom screening criteria
- **Priority**: Medium
- **Inputs**: Screen name, filter configuration
- **Processing**: Store in saved_screens table
- **Outputs**: Saved screen confirmation
- **Error Handling**: Prevent duplicate names for same user

**REQ-SCREEN-004: Screening Results Export**
- **Description**: Premium users shall export results to CSV/Excel
- **Priority**: Medium
- **Inputs**: Screening results
- **Processing**: Convert to CSV/XLSX format
- **Outputs**: Downloadable file
- **Performance**: < 2 seconds for 1000 rows
- **Error Handling**: Limit to 5000 rows to prevent abuse

#### 3.1.4 Market Insights

**REQ-MARKET-001: Market Overview**
- **Description**: System shall display current market statistics
- **Priority**: High
- **Inputs**: None (current date implied)
- **Processing**: Execute get_market_overview() database function
- **Outputs**: KOSPI and KOSDAQ statistics (advancers, decliners, volume, etc.)
- **Performance**: < 100ms (cached for 5 minutes)
- **Error Handling**: Return last known good data if calculation fails

**REQ-MARKET-002: Hot Stocks Detection**
- **Description**: System shall identify stocks with significant volume surge
- **Priority**: High
- **Inputs**: Minimum surge percentage (default 150%), limit (default 20)
- **Processing**: Execute get_hot_stocks() database function
- **Outputs**: Array of hot stocks with volume metrics
- **Performance**: < 200ms (cached for 5 minutes during market hours)
- **Error Handling**: Return empty array if market closed

**REQ-MARKET-003: Top Movers**
- **Description**: System shall show top gainers/losers by timeframe
- **Priority**: High
- **Inputs**: Type (gainers/losers), period (1d/1w/1m/etc.), limit
- **Processing**: Execute get_top_movers() database function
- **Outputs**: Ranked list of stocks by price change
- **Performance**: < 150ms (cached for 5 minutes)
- **Error Handling**: Return error if invalid period

**REQ-MARKET-004: Sector Performance**
- **Description**: System shall display sector-level performance
- **Priority**: Medium
- **Inputs**: None
- **Processing**: Query sector_performance materialized view
- **Outputs**: Sector statistics with price changes
- **Performance**: < 100ms
- **Error Handling**: None

#### 3.1.5 Portfolio Management

**REQ-PORT-001: Create Portfolio**
- **Description**: Authenticated users shall create portfolios
- **Priority**: High
- **Inputs**: Portfolio name, description (optional)
- **Processing**: Insert into portfolios table
- **Outputs**: Created portfolio object
- **Error Handling**: Prevent duplicate names for same user, enforce tier limits (Free: 1, Basic: 3, Pro: unlimited)

**REQ-PORT-002: List Portfolios**
- **Description**: Users shall view their portfolios
- **Priority**: High
- **Inputs**: User authentication
- **Processing**: Query portfolios for current user
- **Outputs**: Array of user's portfolios
- **Performance**: < 100ms
- **Error Handling**: Return empty array if no portfolios

**REQ-PORT-003: Portfolio Detail**
- **Description**: System shall show portfolio with holdings and performance
- **Priority**: High
- **Inputs**: Portfolio ID
- **Processing**:
  - Execute calculate_portfolio_value() function
  - Fetch holdings with current prices
  - Calculate gains/losses
- **Outputs**: Portfolio details with performance metrics
- **Performance**: < 200ms
- **Error Handling**: Return 404 if portfolio not found or unauthorized

**REQ-PORT-004: Add Holding**
- **Description**: Users shall add stocks to portfolio
- **Priority**: High
- **Inputs**: Portfolio ID, stock code, quantity, average price, purchase date
- **Processing**: Insert into portfolio_holdings
- **Outputs**: Created holding object
- **Error Handling**: Prevent duplicate stocks in same portfolio (update quantity instead)

**REQ-PORT-005: Update Holding**
- **Description**: Users shall modify holding details
- **Priority**: Medium
- **Inputs**: Holding ID, updated fields
- **Processing**: Update portfolio_holdings record
- **Outputs**: Updated holding object
- **Error Handling**: Return 404 if holding not found

**REQ-PORT-006: Delete Holding**
- **Description**: Users shall remove stocks from portfolio
- **Priority**: Medium
- **Inputs**: Holding ID
- **Processing**: Delete from portfolio_holdings
- **Outputs**: Success confirmation
- **Error Handling**: Return 404 if not found

**REQ-PORT-007: Portfolio Performance**
- **Description**: System shall calculate portfolio vs benchmark performance
- **Priority**: Medium
- **Inputs**: Portfolio ID, comparison index (KOSPI/KOSDAQ)
- **Processing**: Calculate portfolio returns, fetch index returns, compute relative performance
- **Outputs**: Performance comparison data
- **Performance**: < 300ms
- **Error Handling**: Handle missing index data gracefully

#### 3.1.6 Alerts & Notifications

**REQ-ALERT-001: Create Price Alert**
- **Description**: Users shall create price alerts
- **Priority**: High
- **Inputs**: Stock code, condition (above/below), threshold value, notification channels
- **Processing**: Insert into alerts table
- **Outputs**: Created alert object
- **Error Handling**: Enforce tier limits (Free: 3, Basic: 10, Pro: unlimited)

**REQ-ALERT-002: Create Volume Alert**
- **Description**: Users shall create volume surge alerts
- **Priority**: Medium
- **Inputs**: Stock code, surge percentage threshold
- **Processing**: Insert into alerts table
- **Outputs**: Created alert object
- **Error Handling**: Same as REQ-ALERT-001

**REQ-ALERT-003: List Alerts**
- **Description**: Users shall view their active alerts
- **Priority**: High
- **Inputs**: User authentication, filter (active/triggered/all)
- **Processing**: Query alerts table
- **Outputs**: Array of user's alerts
- **Performance**: < 100ms
- **Error Handling**: None

**REQ-ALERT-004: Delete Alert**
- **Description**: Users shall delete alerts
- **Priority**: High
- **Inputs**: Alert ID
- **Processing**: Delete from alerts table
- **Outputs**: Success confirmation
- **Error Handling**: Return 404 if not found or unauthorized

**REQ-ALERT-005: Alert Checking**
- **Description**: System shall check alerts every 5 minutes during market hours
- **Priority**: Critical
- **Inputs**: None (automated process)
- **Processing**: Execute check_price_alerts() function, trigger notifications
- **Outputs**: Triggered alerts logged
- **Performance**: Must complete within 5 minutes for all alerts
- **Error Handling**: Retry failed notifications up to 3 times

**REQ-ALERT-006: Email Notifications**
- **Description**: System shall send email notifications for triggered alerts
- **Priority**: High
- **Inputs**: Alert data, user email
- **Processing**: Format email template, send via SMTP
- **Outputs**: Email delivered
- **Performance**: < 10 seconds delivery
- **Error Handling**: Log failed deliveries, retry up to 3 times

**REQ-ALERT-007: Push Notifications**
- **Description**: System shall send browser push notifications
- **Priority**: Low
- **Inputs**: Alert data, user subscription
- **Processing**: Send via Web Push API
- **Outputs**: Notification displayed
- **Error Handling**: Gracefully handle denied permissions

#### 3.1.7 Watchlists

**REQ-WATCH-001: Create Watchlist**
- **Description**: Users shall create named watchlists
- **Priority**: Medium
- **Inputs**: Watchlist name
- **Processing**: Insert into watchlists table
- **Outputs**: Created watchlist object
- **Error Handling**: Prevent duplicate names for same user

**REQ-WATCH-002: Add to Watchlist**
- **Description**: Users shall add stocks to watchlist
- **Priority**: Medium
- **Inputs**: Watchlist ID, stock code, notes (optional)
- **Processing**: Insert into watchlist_items
- **Outputs**: Added item confirmation
- **Error Handling**: Prevent duplicate stocks in same watchlist

**REQ-WATCH-003: Remove from Watchlist**
- **Description**: Users shall remove stocks from watchlist
- **Priority**: Medium
- **Inputs**: Watchlist item ID
- **Processing**: Delete from watchlist_items
- **Outputs**: Success confirmation
- **Error Handling**: Return 404 if not found

**REQ-WATCH-004: View Watchlist**
- **Description**: Users shall view watchlist with current prices
- **Priority**: Medium
- **Inputs**: Watchlist ID
- **Processing**: Query watchlist_items with latest prices
- **Outputs**: Watchlist details with stock data
- **Performance**: < 200ms
- **Error Handling**: Return 404 if not found

#### 3.1.8 Subscription & Billing

**REQ-SUB-001: Subscription Tiers**
- **Description**: System shall enforce three subscription tiers
- **Priority**: Critical
- **Tiers**:
  - **Free**: 10 filters, 1 portfolio, 3 alerts, 20-min delayed data
  - **Basic** (₩9,900/mo): Unlimited filters, 3 portfolios, 10 alerts, real-time data
  - **Pro** (₩29,900/mo): All Basic features + unlimited portfolios/alerts, API access, export
- **Processing**: Check user subscription tier before feature access
- **Outputs**: Access granted or 403 Forbidden
- **Error Handling**: Return clear upgrade message

**REQ-SUB-002: Subscription Upgrade**
- **Description**: Users shall upgrade subscription
- **Priority**: High
- **Inputs**: Target tier, payment method
- **Processing**: Process payment, update user subscription tier
- **Outputs**: Subscription confirmation
- **Error Handling**: Handle payment failures gracefully

**REQ-SUB-003: Subscription Cancellation**
- **Description**: Users shall cancel subscription (no refund)
- **Priority**: High
- **Inputs**: User confirmation
- **Processing**: Mark subscription for cancellation at period end
- **Outputs**: Cancellation confirmation
- **Error Handling**: None

**REQ-SUB-004: Billing History**
- **Description**: Users shall view payment history
- **Priority**: Medium
- **Inputs**: User authentication
- **Processing**: Query payment records
- **Outputs**: Array of invoices
- **Performance**: < 150ms
- **Error Handling**: None

#### 3.1.9 Data Pipeline

**REQ-DATA-001: Daily Price Ingestion**
- **Description**: System shall ingest daily prices for all stocks after market close
- **Priority**: Critical
- **Schedule**: Mon-Fri at 18:00 KST
- **Processing**:
  - Fetch data from KRX API
  - Validate data quality (price relationships, non-negative values)
  - Upsert to daily_prices table
  - Verify ≥95% completeness
- **Outputs**: Daily prices loaded, data quality report
- **Performance**: Complete within 5 minutes
- **Error Handling**: Retry failed API calls 3 times, email alert if &lt;95% complete

**REQ-DATA-002: Indicator Calculation**
- **Description**: System shall calculate 200+ indicators for all stocks daily
- **Priority**: Critical
- **Trigger**: After REQ-DATA-001 completes
- **Processing**:
  - Calculate indicators for each stock
  - Upsert to calculated_indicators table
  - Refresh materialized views
- **Outputs**: Indicators updated
- **Performance**: Complete within 20 minutes for 2,400 stocks
- **Error Handling**: Log failed stocks, continue processing others

**REQ-DATA-003: Financial Statement Updates**
- **Description**: System shall ingest quarterly/annual financials
- **Priority**: High
- **Schedule**: Weekly check for new reports
- **Processing**: Fetch from F&Guide API, validate, upsert to financial_statements
- **Outputs**: New financials loaded
- **Performance**: < 10 minutes
- **Error Handling**: Retry failures, alert on persistent errors

**REQ-DATA-004: Data Quality Monitoring**
- **Description**: System shall monitor data completeness and accuracy
- **Priority**: High
- **Schedule**: Daily after data pipelines
- **Processing**: Execute check_data_completeness() function, log results
- **Outputs**: Data quality report
- **Error Handling**: Alert if quality below threshold

**REQ-DATA-005: Real-time Data Source Integration**
- **Description**: System shall integrate with Korea Investment & Securities (KIS) API for real-time market data
- **Priority**: Critical
- **Data Sources**:
  - Primary: KIS API (한국투자증권 Open API)
  - Fallback: KRX Public Data Portal
  - Development: Mock data source
- **Data Types**:
  - Current prices (현재가) - 3-5 second delay
  - Order book (호가) - 10-level bid/ask depth
  - Historical chart data (OHLCV)
  - Stock information
- **Authentication**: OAuth 2.0 with automatic token refresh
- **Rate Limiting**: Maximum 20 requests/second (KIS API limit)
- **Caching**: Redis cache with TTL (prices: 30min, order book: 10sec)
- **Error Handling**:
  - Circuit breaker on repeated failures (threshold: 5)
  - Automatic fallback to cached data
  - Retry with exponential backoff
  - Alert on authentication failures
- **Performance**: API latency < 200ms (p95)
- **Reliability**: 99.9% success rate during market hours

---

## 4. External Interface Requirements

### 4.1 User Interfaces

**UI-001: Responsive Design**
- **Description**: All user interfaces shall be responsive across devices
- **Requirements**:
  - Support screen widths from 360px (mobile) to 3840px (4K desktop)
  - Touch-friendly tap targets (minimum 44x44px)
  - Readable text (minimum 16px base font size)
  - Consistent navigation across breakpoints

**UI-002: Accessibility**
- **Description**: Interfaces shall meet WCAG 2.1 Level AA standards
- **Requirements**:
  - Keyboard navigation support (Tab, Enter, Esc)
  - Screen reader compatibility (semantic HTML, ARIA labels)
  - Color contrast ratios: 4.5:1 for text, 3:1 for UI components
  - Focus indicators visible on all interactive elements

**UI-003: Screener Interface**
- **Layout**: Two-panel layout (filters left, results right)
- **Components**:
  - Filter panel with collapsible sections
  - Results table with sortable columns
  - Pagination controls
  - Template selector dropdown
- **Interactions**:
  - Real-time result updates as filters change (debounced 500ms)
  - Click stock row to navigate to detail page
  - Export button (for Premium users)

**UI-004: Stock Detail Interface**
- **Layout**: Tab-based layout (Overview, Financials, Valuation, Technical)
- **Components**:
  - Stock header (name, code, current price, change %)
  - Interactive price chart (TradingView Lightweight Charts)
  - Metric cards (PER, PBR, ROE, etc.)
  - Financial statement tables
  - Add to watchlist/portfolio buttons
- **Interactions**:
  - Chart timeframe selection (1D, 1W, 1M, 3M, 6M, 1Y, 5Y)
  - Hover tooltips on metrics with explanations
  - Tab switching without page reload

**UI-005: Portfolio Interface**
- **Layout**: Portfolio selector with detail view
- **Components**:
  - Portfolio cards with summary metrics
  - Holdings table (stock, quantity, avg price, current value, gain/loss)
  - Performance chart (portfolio vs benchmark)
  - Asset allocation pie chart
  - Add holding modal
- **Interactions**:
  - Switch between portfolios
  - Inline editing of holdings
  - Drag-and-drop reordering (optional)

**UI-006: Color Scheme**
- **Primary Colors**:
  - Brand: #2563eb (Blue)
  - Success/Gains: #10b981 (Green)
  - Danger/Losses: #ef4444 (Red)
  - Warning: #f59e0b (Yellow)
  - Neutral: #6b7280 (Gray)
- **Dark Mode**: Optional (Phase 2+)

**UI-007: Order Book Display (호가)**
- **Description**: Real-time order book visualization showing 10-level bid/ask depth
- **Layout**: Two-column grid (Ask levels on top, Bid levels on bottom)
- **Components**:
  - 10 ask levels (매도 호가) - price, volume, total volume
  - 10 bid levels (매수 호가) - price, volume, total volume
  - Price spread indicator (best_ask - best_bid)
  - Spread percentage display
  - Mid-price calculation
  - Volume visualization bars (horizontal bars showing relative volume)
  - Buy/sell pressure indicator (cumulative volume ratio)
  - Last update timestamp
- **Interactions**:
  - Real-time WebSocket updates (< 100ms latency)
  - Flash animation on price changes (highlight changed rows)
  - Freeze/unfreeze button to pause updates
  - Click price level to populate order entry (Phase 2+)
  - Hover tooltips explaining bid/ask concepts
- **Color Coding**:
  - Ask levels: Red (#ef4444) background
  - Bid levels: Blue (#2563eb) background
  - Best bid/ask: Highlighted with border
- **Responsive Behavior**:
  - Desktop: Show full 10-level depth
  - Tablet: Show 5-level depth
  - Mobile: Show best bid/ask only with expandable full view
- **Performance**: Smooth animations even with 100+ updates/second
- **Accessibility**: Screen reader announces price changes for important levels

### 4.2 Hardware Interfaces

Not applicable (web-based application, no direct hardware interfaces)

### 4.3 Software Interfaces

**SI-001: KRX API Interface**
- **Interface Type**: RESTful HTTP API
- **Protocol**: HTTPS
- **Authentication**: API Key in Authorization header
- **Data Format**: JSON
- **Operations**:
  - `GET /market/stocks/prices?date={YYYY-MM-DD}`: Fetch daily prices
  - `GET /market/stocks/{code}/info`: Fetch stock info
- **Error Handling**: Retry up to 3 times with exponential backoff
- **Rate Limit**: 100 requests/minute (to be confirmed with KRX)

**SI-002: F&Guide API Interface**
- **Interface Type**: RESTful HTTP API
- **Protocol**: HTTPS
- **Authentication**: OAuth 2.0
- **Data Format**: JSON or XML (to be confirmed)
- **Operations**:
  - `GET /financials/{stock_code}?period={quarterly|annual}`: Fetch financial statements
  - `GET /consensus/{stock_code}`: Fetch analyst consensus (Phase 2)
- **Error Handling**: Retry failed requests, alert on persistent failures
- **Rate Limit**: 500 requests/minute (to be confirmed)

**SI-003: Payment Gateway Interface (Stripe)**
- **Interface Type**: RESTful HTTP API + Webhooks
- **Protocol**: HTTPS
- **Authentication**: API Key (secret)
- **Data Format**: JSON
- **Operations**:
  - `POST /v1/checkout/sessions`: Create payment session
  - `POST /v1/subscriptions`: Create subscription
  - Webhook: `invoice.paid`, `subscription.deleted`
- **Error Handling**: Handle payment failures, retry webhooks
- **Compliance**: PCI DSS Level 1 (handled by Stripe)

**SI-004: Email Service Interface (SMTP)**
- **Interface Type**: SMTP protocol
- **Server**: Gmail SMTP (smtp.gmail.com:587) or SendGrid
- **Authentication**: Username/password or API key
- **Operations**:
  - Send email notifications (alerts, verification, password reset)
- **Error Handling**: Retry failed sends up to 3 times
- **Rate Limit**: 500 emails/day (Gmail), higher with SendGrid

**SI-005: OAuth Providers**
- **Providers**: Kakao, Naver, Google
- **Protocol**: OAuth 2.0
- **Operations**:
  - Authorization code flow
  - Exchange code for access token
  - Fetch user profile
- **Error Handling**: Display user-friendly error messages

**SI-006: KIS API Interface (Korea Investment & Securities)**
- **Interface Type**: RESTful HTTP API
- **Protocol**: HTTPS
- **Base URL**: https://openapi.koreainvestment.com:9443 (production)
- **Authentication**: OAuth 2.0 with automatic token refresh
  - Access token expiry: 24 hours
  - Refresh token: Auto-refresh before expiration
  - Token storage: Secure encrypted storage
- **Data Format**: JSON
- **Operations**:
  - `POST /oauth2/tokenP`: Get OAuth access token
  - `GET /uapi/domestic-stock/v1/quotations/inquire-price`: Current price (현재가)
  - `GET /uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn`: Order book (호가)
  - `GET /uapi/domestic-stock/v1/quotations/inquire-daily-price`: Historical OHLCV
  - `GET /uapi/domestic-stock/v1/quotations/search-stock-info`: Stock information
- **Rate Limiting**:
  - Maximum 20 requests/second (API limit)
  - Request queue with priority (real-time > batch)
  - Token bucket algorithm for smooth rate limiting
- **Error Handling**:
  - Circuit breaker pattern (CLOSED → OPEN → HALF_OPEN)
  - Circuit opens after 5 consecutive failures
  - Half-open test after 60 seconds
  - Exponential backoff: 1s, 2s, 4s, 8s
  - Fallback to cached data when circuit open
  - Alert on authentication failures
- **Caching Strategy**:
  - Current prices: 30 minutes TTL
  - Order book: 10 seconds TTL
  - Stock info: 24 hours TTL
  - 80%+ cache hit rate target
- **Connection Pooling**:
  - Keep-alive connections
  - Connection pool size: 10-20 connections
  - Connection timeout: 5 seconds
  - Read timeout: 10 seconds
- **Data Latency**: 3-5 seconds delay from real-time (API characteristic)
- **Reliability Target**: 99.9% success rate during market hours (09:00-15:30 KST)

### 4.4 Communications Interfaces

**CI-001: HTTP/HTTPS Protocol**
- **Client-Server**: HTTPS (TLS 1.3) for all API requests
- **Ports**: 80 (HTTP, redirect to HTTPS), 443 (HTTPS)
- **Compression**: gzip or brotli for API responses

**CI-002: WebSocket Protocol**
- **Purpose**: Real-time price and order book updates during market hours
- **Protocol**: WSS (WebSocket Secure over TLS 1.3)
- **Port**: 443
- **Message Format**: JSON with gzip compression
- **Connection Management**:
  - Heartbeat: Ping/pong every 30 seconds
  - Connection timeout: 30 seconds idle
  - Automatic reconnection with exponential backoff
  - JWT authentication in handshake
- **Subscription System**:
  - Room-based subscriptions (stock code, market, sector)
  - Multiple subscriptions per connection
  - Subscribe/unsubscribe messages
  - Only receive subscribed updates
- **Message Types**:
  - `price_update`: Current price changes
  - `orderbook_update`: Order book (호가) changes
  - `market_status`: Market open/close events
  - `alert`: User alert notifications
  - `error`: Error messages
- **Message Structure**:
  - Event type field
  - Timestamp (ISO 8601 format)
  - Sequence number (for ordering)
  - Data payload (event-specific)
- **Performance**:
  - Message latency: < 100ms (p99)
  - Support 10,000+ concurrent connections
  - Message batching: 10-50ms window
  - Delivery rate: 99.9%
- **Scalability**: Redis Pub/Sub for multi-instance broadcasting
- **Rate Limiting**: 100 messages/second per connection

**CI-003: Database Protocol**
- **Protocol**: PostgreSQL wire protocol
- **Port**: 5432 (internal network only, not exposed publicly)
- **Connection Pooling**: Max 20 connections per application instance
- **SSL**: Enabled for production

**CI-004: Cache Protocol**
- **Protocol**: Redis RESP (REdis Serialization Protocol)
- **Port**: 6379 (internal network only)
- **Authentication**: Password-protected
- **Persistence**: AOF (Append-Only File) enabled

---

## 5. System Features

### 5.1 Stock Screening Feature

**5.1.1 Description and Priority**
- **Priority**: Critical (Highest)
- **Description**: Core feature allowing users to filter stocks using multiple criteria

**5.1.2 Stimulus/Response Sequences**
1. User selects filters (market, PER < 15, ROE > 10%)
2. System queries database with filters
3. System returns matching stocks sorted by market cap
4. User clicks "Export to CSV"
5. System generates CSV file
6. User downloads file

**5.1.3 Functional Requirements**
- See REQ-SCREEN-001 through REQ-SCREEN-004

### 5.2 Real-Time Market Insights Feature

**5.2.1 Description and Priority**
- **Priority**: High
- **Description**: Provides users with current market trends and opportunities

**5.2.2 Stimulus/Response Sequences**
1. User navigates to homepage
2. System displays market overview (cached data)
3. System shows hot stocks (volume surge > 150%)
4. User clicks on hot stock
5. System navigates to stock detail page

**5.2.3 Functional Requirements**
- See REQ-MARKET-001 through REQ-MARKET-004

### 5.3 Portfolio Tracking Feature

**5.3.1 Description and Priority**
- **Priority**: High
- **Description**: Enables users to track holdings and performance

**5.3.2 Stimulus/Response Sequences**
1. User creates portfolio "Growth Portfolio"
2. User adds Samsung Electronics: 10 shares @ ₩68,000
3. System calculates current value using latest price (₩70,500)
4. System shows unrealized gain: ₩25,000 (+3.68%)
5. User compares portfolio vs KOSPI index
6. System displays relative performance chart

**5.3.3 Functional Requirements**
- See REQ-PORT-001 through REQ-PORT-007

### 5.4 Price Alert Feature

**5.4.1 Description and Priority**
- **Priority**: High
- **Description**: Notifies users when stocks meet specified conditions

**5.4.2 Stimulus/Response Sequences**
1. User creates alert: Samsung > ₩75,000
2. System stores alert in database
3. Automated job checks alerts every 5 minutes
4. Samsung price reaches ₩75,500
5. System triggers alert
6. System sends email notification
7. User receives email: "Alert triggered for Samsung Electronics"

**5.4.3 Functional Requirements**
- See REQ-ALERT-001 through REQ-ALERT-007

---