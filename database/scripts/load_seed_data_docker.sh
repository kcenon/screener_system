#!/bin/bash
# ============================================================================
# Load Seed Data (Docker Version)
# Description: Load seed data into PostgreSQL from within Docker container
# This script is called from docker-entrypoint-initdb.d
# ============================================================================

set -e

# Only load seed data if LOAD_SEED_DATA environment variable is set
if [ -z "$LOAD_SEED_DATA" ]; then
    echo "Skipping seed data (LOAD_SEED_DATA not set)"
    echo "To load seed data, set LOAD_SEED_DATA=1 in .env and rebuild"
    exit 0
fi

echo "========================================="
echo "Loading Seed Data"
echo "========================================="

SEED_FILE="/docker-entrypoint-initdb.d/seeds/seed_data.sql"

if [ ! -f "$SEED_FILE" ]; then
    echo "Error: Seed file not found: $SEED_FILE"
    echo "Please generate seed data first:"
    echo "  cd database && python3 seeds/generate_seed_data.py"
    exit 1
fi

echo "Loading seed data from: $SEED_FILE"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f "$SEED_FILE"

echo "✓ Seed data loaded successfully"
echo "========================================="
