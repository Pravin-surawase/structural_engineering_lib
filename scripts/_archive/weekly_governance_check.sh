#!/usr/bin/env bash
#
# Weekly Governance Check
# Runs all validation checks for folder structure, links, and documentation quality.
#
# Usage:
#   ./scripts/weekly_governance_check.sh           # Run all checks
#   ./scripts/weekly_governance_check.sh --quick   # Skip slow checks
#   ./scripts/weekly_governance_check.sh --fix     # Run fixes where available
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed
#

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Options
QUICK=false
FIX=false
FAILED=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --quick) QUICK=true; shift ;;
        --fix) FIX=true; shift ;;
        --help|-h)
            echo "Usage: $0 [--quick] [--fix]"
            echo "  --quick  Skip slow checks (like full link scan)"
            echo "  --fix    Run fixes where available"
            exit 0
            ;;
        *) shift ;;
    esac
done

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}     Weekly Governance Check${NC}"
echo -e "${BLUE}     $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check 1: Folder structure validation
echo -e "${YELLOW}[1/5] Folder Structure Validation${NC}"
if .venv/bin/python scripts/validate_folder_structure.py 2>&1 | tail -5; then
    echo -e "${GREEN}  ✅ Folder structure valid${NC}"
else
    echo -e "${RED}  ❌ Folder structure issues found${NC}"
    FAILED=$((FAILED + 1))
fi
echo ""

# Check 2: Internal link validation
echo -e "${YELLOW}[2/5] Internal Link Validation${NC}"
if [[ "$QUICK" == "true" ]]; then
    echo -e "  (Skipped in quick mode)"
else
    LINK_OUTPUT=$(.venv/bin/python scripts/check_links.py 2>&1 | tail -5)
    echo "$LINK_OUTPUT"
    if echo "$LINK_OUTPUT" | grep -q "Broken links: 0"; then
        echo -e "${GREEN}  ✅ All links valid${NC}"
    else
        echo -e "${RED}  ❌ Broken links found${NC}"
        if [[ "$FIX" == "true" ]]; then
            echo "  Running fix_broken_links.py..."
            .venv/bin/python scripts/fix_broken_links.py --fix 2>&1 | tail -10 || true
        fi
        FAILED=$((FAILED + 1))
    fi
fi
echo ""

# Check 3: Root file count
echo -e "${YELLOW}[3/5] Root File Count${NC}"
ROOT_COUNT=$(find . -maxdepth 1 -name "*.md" -o -name "*.py" | grep -v ".venv" | wc -l | tr -d ' ')
ROOT_TARGET=10
if [[ "$ROOT_COUNT" -le "$ROOT_TARGET" ]]; then
    echo -e "${GREEN}  ✅ Root files: $ROOT_COUNT (target: ≤$ROOT_TARGET)${NC}"
else
    echo -e "${RED}  ❌ Root files: $ROOT_COUNT (target: ≤$ROOT_TARGET)${NC}"
    FAILED=$((FAILED + 1))
fi
echo ""

# Check 4: Docs root file count
echo -e "${YELLOW}[4/5] Docs Root File Count${NC}"
DOCS_ROOT_COUNT=$(find docs -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
DOCS_TARGET=5
if [[ "$DOCS_ROOT_COUNT" -le "$DOCS_TARGET" ]]; then
    echo -e "${GREEN}  ✅ docs/ root files: $DOCS_ROOT_COUNT (target: ≤$DOCS_TARGET)${NC}"
else
    echo -e "${RED}  ❌ docs/ root files: $DOCS_ROOT_COUNT (target: ≤$DOCS_TARGET)${NC}"
    FAILED=$((FAILED + 1))
fi
echo ""

# Check 5: Agent entry points
echo -e "${YELLOW}[5/5] Agent Entry Points${NC}"
ENTRY_POINTS=0
EXPECTED=3

# Agent 6
if [[ -f "docs/agents/guides/agent-6-quick-start.md" ]]; then
    ENTRY_POINTS=$((ENTRY_POINTS + 1))
fi
# Agent 8
if [[ -f "docs/agents/guides/agent-8-quick-start.md" ]]; then
    ENTRY_POINTS=$((ENTRY_POINTS + 1))
fi
# Agent 9
if [[ -f "docs/agents/guides/agent-9-quick-start.md" ]]; then
    ENTRY_POINTS=$((ENTRY_POINTS + 1))
fi

if [[ "$ENTRY_POINTS" -eq "$EXPECTED" ]]; then
    echo -e "${GREEN}  ✅ Agent entry points: $ENTRY_POINTS/$EXPECTED${NC}"
else
    echo -e "${RED}  ❌ Agent entry points: $ENTRY_POINTS/$EXPECTED${NC}"
    FAILED=$((FAILED + 1))
fi
echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [[ "$FAILED" -eq 0 ]]; then
    echo -e "${GREEN}✅ All governance checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAILED check(s) failed${NC}"
    exit 1
fi
