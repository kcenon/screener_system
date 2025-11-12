Overview
========

The Stock Screening Platform Backend provides a comprehensive REST API and WebSocket interface for stock market data analysis and screening.

Key Features
-----------

Stock Screening
~~~~~~~~~~~~~~

Filter stocks using 200+ financial and technical indicators:

* **Financial Metrics**: P/E ratio, P/B ratio, ROE, debt ratios, etc.
* **Technical Indicators**: RSI, MACD, moving averages, volume analysis
* **Market Data**: Price, volume, market cap, trading value
* **Sector Analysis**: Industry classification and sector performance

Real-time Updates
~~~~~~~~~~~~~~~

WebSocket streaming for live data:

* Stock price updates
* Order book changes (10-level bid/ask)
* Market-wide updates
* Sector performance tracking

Authentication & Authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Secure JWT-based authentication:

* User registration and login
* Token-based session management
* Role-based access control (RBAC)
* Rate limiting by user tier

Performance
-----------

The API is optimized for high performance:

* **Response Time**: p95 < 200ms for most endpoints
* **Screening**: p99 < 500ms for complex queries
* **Cache Hit Rate**: > 80% for frequently accessed data
* **Concurrent Users**: Supports 1,000+ simultaneous connections

Rate Limiting
-------------

API requests are rate-limited based on subscription tier:

============= ============== =================
Tier          Requests/Min   WebSocket Limit
============= ============== =================
Free          100            5 connections
Standard      500            20 connections
Premium       2000           100 connections
============= ============== =================

Data Sources
------------

Stock data is sourced from:

* **Korea Investment & Securities (KIS) API**: Real-time and historical prices
* **KRX (Korea Exchange)**: Official market data
* **F&Guide**: Fundamental financial data

The data pipeline runs daily to update:

* Stock prices and trading volumes
* Financial statements and ratios
* Technical indicators
* Corporate actions

API Structure
-------------

The backend codebase is organized as follows:

.. code-block::

   backend/app/
   ├── api/           # FastAPI route handlers
   ├── core/          # Core utilities (config, security, cache)
   ├── db/            # Database models and session management
   ├── repositories/  # Data access layer
   ├── schemas/       # Pydantic request/response models
   └── services/      # Business logic layer

For detailed documentation of each module, see:

* :doc:`backend/api` - API endpoints
* :doc:`backend/services` - Business logic services
* :doc:`backend/repositories` - Database operations
* :doc:`backend/models` - SQLAlchemy models
