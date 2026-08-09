#!/bin/bash
# Watch Mode (Solution 5 - Dev Automation)
#
# Auto-run tests when files change
# Provides instant feedback during development
#
# Requires: fswatch (install with: brew install fswatch on macOS)
# When to use: during a focused Python implementation loop when fswatch is available.
#
# Author: Agent 6 (Quality Improvement - Solution 5)
# Date: 2026-01-09

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_RUNTIME="$SCRIPT_DIR/python_runtime.sh"
cd "$REPO_ROOT"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Usage: ./scripts/watch_tests.sh [watch_dir] [pytest_path]"
    echo "Defaults: watch_dir=. pytest_path=Python/tests/"
    exit 0
fi

WATCH_DIR=${1:-.}
TEST_PATTERN=${2:-Python/tests/}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if fswatch is installed
if ! command -v fswatch &> /dev/null; then
    echo -e "${RED}❌ fswatch not found${NC}"
    echo ""
    echo "Install fswatch:"
    echo "  macOS:   brew install fswatch"
    echo "  Ubuntu:  apt-get install fswatch"
    echo "  Other:   https://github.com/emcrisostomo/fswatch"
    echo ""
    exit 1
fi

echo -e "${BLUE}👀 Watch Mode Starting...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Watching:${NC} $WATCH_DIR"
echo -e "${YELLOW}Running tests:${NC} $TEST_PATTERN"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run initial validation
echo -e "${GREEN}▶ Initial validation...${NC}"
"$REPO_ROOT/run.sh" check --quick || true
"$PYTHON_RUNTIME" -m pytest "$TEST_PATTERN" -x -q --tb=short || true
echo ""
echo -e "${BLUE}👀 Waiting for changes...${NC}"

# Watch loop
while true; do
    # Wait for file change (blocks until change detected)
    fswatch -1 "$WATCH_DIR" \
        --exclude '.*\.pyc$' \
        --exclude '__pycache__' \
        --exclude '.pytest_cache' \
        --exclude '.git' \
        --exclude 'node_modules' \
        --include '.*\.py$' > /dev/null

    # Clear screen and show timestamp
    clear
    echo -e "${BLUE}══════════════════════════════════════${NC}"
    echo -e "${YELLOW}🔄 Files changed at $(date '+%H:%M:%S')${NC}"
    echo -e "${BLUE}══════════════════════════════════════${NC}"
    echo ""

    # Run quick validation
    echo -e "${YELLOW}🔍 Running quick validation...${NC}"
    "$REPO_ROOT/run.sh" check --quick || true

    echo ""

    # Run tests (stop on first failure for speed)
    echo -e "${YELLOW}🧪 Running tests...${NC}"
    if "$PYTHON_RUNTIME" -m pytest "$TEST_PATTERN" -v --tb=short -x --maxfail=3; then
        echo ""
        echo -e "${GREEN}✅ All checks passed!${NC}"
    else
        echo ""
        echo -e "${RED}❌ Tests failed${NC}"
    fi

    echo ""
    echo -e "${BLUE}══════════════════════════════════════${NC}"
    echo -e "${BLUE}👀 Waiting for changes...${NC}"
    echo -e "${BLUE}══════════════════════════════════════${NC}"
done
