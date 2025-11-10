#!/bin/bash
# ============================================================================
# Load Seed Data Script
# Description: Load seed data into PostgreSQL database
# Usage:
#   ./load_seed_data.sh                    # Load to screener_db (default)
#   ./load_seed_data.sh screener_test      # Load to test database
# ============================================================================

set -e

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-screener_user}"
DB_NAME="${1:-screener_db}"
SEED_FILE="${2:-seeds/seed_data.sql}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Loading Seed Data${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "Database: ${GREEN}${DB_NAME}${NC}"
echo -e "Host: ${DB_HOST}:${DB_PORT}"
echo -e "User: ${DB_USER}"
echo -e "Seed File: ${SEED_FILE}"
echo ""

# Check if seed file exists
if [ ! -f "$SEED_FILE" ]; then
    echo -e "${RED}Error: Seed file not found: ${SEED_FILE}${NC}"
    echo "Run: python3 seeds/generate_seed_data.py"
    exit 1
fi

# Check database connection
echo -e "${YELLOW}Checking database connection...${NC}"
if ! PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${RED}Error: Cannot connect to database${NC}"
    echo "Make sure PostgreSQL is running and credentials are correct"
    exit 1
fi
echo -e "${GREEN}✓ Database connection successful${NC}"
echo ""

# Show current data counts (before)
echo -e "${YELLOW}Current data counts (before):${NC}"
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
SELECT
    (SELECT COUNT(*) FROM stocks) as stocks,
    (SELECT COUNT(*) FROM daily_prices) as daily_prices,
    (SELECT COUNT(*) FROM financial_statements) as financial_statements,
    (SELECT COUNT(*) FROM calculated_indicators) as calculated_indicators;
"

# Load seed data
echo -e "${YELLOW}Loading seed data...${NC}"
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SEED_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Seed data loaded successfully${NC}"
else
    echo -e "${RED}✗ Error loading seed data${NC}"
    exit 1
fi
echo ""

# Show final data counts (after)
echo -e "${YELLOW}Final data counts (after):${NC}"
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
SELECT
    (SELECT COUNT(*) FROM stocks) as stocks,
    (SELECT COUNT(*) FROM daily_prices) as daily_prices,
    (SELECT COUNT(*) FROM financial_statements) as financial_statements,
    (SELECT COUNT(*) FROM calculated_indicators) as calculated_indicators;
"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Seed data loaded successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
