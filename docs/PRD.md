# Product Requirements Document (PRD)
# Stock Screening & Analysis Platform

## Document Information

| Field | Value |
|-------|-------|
| **Product Name** | The Screener - Stock Analysis Platform |
| **Version** | 1.2 |
| **Status** | Updated - Documentation Platform Deployed |
| **Created Date** | 2025-11-09 |
| **Last Updated** | 2025-11-15 |
| **Author** | Product Team |
| **Stakeholders** | Engineering, Design, Data Science, Business, Growth |
| **Classification** | Internal |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Vision & Objectives](#2-product-vision--objectives)
3. [Market Analysis](#3-market-analysis)
4. [User Personas & Use Cases](#4-user-personas--use-cases)
5. [Feature Requirements](#5-feature-requirements)
6. [Technical Requirements](#6-technical-requirements)
7. [Data Requirements](#7-data-requirements)
8. [UI/UX Requirements](#8-uiux-requirements)
9. [Success Metrics](#9-success-metrics)
10. [Development Roadmap](#10-development-roadmap)
11. [Risk Analysis & Mitigation](#11-risk-analysis--mitigation)
12. [Appendices](#12-appendices)

---

## 1. Executive Summary

### 1.1 Product Overview

**The Screener** is a comprehensive data-driven stock screening and analysis platform designed for Korean individual investors. The platform enables users to discover investment opportunities through advanced filtering capabilities powered by 200+ financial and technical indicators.

### 1.2 Problem Statement

Individual investors face several challenges in the Korean stock market:
- **Information Overload**: Over 2,400 listed companies on KOSPI/KOSDAQ with complex financial data
- **Time Constraints**: Analyzing hundreds of stocks manually is time-prohibitive
- **Limited Tools**: Existing platforms lack sophisticated filtering or charge premium fees
- **Data Complexity**: Financial metrics require expertise to interpret correctly

### 1.3 Proposed Solution

A web-based platform that:
- Provides **instant stock screening** using 200+ indicators with intuitive filters
- Delivers **comprehensive analysis** for individual stocks with visual charts and financial breakdowns
- Offers **real-time insights** on market trends, hot stocks, and sector movements
- Enables **portfolio tracking** with performance analytics
- Democratizes access to **institutional-grade data** for retail investors

### 1.4 Success Criteria

#### MVP Success Criteria (Achieved ✅)
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **Screening Performance** | < 500ms query time | ~220ms (p99) | ✅ Exceeded |
| **API Response Time** | < 200ms (p95) | ~150ms | ✅ Exceeded |
| **Test Coverage** | > 70% | 80% backend | ✅ Exceeded |

#### Phase 2 Success Criteria (Freemium Model)
| Metric | Current (Login-Required) | Target (Freemium) | Timeline |
|--------|-------------------------|-------------------|----------|
| **Visitor → Screener Use** | 15% | 60% (+300%) | 1 month |
| **Overall Conversion Rate** | 0.75% | 12% (+1,500%) | 3 months |
| **Active Users** | ~100 | 50,000+ | 12 months |
| **Organic Traffic (SEO)** | Limited | +500% | 6 months |
| **User Retention** (30-day) | 25% | 45% (+80%) | 6 months |
| **Average Session Duration** | ~5 min | 10+ min | 3 months |
| **Free → Paid Conversion** | N/A | 5-10% | 6 months |

---

## 2. Product Vision & Objectives

### 2.1 Vision Statement

> "Empower every Korean investor with institutional-quality stock analysis tools, enabling data-driven investment decisions through simplicity and transparency."

### 2.2 Core Objectives

#### Business Objectives
1. **Market Leadership**: Become the #1 stock screening platform in Korea within 18 months
2. **Revenue Growth**: Achieve $500K ARR by end of Year 1
3. **User Base**: Acquire 100,000 registered users within 12 months
4. **Brand Recognition**: Establish thought leadership in data-driven investing

#### Product Objectives
1. **Comprehensiveness**: Support 200+ financial indicators covering all analysis dimensions
2. **Performance**: Deliver screening results in under 500ms for 99th percentile queries
3. **Usability**: Enable users to find relevant stocks within 60 seconds ("1분 만에 골라보세요")
4. **Accuracy**: Maintain 99.9% data accuracy with real-time updates
5. **Scalability**: Support 10,000+ concurrent users without degradation

#### User Objectives
1. **Discovery**: Help users identify investment opportunities aligned with their strategy
2. **Education**: Teach users how to interpret financial metrics through contextual guidance
3. **Efficiency**: Reduce research time from hours to minutes
4. **Confidence**: Provide reliable, audited data from official sources (KRX, F&Guide)

### 2.3 Key Differentiators

| Feature | Our Platform | Competitors |
|---------|--------------|-------------|
| **Indicator Count** | 200+ comprehensive metrics | 20-50 basic metrics |
| **Response Time** | < 500ms | 2-5 seconds |
| **Data Sources** | KRX + F&Guide (official) | Mixed/unverified sources |
| **Pricing** | Freemium with generous free tier | Expensive premium-only |
| **User Experience** | Modern React SPA | Legacy interfaces |
| **Real-time Updates** | Live market data | 15-20 min delay |

---

## 3. Market Analysis

### 3.1 Market Size & Opportunity

**Korean Stock Market Overview (2024)**
- **Total Listed Companies**: ~2,400 (KOSPI: ~900, KOSDAQ: ~1,500)
- **Active Trading Accounts**: 35M+ (56% of population)
- **Individual Investor Market Share**: 65% of daily trading volume
- **Average Age of Retail Investors**: 35-45 years (increasingly younger)

**Target Addressable Market**
- **TAM** (Total Addressable Market): 35M trading accounts
- **SAM** (Serviceable Addressable Market): 10M active traders (trade monthly)
- **SOM** (Serviceable Obtainable Market): 500K users (5% of SAM within 2 years)

### 3.2 Competitive Landscape

#### Direct Competitors

**1. Naver Finance**
- Strengths: Massive user base, integrated news, free
- Weaknesses: Limited screening, basic metrics only, slow
- Market Share: ~60%

**2. Investing.com Korea**
- Strengths: Global platform, technical analysis tools
- Weaknesses: Not optimized for Korean market, English-focused
- Market Share: ~5%

**3. WiseFn/FnGuide Direct**
- Strengths: Professional-grade data
- Weaknesses: Expensive (B2B focus), complex UI
- Market Share: ~2% (retail)

**4. Quantit (퀀티트)**
- Strengths: Quantitative focus, backtesting
- Weaknesses: Complex for beginners, limited free tier
- Market Share: ~3%

#### Competitive Advantages

1. **Speed**: Sub-500ms screening vs 2-5s competitors
2. **Depth**: 200+ indicators vs 20-50 typical
3. **UX**: Modern React SPA vs legacy interfaces
4. **Accessibility**: Generous free tier vs paywall-first
5. **Education**: Contextual metric explanations vs raw numbers

### 3.3 Market Trends

1. **Rising Retail Participation**: Individual investors now dominate daily volume (65%+)
2. **Younger Demographics**: 20-30s age group growing fastest (40% YoY)
3. **Mobile-First**: 70% of trading via mobile apps
4. **Data Democratization**: Demand for institutional-quality tools
5. **ESG/Thematic Investing**: Growing interest in sector/theme-based strategies

---

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

#### FR-0: Public Access & Freemium Model 🆕

**Priority**: P0 (Critical for Growth)

**Description**: Transform the platform from login-required to freemium model, enabling anonymous users to access core features with limitations while encouraging conversion to registered users.

**Business Rationale**:
- **Current Problem**: 60-70% of visitors bounce at login wall
- **SEO Impact**: Stock pages not indexed by Google (login required)
- **Viral Growth**: Cannot share screening results or stock analyses
- **User Acquisition**: High barrier to entry limits growth

**Requirements**:

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-0.1 | Public access to stock screener | P0 | Anonymous users can use screener with limitations |
| FR-0.2 | Public access to stock detail pages | P0 | Stock pages accessible without login (SEO-friendly) |
| FR-0.3 | Screening result limits (public) | P0 | Display max 20 results for anonymous users |
| FR-0.4 | Daily usage limits (public) | P0 | Max 10 searches per day for anonymous users |
| FR-0.5 | Content restrictions (public) | P0 | Blur/lock financial statements and advanced features |
| FR-0.6 | Freemium UI components | P0 | Upgrade prompts, limit modals, locked content overlays |
| FR-0.7 | Usage tracking (client-side) | P0 | localStorage-based tracking for public users |
| FR-0.8 | Server-side rate limiting | P0 | IP-based rate limiting (10 searches/day) |
| FR-0.9 | SEO meta tags | P1 | Dynamic meta tags for stock pages (Open Graph, Twitter Card) |
| FR-0.10 | Social sharing functionality | P1 | Share buttons for stock pages and screening results |
| FR-0.11 | User tier detection | P0 | System identifies Public/Free/Premium users |
| FR-0.12 | Upgrade CTAs | P1 | Persistent banners and modals encouraging registration |

**User Tier Matrix**:

| Feature | Public (No Login) | Registered (Free) | Premium (Future) |
|---------|-------------------|-------------------|------------------|
| Stock Screener | ⚠️ Limited (20 results, 10/day) | ✅ Unlimited | ✅ Unlimited + AI |
| Stock Detail | ⚠️ Limited (charts, blurred financials) | ✅ Full access | ✅ Full + Analysis |
| Market Overview | ✅ Full access | ✅ Full access | ✅ Full access |
| Compare Tool | ⚠️ 2 stocks max | ✅ 5 stocks | ✅ 10 stocks |
| Watchlists | ❌ Not available | ✅ 10 lists (100 stocks each) | ✅ Unlimited |
| Dashboard | ❌ Not available | ✅ Full access | ✅ Full + Insights |
| Export Data | ❌ Not available | ✅ CSV only | ✅ CSV + PDF + API |
| Filter Presets | ❌ Not available | ✅ Up to 10 | ✅ Unlimited |
| Price Alerts | ❌ Not available | ❌ Not available | ✅ Available |

**User Stories**:
- As a **prospective user**, I want to try the screener without registering, so that I can evaluate the platform before committing
- As a **Google searcher**, I want to land directly on stock detail pages, so that I can quickly get the information I need
- As a **satisfied public user**, I want clear upgrade prompts, so that I understand the benefits of registering
- As a **registered user**, I want unrestricted access to all free features, so that I feel the value of creating an account

**Expected Impact**:
- Visitor → Screener: 15% → 60% (+300%)
- Overall Conversion: 0.75% → 12% (+1,500%)
- Organic Traffic: +500% (SEO indexing)
- New Signups: +400% in 30 days

**Technical Components**:
- `useFreemiumAccess` hook for tier detection
- `FreemiumBanner`, `LockedContent`, `LimitReachedModal` components
- localStorage-based usage tracking
- Server-side rate limiting (BE-010)
- SEO meta tags (react-helmet-async)
- Social sharing (Web Share API)

**Dependencies**:
- BE-010: Server-side rate limiting API
- Remove `ProtectedRoute` from screener and stock detail pages

---

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

## 6. Technical Requirements

### 6.1 Technology Stack

#### Frontend

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Framework** | React | 18+ | Industry standard, component reusability, large ecosystem |
| **Build Tool** | Vite | 5+ | Fast HMR, optimized builds, better DX than Webpack |
| **State Management** | Zustand | 4+ | Lightweight, simpler than Redux, sufficient for our needs |
| **Routing** | React Router | 6+ | De facto standard for React SPAs |
| **Data Fetching** | TanStack Query (React Query) | 5+ | Caching, automatic refetch, optimistic updates |
| **Charts** | TradingView Lightweight Charts + Recharts | Latest | Financial charts (TV) + general charts (Recharts) |
| **UI Components** | Radix UI + Tailwind CSS | Latest | Accessible primitives + utility-first CSS |
| **Forms** | React Hook Form | 7+ | Performance, DX, built-in validation |
| **Validation** | Zod | 3+ | TypeScript-first schema validation |
| **HTTP Client** | Axios | 1+ | Interceptors, better error handling than fetch |
| **Date Handling** | date-fns | 3+ | Smaller than moment.js, tree-shakeable |
| **Notifications** | React Hot Toast | 2+ | Lightweight, customizable |
| **Testing** | Vitest + Testing Library | Latest | Fast, Jest-compatible, React Testing Library |

#### Backend

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Framework** | FastAPI (Python) | 0.110+ | High performance, auto OpenAPI docs, async support |
| **ASGI Server** | Uvicorn | 0.27+ | Fast ASGI server for FastAPI |
| **ORM** | SQLAlchemy | 2+ | Mature, supports async, complex queries |
| **Migration** | Alembic | 1.13+ | Database migration tool for SQLAlchemy |
| **Validation** | Pydantic | 2+ | Data validation, serialization (built into FastAPI) |
| **Authentication** | FastAPI-Users + PyJWT | Latest | Flexible auth system, JWT tokens |
| **Task Queue** | Celery | 5+ | Distributed task processing for indicator calculations |
| **Message Broker** | Redis | 7+ | Celery broker, also used for caching |
| **API Documentation** | Swagger UI (auto via FastAPI) | Auto | Interactive API docs |
| **Testing** | Pytest | 8+ | Industry standard for Python testing |
| **Linting** | Ruff | Latest | Fast Python linter (replaces flake8, isort, etc.) |
| **Type Checking** | MyPy | 1.8+ | Static type checking for Python |

#### Database

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Primary DB** | PostgreSQL | 16+ | ACID compliant, JSON support, mature |
| **Time Series** | TimescaleDB (Postgres extension) | 2.14+ | Optimized for time-series data (stock prices) |
| **Cache** | Redis | 7+ | In-memory cache, pub/sub, session storage |
| **Search** | PostgreSQL Full-Text Search | Built-in | Sufficient for stock name/code search, avoid Elasticsearch overhead |

#### Infrastructure

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Container** | Docker | 24+ | Consistent environments, easy deployment |
| **Orchestration** | Kubernetes | 1.29+ | Auto-scaling, self-healing, industry standard |
| **Cloud Provider** | AWS / GCP / Naver Cloud | N/A | TBD based on cost/compliance requirements |
| **CDN** | CloudFlare | N/A | Fast static asset delivery, DDoS protection |
| **CI/CD** | GitHub Actions | N/A | Integrated with repo, free for public repos |
| **Monitoring** | Grafana + Prometheus | Latest | Metrics visualization + time-series DB |
| **Logging** | ELK Stack (Elasticsearch, Logstash, Kibana) | 8+ | Centralized logging, search, visualization |
| **APM** | Sentry | Cloud | Error tracking, performance monitoring |
| **Uptime Monitoring** | UptimeRobot / Pingdom | Cloud | Availability monitoring |

#### Data Pipeline

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Orchestration** | Apache Airflow | 2.8+ | Workflow scheduling, monitoring, retries |
| **Data Processing** | Pandas + NumPy | Latest | Financial calculations, data transformation |
| **API Clients** | Requests + Custom wrappers | Latest | Fetch data from KRX, F&Guide APIs |

---

### 6.2 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Users                                  │
│                     (Web Browser / Mobile)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       CloudFlare CDN                             │
│              (Static Assets, DDoS Protection)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Load Balancer                               │
│                    (NGINX / AWS ALB)                             │
└────────┬────────────────────────────────────────────────────────┘
         │
         ├─────────────┬──────────────┬──────────────┐
         ▼             ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Frontend    │ │ Frontend    │ │ Frontend    │ │ Frontend    │
│ Server 1    │ │ Server 2    │ │ Server 3    │ │ Server N    │
│ (Nginx)     │ │ (Nginx)     │ │ (Nginx)     │ │ (Nginx)     │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
         │             │              │              │
         └─────────────┴──────────────┴──────────────┘
                         │ REST API / GraphQL
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API Gateway                                │
│        (Rate Limiting, Auth Check, Request Routing)             │
└────────┬────────────────────────────────────────────────────────┘
         │
         ├─────────────┬──────────────┬──────────────┐
         ▼             ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ API Server  │ │ API Server  │ │ API Server  │ │ API Server  │
│ 1 (FastAPI) │ │ 2 (FastAPI) │ │ 3 (FastAPI) │ │ N (FastAPI) │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │               │
       └───────────────┴───────────────┴───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Analytics       │ │ Notification    │ │ Auth Service    │
│ Engine          │ │ Service         │ │                 │
│ (Indicator Calc)│ │ (Alerts)        │ │ (JWT Tokens)    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Celery Workers                              │
│              (Async Indicator Calculations)                      │
└─────────────────────────────────────────────────────────────────┘
         │
         └──────────────┬────────────────────────────────┐
                        │                                │
                        ▼                                ▼
┌───────────────────────────────────────┐ ┌─────────────────────────┐
│          Redis Cluster                │ │   PostgreSQL Cluster    │
│  ┌──────────┐  ┌──────────┐          │ │  ┌──────────────────┐   │
│  │ Cache    │  │ Session  │          │ │  │ Primary (RW)     │   │
│  │          │  │ Store    │          │ │  │ + TimescaleDB    │   │
│  └──────────┘  └──────────┘          │ │  └────────┬─────────┘   │
│  ┌──────────┐  ┌──────────┐          │ │           │             │
│  │ Celery   │  │ Pub/Sub  │          │ │           ▼             │
│  │ Broker   │  │          │          │ │  ┌──────────────────┐   │
│  └──────────┘  └──────────┘          │ │  │ Replica 1 (RO)   │   │
└───────────────────────────────────────┘ │  └──────────────────┘   │
                                          │  ┌──────────────────┐   │
                                          │  │ Replica 2 (RO)   │   │
                                          │  └──────────────────┘   │
                                          └─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Pipeline Layer                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │               Apache Airflow Scheduler                   │    │
│  └────────┬────────────────────────────────────────────────┘    │
│           │                                                      │
│  ┌────────▼────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │ KRX Data        │  │ F&Guide API │  │ News Scraper    │    │
│  │ Collector       │  │ Collector   │  │ (Themes)        │    │
│  │ (Daily Prices)  │  │ (Financials)│  │                 │    │
│  └─────────────────┘  └─────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐     │
│  │ KRX API     │  │ F&Guide API │  │ Payment Gateway     │     │
│  │ (Official   │  │ (Financial  │  │ (Stripe / Toss)     │     │
│  │  Prices)    │  │  Data)      │  │                     │     │
│  └─────────────┘  └─────────────┘  └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

### 6.3 API Design

#### RESTful Endpoints

**Base URL**: `https://api.screener.kr/v1`

**Authentication**:
- Public endpoints: No auth required
- Private endpoints: `Authorization: Bearer <JWT_TOKEN>`

#### Stock Endpoints

```
GET    /stocks
       Query params: market, min_per, max_per, min_market_cap, sort_by, page, limit
       Response: { stocks: [...], total: 1234, page: 1, pages: 25 }

GET    /stocks/{stock_code}
       Response: { code, name, market, sector, current_price, ... }

GET    /stocks/{stock_code}/financials
       Query params: period (quarterly/annual), years
       Response: { income_statement: [...], balance_sheet: [...], cash_flow: [...] }

GET    /stocks/{stock_code}/prices
       Query params: from_date, to_date, interval (daily/weekly/monthly)
       Response: { prices: [{ date, open, high, low, close, volume }, ...] }

GET    /stocks/{stock_code}/indicators
       Response: { valuation: {...}, growth: {...}, profitability: {...}, ... }
```

#### Screening Endpoints

```
POST   /screen
       Body: { filters: { per: { max: 15 }, roe: { min: 10 } }, sort: "market_cap", order: "desc" }
       Response: { stocks: [...], count: 50, query_time_ms: 234 }

GET    /screen/templates
       Response: { templates: [{ id, name, description, filters }, ...] }

GET    /screen/templates/{template_id}
       Response: { id, name, filters, ... }
```

#### Market Endpoints

```
GET    /market/overview
       Response: { kospi_index, kosdaq_index, volume, ... }

GET    /market/hot-stocks
       Response: { hot_stocks: [{ code, name, volume_surge_pct, price_change_pct }, ...] }

GET    /market/movers
       Query params: type (gainers/losers), limit
       Response: { movers: [...] }

GET    /market/sectors
       Response: { sectors: [{ name, price_change_pct, volume }, ...] }
```

#### User Endpoints

```
POST   /auth/register
       Body: { email, password }
       Response: { user_id, email, token }

POST   /auth/login
       Body: { email, password }
       Response: { user_id, token, refresh_token }

POST   /auth/refresh
       Body: { refresh_token }
       Response: { token }

GET    /users/me
       Auth: Required
       Response: { id, email, subscription_tier, created_at }

PATCH  /users/me
       Auth: Required
       Body: { name, email, password }
       Response: { updated_user }
```

#### Portfolio Endpoints

```
GET    /portfolios
       Auth: Required
       Response: { portfolios: [...] }

POST   /portfolios
       Auth: Required
       Body: { name }
       Response: { id, name, created_at }

GET    /portfolios/{portfolio_id}
       Auth: Required
       Response: { id, name, holdings: [...], total_value, total_gain, ... }

POST   /portfolios/{portfolio_id}/holdings
       Auth: Required
       Body: { stock_code, quantity, avg_price, purchase_date }
       Response: { holding_id, ... }

DELETE /portfolios/{portfolio_id}/holdings/{holding_id}
       Auth: Required
       Response: { success: true }
```

#### Alert Endpoints

```
GET    /alerts
       Auth: Required
       Response: { alerts: [...] }

POST   /alerts
       Auth: Required
       Body: { stock_code, type: "price", condition: "above", value: 80000, notify_via: ["email", "push"] }
       Response: { alert_id, ... }

DELETE /alerts/{alert_id}
       Auth: Required
       Response: { success: true }
```

---

### 6.4 Database Schema

#### Core Tables

**stocks**
```sql
CREATE TABLE stocks (
    code VARCHAR(6) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    name_english VARCHAR(100),
    market VARCHAR(10) NOT NULL CHECK (market IN ('KOSPI', 'KOSDAQ')),
    sector VARCHAR(50),
    industry VARCHAR(100),
    listing_date DATE,
    delisting_date DATE,
    shares_outstanding BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_stocks_market ON stocks(market);
CREATE INDEX idx_stocks_sector ON stocks(sector);
CREATE INDEX idx_stocks_name_trgm ON stocks USING gin (name gin_trgm_ops); -- For fuzzy search
```

**daily_prices** (TimescaleDB hypertable)
```sql
CREATE TABLE daily_prices (
    stock_code VARCHAR(6) NOT NULL REFERENCES stocks(code),
    trade_date DATE NOT NULL,
    open_price INTEGER,
    high_price INTEGER,
    low_price INTEGER,
    close_price INTEGER,
    adjusted_close INTEGER, -- For splits/dividends
    volume BIGINT,
    trading_value BIGINT,
    market_cap BIGINT,
    PRIMARY KEY (stock_code, trade_date)
);

-- Convert to TimescaleDB hypertable for efficient time-series queries
SELECT create_hypertable('daily_prices', 'trade_date');

-- Create continuous aggregate for faster queries
CREATE MATERIALIZED VIEW daily_prices_monthly
WITH (timescaledb.continuous) AS
SELECT
    stock_code,
    time_bucket('1 month', trade_date) AS month,
    first(open_price, trade_date) AS open,
    max(high_price) AS high,
    min(low_price) AS low,
    last(close_price, trade_date) AS close,
    sum(volume) AS total_volume
FROM daily_prices
GROUP BY stock_code, month;
```

**financial_statements**
```sql
CREATE TABLE financial_statements (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(6) NOT NULL REFERENCES stocks(code),
    period_type VARCHAR(10) NOT NULL CHECK (period_type IN ('quarterly', 'annual')),
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER CHECK (fiscal_quarter BETWEEN 1 AND 4),
    report_date DATE NOT NULL,

    -- Income Statement
    revenue BIGINT,
    cost_of_revenue BIGINT,
    gross_profit BIGINT,
    operating_expenses BIGINT,
    operating_profit BIGINT,
    non_operating_income BIGINT,
    non_operating_expenses BIGINT,
    ebt BIGINT, -- Earnings Before Tax
    tax_expense BIGINT,
    net_profit BIGINT,

    -- Balance Sheet
    current_assets BIGINT,
    non_current_assets BIGINT,
    total_assets BIGINT,
    current_liabilities BIGINT,
    non_current_liabilities BIGINT,
    total_liabilities BIGINT,
    equity BIGINT,

    -- Cash Flow Statement
    operating_cash_flow BIGINT,
    investing_cash_flow BIGINT,
    financing_cash_flow BIGINT,
    free_cash_flow BIGINT,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(stock_code, period_type, fiscal_year, fiscal_quarter)
);

CREATE INDEX idx_financials_stock_period ON financial_statements(stock_code, period_type, fiscal_year DESC);
```

**calculated_indicators**
```sql
CREATE TABLE calculated_indicators (
    stock_code VARCHAR(6) NOT NULL REFERENCES stocks(code),
    calculation_date DATE NOT NULL,

    -- Valuation
    per NUMERIC(10, 2),
    pbr NUMERIC(10, 2),
    psr NUMERIC(10, 2),
    pcr NUMERIC(10, 2),
    ev_ebitda NUMERIC(10, 2),
    dividend_yield NUMERIC(5, 2),

    -- Profitability
    roe NUMERIC(5, 2),
    roa NUMERIC(5, 2),
    gross_margin NUMERIC(5, 2),
    operating_margin NUMERIC(5, 2),
    net_margin NUMERIC(5, 2),

    -- Growth (YoY %)
    revenue_growth NUMERIC(6, 2),
    profit_growth NUMERIC(6, 2),
    eps_growth NUMERIC(6, 2),

    -- Stability
    debt_to_equity NUMERIC(6, 2),
    current_ratio NUMERIC(5, 2),
    quick_ratio NUMERIC(5, 2),
    interest_coverage NUMERIC(6, 2),

    -- Efficiency
    asset_turnover NUMERIC(5, 2),
    inventory_turnover NUMERIC(5, 2),
    receivables_turnover NUMERIC(5, 2),

    -- Technical
    price_change_1d NUMERIC(5, 2),
    price_change_1w NUMERIC(5, 2),
    price_change_1m NUMERIC(5, 2),
    price_change_3m NUMERIC(5, 2),
    price_change_6m NUMERIC(5, 2),
    price_change_1y NUMERIC(5, 2),
    volume_20d_avg BIGINT,
    volume_surge_pct NUMERIC(6, 2),

    -- Overall Score
    quality_score INTEGER CHECK (quality_score BETWEEN 1 AND 100),
    value_score INTEGER CHECK (value_score BETWEEN 1 AND 100),
    growth_score INTEGER CHECK (growth_score BETWEEN 1 AND 100),

    created_at TIMESTAMP DEFAULT NOW(),

    PRIMARY KEY (stock_code, calculation_date)
);

CREATE INDEX idx_indicators_date ON calculated_indicators(calculation_date DESC);
CREATE INDEX idx_indicators_per ON calculated_indicators(per) WHERE per IS NOT NULL;
CREATE INDEX idx_indicators_pbr ON calculated_indicators(pbr) WHERE pbr IS NOT NULL;
CREATE INDEX idx_indicators_roe ON calculated_indicators(roe) WHERE roe IS NOT NULL;
```

#### User & Portfolio Tables

**users**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    subscription_tier VARCHAR(20) NOT NULL DEFAULT 'free' CHECK (subscription_tier IN ('free', 'basic', 'pro')),
    subscription_expires_at TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_tier);
```

**portfolios**
```sql
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_portfolios_user ON portfolios(user_id);
```

**portfolio_holdings**
```sql
CREATE TABLE portfolio_holdings (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    stock_code VARCHAR(6) NOT NULL REFERENCES stocks(code),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    avg_price NUMERIC(10, 2) NOT NULL,
    purchase_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(portfolio_id, stock_code)
);

CREATE INDEX idx_holdings_portfolio ON portfolio_holdings(portfolio_id);
```

**alerts**
```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_code VARCHAR(6) NOT NULL REFERENCES stocks(code),
    alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('price', 'volume', 'indicator')),
    condition VARCHAR(20) NOT NULL CHECK (condition IN ('above', 'below', 'equals')),
    threshold_value NUMERIC(15, 4) NOT NULL,
    notify_via VARCHAR(20)[] DEFAULT ARRAY['email'], -- Array of: email, push
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alerts_user_active ON alerts(user_id, is_active);
CREATE INDEX idx_alerts_stock ON alerts(stock_code) WHERE is_active = TRUE;
```

#### Audit & Analytics Tables

**user_activity_log**
```sql
CREATE TABLE user_activity_log (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action_type VARCHAR(50) NOT NULL, -- login, screen, view_stock, create_portfolio, etc.
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    metadata JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_activity_user_date ON user_activity_log(user_id, created_at DESC);
CREATE INDEX idx_activity_type ON user_activity_log(action_type);
```

**data_ingestion_log**
```sql
CREATE TABLE data_ingestion_log (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL, -- krx, fguide, etc.
    data_type VARCHAR(50) NOT NULL, -- prices, financials, etc.
    records_processed INTEGER,
    records_failed INTEGER,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'partial', 'failed')),
    error_message TEXT,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ingestion_source_date ON data_ingestion_log(source, created_at DESC);
```

---

### 6.5 Caching Strategy

#### Cache Layers

**1. Browser Cache**
- Static assets (JS, CSS, images): 1 year TTL
- Service Worker for offline support (optional Phase 3)

**2. CDN Cache (CloudFlare)**
- Static assets: Edge caching
- API responses: Cache-Control headers for public data

**3. Application Cache (Redis)**

| Data Type | Key Pattern | TTL | Update Trigger |
|-----------|-------------|-----|----------------|
| Hot stocks | `hot_stocks:realtime` | 5 min | Scheduled job every 5 min |
| Stock detail | `stock:{code}:detail` | 1 hour | Daily data pipeline |
| Stock prices (recent) | `stock:{code}:prices:1y` | 1 hour | Daily data pipeline |
| Screening results | `screen:{filter_hash}` | 10 min | Calculated on-demand |
| Market overview | `market:overview` | 5 min | Scheduled job every 5 min |
| User session | `session:{user_id}` | 15 min | Token refresh |
| Indicators (all stocks) | `indicators:all:{date}` | 24 hours | Daily calculation |

**4. Database Query Cache**
- PostgreSQL shared_buffers: 25% of RAM
- Materialized views for common aggregations

#### Cache Invalidation

```python
# Example: Invalidate cache on data update
@celery.task
def update_daily_prices():
    # 1. Fetch new prices from KRX
    new_prices = krx_api.get_daily_prices()

    # 2. Update database
    db.bulk_insert(new_prices)

    # 3. Invalidate relevant caches
    for stock_code in new_prices:
        redis.delete(f"stock:{stock_code}:detail")
        redis.delete(f"stock:{stock_code}:prices:*")

    # 4. Update calculated indicators
    recalculate_indicators.delay()
```

---

### 6.6 Security Architecture

#### Authentication Flow

```
1. User Login
   → Client sends { email, password } to /auth/login
   → Server validates credentials
   → Server generates JWT access token (15 min expiry)
   → Server generates refresh token (30 days expiry, stored in DB)
   → Server returns both tokens

2. Authenticated Request
   → Client includes: Authorization: Bearer <access_token>
   → API Gateway validates JWT signature + expiry
   → If valid, request proceeds to API server
   → If expired, client must refresh

3. Token Refresh
   → Client sends refresh token to /auth/refresh
   → Server validates refresh token (check DB, not revoked)
   → Server issues new access token
   → Client stores new access token

4. Logout
   → Client sends request to /auth/logout
   → Server revokes refresh token (add to blacklist)
   → Client discards tokens
```

#### Security Measures

| Threat | Mitigation |
|--------|------------|
| **SQL Injection** | Parameterized queries via SQLAlchemy ORM |
| **XSS** | CSP headers, sanitize user inputs, escape outputs |
| **CSRF** | SameSite cookies, CSRF tokens for state-changing ops |
| **Brute Force** | Rate limiting (5 failed logins → 15 min lockout) |
| **DDoS** | CloudFlare protection, rate limiting per IP |
| **Data Breach** | Encrypt PII at rest (AES-256), TLS 1.3 in transit |
| **Dependency Vulnerabilities** | Weekly Dependabot scans, automated updates |
| **API Abuse** | Rate limiting (100 req/min per user, 1000/min per IP) |

---

### 6.7 Documentation Infrastructure

#### Unified Documentation Platform

To ensure comprehensive, accessible, and maintainable documentation for all stakeholders (developers, users, QA, and business teams), we will implement a unified documentation platform that consolidates all project documentation.

**Documentation Platform**: Docusaurus (React-based)

**Rationale**:
- **Modern & Interactive**: React-based with MDX support for interactive components
- **Multi-language Support**: Integrates with Python (Sphinx) and TypeScript (TypeDoc) auto-documentation
- **Developer-friendly**: Markdown-based authoring with hot reload
- **Search & Navigation**: Built-in search with Algolia DocSearch integration
- **Versioning**: Support for multiple documentation versions
- **Deployment**: Simple deployment to GitHub Pages, Vercel, or Netlify with CDN

#### Documentation Structure

```
docs-site/
├── docs/
│   ├── 01-getting-started/          # Quickstart, installation, setup
│   ├── 02-guides/
│   │   ├── user-guides/             # End-user feature guides
│   │   ├── developer-guides/        # Development, testing, debugging
│   │   └── deployment/              # Docker, K8s, monitoring setup
│   ├── 03-api-reference/
│   │   ├── backend/                 # Auto-generated from Python (Sphinx)
│   │   ├── frontend/                # Auto-generated from TypeScript (TypeDoc)
│   │   ├── rest-api.md              # REST API endpoints
│   │   ├── websocket-api.md         # WebSocket API
│   │   └── rate-limiting.md         # Rate limiting policies
│   ├── 04-architecture/
│   │   ├── system-design.md         # High-level architecture
│   │   ├── database-schema.md       # Database design
│   │   ├── data-pipeline.md         # Airflow DAGs
│   │   ├── security.md              # Security architecture
│   │   └── performance.md           # Performance design
│   ├── 05-specifications/
│   │   ├── prd.md                   # Product Requirements Document
│   │   ├── srs.md                   # Software Requirements Specification
│   │   └── sds.md                   # Software Design Specification
│   └── 06-operations/
│       ├── monitoring.md            # Monitoring & alerting
│       ├── troubleshooting.md       # Common issues & solutions
│       ├── performance-tuning.md    # Optimization guide
│       └── disaster-recovery.md     # DR procedures
└── blog/                            # Release notes, updates
```

#### Auto-Documentation Integration

| Component | Tool | Source | Output |
|-----------|------|--------|--------|
| **Python Backend** | Sphinx + autodoc | Docstrings in `.py` files | API reference HTML |
| **TypeScript Frontend** | TypeDoc | TSDoc comments in `.ts/.tsx` | Component docs |
| **REST API** | FastAPI | OpenAPI spec | Interactive API docs |
| **Database** | SchemaSpy | PostgreSQL schema | ER diagrams, table docs |

#### Documentation Standards

**Python Docstrings** (Google Style):
```python
def get_stock_by_code(stock_code: str) -> StockDetail:
    """
    Get stock detail by code with caching.

    Args:
        stock_code: 6-digit stock code (e.g., "005930").

    Returns:
        StockDetail with latest price and indicators.

    Raises:
        NotFoundException: If stock not found.

    Example:
        >>> detail = service.get_stock_by_code("005930")
        >>> print(f"{detail.name}: {detail.latest_price.close_price:,} KRW")
        Samsung Electronics: 71,000 KRW
    """
```

**TypeScript TSDoc**:
```typescript
/**
 * Stock screening table with advanced filtering.
 *
 * @param props - Component props
 * @param props.filters - Active screening filters
 * @param props.onStockSelect - Callback when stock selected
 *
 * @example
 * ```tsx
 * <StockScreener
 *   filters={{ market: 'KOSPI', per: { max: 20 } }}
 *   onStockSelect={(stock) => navigate(`/stocks/${stock.code}`)}
 * />
 * ```
 */
export const StockScreener: React.FC<Props> = ({ filters, onStockSelect }) => {
  // Implementation
};
```

#### CI/CD Integration

Documentation will be automatically built and deployed on every commit:

```yaml
# .github/workflows/docs.yml
on:
  pull_request:
    paths: ['docs/**', 'frontend/src/**', 'backend/app/**']
  push:
    branches: [main]

jobs:
  build:
    - Build Sphinx Python docs
    - Build TypeDoc TypeScript docs
    - Build Docusaurus site
    - Check for broken links
    - Run Lighthouse CI (performance audit)
    - Deploy preview (PR only)
    - Deploy production (main branch)
```

#### Documentation Hosting (GitHub Pages)

**Platform**: GitHub Pages

**Rationale**:
- **Cost**: Free for public repositories (unlimited bandwidth)
- **Integration**: Seamless integration with GitHub Actions
- **Simplicity**: Single workflow file, no external services needed
- **Reliability**: GitHub's infrastructure and SLA
- **Version Control**: Documentation versioned alongside code
- **No Limits**: Unlike Vercel/Netlify free tiers

**Configuration**:
- **Production URL**: `https://docs.screener.kr` (custom domain)
- **Fallback URL**: `https://kcenon.github.io/screener_system/`
- **Deployment**: Automatic via GitHub Actions on push to main
- **Branch**: `gh-pages` (auto-created by deployment action)
- **CDN**: GitHub's global CDN (Fastly-powered)
- **SSL**: Auto-managed HTTPS with free certificate
- **Search**: Algolia DocSearch integration (free for open source)

#### Success Metrics

| Metric | Target |
|--------|--------|
| **Documentation Coverage** | > 80% of public APIs documented |
| **Build Time** | < 3 minutes |
| **Page Load Speed** | < 1 second (Lighthouse score > 90) |
| **Search Quality** | > 90% of queries return relevant results |
| **Developer Usage** | > 70% of developers consult docs weekly |

#### Benefits

1. **Single Source of Truth**: All documentation in one searchable location
2. **Auto-updated**: API docs generated from source code, always accurate
3. **Version Control**: Documentation versioned alongside code
4. **Discoverable**: Search, navigation, cross-references make finding info easy
5. **Maintainable**: Markdown-based, easy to contribute, automated checks
6. **Professional**: Modern UI, mobile-friendly, fast loading

---

## 7. Data Requirements

### 7.1 Data Sources

#### Primary Sources

**1. Korea Exchange (KRX)**
- **Data**: Daily stock prices (OHLCV), market cap, shares outstanding
- **Update Frequency**: Daily (after market close, ~16:00 KST)
- **Access Method**: Official API / Web scraping (if no API)
- **Cost**: Free for delayed data, paid for real-time
- **License**: Attribution required

**2. F&Guide (Financial data provider)**
- **Data**: Financial statements, earnings estimates, corporate actions
- **Update Frequency**: Quarterly (earnings reports), daily (estimates)
- **Access Method**: Paid API subscription
- **Cost**: ~$500-1000/month (estimated)
- **License**: Restricted usage, no redistribution

#### Supplementary Sources

**3. Financial news / Press releases**
- **Data**: Corporate events, industry trends for theme detection
- **Sources**: Naver Finance, Company IR pages
- **Update Frequency**: Real-time
- **Access Method**: Web scraping
- **Cost**: Free

**4. Bank of Korea (for macro data)**
- **Data**: Interest rates, inflation, economic indicators
- **Update Frequency**: Monthly
- **Access Method**: Open API
- **Cost**: Free

---

### 7.2 Data Specifications

#### Stock Master Data

| Field | Type | Source | Update Frequency |
|-------|------|--------|------------------|
| Stock Code | VARCHAR(6) | KRX | Static (unless new listings) |
| Stock Name (Korean) | VARCHAR(100) | KRX | Static |
| Market (KOSPI/KOSDAQ) | ENUM | KRX | Static |
| Sector | VARCHAR(50) | KRX | Quarterly (reclassifications) |
| Industry | VARCHAR(100) | KRX | Quarterly |
| Listing Date | DATE | KRX | Static |
| Shares Outstanding | BIGINT | KRX | Quarterly (updated on splits) |

#### Price Data

| Field | Type | Source | Update Frequency |
|-------|------|--------|------------------|
| Trade Date | DATE | KRX | Daily |
| Open Price | INTEGER | KRX | Daily |
| High Price | INTEGER | KRX | Daily |
| Low Price | INTEGER | KRX | Daily |
| Close Price | INTEGER | KRX | Daily |
| Adjusted Close | INTEGER | Calculated | Daily (on corporate actions) |
| Volume | BIGINT | KRX | Daily |
| Trading Value | BIGINT | KRX | Daily |
| Market Cap | BIGINT | Calculated | Daily |

#### Financial Statement Data

| Field | Type | Source | Update Frequency |
|-------|------|--------|------------------|
| Period Type | ENUM | F&Guide | Quarterly/Annually |
| Fiscal Year | INTEGER | F&Guide | Quarterly |
| Fiscal Quarter | INTEGER | F&Guide | Quarterly |
| Revenue | BIGINT | F&Guide | Quarterly |
| Operating Profit | BIGINT | F&Guide | Quarterly |
| Net Profit | BIGINT | F&Guide | Quarterly |
| Total Assets | BIGINT | F&Guide | Quarterly |
| Total Liabilities | BIGINT | F&Guide | Quarterly |
| Equity | BIGINT | F&Guide | Quarterly |
| Operating Cash Flow | BIGINT | F&Guide | Quarterly |
| Free Cash Flow | BIGINT | Calculated | Quarterly |

#### Calculated Indicators (200+ total)

**Valuation (15 indicators)**
- PER (Price-to-Earnings Ratio)
- PBR (Price-to-Book Ratio)
- PSR (Price-to-Sales Ratio)
- PCR (Price-to-Cash Flow Ratio)
- EV/EBITDA
- EV/Sales
- EV/FCF
- Dividend Yield
- Payout Ratio
- PEG Ratio
- Graham Number
- Intrinsic Value (DCF-based)
- Price to Tangible Book
- Price to Operating Cash Flow
- Enterprise Value

**Profitability (20 indicators)**
- ROE (Return on Equity)
- ROA (Return on Assets)
- ROIC (Return on Invested Capital)
- Gross Profit Margin
- Operating Profit Margin
- Net Profit Margin
- EBITDA Margin
- Free Cash Flow Margin
- Asset Turnover
- Equity Multiplier
- DuPont ROE Decomposition
- Operating Leverage
- Earnings Quality (CFO / Net Income)
- Accruals Ratio
- ...

**Growth (25 indicators)**
- Revenue Growth (YoY, QoQ, 3Y CAGR, 5Y CAGR)
- Profit Growth (YoY, QoQ, 3Y CAGR, 5Y CAGR)
- EPS Growth (YoY, QoQ, 3Y CAGR, 5Y CAGR)
- Book Value Growth
- Operating Cash Flow Growth
- Free Cash Flow Growth
- Dividend Growth (5Y CAGR)
- Asset Growth
- Equity Growth
- Sales per Employee Growth
- ...

**Stability (20 indicators)**
- Debt-to-Equity Ratio
- Debt-to-Assets Ratio
- Interest Coverage Ratio
- Current Ratio
- Quick Ratio
- Cash Ratio
- Altman Z-Score
- Piotroski F-Score
- Earnings Stability (Std Dev of ROE)
- Revenue Stability
- Beta (market volatility)
- ...

**Efficiency (15 indicators)**
- Asset Turnover
- Inventory Turnover
- Receivables Turnover
- Payables Turnover
- Cash Conversion Cycle
- Days Sales Outstanding
- Days Inventory Outstanding
- Days Payables Outstanding
- Fixed Asset Turnover
- Working Capital Turnover
- ...

**Technical (30 indicators)**
- Price Change (1D, 1W, 1M, 3M, 6M, 1Y, 3Y, 5Y)
- Volume (20D avg, 60D avg)
- Volume Surge % (vs 20D avg)
- Moving Averages (5D, 20D, 60D, 120D, 200D)
- MACD
- RSI (14-day)
- Bollinger Bands
- ATR (Average True Range)
- On-Balance Volume
- Accumulation/Distribution
- 52-week High/Low
- Distance from 52W High
- New High/Low indicators
- ...

**Quality (15 indicators)**
- Piotroski F-Score (0-9)
- Beneish M-Score (earnings manipulation)
- Earnings Quality Score
- Accounting Quality
- Cash Flow Quality
- Dividend Consistency
- Earnings Consistency
- Return Consistency
- Management Efficiency
- Corporate Governance Score
- ...

**Momentum (10 indicators)**
- Relative Strength (vs index)
- Price Momentum (6M, 12M)
- Earnings Momentum
- Estimate Revisions
- Analyst Rating Changes
- Institutional Ownership Change
- Short Interest Ratio
- ...

**Value Composite Scores (10 indicators)**
- Overall Quality Score (1-100)
- Value Score (1-100)
- Growth Score (1-100)
- Momentum Score (1-100)
- Combined Score (weighted)
- Sector-relative scores
- Percentile rankings
- ...

**Total: 200+ indicators**

---

### 7.3 Data Quality Requirements

| Requirement | Target | Validation Method |
|-------------|--------|-------------------|
| **Accuracy** | 99.9% match with official sources | Daily reconciliation against KRX |
| **Completeness** | < 0.1% missing data points | Data quality checks, alert on gaps |
| **Timeliness** | Daily prices loaded within 30 min of market close | Pipeline monitoring |
| **Consistency** | No conflicting data across tables | Foreign key constraints, checksums |
| **Historical Integrity** | No unauthorized changes to historical data | Audit logs, immutable timestamps |

---

### 7.4 Data Retention Policy

| Data Type | Retention Period | Archive Policy |
|-----------|------------------|----------------|
| Daily prices | Indefinite | Compress data older than 5 years (TimescaleDB compression) |
| Financial statements | Indefinite | Keep all historical reports |
| Calculated indicators | 5 years online, older archived | Move to cold storage after 5 years |
| User activity logs | 2 years | Delete after 2 years (GDPR compliance) |
| User portfolios | Until account deletion | Soft delete (30-day grace period) |
| Alert history | 1 year | Delete after 1 year |

---

## 8. UI/UX Requirements

### 8.1 Design Principles

1. **Simplicity**: Complex data presented in digestible formats
2. **Speed**: Instant feedback, no loading spinners for < 500ms operations
3. **Education**: Contextual help without overwhelming users
4. **Accessibility**: WCAG 2.1 AA compliance
5. **Mobile-First**: Responsive design, touch-friendly

---

### 8.2 Key Screens

#### 1. Homepage / Stock Screener

**Purpose**: Primary entry point, stock discovery

**Layout**:
```
┌────────────────────────────────────────────────────────┐
│ Header: Logo | Search | Login/Account                  │
├────────────────────────────────────────────────────────┤
│ Hero: "Find your next investment in 60 seconds"        │
│ Templates: [High Dividend] [Growth] [Value] [Custom]   │
├────────────────────────────────────────────────────────┤
│ Filters Panel (Left)      │ Results Table (Right)      │
│ ┌──────────────────────┐  │ ┌────────────────────────┐ │
│ │ Market: [x] KOSPI    │  │ │ Stock | Price | PER |  │ │
│ │         [ ] KOSDAQ   │  │ │ Samsung | 70,000 | 12 │ │
│ │                      │  │ │ ...                    │ │
│ │ Valuation            │  │ └────────────────────────┘ │
│ │ PER: [__] - [15]     │  │ Pagination: 1 2 3 ... 10  │
│ │ PBR: [__] - [1.0]    │  │                            │
│ │                      │  │                            │
│ │ Growth               │  │                            │
│ │ Revenue Growth:      │  │                            │
│ │ [10%] - [__]         │  │                            │
│ │                      │  │                            │
│ │ [Apply Filters]      │  │                            │
│ └──────────────────────┘  │                            │
└────────────────────────────────────────────────────────┘
│ Today's Hot Stocks: [Stock1] [Stock2] [Stock3] ...     │
└────────────────────────────────────────────────────────┘
```

**Interactions**:
- Click template → Auto-populate filters
- Adjust sliders → Real-time result update (debounced)
- Click stock → Navigate to detail page
- Sort by column header
- Export to CSV button (Premium)

---

#### 2. Stock Detail Page

**Purpose**: In-depth analysis of individual stock

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│ Header                                                     │
├────────────────────────────────────────────────────────────┤
│ Samsung Electronics (005930)                   [Watchlist] │
│ KOSPI | Semiconductors                                     │
│ ₩70,000 (+2,500 +3.57%)                                    │
├────────────────────────────────────────────────────────────┤
│ Tabs: [Overview] [Financials] [Valuation] [Technicals]    │
├────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────┐   │
│ │             Price Chart (TradingView)                │   │
│ │                                                      │   │
│ │   [1D] [1W] [1M] [3M] [6M] [1Y] [5Y]                │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                            │
│ ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│ │ Valuation       │ │ Profitability   │ │ Growth       │  │
│ │ PER: 12.3       │ │ ROE: 15.2%      │ │ Revenue: +8% │  │
│ │ PBR: 0.85       │ │ ROA: 8.1%       │ │ Profit: +12% │  │
│ │ PSR: 1.2        │ │ Net Margin: 10% │ │ EPS: +15%    │  │
│ └─────────────────┘ └─────────────────┘ └──────────────┘  │
│                                                            │
│ Financial Summary (5 years bar chart)                     │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ Revenue:  ███ ███ ███ ███ ███                        │   │
│ │ Profit:   ██  ██  ██  ███ ███                        │   │
│ └──────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

**Interactions**:
- Hover over metrics → Tooltip with explanation
- Switch chart timeframes
- Toggle between quarterly/annual data
- Add to watchlist (authenticated users)
- Create alert (Premium)

---

#### 3. Portfolio Page

**Purpose**: Track user's holdings and performance

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│ My Portfolios                                   [+ New]    │
├────────────────────────────────────────────────────────────┤
│ [Growth Portfolio ▼] [Value Portfolio] [Dividend Portfolio]│
├────────────────────────────────────────────────────────────┤
│ Total Value: ₩50,250,000      (+₩2,500,000 +5.24%)        │
│ vs KOSPI: +2.1% (outperforming)                            │
│                                                            │
│ Performance Chart (1M)                                     │
│ ┌──────────────────────────────────────────────────────┐   │
│ │         /\    /\                                     │   │
│ │        /  \  /  \    /\                              │   │
│ │ ──────/────\/────\──/──\─────────────                │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                            │
│ Holdings:                                       [+ Add]    │
│ ┌──────────────────────────────────────────────────────┐   │
│ │Stock     │Shares│Avg Cost│Current│ Gain/Loss │ % │   │   │
│ ├──────────┼──────┼────────┼───────┼───────────┼───┤   │   │
│ │Samsung   │ 10   │ 68,000 │70,000 │+20,000    │+3%│   │   │
│ │Hyundai   │ 5    │200,000 │195,000│-25,000    │-3%│   │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                            │
│ Asset Allocation (Pie Chart)                               │
│ ┌──────────────────────────────────────────────────────┐   │
│ │  Tech: 60%  █████                                    │   │
│ │  Auto: 30%  ███                                      │   │
│ │  Finance: 10% █                                      │   │
│ └──────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

**Interactions**:
- Switch between portfolios
- Add new holding (search stock, enter details)
- Edit/delete holdings
- View transaction history
- Export to Excel

---

#### 4. Mobile Views

**Responsive Breakpoints**:
- Mobile: < 768px (single column, stacked components)
- Tablet: 768px - 1024px (2 columns)
- Desktop: > 1024px (full layout)

**Mobile-Specific Features**:
- Bottom navigation bar (Home, Screen, Portfolio, Account)
- Swipeable charts
- Collapsible filter panel
- Pull-to-refresh for real-time updates

---

### 8.3 Accessibility Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Keyboard Navigation** | All interactive elements accessible via Tab, Enter, Esc |
| **Screen Reader** | Semantic HTML, ARIA labels, alt text for images |
| **Color Contrast** | WCAG AA: 4.5:1 for text, 3:1 for UI components |
| **Focus Indicators** | Visible focus rings for all interactive elements |
| **Text Scaling** | Support up to 200% zoom without breaking layout |
| **Error Messages** | Clear, actionable error messages with suggestions |

---

### 8.4 Design System

**Color Palette**:
- Primary: #2563eb (Blue - trust, stability)
- Success: #10b981 (Green - positive gains)
- Danger: #ef4444 (Red - losses, alerts)
- Warning: #f59e0b (Yellow - caution)
- Neutral: #6b7280 (Gray - text, borders)

**Typography**:
- Headings: Pretendard (Korean-optimized), Inter (English fallback)
- Body: Pretendard, system fonts
- Code/Numbers: JetBrains Mono (monospace)

**Components**:
- Buttons: Rounded corners, hover states, disabled states
- Tables: Striped rows, sortable columns, sticky headers
- Charts: Consistent color scheme, tooltips, zoom controls
- Forms: Inline validation, clear error messages
- Cards: Shadow on hover, clear hierarchy

---

## 9. Success Metrics

### 9.1 Key Performance Indicators (KPIs)

#### Product Metrics

| Metric | Target | Measurement | Frequency |
|--------|--------|-------------|-----------|
| **Active Users (MAU)** | 50,000 by Month 12 | Google Analytics | Monthly |
| **Screening Sessions** | 100,000/month by Month 6 | App telemetry | Monthly |
| **Avg Session Duration** | 8+ minutes | Google Analytics | Weekly |
| **User Retention (30-day)** | 40% | Cohort analysis | Monthly |
| **Conversion Rate (Free → Paid)** | 5% | Subscription funnel | Monthly |
| **Churn Rate** | < 5% monthly | Subscription cancellations | Monthly |
| **NPS (Net Promoter Score)** | > 50 | User surveys | Quarterly |

#### Technical Metrics

| Metric | Target | Measurement | Frequency |
|--------|--------|-------------|-----------|
| **API Response Time (p95)** | < 200ms | APM (Sentry) | Real-time |
| **Screening Query Time (p99)** | < 500ms | APM | Real-time |
| **Page Load Time (p95)** | < 1.5s | RUM | Real-time |
| **Uptime** | 99.9% | Uptime monitoring | Monthly |
| **Error Rate** | < 0.1% | Error tracking | Real-time |
| **Cache Hit Rate** | > 80% | Redis metrics | Daily |

#### Business Metrics

| Metric | Target | Measurement | Frequency |
|--------|--------|-------------|-----------|
| **Monthly Recurring Revenue (MRR)** | $50K by Month 12 | Billing system | Monthly |
| **Customer Acquisition Cost (CAC)** | < $20 | Marketing spend / new users | Monthly |
| **Lifetime Value (LTV)** | > $100 | Cohort analysis | Quarterly |
| **LTV:CAC Ratio** | > 5:1 | Calculated | Quarterly |

---

### 9.2 Success Criteria by Milestone

#### Month 3 (Beta Launch)

- [ ] 1,000 registered users
- [ ] 10,000 screening sessions
- [ ] < 1% error rate
- [ ] Screening queries < 500ms (p99)
- [ ] Core features complete (screening, stock detail, basic portfolio)

#### Month 6 (Public Launch)

- [ ] 10,000 active users
- [ ] 50,000 screening sessions/month
- [ ] 100 paid subscribers
- [ ] $3,000 MRR
- [ ] 30% user retention (30-day)
- [ ] NPS > 40

#### Month 12 (Growth Phase)

- [ ] 50,000 active users
- [ ] 100,000 screening sessions/month
- [ ] 2,500 paid subscribers (5% conversion)
- [ ] $50,000 MRR
- [ ] 40% user retention (30-day)
- [ ] NPS > 50
- [ ] Featured in major Korean financial media

---

### 9.3 Measurement & Analytics

**Tools**:
- **Google Analytics 4**: User behavior, funnel analysis
- **Mixpanel**: Event tracking, cohort analysis, A/B testing
- **Sentry**: Error tracking, performance monitoring
- **LogRocket**: Session replay for debugging UX issues
- **Stripe/Billing System**: Revenue metrics

**Key Events to Track**:
- User Registration
- First Screening
- Stock Detail View
- Watchlist Add
- Portfolio Created
- Subscription Upgrade
- Alert Created
- Export Data
- Session Duration
- Feature Usage Frequency

---

## 10. Development Roadmap

### 10.1 Phase 1: MVP (Months 1-3)

**Goal**: Functional screening platform with core features

**Features**:
- [x] Stock screening (20 key indicators)
- [x] Stock detail pages (basic charts + financials)
- [x] User authentication (email/password)
- [x] Search functionality
- [x] Responsive web design (desktop + mobile)

**Infrastructure**:
- [x] Frontend (React + Vite + Tailwind)
- [x] Backend (FastAPI + PostgreSQL)
- [x] Data pipeline (daily KRX prices)
- [x] Basic caching (Redis)
- [x] Deployment (Docker + basic CI/CD)

**Success Criteria**:
- 1,000 beta users
- Screening < 500ms (p99)
- 99% uptime

**Timeline**: 12 weeks
- Week 1-2: Setup, architecture, DB schema
- Week 3-5: Backend API development
- Week 6-8: Frontend development
- Week 9-10: Data pipeline + indicator calculations
- Week 11: Testing, bug fixes
- Week 12: Beta launch

---

### 10.2 Phase 2: Public Launch (Months 4-6)

**Goal**: Feature-complete platform ready for public launch

**Features**:
- [x] Expand to 200+ indicators
- [x] Real-time hot stocks section
- [x] Portfolio management (basic)
- [x] Pre-built screening templates
- [x] OAuth login (Kakao, Naver, Google)
- [x] Subscription tiers (Free/Basic/Pro)
- [x] Payment integration (Stripe)
- [x] Educational content (metric explanations)

**Infrastructure**:
- [x] TimescaleDB for time-series data
- [x] Advanced caching strategy
- [x] Kubernetes deployment
- [x] Monitoring (Grafana + Prometheus)
- [x] Security hardening

**Success Criteria**:
- 10,000 active users
- 100 paid subscribers
- $3,000 MRR

**Timeline**: 12 weeks
- Week 13-15: Expand indicators to 200+
- Week 16-17: Portfolio + subscription system
- Week 18-19: Hot stocks + templates
- Week 20-21: Payment integration + testing
- Week 22-23: Marketing prep, documentation
- Week 24: Public launch

---

### 10.3 Phase 3: Growth & Optimization (Months 7-12)

**Goal**: Scale to 50,000 users, optimize conversion

**Features**:
- [x] Alerts & notifications
- [x] Advanced portfolio analytics
- [x] Peer comparison
- [x] Export to Excel/CSV
- [x] API access (Pro tier)
- [x] Mobile app (iOS/Android - React Native)
- [x] Backtesting (simple)
- [x] Theme-based investing

**Infrastructure**:
- [x] Auto-scaling (Kubernetes HPA)
- [x] Multi-region deployment (if needed)
- [x] Advanced monitoring & alerting
- [x] Performance optimization

**Success Criteria**:
- 50,000 active users
- 2,500 paid subscribers
- $50,000 MRR
- Featured in media

**Timeline**: 24 weeks
- Week 25-28: Alerts + notifications
- Week 29-32: Advanced portfolio features
- Week 33-36: Mobile app (MVP)
- Week 37-40: API + export features
- Week 41-44: Backtesting + themes
- Week 45-48: Optimization, marketing push

---

### 10.4 Phase 4: Advanced Features (Months 13+)

**Future Considerations** (Post-Year 1):
- AI-powered stock recommendations
- Social features (follow other investors, share portfolios)
- Live chat support
- Webinars / educational content
- Institutional-grade analytics
- ETF screening
- International markets (US, China)
- Cryptocurrency integration
- Advanced backtesting with custom strategies
- White-label solution for financial institutions

---

## 11. Risk Analysis & Mitigation

### 11.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Data source API downtime** | Medium | High | - Multiple data sources<br>- Fallback to web scraping<br>- Cache last known good data |
| **Database performance degradation** | Medium | High | - TimescaleDB for time-series optimization<br>- Read replicas<br>- Aggressive caching |
| **Security breach** | Low | Critical | - Regular security audits<br>- Penetration testing<br>- Bug bounty program<br>- Insurance |
| **Scaling issues under high load** | Medium | Medium | - Load testing before launch<br>- Auto-scaling (Kubernetes HPA)<br>- CDN for static assets |
| **Data accuracy errors** | Low | High | - Daily reconciliation with official sources<br>- Automated validation checks<br>- User reporting mechanism |

---

### 11.2 Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Low user acquisition** | Medium | High | - Pre-launch marketing<br>- SEO optimization<br>- Content marketing (blog)<br>- Partnerships with finance influencers |
| **High churn rate** | Medium | High | - Excellent onboarding<br>- Regular feature updates<br>- User feedback loops<br>- Retention campaigns |
| **Competitor with deeper pockets** | Medium | Medium | - Focus on speed & UX (hard to replicate)<br>- Build community<br>- Proprietary scoring algorithms |
| **Regulatory changes (data licensing)** | Low | High | - Legal review of data usage terms<br>- Diversify data sources<br>- Budget for increased licensing costs |
| **Market downturn (reduced trading activity)** | Medium | Medium | - Long-term investors also use screeners<br>- Diversify use cases (portfolio tracking)<br>- Freemium model sustains user base |

---

### 11.3 Legal & Compliance Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Data licensing violations** | Low | Critical | - Clear licensing agreements with KRX/F&Guide<br>- Legal review<br>- Proper attribution |
| **Investment advice liability** | Low | High | - Prominent disclaimers on all pages<br>- Terms of Service clearly state "informational only"<br>- No personalized recommendations (Phase 1) |
| **Privacy law violations (PIPA/GDPR)** | Low | High | - Privacy policy review by legal<br>- User consent flows<br>- Data deletion on request<br>- Encryption of PII |
| **Copyright issues (charts, content)** | Low | Medium | - Use open-source chart libraries<br>- Original content only<br>- Proper attribution for third-party sources |

---

### 11.4 Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Key team member departure** | Medium | Medium | - Documentation of all systems<br>- Knowledge sharing<br>- Redundancy in critical roles |
| **Vendor lock-in (cloud provider)** | Low | Medium | - Use containerization (Docker/K8s)<br>- Avoid proprietary services<br>- Multi-cloud architecture (if needed) |
| **Data pipeline failures** | Medium | Medium | - Airflow retry mechanisms<br>- Alerting on pipeline failures<br>- Manual override capability |
| **Customer support overload** | Low | Medium | - Comprehensive documentation<br>- FAQs and tutorials<br>- Automated chatbot for common questions<br>- Tiered support (email for Free, priority for Pro) |

---

## 12. Appendices

### Appendix A: Glossary of Financial Terms

**PER (Price-to-Earnings Ratio)**
- Definition: Current stock price divided by earnings per share (EPS)
- Formula: Stock Price / EPS
- Interpretation: Lower PER may indicate undervaluation, but varies by industry

**PBR (Price-to-Book Ratio)**
- Definition: Market capitalization divided by book value of equity
- Formula: Market Cap / Total Equity
- Interpretation: PBR < 1 suggests stock trades below book value

**ROE (Return on Equity)**
- Definition: Profitability relative to shareholders' equity
- Formula: Net Income / Shareholders' Equity × 100%
- Interpretation: Higher ROE indicates efficient use of equity capital

**Free Cash Flow (FCF)**
- Definition: Cash generated after capital expenditures
- Formula: Operating Cash Flow - Capital Expenditures
- Interpretation: Positive FCF indicates cash available for dividends, buybacks, or reinvestment

*(... Full glossary of 200+ terms in separate document)*

---

### Appendix B: Competitor Feature Comparison

| Feature | Our Platform | Naver Finance | Investing.com | Quantit |
|---------|--------------|---------------|---------------|---------|
| Indicator Count | 200+ | ~20 | ~50 | ~80 |
| Screening Speed | < 500ms | 2-3s | 1-2s | 3-5s |
| Real-time Updates | ✓ (Premium) | ✓ | ✓ (delayed) | ✗ |
| Portfolio Tracking | ✓ | ✗ | ✓ | ✓ |
| Mobile App | ✓ (Phase 3) | ✓ | ✓ | ✗ |
| Free Tier | ✓ (generous) | ✓ | ✓ (limited) | ✓ (very limited) |
| Export Data | ✓ | ✗ | ✓ (Premium) | ✓ |
| API Access | ✓ (Pro) | ✗ | ✓ (Enterprise) | ✗ |
| Backtesting | ✓ (Phase 3) | ✗ | ✗ | ✓ |
| Korean Language | ✓ | ✓ | Partial | ✓ |
| Educational Content | ✓ | Limited | ✓ | Limited |

---

### Appendix C: User Research Summary

**Method**: Surveys (n=100), Interviews (n=20)

**Key Findings**:
1. **78%** of respondents find current tools "too complex" or "too slow"
2. **65%** want more indicators, especially value-focused metrics
3. **82%** would pay for faster, more comprehensive screening
4. **Top 3 desired features**:
   - Advanced filtering (92%)
   - Real-time alerts (78%)
   - Portfolio tracking (71%)
5. **Primary use case**:
   - Long-term investing (52%)
   - Swing trading (31%)
   - Day trading (17%)

**Quotes**:
> "I spend 2 hours every weekend screening stocks manually. If a tool could do it in 2 minutes, I'd pay for that." - Survey Respondent #34

> "I love the idea of 200 indicators, but please explain them simply. I'm not a finance major." - Interview Participant #8

---

### Appendix D: Technical Debt & Future Refactoring

**Known Technical Debt**:
1. **Monolithic API**: Consider microservices architecture in Phase 4 for better scalability
2. **PostgreSQL Full-Text Search**: May need Elasticsearch if search volume grows significantly
3. **Manual indicator calculations**: Explore GPU acceleration (CUDA) for massive parallel processing
4. **Session storage in Redis**: Migrate to dedicated session store if scale demands it

**Future Optimizations**:
- Implement GraphQL for more flexible API queries (reduce over-fetching)
- Edge computing for real-time price updates (reduce latency)
- Machine learning for anomaly detection in financial data
- Blockchain-based audit trail for data integrity

---

### Appendix E: Data Source API Documentation

**KRX API** (Korea Exchange)
- Endpoint: `https://api.krx.co.kr/...` (hypothetical)
- Authentication: API Key
- Rate Limit: 100 requests/min
- Data Format: JSON
- Documentation: (link to official docs)

**F&Guide API**
- Endpoint: `https://api.fguide.com/...` (hypothetical)
- Authentication: OAuth 2.0
- Rate Limit: 500 requests/min
- Data Format: JSON
- Documentation: (link to official docs)

*(Detailed API specs in separate integration document)*

---

### Appendix F: Deployment Architecture Diagram

```
[Detailed Kubernetes deployment diagram with pods, services, ingress, persistent volumes, etc.]
```

*(Full infrastructure-as-code repository link)*

---

### Appendix G: Testing Strategy

**Unit Tests**:
- Backend: 80%+ coverage (Pytest)
- Frontend: 70%+ coverage (Vitest + Testing Library)
- Critical paths: 100% coverage

**Integration Tests**:
- API endpoint tests (all endpoints)
- Database integration tests
- Data pipeline end-to-end tests

**Performance Tests**:
- Load testing (10,000 concurrent users)
- Stress testing (identify breaking point)
- Endurance testing (24-hour sustained load)

**Security Tests**:
- OWASP Top 10 vulnerability scanning
- Penetration testing (quarterly)
- Dependency vulnerability scanning (weekly)

**User Acceptance Testing**:
- Beta testing with 100 users (Month 3)
- A/B testing for conversion optimization (ongoing)

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-09 | Product Team | Initial PRD creation |

---

## Approval & Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Manager | _______________ | _______________ | ______ |
| Engineering Lead | _______________ | _______________ | ______ |
| Design Lead | _______________ | _______________ | ______ |
| Data Lead | _______________ | _______________ | ______ |
| CEO | _______________ | _______________ | ______ |

---

**END OF DOCUMENT**
