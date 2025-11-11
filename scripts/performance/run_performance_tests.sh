#!/bin/bash

# Performance Testing Script for Stock Screening Platform
# Tests BE-004, BE-005, BE-006 performance requirements

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
RESULTS_DIR="$PROJECT_ROOT/results/performance"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="$RESULTS_DIR/performance_results_$TIMESTAMP.txt"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Performance thresholds (from SRS)
SIMPLE_SCREENING_P95_MS=200
COMPLEX_SCREENING_P99_MS=500
CACHE_HIT_AVG_MS=50
WEBSOCKET_CONNECT_MS=100
WEBSOCKET_MSG_AVG_MS=50

echo "========================================="
echo "Stock Screening Platform - Performance Testing"
echo "========================================="
echo "Timestamp: $TIMESTAMP"
echo "Results will be saved to: $RESULTS_FILE"
echo ""

# Create results directory
mkdir -p "$RESULTS_DIR"

# Initialize results file
cat > "$RESULTS_FILE" << EOF
# Performance Testing Results
Date: $(date)
Environment: Docker Compose (Local)

## System Information
Backend URL: http://localhost:8000
Redis: localhost:6379
PostgreSQL: localhost:5432

EOF

# Function to check if service is running
check_service() {
    local service_name=$1
    local url=$2

    echo -n "Checking $service_name... "
    if curl -sf "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not responding${NC}"
        return 1
    fi
}

# Function to run wrk test
run_wrk_test() {
    local name=$1
    local duration=$2
    local threads=$3
    local connections=$4
    local url=$5
    local script=$6

    echo ""
    echo -e "${BLUE}Running: $name${NC}"
    echo "  Duration: ${duration}s, Threads: $threads, Connections: $connections"

    if [ -n "$script" ]; then
        wrk -t$threads -c$connections -d${duration}s --latency -s "$script" "$url"
    else
        wrk -t$threads -c$connections -d${duration}s --latency "$url"
    fi
}

# Check prerequisites
echo "========================================="
echo "Checking Prerequisites"
echo "========================================="
echo ""

if ! command -v wrk &> /dev/null; then
    echo -e "${RED}✗ wrk not installed${NC}"
    echo "Install with: brew install wrk"
    exit 1
fi
echo -e "${GREEN}✓ wrk installed${NC}"

if ! command -v curl &> /dev/null; then
    echo -e "${RED}✗ curl not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ curl installed${NC}"

# Check services
echo ""
check_service "Backend API" "http://localhost:8000/health" || exit 1
check_service "Redis" "redis://localhost:6379" || echo -e "${YELLOW}⚠ Redis check skipped${NC}"

echo ""
echo "========================================="
echo "Test 1: Health Check Baseline"
echo "========================================="
echo "" | tee -a "$RESULTS_FILE"

echo "## Test 1: Health Check Baseline" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

run_wrk_test "Health Check" 10 2 50 "http://localhost:8000/health" | tee -a "$RESULTS_FILE"

echo ""
echo "========================================="
echo "Test 2: Simple Screening Query"
echo "========================================="
echo "Target: < ${SIMPLE_SCREENING_P95_MS}ms (p95)"
echo "" | tee -a "$RESULTS_FILE"

echo "## Test 2: Simple Screening Query (No Filters)" >> "$RESULTS_FILE"
echo "**Target**: < ${SIMPLE_SCREENING_P95_MS}ms (p95)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

run_wrk_test "Simple Screening" 30 4 100 "http://localhost:8000/v1/screen" \
    "$SCRIPT_DIR/wrk_simple_screening.lua" | tee -a "$RESULTS_FILE"

echo ""
echo "========================================="
echo "Test 3: Complex Screening Query"
echo "========================================="
echo "Target: < ${COMPLEX_SCREENING_P99_MS}ms (p99)"
echo "" | tee -a "$RESULTS_FILE"

echo "## Test 3: Complex Screening Query (10+ Filters)" >> "$RESULTS_FILE"
echo "**Target**: < ${COMPLEX_SCREENING_P99_MS}ms (p99)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

run_wrk_test "Complex Screening" 30 4 100 "http://localhost:8000/v1/screen" \
    "$SCRIPT_DIR/wrk_complex_screening.lua" | tee -a "$RESULTS_FILE"

echo ""
echo "========================================="
echo "Test 4: Cache Performance"
echo "========================================="
echo "Testing first request (cache miss) vs subsequent requests (cache hit)"
echo "Target: < ${CACHE_HIT_AVG_MS}ms (cache hit)"
echo "" | tee -a "$RESULTS_FILE"

echo "## Test 4: Cache Performance" >> "$RESULTS_FILE"
echo "**Target**: < ${CACHE_HIT_AVG_MS}ms (cache hit)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# First request (cache miss)
echo "First request (cache miss):" >> "$RESULTS_FILE"
time_output=$(time ( curl -s -X POST http://localhost:8000/v1/screen \
    -H "Content-Type: application/json" \
    -d '{}' > /dev/null ) 2>&1)
echo "$time_output" >> "$RESULTS_FILE"

# Wait a moment
sleep 1

# Second request (cache hit)
echo "" >> "$RESULTS_FILE"
echo "Second request (cache hit):" >> "$RESULTS_FILE"
time_output=$(time ( curl -s -X POST http://localhost:8000/v1/screen \
    -H "Content-Type: application/json" \
    -d '{}' > /dev/null ) 2>&1)
echo "$time_output" >> "$RESULTS_FILE"

echo ""
echo "========================================="
echo "Test 5: Concurrent Requests Stress Test"
echo "========================================="
echo "100 concurrent requests for 60 seconds"
echo "" | tee -a "$RESULTS_FILE"

echo "## Test 5: Concurrent Requests (100 concurrent)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

run_wrk_test "Stress Test" 60 4 100 "http://localhost:8000/v1/screen" \
    "$SCRIPT_DIR/wrk_simple_screening.lua" | tee -a "$RESULTS_FILE"

echo ""
echo "========================================="
echo "Test 6: Redis Performance Check"
echo "========================================="
echo "" | tee -a "$RESULTS_FILE"

echo "## Test 6: Redis Performance" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

if docker ps | grep -q screener_redis; then
    echo "Redis Stats:" >> "$RESULTS_FILE"
    docker exec screener_redis redis-cli INFO stats | tee -a "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"

    echo "Redis Memory:" >> "$RESULTS_FILE"
    docker exec screener_redis redis-cli INFO memory | grep -E "used_memory_human|used_memory_peak_human" | tee -a "$RESULTS_FILE"
else
    echo -e "${YELLOW}⚠ Redis container not found${NC}"
    echo "Redis container not found" >> "$RESULTS_FILE"
fi

echo ""
echo "========================================="
echo "Test 7: Database Connection Pool"
echo "========================================="
echo "" | tee -a "$RESULTS_FILE"

echo "## Test 7: Database Connection Pool" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

if docker ps | grep -q screener_postgres; then
    echo "Active connections:" >> "$RESULTS_FILE"
    docker exec screener_postgres psql -U screener_user -d screener_db \
        -c "SELECT count(*) as active_connections FROM pg_stat_activity WHERE datname = 'screener_db';" \
        | tee -a "$RESULTS_FILE"
else
    echo -e "${YELLOW}⚠ PostgreSQL container not found${NC}"
    echo "PostgreSQL container not found" >> "$RESULTS_FILE"
fi

echo ""
echo "========================================="
echo "Performance Testing Complete"
echo "========================================="
echo ""
echo -e "${GREEN}Results saved to: $RESULTS_FILE${NC}"
echo ""
echo "To view results:"
echo "  cat $RESULTS_FILE"
echo ""
echo "Next steps:"
echo "  1. Review results against SRS requirements"
echo "  2. Identify bottlenecks if targets not met"
echo "  3. Document baseline performance"
echo "  4. Add performance regression tests to CI/CD"
echo ""
