#!/bin/bash
# Integration test for agent automation system
# Tests all workflow scripts work together

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "╔════════════════════════════════════════════════════════╗"
echo "║    Agent Automation System Integration Test           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

TESTS_PASSED=0
TESTS_FAILED=0

test_result() {
    if [[ $1 -eq 0 ]]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test 1: Scripts exist
echo "[1/10] Checking script files exist..."
MISSING=0
for script in agent_setup.sh agent_preflight.sh worktree_manager.sh; do
    if [[ ! -f "scripts/$script" ]]; then
        MISSING=1
        break
    fi
done
test_result $MISSING "All automation scripts exist"

# Test 2: Scripts are executable
echo "[2/10] Checking script permissions..."
NOT_EXEC=0
for script in agent_setup.sh agent_preflight.sh worktree_manager.sh; do
    if [[ ! -x "scripts/$script" ]]; then
        NOT_EXEC=1
        break
    fi
done
test_result $NOT_EXEC "All scripts are executable"

# Test 3: agent_setup.sh runs
echo "[3/10] Testing agent_setup.sh..."
./scripts/agent_setup.sh --quick >/dev/null 2>&1
test_result $? "agent_setup.sh executes successfully"

# Test 4: agent_preflight.sh runs
echo "[4/10] Testing agent_preflight.sh..."
./scripts/agent_preflight.sh --quick >/dev/null 2>&1
EXIT_CODE=$?
if [[ $EXIT_CODE -eq 0 ]] || [[ $EXIT_CODE -eq 1 ]]; then
    # Both success (0) and warnings (1) are acceptable
    test_result 0 "agent_preflight.sh executes successfully"
else
    test_result 1 "agent_preflight.sh executes successfully"
fi

# Test 5: worktree_manager.sh list runs
echo "[5/10] Testing worktree_manager.sh list..."
./scripts/worktree_manager.sh list >/dev/null 2>&1
test_result $? "worktree_manager.sh list works"

# Test 6: worktree_manager.sh help runs
echo "[6/10] Testing worktree_manager.sh help..."
./scripts/worktree_manager.sh help >/dev/null 2>&1
test_result $? "worktree_manager.sh help works"

# Test 7: Documentation files exist
echo "[7/10] Checking documentation files..."
DOCS_MISSING=0
for doc in AGENT_WORKFLOW_MASTER_GUIDE.md AGENT_QUICK_REFERENCE.md; do
    if [[ ! -f "docs/$doc" ]]; then
        DOCS_MISSING=1
        break
    fi
done
test_result $DOCS_MISSING "All documentation files exist"

# Test 8: Existing workflow scripts still work
echo "[8/10] Testing existing ai_commit.sh..."
if [[ -x "scripts/ai_commit.sh" ]]; then
    test_result 0 "ai_commit.sh still exists and is executable"
else
    test_result 1 "ai_commit.sh still exists and is executable"
fi

# Test 9: Existing safe_push.sh still works
echo "[9/10] Testing existing safe_push.sh..."
if [[ -x "scripts/safe_push.sh" ]]; then
    test_result 0 "safe_push.sh still exists and is executable"
else
    test_result 1 "safe_push.sh still exists and is executable"
fi

# Test 10: Integration - scripts can find each other
echo "[10/10] Testing script integration..."
# agent_setup.sh should find other scripts
if ./scripts/agent_setup.sh --quick 2>&1 | grep -q "All workflow scripts present"; then
    test_result 0 "Scripts can find each other"
else
    test_result 1 "Scripts can find each other"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Results:"
echo "  ✓ Passed: $TESTS_PASSED"
echo "  ✗ Failed: $TESTS_FAILED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo ""
    echo "The agent automation system is ready for production use!"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review the failures above before deploying."
    exit 1
fi
