#!/bin/bash
# ============================================================================
# Indexes and Materialized Views Verification Script (Docker Version)
# ============================================================================
#
# This script verifies indexes and materialized views using Docker
#
# Usage:
#   ./database/scripts/verify_indexes_views_docker.sh
#
# Prerequisites:
#   - Docker and Docker Compose running
#   - PostgreSQL container (postgres) running
#
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_ROOT"

# Database parameters
DB_NAME="${SCREENER_DB_NAME:-screener_db}"
DB_USER="${SCREENER_DB_USER:-screener_user}"

# Docker exec command
DOCKER_EXEC="docker-compose exec -T postgres"

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Run SQL query via Docker
run_query() {
    echo "$1" | $DOCKER_EXEC psql -U $DB_USER -d $DB_NAME -t -A
}

# ============================================================================
# Verification Tests
# ============================================================================

echo ""
log_info "==========================================================================="
log_info "  Stock Screener - Indexes & Views Verification (Docker)"
log_info "==========================================================================="
log_info "Database: $DB_USER@postgres/$DB_NAME"
echo ""

# Test 1: Count indexes
log_info "Test 1: Verifying Indexes"
log_info "==========================================================================="

INDEX_COUNT=$(run_query "
    SELECT COUNT(*)
    FROM pg_indexes
    WHERE schemaname = 'public'
    AND indexname NOT LIKE '%_pkey';
")

log_info "Found $INDEX_COUNT custom indexes"

if [ "$INDEX_COUNT" -gt 30 ]; then
    log_success "✓ All indexes created ($INDEX_COUNT found, expected 30+)"
else
    log_error "✗ Expected 30+ indexes, found only $INDEX_COUNT"
fi

# Test 2: List all indexes
log_info ""
log_info "Index Inventory (top 15):"
run_query "
    SELECT
        tablename || '.' || indexname AS idx,
        pg_size_pretty(pg_relation_size(indexrelid)) AS size
    FROM pg_stat_user_indexes
    WHERE schemaname = 'public'
    ORDER BY pg_relation_size(indexrelid) DESC
    LIMIT 15;
" | while IFS='|' read -r idx size; do
    echo "  - $idx (${size})"
done

# Test 3: Verify materialized views
log_info ""
log_info "Test 2: Verifying Materialized Views"
log_info "==========================================================================="

MATVIEW_COUNT=$(run_query "
    SELECT COUNT(*)
    FROM pg_matviews
    WHERE schemaname = 'public';
")

log_info "Found $MATVIEW_COUNT materialized views"

if [ "$MATVIEW_COUNT" -ge 6 ]; then
    log_success "✓ All materialized views created ($MATVIEW_COUNT found, expected 6+)"
else
    log_error "✗ Expected 6+ materialized views, found only $MATVIEW_COUNT"
fi

# List materialized views
log_info ""
log_info "Materialized View Inventory:"
run_query "
    SELECT
        matviewname,
        pg_size_pretty(pg_total_relation_size('public.'||matviewname)) AS size,
        ispopulated::TEXT
    FROM pg_matviews
    WHERE schemaname = 'public'
    ORDER BY matviewname;
" | while IFS='|' read -r viewname size populated; do
    if [ "$populated" = "t" ]; then
        echo -e "  ${GREEN}✓${NC} $viewname (${size}, populated)"
    else
        echo -e "  ${YELLOW}!${NC} $viewname (${size}, not populated)"
    fi
done

# Test 4: Verify key indexes exist
log_info ""
log_info "Test 3: Checking Key Indexes"
log_info "==========================================================================="

REQUIRED_INDEXES=(
    "idx_stocks_market"
    "idx_stocks_sector"
    "idx_stocks_name_trgm"
    "idx_indicators_per"
    "idx_indicators_pbr"
    "idx_indicators_roe"
    "idx_alerts_user_active"
)

MISSING_COUNT=0
for idx in "${REQUIRED_INDEXES[@]}"; do
    EXISTS=$(run_query "SELECT COUNT(*) FROM pg_indexes WHERE indexname = '$idx';")
    if [ "$EXISTS" -eq 1 ]; then
        log_success "  ✓ $idx"
    else
        log_error "  ✗ $idx MISSING"
        MISSING_COUNT=$((MISSING_COUNT + 1))
    fi
done

if [ "$MISSING_COUNT" -eq 0 ]; then
    log_success "✓ All key indexes verified"
fi

# Test 5: Verify pg_trgm extension
log_info ""
log_info "Test 4: Verifying Extensions"
log_info "==========================================================================="

TRGM_INSTALLED=$(run_query "SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_trgm';")
if [ "$TRGM_INSTALLED" -eq 1 ]; then
    log_success "✓ pg_trgm extension installed (fuzzy search enabled)"
else
    log_error "✗ pg_trgm extension NOT installed"
fi

TIMESCALEDB_INSTALLED=$(run_query "SELECT COUNT(*) FROM pg_extension WHERE extname = 'timescaledb';")
if [ "$TIMESCALEDB_INSTALLED" -eq 1 ]; then
    log_success "✓ timescaledb extension installed"
else
    log_error "✗ timescaledb extension NOT installed"
fi

# Test 6: Verify refresh function
log_info ""
log_info "Test 5: Verifying Refresh Function"
log_info "==========================================================================="

FUNCTION_EXISTS=$(run_query "
    SELECT COUNT(*)
    FROM pg_proc
    WHERE proname = 'refresh_all_materialized_views';
")

if [ "$FUNCTION_EXISTS" -eq 1 ]; then
    log_success "✓ refresh_all_materialized_views() function exists"
else
    log_error "✗ refresh_all_materialized_views() function NOT FOUND"
fi

# Test 7: Check index_usage_stats view
log_info ""
log_info "Test 6: Verifying Monitoring Views"
log_info "==========================================================================="

VIEW_EXISTS=$(run_query "
    SELECT COUNT(*)
    FROM pg_views
    WHERE schemaname = 'public' AND viewname = 'index_usage_stats';
")

if [ "$VIEW_EXISTS" -eq 1 ]; then
    log_success "✓ index_usage_stats view exists"
else
    log_error "✗ index_usage_stats view NOT FOUND"
fi

# Test 8: Verify indexes on materialized views
log_info ""
log_info "Test 7: Verifying Indexes on Materialized Views"
log_info "==========================================================================="

MATVIEW_INDEXES=$(run_query "
    SELECT COUNT(*)
    FROM pg_indexes
    WHERE schemaname = 'public'
    AND (
        indexname LIKE 'idx_screening_%'
        OR indexname LIKE 'idx_sector_%'
        OR indexname LIKE 'idx_dividend_%'
        OR indexname LIKE 'idx_value_%'
        OR indexname LIKE 'idx_growth_%'
        OR indexname LIKE 'idx_quality_%'
    );
")

log_info "Found $MATVIEW_INDEXES indexes on materialized views"

if [ "$MATVIEW_INDEXES" -gt 5 ]; then
    log_success "✓ Materialized views have indexes for fast filtering"
else
    log_warning "! Only $MATVIEW_INDEXES indexes found on materialized views"
fi

# Test 9: Total database size
log_info ""
log_info "Test 8: Database Size Summary"
log_info "==========================================================================="

TOTAL_INDEX_SIZE=$(run_query "
    SELECT pg_size_pretty(SUM(pg_relation_size(indexrelid)))
    FROM pg_stat_user_indexes
    WHERE schemaname = 'public';
")

TOTAL_MATVIEW_SIZE=$(run_query "
    SELECT pg_size_pretty(SUM(pg_total_relation_size('public.'||matviewname)))
    FROM pg_matviews
    WHERE schemaname = 'public';
")

log_info "Total index size: $TOTAL_INDEX_SIZE"
log_info "Total materialized view size: $TOTAL_MATVIEW_SIZE"

# Summary
echo ""
log_info "==========================================================================="
log_success "Verification Complete!"
log_info "==========================================================================="
echo ""
log_info "Summary:"
log_info "  - Indexes: $INDEX_COUNT created"
log_info "  - Materialized Views: $MATVIEW_COUNT created"
log_info "  - Total Index Size: $TOTAL_INDEX_SIZE"
log_info "  - Total Materialized View Size: $TOTAL_MATVIEW_SIZE"
echo ""
log_info "Next Steps:"
log_info "  1. Load sample data to test query performance"
log_info "  2. Run EXPLAIN ANALYZE on screening queries"
log_info "  3. Monitor index usage: SELECT * FROM index_usage_stats;"
log_info "  4. Refresh materialized views: SELECT refresh_all_materialized_views();"
echo ""
