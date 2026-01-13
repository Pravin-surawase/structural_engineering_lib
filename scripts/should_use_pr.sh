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
#   ./scripts/should_use_pr.sh --staged-only
#   ./scripts/should_use_pr.sh --include-untracked

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

EXPLAIN=false
STAGED_ONLY=false
INCLUDE_UNTRACKED=false
for arg in "$@"; do
    if [[ "$arg" == "--explain" ]]; then
        EXPLAIN=true
    elif [[ "$arg" == "--staged-only" ]]; then
        STAGED_ONLY=true
    elif [[ "$arg" == "--include-untracked" ]]; then
        INCLUDE_UNTRACKED=true
    fi
done

# Collect files (staged, unstaged, untracked)
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || echo "")
UNSTAGED_FILES=$(git diff --name-only 2>/dev/null || echo "")
UNTRACKED_FILES=""
if [[ "$INCLUDE_UNTRACKED" == "true" ]]; then
    UNTRACKED_FILES=$(git ls-files --others --exclude-standard 2>/dev/null || echo "")
fi

if [[ "$STAGED_ONLY" == "true" ]]; then
    FILES="$STAGED_FILES"
else
    FILES=$(printf "%s\n%s\n%s\n" "$STAGED_FILES" "$UNSTAGED_FILES" "$UNTRACKED_FILES" | sed '/^$/d' | sort -u)
fi

if [[ -z "$FILES" ]]; then
    echo -e "${YELLOW}No changes detected.${NC}"
    echo -e "  ${BLUE}Update files first, then rerun this script.${NC}"
    exit 1
fi

# Calculate change metrics
FILE_COUNT=$(echo "$FILES" | wc -l | tr -d ' ')
if [[ "$STAGED_ONLY" == "true" ]]; then
    LINES_CHANGED=$(git diff --cached --numstat | awk '{sum+=$1+$2} END {print sum+0}')
    NEW_FILES=$(git diff --cached --diff-filter=A --name-only | wc -l | tr -d ' ')
    RENAMED_FILES=$(git diff --cached --diff-filter=R --name-only | wc -l | tr -d ' ')
else
    LINES_CHANGED=$(git diff --numstat HEAD | awk '{sum+=$1+$2} END {print sum+0}')
    NEW_FILES=$(git diff --diff-filter=A --name-only HEAD | wc -l | tr -d ' ')
    RENAMED_FILES=$(git diff --diff-filter=R --name-only HEAD | wc -l | tr -d ' ')
    if [[ "$INCLUDE_UNTRACKED" == "true" ]]; then
        UNTRACKED_COUNT=$(echo "$UNTRACKED_FILES" | sed '/^$/d' | wc -l | tr -d ' ')
        NEW_FILES=$((NEW_FILES + UNTRACKED_COUNT))
    fi
fi

# Thresholds for "minor" changes
MINOR_LINES_THRESHOLD=50       # <50 lines = potentially minor
MINOR_FILES_THRESHOLD=2        # <2 files = potentially minor
SUBSTANTIAL_LINES=150          # >150 lines = definitely substantial
MAJOR_LINES=500                # >500 lines = major change
STREAMLIT_MINOR_THRESHOLD=20   # <20 lines for streamlit = minor (stricter)
# Solo-dev thresholds (no reviewers available)
DOCS_SCRIPTS_MINOR_THRESHOLD=150  # <150 lines for docs+scripts (CI validates)

# Analyze files
DOCS_ONLY=true
TESTS_ONLY=true
SCRIPTS_ONLY=true
DOCS_OR_SCRIPTS=true
HAS_PRODUCTION_CODE=false
HAS_VBA_CODE=false
HAS_CI_CODE=false
HAS_DEPS=false
HAS_STREAMLIT_CODE=false
STREAMLIT_ONLY=true

is_docs_like() {
    local file="$1"
    if [[ "$file" =~ ^docs/ ]]; then
        return 0
    fi
    if [[ "$file" =~ ^metrics/ ]]; then
        return 0
    fi
    if [[ "$file" =~ \.md$ ]]; then
        return 0
    fi
    if [[ "$file" =~ \.ipynb$ ]]; then
        return 0
    fi
    if [[ "$file" =~ \.cff$ ]]; then
        return 0
    fi
    if [[ "$file" =~ \.txt$ ]]; then
        return 0
    fi
    if [[ "$file" =~ ^(LICENSE|NOTICE|COPYING)$ ]]; then
        return 0
    fi
    return 1
}

while IFS= read -r file; do
    # Check if file matches production code (core library)
    if [[ "$file" =~ ^Python/structural_lib/.*\.py$ ]]; then
        HAS_PRODUCTION_CODE=true
        DOCS_ONLY=false
        TESTS_ONLY=false
        SCRIPTS_ONLY=false
        DOCS_OR_SCRIPTS=false
        STREAMLIT_ONLY=false
    fi

    # Check if file is Streamlit app code
    if [[ "$file" =~ ^streamlit_app/.*\.py$ ]]; then
        HAS_STREAMLIT_CODE=true
        DOCS_ONLY=false
        TESTS_ONLY=false
        SCRIPTS_ONLY=false
        DOCS_OR_SCRIPTS=false
    fi

    # Check if NOT streamlit
    if [[ ! "$file" =~ ^streamlit_app/ ]]; then
        STREAMLIT_ONLY=false
    fi

    # Check if file is VBA
    if [[ "$file" =~ ^VBA/.*\.(bas|cls|frm)$ ]] || [[ "$file" =~ ^Excel/.*\.xlsm$ ]]; then
        HAS_VBA_CODE=true
        DOCS_ONLY=false
        TESTS_ONLY=false
        SCRIPTS_ONLY=false
        DOCS_OR_SCRIPTS=false
        STREAMLIT_ONLY=false
    fi

    # Check if file is CI
    if [[ "$file" =~ ^\.github/workflows/.*\.yml$ ]]; then
        HAS_CI_CODE=true
        DOCS_ONLY=false
        TESTS_ONLY=false
        SCRIPTS_ONLY=false
        DOCS_OR_SCRIPTS=false
        STREAMLIT_ONLY=false
    fi

    # Check if file is dependency
    if [[ "$file" =~ ^Python/(pyproject\.toml|requirements.*\.txt)$ ]]; then
        HAS_DEPS=true
        DOCS_ONLY=false
        TESTS_ONLY=false
        SCRIPTS_ONLY=false
        DOCS_OR_SCRIPTS=false
        STREAMLIT_ONLY=false
    fi

    # Check if NOT docs-like
    if ! is_docs_like "$file"; then
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
done <<< "$FILES"

# Make recommendation
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Git Workflow Recommendation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}Change metrics:${NC}"
echo "  Files changed: $FILE_COUNT"
echo "  Lines changed: $LINES_CHANGED"
echo "  New files: $NEW_FILES"
echo "  Renamed files: $RENAMED_FILES"
echo ""

if [[ "$STAGED_ONLY" == "true" ]]; then
    echo -e "${YELLOW}Staged files:${NC}"
    echo "$FILES" | sed 's/^/  /'
else
    echo -e "${YELLOW}Files (staged + unstaged + untracked):${NC}"
    echo "$FILES" | sed 's/^/  /'
fi
echo ""

# Decision logic - ALWAYS check production code first (highest risk)
if [[ "$HAS_PRODUCTION_CODE" == "true" ]]; then
    echo -e "${RED}🔀 RECOMMENDATION: Pull Request${NC}"
    echo -e "${RED}   (Production code changed)${NC}"
    if [[ "$EXPLAIN" == "true" ]]; then
        echo ""
        echo "Reasoning:"
        echo "- Python/structural_lib/ files changed"
        echo "- User-facing production code"
        echo "- CI validation + audit trail REQUIRED"
        echo "- No exceptions for production code"
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

# Streamlit code: Allow small fixes, require PR for substantial changes
# Rationale: No human reviewer, but scanner + CI + pre-commit hooks catch issues
if [[ "$STREAMLIT_ONLY" == "true" ]] && [[ "$HAS_STREAMLIT_CODE" == "true" ]]; then
    if [[ "$LINES_CHANGED" -lt "$STREAMLIT_MINOR_THRESHOLD" ]] && [[ "$FILE_COUNT" -eq 1 ]]; then
        echo -e "${GREEN}✅ RECOMMENDATION: Direct commit${NC}"
        echo -e "${GREEN}   (Minor Streamlit fix: $LINES_CHANGED lines, $FILE_COUNT file)${NC}"
        if [[ "$EXPLAIN" == "true" ]]; then
            echo ""
            echo "Reasoning:"
            echo "- Only streamlit_app/ files changed"
            echo "- Very small scope ($LINES_CHANGED lines < $STREAMLIT_MINOR_THRESHOLD threshold)"
            echo "- Single file change"
            echo "- Pre-commit hooks + CI scanner will validate"
        fi
        echo ""
        echo "Use: ./scripts/safe_push.sh \"fix(streamlit): <message>\""
        exit 0
    else
        echo -e "${RED}🔀 RECOMMENDATION: Pull Request${NC}"
        echo -e "${RED}   (Streamlit changes: $LINES_CHANGED lines, $FILE_COUNT file(s))${NC}"
        if [[ "$EXPLAIN" == "true" ]]; then
            echo ""
            echo "Reasoning:"
            echo "- Streamlit app code changed"
            echo "- $LINES_CHANGED lines (≥$STREAMLIT_MINOR_THRESHOLD) or $FILE_COUNT files (>1)"
            echo "- User-facing code deserves CI validation via PR"
        fi
        echo ""
        echo "Use: ./scripts/create_task_pr.sh TASK-XXX \"description\""
        exit 1
    fi
fi

# Now check docs/tests/scripts with SIZE sophistication
# Philosophy: Even low-risk files need PR if change is substantial

if [[ "$TESTS_ONLY" == "true" ]]; then
    # Tests: Minor edits OK, but substantial changes → PR
    if [[ "$LINES_CHANGED" -lt "$MINOR_LINES_THRESHOLD" ]] && [[ "$FILE_COUNT" -lt "$MINOR_FILES_THRESHOLD" ]]; then
        echo -e "${GREEN}✅ RECOMMENDATION: Direct commit${NC}"
        echo -e "${GREEN}   (Minor test changes: $LINES_CHANGED lines, $FILE_COUNT file(s))${NC}"
        if [[ "$EXPLAIN" == "true" ]]; then
            echo ""
            echo "Reasoning:"
            echo "- Only test files changed"
            echo "- Small scope ($LINES_CHANGED lines < $MINOR_LINES_THRESHOLD threshold)"
            echo "- Quick iteration appropriate"
        fi
        echo ""
        echo "Use: ./scripts/safe_push.sh \"test: <message>\""
        exit 0
    else
        echo -e "${RED}🔀 RECOMMENDATION: Pull Request${NC}"
        echo -e "${RED}   (Substantial test changes: $LINES_CHANGED lines, $FILE_COUNT file(s))${NC}"
        if [[ "$EXPLAIN" == "true" ]]; then
            echo ""
            echo "Reasoning:"
            echo "- Test changes but SUBSTANTIAL in size"
            echo "- $LINES_CHANGED lines (≥$MINOR_LINES_THRESHOLD) or $FILE_COUNT files (≥$MINOR_FILES_THRESHOLD)"
            echo "- Large test changes deserve review"
        fi
        echo ""
        echo "Use: ./scripts/create_task_pr.sh TASK-XXX \"description\""
        exit 1
    fi
fi

if [[ "$SCRIPTS_ONLY" == "true" ]]; then
    # Scripts: Minor edits OK, but substantial changes → PR
    if [[ "$LINES_CHANGED" -lt "$MINOR_LINES_THRESHOLD" ]] && [[ "$FILE_COUNT" -lt "$MINOR_FILES_THRESHOLD" ]]; then
        echo -e "${GREEN}✅ RECOMMENDATION: Direct commit${NC}"
        echo -e "${GREEN}   (Minor script changes: $LINES_CHANGED lines, $FILE_COUNT file(s))${NC}"
        if [[ "$EXPLAIN" == "true" ]]; then
            echo ""
            echo "Reasoning:"
            echo "- Only scripts/ directory changed"
            echo "- Small scope ($LINES_CHANGED lines < $MINOR_LINES_THRESHOLD threshold)"
            echo "- Quick tooling iteration appropriate"
        fi
        echo ""
        echo "Use: ./scripts/safe_push.sh \"chore: <message>\""
        exit 0
    else
        echo -e "${RED}🔀 RECOMMENDATION: Pull Request${NC}"
        echo -e "${RED}   (Substantial script changes: $LINES_CHANGED lines, $FILE_COUNT file(s))${NC}"
        if [[ "$EXPLAIN" == "true" ]]; then
            echo ""
            echo "Reasoning:"
            echo "- Script changes but SUBSTANTIAL in size"
            echo "- $LINES_CHANGED lines (≥$MINOR_LINES_THRESHOLD) or $FILE_COUNT files (≥$MINOR_FILES_THRESHOLD)"
            echo "- Large automation changes deserve review"
        fi
        echo ""
        echo "Use: ./scripts/create_task_pr.sh TASK-XXX \"description\""
        exit 1
    fi
fi

if [[ "$DOCS_ONLY" == "true" ]]; then
    # Documentation and research: PRs disabled, rely on pre-commit + CI checks.
    echo -e "${GREEN}✅ RECOMMENDATION: Direct commit${NC}"
    echo -e "${GREEN}   (Docs-only changes: PR not required)${NC}"
    if [[ "$EXPLAIN" == "true" ]]; then
        echo ""
        echo "Reasoning:"
        echo "- Documentation/research files only"
        echo "- PRs disabled to reduce workflow friction"
        echo "- Pre-commit hooks and CI still run for safety"
    fi
    echo ""
    echo "Use: ./scripts/safe_push.sh \"docs: <message>\""
    exit 0
fi

if [[ "$DOCS_OR_SCRIPTS" == "true" ]]; then
    # Mixed docs + scripts: Use solo-dev threshold (higher, since CI validates)
    if [[ "$LINES_CHANGED" -lt "$DOCS_SCRIPTS_MINOR_THRESHOLD" ]] && [[ "$FILE_COUNT" -le 4 ]]; then
        echo -e "${GREEN}✅ RECOMMENDATION: Direct commit${NC}"
        echo -e "${GREEN}   (Minor docs+scripts: $LINES_CHANGED lines, $FILE_COUNT file(s))${NC}"
        if [[ "$EXPLAIN" == "true" ]]; then
            echo ""
            echo "Reasoning:"
            echo "- Only docs/ and scripts/ changed"
            echo "- Small scope ($LINES_CHANGED lines < $DOCS_SCRIPTS_MINOR_THRESHOLD)"
            echo "- Low-risk: CI validates, pre-commit hooks check formatting"
            echo "- No human reviewer needed for docs+scripts"
        fi
        echo ""
        echo "Use: ./scripts/safe_push.sh \"docs: <message>\""
        exit 0
    else
        echo -e "${RED}🔀 RECOMMENDATION: Pull Request${NC}"
        echo -e "${RED}   (Substantial docs+scripts: $LINES_CHANGED lines, $FILE_COUNT file(s))${NC}"
        if [[ "$EXPLAIN" == "true" ]]; then
            echo ""
            echo "Reasoning:"
            echo "- Mixed docs + scripts changes"
            echo "- Substantial scope ($LINES_CHANGED lines ≥$DOCS_SCRIPTS_MINOR_THRESHOLD or >4 files)"
            echo "- Combined changes deserve review"
        fi
        echo ""
        echo "Use: ./scripts/create_task_pr.sh TASK-XXX \"description\""
        exit 1
    fi
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
