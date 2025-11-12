Stock Screening Platform - Backend API Documentation
=================================================

Welcome to the Stock Screening Platform Backend API documentation. This documentation is automatically generated from the Python backend source code using Sphinx.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   backend/index
   data_pipeline/index

Overview
--------

The Stock Screening Platform provides a comprehensive API for:

* **Stock Screening**: Filter 2,400+ Korean stocks using 200+ indicators
* **Real-time Data**: WebSocket streaming for live price updates
* **User Authentication**: JWT-based authentication with role-based access control
* **Portfolio Management**: Track holdings and performance
* **Price Alerts**: Customizable notifications

Architecture
-----------

The backend is built with:

* **FastAPI**: Modern, fast web framework for building APIs
* **SQLAlchemy 2.0**: Async ORM for database operations
* **PostgreSQL + TimescaleDB**: Time-series data storage
* **Redis**: Caching and pub/sub for real-time features
* **Celery**: Background task processing

Quick Start
----------

To use this API documentation:

1. Browse the **Backend** section for API endpoints, services, and models
2. Check **Data Pipeline** for Airflow DAGs and data ingestion
3. Use the search function to find specific classes or methods

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
