#!/bin/bash
# =============================================================================
# Airflow Setup Script
# =============================================================================
#
# This script initializes Apache Airflow environment for the Stock Screener.
#
# Usage:
#   ./scripts/setup_airflow.sh [local|docker]
#
# Modes:
#   local  - Set up Airflow in local Python environment
#   docker - Initialize Airflow in Docker containers (default)
#
# Prerequisites:
#   - Docker and Docker Compose (for docker mode)
#   - Python 3.9+ (for local mode)
#   - PostgreSQL running and accessible
#
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default mode
MODE="${1:-docker}"

# =============================================================================
# Helper Functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed"
        return 1
    fi
    return 0
}

# =============================================================================
# Docker Mode Setup
# =============================================================================

setup_docker() {
    log_info "Setting up Airflow in Docker mode..."

    # Check Docker
    if ! check_command docker; then
        log_error "Docker is required for docker mode"
        exit 1
    fi

    if ! check_command docker-compose; then
        log_error "Docker Compose is required for docker mode"
        exit 1
    fi

    # Load environment variables
    if [ -f "$PROJECT_ROOT/.env" ]; then
        log_info "Loading environment variables from .env"
        source "$PROJECT_ROOT/.env"
    else
        log_warning ".env file not found"
        log_warning "Using default values from docker-compose.yml"
    fi

    # Generate Fernet key if not set
    if [ -z "$AIRFLOW_FERNET_KEY" ] || [ "$AIRFLOW_FERNET_KEY" = "your-fernet-key-here-generate-with-python-cryptography-fernet" ]; then
        log_info "Generating Airflow Fernet key..."
        FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
        log_info "Add this to your .env file:"
        echo "AIRFLOW_FERNET_KEY=$FERNET_KEY"
    fi

    # Create airflow_logs volume if it doesn't exist
    log_info "Creating Docker volumes..."
    docker volume create screener_system_airflow_logs 2>/dev/null || true

    # Start Airflow services with 'full' profile
    log_info "Starting Airflow services..."
    cd "$PROJECT_ROOT"
    docker-compose --profile full up -d airflow_webserver airflow_scheduler

    # Wait for webserver to be healthy
    log_info "Waiting for Airflow webserver to be ready..."
    RETRY_COUNT=0
    MAX_RETRIES=30

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if docker-compose exec -T airflow_webserver airflow db check &>/dev/null; then
            log_success "Airflow is ready!"
            break
        fi

        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            log_error "Airflow failed to start after ${MAX_RETRIES} retries"
            log_info "Check logs with: docker-compose logs airflow_webserver"
            exit 1
        fi

        echo -n "."
        sleep 2
    done
    echo ""

    # Set up database connections
    log_info "Setting up database connections..."
    docker-compose exec -T airflow_webserver python /opt/airflow/dags/../config/setup_connections.py

    # Print access information
    log_success "Airflow setup completed!"
    echo ""
    echo "=========================================================================="
    echo "  Airflow Access Information"
    echo "=========================================================================="
    echo "  Web UI:   http://localhost:${AIRFLOW_PORT:-8080}"
    echo "  Username: ${AIRFLOW_USER:-admin}"
    echo "  Password: ${AIRFLOW_PASSWORD:-admin}"
    echo ""
    echo "  Useful commands:"
    echo "    - View logs:        docker-compose logs -f airflow_scheduler"
    echo "    - Stop Airflow:     docker-compose --profile full stop"
    echo "    - Restart Airflow:  docker-compose --profile full restart"
    echo "    - Access shell:     docker-compose exec airflow_webserver bash"
    echo "=========================================================================="
}

# =============================================================================
# Local Mode Setup
# =============================================================================

setup_local() {
    log_info "Setting up Airflow in local mode..."

    # Check Python
    if ! check_command python3; then
        log_error "Python 3 is required"
        exit 1
    fi

    # Check if virtual environment exists
    if [ ! -d "$PROJECT_ROOT/data_pipeline/venv" ]; then
        log_info "Creating Python virtual environment..."
        cd "$PROJECT_ROOT/data_pipeline"
        python3 -m venv venv
    fi

    # Activate virtual environment
    log_info "Activating virtual environment..."
    source "$PROJECT_ROOT/data_pipeline/venv/bin/activate"

    # Install dependencies
    log_info "Installing Airflow and dependencies..."
    pip install --upgrade pip
    pip install -r "$PROJECT_ROOT/data_pipeline/requirements.txt"

    # Set AIRFLOW_HOME
    export AIRFLOW_HOME="$PROJECT_ROOT/data_pipeline"
    log_info "AIRFLOW_HOME set to: $AIRFLOW_HOME"

    # Initialize Airflow database
    if [ ! -f "$AIRFLOW_HOME/airflow.db" ] && [ ! -f "$AIRFLOW_HOME/airflow.cfg" ]; then
        log_info "Initializing Airflow database..."
        airflow db init

        # Create admin user
        log_info "Creating admin user..."
        airflow users create \
            --username admin \
            --firstname Admin \
            --lastname User \
            --role Admin \
            --email admin@example.com \
            --password admin

        log_success "Airflow database initialized"
    else
        log_info "Airflow database already exists, upgrading..."
        airflow db upgrade
    fi

    # Set up connections
    log_info "Setting up database connections..."
    cd "$PROJECT_ROOT/data_pipeline/config"
    python setup_connections.py

    # Print access information
    log_success "Airflow setup completed!"
    echo ""
    echo "=========================================================================="
    echo "  Airflow Setup Complete (Local Mode)"
    echo "=========================================================================="
    echo "  AIRFLOW_HOME: $AIRFLOW_HOME"
    echo ""
    echo "  To start Airflow:"
    echo "    1. Terminal 1: source data_pipeline/venv/bin/activate && airflow webserver"
    echo "    2. Terminal 2: source data_pipeline/venv/bin/activate && airflow scheduler"
    echo ""
    echo "  Web UI:   http://localhost:8080"
    echo "  Username: admin"
    echo "  Password: admin"
    echo "=========================================================================="
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo ""
    log_info "=========================================================================="
    log_info "  Stock Screener - Airflow Setup"
    log_info "=========================================================================="
    log_info "Mode: $MODE"
    echo ""

    case "$MODE" in
        docker)
            setup_docker
            ;;
        local)
            setup_local
            ;;
        *)
            log_error "Invalid mode: $MODE"
            log_info "Usage: $0 [local|docker]"
            exit 1
            ;;
    esac

    echo ""
    log_success "Setup complete! You can now access Airflow."
}

# Run main function
main
