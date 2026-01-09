#!/bin/bash
# Metrics Collection Script
# TASK-282: Automated baseline tracking for velocity, WIP, quality
# Research: Based on METRICS_BASELINE.md and RESEARCH_FINDINGS_EXTERNAL.md

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Configuration
METRICS_DIR="metrics"
TIMESTAMP=$(date +%Y-%m-%d)
OUTPUT_FILE="${METRICS_DIR}/metrics_${TIMESTAMP}.json"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=== Governance Metrics Collection ==="
echo "Timestamp: $TIMESTAMP"
echo ""

# Create metrics directory if it doesn't exist
mkdir -p "$METRICS_DIR"

# ==========================================
# 1. VELOCITY METRICS
# ==========================================
echo "📊 Collecting velocity metrics..."

# Commits in last 24 hours
COMMITS_24H=$(git log --since="24 hours ago" --oneline | wc -l | tr -d ' ')

# Commits in last 7 days
COMMITS_7D=$(git log --since="7 days ago" --oneline | wc -l | tr -d ' ')

# Average commits per day (7-day window)
COMMITS_PER_DAY=$(echo "scale=1; $COMMITS_7D / 7" | bc)

# Total commits
TOTAL_COMMITS=$(git rev-list --count HEAD)

echo "  ✓ 24h commits: $COMMITS_24H"
echo "  ✓ 7d commits: $COMMITS_7D"
echo "  ✓ Avg/day: $COMMITS_PER_DAY"

# ==========================================
# 2. WIP METRICS
# ==========================================
echo ""
echo "🔧 Collecting WIP metrics..."

# Active PRs
if command -v gh &> /dev/null; then
    ACTIVE_PRS=$(gh pr list --state open --json number | jq '. | length')
else
    ACTIVE_PRS="N/A (gh CLI not available)"
fi

# Active worktrees
ACTIVE_WORKTREES=$(git worktree list | grep -v "(bare)" | tail -n +2 | wc -l | tr -d ' ')

# Active tasks (from TASKS.md)
if [ -f "docs/TASKS.md" ]; then
    ACTIVE_TASKS=$(grep -c "⏳ Ready\|⏳ In Progress" docs/TASKS.md || echo "0")
else
    ACTIVE_TASKS="0"
fi

echo "  ✓ Active PRs: $ACTIVE_PRS"
echo "  ✓ Worktrees: $ACTIVE_WORKTREES"
echo "  ✓ Active tasks: $ACTIVE_TASKS"

# ==========================================
# 3. DOCUMENTATION METRICS
# ==========================================
echo ""
echo "📝 Collecting documentation metrics..."

# Root files count
ROOT_FILES=$(find . -maxdepth 1 -type f \( -name "*.md" -o -name "*.txt" -o -name "*.sh" \) | wc -l | tr -d ' ')

# Total docs
TOTAL_DOCS=$(find docs/ -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')

# Archive files
ARCHIVE_FILES=$(find docs/_archive/ -type f 2>/dev/null | wc -l | tr -d ' ')

echo "  ✓ Root files: $ROOT_FILES"
echo "  ✓ Total docs: $TOTAL_DOCS"
echo "  ✓ Archived: $ARCHIVE_FILES"

# ==========================================
# 4. QUALITY METRICS
# ==========================================
echo ""
echo "✅ Collecting quality metrics..."

# Test files
if [ -d "Python/tests" ]; then
    TEST_FILES=$(find Python/tests -name "test_*.py" -type f | wc -l | tr -d ' ')
else
    TEST_FILES="0"
fi

# Run pytest to get coverage (if available)
if [ -f ".venv/bin/pytest" ] && [ -d "Python/tests" ]; then
    COVERAGE_OUTPUT=$(.venv/bin/python -m pytest --cov=Python/structural_lib --cov-report=term-missing --quiet Python/tests 2>&1 | grep "TOTAL" || echo "N/A")
    COVERAGE=$(echo "$COVERAGE_OUTPUT" | awk '{print $NF}' | tr -d '%' || echo "N/A")
    TEST_COUNT=$(.venv/bin/python -m pytest --collect-only --quiet Python/tests 2>&1 | grep "test session starts" -A 1 | tail -n 1 | awk '{print $2}' || echo "N/A")
else
    COVERAGE="N/A"
    TEST_COUNT="N/A"
fi

# Ruff errors
if [ -f ".venv/bin/ruff" ]; then
    RUFF_ERRORS=$(.venv/bin/python -m ruff check Python/structural_lib --quiet 2>&1 | wc -l | tr -d ' ')
else
    RUFF_ERRORS="N/A"
fi

# Mypy errors
if [ -f ".venv/bin/mypy" ]; then
    MYPY_ERRORS=$(.venv/bin/python -m mypy Python/structural_lib --no-error-summary 2>&1 | grep "error:" | wc -l | tr -d ' ')
else
    MYPY_ERRORS="N/A"
fi

echo "  ✓ Test files: $TEST_FILES"
echo "  ✓ Test count: $TEST_COUNT"
echo "  ✓ Coverage: $COVERAGE%"
echo "  ✓ Ruff errors: $RUFF_ERRORS"
echo "  ✓ Mypy errors: $MYPY_ERRORS"

# ==========================================
# 5. LEADING INDICATORS
# ==========================================
echo ""
echo "🚨 Collecting leading indicators..."

# Root doc creation rate (docs created in last 7 days)
ROOT_DOCS_CREATED=$(git log --since="7 days ago" --name-only --diff-filter=A --pretty=format: | grep "^[^/]*\.md$" | grep -v "^$" | wc -l | tr -d ' ')

# Crisis docs (count BUG, FIX, CRISIS in root and docs/)
CRISIS_DOCS=$(find . -maxdepth 2 -name "*BUG*.md" -o -name "*FIX*.md" -o -name "*CRISIS*.md" -o -name "*EMERGENCY*.md" 2>/dev/null | wc -l | tr -d ' ')

# Handoff docs
HANDOFF_DOCS=$(find . -maxdepth 2 -name "*HANDOFF*.md" -o -name "*SESSION*.md" 2>/dev/null | wc -l | tr -d ' ')

# Completion docs
COMPLETION_DOCS=$(find . -maxdepth 2 -name "*COMPLETE*.md" 2>/dev/null | wc -l | tr -d ' ')

# PR age (oldest open PR)
if command -v gh &> /dev/null && [ "$ACTIVE_PRS" != "N/A (gh CLI not available)" ]; then
    OLDEST_PR_DAYS=$(gh pr list --state open --json createdAt --jq 'sort_by(.createdAt) | .[0].createdAt' 2>/dev/null | xargs -I {} date -j -f "%Y-%m-%dT%H:%M:%SZ" {} "+%s" 2>/dev/null | xargs -I {} echo "($(date +%s) - {}) / 86400" | bc 2>/dev/null || echo "N/A")
else
    OLDEST_PR_DAYS="N/A"
fi

echo "  ✓ Root docs created (7d): $ROOT_DOCS_CREATED"
echo "  ✓ Crisis docs: $CRISIS_DOCS"
echo "  ✓ Handoff docs: $HANDOFF_DOCS"
echo "  ✓ Completion docs: $COMPLETION_DOCS"
echo "  ✓ Oldest PR age: $OLDEST_PR_DAYS days"

# ==========================================
# 6. ALERT EVALUATION
# ==========================================
echo ""
echo "⚠️  Evaluating alerts..."

ALERTS=()

# Alert 1: Root doc creation rate >2/day for 3+ days
if [ "$ROOT_DOCS_CREATED" -gt 6 ]; then
    ALERTS+=("Root doc creation rate HIGH: $ROOT_DOCS_CREATED in 7 days (threshold: 6)")
fi

# Alert 2: Crisis docs >3
if [ "$CRISIS_DOCS" -gt 3 ]; then
    ALERTS+=("Crisis docs HIGH: $CRISIS_DOCS (threshold: 3)")
fi

# Alert 3: Handoff docs >2
if [ "$HANDOFF_DOCS" -gt 2 ]; then
    ALERTS+=("Handoff docs HIGH: $HANDOFF_DOCS (threshold: 2)")
fi

# Alert 4: Completion docs >5
if [ "$COMPLETION_DOCS" -gt 5 ]; then
    ALERTS+=("Completion docs HIGH: $COMPLETION_DOCS (threshold: 5)")
fi

# Alert 5: Commits/day >100
COMMITS_THRESHOLD=100
if (( $(echo "$COMMITS_PER_DAY > $COMMITS_THRESHOLD" | bc -l) )); then
    ALERTS+=("Velocity spike: $COMMITS_PER_DAY commits/day (threshold: $COMMITS_THRESHOLD)")
fi

# Alert 6: PR age >3 days
if [ "$OLDEST_PR_DAYS" != "N/A" ] && [ "$OLDEST_PR_DAYS" -gt 3 ]; then
    ALERTS+=("PR age HIGH: $OLDEST_PR_DAYS days (threshold: 3)")
fi

if [ ${#ALERTS[@]} -eq 0 ]; then
    echo -e "  ${GREEN}✓ No alerts${NC}"
else
    echo -e "  ${RED}⚠  ${#ALERTS[@]} alert(s):${NC}"
    for alert in "${ALERTS[@]}"; do
        echo -e "    ${RED}▸${NC} $alert"
    done
fi

# ==========================================
# 7. WRITE JSON OUTPUT
# ==========================================
echo ""
echo "💾 Writing metrics to $OUTPUT_FILE..."

cat > "$OUTPUT_FILE" << EOF
{
  "timestamp": "$TIMESTAMP",
  "velocity": {
    "commits_24h": $COMMITS_24H,
    "commits_7d": $COMMITS_7D,
    "commits_per_day": $COMMITS_PER_DAY,
    "total_commits": $TOTAL_COMMITS
  },
  "wip": {
    "active_prs": "$ACTIVE_PRS",
    "active_worktrees": $ACTIVE_WORKTREES,
    "active_tasks": $ACTIVE_TASKS
  },
  "documentation": {
    "root_files": $ROOT_FILES,
    "total_docs": $TOTAL_DOCS,
    "archived_files": $ARCHIVE_FILES
  },
  "quality": {
    "test_files": $TEST_FILES,
    "test_count": "$TEST_COUNT",
    "coverage_percent": "$COVERAGE",
    "ruff_errors": "$RUFF_ERRORS",
    "mypy_errors": "$MYPY_ERRORS"
  },
  "leading_indicators": {
    "root_docs_created_7d": $ROOT_DOCS_CREATED,
    "crisis_docs": $CRISIS_DOCS,
    "handoff_docs": $HANDOFF_DOCS,
    "completion_docs": $COMPLETION_DOCS,
    "oldest_pr_days": "$OLDEST_PR_DAYS"
  },
  "alerts": [
$(IFS=$'\n'; for alert in "${ALERTS[@]}"; do echo "    \"$alert\","; done | sed '$ s/,$//')
  ],
  "alert_count": ${#ALERTS[@]}
}
EOF

echo -e "${GREEN}✓ Metrics collection complete${NC}"
echo ""
echo "Summary:"
echo "  📊 Velocity: $COMMITS_PER_DAY commits/day (7d avg)"
echo "  🔧 WIP: $ACTIVE_PRS PRs, $ACTIVE_WORKTREES worktrees, $ACTIVE_TASKS tasks"
echo "  📝 Docs: $ROOT_FILES root files (target: <10)"
echo "  ✅ Quality: $COVERAGE% coverage, $RUFF_ERRORS ruff errors"
echo "  ⚠️  Alerts: ${#ALERTS[@]} active"

exit 0
