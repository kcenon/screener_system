#!/bin/bash
# =============================================================================
# Initialize Airflow Database
# =============================================================================
#
# This script creates the Airflow metadata database if it doesn't exist.
# Run this script once during initial setup or when setting up Airflow.
#
# Usage:
#   ./database/scripts/init_airflow_db.sh
#
# Or via Docker:
#   docker-compose exec postgres /docker-entrypoint-initdb.d/init_airflow_db.sh
#
# =============================================================================

set -e

# Database configuration
POSTGRES_USER="${POSTGRES_USER:-screener_user}"
POSTGRES_DB="${POSTGRES_DB:-postgres}"
AIRFLOW_DB="${AIRFLOW_DB:-airflow}"

echo "=========================================================================="
echo "  Airflow Database Initialization"
echo "=========================================================================="
echo "User: $POSTGRES_USER"
echo "Airflow DB: $AIRFLOW_DB"
echo ""

# Check if airflow database exists
DB_EXISTS=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT 1 FROM pg_database WHERE datname='$AIRFLOW_DB'")

if [ "$DB_EXISTS" = "1" ]; then
    echo "✓ Database '$AIRFLOW_DB' already exists"
else
    echo "Creating database '$AIRFLOW_DB'..."
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE DATABASE $AIRFLOW_DB OWNER $POSTGRES_USER;"
    echo "✓ Database '$AIRFLOW_DB' created successfully"
fi

echo ""
echo "=========================================================================="
echo "  Airflow Database Ready"
echo "=========================================================================="
echo ""
echo "You can now start Airflow services:"
echo "  docker-compose up -d airflow_webserver airflow_scheduler"
echo ""
