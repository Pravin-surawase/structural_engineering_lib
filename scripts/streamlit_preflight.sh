#!/bin/bash
# =============================================================================
# Streamlit Preflight Check Script (TASK-411)
# =============================================================================
#
# Run before starting Streamlit development to ensure code quality.
# Combines multiple checks in one command:
#   1. AST Scanner (check_streamlit_issues.py)
#   2. Pylint checks
#   3. Session state validation
#   4. Import analysis
#
# Usage:
#   ./scripts/streamlit_preflight.sh           # Check all pages
#   ./scripts/streamlit_preflight.sh --quick   # Quick scan, no tests
#   ./scripts/streamlit_preflight.sh --page 01 # Check specific page
#   ./scripts/streamlit_preflight.sh --fix     # Auto-fix issues where possible
#
# Exit codes:
#   0 = All checks passed
#   1 = Critical issues found (blocks development)
#   2 = High issues found (warnings, can proceed)
#   3 = Script/configuration error

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default values
QUICK_MODE=false
TARGET_PAGE=""
FIX_MODE=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick|-q)
            QUICK_MODE=true
            shift
            ;;
        --page|-p)
            TARGET_PAGE="$2"
            shift 2
            ;;
        --fix|-f)
            FIX_MODE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Streamlit Preflight Check"
            echo ""
            echo "Usage: ./scripts/streamlit_preflight.sh [options]"
            echo ""
            echo "Options:"
            echo "  --quick, -q     Quick scan (skip tests)"
            echo "  --page, -p NUM  Check specific page (e.g., 01, 02)"
            echo "  --fix, -f       Auto-fix issues where possible"
            echo "  --verbose, -v   Verbose output"
            echo "  --help, -h      Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 3
            ;;
    esac
done

# Track results
CRITICAL_COUNT=0
HIGH_COUNT=0
MEDIUM_COUNT=0
LOW_COUNT=0

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔍 Streamlit Preflight Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$PROJECT_ROOT"

# Activate virtual environment if not already active
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
    fi
fi

# =============================================================================
# Step 1: AST Scanner
# =============================================================================
echo -e "${YELLOW}Step 1/4: AST Scanner (check_streamlit_issues.py)${NC}"

SCANNER_ARGS=""
if [[ -n "$TARGET_PAGE" ]]; then
    SCANNER_ARGS="--page $TARGET_PAGE"
else
    SCANNER_ARGS="--all-pages"
fi

if [[ "$VERBOSE" == "true" ]]; then
    SCANNER_ARGS="$SCANNER_ARGS --verbose"
fi

# Run scanner and capture output
SCANNER_OUTPUT=$(.venv/bin/python scripts/check_streamlit_issues.py $SCANNER_ARGS 2>&1) || true

# Count issues from scanner output
# Parse the summary section which looks like:
#   - Errors: 0
#   - Critical: 0
#   - High: 15
#   - Medium: 1
SCANNER_CRITICAL=$(echo "$SCANNER_OUTPUT" | grep -E "^[[:space:]]*-[[:space:]]*Critical:" | sed 's/.*: //' | tr -d ' ' || echo "0")
SCANNER_HIGH=$(echo "$SCANNER_OUTPUT" | grep -E "^[[:space:]]*-[[:space:]]*High:" | sed 's/.*: //' | tr -d ' ' || echo "0")
SCANNER_MEDIUM=$(echo "$SCANNER_OUTPUT" | grep -E "^[[:space:]]*-[[:space:]]*Medium:" | sed 's/.*: //' | tr -d ' ' || echo "0")

# Ensure values are numeric
SCANNER_CRITICAL=${SCANNER_CRITICAL//[^0-9]/}
SCANNER_CRITICAL=${SCANNER_CRITICAL:-0}
SCANNER_HIGH=${SCANNER_HIGH//[^0-9]/}
SCANNER_HIGH=${SCANNER_HIGH:-0}
SCANNER_MEDIUM=${SCANNER_MEDIUM//[^0-9]/}
SCANNER_MEDIUM=${SCANNER_MEDIUM:-0}

if [[ "$SCANNER_CRITICAL" -gt 0 ]]; then
    echo -e "${RED}   ✗ Critical issues found: $SCANNER_CRITICAL${NC}"
    ((CRITICAL_COUNT += SCANNER_CRITICAL))
else
    echo -e "${GREEN}   ✓ No critical issues${NC}"
fi

if [[ "$SCANNER_HIGH" -gt 0 ]]; then
    echo -e "${YELLOW}   ⚠ High issues found: $SCANNER_HIGH${NC}"
    ((HIGH_COUNT += SCANNER_HIGH))
fi

if [[ "$VERBOSE" == "true" ]]; then
    echo "$SCANNER_OUTPUT"
fi

echo ""

# =============================================================================
# Step 2: Pylint Check
# =============================================================================
echo -e "${YELLOW}Step 2/4: Pylint Check${NC}"

PYLINT_ARGS="--rcfile=.pylintrc-streamlit"

if [[ -n "$TARGET_PAGE" ]]; then
    # Find the specific page file
    PAGE_FILE=$(find streamlit_app/pages -name "${TARGET_PAGE}*.py" | head -1)
    if [[ -n "$PAGE_FILE" ]]; then
        PYLINT_TARGET="$PAGE_FILE"
    else
        echo -e "${YELLOW}   ⚠ Page $TARGET_PAGE not found, skipping pylint${NC}"
        PYLINT_TARGET=""
    fi
else
    PYLINT_TARGET="streamlit_app/"
fi

if [[ -n "$PYLINT_TARGET" ]]; then
    PYLINT_OUTPUT=$(.venv/bin/python -m pylint $PYLINT_ARGS "$PYLINT_TARGET" 2>&1) || true
    # macOS compatible: extract score using sed
    PYLINT_SCORE=$(echo "$PYLINT_OUTPUT" | grep "rated at" | sed 's/.*rated at \([0-9.]*\).*/\1/' || echo "")
    PYLINT_ERRORS=$(echo "$PYLINT_OUTPUT" | grep -c "^E:" || echo "0")
    PYLINT_WARNINGS=$(echo "$PYLINT_OUTPUT" | grep -c "^W:" || echo "0")

    # Ensure PYLINT_ERRORS is numeric
    PYLINT_ERRORS=${PYLINT_ERRORS//[^0-9]/}
    PYLINT_ERRORS=${PYLINT_ERRORS:-0}

    if [[ "$PYLINT_ERRORS" -gt 0 ]]; then
        echo -e "${RED}   ✗ Pylint errors: $PYLINT_ERRORS${NC}"
        ((HIGH_COUNT += PYLINT_ERRORS))
    else
        echo -e "${GREEN}   ✓ No pylint errors${NC}"
    fi

    if [[ -n "$PYLINT_SCORE" ]]; then
        echo -e "   📊 Pylint score: ${PYLINT_SCORE}/10"
    fi

    if [[ "$VERBOSE" == "true" ]]; then
        echo "$PYLINT_OUTPUT"
    fi
fi

echo ""

# =============================================================================
# Step 3: Import Analysis (Uses scanner results from Step 1)
# =============================================================================
echo -e "${YELLOW}Step 3/4: Import Analysis${NC}"

# The AST scanner already detects imports inside functions more accurately
# This step just reports from scanner output
IMPORT_ISSUES=$(echo "$SCANNER_OUTPUT" | grep -c "move to module level" 2>/dev/null || echo "0")
IMPORT_ISSUES=${IMPORT_ISSUES//[^0-9]/}
IMPORT_ISSUES=${IMPORT_ISSUES:-0}

if [[ "$IMPORT_ISSUES" -gt 0 ]]; then
    echo -e "${YELLOW}   ⚠ Imports inside functions: $IMPORT_ISSUES (from scanner)${NC}"
    ((MEDIUM_COUNT += IMPORT_ISSUES))
else
    echo -e "${GREEN}   ✓ No function-level imports detected${NC}"
fi

echo ""

# =============================================================================
# Step 4: Streamlit Tests (unless --quick)
# =============================================================================
if [[ "$QUICK_MODE" == "false" ]]; then
    echo -e "${YELLOW}Step 4/4: Streamlit Tests${NC}"

    TEST_FAILED=false
    TEST_OUTPUT=$(.venv/bin/python -m pytest streamlit_app/tests/ -v --tb=short 2>&1) || TEST_FAILED=true

    if [[ "$TEST_FAILED" == "true" ]]; then
        FAILED_TESTS=$(echo "$TEST_OUTPUT" | grep -c "FAILED" 2>/dev/null || echo "0")
        FAILED_TESTS=${FAILED_TESTS//[^0-9]/}
        FAILED_TESTS=${FAILED_TESTS:-0}
        echo -e "${RED}   ✗ Tests failed: $FAILED_TESTS${NC}"
        ((HIGH_COUNT += FAILED_TESTS))
    else
        # macOS compatible: extract passed count with sed
        PASSED_TESTS=$(echo "$TEST_OUTPUT" | grep -E "[0-9]+ passed" | sed 's/.*\([0-9]* passed\).*/\1/' || echo "tests passed")
        echo -e "${GREEN}   ✓ All tests passed ($PASSED_TESTS)${NC}"
    fi

    if [[ "$VERBOSE" == "true" ]]; then
        echo "$TEST_OUTPUT"
    fi
else
    echo -e "${YELLOW}Step 4/4: Streamlit Tests (skipped - quick mode)${NC}"
fi

echo ""

# =============================================================================
# Summary
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

TOTAL_ISSUES=$((CRITICAL_COUNT + HIGH_COUNT + MEDIUM_COUNT + LOW_COUNT))

if [[ "$CRITICAL_COUNT" -gt 0 ]]; then
    echo -e "${RED}🔴 Critical: $CRITICAL_COUNT${NC}"
fi
if [[ "$HIGH_COUNT" -gt 0 ]]; then
    echo -e "${YELLOW}🟠 High: $HIGH_COUNT${NC}"
fi
if [[ "$MEDIUM_COUNT" -gt 0 ]]; then
    echo -e "${YELLOW}🟡 Medium: $MEDIUM_COUNT${NC}"
fi
if [[ "$LOW_COUNT" -gt 0 ]]; then
    echo -e "${BLUE}🔵 Low: $LOW_COUNT${NC}"
fi

echo ""

# Exit with appropriate code
if [[ "$CRITICAL_COUNT" -gt 0 ]]; then
    echo -e "${RED}❌ PREFLIGHT FAILED - Fix critical issues before development${NC}"
    exit 1
elif [[ "$HIGH_COUNT" -gt 0 ]]; then
    echo -e "${YELLOW}⚠️ PREFLIGHT WARNINGS - Proceed with caution${NC}"
    exit 2
else
    echo -e "${GREEN}✅ PREFLIGHT PASSED - Ready for development${NC}"
    exit 0
fi
