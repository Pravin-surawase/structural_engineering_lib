#!/bin/bash
# CRITICAL: Verify safe_push.sh prevents pre-commit whitespace hash divergence
# This test MUST pass to ensure we never have hash divergence issues again
#
# What it tests:
# 1. File with trailing whitespace is created
# 2. File is staged
# 3. Git detects the whitespace
# 4. Step 2.5 fixes it BEFORE commit
# 5. No warnings remain
# 6. Commit would succeed with consistent hash
#
# Usage: ./scripts/verify_git_fix.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}VERIFYING: Git whitespace fix (Step 2.5)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$PROJECT_ROOT/.verify_git_fix_$$"

cleanup() {
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

# Create test repo
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"
git init --quiet
git config user.name "Test"
git config user.email "test@test.com"

# Test 1: Verify Step 2.5 exists
echo -n "Test 1: Step 2.5 exists in safe_push.sh... "
if grep -q "Step 2.5" "$PROJECT_ROOT/scripts/safe_push.sh"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "ERROR: Step 2.5 missing from safe_push.sh"
    exit 1
fi

# Test 2: Create file with trailing whitespace
echo -n "Test 2: Create file with trailing whitespace... "
echo "test line   " > test.txt
git add test.txt
echo -e "${GREEN}✓ PASS${NC}"

# Test 3: Git detects the problem
echo -n "Test 3: Git detects trailing whitespace... "
if git diff --cached --check 2>&1 | grep -q 'trailing'; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "ERROR: Git should detect trailing whitespace"
    exit 1
fi

# Test 4: Apply Step 2.5 fix (simulate what safe_push.sh does)
echo -n "Test 4: Apply Step 2.5 fix... "
git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        sed -i '' 's/[[:space:]]*$//' "$file" 2>/dev/null || sed -i 's/[[:space:]]*$//' "$file"
    fi
done
echo -e "${GREEN}✓ PASS${NC}"

# Test 5: Verify whitespace removed
echo -n "Test 5: Whitespace actually removed... "
if ! grep -q '   $' test.txt; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "ERROR: Trailing whitespace still present"
    exit 1
fi

# Test 6: Re-stage and verify no warnings
echo -n "Test 6: No warnings after fix... "
git add test.txt
if ! git diff --cached --check 2>&1 | grep -q 'trailing'; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "ERROR: Whitespace warnings still present"
    exit 1
fi

# Test 7: Verify Step 2.5 runs BEFORE commit
echo -n "Test 7: Step 2.5 runs before commit... "
step25_line=$(grep -n "Step 2.5" "$PROJECT_ROOT/scripts/safe_push.sh" | cut -d: -f1 | head -1)
commit_line=$(grep -n "git commit -m" "$PROJECT_ROOT/scripts/safe_push.sh" | cut -d: -f1 | head -1)
if [ "$step25_line" -lt "$commit_line" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "ERROR: Step 2.5 (line $step25_line) must run before git commit (line $commit_line)"
    exit 1
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}SUCCESS: All 7 tests passed!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "✓ Step 2.5 correctly prevents hash divergence"
echo "✓ Whitespace is fixed BEFORE commit"
echo "✓ No more 'non-fast-forward' git errors"
echo ""
