#!/bin/bash
# Test suite for should_use_pr.sh
# Validates workflow decision logic with various file combinations
#
# Usage: ./scripts/test_should_use_pr.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$PROJECT_ROOT/.test_should_use_pr_$$"
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

cleanup() {
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

log_test() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}TEST: $1${NC}"
    TESTS_RUN=$((TESTS_RUN + 1))
}

log_pass() {
    echo -e "${GREEN}✓ PASS: $1${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

log_fail() {
    echo -e "${RED}✗ FAIL: $1${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

# Create test repo
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"
git init --quiet
git config user.name "Test"
git config user.email "test@test.com"

# Create initial commit (needed for git reset to work)
echo "# Test Repo" > README.md
git add README.md
git commit -m "Initial commit" --quiet

# Copy the script
cp "$PROJECT_ROOT/scripts/should_use_pr.sh" "$TEST_DIR/"
chmod +x should_use_pr.sh

# Create dummy directory structure
mkdir -p docs Python/structural_lib Python/tests scripts VBA Excel .github/workflows

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Testing: should_use_pr.sh workflow decisions${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# TEST 1: Documentation only (should recommend direct commit)
log_test "Documentation only → Direct commit"
echo "test" > docs/README.md
git add docs/README.md
if ./should_use_pr.sh >/dev/null 2>&1; then
    log_pass "Docs only: Direct commit (exit 0)"
else
    log_fail "Docs only: Should allow direct commit"
fi
git reset HEAD --quiet
rm docs/README.md

# TEST 2: Tests only (should recommend direct commit)
log_test "Tests only → Direct commit"
echo "test" > Python/tests/test_example.py
git add Python/tests/test_example.py
if ./should_use_pr.sh >/dev/null 2>&1; then
    log_pass "Tests only: Direct commit (exit 0)"
else
    log_fail "Tests only: Should allow direct commit"
fi
git reset HEAD --quiet
rm Python/tests/test_example.py

# TEST 3: Scripts only (should recommend direct commit)
log_test "Scripts only → Direct commit"
echo "#!/bin/bash" > scripts/helper.sh
git add scripts/helper.sh
if ./should_use_pr.sh >/dev/null 2>&1; then
    log_pass "Scripts only: Direct commit (exit 0)"
else
    log_fail "Scripts only: Should allow direct commit"
fi
git reset HEAD --quiet
rm scripts/helper.sh

# TEST 4: Docs + Scripts (should recommend direct commit)
log_test "Docs + Scripts → Direct commit"
echo "test" > docs/README.md
echo "#!/bin/bash" > scripts/helper.sh
git add docs/README.md scripts/helper.sh
if ./should_use_pr.sh >/dev/null 2>&1; then
    log_pass "Docs + Scripts: Direct commit (exit 0)"
else
    log_fail "Docs + Scripts: Should allow direct commit"
fi
git reset HEAD --quiet
rm docs/README.md scripts/helper.sh

# TEST 5: Production code (should require PR)
log_test "Production code → Pull Request"
echo "def foo(): pass" > Python/structural_lib/flexure.py
git add Python/structural_lib/flexure.py
if ! ./should_use_pr.sh >/dev/null 2>&1; then
    log_pass "Production code: Requires PR (exit 1)"
else
    log_fail "Production code: Should require PR"
fi
git reset HEAD --quiet
rm Python/structural_lib/flexure.py

# TEST 6: VBA code (should require PR)
log_test "VBA code → Pull Request"
echo "Sub Test()" > VBA/Module1.bas
git add VBA/Module1.bas
if ! ./should_use_pr.sh >/dev/null 2>&1; then
    log_pass "VBA code: Requires PR (exit 1)"
else
    log_fail "VBA code: Should require PR"
fi
git reset HEAD --quiet
rm VBA/Module1.bas

# TEST 7: CI workflow (should require PR)
log_test "CI workflow → Pull Request"
echo "name: test" > .github/workflows/test.yml
git add .github/workflows/test.yml
if ! ./should_use_pr.sh >/dev/null 2>&1; then
    log_pass "CI workflow: Requires PR (exit 1)"
else
    log_fail "CI workflow: Should require PR"
fi
git reset HEAD --quiet
rm .github/workflows/test.yml

# TEST 8: Dependencies (should require PR)
log_test "Dependencies → Pull Request"
echo "pytest==7.0" > Python/requirements.txt
git add Python/requirements.txt
if ! ./should_use_pr.sh >/dev/null 2>&1; then
    log_pass "Dependencies: Requires PR (exit 1)"
else
    log_fail "Dependencies: Should require PR"
fi
git reset HEAD --quiet
rm Python/requirements.txt

# TEST 9: Mixed (docs + production code) (should require PR)
log_test "Mixed (docs + code) → Pull Request"
echo "test" > docs/README.md
echo "def foo(): pass" > Python/structural_lib/flexure.py
git add docs/README.md Python/structural_lib/flexure.py
if ! ./should_use_pr.sh >/dev/null 2>&1; then
    log_pass "Mixed changes: Requires PR (exit 1)"
else
    log_fail "Mixed changes: Should require PR"
fi
git reset HEAD --quiet
rm docs/README.md Python/structural_lib/flexure.py

# TEST 10: copilot-instructions.md (should allow direct commit)
log_test "copilot-instructions.md → Direct commit"
echo "test" > .github/copilot-instructions.md
git add .github/copilot-instructions.md
if ./should_use_pr.sh >/dev/null 2>&1; then
    log_pass "copilot-instructions: Direct commit (exit 0)"
else
    log_fail "copilot-instructions: Should allow direct commit"
fi
git reset HEAD --quiet
rm .github/copilot-instructions.md

# TEST 11: Excel file (should require PR)
log_test "Excel file → Pull Request"
echo "test" > Excel/test.xlsm
git add Excel/test.xlsm
if ! ./should_use_pr.sh >/dev/null 2>&1; then
    log_pass "Excel file: Requires PR (exit 1)"
else
    log_fail "Excel file: Should require PR"
fi
git reset HEAD --quiet
rm Excel/test.xlsm

# TEST 12: pyproject.toml (should require PR)
log_test "pyproject.toml → Pull Request"
echo "test" > Python/pyproject.toml
git add Python/pyproject.toml
if ! ./should_use_pr.sh >/dev/null 2>&1; then
    log_pass "pyproject.toml: Requires PR (exit 1)"
else
    log_fail "pyproject.toml: Should require PR"
fi
git reset HEAD --quiet
rm Python/pyproject.toml

# TEST 13: Tests + Production code (should require PR)
log_test "Tests + Production → Pull Request"
echo "test" > Python/tests/test_example.py
echo "def foo(): pass" > Python/structural_lib/flexure.py
git add Python/tests/test_example.py Python/structural_lib/flexure.py
if ! ./should_use_pr.sh >/dev/null 2>&1; then
    log_pass "Tests + Production: Requires PR (exit 1)"
else
    log_fail "Tests + Production: Should require PR"
fi
git reset HEAD --quiet
rm Python/tests/test_example.py Python/structural_lib/flexure.py

# Summary
cd "$PROJECT_ROOT"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}TEST SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Tests run:    ${BLUE}$TESTS_RUN${NC}"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}  should_use_pr.sh is ready for production use${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo -e "${RED}  Fix issues before using in production${NC}"
    echo ""
    exit 1
fi
