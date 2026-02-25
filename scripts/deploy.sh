#!/usr/bin/env bash
# ============================================================================
# Deployment Script for Stock Screening Platform
# ============================================================================
# Runs on the target server via SSH from the CD pipeline.
# Handles image pulling, container deployment, and rollback.
#
# Usage:
#   ./scripts/deploy.sh --environment staging --image-tag <sha> [options]
#   ./scripts/deploy.sh --environment staging --rollback
#
# Required options:
#   --environment       staging or production
#   --image-tag         Docker image tag (commit SHA)
#   --registry          Container registry (ghcr.io)
#   --backend-image     Full backend image name
#   --frontend-image    Full frontend image name
#   --github-token      GitHub token for GHCR auth
#   --github-actor      GitHub username for GHCR auth
#
# Rollback:
#   --rollback          Roll back to the previous deployment
# ============================================================================

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

DEPLOY_DIR="$HOME/screener"
BACKUP_DIR="$DEPLOY_DIR/.deploy-backups"
STATE_FILE="$DEPLOY_DIR/.deploy-state"
LOG_FILE="$DEPLOY_DIR/.deploy.log"
MAX_BACKUPS=5

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ============================================================================
# Argument Parsing
# ============================================================================

ENVIRONMENT=""
IMAGE_TAG=""
REGISTRY=""
BACKEND_IMAGE=""
FRONTEND_IMAGE=""
GITHUB_TOKEN=""
GITHUB_ACTOR=""
ROLLBACK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --environment)    ENVIRONMENT="$2"; shift 2 ;;
        --image-tag)      IMAGE_TAG="$2"; shift 2 ;;
        --registry)       REGISTRY="$2"; shift 2 ;;
        --backend-image)  BACKEND_IMAGE="$2"; shift 2 ;;
        --frontend-image) FRONTEND_IMAGE="$2"; shift 2 ;;
        --github-token)   GITHUB_TOKEN="$2"; shift 2 ;;
        --github-actor)   GITHUB_ACTOR="$2"; shift 2 ;;
        --rollback)       ROLLBACK=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ============================================================================
# Helpers
# ============================================================================

log() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] $1" | tee -a "$LOG_FILE"
}

die() {
    log "${RED}ERROR: $1${NC}"
    exit 1
}

get_compose_file() {
    case "$ENVIRONMENT" in
        staging)    echo "$DEPLOY_DIR/docker-compose.staging.yml" ;;
        production) echo "$DEPLOY_DIR/docker-compose.prod.yml" ;;
        *) die "Unknown environment: $ENVIRONMENT" ;;
    esac
}

# ============================================================================
# Validation
# ============================================================================

validate_args() {
    [ -z "$ENVIRONMENT" ] && die "--environment is required"

    if [ "$ROLLBACK" = true ]; then
        return 0
    fi

    [ -z "$IMAGE_TAG" ] && die "--image-tag is required"
    [ -z "$REGISTRY" ] && die "--registry is required"
    [ -z "$BACKEND_IMAGE" ] && die "--backend-image is required"
    [ -z "$FRONTEND_IMAGE" ] && die "--frontend-image is required"
    [ -z "$GITHUB_TOKEN" ] && die "--github-token is required"
    [ -z "$GITHUB_ACTOR" ] && die "--github-actor is required"

    local compose_file
    compose_file=$(get_compose_file)
    [ ! -f "$compose_file" ] && die "Compose file not found: $compose_file"
}

# ============================================================================
# Backup Current State
# ============================================================================

backup_current_state() {
    mkdir -p "$BACKUP_DIR"

    local compose_file
    compose_file=$(get_compose_file)

    # Save currently running image tags
    local backup_file="$BACKUP_DIR/$(date '+%Y%m%d_%H%M%S')_${ENVIRONMENT}.env"

    log "Backing up current deployment state..."

    # Get current image IDs from running containers
    local current_backend_image=""
    local current_frontend_image=""

    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "screener_backend"; then
        current_backend_image=$(docker inspect screener_backend --format='{{.Config.Image}}' 2>/dev/null || echo "")
    fi
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "screener_frontend"; then
        current_frontend_image=$(docker inspect screener_frontend --format='{{.Config.Image}}' 2>/dev/null || echo "")
    fi

    cat > "$backup_file" <<EOF
ENVIRONMENT=$ENVIRONMENT
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
BACKEND_IMAGE=$current_backend_image
FRONTEND_IMAGE=$current_frontend_image
COMPOSE_FILE=$compose_file
EOF

    # Update state file with latest backup reference
    echo "$backup_file" > "$STATE_FILE"

    log "${GREEN}Backup saved: $backup_file${NC}"

    # Cleanup old backups (keep MAX_BACKUPS most recent)
    local backup_count
    backup_count=$(ls -1 "$BACKUP_DIR"/*_${ENVIRONMENT}.env 2>/dev/null | wc -l)
    if [ "$backup_count" -gt "$MAX_BACKUPS" ]; then
        ls -1t "$BACKUP_DIR"/*_${ENVIRONMENT}.env | tail -n +"$((MAX_BACKUPS + 1))" | xargs rm -f
        log "Cleaned up old backups (kept $MAX_BACKUPS most recent)"
    fi
}

# ============================================================================
# Rollback
# ============================================================================

do_rollback() {
    log "${YELLOW}Starting rollback for $ENVIRONMENT...${NC}"

    if [ ! -f "$STATE_FILE" ]; then
        die "No deployment state found. Cannot rollback."
    fi

    local backup_file
    backup_file=$(cat "$STATE_FILE")

    if [ ! -f "$backup_file" ]; then
        die "Backup file not found: $backup_file"
    fi

    # shellcheck source=/dev/null
    source "$backup_file"

    local compose_file
    compose_file=$(get_compose_file)

    if [ -z "$BACKEND_IMAGE" ] || [ -z "$FRONTEND_IMAGE" ]; then
        die "No previous image references found in backup"
    fi

    log "Rolling back to:"
    log "  Backend:  $BACKEND_IMAGE"
    log "  Frontend: $FRONTEND_IMAGE"

    # Set images for docker compose
    export BACKEND_IMAGE
    export FRONTEND_IMAGE

    docker compose -f "$compose_file" up -d --no-build --remove-orphans 2>&1 | tee -a "$LOG_FILE"

    log "${GREEN}Rollback completed${NC}"
}

# ============================================================================
# Deploy
# ============================================================================

do_deploy() {
    local compose_file
    compose_file=$(get_compose_file)

    log "============================================"
    log "Deploying to $ENVIRONMENT"
    log "  Image tag: $IMAGE_TAG"
    log "  Compose:   $compose_file"
    log "============================================"

    # Step 1: Authenticate with GHCR
    log "Authenticating with container registry..."
    echo "$GITHUB_TOKEN" | docker login "$REGISTRY" -u "$GITHUB_ACTOR" --password-stdin 2>&1 | tee -a "$LOG_FILE"

    # Step 2: Pull new images
    log "Pulling images with tag: $IMAGE_TAG..."
    docker pull "${BACKEND_IMAGE}:${IMAGE_TAG}" 2>&1 | tee -a "$LOG_FILE"
    docker pull "${FRONTEND_IMAGE}:${IMAGE_TAG}" 2>&1 | tee -a "$LOG_FILE"

    # Also tag as environment-specific for compose reference
    docker tag "${BACKEND_IMAGE}:${IMAGE_TAG}" "${BACKEND_IMAGE}:${ENVIRONMENT}"
    docker tag "${FRONTEND_IMAGE}:${IMAGE_TAG}" "${FRONTEND_IMAGE}:${ENVIRONMENT}"

    log "${GREEN}Images pulled successfully${NC}"

    # Step 3: Backup current state
    backup_current_state

    # Step 4: Deploy with Docker Compose
    log "Starting deployment..."
    export BACKEND_IMAGE="${BACKEND_IMAGE}:${IMAGE_TAG}"
    export FRONTEND_IMAGE="${FRONTEND_IMAGE}:${IMAGE_TAG}"

    docker compose -f "$compose_file" up -d --no-build --remove-orphans 2>&1 | tee -a "$LOG_FILE"

    # Step 5: Wait for containers to be running
    log "Waiting for containers to start..."
    sleep 5

    # Check container status
    local failed=false
    for service in backend postgres redis; do
        local container_name="screener_${service}"
        if docker ps --format '{{.Names}}' | grep -q "$container_name"; then
            local status
            status=$(docker inspect "$container_name" --format='{{.State.Status}}' 2>/dev/null || echo "unknown")
            log "  $container_name: $status"
            if [ "$status" != "running" ]; then
                failed=true
            fi
        else
            log "${YELLOW}  $container_name: not found (may be expected)${NC}"
        fi
    done

    if [ "$failed" = true ]; then
        die "Some containers failed to start"
    fi

    log "${GREEN}Deployment to $ENVIRONMENT completed successfully${NC}"
    log "============================================"
}

# ============================================================================
# Main
# ============================================================================

mkdir -p "$DEPLOY_DIR"
touch "$LOG_FILE"

validate_args

if [ "$ROLLBACK" = true ]; then
    do_rollback
else
    do_deploy
fi
