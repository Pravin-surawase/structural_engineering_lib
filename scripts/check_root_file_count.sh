#!/bin/bash
# Check Root File Count
# Ensures root directory doesn't accumulate documentation sprawl
# Target: ≤10 files (ALL non-hidden files, consistent with Python validator)
# Research: Industry standard from Prettier, Vitest, tRPC case studies
#
# FIXED Session 13: Now counts ALL files (not just .md/.txt/.sh) to match
# check_governance_compliance.py behavior. Previous version had inconsistent
# counting that could pass bash check but fail Python check.

set -e

# Configuration
MAX_FILES=10
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

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
    echo "3. Run: git mv <file> docs/_archive/\$(date +%Y-%m)/"
    echo "4. Update docs/_archive/README.md"
    echo ""
    echo "See: docs/_archive/README.md for archival guidelines"
    exit 1
fi
