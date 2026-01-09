#!/bin/bash
# Auto-archive files older than 90 days from docs/_active/
#
# Usage:
#   ./scripts/archive_old_files.sh           # Execute archival
#   ./scripts/archive_old_files.sh --dry-run # Preview only
#   ./scripts/archive_old_files.sh --help    # Show help
#
# Runs monthly via CI cron job (defined in .github/workflows/monthly-maintenance.yml)

set -euo pipefail

# Configuration
ACTIVE_DIR="docs/_active"
ARCHIVE_DIR="docs/_archive"
RETENTION_DAYS=90
DRY_RUN=false
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Archive files older than $RETENTION_DAYS days from $ACTIVE_DIR/ to $ARCHIVE_DIR/"
            echo ""
            echo "Options:"
            echo "  --dry-run    Preview changes without executing"
            echo "  --verbose    Show detailed output"
            echo "  --help       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Error: Must run from project root (where pyproject.toml is)${NC}"
    exit 1
fi

# Check if directories exist
if [ ! -d "$ACTIVE_DIR" ]; then
    echo -e "${RED}❌ Error: $ACTIVE_DIR/ not found${NC}"
    exit 1
fi

# Create archive directory if needed
if [ ! -d "$ARCHIVE_DIR" ]; then
    echo -e "${YELLOW}⚠️  Creating $ARCHIVE_DIR/ ...${NC}"
    mkdir -p "$ARCHIVE_DIR"
fi

# Header
echo -e "${BLUE}🗂️  Auto-Archival System${NC}"
echo -e "${BLUE}════════════════════════${NC}"
echo ""
echo "Configuration:"
echo "  • Active directory:  $ACTIVE_DIR/"
echo "  • Archive directory: $ARCHIVE_DIR/"
echo "  • Retention period:  $RETENTION_DAYS days"
echo "  • Mode:              $([ "$DRY_RUN" = true ] && echo "DRY RUN" || echo "LIVE")"
echo ""

# Find files to archive
echo -e "${BLUE}🔍 Scanning for old files...${NC}"

archived_count=0
skipped_count=0

# Find all markdown files in _active/ older than RETENTION_DAYS
# Note: BSD find (macOS) uses different syntax than GNU find (Linux)
if [ "$(uname)" = "Darwin" ]; then
    # macOS (BSD find)
    OLD_FILES=$(find "$ACTIVE_DIR" -type f -name "*.md" -mtime +${RETENTION_DAYS} 2>/dev/null || true)
else
    # Linux (GNU find)
    OLD_FILES=$(find "$ACTIVE_DIR" -type f -name "*.md" -mtime +${RETENTION_DAYS} 2>/dev/null || true)
fi

if [ -z "$OLD_FILES" ]; then
    echo -e "${GREEN}✅ No files older than $RETENTION_DAYS days found${NC}"
    exit 0
fi

echo "$OLD_FILES" | while IFS= read -r file; do
    if [ -z "$file" ]; then
        continue
    fi

    # Get file metadata
    filename=$(basename "$file")

    # Extract year-month from file modification date
    if [ "$(uname)" = "Darwin" ]; then
        # macOS
        year_month=$(stat -f "%Sm" -t "%Y-%m" "$file")
    else
        # Linux
        year_month=$(date -r "$file" +%Y-%m)
    fi

    # Determine archive location
    archive_folder="$ARCHIVE_DIR/$year_month"
    archive_path="$archive_folder/$filename"

    # Check if file already exists in archive
    if [ -f "$archive_path" ]; then
        echo -e "${YELLOW}  ⚠️  Skipping (already exists): $filename${NC}"
        skipped_count=$((skipped_count + 1))
        continue
    fi

    # Archive file
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}  📦 [DRY RUN] Would archive: $file → $archive_path${NC}"
    else
        # Create archive folder if needed
        mkdir -p "$archive_folder"

        # Move file
        mv "$file" "$archive_path"
        echo -e "${GREEN}  ✅ Archived: $filename → $year_month/${NC}"

        [ "$VERBOSE" = true ] && echo "     From: $file"
        [ "$VERBOSE" = true ] && echo "     To:   $archive_path"
    fi

    archived_count=$((archived_count + 1))
done

# Summary
echo ""
echo -e "${BLUE}📊 Summary${NC}"
echo -e "${BLUE}═══════════${NC}"

if [ "$DRY_RUN" = true ]; then
    echo -e "  • Files that would be archived: ${YELLOW}$archived_count${NC}"
    echo -e "  • Files that would be skipped:  ${YELLOW}$skipped_count${NC}"
    echo ""
    echo -e "${YELLOW}ℹ️  This was a dry run. No files were moved.${NC}"
    echo -e "${YELLOW}   Run without --dry-run to execute archival.${NC}"
else
    echo -e "  • Files archived: ${GREEN}$archived_count${NC}"
    echo -e "  • Files skipped:  ${YELLOW}$skipped_count${NC}"
    echo ""

    if [ $archived_count -gt 0 ]; then
        echo -e "${GREEN}✅ Archival complete${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Update archive index: python scripts/update_archive_index.py"
        echo "  2. Commit changes: ./scripts/ai_commit.sh \"chore: archive old files\""
    else
        echo -e "${GREEN}✅ No files archived (all up to date)${NC}"
    fi
fi

exit 0
