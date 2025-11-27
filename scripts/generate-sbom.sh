#!/bin/bash
# Master script for generating Software Bill of Materials (SBOM)
# Generates CycloneDX format SBOMs for all project components

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SBOM_SCRIPT_DIR="$SCRIPT_DIR/sbom"
OUTPUT_DIR="${OUTPUT_DIR:-$PROJECT_ROOT/sbom}"

# Parse arguments
SKIP_FRONTEND=false
SKIP_BACKEND=false
SKIP_PIPELINE=false
SKIP_MERGE=false
VERBOSE=false

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Generate Software Bill of Materials (SBOM) for all components"
    echo ""
    echo "Options:"
    echo "  --skip-frontend    Skip frontend SBOM generation"
    echo "  --skip-backend     Skip backend SBOM generation"
    echo "  --skip-pipeline    Skip data pipeline SBOM generation"
    echo "  --skip-merge       Skip SBOM merge step"
    echo "  --output-dir DIR   Specify output directory (default: ./sbom)"
    echo "  -v, --verbose      Enable verbose output"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Generate all SBOMs"
    echo "  $0 --skip-pipeline           # Skip data pipeline"
    echo "  $0 --output-dir ./dist/sbom  # Custom output directory"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        --skip-backend)
            SKIP_BACKEND=true
            shift
            ;;
        --skip-pipeline)
            SKIP_PIPELINE=true
            shift
            ;;
        --skip-merge)
            SKIP_MERGE=true
            shift
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          SBOM Generator - Stock Screening Platform           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Project Root: $PROJECT_ROOT"
echo "Output Directory: $OUTPUT_DIR"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"
export OUTPUT_DIR

# Track results
RESULTS=()
FAILED=false

# Generate Frontend SBOM
if [ "$SKIP_FRONTEND" = false ]; then
    echo "┌────────────────────────────────────────────────────────────┐"
    echo "│ [1/4] Frontend SBOM (npm)                                  │"
    echo "└────────────────────────────────────────────────────────────┘"
    if bash "$SBOM_SCRIPT_DIR/generate-frontend.sh"; then
        RESULTS+=("✅ Frontend: SUCCESS")
    else
        RESULTS+=("❌ Frontend: FAILED")
        FAILED=true
    fi
    echo ""
else
    RESULTS+=("⏭️  Frontend: SKIPPED")
fi

# Generate Backend SBOM
if [ "$SKIP_BACKEND" = false ]; then
    echo "┌────────────────────────────────────────────────────────────┐"
    echo "│ [2/4] Backend SBOM (Python)                                │"
    echo "└────────────────────────────────────────────────────────────┘"
    if bash "$SBOM_SCRIPT_DIR/generate-backend.sh"; then
        RESULTS+=("✅ Backend: SUCCESS")
    else
        RESULTS+=("❌ Backend: FAILED")
        FAILED=true
    fi
    echo ""
else
    RESULTS+=("⏭️  Backend: SKIPPED")
fi

# Generate Data Pipeline SBOM
if [ "$SKIP_PIPELINE" = false ]; then
    echo "┌────────────────────────────────────────────────────────────┐"
    echo "│ [3/4] Data Pipeline SBOM (Python/Airflow)                  │"
    echo "└────────────────────────────────────────────────────────────┘"
    if bash "$SBOM_SCRIPT_DIR/generate-pipeline.sh"; then
        RESULTS+=("✅ Data Pipeline: SUCCESS")
    else
        RESULTS+=("❌ Data Pipeline: FAILED")
        FAILED=true
    fi
    echo ""
else
    RESULTS+=("⏭️  Data Pipeline: SKIPPED")
fi

# Merge SBOMs
if [ "$SKIP_MERGE" = false ]; then
    echo "┌────────────────────────────────────────────────────────────┐"
    echo "│ [4/4] Merging SBOMs                                        │"
    echo "└────────────────────────────────────────────────────────────┘"
    if bash "$SBOM_SCRIPT_DIR/merge-sbom.sh"; then
        RESULTS+=("✅ Merge: SUCCESS")
    else
        RESULTS+=("❌ Merge: FAILED")
        FAILED=true
    fi
    echo ""
else
    RESULTS+=("⏭️  Merge: SKIPPED")
fi

# Print summary
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                       SBOM Summary                           ║"
echo "╠══════════════════════════════════════════════════════════════╣"
for result in "${RESULTS[@]}"; do
    printf "║ %-60s ║\n" "$result"
done
echo "╠══════════════════════════════════════════════════════════════╣"

# List generated files
echo "║ Generated Files:                                             ║"
for f in "$OUTPUT_DIR"/sbom-*.json; do
    if [ -f "$f" ]; then
        SIZE=$(ls -lh "$f" | awk '{print $5}')
        BASENAME=$(basename "$f")
        printf "║   %-50s %6s ║\n" "$BASENAME" "$SIZE"
    fi
done

echo "╚══════════════════════════════════════════════════════════════╝"

if [ "$FAILED" = true ]; then
    echo ""
    echo "⚠️  Some SBOM generations failed. Check the logs above."
    exit 1
else
    echo ""
    echo "🎉 All SBOMs generated successfully!"
    exit 0
fi
