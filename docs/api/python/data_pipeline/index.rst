Data Pipeline Reference
======================

Apache Airflow data pipeline documentation.

.. toctree::
   :maxdepth: 2
   :caption: Data Pipeline Components:

   dags
   clients

Overview
--------

The data pipeline handles:

* Daily stock price ingestion from KIS API
* Technical indicator calculation (200+ indicators)
* Financial data updates
* Data validation and quality checks

DAGs are scheduled to run:

* **Daily Price Updates**: Every trading day at 18:00 KST
* **Indicator Calculations**: After price updates complete
* **Weekly Reports**: Sundays at 09:00 KST
