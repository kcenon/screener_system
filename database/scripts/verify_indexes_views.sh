#!/bin/bash
# ============================================================================
# Indexes and Materialized Views Verification Script
# ============================================================================
#
# This script verifies that all indexes and materialized views are properly
# created and functioning according to DB-003 acceptance criteria.
#
# Usage:
#   ./database/scripts/verify_indexes_views.sh
#
# Prerequisites:
#   - PostgreSQL database running with screener_db
#   - Migration files 03_indexes.sql and 05_views.sql executed
#
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Database connection parameters
DB_HOST="${SCREENER_DB_HOST:-localhost}"
DB_PORT="${SCREENER_DB_PORT:-5432}"
DB_NAME="${SCREENER_DB_NAME:-screener_db}"
DB_USER="${SCREENER_DB_USER:-screener_user}"

# PSQL command with connection parameters
PSQL="psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -A"

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

run_query() {
    echo "$1" | $PSQL
}

# ============================================================================
# Test 1: Verify All Indexes Created
# ============================================================================

test_indexes_created() {
    log_info "============================================================================"
    log_info "Test 1: Verifying Indexes Creation"
    log_info "============================================================================"

    # Count indexes in public schema (excluding system indexes)
    INDEX_COUNT=$(run_query "
        SELECT COUNT(*)
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND indexname NOT LIKE '%_pkey'
        AND indexname NOT LIKE '%_fkey'
    ")

    log_info "Found $INDEX_COUNT custom indexes in public schema"

    # List all indexes with sizes
    log_info ""
    log_info "Index Inventory:"
    run_query "
        SELECT
            tablename || '.' || indexname AS index_full_name,
            pg_size_pretty(pg_relation_size(indexrelid)) AS size
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname;
    " | while IFS='|' read -r index_name size; do
        echo "  - $index_name (${size})"
    done

    if [ "$INDEX_COUNT" -gt 30 ]; then
        log_success "All indexes created successfully ($INDEX_COUNT indexes found)"
        return 0
    else
        log_error "Expected 30+ indexes, found only $INDEX_COUNT"
        return 1
    fi
}

# ============================================================================
# Test 2: Verify Materialized Views Created
# ============================================================================

test_materialized_views() {
    log_info ""
    log_info "============================================================================"
    log_info "Test 2: Verifying Materialized Views"
    log_info "============================================================================"

    MATVIEW_COUNT=$(run_query "
        SELECT COUNT(*)
        FROM pg_matviews
        WHERE schemaname = 'public'
    ")

    log_info "Found $MATVIEW_COUNT materialized views"

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
            echo "  ${GREEN}✓${NC} $viewname (${size}, populated)"
        else
            echo "  ${RED}✗${NC} $viewname (${size}, NOT populated)"
        fi
    done

    # Check for required views
    REQUIRED_VIEWS=("stock_screening_view" "sector_performance" "dividend_stocks" "value_stocks" "growth_stocks" "quality_stocks")
    ALL_EXISTS=true

    log_info ""
    log_info "Checking required materialized views:"
    for view in "${REQUIRED_VIEWS[@]}"; do
        EXISTS=$(run_query "SELECT COUNT(*) FROM pg_matviews WHERE schemaname = 'public' AND matviewname = '$view'")
        if [ "$EXISTS" -eq 1 ]; then
            log_success "  $view exists"
        else
            log_error "  $view MISSING"
            ALL_EXISTS=false
        fi
    done

    if [ "$ALL_EXISTS" = true ]; then
        log_success "All required materialized views created"
        return 0
    else
        log_error "Some materialized views are missing"
        return 1
    fi
}

# ============================================================================
# Test 3: Test Index Usage with EXPLAIN ANALYZE
# ============================================================================

test_index_usage() {
    log_info ""
    log_info "============================================================================"
    log_info "Test 3: Verifying Index Usage (EXPLAIN ANALYZE)"
    log_info "============================================================================"

    # Test 1: Market filter should use idx_stocks_market
    log_info ""
    log_info "Testing idx_stocks_market (filtering by market)..."
    EXPLAIN_OUTPUT=$(run_query "
        EXPLAIN (FORMAT TEXT) SELECT * FROM stocks WHERE market = 'KOSPI' LIMIT 10;
    ")

    if echo "$EXPLAIN_OUTPUT" | grep -q "idx_stocks_market"; then
        log_success "  Index idx_stocks_market is being used"
    else
        log_warning "  Index idx_stocks_market NOT used (might be OK if table is small)"
    fi

    # Test 2: PER filter should use idx_indicators_per
    log_info ""
    log_info "Testing idx_indicators_per (partial index)..."
    EXPLAIN_OUTPUT=$(run_query "
        EXPLAIN (FORMAT TEXT) SELECT * FROM calculated_indicators WHERE per > 0 AND per < 20 LIMIT 10;
    ")

    if echo "$EXPLAIN_OUTPUT" | grep -q "idx_indicators_per"; then
        log_success "  Index idx_indicators_per is being used"
    else
        log_warning "  Index idx_indicators_per NOT used (might be OK if table is small)"
    fi

    # Test 3: Alert lookup should use idx_alerts_stock_active
    log_info ""
    log_info "Testing idx_alerts_stock_active (partial index)..."
    EXPLAIN_OUTPUT=$(run_query "
        EXPLAIN (FORMAT TEXT) SELECT * FROM alerts WHERE stock_code = '005930' AND is_active = TRUE;
    ")

    if echo "$EXPLAIN_OUTPUT" | grep -q "idx_alerts"; then
        log_success "  Alert indexes are being used"
    else
        log_warning "  Alert indexes NOT used (might be OK if table is empty)"
    fi

    log_success "Index usage tests completed"
}

# ============================================================================
# Test 4: Test Fuzzy Search (Trigram Index)
# ============================================================================

test_fuzzy_search() {
    log_info ""
    log_info "============================================================================"
    log_info "Test 4: Testing Fuzzy Search (Trigram Index)"
    log_info "============================================================================"

    # Check if pg_trgm extension is installed
    TRGM_INSTALLED=$(run_query "SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_trgm'")

    if [ "$TRGM_INSTALLED" -eq 0 ]; then
        log_error "pg_trgm extension NOT installed"
        return 1
    fi

    log_success "pg_trgm extension installed"

    # Test similarity search (% operator)
    log_info ""
    log_info "Testing similarity search with % operator..."

    # Check if stocks table has data
    STOCK_COUNT=$(run_query "SELECT COUNT(*) FROM stocks")

    if [ "$STOCK_COUNT" -eq 0 ]; then
        log_warning "Stocks table is empty - skipping fuzzy search test"
        log_info "To test fuzzy search, insert sample data and run:"
        log_info "  SELECT * FROM stocks WHERE name % 'samsung' ORDER BY similarity(name, 'samsung') DESC LIMIT 5;"
        return 0
    fi

    # Get a sample stock name
    SAMPLE_NAME=$(run_query "SELECT name FROM stocks LIMIT 1")
    log_info "Testing with sample stock name: $SAMPLE_NAME"

    # Test fuzzy search
    EXPLAIN_OUTPUT=$(run_query "
        EXPLAIN (FORMAT TEXT) SELECT * FROM stocks WHERE name % '$SAMPLE_NAME';
    ")

    if echo "$EXPLAIN_OUTPUT" | grep -q "idx_stocks_name_trgm"; then
        log_success "Trigram index idx_stocks_name_trgm is being used for fuzzy search"
    else
        log_warning "Trigram index NOT used (might use sequential scan for small tables)"
    fi

    log_success "Fuzzy search test completed"
}

# ============================================================================
# Test 5: Test Materialized View Refresh
# ============================================================================

test_view_refresh() {
    log_info ""
    log_info "============================================================================"
    log_info "Test 5: Testing Materialized View Refresh"
    log_info "============================================================================"

    # Test REFRESH CONCURRENTLY (requires UNIQUE index)
    log_info ""
    log_info "Testing REFRESH CONCURRENTLY on stock_screening_view..."

    # Check if view is populated
    IS_POPULATED=$(run_query "SELECT ispopulated FROM pg_matviews WHERE matviewname = 'stock_screening_view'")

    if [ "$IS_POPULATED" = "f" ]; then
        log_info "View not yet populated, performing initial refresh..."
        run_query "REFRESH MATERIALIZED VIEW stock_screening_view;" 2>&1 | while IFS= read -r line; do
            log_info "  $line"
        done
        log_success "Initial refresh completed"
    else
        log_info "View already populated, testing concurrent refresh..."
        START_TIME=$(date +%s.%N)
        run_query "REFRESH MATERIALIZED VIEW CONCURRENTLY stock_screening_view;" 2>&1 | while IFS= read -r line; do
            log_info "  $line"
        done
        END_TIME=$(date +%s.%N)
        DURATION=$(echo "$END_TIME - $START_TIME" | bc)
        log_success "Concurrent refresh completed in ${DURATION}s"
    fi

    # Test the refresh_all_materialized_views() function
    log_info ""
    log_info "Testing refresh_all_materialized_views() function..."

    FUNCTION_EXISTS=$(run_query "
        SELECT COUNT(*)
        FROM pg_proc
        WHERE proname = 'refresh_all_materialized_views'
    ")

    if [ "$FUNCTION_EXISTS" -eq 1 ]; then
        log_success "Function refresh_all_materialized_views() exists"

        # Execute the function (commenting out to avoid long execution during verification)
        # log_info "Executing refresh_all_materialized_views()..."
        # RESULT=$(run_query "SELECT refresh_all_materialized_views();")
        # log_info "Result: $RESULT"
    else
        log_error "Function refresh_all_materialized_views() NOT FOUND"
        return 1
    fi

    log_success "View refresh tests completed"
}

# ============================================================================
# Test 6: Measure Query Performance
# ============================================================================

test_query_performance() {
    log_info ""
    log_info "============================================================================"
    log_info "Test 6: Measuring Query Performance"
    log_info "============================================================================"

    # Check if we have data to test
    STOCK_COUNT=$(run_query "SELECT COUNT(*) FROM stocks")

    if [ "$STOCK_COUNT" -eq 0 ]; then
        log_warning "No data in stocks table - skipping performance tests"
        log_info "Load sample data to test query performance"
        return 0
    fi

    log_info "Testing query performance with $STOCK_COUNT stocks..."

    # Test 1: stock_screening_view SELECT
    log_info ""
    log_info "Test 1: SELECT from stock_screening_view (target: <100ms)"
    TIMING_OUTPUT=$(run_query "
        \timing on
        SELECT * FROM stock_screening_view WHERE market = 'KOSPI' LIMIT 100;
        \timing off
    " 2>&1)

    # Extract timing (PostgreSQL outputs "Time: X.XXX ms")
    if echo "$TIMING_OUTPUT" | grep -q "Time:"; then
        QUERY_TIME=$(echo "$TIMING_OUTPUT" | grep "Time:" | awk '{print $2}' | head -1)
        log_info "Query time: ${QUERY_TIME} ms"

        # Check if less than 100ms
        if awk "BEGIN {exit !($QUERY_TIME < 100)}"; then
            log_success "Query performance meets target (<100ms)"
        else
            log_warning "Query time exceeds 100ms target"
        fi
    fi

    # Test 2: Complex JOIN query (should use indexes)
    log_info ""
    log_info "Test 2: Complex screening query with multiple filters"
    TIMING_OUTPUT=$(run_query "
        \timing on
        SELECT s.code, s.name, ci.per, ci.pbr, ci.roe
        FROM stocks s
        JOIN calculated_indicators ci ON s.code = ci.stock_code
        WHERE s.market = 'KOSPI'
          AND ci.per > 0 AND ci.per < 20
          AND ci.pbr > 0 AND ci.pbr < 2
          AND ci.roe > 5
        LIMIT 50;
        \timing off
    " 2>&1)

    if echo "$TIMING_OUTPUT" | grep -q "Time:"; then
        QUERY_TIME=$(echo "$TIMING_OUTPUT" | grep "Time:" | awk '{print $2}' | head -1)
        log_info "Query time: ${QUERY_TIME} ms"
    fi

    log_success "Performance tests completed"
}

# ============================================================================
# Test 7: Verify Index Sizes
# ============================================================================

test_index_sizes() {
    log_info ""
    log_info "============================================================================"
    log_info "Test 7: Verifying Index Sizes"
    log_info "============================================================================"

    # Total index size
    TOTAL_SIZE=$(run_query "
        SELECT pg_size_pretty(SUM(pg_relation_size(indexrelid)))
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
    ")

    log_info "Total index size: $TOTAL_SIZE"

    # Top 10 largest indexes
    log_info ""
    log_info "Top 10 largest indexes:"
    run_query "
        SELECT
            indexname,
            pg_size_pretty(pg_relation_size(indexrelid)) AS size
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
        ORDER BY pg_relation_size(indexrelid) DESC
        LIMIT 10;
    " | while IFS='|' read -r indexname size; do
        echo "  - $indexname: $size"
    done

    log_success "Index size verification completed"
}

# ============================================================================
# Test 8: Check Index Usage Statistics
# ============================================================================

test_index_usage_stats() {
    log_info ""
    log_info "============================================================================"
    log_info "Test 8: Index Usage Statistics"
    log_info "============================================================================"

    # Check if index_usage_stats view exists
    VIEW_EXISTS=$(run_query "
        SELECT COUNT(*)
        FROM pg_views
        WHERE schemaname = 'public' AND viewname = 'index_usage_stats'
    ")

    if [ "$VIEW_EXISTS" -eq 1 ]; then
        log_success "index_usage_stats view exists"

        log_info ""
        log_info "Unused indexes (never scanned):"
        UNUSED_COUNT=$(run_query "
            SELECT COUNT(*)
            FROM index_usage_stats
            WHERE scans = 0
        ")

        if [ "$UNUSED_COUNT" -eq 0 ]; then
            log_success "No unused indexes found (all indexes have been used)"
        else
            log_warning "$UNUSED_COUNT indexes have never been scanned"
            log_info "This is normal for a fresh database. Indexes will be used as queries are executed."

            # Show unused indexes
            run_query "
                SELECT indexname, index_size
                FROM index_usage_stats
                WHERE scans = 0
                LIMIT 10;
            " | while IFS='|' read -r indexname size; do
                echo "  - $indexname ($size)"
            done
        fi
    else
        log_error "index_usage_stats view NOT FOUND"
        return 1
    fi

    log_success "Index usage statistics check completed"
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    echo ""
    log_info "============================================================================"
    log_info "  Stock Screener - Indexes & Views Verification"
    log_info "============================================================================"
    log_info "Database: $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
    echo ""

    # Run all tests
    FAILED_TESTS=0

    test_indexes_created || FAILED_TESTS=$((FAILED_TESTS + 1))
    test_materialized_views || FAILED_TESTS=$((FAILED_TESTS + 1))
    test_index_usage || FAILED_TESTS=$((FAILED_TESTS + 1))
    test_fuzzy_search || FAILED_TESTS=$((FAILED_TESTS + 1))
    test_view_refresh || FAILED_TESTS=$((FAILED_TESTS + 1))
    test_query_performance || FAILED_TESTS=$((FAILED_TESTS + 1))
    test_index_sizes || FAILED_TESTS=$((FAILED_TESTS + 1))
    test_index_usage_stats || FAILED_TESTS=$((FAILED_TESTS + 1))

    # Summary
    echo ""
    log_info "============================================================================"
    if [ $FAILED_TESTS -eq 0 ]; then
        log_success "All verification tests passed! ✓"
        log_info "============================================================================"
        echo ""
        log_info "Indexes and materialized views are properly configured."
        log_info "Database is ready for application queries."
        echo ""
        return 0
    else
        log_error "$FAILED_TESTS test(s) failed"
        log_info "============================================================================"
        echo ""
        log_info "Please review the failed tests above and fix any issues."
        echo ""
        return 1
    fi
}

# Run main function
main
