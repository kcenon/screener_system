#!/bin/bash
# Build API documentation (Sphinx + TypeDoc) and integrate with Docusaurus

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================================"
echo "Building API Documentation"
echo "================================================"

# Colors for output
GREEN='\033[0.32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

#Step 1: Build Sphinx documentation (Python API)
echo -e "${BLUE}Step 1: Building Sphinx documentation...${NC}"
cd "$PROJECT_ROOT/docs/api/python"

# Check if sphinx-build is available
if ! command -v sphinx-build &> /dev/null; then
    echo "WARNING: sphinx-build not found. Please install Sphinx:"
    echo "  pip install -r requirements-docs.txt"
    echo ""
    echo "Attempting to install dependencies..."
    if command -v pip &> /dev/null; then
        pip install -r "$PROJECT_ROOT/requirements-docs.txt"
    elif command -v pip3 &> /dev/null; then
        pip3 install -r "$PROJECT_ROOT/requirements-docs.txt"
    else
        echo "ERROR: pip/pip3 not found. Please install Python dependencies manually."
        exit 1
    fi
fi

# Clean previous build
make clean

# Build HTML documentation
make html

echo -e "${GREEN}✓ Sphinx documentation built successfully${NC}"

# Step 2: Copy Sphinx HTML to Docusaurus static folder
echo -e "${BLUE}Step 2: Copying Sphinx HTML to Docusaurus...${NC}"
DOCUSAURUS_STATIC="$PROJECT_ROOT/docs-site/static/api"
mkdir -p "$DOCUSAURUS_STATIC"
rm -rf "$DOCUSAURUS_STATIC/python"
cp -r _build/html "$DOCUSAURUS_STATIC/python"

echo -e "${GREEN}✓ Sphinx HTML copied to docs-site/static/api/python${NC}"

# Step 3: Build TypeDoc documentation (TypeScript API) - if exists
# This will be handled by DOC-003
echo -e "${BLUE}Step 3: TypeDoc build (placeholder for DOC-003)${NC}"
echo "  TypeDoc integration will be handled in DOC-003"

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}API Documentation Build Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Sphinx HTML: $DOCUSAURUS_STATIC/python/index.html"
echo ""
echo "To view in Docusaurus:"
echo "  cd docs-site && npm start"
echo "  Navigate to: http://localhost:3000/api/python/"
echo ""
