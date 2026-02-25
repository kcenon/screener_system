#!/usr/bin/env bash
# ============================================================================
# Environment Variable Validation Script
# ============================================================================
# Validates that all required environment variables are set before starting
# the application. Run this before `docker compose up`.
#
# Usage:
#   ./scripts/check-env.sh          # Check all required vars
#   ./scripts/check-env.sh --full   # Include optional service vars (Airflow, Grafana)
# ============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

check_required() {
    local var_name="$1"
    local description="$2"
    local value="${!var_name:-}"

    if [ -z "$value" ]; then
        echo -e "  ${RED}MISSING${NC}  $var_name - $description"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "  ${GREEN}OK${NC}      $var_name"
    fi
}

check_not_default() {
    local var_name="$1"
    local bad_default="$2"
    local description="$3"
    local value="${!var_name:-}"

    if [ -z "$value" ]; then
        echo -e "  ${RED}MISSING${NC}  $var_name - $description"
        ERRORS=$((ERRORS + 1))
    elif [ "$value" = "$bad_default" ]; then
        echo -e "  ${YELLOW}WARNING${NC}  $var_name is set to insecure default '$bad_default'"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "  ${GREEN}OK${NC}      $var_name"
    fi
}

check_optional() {
    local var_name="$1"
    local description="$2"
    local value="${!var_name:-}"

    if [ -z "$value" ]; then
        echo -e "  ${YELLOW}UNSET${NC}   $var_name - $description (optional)"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "  ${GREEN}OK${NC}      $var_name"
    fi
}

# Load .env file if it exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo -e "${GREEN}Loaded .env file${NC}\n"
else
    echo -e "${YELLOW}No .env file found. Checking environment variables only.${NC}\n"
fi

# ============================================================================
# Core Services (always required)
# ============================================================================

echo "=== Core Secrets ==="
check_required "DB_PASSWORD" "PostgreSQL database password"
check_required "REDIS_PASSWORD" "Redis cache password"
check_required "SECRET_KEY" "JWT signing key (generate with: openssl rand -hex 32)"

echo ""
echo "=== Database Configuration ==="
check_optional "DB_NAME" "Database name (default: screener_db)"
check_optional "DB_USER" "Database user (default: screener_user)"
check_optional "DATABASE_URL" "Full database connection string"

echo ""
echo "=== Application Settings ==="
check_optional "ENVIRONMENT" "Runtime environment (default: development)"
check_optional "DEBUG" "Debug mode (default: false)"

# ============================================================================
# Optional Services (--full flag)
# ============================================================================

if [ "${1:-}" = "--full" ]; then
    echo ""
    echo "=== Airflow (Data Pipeline) ==="
    check_required "AIRFLOW_FERNET_KEY" "Encryption key (generate with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\")"
    check_required "AIRFLOW_SECRET_KEY" "Airflow webserver secret key"
    check_not_default "AIRFLOW_PASSWORD" "admin" "Airflow admin password"

    echo ""
    echo "=== Grafana (Monitoring) ==="
    check_not_default "GRAFANA_PASSWORD" "admin" "Grafana admin password"

    echo ""
    echo "=== External APIs ==="
    check_optional "KRX_API_KEY" "Korea Exchange API key"
    check_optional "FGUIDE_API_KEY" "F&Guide financial data API key"

    echo ""
    echo "=== Payment (Stripe) ==="
    check_optional "STRIPE_SECRET_KEY" "Stripe secret API key"
    check_optional "STRIPE_WEBHOOK_SECRET" "Stripe webhook signature secret"
fi

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "============================================"
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}FAILED: $ERRORS required variable(s) missing${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}WARNINGS: $WARNINGS issue(s) found${NC}"
    fi
    echo ""
    echo "To fix:"
    echo "  1. Copy .env.example to .env:  cp .env.example .env"
    echo "  2. Edit .env with your actual secret values"
    echo "  3. Re-run this script to verify"
    echo "============================================"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}PASSED with $WARNINGS warning(s)${NC}"
    echo "============================================"
    exit 0
else
    echo -e "${GREEN}PASSED: All required variables are set${NC}"
    echo "============================================"
    exit 0
fi
