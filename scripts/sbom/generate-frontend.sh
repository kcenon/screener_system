#!/bin/bash
# Generate SBOM for Frontend (npm/Node.js)
# Uses @cyclonedx/cyclonedx-npm to generate CycloneDX format SBOM

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
OUTPUT_DIR="${OUTPUT_DIR:-$PROJECT_ROOT/sbom}"

echo "=== Generating Frontend SBOM ==="
echo "Frontend directory: $FRONTEND_DIR"
echo "Output directory: $OUTPUT_DIR"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

cd "$FRONTEND_DIR"

# Check if package-lock.json exists
if [ ! -f "package-lock.json" ]; then
    echo "Error: package-lock.json not found in $FRONTEND_DIR"
    exit 1
fi

# Check if cyclonedx-npm is available
if ! npx @cyclonedx/cyclonedx-npm --version &>/dev/null; then
    echo "Installing @cyclonedx/cyclonedx-npm..."
    npm install --save-dev @cyclonedx/cyclonedx-npm
fi

# Generate SBOM
echo "Generating CycloneDX SBOM..."
npx @cyclonedx/cyclonedx-npm \
    --output-file "$OUTPUT_DIR/sbom-frontend.json" \
    --output-format JSON \
    --spec-version 1.5 \
    --mc-type application \
    --package-lock-only

# Validate output
if [ -f "$OUTPUT_DIR/sbom-frontend.json" ]; then
    COMPONENT_COUNT=$(cat "$OUTPUT_DIR/sbom-frontend.json" | grep -c '"type"' || echo "0")
    echo "Frontend SBOM generated successfully!"
    echo "Output: $OUTPUT_DIR/sbom-frontend.json"
    echo "Components: ~$COMPONENT_COUNT"
else
    echo "Error: Failed to generate Frontend SBOM"
    exit 1
fi
