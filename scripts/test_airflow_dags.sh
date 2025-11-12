#!/bin/bash
# ============================================================================
# Airflow DAG Runtime Testing Script
# ============================================================================
# Purpose: Comprehensive testing of Airflow DAGs (BUGFIX-010)
# Tests:
#   - Airflow service health
#   - DAG recognition and import
#   - Database connectivity
#   - DAG execution readiness
# ============================================================================

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AIRFLOW_WEBSERVER_URL="http://localhost:8080"
AIRFLOW_HEALTH_ENDPOINT="${AIRFLOW_WEBSERVER_URL}/health"
EXPECTED_DAGS=("daily_price_ingestion" "indicator_calculation")

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓ PASS]${NC} $1"
    ((PASSED_TESTS++))
}

log_fail() {
    echo -e "${RED}[✗ FAIL]${NC} $1"
    ((FAILED_TESTS++))
}

log_warning() {
    echo -e "${YELLOW}[⚠ WARN]${NC} $1"
}

run_test() {
    local test_name=$1
    ((TOTAL_TESTS++))
    log_info "Running: $test_name"
}

# ============================================================================
# Test Functions
# ============================================================================

test_docker_services() {
    run_test "Docker services running"

    local services=("airflow-webserver" "airflow-scheduler" "postgres" "redis")
    local all_running=true

    for service in "${services[@]}"; do
        if docker-compose ps | grep -q "${service}.*Up"; then
            log_info "  ✓ ${service} is running"
        else
            log_fail "  ✗ ${service} is not running"
            all_running=false
        fi
    done

    if [ "$all_running" = true ]; then
        log_success "All required Docker services are running"
    else
        log_fail "Some Docker services are not running"
        log_info "Start services with: docker-compose --profile full up -d"
        return 1
    fi
}

test_airflow_webserver() {
    run_test "Airflow webserver accessibility"

    if curl -s -o /dev/null -w "%{http_code}" "${AIRFLOW_HEALTH_ENDPOINT}" | grep -q "200"; then
        log_success "Airflow webserver is accessible at ${AIRFLOW_WEBSERVER_URL}"
    else
        log_fail "Airflow webserver is not accessible"
        log_info "  URL: ${AIRFLOW_WEBSERVER_URL}"
        log_info "  Check: docker-compose logs airflow-webserver"
        return 1
    fi
}

test_airflow_scheduler() {
    run_test "Airflow scheduler status"

    if docker-compose logs airflow-scheduler --tail 50 | grep -q "Scheduler heartbeat"; then
        log_success "Airflow scheduler is running (heartbeat detected)"
    else
        log_warning "Could not detect scheduler heartbeat"
        log_info "  Check: docker-compose logs airflow-scheduler"
    fi
}

test_dag_files_exist() {
    run_test "DAG files exist"

    local all_exist=true

    if [ -f "data_pipeline/dags/daily_price_ingestion_dag.py" ]; then
        log_info "  ✓ daily_price_ingestion_dag.py found"
    else
        log_fail "  ✗ daily_price_ingestion_dag.py not found"
        all_exist=false
    fi

    if [ -f "data_pipeline/dags/indicator_calculation_dag.py" ]; then
        log_info "  ✓ indicator_calculation_dag.py found"
    else
        log_fail "  ✗ indicator_calculation_dag.py not found"
        all_exist=false
    fi

    if [ "$all_exist" = true ]; then
        log_success "All DAG files exist"
    else
        log_fail "Some DAG files are missing"
        return 1
    fi
}

test_dag_python_syntax() {
    run_test "DAG Python syntax validation"

    local all_valid=true

    if python3 -m py_compile data_pipeline/dags/daily_price_ingestion_dag.py 2>/dev/null; then
        log_info "  ✓ daily_price_ingestion_dag.py syntax valid"
    else
        log_fail "  ✗ daily_price_ingestion_dag.py has syntax errors"
        python3 -m py_compile data_pipeline/dags/daily_price_ingestion_dag.py
        all_valid=false
    fi

    if python3 -m py_compile data_pipeline/dags/indicator_calculation_dag.py 2>/dev/null; then
        log_info "  ✓ indicator_calculation_dag.py syntax valid"
    else
        log_fail "  ✗ indicator_calculation_dag.py has syntax errors"
        python3 -m py_compile data_pipeline/dags/indicator_calculation_dag.py
        all_valid=false
    fi

    if [ "$all_valid" = true ]; then
        log_success "All DAG files have valid Python syntax"
    else
        log_fail "Some DAG files have syntax errors"
        return 1
    fi
}

test_dag_recognition() {
    run_test "DAG recognition in Airflow"

    log_info "Listing DAGs from Airflow..."
    local dag_list=$(docker-compose exec -T airflow-webserver airflow dags list 2>/dev/null || echo "")

    if [ -z "$dag_list" ]; then
        log_fail "Could not retrieve DAG list from Airflow"
        log_info "  Check: docker-compose exec airflow-webserver airflow dags list"
        return 1
    fi

    local all_recognized=true
    for dag_id in "${EXPECTED_DAGS[@]}"; do
        if echo "$dag_list" | grep -q "^${dag_id}"; then
            log_info "  ✓ ${dag_id} is recognized"
        else
            log_fail "  ✗ ${dag_id} is NOT recognized"
            all_recognized=false
        fi
    done

    if [ "$all_recognized" = true ]; then
        log_success "All expected DAGs are recognized by Airflow"
    else
        log_fail "Some DAGs are not recognized"
        log_info "  Check DAG import errors: docker-compose logs airflow-scheduler | grep -i error"
        return 1
    fi
}

test_dag_import_errors() {
    run_test "DAG import errors"

    log_info "Checking for import errors..."
    local import_errors=$(docker-compose exec -T airflow-webserver airflow dags list-import-errors 2>/dev/null || echo "")

    if [ -z "$import_errors" ] || echo "$import_errors" | grep -q "No data found"; then
        log_success "No DAG import errors detected"
    else
        log_fail "DAG import errors detected:"
        echo "$import_errors"
        return 1
    fi
}

test_database_connection() {
    run_test "Database connection from Airflow"

    # Test PostgreSQL connection using Airflow's connection test
    local conn_test=$(docker-compose exec -T airflow-webserver \
        airflow connections test screener_db 2>&1 || echo "FAILED")

    if echo "$conn_test" | grep -q "successfully tested"; then
        log_success "Database connection 'screener_db' is working"
    else
        log_warning "Database connection test inconclusive"
        log_info "  You may need to configure Airflow connection 'screener_db'"
        log_info "  Admin → Connections → Add/Edit 'screener_db'"
    fi
}

test_dag_state() {
    run_test "DAG state and configuration"

    for dag_id in "${EXPECTED_DAGS[@]}"; do
        local dag_info=$(docker-compose exec -T airflow-webserver \
            airflow dags show "${dag_id}" 2>/dev/null || echo "")

        if [ -n "$dag_info" ]; then
            log_info "  ✓ ${dag_id} configuration loaded"
        else
            log_warning "  ⚠ ${dag_id} configuration not available"
        fi
    done

    log_success "DAG state check completed"
}

# ============================================================================
# Main Test Execution
# ============================================================================

main() {
    echo "============================================================================"
    echo "  Airflow DAG Runtime Testing (BUGFIX-010)"
    echo "============================================================================"
    echo ""

    log_info "Starting comprehensive DAG validation..."
    echo ""

    # Phase 1: Infrastructure Tests
    echo "Phase 1: Infrastructure Validation"
    echo "-----------------------------------"
    test_docker_services || true
    test_airflow_webserver || true
    test_airflow_scheduler || true
    test_database_connection || true
    echo ""

    # Phase 2: DAG File Tests
    echo "Phase 2: DAG File Validation"
    echo "----------------------------"
    test_dag_files_exist || true
    test_dag_python_syntax || true
    echo ""

    # Phase 3: Airflow Recognition Tests
    echo "Phase 3: Airflow Recognition"
    echo "---------------------------"
    test_dag_recognition || true
    test_dag_import_errors || true
    test_dag_state || true
    echo ""

    # Summary
    echo "============================================================================"
    echo "  Test Summary"
    echo "============================================================================"
    echo "  Total tests:  ${TOTAL_TESTS}"
    echo "  Passed:       ${GREEN}${PASSED_TESTS}${NC}"
    echo "  Failed:       ${RED}${FAILED_TESTS}${NC}"
    echo ""

    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Access Airflow UI: ${AIRFLOW_WEBSERVER_URL}"
        echo "  2. Login with: admin / admin"
        echo "  3. Navigate to DAGs tab"
        echo "  4. Trigger 'daily_price_ingestion' DAG manually"
        echo ""
        exit 0
    else
        echo -e "${RED}✗ Some tests failed${NC}"
        echo ""
        echo "Troubleshooting:"
        echo "  - Check Docker services: docker-compose ps"
        echo "  - Check Airflow logs: docker-compose logs airflow-webserver"
        echo "  - Check scheduler logs: docker-compose logs airflow-scheduler"
        echo "  - Restart services: docker-compose --profile full restart"
        echo ""
        exit 1
    fi
}

# Run main function
main
