#!/bin/bash
# ============================================================================
# Database Migration Execution Script
# Description: Run all SQL migrations in order
# Author: Database Team
# Created: 2025-11-09
# ============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATIONS_DIR="${SCRIPT_DIR}/../migrations"
LOG_FILE="${SCRIPT_DIR}/migration_$(date +%Y%m%d_%H%M%S).log"

# PostgreSQL connection (from environment or defaults)
PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGDATABASE="${PGDATABASE:-screener}"
PGUSER="${PGUSER:-postgres}"
PGPASSWORD="${PGPASSWORD:-postgres}"

# Export for psql
export PGHOST PGPORT PGDATABASE PGUSER PGPASSWORD

# Migration files in execution order
MIGRATION_FILES=(
    "00_extensions.sql"
    "01_create_tables.sql"
    "02_timescaledb_setup.sql"
    "03_indexes.sql"
    "04_functions_triggers.sql"
    "05_views.sql"
)

# ============================================================================
# FUNCTIONS
# ============================================================================

log() {
    local level="$1"
    shift
    local message="$@"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

check_postgres_connection() {
    log "INFO" "Checking PostgreSQL connection..."
    if ! psql -c "SELECT version();" &>/dev/null; then
        log "ERROR" "Cannot connect to PostgreSQL"
        log "ERROR" "  Host: $PGHOST"
        log "ERROR" "  Port: $PGPORT"
        log "ERROR" "  Database: $PGDATABASE"
        log "ERROR" "  User: $PGUSER"
        return 1
    fi
    log "INFO" "PostgreSQL connection successful"
    return 0
}

run_migration() {
    local migration_file="$1"
    local file_path="${MIGRATIONS_DIR}/${migration_file}"

    if [ ! -f "$file_path" ]; then
        log "ERROR" "Migration file not found: $migration_file"
        return 1
    fi

    log "INFO" "Running migration: $migration_file"

    if psql -f "$file_path" >> "$LOG_FILE" 2>&1; then
        log "INFO" "✓ Success: $migration_file"
        return 0
    else
        log "ERROR" "✗ Failed: $migration_file"
        log "ERROR" "Check log file for details: $LOG_FILE"
        return 1
    fi
}

verify_tables() {
    log "INFO" "Verifying tables..."

    local table_count
    table_count=$(psql -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';" 2>/dev/null || echo "0")

    log "INFO" "Total tables created: $table_count"

    if [ "$table_count" -ge 14 ]; then
        log "INFO" "✓ Expected table count verified (minimum 14 tables)"
        return 0
    else
        log "WARN" "Expected at least 14 tables, found: $table_count"
        return 1
    fi
}

verify_hypertable() {
    log "INFO" "Verifying TimescaleDB hypertables..."

    local hypertable_count
    hypertable_count=$(psql -t -c "SELECT COUNT(*) FROM timescaledb_information.hypertables;" 2>/dev/null || echo "0")

    if [ "$hypertable_count" -ge 1 ]; then
        log "INFO" "✓ TimescaleDB hypertables verified: $hypertable_count"
        return 0
    else
        log "WARN" "No hypertables found"
        return 1
    fi
}

list_tables() {
    log "INFO" "Listing all tables:"
    psql -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;" 2>&1 | tee -a "$LOG_FILE"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    log "INFO" "========================================"
    log "INFO" "Database Migration Script"
    log "INFO" "========================================"
    log "INFO" "Log file: $LOG_FILE"
    log "INFO" "Migrations directory: $MIGRATIONS_DIR"
    echo

    # Check connection
    if ! check_postgres_connection; then
        log "ERROR" "Migration aborted: Cannot connect to database"
        exit 1
    fi
    echo

    # Run migrations
    log "INFO" "Starting migrations..."
    for migration in "${MIGRATION_FILES[@]}"; do
        if ! run_migration "$migration"; then
            log "ERROR" "Migration failed: $migration"
            log "ERROR" "All subsequent migrations skipped"
            exit 1
        fi
    done
    echo

    # Verify results
    log "INFO" "Verifying migration results..."
    verify_tables
    verify_hypertable
    echo

    # List tables
    list_tables
    echo

    log "INFO" "========================================"
    log "INFO" "Migration completed successfully!"
    log "INFO" "========================================"
    log "INFO" "Full log: $LOG_FILE"
}

# Run main function
main "$@"
