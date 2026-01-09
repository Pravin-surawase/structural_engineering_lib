#!/bin/bash
# Automated Archival Script
# TASK-283: Weekly cleanup of root directory documentation sprawl
# Research: Based on RESEARCH_FINDINGS_STRUCTURE.md archival strategy

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Configuration
ARCHIVE_BASE="docs/_archive"
CURRENT_MONTH=$(date +%Y-%m)
ARCHIVE_DIR="${ARCHIVE_BASE}/${CURRENT_MONTH}"

# Thresholds (in days)
COMPLETION_DOC_AGE=7    # Archive completion docs after 7 days
HANDOFF_DOC_AGE=7       # Archive handoff docs after 7 days
CRISIS_DOC_AGE=14       # Archive crisis docs after 14 days

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Dry run mode (set to 1 to preview without changes)
DRY_RUN=${DRY_RUN:-0}

echo "=== Automated Archival Script ==="
echo "Archive directory: $ARCHIVE_DIR"
echo "Dry run: $([ $DRY_RUN -eq 1 ] && echo 'YES (no changes will be made)' || echo 'NO')"
echo ""

# Create archive directory if needed
if [ ! -d "$ARCHIVE_DIR" ]; then
    if [ $DRY_RUN -eq 0 ]; then
        mkdir -p "$ARCHIVE_DIR"
        echo -e "${GREEN}✓ Created archive directory${NC}"
    else
        echo -e "${BLUE}[DRY RUN] Would create: $ARCHIVE_DIR${NC}"
    fi
fi

# Arrays to track files
declare -a TO_ARCHIVE
declare -a SKIPPED

# ==========================================
# HELPER FUNCTIONS
# ==========================================

# Get file age in days
get_file_age() {
    local file=$1
    if [ "$(uname)" = "Darwin" ]; then
        # macOS
        local file_time=$(stat -f %m "$file")
    else
        # Linux
        local file_time=$(stat -c %Y "$file")
    fi
    local current_time=$(date +%s)
    echo $(( (current_time - file_time) / 86400 ))
}

# Check if file should be archived
should_archive() {
    local file=$1
    local pattern=$2
    local age_threshold=$3

    if [[ "$file" =~ $pattern ]]; then
        local age=$(get_file_age "$file")
        if [ "$age" -ge "$age_threshold" ]; then
            return 0  # Should archive
        fi
    fi
    return 1  # Should not archive
}

# Archive a file
archive_file() {
    local file=$1
    local reason=$2

    if [ $DRY_RUN -eq 1 ]; then
        echo -e "${BLUE}[DRY RUN] Would archive: $file ($reason)${NC}"
        TO_ARCHIVE+=("$file")
    else
        echo -e "${GREEN}Archiving: $file ($reason)${NC}"
        git mv "$file" "$ARCHIVE_DIR/"
        TO_ARCHIVE+=("$file")
    fi
}

# ==========================================
# ARCHIVAL RULES
# ==========================================

echo "Scanning root directory for archivable files..."
echo ""

# Find all .md, .txt, .sh files in root (excluding hidden files)
ROOT_FILES=$(find . -maxdepth 1 -type f \( -name "*.md" -o -name "*.txt" -o -name "*.sh" \) ! -name ".*" | sort)

# Canonical files that should NEVER be archived (pipe-separated for grep)
CANONICAL_PATTERN="./README.md|./CHANGELOG.md|./CONTRIBUTING.md|./CODE_OF_CONDUCT.md|./SECURITY.md|./AUTHORS.md|./LICENSE_ENGINEERING.md|./SUPPORT.md|./llms.txt"

# Check if file is canonical
is_canonical() {
    echo "$1" | grep -E "^(${CANONICAL_PATTERN})$" > /dev/null
}

# Process each root file
for file in $ROOT_FILES; do
    # Skip if canonical
    if is_canonical "$file"; then
        continue
    fi

    filename=$(basename "$file")
    age=$(get_file_age "$file")

    # Rule 1: Completion docs (AGENT-*-COMPLETE.md, *-COMPLETE.md)
    if [[ "$filename" =~ -COMPLETE\.md$ ]]; then
        if [ "$age" -ge "$COMPLETION_DOC_AGE" ]; then
            archive_file "$file" "completion doc, age: ${age}d (threshold: ${COMPLETION_DOC_AGE}d)"
            continue
        else
            SKIPPED+=("$file (completion doc, age: ${age}d < ${COMPLETION_DOC_AGE}d)")
        fi
    fi

    # Rule 2: Handoff docs (*-HANDOFF*.md, SESSION-*.md)
    if [[ "$filename" =~ HANDOFF|SESSION ]]; then
        if [ "$age" -ge "$HANDOFF_DOC_AGE" ]; then
            archive_file "$file" "handoff doc, age: ${age}d (threshold: ${HANDOFF_DOC_AGE}d)"
            continue
        else
            SKIPPED+=("$file (handoff doc, age: ${age}d < ${HANDOFF_DOC_AGE}d)")
        fi
    fi

    # Rule 3: Crisis docs (BUG-*, FIX-*, *-FIXED.md, *-APPLIED.md, *_PLAN.md, *_REPORT.md)
    if [[ "$filename" =~ BUG-|FIX-|-FIXED\.md$|-APPLIED\.md$|_PLAN\.md$|_REPORT\.md$ ]]; then
        if [ "$age" -ge "$CRISIS_DOC_AGE" ]; then
            archive_file "$file" "crisis doc, age: ${age}d (threshold: ${CRISIS_DOC_AGE}d)"
            continue
        else
            SKIPPED+=("$file (crisis doc, age: ${age}d < ${CRISIS_DOC_AGE}d)")
        fi
    fi

    # Rule 4: Work summary docs (*-SUMMARY.md, WORK-*.md)
    if [[ "$filename" =~ -SUMMARY\.md$|^WORK- ]]; then
        if [ "$age" -ge "$HANDOFF_DOC_AGE" ]; then
            archive_file "$file" "work summary, age: ${age}d (threshold: ${HANDOFF_DOC_AGE}d)"
            continue
        else
            SKIPPED+=("$file (work summary, age: ${age}d < ${HANDOFF_DOC_AGE}d)")
        fi
    fi

    # Rule 5: Temporary/status docs (READY-*, DELEGATE-*, SOLUTIONS-*)
    if [[ "$filename" =~ ^READY-|^DELEGATE-|^SOLUTIONS- ]]; then
        if [ "$age" -ge "$HANDOFF_DOC_AGE" ]; then
            archive_file "$file" "temporary doc, age: ${age}d (threshold: ${HANDOFF_DOC_AGE}d)"
            continue
        else
            SKIPPED+=("$file (temporary doc, age: ${age}d < ${HANDOFF_DOC_AGE}d)")
        fi
    fi

    # Rule 6: Analysis/research docs (ANALYSIS-*, RESEARCH-*, *-STRATEGY.md)
    if [[ "$filename" =~ ANALYSIS-|RESEARCH-|-STRATEGY\.md$|-ENHANCED\.md$ ]]; then
        if [ "$age" -ge "$HANDOFF_DOC_AGE" ]; then
            archive_file "$file" "analysis doc, age: ${age}d (threshold: ${HANDOFF_DOC_AGE}d)"
            continue
        else
            SKIPPED+=("$file (analysis doc, age: ${age}d < ${HANDOFF_DOC_AGE}d)")
        fi
    fi

    # Rule 7: Temporary scripts and text files
    if [[ "$filename" =~ \.txt$|\.sh$ ]] && [[ ! "$filename" =~ ^llms\.txt$ ]]; then
        if [ "$age" -ge "$HANDOFF_DOC_AGE" ]; then
            archive_file "$file" "temporary file, age: ${age}d (threshold: ${HANDOFF_DOC_AGE}d)"
            continue
        else
            SKIPPED+=("$file (temporary file, age: ${age}d < ${HANDOFF_DOC_AGE}d)")
        fi
    fi

    # If we get here, file doesn't match any archival rule
    SKIPPED+=("$file (no archival rule matched)")
done

# ==========================================
# REPORT
# ==========================================

echo ""
echo "=== Archival Summary ==="
echo ""

if [ ${#TO_ARCHIVE[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ No files to archive${NC}"
else
    echo -e "${YELLOW}Files to archive: ${#TO_ARCHIVE[@]}${NC}"
    for file in "${TO_ARCHIVE[@]}"; do
        echo "  ▸ $file"
    done
fi

echo ""
echo -e "${BLUE}Files skipped: ${#SKIPPED[@]}${NC}"
if [ ${#SKIPPED[@]} -gt 0 ]; then
    echo "(Reasons: too new, canonical, or no matching rule)"
fi

# Check final root file count
FINAL_ROOT_COUNT=$(find . -maxdepth 1 -type f \( -name "*.md" -o -name "*.txt" -o -name "*.sh" \) | wc -l | tr -d ' ')

if [ $DRY_RUN -eq 0 ]; then
    FINAL_ROOT_COUNT=$((FINAL_ROOT_COUNT - ${#TO_ARCHIVE[@]}))
fi

echo ""
echo "Root file count after archival: $FINAL_ROOT_COUNT"

if [ "$FINAL_ROOT_COUNT" -le 10 ]; then
    echo -e "${GREEN}✓ Within limit (target: ≤10)${NC}"
else
    echo -e "${RED}⚠ Above limit (target: ≤10)${NC}"
    echo "Consider manual review of remaining files"
fi

# ==========================================
# COMMIT (if not dry run and files archived)
# ==========================================

if [ $DRY_RUN -eq 0 ] && [ ${#TO_ARCHIVE[@]} -gt 0 ]; then
    echo ""
    echo "Committing archived files..."

    # Commit message
    COMMIT_MSG="chore(governance): automated archival - ${#TO_ARCHIVE[@]} files to ${CURRENT_MONTH}

Archived files:
$(for file in "${TO_ARCHIVE[@]}"; do echo "- $(basename $file)"; done)

Automated by: scripts/archive_old_sessions.sh (TASK-283)
Root file count: ${FINAL_ROOT_COUNT}/10"

    git commit -m "$COMMIT_MSG"
    echo -e "${GREEN}✓ Committed archival changes${NC}"
fi

echo ""
echo "=== Archival Complete ===$([ $DRY_RUN -eq 1 ] && echo ' (DRY RUN)' || echo '')"

exit 0
