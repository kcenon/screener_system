---
id: srs-introduction
title: SRS - Introduction & Overview
description: Software requirements specification introduction and overall description
sidebar_label: Introduction
sidebar_position: 1
tags:
  - specification
  - requirements
  - software
---

:::info Navigation
- [Introduction](introduction.md) (Current)
- [Requirements](requirements.md)
- [Non-Functional](nonfunctional-other.md)
:::

# Software Requirements Specification - Introduction

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document provides a complete description of all functions and requirements of the Stock Screening Platform. It is intended for:

- **Development Team**: To understand implementation requirements
- **QA Team**: To develop test plans and cases
- **Project Management**: To track progress against requirements
- **Stakeholders**: To verify system meets business needs

### 1.2 Scope

**Product Name**: Stock Screening Platform ("The Screener")

**Product Scope**: A web-based stock analysis and screening platform for Korean equity markets (KOSPI/KOSDAQ) providing:

- Advanced stock filtering using 200+ financial and technical indicators
- Real-time market data and analytics
- Portfolio tracking and performance monitoring
- Price and volume alert notifications
- Comprehensive financial statement analysis

**Benefits**:
- Reduce stock research time from hours to minutes
- Enable data-driven investment decisions
- Democratize access to institutional-quality analytics
- Improve investment returns through better stock selection

**Goals**:
- Achieve < 500ms screening query response time
- Support 10,000+ concurrent users
- Provide 99.9% system uptime
- Process 2,400+ stocks with 200+ indicators daily

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| **KOSPI** | Korea Composite Stock Price Index (main market) |
| **KOSDAQ** | Korean Securities Dealers Automated Quotations (tech-focused market) |
| **OHLCV** | Open, High, Low, Close, Volume (price data format) |
| **PER** | Price-to-Earnings Ratio |
| **PBR** | Price-to-Book Ratio |
| **ROE** | Return on Equity |
| **JWT** | JSON Web Token (authentication method) |
| **API** | Application Programming Interface |
| **SPA** | Single Page Application |
| **CRUD** | Create, Read, Update, Delete operations |
| **TTL** | Time To Live (cache expiration) |
| **DAG** | Directed Acyclic Graph (Airflow workflow) |
| **MVP** | Minimum Viable Product |
| **KRX** | Korea Exchange |

### 1.4 References

- [Product Requirements Document (PRD)](PRD.md)
- [OpenAPI Specification](../api/openapi.yaml)
- [Database Schema Documentation](../database/README.md)
- [Data Pipeline Documentation](../data_pipeline/README.md)
- IEEE Std 830-1998: IEEE Recommended Practice for Software Requirements Specifications

### 1.5 Overview

This document is organized as follows:
- **Section 2**: Overall system description and context
- **Section 3**: Specific functional requirements
- **Section 4**: External interface requirements
- **Section 5**: Detailed system features
- **Section 6**: Non-functional requirements (performance, security, etc.)
- **Section 7**: Other requirements (legal, regulatory, etc.)

---

## 2. Overall Description

### 2.1 Product Perspective

The Stock Screening Platform is a new, self-contained web application that integrates with external data sources:

```
┌─────────────────────────────────────────────────────────────┐
│                        End Users                             │
│              (Web Browser - Desktop/Mobile)                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               Stock Screening Platform                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Frontend    │  │   Backend    │  │   Database   │      │
│  │  (React)     │──│   (FastAPI)  │──│ (PostgreSQL) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                           │                                  │
│                    ┌──────┴──────┐                          │
│                    ▼             ▼                           │
│           ┌──────────────┐  ┌──────────────┐               │
│           │  Data        │  │  Cache       │               │
│           │  Pipeline    │  │  (Redis)     │               │
│           │  (Airflow)   │  └──────────────┘               │
│           └──────────────┘                                  │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌──────────────┐   ┌──────────────┐
│  KRX API     │   │  F&Guide API │
│  (Prices)    │   │  (Financials)│
└──────────────┘   └──────────────┘
```

**System Interfaces**:
- **Web Browser**: Primary user interface (Chrome, Safari, Firefox, Edge)
- **KRX API**: Real-time/delayed stock price data
- **F&Guide API**: Financial statement and earnings data
- **SMTP Server**: Email notifications for alerts
- **Payment Gateway**: Subscription payment processing (Stripe/Toss)

**Hardware Interfaces**:
- **Server**: Cloud-based infrastructure (AWS/GCP/Naver Cloud)
- **Database**: PostgreSQL with TimescaleDB extension
- **Cache**: Redis cluster for high-performance caching

**Software Interfaces**:
- **Operating System**: Linux (Ubuntu 22.04 LTS or later)
- **Web Server**: NGINX (reverse proxy)
- **Container Runtime**: Docker 24+
- **Orchestration**: Kubernetes 1.29+

### 2.2 Product Functions

**Major Functions**:

1. **Stock Screening**
   - Filter stocks using multiple criteria across 200+ indicators
   - Save and reuse custom screening configurations
   - Use pre-built templates (dividend, value, growth, quality)
   - Export screening results to CSV/Excel

2. **Stock Analysis**
   - View detailed stock information (price, financials, indicators)
   - Display interactive price charts with multiple timeframes
   - Show 5-year financial statement history
   - Compare stock with industry peers

3. **Market Insights**
   - Display real-time market overview (KOSPI/KOSDAQ indices)
   - Identify hot stocks (volume surge detection)
   - Show top gainers/losers by timeframe
   - Track sector performance

4. **Portfolio Management**
   - Create and manage multiple portfolios
   - Track holdings with purchase price and quantity
   - Calculate unrealized gains/losses
   - Compare portfolio performance vs KOSPI benchmark

5. **Alerts & Notifications**
   - Set price alerts (above/below threshold)
   - Configure volume surge alerts
   - Receive notifications via email/push
   - Manage active alerts

6. **User Management**
   - Register with email/password or OAuth (Kakao, Naver, Google)
   - Manage user profile and preferences
   - Subscribe to paid tiers (Basic, Pro)
   - View subscription and billing history

### 2.3 User Classes and Characteristics

**User Class 1: Novice Investor**
- **Characteristics**: Limited investment experience (< 1 year), needs guidance
- **Technical Expertise**: Low (basic web browsing)
- **Frequency of Use**: Weekly
- **Priority**: High (target demographic)
- **Functions Used**: Pre-built templates, stock details, watchlists

**User Class 2: Active Trader**
- **Characteristics**: Frequent trading, seeks short-term opportunities
- **Technical Expertise**: Medium
- **Frequency of Use**: Daily (multiple times)
- **Priority**: High (high engagement)
- **Functions Used**: Hot stocks, custom screening, alerts

**User Class 3: Value Investor**
- **Characteristics**: Long-term focus, fundamental analysis
- **Technical Expertise**: High (understands financial metrics)
- **Frequency of Use**: Weekly
- **Priority**: Medium
- **Functions Used**: Advanced screening, financial statements, peer comparison

**User Class 4: Administrator**
- **Characteristics**: System operator, data quality monitor
- **Technical Expertise**: Very High
- **Frequency of Use**: Daily
- **Priority**: Critical (system maintenance)
- **Functions Used**: Data pipeline monitoring, user management, system health

### 2.4 Operating Environment

**Client-Side**:
- **Web Browsers**: Chrome 100+, Safari 15+, Firefox 100+, Edge 100+
- **Screen Resolutions**: 360px width minimum (mobile) to 4K displays
- **JavaScript**: ES2020+ support required
- **Storage**: 50MB minimum for cached data

**Server-Side**:
- **Operating System**: Ubuntu 22.04 LTS or compatible Linux distribution
- **Python**: 3.11 or later
- **Node.js**: 18 LTS or later (for frontend build)
- **Database**: PostgreSQL 16+ with TimescaleDB 2.14+
- **Cache**: Redis 7+
- **Container Runtime**: Docker 24+ / Kubernetes 1.29+

**Network**:
- **Bandwidth**: 100 Mbps minimum (server-side)
- **Latency**: < 50ms to database (same region deployment)
- **Firewall**: Ports 80 (HTTP), 443 (HTTPS), 5432 (PostgreSQL), 6379 (Redis)

### 2.5 Design and Implementation Constraints

**Regulatory Constraints**:
- **Data Licensing**: Must comply with KRX and F&Guide data usage terms
- **Investment Disclaimer**: Display disclaimer on all pages with financial data
- **Privacy Compliance**: GDPR and PIPA (Personal Information Protection Act) compliance
- **Financial Regulations**: Cannot provide personalized investment advice

**Technical Constraints**:
- **Database**: Must use PostgreSQL for ACID compliance and TimescaleDB for time-series optimization
- **Authentication**: Must use JWT for stateless authentication
- **Data Freshness**: Price data must be updated within 30 minutes of market close
- **Browser Support**: Must support last 2 major versions of mainstream browsers

**Business Constraints**:
- **Budget**: Limited to $50K development budget (MVP phase)
- **Timeline**: MVP must launch within 12 weeks
- **Team Size**: Maximum 5 developers (2 frontend, 2 backend, 1 DevOps)
- **Third-Party Costs**: API costs must not exceed $2K/month

**Performance Constraints**:
- **Response Time**: API calls must complete in < 200ms (p95)
- **Screening Query**: Must return results in < 500ms (p99)
- **Concurrent Users**: Must support 10,000 concurrent users without degradation
- **Database Size**: Must efficiently handle 10+ years of historical data

### 2.6 Assumptions and Dependencies

**Assumptions**:
1. Users have stable internet connection (minimum 1 Mbps)
2. Users have modern web browsers with JavaScript enabled
3. KRX and F&Guide APIs remain available and pricing stable
4. Korean market structure (KOSPI/KOSDAQ) remains consistent
5. PostgreSQL and TimescaleDB continue to be actively maintained

**Dependencies**:
1. **External APIs**:
   - KRX API for stock price data (critical dependency)
   - F&Guide API for financial statements (critical dependency)
   - OAuth providers (Kakao, Naver, Google) for social login

2. **Third-Party Services**:
   - Stripe/Toss for payment processing
   - SMTP service (Gmail, SendGrid) for email notifications
   - Cloud provider (AWS/GCP/Naver Cloud) for infrastructure

3. **Open Source Libraries**:
   - React, FastAPI, PostgreSQL, Redis, Airflow (see package.json, requirements.txt)
   - Security updates must be applied promptly

4. **Data Availability**:
   - Daily price data available by 18:00 KST
   - Quarterly financial statements within 45 days of quarter end
   - Annual reports within 90 days of fiscal year end

---