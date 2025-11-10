#!/bin/bash
# ============================================================================
# Initialize Test Database
# ============================================================================
# This script creates a separate test database for running tests
# It runs during PostgreSQL container initialization
# ============================================================================

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create test database if it doesn't exist
    SELECT 'CREATE DATABASE screener_test'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'screener_test')\gexec

    -- Grant privileges to screener_user
    GRANT ALL PRIVILEGES ON DATABASE screener_test TO $POSTGRES_USER;
EOSQL

echo "Test database 'screener_test' created successfully"
