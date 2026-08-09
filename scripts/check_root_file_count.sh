#!/bin/bash
# Check Root File Count
# Ensures root directory doesn't accumulate documentation sprawl
# Target: ≤15 files (ALL non-hidden files, consistent with Python validator)
# Research: Industry standard from Prettier, Vitest, tRPC case studies
#
# FIXED Session 13: Now counts ALL files (not just .md/.txt/.sh) to match
# check_governance_compliance.py behavior. Previous version had inconsistent
# counting that could pass bash check but fail Python check.

set -e

# Configuration — single source of truth: governance-limits.json
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_RUNTIME="$PROJECT_ROOT/scripts/python_runtime.sh"
cd "$PROJECT_ROOT"

GOVERNANCE_JSON="$PROJECT_ROOT/docs/guidelines/governance-limits.json"
if [[ -f "$GOVERNANCE_JSON" ]]; then
    MAX_FILES=$("$PYTHON_RUNTIME" -c 'import json, sys; print(json.load(open(sys.argv[1]))["root"]["max_files"])' "$GOVERNANCE_JSON" 2>/dev/null || echo 17)
else
    MAX_FILES=17
    echo "⚠ governance-limits.json not found, using default MAX_FILES=$MAX_FILES"
fi

# Count ALL root files (excluding hidden files) - FIXED: matches Python validator
# Excludes: hidden files (.*), directories
ROOT_FILES=$(find . -maxdepth 1 -type f ! -name ".*" | sort)
FILE_COUNT=$(echo "$ROOT_FILES" | grep -v "^$" | wc -l | tr -d ' ')

echo "=== Root File Count Check ==="
echo "Target: ≤${MAX_FILES} files"
echo "Current: ${FILE_COUNT} files"
echo ""

if [ "$FILE_COUNT" -le "$MAX_FILES" ]; then
    echo "✅ PASS: Root file count is within limit"
    echo ""
    echo "Current root files:"
    echo "$ROOT_FILES" | sed 's|^\./|  - |'
    exit 0
else
    echo "❌ FAIL: Root file count exceeds limit"
    echo ""
    echo "Current root files (${FILE_COUNT}):"
    echo "$ROOT_FILES" | sed 's|^\./|  - |'
    echo ""
    echo "Action Required:"
    echo "1. Review which files can be archived to docs/_archive/YYYY-MM/"
    echo "2. Canonical files that should stay in root:"
    echo "   - README.md, CHANGELOG.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md"
    echo "   - SECURITY.md, AUTHORS.md, LICENSE*, SUPPORT.md"
    echo "3. Run: ./scripts/python_runtime.sh scripts/safe_file_move.py <file> docs/_archive/YYYY-MM/<file> --dry-run"
    echo "   Then rerun without --dry-run after reviewing the preview."
    echo "4. Update docs/_archive/README.md"
    echo ""
    echo "See: docs/_archive/README.md for archival guidelines"
    exit 1
fi
