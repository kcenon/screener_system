# Getting Started

Welcome to the Stock Screening Platform documentation!

This guide will help you set up and start using the platform for Korean stock market analysis.

## What is Stock Screening Platform?

The Stock Screening Platform is a comprehensive stock analysis and screening system for Korean markets (KOSPI/KOSDAQ) with 200+ financial and technical indicators.

### Key Features

- **Advanced Stock Screening**: Filter 2,400+ stocks using 200+ indicators
- **Real-time Market Data**: Live price updates and volume tracking
- **Portfolio Management**: Track holdings and performance vs benchmarks
- **Price Alerts**: Customizable notifications for price movements
- **Financial Analysis**: Detailed financial statements and ratio analysis
- **Technical Analysis**: Charts with indicators (MA, RSI, MACD, etc.)

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/kcenon/screener_system.git
cd screener_system
```

2. Start the development environment:
```bash
docker-compose up -d
```

3. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Next Steps

- [API Reference](/docs/api/intro) - Explore the REST and WebSocket APIs
- [Architecture Overview](/docs/architecture/overview) - Learn about system design
- [User Guides](/docs/guides/intro) - Detailed feature documentation
- [Contributing](/docs/contributing/intro) - Help improve the platform
