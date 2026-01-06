#!/bin/bash
# Helper script: Should this change use a Pull Request?
# Analyzes staged files and recommends workflow based on:
# - File type (production code vs docs/tests)
# - Change size (lines added/removed)
# - File count (multiple files = higher impact)
# - Change complexity (new files, renames, etc.)
#
# Philosophy: PR-first for substantial changes, direct commit for minor edits only
#
# Usage:
#   ./scripts/should_use_pr.sh
#   ./scripts/should_use_pr.sh --explain

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

EXPLAIN=false
if [[ "$1" == "--explain" ]]; then
    EXPLAIN=true
fi

# Get staged files
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || echo "")

if [[ -z "$STAGED_FILES" ]]; then
    echo -e "${YELLOW}No staged files. Stage changes first with:${NC}"
    echo -e "  ${BLUE}git add <files>${NC}"
    exit 1
fi

# Calculate change metrics
FILE_COUNT=$(echo "$STAGED_FILES" | wc -l | tr -d ' ')
LINES_CHANGED=$(git diff --cached --numstat | awk '{sum+=$1+$2} END {print sum+0}')
NEW_FILES=$(git diff --cached --diff-filter=A --name-only | wc -l | tr -d ' ')
RENAMED_FILES=$(git diff --cached --diff-filter=R --name-only | wc -l | tr -d ' ')

# Thresholds for "minor" changes
MINOR_LINES_THRESHOLD=50       # <50 lines = potentially minor
MINOR_FILES_THRESHOLD=2        # <2 files = potentially minor
SUBSTANTIAL_LINES=150          # >150 lines = definitely substantial
MAJOR_LINES=500                # >500 lines = major change

# Analyze files
DOCS_ONLY=true
TESTS_ONLY=true
SCRIPTS_ONLY=true
DOCS_OR_SCRIPTS=true
HAS_PRODUCTION_CODE=false
HAS_VBA_CODE=false
HAS_CI_CODE=false
HAS_DEPS=false

while IFS= read -r file; do
    # Check if file matches production code
    if [[ "$file" =~ ^Python/structural_lib/.*\.py$ ]]; then
        HAS_PRODUCTION_CODE=true
        DOCS_ONLY=false
        TESTS_ONLY=false
        SCRIPTS_ONLY=false
        DOCS_OR_SCRIPTS=false
    fi

    # Check if file is VBA
    if [[ "$file" =~ ^VBA/.*\.(bas|cls|frm)$ ]] || [[ "$file" =~ ^Excel/.*\.xlsm$ ]]; then
        HAS_VBA_CODE=true
        DOCS_ONLY=false
        TESTS_ONLY=false
        SCRIPTS_ONLY=false
        DOCS_OR_SCRIPTS=false
    fi

    # Check if file is CI
    if [[ "$file" =~ ^\.github/workflows/.*\.yml$ ]]; then
        HAS_CI_CODE=true
        DOCS_ONLY=false
        TESTS_ONLY=false
        SCRIPTS_ONLY=false
        DOCS_OR_SCRIPTS=false
    fi

    # Check if file is dependency
    if [[ "$file" =~ ^Python/(pyproject\.toml|requirements.*\.txt)$ ]]; then
        HAS_DEPS=true
        DOCS_ONLY=false
        TESTS_ONLY=false
        SCRIPTS_ONLY=false
        DOCS_OR_SCRIPTS=false
    fi

    # Check if NOT docs
    if [[ ! "$file" =~ ^docs/ ]]; then
        DOCS_ONLY=false
    fi

    # Check if NOT tests
    if [[ ! "$file" =~ ^Python/tests/ ]]; then
        TESTS_ONLY=false
    fi

    # Check if NOT scripts
    if [[ ! "$file" =~ ^scripts/ ]]; then
        SCRIPTS_ONLY=false
    fi

    # Check if NOT docs OR scripts (combined is OK)
    if [[ ! "$file" =~ ^docs/ ]] && [[ ! "$file" =~ ^scripts/ ]] && [[ ! "$file" =~ ^\.github/copilot-instructions\.md$ ]]; then
        DOCS_OR_SCRIPTS=false
    fi
done <<< "$STAGED_FILES"

# Make recommendation
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Git Workflow Recommendation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}Staged files:${NC}"
echo "$STAGED_FILES" | sed 's/^/  /'
echo ""

# Decision logic
if [[ "$DOCS_ONLY" == "true" ]]; then
    echo -e "${GREEN}✅ RECOMMENDATION: Direct commit${NC}"
    echo -e "${GREEN}   (Documentation only)${NC}"
    if [[ "$EXPLAIN" == "true" ]]; then
        echo ""
        echo "Reasoning:"
        echo "- Only documentation files changed"
        echo "- Low risk (no production code)"
        echo "- Fast iteration preferred"
    fi
    echo ""
    echo "Use: ./scripts/safe_push.sh \"docs: <message>\""
    exit 0
fi

if [[ "$TESTS_ONLY" == "true" ]]; then
    echo -e "${GREEN}✅ RECOMMENDATION: Direct commit${NC}"
    echo -e "${GREEN}   (Test files only)${NC}"
    if [[ "$EXPLAIN" == "true" ]]; then
        echo ""
        echo "Reasoning:"
        echo "- Only test files changed"
        echo "- No production code affected"
        echo "- Tests validate themselves"
    fi
    echo ""
    echo "Use: ./scripts/safe_push.sh \"test: <message>\""
    exit 0
fi

if [[ "$SCRIPTS_ONLY" == "true" ]]; then
    echo -e "${GREEN}✅ RECOMMENDATION: Direct commit${NC}"
    echo -e "${GREEN}   (Scripts only)${NC}"
    if [[ "$EXPLAIN" == "true" ]]; then
        echo ""
        echo "Reasoning:"
        echo "- Only scripts/ directory changed"
        echo "- Not user-facing production code"
        echo "- Quick iteration needed for tooling"
    fi
    echo ""
    echo "Use: ./scripts/safe_push.sh \"chore: <message>\""
    exit 0
fi

if [[ "$DOCS_OR_SCRIPTS" == "true" ]]; then
    echo -e "${GREEN}✅ RECOMMENDATION: Direct commit${NC}"
    echo -e "${GREEN}   (Documentation and/or scripts only)${NC}"
    if [[ "$EXPLAIN" == "true" ]]; then
        echo ""
        echo "Reasoning:"
        echo "- Only docs/ and scripts/ changed"
        echo "- No production code affected"
        echo "- Low risk combination"
    fi
    echo ""
    echo "Use: ./scripts/safe_push.sh \"docs: <message>\""
    exit 0
fi

# High-risk changes need PR
if [[ "$HAS_PRODUCTION_CODE" == "true" ]]; then
    echo -e "${RED}🔀 RECOMMENDATION: Pull Request${NC}"
    echo -e "${RED}   (Production code changed)${NC}"
    if [[ "$EXPLAIN" == "true" ]]; then
        echo ""
        echo "Reasoning:"
        echo "- Python/structural_lib/ files changed"
        echo "- User-facing production code"
        echo "- CI validation + audit trail needed"
    fi
    echo ""
    echo "Use: ./scripts/create_task_pr.sh TASK-XXX \"description\""
    exit 1
fi

if [[ "$HAS_VBA_CODE" == "true" ]]; then
    echo -e "${RED}🔀 RECOMMENDATION: Pull Request${NC}"
    echo -e "${RED}   (VBA code changed)${NC}"
    if [[ "$EXPLAIN" == "true" ]]; then
        echo ""
        echo "Reasoning:"
        echo "- VBA/*.bas or Excel/*.xlsm changed"
        echo "- Excel user-facing code"
        echo "- Requires careful review"
    fi
    echo ""
    echo "Use: ./scripts/create_task_pr.sh TASK-XXX \"description\""
    exit 1
fi

if [[ "$HAS_CI_CODE" == "true" ]]; then
    echo -e "${RED}🔀 RECOMMENDATION: Pull Request${NC}"
    echo -e "${RED}   (CI workflow changed)${NC}"
    if [[ "$EXPLAIN" == "true" ]]; then
        echo ""
        echo "Reasoning:"
        echo "- .github/workflows/*.yml changed"
        echo "- Affects all future commits"
        echo "- Must test before merge"
    fi
    echo ""
    echo "Use: ./scripts/create_task_pr.sh TASK-XXX \"description\""
    exit 1
fi

if [[ "$HAS_DEPS" == "true" ]]; then
    echo -e "${RED}🔀 RECOMMENDATION: Pull Request${NC}"
    echo -e "${RED}   (Dependencies changed)${NC}"
    if [[ "$EXPLAIN" == "true" ]]; then
        echo ""
        echo "Reasoning:"
        echo "- pyproject.toml or requirements.txt changed"
        echo "- Affects all environments"
        echo "- Test in CI before merge"
    fi
    echo ""
    echo "Use: ./scripts/create_task_pr.sh TASK-XXX \"description\""
    exit 1
fi

# Mixed or unclear
echo -e "${YELLOW}⚠️  RECOMMENDATION: Pull Request (mixed changes)${NC}"
if [[ "$EXPLAIN" == "true" ]]; then
    echo ""
    echo "Reasoning:"
    echo "- Multiple file types changed"
    echo "- Cannot determine risk level"
    echo "- Safer to use PR workflow"
fi
echo ""
echo "Use: ./scripts/create_task_pr.sh TASK-XXX \"description\""
exit 1
