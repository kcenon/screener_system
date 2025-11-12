Backend API Reference
====================

This section documents the FastAPI backend application structure.

.. toctree::
   :maxdepth: 2
   :caption: Backend Components:

   api
   services
   repositories
   models
   core
   middleware

The backend is organized into layers:

1. **API Layer** (:doc:`api`): FastAPI route handlers and endpoints
2. **Service Layer** (:doc:`services`): Business logic and orchestration
3. **Repository Layer** (:doc:`repositories`): Database access and queries
4. **Model Layer** (:doc:`models`): SQLAlchemy database models
5. **Core** (:doc:`core`): Configuration, security, caching
6. **Middleware** (:doc:`middleware`): Request/response processing
