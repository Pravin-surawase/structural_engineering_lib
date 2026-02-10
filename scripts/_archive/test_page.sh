#!/bin/bash
# Page Test Runner (Solution 5 - Dev Automation)
#
# Test a single Streamlit page quickly
# Runs scanner + tests + import check
#
# Author: Agent 6 (Quality Improvement - Solution 5)
# Date: 2026-01-09

set -e

PAGE_NAME=$1

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$PAGE_NAME" ]; then
    echo "Page Test Runner"
    echo "════════════════════════════════════"
    echo ""
    echo "Usage: ./scripts/test_page.sh <page_name>"
    echo ""
    echo "Examples:"
    echo "  ./scripts/test_page.sh beam_design"
    echo "  ./scripts/test_page.sh bbs_generator"
    echo "  ./scripts/test_page.sh dxf_export"
    echo ""
    echo "What it does:"
    echo "  1. Scans page for issues (scanner)"
    echo "  2. Runs page-specific tests"
    echo "  3. Verifies page imports successfully"
    echo ""
    exit 1
fi

echo "🧪 Testing page: $PAGE_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

START=$(date +%s)
FAILED=0

# 1. Scan page for issues
echo -e "${YELLOW}🔍 Scanning page for issues...${NC}"
if python3 scripts/check_streamlit_issues.py --page "$PAGE_NAME" 2>/dev/null; then
    echo -e "${GREEN}  ✓ No critical issues${NC}"
else
    echo -e "${RED}  ✗ Issues found${NC}"
    FAILED=1
fi

# 2. Run page tests
echo -e "${YELLOW}🧪 Running page tests...${NC}"
TEST_FILE="streamlit_app/tests/test_${PAGE_NAME}.py"
if [ -f "$TEST_FILE" ]; then
    if pytest "$TEST_FILE" -v --tb=short; then
        echo -e "${GREEN}  ✓ Tests passed${NC}"
    else
        echo -e "${RED}  ✗ Tests failed${NC}"
        FAILED=1
    fi
else
    echo -e "${YELLOW}  ⚠ No test file found: $TEST_FILE${NC}"
    echo -e "${YELLOW}    Create with: python scripts/create_test_scaffold.py ${PAGE_NAME^} streamlit_app.pages.${PAGE_NAME} streamlit_page${NC}"
fi

# 3. Import check
echo -e "${YELLOW}📦 Checking imports...${NC}"
PAGE_FILE=$(find streamlit_app/pages -name "*${PAGE_NAME}.py" | head -1)
if [ -n "$PAGE_FILE" ]; then
    # Extract module name from file path
    MODULE_NAME=$(echo "$PAGE_FILE" | sed 's/\//./g' | sed 's/\.py$//' | sed 's/^\.\///')

    if python3 -c "import sys; sys.path.insert(0, '.'); import $MODULE_NAME" 2>/dev/null; then
        echo -e "${GREEN}  ✓ Import successful${NC}"
    else
        echo -e "${RED}  ✗ Import failed${NC}"
        echo -e "${RED}    Page has syntax or import errors${NC}"
        FAILED=1
    fi
else
    echo -e "${RED}  ✗ Page file not found${NC}"
    FAILED=1
fi

# Summary
END=$(date +%s)
ELAPSED=$((END - START))

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Page tests complete in ${ELAPSED}s${NC}"
    echo -e "${GREEN}   $PAGE_NAME is ready!${NC}"
    exit 0
else
    echo -e "${RED}❌ Page tests failed in ${ELAPSED}s${NC}"
    echo -e "${RED}   Fix issues in $PAGE_NAME${NC}"
    exit 1
fi
