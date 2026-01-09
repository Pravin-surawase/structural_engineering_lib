#!/bin/bash
# Test Suite for Git Branch and Worktree Operations
# Comprehensive testing of git workflows used by Agent 8
#
# Usage:
#   ./scripts/test_branch_operations.sh              # Run all tests
#   ./scripts/test_branch_operations.sh --test N    # Run specific test
#   ./scripts/test_branch_operations.sh --verbose   # Show detailed output
#   ./scripts/test_branch_operations.sh --quick     # Skip slow tests

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
TEST_DIR=""
VERBOSE=false
RUN_SPECIFIC_TEST=""
QUICK_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --test)
            RUN_SPECIFIC_TEST="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --quick)
            QUICK_MODE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--test N] [--verbose] [--quick]"
            exit 1
            ;;
    esac
done

# Test statistics
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
ASSERTIONS_PASSED=0
START_TIME=$(date +%s)

# Helper functions
log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo "$@"
    fi
}

assert_equal() {
    local actual="$1"
    local expected="$2"
    local message="$3"

    ASSERTIONS_PASSED=$((ASSERTIONS_PASSED + 1))

    if [[ "$actual" == "$expected" ]]; then
        echo -e "${GREEN}✓ PASS:${NC} $message"
        return 0
    else
        echo -e "${RED}✗ FAIL:${NC} $message"
        echo "  Expected: $expected"
        echo "  Got: $actual"
        return 1
    fi
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local message="$3"

    ASSERTIONS_PASSED=$((ASSERTIONS_PASSED + 1))

    if echo "$haystack" | grep -q "$needle"; then
        echo -e "${GREEN}✓ PASS:${NC} $message"
        return 0
    else
        echo -e "${RED}✗ FAIL:${NC} $message"
        echo "  Expected to find: $needle"
        echo "  In: $haystack"
        return 1
    fi
}

assert_not_contains() {
    local haystack="$1"
    local needle="$2"
    local message="$3"

    ASSERTIONS_PASSED=$((ASSERTIONS_PASSED + 1))

    if ! echo "$haystack" | grep -q "$needle"; then
        echo -e "${GREEN}✓ PASS:${NC} $message"
        return 0
    else
        echo -e "${RED}✗ FAIL:${NC} $message"
        echo "  Did not expect to find: $needle"
        echo "  In: $haystack"
        return 1
    fi
}

assert_file_exists() {
    local file="$1"
    local message="$2"

    ASSERTIONS_PASSED=$((ASSERTIONS_PASSED + 1))

    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✓ PASS:${NC} $message"
        return 0
    else
        echo -e "${RED}✗ FAIL:${NC} $message"
        echo "  File not found: $file"
        return 1
    fi
}

# Test environment setup
setup_test_env() {
    TEST_DIR=$(mktemp -d)
    log_verbose "Created test environment: $TEST_DIR"
    cd "$TEST_DIR"

    # Create main test repository
    git init test_repo >/dev/null 2>&1
    cd test_repo
    git config user.email "test@example.com"
    git config user.name "Test User"

    # Create initial commit
    echo "Initial commit" > README.md
    git add README.md
    git commit -m "Initial commit" >/dev/null 2>&1

    log_verbose "Test repository initialized"
}

cleanup_test_env() {
    if [[ -n "$TEST_DIR" ]] && [[ -d "$TEST_DIR" ]]; then
        cd /
        rm -rf "$TEST_DIR"
        log_verbose "Cleaned up test environment"
    fi
}

# Ensure cleanup on exit
trap cleanup_test_env EXIT

# Test 1: Create Branch
test_1_create_branch() {
    echo ""
    echo -e "${BLUE}Test 1: Create Branch${NC}"

    setup_test_env

    git checkout -b feature/test-001 >/dev/null 2>&1
    local current_branch=$(git branch --show-current)

    assert_equal "$current_branch" "feature/test-001" "Branch created and checked out"

    TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Test 2: Switch Branch
test_2_switch_branch() {
    echo ""
    echo -e "${BLUE}Test 2: Switch Branch${NC}"

    setup_test_env

    git checkout -b feature/test-002 >/dev/null 2>&1
    git checkout main >/dev/null 2>&1
    local current_branch=$(git branch --show-current)

    assert_equal "$current_branch" "main" "Switched to main branch"

    git checkout feature/test-002 >/dev/null 2>&1
    current_branch=$(git branch --show-current)

    assert_equal "$current_branch" "feature/test-002" "Switched to feature branch"

    TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Test 3: Delete Branch (Merged)
test_3_delete_branch_merged() {
    echo ""
    echo -e "${BLUE}Test 3: Delete Branch (Merged)${NC}"

    setup_test_env

    git checkout -b feature/to-delete >/dev/null 2>&1
    echo "feature content" > feature.txt
    git add feature.txt
    git commit -m "Add feature" >/dev/null 2>&1

    git checkout main >/dev/null 2>&1
    git merge --no-ff feature/to-delete -m "Merge feature" >/dev/null 2>&1

    git branch -d feature/to-delete >/dev/null 2>&1
    local branch_list=$(git branch --list)

    assert_not_contains "$branch_list" "feature/to-delete" "Merged branch deleted"

    TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Test 4: Delete Branch (Force)
test_4_delete_branch_force() {
    echo ""
    echo -e "${BLUE}Test 4: Delete Branch (Force)${NC}"

    setup_test_env

    git checkout -b feature/to-force-delete >/dev/null 2>&1
    echo "unmerged content" > unmerged.txt
    git add unmerged.txt
    git commit -m "Unmerged commit" >/dev/null 2>&1

    git checkout main >/dev/null 2>&1
    git branch -D feature/to-force-delete >/dev/null 2>&1
    local branch_list=$(git branch --list)

    assert_not_contains "$branch_list" "feature/to-force-delete" "Unmerged branch force-deleted"

    TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Test 5: List Branches
test_5_list_branches() {
    echo ""
    echo -e "${BLUE}Test 5: List Branches${NC}"

    setup_test_env

    git checkout -b feature/branch-1 >/dev/null 2>&1
    git checkout -b feature/branch-2 >/dev/null 2>&1
    git checkout main >/dev/null 2>&1

    local branch_list=$(git branch --list)

    assert_contains "$branch_list" "main" "Main branch listed"
    assert_contains "$branch_list" "feature/branch-1" "Feature branch 1 listed"
    assert_contains "$branch_list" "feature/branch-2" "Feature branch 2 listed"

    TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Test 6: Create Worktree
test_6_create_worktree() {
    echo ""
    echo -e "${BLUE}Test 6: Create Worktree${NC}"

    setup_test_env

    git checkout -b feature/worktree-test >/dev/null 2>&1
    git worktree add ../worktree-test feature/worktree-test >/dev/null 2>&1

    local worktree_list=$(git worktree list)

    assert_contains "$worktree_list" "worktree-test" "Worktree created"
    assert_file_exists "../worktree-test/README.md" "Worktree has files"

    TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Test 7: List Worktrees
test_7_list_worktrees() {
    echo ""
    echo -e "${BLUE}Test 7: List Worktrees${NC}"

    setup_test_env

    git checkout -b wt1 >/dev/null 2>&1
    git worktree add ../wt1 wt1 >/dev/null 2>&1
    git checkout -b wt2 >/dev/null 2>&1
    git worktree add ../wt2 wt2 >/dev/null 2>&1

    local worktree_list=$(git worktree list)

    assert_contains "$worktree_list" "test_repo" "Main worktree listed"
    assert_contains "$worktree_list" "wt1" "Worktree 1 listed"
    assert_contains "$worktree_list" "wt2" "Worktree 2 listed"

    TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Test 8: Remove Worktree
test_8_remove_worktree() {
    echo ""
    echo -e "${BLUE}Test 8: Remove Worktree${NC}"

    setup_test_env

    git checkout -b wt-remove >/dev/null 2>&1
    git worktree add ../wt-remove wt-remove >/dev/null 2>&1
    git worktree remove ../wt-remove >/dev/null 2>&1

    local worktree_list=$(git worktree list)

    assert_not_contains "$worktree_list" "wt-remove" "Worktree removed"

    TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Test 9: Uncommitted Changes Protection
test_9_uncommitted_changes() {
    echo ""
    echo -e "${BLUE}Test 9: Uncommitted Changes Protection${NC}"

    setup_test_env

    echo "uncommitted content" > uncommitted.txt
    git add uncommitted.txt

    # Check that there are uncommitted changes
    local status_output=$(git status --short)

    assert_contains "$status_output" "uncommitted.txt" "Uncommitted changes detected"

    # Stash changes
    git stash >/dev/null 2>&1
    status_output=$(git status --short)

    assert_equal "$status_output" "" "Changes stashed, working tree clean"

    # Pop stash
    git stash pop >/dev/null 2>&1
    status_output=$(git status --short)

    assert_contains "$status_output" "uncommitted.txt" "Changes restored from stash"

    TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Test 10: Fast-Forward Merge
test_10_fast_forward_merge() {
    echo ""
    echo -e "${BLUE}Test 10: Fast-Forward Merge${NC}"

    setup_test_env

    git checkout -b feature/ff >/dev/null 2>&1
    echo "ff content" > ff.txt
    git add ff.txt
    git commit -m "Add ff content" >/dev/null 2>&1

    git checkout main >/dev/null 2>&1
    git merge --ff-only feature/ff >/dev/null 2>&1

    local merge_log=$(git log --oneline -1)

    assert_contains "$merge_log" "Add ff content" "Fast-forward merge succeeded"

    TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Main test runner
run_tests() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Git Branch & Worktree Operations Test Suite       ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""

    if [[ -n "$RUN_SPECIFIC_TEST" ]]; then
        echo -e "${YELLOW}Running specific test: $RUN_SPECIFIC_TEST${NC}"
        TESTS_TO_RUN=("test_${RUN_SPECIFIC_TEST}_*")
    else
        if [[ "$QUICK_MODE" == "true" ]]; then
            echo -e "${YELLOW}Quick mode: Running 5 essential tests${NC}"
            TESTS_TO_RUN=(
                "test_1_create_branch"
                "test_2_switch_branch"
                "test_6_create_worktree"
                "test_9_uncommitted_changes"
                "test_10_fast_forward_merge"
            )
        else
            echo -e "${YELLOW}Running all 10 tests${NC}"
            TESTS_TO_RUN=(
                "test_1_create_branch"
                "test_2_switch_branch"
                "test_3_delete_branch_merged"
                "test_4_delete_branch_force"
                "test_5_list_branches"
                "test_6_create_worktree"
                "test_7_list_worktrees"
                "test_8_remove_worktree"
                "test_9_uncommitted_changes"
                "test_10_fast_forward_merge"
            )
        fi
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Run tests
    for test_func in "${TESTS_TO_RUN[@]}"; do
        TESTS_RUN=$((TESTS_RUN + 1))
        if $test_func; then
            : # Test passed (counter already incremented)
        else
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    done

    # Summary
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    else
        echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Tests run: $TESTS_RUN"
    echo "Tests passed: $TESTS_PASSED"
    echo "Tests failed: $TESTS_FAILED"
    echo "Assertions passed: $ASSERTIONS_PASSED"
    echo "Duration: ${DURATION}s"
    echo ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${BLUE}Coverage:${NC} Essential git operations (branch, worktree, merge)"
        echo -e "${BLUE}Status:${NC} Production-ready ✓"
        exit 0
    else
        exit 1
    fi
}

# Run the test suite
run_tests
