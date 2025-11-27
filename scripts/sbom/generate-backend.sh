#!/bin/bash
# Generate SBOM for Backend (Python)
# Uses cyclonedx-py to generate CycloneDX format SBOM

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
OUTPUT_DIR="${OUTPUT_DIR:-$PROJECT_ROOT/sbom}"

echo "=== Generating Backend SBOM ==="
echo "Backend directory: $BACKEND_DIR"
echo "Output directory: $OUTPUT_DIR"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

cd "$BACKEND_DIR"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found in $BACKEND_DIR"
    exit 1
fi

# Create temporary venv for cyclonedx-bom
VENV_DIR="$SCRIPT_DIR/.venv-sbom"

# Check if we need to create/use venv
if ! python3 -m cyclonedx_py --version &>/dev/null; then
    echo "Setting up cyclonedx-bom in virtual environment..."

    # Create venv if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
    fi

    # Activate venv and install
    source "$VENV_DIR/bin/activate"
    pip install --quiet cyclonedx-bom

    PYTHON="$VENV_DIR/bin/python3"
else
    PYTHON="python3"
fi

# Generate SBOM from requirements.txt
echo "Generating CycloneDX SBOM from requirements.txt..."
$PYTHON -m cyclonedx_py requirements \
    requirements.txt \
    -o "$OUTPUT_DIR/sbom-backend.json" \
    --of JSON \
    --sv 1.5 \
    --mc-type application

# Validate output
if [ -f "$OUTPUT_DIR/sbom-backend.json" ]; then
    COMPONENT_COUNT=$(cat "$OUTPUT_DIR/sbom-backend.json" | grep -c '"name"' || echo "0")
    echo "Backend SBOM generated successfully!"
    echo "Output: $OUTPUT_DIR/sbom-backend.json"
    echo "Components: ~$COMPONENT_COUNT"
else
    echo "Error: Failed to generate Backend SBOM"
    exit 1
fi
