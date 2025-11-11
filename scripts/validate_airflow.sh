#!/bin/bash

# Airflow DAG Runtime Validation Script
# Tests Airflow services, DAG parsing, and database connections

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "Airflow DAG Runtime Validation"
echo "========================================="
echo ""

# Check if Airflow containers are running
echo "Checking Airflow Services..."
echo ""

if ! docker ps | grep -q "screener_airflow_webserver"; then
    echo -e "${RED}✗ Airflow webserver not running${NC}"
    echo "Start with: docker-compose up -d airflow-webserver"
    exit 1
fi
echo -e "${GREEN}✓ Airflow webserver running${NC}"

if ! docker ps | grep -q "screener_airflow_scheduler"; then
    echo -e "${RED}✗ Airflow scheduler not running${NC}"
    echo "Start with: docker-compose up -d airflow-scheduler"
    exit 1
fi
echo -e "${GREEN}✓ Airflow scheduler running${NC}"

# Check Airflow health endpoint
echo ""
echo "Checking Airflow Health..."
echo ""

HEALTH_RESPONSE=$(curl -s http://localhost:8080/health)

if echo "$HEALTH_RESPONSE" | grep -q '"status": "healthy"'; then
    echo -e "${GREEN}✓ Metadatabase healthy${NC}"
else
    echo -e "${RED}✗ Metadatabase unhealthy${NC}"
    echo "Response: $HEALTH_RESPONSE"
    exit 1
fi

if echo "$HEALTH_RESPONSE" | grep -q '"scheduler".*"healthy"'; then
    echo -e "${GREEN}✓ Scheduler healthy${NC}"
else
    echo -e "${YELLOW}⚠ Scheduler status check inconclusive${NC}"
fi

# List DAGs
echo ""
echo "Checking DAG Files..."
echo ""

DAG_LIST=$(docker exec screener_airflow_webserver airflow dags list 2>/dev/null)

echo "Available DAGs:"
echo "$DAG_LIST"
echo ""

# Check specific DAGs
if echo "$DAG_LIST" | grep -q "daily_price_ingestion"; then
    echo -e "${GREEN}✓ daily_price_ingestion DAG found${NC}"
    DAILY_PRICE_DAG=true
else
    echo -e "${YELLOW}⚠ daily_price_ingestion DAG not found${NC}"
    DAILY_PRICE_DAG=false
fi

if echo "$DAG_LIST" | grep -q "indicator_calculation"; then
    echo -e "${GREEN}✓ indicator_calculation DAG found${NC}"
    INDICATOR_DAG=true
else
    echo -e "${YELLOW}⚠ indicator_calculation DAG not found${NC}"
    INDICATOR_DAG=false
fi

# Check DAG parsing errors
echo ""
echo "Checking for DAG Import Errors..."
echo ""

IMPORT_ERRORS=$(docker exec screener_airflow_webserver airflow dags list-import-errors 2>/dev/null)

if [ -z "$IMPORT_ERRORS" ] || echo "$IMPORT_ERRORS" | grep -q "No data found"; then
    echo -e "${GREEN}✓ No DAG import errors${NC}"
else
    echo -e "${RED}✗ DAG import errors found:${NC}"
    echo "$IMPORT_ERRORS"
fi

# Check database connection
echo ""
echo "Checking Database Connection..."
echo ""

DB_CHECK=$(docker exec screener_airflow_webserver airflow db check 2>/dev/null || echo "DB check failed")

if echo "$DB_CHECK" | grep -q "No issues"; then
    echo -e "${GREEN}✓ Database connection healthy${NC}"
else
    echo -e "${YELLOW}⚠ Database check:${NC}"
    echo "$DB_CHECK"
fi

# Test database connection to screener_db
echo ""
echo "Checking Screener Database Connection..."
echo ""

if docker exec screener_postgres psql -U screener_user -d screener_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Screener database accessible${NC}"
else
    echo -e "${RED}✗ Screener database not accessible${NC}"
    exit 1
fi

# Check if stock tables exist
STOCK_TABLE_CHECK=$(docker exec screener_postgres psql -U screener_user -d screener_db -c "\dt stocks" 2>&1)

if echo "$STOCK_TABLE_CHECK" | grep -q "stocks"; then
    echo -e "${GREEN}✓ Stocks table exists${NC}"

    # Count stocks
    STOCK_COUNT=$(docker exec screener_postgres psql -U screener_user -d screener_db -t -c "SELECT COUNT(*) FROM stocks;" 2>/dev/null | tr -d ' ')
    echo "  Stock count: $STOCK_COUNT"
else
    echo -e "${YELLOW}⚠ Stocks table not found${NC}"
fi

# Check daily_prices table
PRICE_TABLE_CHECK=$(docker exec screener_postgres psql -U screener_user -d screener_db -c "\dt daily_prices" 2>&1)

if echo "$PRICE_TABLE_CHECK" | grep -q "daily_prices"; then
    echo -e "${GREEN}✓ Daily prices table exists${NC}"

    # Count price records
    PRICE_COUNT=$(docker exec screener_postgres psql -U screener_user -d screener_db -t -c "SELECT COUNT(*) FROM daily_prices;" 2>/dev/null | tr -d ' ')
    echo "  Price record count: $PRICE_COUNT"
else
    echo -e "${YELLOW}⚠ Daily prices table not found${NC}"
fi

# Summary
echo ""
echo "========================================="
echo "Validation Summary"
echo "========================================="
echo ""

ISSUES=0

if [ "$DAILY_PRICE_DAG" = false ]; then
    echo -e "${YELLOW}⚠ Issue: daily_price_ingestion DAG not recognized${NC}"
    ISSUES=$((ISSUES + 1))
fi

if [ "$INDICATOR_DAG" = false ]; then
    echo -e "${YELLOW}⚠ Issue: indicator_calculation DAG not recognized${NC}"
    ISSUES=$((ISSUES + 1))
fi

if [ "$STOCK_COUNT" = "0" ] || [ -z "$STOCK_COUNT" ]; then
    echo -e "${YELLOW}⚠ Issue: No stock data loaded${NC}"
    ISSUES=$((ISSUES + 1))
fi

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Access Airflow UI: http://localhost:8080"
    echo "  2. Default credentials: admin / admin"
    echo "  3. Unpause DAGs to enable scheduling"
    echo "  4. Trigger manual DAG run for testing"
else
    echo -e "${YELLOW}⚠ $ISSUES issue(s) found${NC}"
    echo ""
    echo "Recommendations:"
    if [ "$DAILY_PRICE_DAG" = false ]; then
        echo "  - Check daily_price_ingestion_dag.py for syntax errors"
    fi
    if [ "$INDICATOR_DAG" = false ]; then
        echo "  - Check indicator_calculation_dag.py for syntax errors"
    fi
    if [ "$STOCK_COUNT" = "0" ] || [ -z "$STOCK_COUNT" ]; then
        echo "  - Load stock data before running DAGs"
        echo "  - Check database seed scripts"
    fi
fi

echo ""
