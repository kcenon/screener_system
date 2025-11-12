---
id: prd-users-features
title: PRD - Users & Features
description: User personas, use cases, and feature requirements
sidebar_label: Users & Features
sidebar_position: 2
tags:
  - specification
  - product
  - requirements
---

:::info Navigation
- [Overview](overview.md)
- [Users & Features](users-features.md) (Current)
- [Technical](technical.md)
- [Implementation](implementation.md)
:::

# Product Requirements Document - Users & Features

## 4. User Personas & Use Cases

### 4.1 Primary Personas

#### Persona 1: "Novice Nina" - The Beginner Investor

**Demographics**
- Age: 28
- Occupation: Office worker
- Income: ₩40M/year
- Investment Experience: < 1 year
- Investment Amount: ₩10M

**Goals**
- Learn how to analyze stocks properly
- Find stable, dividend-paying stocks
- Avoid risky investments
- Build long-term portfolio

**Pain Points**
- Overwhelmed by financial jargon
- Doesn't know which metrics matter
- Scared of making mistakes
- Needs guidance and education

**Key Features Needed**
- Pre-built screening templates ("Stable Dividend Stocks")
- Metric explanations and tooltips
- Visual indicators (grades, scores)
- Conservative filtering options

**Success Scenario**
> Nina opens the platform, clicks "Dividend Stocks" template, sees 50 results sorted by dividend yield with A-grade financial stability. She clicks Samsung Electronics, sees clear financial charts with explanations, and feels confident adding it to her watchlist.

---

#### Persona 2: "Tactical Tom" - The Active Trader

**Demographics**
- Age: 38
- Occupation: Self-employed / Day trader
- Income: ₩80M/year
- Investment Experience: 5+ years
- Investment Amount: ₩100M

**Goals**
- Find short-term trading opportunities
- Identify momentum stocks early
- Track sector rotations
- Maximize returns through active trading

**Pain Points**
- Too slow to scan all stocks manually
- Misses fast-moving opportunities
- Needs real-time data
- Wants customizable alerts

**Key Features Needed**
- Real-time HOT stocks (volume surge detection)
- Technical indicator filtering
- Custom screening criteria
- Price/volume alerts

**Success Scenario**
> Tom checks "Today's Hot Stocks" at 10 AM, sees a biotech stock with 300% volume surge and breaking resistance. He filters for "Volume > 200%, Price Change > 5%, Market Cap < 500B" to find similar opportunities. Sets alert for stocks matching criteria.

---

#### Persona 3: "Value Victor" - The Fundamental Investor

**Demographics**
- Age: 45
- Occupation: Senior manager
- Income: ₩120M/year
- Investment Experience: 10+ years
- Investment Amount: ₩300M

**Goals**
- Find undervalued quality companies
- Long-term wealth accumulation
- Outperform index through stock-picking
- Data-driven decision making

**Pain Points**
- Time-consuming fundamental analysis
- Difficult to compare across sectors
- Needs comprehensive financial data
- Wants backtest strategies

**Key Features Needed**
- Advanced valuation filters (PER, PBR, EV/EBITDA)
- Financial statement comparisons
- Industry peer analysis
- Quality metrics (ROE, profit margins)

**Success Scenario**
> Victor creates a custom screen: "PER < 10, PBR < 1, ROE > 15%, Debt Ratio < 100%, Dividend Yield > 3%". Gets 15 results. Compares them side-by-side, exports to Excel for deeper analysis. Adds 3 stocks to his "Value Portfolio" for tracking.

---

### 4.2 User Journey Maps

#### Journey 1: First-Time Stock Screening

```
1. Landing Page
   → Sees "Find your next investment in 60 seconds"
   → Clicks "Start Screening"

2. Screening Interface
   → Presented with simple filters + templates
   → Selects "High Dividend Stocks" template
   → Adjusts dividend yield slider: > 4%

3. Results Display
   → 50 stocks appear instantly (< 500ms)
   → Sorted by dividend yield
   → Color-coded by financial grade

4. Stock Selection
   → Clicks on "KB Financial Group"
   → Sees detailed page with charts

5. Analysis
   → Reviews financial summary
   → Checks 5-year dividend history chart
   → Reads metric explanations

6. Action
   → Adds to "Watchlist"
   → (Optional) Creates account to save
```

#### Journey 2: Portfolio Tracking

```
1. Login
   → Navigates to "My Portfolio"

2. Portfolio Creation
   → Clicks "New Portfolio"
   → Names it "Growth Portfolio"

3. Adding Holdings
   → Searches "Samsung Electronics"
   → Enters: 10 shares @ ₩70,000

4. Performance Monitoring
   → Dashboard shows: +5.2% gain
   → Sees daily P&L chart
   → Compares vs KOSPI index

5. Rebalancing Decision
   → One stock down 15%
   → Uses screener to find replacement
   → Updates portfolio
```

---

### 4.3 Use Cases

#### UC-001: Basic Stock Screening

**Actor**: Any user (guest or registered)

**Precondition**: User is on the main screening page

**Main Flow**:
1. User selects market (KOSPI/KOSDAQ/All)
2. User applies filters:
   - Valuation: PER < 15
   - Growth: Revenue Growth > 10%
   - Size: Market Cap > ₩1T
3. System queries database
4. System returns filtered results in < 500ms
5. User sees list of matching stocks with key metrics

**Postcondition**: Results are displayed with option to refine filters

**Alternative Flows**:
- 2a: User selects pre-built template instead
- 4a: No results found → System suggests relaxing filters

---

#### UC-002: Stock Detail Analysis

**Actor**: Registered user

**Precondition**: User has selected a stock from screening results

**Main Flow**:
1. System loads stock detail page
2. System displays:
   - Price chart (1D, 1W, 1M, 3M, 6M, 1Y, 5Y views)
   - Financial summary (revenue, profit, margins)
   - Valuation metrics (PER, PBR, PSR, etc.)
   - Growth indicators
   - Financial statements (5 years)
3. User switches between tabs (Overview, Financials, Valuation, etc.)
4. User hovers over metrics to see explanations
5. User clicks "Add to Watchlist"

**Postcondition**: Stock is saved to user's watchlist

**Alternative Flows**:
- 5a: User not logged in → Prompted to login/register

---

#### UC-003: Real-time Hot Stock Detection

**Actor**: System (automated) + Any user

**Precondition**: Market is open

**Main Flow**:
1. System monitors trading volume every 5 minutes
2. System detects stocks with volume > 150% of 20-day average
3. System calculates price momentum
4. System ranks by combined volume + momentum score
5. System updates "Today's Hot Stocks" section
6. User visits homepage, sees updated hot stocks
7. User clicks on a hot stock to investigate

**Postcondition**: User discovers trending opportunities

**Business Rule**: Only update during market hours (09:00-15:30 KST)

---

#### UC-004: Portfolio Performance Tracking

**Actor**: Registered user (Premium tier)

**Precondition**: User has created at least one portfolio

**Main Flow**:
1. User navigates to "My Portfolio"
2. System calculates current portfolio value
3. System computes:
   - Total gain/loss (KRW and %)
   - Daily change
   - Performance vs KOSPI index
4. System displays:
   - Holdings table (stock, shares, avg cost, current price, P&L)
   - Performance chart over time
   - Asset allocation pie chart
5. User clicks "Add Holding"
6. User searches for stock and enters purchase details
7. System updates portfolio calculations

**Postcondition**: Portfolio reflects new holdings

---

#### UC-005: Custom Alert Creation

**Actor**: Registered user (Premium tier)

**Precondition**: User is viewing a stock detail page

**Main Flow**:
1. User clicks "Create Alert" button
2. System shows alert creation modal
3. User configures alert:
   - Type: Price Alert
   - Condition: "Price rises above ₩75,000"
   - Notification: Email + Push
4. User saves alert
5. System monitors stock price continuously
6. When condition met, system triggers notification
7. User receives email: "Alert triggered for Samsung Electronics"

**Postcondition**: Alert is active and monitoring

**Business Rule**: Free users: 3 alerts max, Premium: Unlimited

---

## 5. Feature Requirements

### 5.1 Feature Prioritization Framework

**Priority Levels**:
- **P0 (Must-Have)**: Core functionality, product unusable without it
- **P1 (High)**: Critical for competitive advantage
- **P2 (Medium)**: Enhances user experience
- **P3 (Low)**: Nice to have, future consideration

---

### 5.2 Functional Requirements

#### FR-1: Stock Screening Engine

**Priority**: P0

**Description**: Core filtering system enabling users to discover stocks matching custom criteria.

**Requirements**:

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-1.1 | Support filtering by 200+ indicators | P0 | All indicators from data spec available |
| FR-1.2 | Multi-dimensional filtering (AND/OR logic) | P0 | Users can combine ≥10 filters simultaneously |
| FR-1.3 | Range-based filters (min/max) | P0 | All numeric filters support min/max values |
| FR-1.4 | Real-time query execution | P0 | Results returned in < 500ms (p99) |
| FR-1.5 | Result sorting (any column) | P0 | Click column header to sort asc/desc |
| FR-1.6 | Result pagination | P1 | Show 50 results per page |
| FR-1.7 | Export results to CSV/Excel | P2 | Download button exports current view |
| FR-1.8 | Save custom screens | P1 | Registered users can save filter combinations |
| FR-1.9 | Pre-built templates | P1 | ≥10 templates (dividend, growth, value, etc.) |
| FR-1.10 | Market selection (KOSPI/KOSDAQ/All) | P0 | Toggle to filter by market |

**User Stories**:
- As a value investor, I want to filter stocks with PER < 10 AND PBR < 1 AND ROE > 15%, so that I can find undervalued quality companies
- As a beginner, I want to use a "High Dividend" template, so that I don't have to understand complex filters
- As an active trader, I want to save my custom screens, so that I can reuse them daily

---

#### FR-2: Stock Detail Page

**Priority**: P0

**Description**: Comprehensive analysis view for individual stocks.

**Requirements**:

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-2.1 | Price chart with multiple timeframes | P0 | Support 1D, 1W, 1M, 3M, 6M, 1Y, 5Y views |
| FR-2.2 | Real-time price updates | P1 | Update price every 30 seconds during market hours |
| FR-2.3 | Financial summary dashboard | P0 | Display revenue, profit, margins, ROE |
| FR-2.4 | Valuation metrics section | P0 | Show PER, PBR, PSR, PCR, EV/EBITDA, etc. |
| FR-2.5 | Financial statements (5 years) | P0 | Income statement, balance sheet, cash flow |
| FR-2.6 | Quarterly & annual data toggle | P1 | Switch between quarterly/annual view |
| FR-2.7 | Peer comparison | P2 | Compare with industry average + top 3 competitors |
| FR-2.8 | Metric explanations (tooltips) | P1 | Hover over metric name to see explanation |
| FR-2.9 | Add to watchlist button | P1 | One-click to add/remove from watchlist |
| FR-2.10 | Historical dividend data | P1 | Chart + table of dividend history |

**User Stories**:
- As an investor, I want to see 5 years of financial statements, so that I can identify trends
- As a beginner, I want metric explanations, so that I can learn what PER means
- As an analyst, I want to compare a stock with its peers, so that I can assess relative valuation

---

#### FR-3: Real-time Market Insights

**Priority**: P1

**Description**: Dynamic sections highlighting market trends and opportunities.

**Requirements**:

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-3.1 | Today's hot stocks (volume surge) | P1 | Top 20 stocks with volume > 150% of 20D avg |
| FR-3.2 | Top gainers/losers | P1 | Top 20 by % price change today |
| FR-3.3 | Sector performance heatmap | P2 | Color-coded grid of 10 sectors with % change |
| FR-3.4 | Rising/falling themes | P1 | Identify trending investment themes |
| FR-3.5 | Market overview dashboard | P1 | KOSPI/KOSDAQ index, volume, top news |
| FR-3.6 | Update frequency | P1 | Refresh every 5 minutes during market hours |
| FR-3.7 | Historical comparison | P2 | Compare today's movers vs yesterday |

**User Stories**:
- As an active trader, I want to see volume surge stocks, so that I can identify momentum opportunities
- As a thematic investor, I want to see rising themes, so that I can ride sector rotations

---

#### FR-4: Portfolio Management

**Priority**: P1

**Description**: Track and analyze personal stock holdings.

**Requirements**:

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-4.1 | Create multiple portfolios | P1 | Users can create ≥5 separate portfolios |
| FR-4.2 | Add/edit/delete holdings | P1 | Enter stock, shares, purchase price, date |
| FR-4.3 | Real-time portfolio valuation | P1 | Calculate current value using live prices |
| FR-4.4 | Gain/loss tracking (absolute & %) | P1 | Show unrealized P&L per holding and total |
| FR-4.5 | Performance vs benchmark | P1 | Compare portfolio return vs KOSPI index |
| FR-4.6 | Asset allocation visualization | P2 | Pie chart by stock, sector, or market cap |
| FR-4.7 | Transaction history | P2 | Log of all buy/sell transactions |
| FR-4.8 | Export portfolio to Excel | P2 | Download current holdings + performance |
| FR-4.9 | Dividend tracking | P2 | Record received dividends, calculate yield |
| FR-4.10 | Portfolio sharing (optional) | P3 | Generate shareable link to portfolio |

**User Stories**:
- As an investor, I want to track my holdings in one place, so that I can monitor performance easily
- As a long-term investor, I want to see my performance vs KOSPI, so that I know if I'm outperforming

---

#### FR-5: User Account & Authentication

**Priority**: P0

**Description**: Secure user registration and authentication system.

**Requirements**:

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-5.1 | Email + password registration | P0 | Users can sign up with email |
| FR-5.2 | Email verification | P0 | Send verification link to confirm email |
| FR-5.3 | Login with email/password | P0 | Authenticate users securely |
| FR-5.4 | OAuth login (Google, Kakao, Naver) | P1 | Support social login for convenience |
| FR-5.5 | Password reset flow | P0 | Email-based password recovery |
| FR-5.6 | Session management | P0 | Secure JWT-based sessions with refresh tokens |
| FR-5.7 | User profile management | P1 | Edit name, email, password, preferences |
| FR-5.8 | Subscription tier display | P1 | Show current plan (Free/Basic/Pro) |
| FR-5.9 | Account deletion | P2 | Users can request account deletion (GDPR) |
| FR-5.10 | Two-factor authentication (2FA) | P3 | Optional 2FA via SMS/authenticator app |

**User Stories**:
- As a new user, I want to sign up with my email, so that I can save my preferences
- As a busy user, I want to login with Kakao, so that I don't have to remember another password

---

#### FR-6: Search & Discovery

**Priority**: P1

**Description**: Quick search functionality to find stocks.

**Requirements**:

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-6.1 | Search by stock name (Korean) | P1 | Autocomplete suggestions as user types |
| FR-6.2 | Search by stock code | P1 | Support 6-digit KOSPI/KOSDAQ codes |
| FR-6.3 | Search autocomplete | P1 | Show top 10 matches in dropdown |
| FR-6.4 | Recent searches | P2 | Show last 5 searched stocks |
| FR-6.5 | Popular stocks section | P2 | Display 10 most-viewed stocks today |
| FR-6.6 | Search performance | P1 | Return autocomplete results in < 100ms |

**User Stories**:
- As a user, I want to quickly search "삼성전자" and jump to its detail page
- As a researcher, I want autocomplete to suggest stocks as I type, saving me time

---

#### FR-7: Alerts & Notifications

**Priority**: P2

**Description**: Customizable alerts for price movements and screening results.

**Requirements**:

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-7.1 | Price alerts (above/below threshold) | P2 | Trigger when stock crosses specified price |
| FR-7.2 | Volume surge alerts | P2 | Notify when volume > X% of average |
| FR-7.3 | Screening result alerts | P2 | Notify when new stocks match saved screen |
| FR-7.4 | Email notifications | P2 | Send alert via email |
| FR-7.5 | Push notifications (web) | P2 | Browser push notifications |
| FR-7.6 | Alert management dashboard | P2 | View/edit/delete all active alerts |
| FR-7.7 | Alert frequency limits | P2 | Max 1 notification per hour per alert |
| FR-7.8 | Free tier limits | P2 | Free: 3 alerts, Basic: 10, Pro: Unlimited |

**User Stories**:
- As a trader, I want to be notified when Samsung crosses ₩80,000, so I can act quickly
- As a screener user, I want daily alerts when new stocks match my "Value" screen

---

#### FR-8: Data Visualization

**Priority**: P1

**Description**: Charts and visual representations of financial data.

**Requirements**:

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-8.1 | Interactive price charts | P1 | Zoom, pan, crosshair on charts |
| FR-8.2 | Chart indicators (MA, volume) | P2 | Overlay moving averages, volume bars |
| FR-8.3 | Financial statement charts | P1 | Bar charts for revenue, profit over time |
| FR-8.4 | Comparison charts | P2 | Overlay multiple stocks on one chart |
| FR-8.5 | Responsive design | P1 | Charts adapt to mobile/tablet/desktop |
| FR-8.6 | Chart export (image) | P3 | Download chart as PNG |
| FR-8.7 | Performance optimization | P1 | Render charts with 5 years data in < 1s |

---

#### FR-9: Educational Content

**Priority**: P2

**Description**: Help users understand financial concepts.

**Requirements**:

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-9.1 | Metric glossary | P2 | Explain 200+ indicators in simple Korean |
| FR-9.2 | Tutorial videos | P2 | ≥10 video guides (screening, analysis, etc.) |
| FR-9.3 | Blog articles | P2 | Weekly investment insights and tips |
| FR-9.4 | Contextual help | P1 | "?" icon next to complex features |
| FR-9.5 | Onboarding flow | P1 | 3-step interactive tutorial for new users |

---

#### FR-10: Subscription & Billing

**Priority**: P1

**Description**: Tiered subscription plans with payment processing.

**Requirements**:

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-10.1 | Three-tier pricing (Free/Basic/Pro) | P1 | Clearly differentiated feature access |
| FR-10.2 | Payment processing | P1 | Support credit card, bank transfer, Kakao Pay |
| FR-10.3 | Subscription upgrade/downgrade | P1 | Users can change plans mid-cycle |
| FR-10.4 | Billing history | P1 | Show past invoices and receipts |
| FR-10.5 | Auto-renewal | P1 | Automatically charge monthly/yearly |
| FR-10.6 | Cancellation flow | P1 | Users can cancel anytime (no refund pro-rata) |
| FR-10.7 | Free trial | P1 | 14-day free trial of Pro tier |

**Pricing Tiers** (Draft):

| Feature | Free | Basic (₩9,900/mo) | Pro (₩29,900/mo) |
|---------|------|-------------------|------------------|
| Stock screening | ✓ (10 filters) | ✓ (Unlimited) | ✓ (Unlimited) |
| Stock detail pages | ✓ | ✓ | ✓ |
| Historical data | 1 year | 5 years | 10 years |
| Portfolios | 1 portfolio | 3 portfolios | Unlimited |
| Alerts | 3 alerts | 10 alerts | Unlimited |
| Export data | ✗ | ✓ CSV | ✓ Excel + API |
| Real-time updates | ✗ (20 min delay) | ✓ | ✓ |
| Peer comparison | ✗ | ✓ | ✓ |
| API access | ✗ | ✗ | ✓ |

---

### 5.3 Non-Functional Requirements

#### NFR-1: Performance

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-1.1 | Screening query response time | < 500ms (p99) | Application Performance Monitoring (APM) |
| NFR-1.2 | Stock detail page load time | < 1.5s (p95) | Real User Monitoring (RUM) |
| NFR-1.3 | API endpoint response time | < 200ms (p95) | APM |
| NFR-1.4 | Chart rendering time | < 1s for 5 years data | Frontend profiling |
| NFR-1.5 | Search autocomplete latency | < 100ms | Frontend metrics |
| NFR-1.6 | Database query optimization | No query > 1s | Slow query log |

#### NFR-2: Scalability

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-2.1 | Concurrent users | Support 10,000+ simultaneously | Load testing |
| NFR-2.2 | Database scalability | Handle 2,400 stocks × 200 indicators = 480K metrics | Database monitoring |
| NFR-2.3 | Horizontal scaling | Auto-scale API servers based on CPU > 70% | Kubernetes HPA |
| NFR-2.4 | Cache hit rate | > 80% for frequently accessed data | Redis monitoring |
| NFR-2.5 | CDN coverage | Serve static assets via CDN | CDN analytics |

#### NFR-3: Reliability

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-3.1 | System uptime | 99.9% (< 8.76 hours downtime/year) | Uptime monitoring |
| NFR-3.2 | Error rate | < 0.1% of all requests | Error tracking (Sentry) |
| NFR-3.3 | Database backup | Daily backups, 30-day retention | Backup logs |
| NFR-3.4 | Disaster recovery | RTO < 4 hours, RPO < 1 hour | DR drills |
| NFR-3.5 | Health checks | All services report health status | Health endpoint monitoring |

#### NFR-4: Security

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-4.1 | Authentication | Secure JWT with refresh tokens, 15min expiry | Security audit |
| NFR-4.2 | Password storage | Bcrypt with salt, min cost factor 12 | Code review |
| NFR-4.3 | HTTPS only | All traffic over TLS 1.3 | SSL Labs scan |
| NFR-4.4 | API rate limiting | 100 req/min per user, 1000 req/min per IP | Rate limiter logs |
| NFR-4.5 | SQL injection prevention | Parameterized queries, ORM usage | Security testing |
| NFR-4.6 | XSS prevention | Content Security Policy, sanitized inputs | Security headers check |
| NFR-4.7 | Sensitive data encryption | Encrypt PII at rest (AES-256) | Compliance audit |
| NFR-4.8 | Vulnerability scanning | Weekly automated scans | Dependency checker |

#### NFR-5: Usability

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-5.1 | Mobile responsiveness | Support screens ≥ 360px width | Device testing |
| NFR-5.2 | Browser compatibility | Support Chrome, Safari, Edge, Firefox (latest 2 versions) | Cross-browser testing |
| NFR-5.3 | Accessibility | WCAG 2.1 Level AA compliance | Accessibility audit |
| NFR-5.4 | Page load performance | Lighthouse score > 90 | Lighthouse CI |
| NFR-5.5 | Internationalization | Korean language, KRW currency | i18n framework |

#### NFR-6: Data Quality

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-6.1 | Data accuracy | 99.9% match with official sources (KRX) | Automated validation |
| NFR-6.2 | Data freshness | Update daily prices within 30 min of market close | Pipeline monitoring |
| NFR-6.3 | Data completeness | < 0.1% missing data points | Data quality checks |
| NFR-6.4 | Historical data integrity | No retroactive changes without audit log | Change tracking |

#### NFR-7: Maintainability

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-7.1 | Code coverage | > 80% unit test coverage | Coverage reports |
| NFR-7.2 | Documentation | All APIs documented (OpenAPI spec) | Documentation review |
| NFR-7.3 | Code quality | SonarQube quality gate pass | Static analysis |
| NFR-7.4 | Deployment frequency | Support daily deployments | CI/CD metrics |
| NFR-7.5 | Rollback capability | Rollback to previous version in < 5 min | Deployment testing |

#### NFR-8: Compliance

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-8.1 | Data licensing | Proper attribution for KRX/F&Guide data | Legal review |
| NFR-8.2 | Investment disclaimer | Display on all pages with financial data | Compliance checklist |
| NFR-8.3 | Privacy policy | GDPR/PIPA compliant | Legal review |
| NFR-8.4 | Terms of service | Clearly stated user agreement | Legal review |
| NFR-8.5 | Cookie consent | EU Cookie Law compliance (if applicable) | Cookie banner implementation |

---