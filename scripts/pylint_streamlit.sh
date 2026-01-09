#!/usr/bin/env bash
#
# Pylint Wrapper for Streamlit Pages
#
# Runs pylint with focused error detection configuration.
# Complements check_streamlit_issues.py AST scanner.
#
# Usage:
#     ./scripts/pylint_streamlit.sh --all-pages
#     ./scripts/pylint_streamlit.sh --page beam_design
#     ./scripts/pylint_streamlit.sh --compare
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAGES_DIR="$PROJECT_ROOT/streamlit_app/pages"
PYLINTRC="$PROJECT_ROOT/.pylintrc-streamlit"

# Check if pylint is installed
if ! command -v pylint &> /dev/null; then
    echo -e "${RED}❌ pylint not found. Install with: pip install pylint${NC}"
    exit 1
fi

# Function to run pylint on files
run_pylint() {
    local files=("$@")

    if [ ${#files[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No files to check${NC}"
        return 0
    fi

    echo -e "${BLUE}🔍 Running pylint on ${#files[@]} file(s)...${NC}"
    echo

    # Run pylint with custom config
    # Use --exit-zero to not fail on findings (we'll parse output)
    pylint --rcfile="$PYLINTRC" "${files[@]}" || true
}

# Function to scan all pages
scan_all_pages() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔍 PYLINT SCAN - ALL STREAMLIT PAGES${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo

    # Find all Python files in pages directory
    mapfile -t page_files < <(find "$PAGES_DIR" -maxdepth 1 -name "*.py" | sort)

    if [ ${#page_files[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No Python files found in $PAGES_DIR${NC}"
        return 1
    fi

    run_pylint "${page_files[@]}"
}

# Function to scan specific page
scan_page() {
    local page_pattern="$1"

    echo -e "${BLUE}🔍 Scanning for pages matching: $page_pattern${NC}"
    echo

    # Find matching files
    mapfile -t matching_files < <(find "$PAGES_DIR" -maxdepth 1 -name "*${page_pattern}*.py" | sort)

    if [ ${#matching_files[@]} -eq 0 ]; then
        echo -e "${RED}❌ No pages found matching '$page_pattern'${NC}"
        return 1
    fi

    echo -e "${GREEN}Found ${#matching_files[@]} matching file(s):${NC}"
    for file in "${matching_files[@]}"; do
        echo "  - $(basename "$file")"
    done
    echo

    run_pylint "${matching_files[@]}"
}

# Function to compare pylint with AST scanner
compare_results() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📊 COMPARISON: Pylint vs AST Scanner${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo

    # Create temp files for outputs
    PYLINT_OUTPUT=$(mktemp)
    AST_OUTPUT=$(mktemp)

    # Ensure cleanup on exit
    trap "rm -f $PYLINT_OUTPUT $AST_OUTPUT" EXIT

    echo -e "${YELLOW}Running pylint...${NC}"
    mapfile -t page_files < <(find "$PAGES_DIR" -maxdepth 1 -name "*.py" | sort)
    pylint --rcfile="$PYLINTRC" "${page_files[@]}" > "$PYLINT_OUTPUT" 2>&1 || true

    echo -e "${YELLOW}Running AST scanner...${NC}"
    python "$PROJECT_ROOT/scripts/check_streamlit_issues.py" --all-pages > "$AST_OUTPUT" 2>&1 || true

    echo
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Count issues in each
    PYLINT_ISSUES=$(grep -c "^\S.*:\d.*:\[" "$PYLINT_OUTPUT" || echo "0")
    AST_CRITICAL=$(grep -c "CRITICAL:" "$AST_OUTPUT" || echo "0")
    AST_HIGH=$(grep -c "HIGH:" "$AST_OUTPUT" || echo "0")
    AST_TOTAL=$((AST_CRITICAL + AST_HIGH))

    echo
    echo -e "${GREEN}Pylint findings:${NC} $PYLINT_ISSUES issues"
    echo -e "${GREEN}AST Scanner findings:${NC} $AST_TOTAL issues (Critical: $AST_CRITICAL, High: $AST_HIGH)"
    echo

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Pylint unique findings (sample):${NC}"
    head -20 "$PYLINT_OUTPUT" | grep "^\S.*:\d.*:\[" || echo "  (none)"
    echo

    echo -e "${YELLOW}AST Scanner unique findings (sample):${NC}"
    grep -A 1 "CRITICAL:" "$AST_OUTPUT" | head -10 || echo "  (none)"
    echo

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ Comparison complete${NC}"
    echo
    echo -e "Full outputs saved to:"
    echo -e "  - Pylint: $PYLINT_OUTPUT"
    echo -e "  - AST: $AST_OUTPUT"
}

# Main script
main() {
    local mode="${1:-}"

    case "$mode" in
        --all-pages)
            scan_all_pages
            ;;
        --page)
            if [ -z "${2:-}" ]; then
                echo -e "${RED}❌ Please provide a page name pattern${NC}"
                echo "Usage: $0 --page <pattern>"
                exit 1
            fi
            scan_page "$2"
            ;;
        --compare)
            compare_results
            ;;
        --help|-h|"")
            echo "Pylint Wrapper for Streamlit Pages"
            echo
            echo "Usage:"
            echo "  $0 --all-pages          Scan all pages"
            echo "  $0 --page <pattern>     Scan specific page"
            echo "  $0 --compare            Compare with AST scanner"
            echo "  $0 --help               Show this help"
            echo
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $mode${NC}"
            echo "Run '$0 --help' for usage"
            exit 1
            ;;
    esac
}

# Run main with all arguments
main "$@"
