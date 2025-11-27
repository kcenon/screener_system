#!/bin/bash
# Merge multiple SBOMs into a single comprehensive SBOM
# Uses cyclonedx-cli for merging CycloneDX format SBOMs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUTPUT_DIR="${OUTPUT_DIR:-$PROJECT_ROOT/sbom}"

echo "=== Merging SBOMs ==="
echo "Output directory: $OUTPUT_DIR"

cd "$OUTPUT_DIR"

# Collect all SBOM files
SBOM_FILES=()
for f in sbom-frontend.json sbom-backend.json sbom-datapipeline.json; do
    if [ -f "$f" ]; then
        SBOM_FILES+=("$f")
        echo "Found: $f"
    fi
done

if [ ${#SBOM_FILES[@]} -eq 0 ]; then
    echo "Error: No SBOM files found to merge"
    exit 1
fi

echo "Merging ${#SBOM_FILES[@]} SBOM files..."

# Check if cyclonedx-cli is available
if command -v cyclonedx &>/dev/null; then
    # Use cyclonedx-cli for merging
    cyclonedx merge \
        --input-files "${SBOM_FILES[@]}" \
        --output-file sbom-complete.json \
        --output-format json
else
    # Fallback: Create a simple merged SBOM using jq
    echo "cyclonedx-cli not found, using jq for basic merge..."

    if ! command -v jq &>/dev/null; then
        echo "Error: Neither cyclonedx-cli nor jq is available"
        echo "Please install one of them:"
        echo "  - cyclonedx-cli: https://github.com/CycloneDX/cyclonedx-cli"
        echo "  - jq: brew install jq (macOS) or apt install jq (Linux)"
        exit 1
    fi

    # Extract components from all SBOMs and merge
    echo '{"bomFormat":"CycloneDX","specVersion":"1.5","version":1,"metadata":{"timestamp":"'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'","tools":[{"vendor":"screener_system","name":"sbom-merge","version":"1.0.0"}],"component":{"type":"application","name":"screener_system","version":"1.0.0"}},"components":[]}' > sbom-complete.json

    # Merge components from each SBOM
    for f in "${SBOM_FILES[@]}"; do
        COMPONENTS=$(jq -c '.components // []' "$f")
        jq --argjson new "$COMPONENTS" '.components += $new' sbom-complete.json > tmp.json && mv tmp.json sbom-complete.json
    done

    # Remove duplicate components by purl
    jq '.components |= unique_by(.purl // .name)' sbom-complete.json > tmp.json && mv tmp.json sbom-complete.json
fi

# Validate output
if [ -f "sbom-complete.json" ]; then
    COMPONENT_COUNT=$(jq '.components | length' sbom-complete.json 2>/dev/null || echo "unknown")
    echo ""
    echo "=== Merge Complete ==="
    echo "Output: $OUTPUT_DIR/sbom-complete.json"
    echo "Total components: $COMPONENT_COUNT"
else
    echo "Error: Failed to create merged SBOM"
    exit 1
fi
