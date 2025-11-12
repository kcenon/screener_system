---
id: prd-overview
title: PRD - Overview
description: Executive summary, product vision, and market analysis
sidebar_label: Overview
sidebar_position: 1
tags:
  - specification
  - product
  - requirements
---

:::info Navigation
- [Overview](overview.md) (Current)
- [Users & Features](users-features.md)
- [Technical](technical.md)
- [Implementation](implementation.md)
:::

# Product Requirements Document - Overview

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

| Metric | Target | Timeline |
|--------|--------|----------|
| **Active Users** | 50,000+ | 12 months |
| **Conversion Rate** (Free → Paid) | 5% | 6 months |
| **User Retention** (30-day) | 40% | 6 months |
| **Average Session Duration** | 8+ minutes | 3 months |
| **Screening Performance** | < 500ms query time | Launch |

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