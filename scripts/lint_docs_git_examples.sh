#!/bin/bash
# lint_docs_git_examples.sh
# Detect manual git command patterns in non-archive documentation.
# These patterns can mislead agents into using manual git commands.
#
# Usage: ./scripts/lint_docs_git_examples.sh [--strict]
#
# Exit codes:
#   0 - No issues found
#   1 - Issues found (non-strict mode, warnings only)
#   2 - Issues found (strict mode, fails)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STRICT="${1:-}"

# Patterns to detect (manual git commands)
PATTERNS=(
    'git add\.'
    'git add -A'
    'git commit -m'
    'git push$'
    'git push origin'
    'git pull$'
    'git pull origin'
)

# Directories to EXCLUDE (archives, historical, research)
EXCLUDE_DIRS=(
    "docs/_archive"
    "docs/research"
    "docs/git-automation/research"
    "docs/git-automation/historical-mistakes"
)

# Files to EXCLUDE (these are meant to document manual commands)
EXCLUDE_FILES=(
    "git-workflow-ai-agents.md"
    "mistakes-prevention.md"
    "workflow-guide.md"
    "copilot-instructions.md"
)

# Build grep exclude args
build_excludes() {
    local excludes=""
    for dir in "${EXCLUDE_DIRS[@]}"; do
        excludes+=" --exclude-dir=$(basename "$dir")"
    done
    for file in "${EXCLUDE_FILES[@]}"; do
        excludes+=" --exclude=$file"
    done
    echo "$excludes"
}

echo ""
echo "Lint: Manual Git Examples in Docs"
echo "=================================="

ISSUES_FOUND=0
TOTAL_MATCHES=0

for pattern in "${PATTERNS[@]}"; do
    # Search in docs/ excluding archive/research
    MATCHES=$(grep -rn --include="*.md" \
        --exclude-dir="_archive" \
        --exclude-dir="research" \
        --exclude-dir="historical-mistakes" \
        --exclude="copilot-instructions.md" \
        --exclude="mistakes-prevention.md" \
        --exclude="workflow-guide.md" \
        --exclude="git-workflow-ai-agents.md" \
        "$pattern" "$PROJECT_ROOT/docs" 2>/dev/null || true)

    if [[ -n "$MATCHES" ]]; then
        COUNT=$(echo "$MATCHES" | wc -l | tr -d ' ')
        ((TOTAL_MATCHES+=COUNT)) || true

        if [[ "$ISSUES_FOUND" -eq 0 ]]; then
            echo ""
            echo "⚠️  Manual git patterns found:"
            echo ""
        fi
        ISSUES_FOUND=1

        echo "Pattern: $pattern"
        echo "$MATCHES" | while read -r line; do
            # Extract file path relative to docs/
            FILE=$(echo "$line" | cut -d: -f1 | sed "s|$PROJECT_ROOT/||")
            LINE_NUM=$(echo "$line" | cut -d: -f2)
            echo "  → $FILE:$LINE_NUM"
        done
        echo ""
    fi
done

if [[ "$ISSUES_FOUND" -eq 1 ]]; then
    echo "----------------------------------------"
    echo "Total matches: $TOTAL_MATCHES"
    echo ""
    echo "Recommendations:"
    echo "1. Replace manual git with: ./scripts/ai_commit.sh \"message\""
    echo "2. If intentional (historical), add <!-- lint-ignore-git --> comment"
    echo "3. If educational, move to docs/_archive/ or docs/research/"
    echo ""

    if [[ "$STRICT" == "--strict" ]]; then
        echo "❌ STRICT MODE: Failing due to manual git patterns"
        exit 2
    else
        echo "ℹ️  Non-strict mode: Warnings only"
        exit 0
    fi
else
    echo ""
    echo "✅ No manual git patterns found in active docs"
    exit 0
fi
