#!/bin/bash
# Metrics Dashboard Script
# TASK-285: Trending visualization for governance metrics
# Research: Table-first format optimized for AI agents (RESEARCH_FINDINGS_EXTERNAL.md)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Configuration
METRICS_DIR="metrics"
DASHBOARD_OUTPUT="docs/governance/METRICS_DASHBOARD.md"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=== Generating Metrics Dashboard ==="
echo ""

# Create governance docs directory if needed
mkdir -p "$(dirname "$DASHBOARD_OUTPUT")"

# Get list of metrics files (last 30 days)
METRICS_FILES=$(find "$METRICS_DIR" -name "metrics_*.json" -type f -mtime -30 2>/dev/null | sort -r)
FILE_COUNT=$(echo "$METRICS_FILES" | grep -c "metrics_" || echo "0")

if [ "$FILE_COUNT" -eq 0 ]; then
    echo -e "${RED}⚠ No metrics files found in last 30 days${NC}"
    exit 1
fi

echo "Found $FILE_COUNT metrics file(s) from last 30 days"
echo "Generating dashboard..."
echo ""

# Get latest metrics
LATEST_METRICS=$(echo "$METRICS_FILES" | head -1)
LATEST_DATE=$(basename "$LATEST_METRICS" | sed 's/metrics_//;s/.json//')

# Start dashboard generation
cat > "$DASHBOARD_OUTPUT" << 'EOF'
# Governance Metrics Dashboard

> **Auto-generated** by `scripts/generate_dashboard.sh` (TASK-285)
> **Last updated:**
EOF

echo "$(date +"%Y-%m-%d %H:%M:%S")" >> "$DASHBOARD_OUTPUT"

cat >> "$DASHBOARD_OUTPUT" << 'EOF'

> **Purpose:** Track project health metrics, velocity trends, and governance compliance
> **Research:** Based on [METRICS_BASELINE.md](../../agents/agent-9/research/METRICS_BASELINE.md)

---

## 🎯 Current Snapshot

EOF

# Latest metrics snapshot
echo "### Latest Metrics (${LATEST_DATE})" >> "$DASHBOARD_OUTPUT"
echo "" >> "$DASHBOARD_OUTPUT"

# Extract and format current metrics
jq -r '
"| Category | Metric | Value | Target | Status |
|----------|--------|-------|--------|--------|
| **Velocity** | Commits/day (7d avg) | \(.velocity.commits_per_day) | 50-75 | " + (if .velocity.commits_per_day >= 50 and .velocity.commits_per_day <= 75 then "✅" elif .velocity.commits_per_day > 100 then "⚠️" else "ℹ️" end) + " |
| | Total commits | \(.velocity.total_commits) | - | ℹ️ |
| **WIP** | Active PRs | \(.wip.active_prs) | ≤2 | " + (if (.wip.active_prs | tonumber) <= 2 then "✅" else "⚠️" end) + " |
| | Worktrees | \(.wip.active_worktrees) | ≤2 | " + (if .wip.active_worktrees <= 2 then "✅" else "⚠️" end) + " |
| | Active tasks | \(.wip.active_tasks) | ≤2 | " + (if .wip.active_tasks <= 2 then "✅" else "⚠️" end) + " |
| **Documentation** | Root files | \(.documentation.root_files) | <10 | " + (if .documentation.root_files < 10 then "✅" else "❌" end) + " |
| | Archived files | \(.documentation.archived_files) | - | ℹ️ |
| **Quality** | Test coverage | \(.quality.coverage_percent)% | >85% | " + (if (.quality.coverage_percent | tonumber) >= 85 then "✅" else "⚠️" end) + " |
| | Ruff errors | \(.quality.ruff_errors) | 0 | " + (if (.quality.ruff_errors | tonumber) == 0 then "✅" else "❌" end) + " |
| | Mypy errors | \(.quality.mypy_errors) | 0 | " + (if (.quality.mypy_errors | tonumber) == 0 then "✅" else "❌" end) + " |
| **Alerts** | Active alerts | \(.alert_count) | 0 | " + (if .alert_count == 0 then "✅" else "⚠️" end) + " |"
' "$LATEST_METRICS" >> "$DASHBOARD_OUTPUT"

echo "" >> "$DASHBOARD_OUTPUT"

# Active alerts section
ALERT_COUNT=$(jq -r '.alert_count' "$LATEST_METRICS")
if [ "$ALERT_COUNT" -gt 0 ]; then
    echo "### 🚨 Active Alerts" >> "$DASHBOARD_OUTPUT"
    echo "" >> "$DASHBOARD_OUTPUT"
    jq -r '.alerts[] | "- ⚠️ " + .' "$LATEST_METRICS" >> "$DASHBOARD_OUTPUT"
    echo "" >> "$DASHBOARD_OUTPUT"
fi

# Trending section
cat >> "$DASHBOARD_OUTPUT" << 'EOF'
---

## 📈 Trends (Last 30 Days)

EOF

# Generate trend tables
echo "### Velocity Trends" >> "$DASHBOARD_OUTPUT"
echo "" >> "$DASHBOARD_OUTPUT"
echo "| Date | Commits/day | Commits (7d) | Total | Trend |" >> "$DASHBOARD_OUTPUT"
echo "|------|-------------|--------------|-------|-------|" >> "$DASHBOARD_OUTPUT"

# Process metrics files (last 10 for readability)
PREV_COMMITS_PER_DAY=""
echo "$METRICS_FILES" | head -10 | while read -r metrics_file; do
    if [ -f "$metrics_file" ]; then
        DATE=$(basename "$metrics_file" | sed 's/metrics_//;s/.json//')
        COMMITS_PER_DAY=$(jq -r '.velocity.commits_per_day' "$metrics_file" 2>/dev/null || echo "N/A")
        COMMITS_7D=$(jq -r '.velocity.commits_7d' "$metrics_file" 2>/dev/null || echo "N/A")
        TOTAL_COMMITS=$(jq -r '.velocity.total_commits' "$metrics_file" 2>/dev/null || echo "N/A")

        # Calculate trend
        if [ -n "$PREV_COMMITS_PER_DAY" ] && [ "$PREV_COMMITS_PER_DAY" != "N/A" ] && [ "$COMMITS_PER_DAY" != "N/A" ]; then
            DIFF=$(echo "$COMMITS_PER_DAY - $PREV_COMMITS_PER_DAY" | bc 2>/dev/null || echo "0")
            if [ "$(echo "$DIFF > 5" | bc 2>/dev/null || echo 0)" -eq 1 ]; then
                TREND="📈 +$(printf '%.1f' $DIFF)"
            elif [ "$(echo "$DIFF < -5" | bc 2>/dev/null || echo 0)" -eq 1 ]; then
                TREND="📉 $(printf '%.1f' $DIFF)"
            else
                TREND="→ stable"
            fi
        else
            TREND="-"
        fi

        echo "| $DATE | $COMMITS_PER_DAY | $COMMITS_7D | $TOTAL_COMMITS | $TREND |" >> "$DASHBOARD_OUTPUT"
        PREV_COMMITS_PER_DAY="$COMMITS_PER_DAY"
    fi
done

echo "" >> "$DASHBOARD_OUTPUT"

echo "### Documentation Trends" >> "$DASHBOARD_OUTPUT"
echo "" >> "$DASHBOARD_OUTPUT"
echo "| Date | Root Files | Total Docs | Archived | Status |" >> "$DASHBOARD_OUTPUT"
echo "|------|------------|------------|----------|--------|" >> "$DASHBOARD_OUTPUT"

echo "$METRICS_FILES" | head -10 | while read -r metrics_file; do
    if [ -f "$metrics_file" ]; then
        DATE=$(basename "$metrics_file" | sed 's/metrics_//;s/.json//')
        ROOT=$(jq -r '.documentation.root_files' "$metrics_file" 2>/dev/null || echo "N/A")
        TOTAL=$(jq -r '.documentation.total_docs' "$metrics_file" 2>/dev/null || echo "N/A")
        ARCHIVED=$(jq -r '.documentation.archived_files' "$metrics_file" 2>/dev/null || echo "N/A")

        if [ "$ROOT" != "N/A" ] && [ "$ROOT" -le 10 ]; then
            STATUS="✅"
        elif [ "$ROOT" != "N/A" ]; then
            STATUS="❌"
        else
            STATUS="-"
        fi

        echo "| $DATE | $ROOT | $TOTAL | $ARCHIVED | $STATUS |" >> "$DASHBOARD_OUTPUT"
    fi
done

echo "" >> "$DASHBOARD_OUTPUT"

echo "### Quality Trends" >> "$DASHBOARD_OUTPUT"
echo "" >> "$DASHBOARD_OUTPUT"
echo "| Date | Coverage | Ruff Errors | Mypy Errors | Status |" >> "$DASHBOARD_OUTPUT"
echo "|------|----------|-------------|-------------|--------|" >> "$DASHBOARD_OUTPUT"

echo "$METRICS_FILES" | head -10 | while read -r metrics_file; do
    if [ -f "$metrics_file" ]; then
        DATE=$(basename "$metrics_file" | sed 's/metrics_//;s/.json//')
        COVERAGE=$(jq -r '.quality.coverage_percent' "$metrics_file" 2>/dev/null || echo "N/A")
        RUFF=$(jq -r '.quality.ruff_errors' "$metrics_file" 2>/dev/null || echo "N/A")
        MYPY=$(jq -r '.quality.mypy_errors' "$metrics_file" 2>/dev/null || echo "N/A")

        if [ "$COVERAGE" != "N/A" ] && [ "$(echo "$COVERAGE >= 85" | bc 2>/dev/null || echo 0)" -eq 1 ] && [ "$RUFF" = "0" ] && [ "$MYPY" = "0" ]; then
            STATUS="✅"
        else
            STATUS="⚠️"
        fi

        echo "| $DATE | ${COVERAGE}% | $RUFF | $MYPY | $STATUS |" >> "$DASHBOARD_OUTPUT"
    fi
done

echo "" >> "$DASHBOARD_OUTPUT"

# Footer
cat >> "$DASHBOARD_OUTPUT" << 'EOF'
---

## 📊 Analysis

### Velocity
- **Target:** 50-75 commits/day (sustainable pace)
- **Research:** 60 commits/day = team-scale velocity (Shopify: 50-100/day)
- **Alert threshold:** >100 commits/day (burnout risk)

### Documentation
- **Target:** <10 root files (industry standard: Prettier 5, Vitest 2, tRPC 2)
- **Archival:** Automated via `scripts/archive_old_sessions.sh`
- **CI enforcement:** `scripts/check_root_file_count.sh`

### Quality
- **Coverage target:** >85% (current industry standard)
- **Zero tolerance:** Ruff and Mypy errors
- **Tests:** Run `pytest` before pushing

### Leading Indicators
Six metrics with alert thresholds:
1. Root doc creation rate: >2/day for 3+ days
2. Crisis docs: >3 in 7 days
3. Handoff docs: >2 overlapping
4. Completion docs: >5
5. Velocity spike: >100 commits/day
6. PR age: >3 days

---

## 🔗 Related Documentation

- [Metrics Baseline](../../agents/agent-9/research/METRICS_BASELINE.md) - Initial research
- [Research Findings](../../agents/agent-9/research/RESEARCH_FINDINGS_EXTERNAL.md) - Industry patterns
- [Implementation Roadmap](../../agents/agent-9/AGENT_9_IMPLEMENTATION_ROADMAP.md) - Complete plan
- [Governance Session Script](../../scripts/governance_session.sh) - 80/20 rule automation

---

**Automation:** Run `./scripts/generate_dashboard.sh` to update this dashboard
**Frequency:** Daily (automated in governance sessions)
**Version:** 1.0.0 (TASK-285)
EOF

echo -e "${GREEN}✓ Dashboard generated: $DASHBOARD_OUTPUT${NC}"
echo ""
echo "Preview:"
echo "  • $FILE_COUNT metrics files processed"
echo "  • Latest: $LATEST_DATE"
echo "  • Alerts: $ALERT_COUNT active"
echo ""
echo "View: cat $DASHBOARD_OUTPUT"

exit 0
