#!/bin/bash

# CI/CD Pipeline Validation Script
# This script validates that GitHub Actions workflows are properly configured

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "CI/CD Pipeline Validation"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in a git repository
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo -e "${RED}✗ Not a git repository${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Git repository detected${NC}"

# Check GitHub remote
REMOTE_URL=$(git -C "$PROJECT_ROOT" remote get-url origin 2>/dev/null || echo "")
if [ -z "$REMOTE_URL" ]; then
    echo -e "${RED}✗ No GitHub remote configured${NC}"
    exit 1
fi
echo -e "${GREEN}✓ GitHub remote: $REMOTE_URL${NC}"

# Extract repository name
if [[ $REMOTE_URL =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
    REPO_OWNER="${BASH_REMATCH[1]}"
    REPO_NAME="${BASH_REMATCH[2]}"
    echo -e "${GREEN}✓ Repository: $REPO_OWNER/$REPO_NAME${NC}"
else
    echo -e "${RED}✗ Could not parse GitHub repository from remote URL${NC}"
    exit 1
fi

echo ""
echo "========================================="
echo "Workflow Files Validation"
echo "========================================="
echo ""

# Check workflow files exist
WORKFLOW_DIR="$PROJECT_ROOT/.github/workflows"
if [ ! -d "$WORKFLOW_DIR" ]; then
    echo -e "${RED}✗ .github/workflows directory not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Workflows directory exists${NC}"

# Required workflows
REQUIRED_WORKFLOWS=("ci.yml" "cd.yml" "pr-checks.yml")
for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
    if [ -f "$WORKFLOW_DIR/$workflow" ]; then
        echo -e "${GREEN}✓ $workflow found${NC}"
    else
        echo -e "${RED}✗ $workflow not found${NC}"
        exit 1
    fi
done

echo ""
echo "========================================="
echo "Workflow Syntax Validation"
echo "========================================="
echo ""

# Validate YAML syntax using Python
if command -v python3 &> /dev/null; then
    for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
        if python3 -c "import yaml; yaml.safe_load(open('$WORKFLOW_DIR/$workflow'))" 2>/dev/null; then
            echo -e "${GREEN}✓ $workflow has valid YAML syntax${NC}"
        else
            echo -e "${RED}✗ $workflow has invalid YAML syntax${NC}"
            exit 1
        fi
    done
else
    echo -e "${YELLOW}⚠ Python3 not available, skipping YAML validation${NC}"
fi

echo ""
echo "========================================="
echo "Backend Test Environment"
echo "========================================="
echo ""

# Check backend test dependencies
cd "$PROJECT_ROOT/backend"

if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✓ requirements.txt found${NC}"

    # Check for pytest
    if grep -q "pytest" requirements.txt; then
        echo -e "${GREEN}✓ pytest in requirements.txt${NC}"
    else
        echo -e "${RED}✗ pytest not found in requirements.txt${NC}"
        exit 1
    fi

    # Check for coverage
    if grep -q "pytest-cov" requirements.txt; then
        echo -e "${GREEN}✓ pytest-cov in requirements.txt${NC}"
    else
        echo -e "${YELLOW}⚠ pytest-cov not found in requirements.txt${NC}"
    fi
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi

# Check test directory
if [ -d "tests" ]; then
    TEST_COUNT=$(find tests -name "test_*.py" -o -name "*_test.py" | wc -l)
    echo -e "${GREEN}✓ Test directory exists ($TEST_COUNT test files)${NC}"
else
    echo -e "${YELLOW}⚠ Test directory not found${NC}"
fi

echo ""
echo "========================================="
echo "Frontend Test Environment"
echo "========================================="
echo ""

# Check frontend test dependencies
cd "$PROJECT_ROOT/frontend"

if [ -f "package.json" ]; then
    echo -e "${GREEN}✓ package.json found${NC}"

    # Check for vitest
    if grep -q "vitest" package.json; then
        echo -e "${GREEN}✓ vitest in package.json${NC}"
    else
        echo -e "${RED}✗ vitest not found in package.json${NC}"
        exit 1
    fi

    # Check for test scripts
    if grep -q "\"test\"" package.json; then
        echo -e "${GREEN}✓ test script defined in package.json${NC}"
    else
        echo -e "${RED}✗ test script not found in package.json${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ package.json not found${NC}"
    exit 1
fi

# Check test directory
if [ -d "src/__tests__" ] || [ -d "tests" ] || find src -name "*.test.tsx" -o -name "*.test.ts" | grep -q .; then
    echo -e "${GREEN}✓ Test files found${NC}"
else
    echo -e "${YELLOW}⚠ No test files found${NC}"
fi

echo ""
echo "========================================="
echo "Docker Configuration"
echo "========================================="
echo ""

cd "$PROJECT_ROOT"

# Check Dockerfile for backend
if [ -f "backend/Dockerfile" ]; then
    echo -e "${GREEN}✓ backend/Dockerfile found${NC}"
else
    echo -e "${RED}✗ backend/Dockerfile not found${NC}"
    exit 1
fi

# Check Dockerfile for frontend
if [ -f "frontend/Dockerfile" ]; then
    echo -e "${GREEN}✓ frontend/Dockerfile found${NC}"
else
    echo -e "${RED}✗ frontend/Dockerfile not found${NC}"
    exit 1
fi

# Check docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    echo -e "${GREEN}✓ docker-compose.yml found${NC}"
else
    echo -e "${YELLOW}⚠ docker-compose.yml not found${NC}"
fi

echo ""
echo "========================================="
echo "README Status Badges"
echo "========================================="
echo ""

if [ -f "README.md" ]; then
    echo -e "${GREEN}✓ README.md found${NC}"

    # Check for CI badge
    if grep -q "actions/workflows/ci.yml/badge.svg" README.md; then
        echo -e "${GREEN}✓ CI Pipeline badge found${NC}"
    else
        echo -e "${YELLOW}⚠ CI Pipeline badge not found${NC}"
    fi

    # Check for CD badge
    if grep -q "actions/workflows/cd.yml/badge.svg" README.md; then
        echo -e "${GREEN}✓ CD Pipeline badge found${NC}"
    else
        echo -e "${YELLOW}⚠ CD Pipeline badge not found${NC}"
    fi

    # Check for PR checks badge
    if grep -q "actions/workflows/pr-checks.yml/badge.svg" README.md; then
        echo -e "${GREEN}✓ PR Checks badge found${NC}"
    else
        echo -e "${YELLOW}⚠ PR Checks badge not found${NC}"
    fi

    # Check for coverage badge
    if grep -q "codecov.io" README.md; then
        echo -e "${GREEN}✓ Code coverage badge found${NC}"
    else
        echo -e "${YELLOW}⚠ Code coverage badge not found${NC}"
    fi
else
    echo -e "${RED}✗ README.md not found${NC}"
    exit 1
fi

echo ""
echo "========================================="
echo "GitHub Actions Permissions"
echo "========================================="
echo ""

echo "The following secrets should be configured in GitHub repository settings:"
echo "  - Navigate to: Settings → Secrets and variables → Actions"
echo ""
echo "Required secrets (if using external services):"
echo "  • CODECOV_TOKEN (for code coverage reporting)"
echo "  • SLACK_WEBHOOK_URL (for Slack notifications)"
echo "  • EMAIL_USERNAME (for email notifications)"
echo "  • EMAIL_PASSWORD (for email notifications)"
echo ""
echo "Note: GITHUB_TOKEN is automatically provided by GitHub Actions"
echo ""
echo -e "${YELLOW}⚠ Manual verification required for repository secrets${NC}"

echo ""
echo "========================================="
echo "Next Steps for Complete Validation"
echo "========================================="
echo ""
echo "To fully validate the CI/CD pipeline:"
echo ""
echo "1. Push this branch to GitHub:"
echo "   git push -u origin $(git branch --show-current)"
echo ""
echo "2. Create a Pull Request:"
echo "   gh pr create --base main --head $(git branch --show-current) \\"
echo "     --title \"ci: Complete CI/CD pipeline validation\" \\"
echo "     --body \"Validates GitHub Actions workflows per BUGFIX-009\""
echo ""
echo "3. Verify workflows run on GitHub:"
echo "   https://github.com/$REPO_OWNER/$REPO_NAME/actions"
echo ""
echo "4. Check workflow results:"
echo "   • Backend Tests: Should pass all tests"
echo "   • Frontend Tests: Should pass all tests"
echo "   • Linting: Should complete (warnings allowed)"
echo "   • PR Checks: Should validate PR format"
echo ""
echo "5. Merge the PR after validation"
echo ""

echo "========================================="
echo "Validation Summary"
echo "========================================="
echo ""
echo -e "${GREEN}✓ All local checks passed!${NC}"
echo ""
echo "CI/CD pipeline is properly configured locally."
echo "Trigger GitHub Actions by pushing to verify complete functionality."
echo ""
