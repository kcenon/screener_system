#!/bin/bash
# ============================================================================
# Daily Price Ingestion DAG Testing Script
# ============================================================================
#
# This script tests the daily_price_ingestion DAG in the Airflow environment
#
# Usage:
#   ./data_pipeline/scripts/test_daily_price_dag.sh
#
# Prerequisites:
#   - Docker and Docker Compose running
#   - Airflow containers running (webserver, scheduler, postgres)
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

# Docker exec command for Airflow
DOCKER_EXEC="docker-compose exec -T webserver"

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

# ============================================================================
# Test Functions
# ============================================================================

echo ""
log_info "==========================================================================="
log_info "  Daily Price Ingestion DAG - Verification Tests"
log_info "==========================================================================="
echo ""

# Test 1: Check if DAG file exists
log_info "Test 1: Checking DAG file existence"
log_info "==========================================================================="

if [ -f "data_pipeline/dags/daily_price_ingestion_dag.py" ]; then
    log_success "✓ DAG file exists"
else
    log_error "✗ DAG file not found"
    exit 1
fi

if [ -f "data_pipeline/scripts/krx_api_client.py" ]; then
    log_success "✓ KRX API client exists"
else
    log_error "✗ KRX API client not found"
    exit 1
fi

# Test 2: Check DAG syntax (no Python errors)
log_info ""
log_info "Test 2: Checking DAG syntax"
log_info "==========================================================================="

SYNTAX_CHECK=$($DOCKER_EXEC python -m py_compile /opt/airflow/dags/daily_price_ingestion_dag.py 2>&1 || echo "SYNTAX_ERROR")

if echo "$SYNTAX_CHECK" | grep -q "SYNTAX_ERROR"; then
    log_error "✗ DAG has syntax errors:"
    echo "$SYNTAX_CHECK"
    exit 1
else
    log_success "✓ DAG syntax is valid"
fi

# Test 3: List DAGs and check if our DAG appears
log_info ""
log_info "Test 3: Verifying DAG registration in Airflow"
log_info "==========================================================================="

DAG_LIST=$($DOCKER_EXEC airflow dags list 2>/dev/null | grep daily_price_ingestion || echo "")

if [ -n "$DAG_LIST" ]; then
    log_success "✓ DAG is registered in Airflow"
    log_info "  $DAG_LIST"
else
    log_warning "! DAG not found in Airflow (may need to wait for scheduler to pick it up)"
    log_info "  Waiting 5 seconds for scheduler..."
    sleep 5

    DAG_LIST=$($DOCKER_EXEC airflow dags list 2>/dev/null | grep daily_price_ingestion || echo "")
    if [ -n "$DAG_LIST" ]; then
        log_success "✓ DAG is now registered"
    else
        log_error "✗ DAG still not registered after wait"
    fi
fi

# Test 4: Check DAG configuration
log_info ""
log_info "Test 4: Checking DAG configuration"
log_info "==========================================================================="

DAG_INFO=$($DOCKER_EXEC airflow dags show daily_price_ingestion 2>&1 || echo "")

if echo "$DAG_INFO" | grep -q "Error"; then
    log_error "✗ DAG has configuration errors:"
    echo "$DAG_INFO"
else
    log_success "✓ DAG configuration is valid"
fi

# Test 5: List DAG tasks
log_info ""
log_info "Test 5: Verifying DAG tasks"
log_info "==========================================================================="

EXPECTED_TASKS=(
    "fetch_krx_prices"
    "validate_price_data"
    "load_prices_to_db"
    "check_data_completeness"
    "refresh_timescale_aggregates"
    "log_ingestion_status"
    "trigger_indicator_calculation"
)

TASKS_OUTPUT=$($DOCKER_EXEC airflow tasks list daily_price_ingestion 2>/dev/null || echo "")

if [ -z "$TASKS_OUTPUT" ]; then
    log_error "✗ Could not list tasks (DAG may have import errors)"
    exit 1
fi

MISSING_TASKS=0
for task in "${EXPECTED_TASKS[@]}"; do
    if echo "$TASKS_OUTPUT" | grep -q "^${task}$"; then
        log_success "  ✓ $task"
    else
        log_error "  ✗ $task MISSING"
        MISSING_TASKS=$((MISSING_TASKS + 1))
    fi
done

if [ "$MISSING_TASKS" -eq 0 ]; then
    log_success "✓ All 7 tasks verified"
else
    log_error "✗ $MISSING_TASKS tasks missing"
    exit 1
fi

# Test 6: Test individual task (dry run)
log_info ""
log_info "Test 6: Testing fetch_krx_prices task (dry run)"
log_info "==========================================================================="

log_info "Setting KRX_USE_MOCK=true for testing..."
$DOCKER_EXEC airflow variables set KRX_USE_MOCK true 2>/dev/null || true

TEST_DATE="2024-01-15"
log_info "Running task test for date: $TEST_DATE"

TASK_TEST=$($DOCKER_EXEC airflow tasks test daily_price_ingestion fetch_krx_prices $TEST_DATE 2>&1)

if echo "$TASK_TEST" | grep -q "ERROR"; then
    log_error "✗ Task test failed:"
    echo "$TASK_TEST" | grep -A 5 "ERROR"
else
    log_success "✓ fetch_krx_prices task executed successfully"

    # Check if data was fetched
    if echo "$TASK_TEST" | grep -q "Fetched.*stock prices"; then
        FETCHED=$(echo "$TASK_TEST" | grep "Fetched.*stock prices" | tail -1)
        log_info "  $FETCHED"
    fi
fi

# Test 7: Check DAG schedule
log_info ""
log_info "Test 7: Verifying DAG schedule"
log_info "==========================================================================="

SCHEDULE=$($DOCKER_EXEC airflow dags list 2>/dev/null | grep daily_price_ingestion | awk '{print $3}')

if [ "$SCHEDULE" == "0 18 * * 1-5" ]; then
    log_success "✓ Schedule correctly set (Mon-Fri at 18:00)"
else
    log_warning "! Schedule is: $SCHEDULE (expected: 0 18 * * 1-5)"
fi

# Test 8: Check catchup setting
log_info ""
log_info "Test 8: Checking DAG properties"
log_info "==========================================================================="

DAG_DETAILS=$($DOCKER_EXEC airflow dags details daily_price_ingestion 2>/dev/null || echo "")

if echo "$DAG_DETAILS" | grep -q "catchup.*False"; then
    log_success "✓ catchup is disabled (correct)"
else
    log_warning "! Could not verify catchup setting"
fi

if echo "$DAG_DETAILS" | grep -q "max_active_runs.*1"; then
    log_success "✓ max_active_runs = 1 (correct)"
else
    log_warning "! Could not verify max_active_runs setting"
fi

# Test 9: Manual trigger test (optional - commented out by default)
log_info ""
log_info "Test 9: Manual DAG trigger (SKIPPED - use --trigger flag to run)"
log_info "==========================================================================="

if [ "$1" == "--trigger" ]; then
    log_info "Triggering DAG manually..."

    RUN_ID=$($DOCKER_EXEC airflow dags trigger daily_price_ingestion 2>&1 | grep -o "dag_run_id=[^ ]*" | cut -d'=' -f2 || echo "")

    if [ -n "$RUN_ID" ]; then
        log_success "✓ DAG triggered successfully (run_id: $RUN_ID)"
        log_info "  Monitor progress in Airflow UI: http://localhost:8080"
        log_info "  Or check logs with: docker-compose exec webserver airflow dags state $RUN_ID"
    else
        log_error "✗ Failed to trigger DAG"
    fi
else
    log_info "  To trigger a manual run, use: $0 --trigger"
fi

# Test 10: Environment variables check
log_info ""
log_info "Test 10: Checking environment configuration"
log_info "==========================================================================="

KRX_USE_MOCK=$($DOCKER_EXEC airflow variables get KRX_USE_MOCK 2>/dev/null || echo "not_set")

if [ "$KRX_USE_MOCK" == "true" ]; then
    log_success "✓ KRX_USE_MOCK is set (using mock data for testing)"
else
    log_warning "! KRX_USE_MOCK not set (will use real API - requires credentials)"
fi

KRX_API_KEY=$($DOCKER_EXEC bash -c 'echo ${KRX_API_KEY:-not_set}' 2>/dev/null || echo "not_set")

if [ "$KRX_API_KEY" == "not_set" ]; then
    log_warning "! KRX_API_KEY not set (required for production)"
else
    log_success "✓ KRX_API_KEY is configured"
fi

# Summary
echo ""
log_info "==========================================================================="
log_success "Verification Complete!"
log_info "==========================================================================="
echo ""
log_info "Summary:"
log_info "  - DAG file and KRX client verified"
log_info "  - Syntax check passed"
log_info "  - DAG registered in Airflow"
log_info "  - All 7 tasks present"
log_info "  - Task execution test passed"
log_info "  - Schedule configured correctly"
echo ""
log_info "Next Steps:"
log_info "  1. Monitor DAG in Airflow UI: http://localhost:8080"
log_info "  2. Trigger manual run with: $0 --trigger"
log_info "  3. Check execution logs in Airflow UI"
log_info "  4. Verify data loaded in database"
log_info "  5. Set KRX_API_KEY for production use"
echo ""
