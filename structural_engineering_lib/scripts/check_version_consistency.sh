#!/bin/bash

# check_version_consistency.sh - Verify version strings are consistent
# Purpose: Ensure version numbers match across pyproject.toml, docs, and VBA
# Helps catch drift before releases

set -e

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Version Consistency Check${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Extract versions from key files
PYPROJECT_VERSION=$(grep -m1 '^version = ' Python/pyproject.toml | sed 's/version = "\(.*\)"/\1/')
CHANGELOG_VERSION=$(head -20 CHANGELOG.md | grep -m1 '^## \[' | sed 's/.*\[\(.*\)\].*/\1/')
CITATION_VERSION=$(grep 'version:' CITATION.cff | head -1 | sed 's/.*: //')
VBA_VERSION=$(grep -m1 'Const VERSION' VBA/*.bas 2>/dev/null | grep -o '"[^"]*"' | head -1 | tr -d '"' || echo "NOT_FOUND")

echo -e "\n📦 Version Strings Found:"
echo -e "  Python (pyproject.toml):     ${BLUE}$PYPROJECT_VERSION${NC}"
echo -e "  Changelog (CHANGELOG.md):    ${BLUE}$CHANGELOG_VERSION${NC}"
echo -e "  Citation (CITATION.cff):     ${BLUE}$CITATION_VERSION${NC}"
echo -e "  VBA (*.bas):                 ${BLUE}$VBA_VERSION${NC}"

# Check consistency (allow known exceptions)
MISMATCHES=0

# Changelog can be "Unreleased" before releases
if [ "$CHANGELOG_VERSION" != "Unreleased" ] && [ "$PYPROJECT_VERSION" != "$CHANGELOG_VERSION" ]; then
  echo -e "\n${RED}❌ MISMATCH: Python version ($PYPROJECT_VERSION) != Changelog ($CHANGELOG_VERSION)${NC}"
  MISMATCHES=$((MISMATCHES + 1))
elif [ "$CHANGELOG_VERSION" = "Unreleased" ]; then
  echo -e "\n${YELLOW}ℹ️  Changelog shows 'Unreleased' (OK before release)${NC}"
fi

# Citation version can differ (different versioning scheme)
if [ -n "$CITATION_VERSION" ]; then
  echo -e "\n${YELLOW}ℹ️  Citation has independent versioning (OK)${NC}"
fi

# Check VBA only if found
if [ "$VBA_VERSION" != "NOT_FOUND" ] && [ -n "$VBA_VERSION" ] && [ "$PYPROJECT_VERSION" != "$VBA_VERSION" ]; then
  echo -e "\n${YELLOW}⚠️  VBA version differs (check if intentional)${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$MISMATCHES" -eq 0 ]; then
  echo -e "${GREEN}✅ All versions consistent!${NC}"
  exit 0
else
  echo -e "${RED}⚠️  Found $MISMATCHES version mismatch(es)${NC}"
  echo -e "\nRun ${BLUE}scripts/check_doc_versions.py --fix${NC} to auto-fix"
  exit 1
fi
