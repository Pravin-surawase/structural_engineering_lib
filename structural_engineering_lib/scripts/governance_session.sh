#!/bin/bash
# Weekly Governance Session Script
# TASK-284: Operationalize 80/20 rule (4 feature sessions : 1 governance session)
# Research: Based on Shopify's 75/25 rule, adapted to 80/20 for this project

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Configuration
SESSION_LOG="docs/SESSION_LOG.md"
GOVERNANCE_RATIO_TARGET=0.20  # 20% governance time
FEATURE_TO_GOVERNANCE=4       # 4 feature sessions : 1 governance session

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=== Weekly Governance Session ==="
echo "Date: $(date +%Y-%m-%d)"
echo ""

# ==========================================
# 1. SESSION TYPE ANALYSIS
# ==========================================

echo -e "${CYAN}📊 Analyzing session history...${NC}"

# Count sessions in last 30 days from SESSION_LOG.md
if [ -f "$SESSION_LOG" ]; then
    THIRTY_DAYS_AGO=$(date -v-30d +%Y-%m-%d 2>/dev/null || date -d "30 days ago" +%Y-%m-%d 2>/dev/null)

    # Extract session entries since 30 days ago
    RECENT_SESSIONS=$(awk -v date="$THIRTY_DAYS_AGO" '
        /^## [0-9]{4}-[0-9]{2}-[0-9]{2}/ {
            session_date = substr($2, 1, 10)
            if (session_date >= date) {
                in_recent = 1
            } else {
                in_recent = 0
            }
        }
        in_recent && /^###/ {
            print
        }
    ' "$SESSION_LOG")

    # Count feature vs governance sessions
    FEATURE_SESSIONS=$(echo "$RECENT_SESSIONS" | grep -ic "feature\|implementation\|fix\|enhancement" || echo "0")
    GOVERNANCE_SESSIONS=$(echo "$RECENT_SESSIONS" | grep -ic "governance\|maintenance\|cleanup\|metrics" || echo "0")
    TOTAL_SESSIONS=$((FEATURE_SESSIONS + GOVERNANCE_SESSIONS))

    if [ "$TOTAL_SESSIONS" -gt 0 ]; then
        GOVERNANCE_RATIO=$(echo "scale=2; $GOVERNANCE_SESSIONS / $TOTAL_SESSIONS" | bc)
    else
        GOVERNANCE_RATIO="0.00"
    fi
else
    FEATURE_SESSIONS=0
    GOVERNANCE_SESSIONS=0
    TOTAL_SESSIONS=0
    GOVERNANCE_RATIO="0.00"
fi

echo "  Last 30 days:"
echo "    Feature sessions: $FEATURE_SESSIONS"
echo "    Governance sessions: $GOVERNANCE_SESSIONS"
echo "    Total: $TOTAL_SESSIONS"
echo "    Governance ratio: ${GOVERNANCE_RATIO} (target: 0.20)"
echo ""

# ==========================================
# 2. 80/20 RULE COMPLIANCE
# ==========================================

echo -e "${CYAN}⚖️  Checking 80/20 rule compliance...${NC}"

# Check if we need a governance session
SESSIONS_SINCE_LAST_GOVERNANCE=$((FEATURE_SESSIONS % (FEATURE_TO_GOVERNANCE + 1)))

if [ "$(echo "$GOVERNANCE_RATIO < 0.15" | bc)" -eq 1 ]; then
    COMPLIANCE_STATUS="${RED}⚠️  BELOW TARGET${NC} (need more governance)"
    RECOMMENDATION="Schedule governance session immediately"
elif [ "$(echo "$GOVERNANCE_RATIO > 0.25" | bc)" -eq 1 ]; then
    COMPLIANCE_STATUS="${YELLOW}⚠️  ABOVE TARGET${NC} (too much governance)"
    RECOMMENDATION="Focus on feature work"
else
    COMPLIANCE_STATUS="${GREEN}✓ COMPLIANT${NC}"
    RECOMMENDATION="Continue current balance"
fi

echo -e "  Status: $COMPLIANCE_STATUS"
echo "  Recommendation: $RECOMMENDATION"
echo ""

# ==========================================
# 3. GOVERNANCE CHECKLIST
# ==========================================

echo -e "${CYAN}📋 Governance Session Checklist${NC}"
echo ""

# Run metrics collection
echo "  1. Collecting current metrics..."
if [ -f "scripts/collect_metrics.sh" ]; then
    ./scripts/collect_metrics.sh > /dev/null 2>&1
    LATEST_METRICS=$(ls -t metrics/metrics_*.json 2>/dev/null | head -1)
    if [ -n "$LATEST_METRICS" ]; then
        echo -e "     ${GREEN}✓ Metrics collected: $(basename $LATEST_METRICS)${NC}"
    else
        echo -e "     ${YELLOW}⚠ No metrics file found${NC}"
    fi
else
    echo -e "     ${YELLOW}⚠ Metrics script not found${NC}"
fi

# Run archival (dry run first)
echo "  2. Checking for archivable files..."
if [ -f "scripts/archive_old_sessions.sh" ]; then
    ARCHIVE_COUNT=$(DRY_RUN=1 ./scripts/archive_old_sessions.sh 2>/dev/null | grep "Files to archive:" | awk '{print $4}')
    if [ -z "$ARCHIVE_COUNT" ]; then
        ARCHIVE_COUNT=0
    fi

    if [ "$ARCHIVE_COUNT" -gt 0 ]; then
        echo -e "     ${YELLOW}⚠ $ARCHIVE_COUNT files can be archived${NC}"
        echo "     Run: ./scripts/archive_old_sessions.sh"
    else
        echo -e "     ${GREEN}✓ No files to archive${NC}"
    fi
else
    echo -e "     ${YELLOW}⚠ Archive script not found${NC}"
fi

# Check root file count
echo "  3. Checking root file limit..."
if [ -f "scripts/check_root_file_count.sh" ]; then
    ROOT_COUNT=$(./scripts/check_root_file_count.sh 2>/dev/null | grep "Current:" | awk '{print $2}')
    if [ "$ROOT_COUNT" -le 10 ]; then
        echo -e "     ${GREEN}✓ Root files: $ROOT_COUNT/10${NC}"
    else
        echo -e "     ${RED}⚠ Root files: $ROOT_COUNT/10 (OVER LIMIT)${NC}"
    fi
else
    echo -e "     ${YELLOW}⚠ Root check script not found${NC}"
fi

# Check for alerts
echo "  4. Reviewing leading indicator alerts..."
if [ -n "$LATEST_METRICS" ]; then
    ALERT_COUNT=$(jq -r '.alert_count // 0' "$LATEST_METRICS" 2>/dev/null)
    if [ "$ALERT_COUNT" -eq 0 ]; then
        echo -e "     ${GREEN}✓ No alerts${NC}"
    else
        echo -e "     ${YELLOW}⚠ $ALERT_COUNT alert(s) active${NC}"
        jq -r '.alerts[]' "$LATEST_METRICS" 2>/dev/null | while read -r alert; do
            echo "       • $alert"
        done
    fi
fi

# Check test coverage
echo "  5. Reviewing quality metrics..."
if [ -n "$LATEST_METRICS" ]; then
    COVERAGE=$(jq -r '.quality.coverage_percent // "N/A"' "$LATEST_METRICS" 2>/dev/null)
    RUFF_ERRORS=$(jq -r '.quality.ruff_errors // "N/A"' "$LATEST_METRICS" 2>/dev/null)
    MYPY_ERRORS=$(jq -r '.quality.mypy_errors // "N/A"' "$LATEST_METRICS" 2>/dev/null)

    echo "     Coverage: ${COVERAGE}% (target: >85%)"
    echo "     Ruff errors: $RUFF_ERRORS (target: 0)"
    echo "     Mypy errors: $MYPY_ERRORS (target: 0)"

    if [ "$COVERAGE" != "N/A" ] && [ "$(echo "$COVERAGE >= 85" | bc)" -eq 1 ] && [ "$RUFF_ERRORS" = "0" ] && [ "$MYPY_ERRORS" = "0" ]; then
        echo -e "     ${GREEN}✓ Quality metrics healthy${NC}"
    else
        echo -e "     ${YELLOW}⚠ Some quality metrics need attention${NC}"
    fi
fi

# Review velocity trends
echo "  6. Analyzing velocity trends..."
if [ -n "$LATEST_METRICS" ]; then
    COMMITS_PER_DAY=$(jq -r '.velocity.commits_per_day // "N/A"' "$LATEST_METRICS" 2>/dev/null)
    echo "     Current: ${COMMITS_PER_DAY} commits/day (target: 50-75)"

    if [ "$COMMITS_PER_DAY" != "N/A" ]; then
        if [ "$(echo "$COMMITS_PER_DAY >= 50 && $COMMITS_PER_DAY <= 75" | bc)" -eq 1 ]; then
            echo -e "     ${GREEN}✓ Velocity within target range${NC}"
        elif [ "$(echo "$COMMITS_PER_DAY > 100" | bc)" -eq 1 ]; then
            echo -e "     ${YELLOW}⚠ High velocity spike - watch for burnout${NC}"
        else
            echo -e "     ${BLUE}ℹ Velocity below target - acceptable variation${NC}"
        fi
    fi
fi

echo ""

# ==========================================
# 4. RECOMMENDATIONS
# ==========================================

echo -e "${CYAN}💡 Recommendations${NC}"
echo ""

if [ "$ARCHIVE_COUNT" -gt 0 ]; then
    echo "  • Archive $ARCHIVE_COUNT old files: ./scripts/archive_old_sessions.sh"
fi

if [ "$(echo "$GOVERNANCE_RATIO < 0.15" | bc)" -eq 1 ]; then
    echo "  • Schedule more governance sessions (currently ${GOVERNANCE_RATIO}, target: 0.20)"
fi

if [ "$ALERT_COUNT" -gt 0 ]; then
    echo "  • Address $ALERT_COUNT active alert(s)"
fi

# Calculate next governance session
NEXT_GOVERNANCE_IN=$((FEATURE_TO_GOVERNANCE - SESSIONS_SINCE_LAST_GOVERNANCE))
if [ "$NEXT_GOVERNANCE_IN" -le 0 ]; then
    echo -e "  • ${YELLOW}Next governance session: NOW (overdue)${NC}"
else
    echo "  • Next governance session: after $NEXT_GOVERNANCE_IN more feature session(s)"
fi

echo ""

# ==========================================
# 5. SESSION LOG UPDATE
# ==========================================

echo -e "${CYAN}📝 Updating session log...${NC}"

if [ -f "$SESSION_LOG" ]; then
    # Check if today's date already exists
    TODAY=$(date +%Y-%m-%d)
    if grep -q "^## $TODAY" "$SESSION_LOG"; then
        echo -e "  ${BLUE}ℹ Session log already has entry for today${NC}"
    else
        echo "  Adding governance session entry..."
        # This would typically be done manually or by another script
        echo -e "  ${YELLOW}⚠ Manual update recommended${NC}"
    fi
fi

echo ""
echo -e "${GREEN}=== Governance Session Complete ===${NC}"
echo ""
echo "Summary:"
echo "  • Feature sessions: $FEATURE_SESSIONS"
echo "  • Governance sessions: $GOVERNANCE_SESSIONS"
echo "  • Governance ratio: ${GOVERNANCE_RATIO} (target: 0.20)"
echo "  • Root files: $ROOT_COUNT/10"
echo "  • Alerts: $ALERT_COUNT active"
echo "  • Next governance in: $NEXT_GOVERNANCE_IN session(s)"

exit 0
