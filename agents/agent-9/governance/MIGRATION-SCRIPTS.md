# Migration Scripts Reference

**Purpose:** Documentation of all automation scripts used during folder structure migration
**Last Updated:** 2026-01-10

---

## Overview

This document catalogs all scripts created or used during the migration, their purpose, usage, and maintenance instructions.

**Script Categories:**
1. **Existing Scripts** (updated during migration)
2. **New Scripts** (created for migration)
3. **Temporary Scripts** (used during migration, can be deleted after)

---

## Existing Scripts (Updated)

### 1. `scripts/validate_folder_structure.py`

**Purpose:** Validate folder structure against governance rules

**Usage:**
```bash
# Basic validation
python scripts/validate_folder_structure.py

# Detailed report
python scripts/validate_folder_structure.py --report

# Auto-fix (if implemented)
python scripts/validate_folder_structure.py --fix
```

**Governance Rules Checked:**
- Root directory file count (max 10)
- docs/ root file count (max 5)
- agents/ root file count (max 1)
- Category folder existence
- Dated file locations
- Naming conventions (kebab-case)
- Duplicate folder concepts

**Exit Codes:**
- `0`: All checks passed
- `1`: Violations found

**Updates During Migration:**
- **Phase 1:** Verified rules match governance doc
- **Phase 7:** Updated to check new folder structure
- **No major changes needed** (already governance-aware)

**Maintenance:**
- Run weekly (Agent 9 task)
- Update if governance rules change
- Keep synchronized with `FOLDER_STRUCTURE_GOVERNANCE.md`

---

### 2. `scripts/archive_old_docs.py`

**Purpose:** Archive dated files to `docs/_archive/YYYY-MM/`

**Usage:**
```bash
# Dry-run (preview what would be archived)
python scripts/archive_old_docs.py --dry-run

# Archive files older than 90 days
python scripts/archive_old_docs.py

# Archive files older than custom threshold
python scripts/archive_old_docs.py --age-days 60

# Exclude specific files
python scripts/archive_old_docs.py --exclude "important-2025-12.md"
```

**Features:**
- Finds files matching pattern `-202[0-9]-` (dated files)
- Checks age (default: 90 days)
- Moves to `docs/_archive/YYYY-MM/` based on file date
- Updates `LINK-MAP.md` with old → new paths
- Uses `git mv` to preserve history
- Creates month subdirectories automatically

**Updates During Migration:**
- **Phase 4:** Used to archive 23 dated files
- **Phase 7:** Updated scan directories (if needed)

**Maintenance:**
- Run monthly (1st of month, Agent 9 task)
- Move files from `docs/_active/` to `docs/_archive/`
- Keep only last 3 months in `_active/`

---

### 3. `scripts/check_links.py`

**Purpose:** Check markdown links for broken references

**Usage:**
```bash
# Check all links in docs/ and agents/
python scripts/check_links.py docs/ agents/

# Detailed report
python scripts/check_links.py docs/ agents/ --report

# With ignore list
python scripts/check_links.py docs/ agents/ --ignore /path/to/ignore-list.txt

# Fix relative links (if implemented)
python scripts/check_links.py docs/ agents/ --fix-relative
```

**Features:**
- Finds all markdown links `[text](target.md)`
- Checks if target files exist
- Handles relative and absolute paths
- Supports anchor links (`file.md#section`)
- Detects broken links

**Updates During Migration:**
- **Phase 0 or 1:** Created if didn't exist
- **Phase 6:** Used extensively to verify link fixes
- **Phase 7:** Updated ignore patterns for `_archive/`

**Maintenance:**
- Run weekly (Agent 9 task)
- Run after any file moves/renames
- Update ignore list as needed

---

### 4. `scripts/generate_health_report.py`

**Purpose:** Generate governance health metrics

**Usage:**
```bash
# Generate report to stdout
python scripts/generate_health_report.py

# Save to file
python scripts/generate_health_report.py --output agents/agent-9/governance/HEALTH-REPORT.md
```

**Metrics Generated:**
- Validation error count
- Folder structure compliance
- Documentation file counts
- Category distribution
- Link health
- Script functionality
- Overall health score

**Updates During Migration:**
- **Phase 5:** Updated agent file path (`agents/roles/`)
- **Phase 7:** Updated docs/ scanning (category folders)

**Maintenance:**
- Run weekly (Agent 9 task)
- Update after governance rule changes
- Track metrics over time

---

### 5. `scripts/check_wip_limits.py`

**Purpose:** Check work-in-progress limits in `docs/_active/`

**Usage:**
```bash
# Check WIP limits
python scripts/check_wip_limits.py

# Custom WIP limit
python scripts/check_wip_limits.py --limit 10
```

**Features:**
- Counts files in `docs/_active/`
- Warns if exceeds threshold (default: 15 files)
- Suggests archiving old files

**Updates During Migration:**
- **Phase 7:** Updated active directory path (if needed)

**Maintenance:**
- Run weekly (Agent 9 task)
- Adjust limit based on team size

---

### 6. `scripts/check_version_consistency.py`

**Purpose:** Check version consistency across documentation

**Usage:**
```bash
# Check all version references
python scripts/check_version_consistency.py

# Check specific version
python scripts/check_version_consistency.py --version 0.16
```

**Features:**
- Finds version references (e.g., `v0.16`, `version 0.16`)
- Checks for inconsistencies
- Reports outdated version mentions

**Updates During Migration:**
- **Phase 5:** Updated if version file paths changed

**Maintenance:**
- Run before releases
- Update after version bumps

---

## New Scripts (Created for Migration)

### 7. `/tmp/rename_batch.sh` (Temporary)

**Purpose:** Batch rename files with validation

**Created:** Phase 5

**Usage:**
```bash
# Rename batch of files from file
/tmp/rename_batch.sh /tmp/batch-1.txt

# Batch file format:
# old/path.md → new/path.md
# (one per line)
```

**Features:**
- Validates new names are kebab-case
- Checks files exist before renaming
- Uses `git mv` to preserve history
- Updates `LINK-MAP.md` automatically
- Error handling and reporting

**Maintenance:**
- **Delete after migration** (temporary script)
- Or move to `scripts/` if useful for future

---

### 8. `/tmp/update_refs.sh` (Temporary)

**Purpose:** Update references after file renames

**Created:** Phase 5

**Usage:**
```bash
# Update references based on LINK-MAP.md
/tmp/update_refs.sh
```

**Features:**
- Reads `LINK-MAP.md` for old → new mappings
- Updates all references using `sed`
- Handles filename and path changes
- Batch processing

**Maintenance:**
- **Delete after migration** (temporary script)

---

### 9. `/tmp/fix_archived_links.sh` (Temporary)

**Purpose:** Fix links to archived dated files

**Created:** Phase 4

**Usage:**
```bash
# Fix links to files moved to _archive/
/tmp/fix_archived_links.sh
```

**Features:**
- Reads `LINK-MAP.md` Phase 4 entries
- Updates links to archived files
- Handles relative path adjustments

**Maintenance:**
- **Delete after migration** (temporary script)

---

### 10. `/tmp/bulk_rename.sh` (Temporary)

**Purpose:** Bulk rename with validation (improved version of #7)

**Created:** Phase 5

**Usage:**
```bash
# Bulk rename with strict validation
/tmp/bulk_rename.sh /tmp/batch-file.txt
```

**Features:**
- Stricter kebab-case validation
- Error counting and reporting
- Dry-run mode support
- Better error messages

**Maintenance:**
- **Delete after migration** (temporary script)
- Or consolidate with #7

---

### 11. `/tmp/fix_refs.sh` (Temporary)

**Purpose:** Fix references with better pattern matching

**Created:** Phase 6

**Usage:**
```bash
# Fix references using LINK-MAP.md
/tmp/fix_refs.sh
```

**Features:**
- Advanced pattern matching
- Case-sensitive replacement
- Multiple path format handling

**Maintenance:**
- **Delete after migration** (temporary script)

---

### 12. `/tmp/validate_kebab.py` (Temporary)

**Purpose:** Validate and suggest kebab-case names

**Created:** Phase 5

**Usage:**
```bash
# Check if filename is valid kebab-case
python /tmp/validate_kebab.py Task_Specs.md

# Output:
# ❌ Invalid: Task_Specs.md
# 💡 Suggest: task-specs.md
```

**Features:**
- Pattern validation
- Automatic conversion suggestion
- Handles PascalCase, snake_case, mixed case

**Maintenance:**
- **Move to `scripts/utils/`** if useful for future
- Or delete after migration

---

## Script Dependencies

**Python Scripts:**
- Python 3.8+
- Standard library only (no external dependencies)
- Pathlib, re, sys, argparse

**Shell Scripts:**
- Bash 4.0+
- GNU sed (macOS: `brew install gnu-sed`)
- Git (for `git mv`)

**Optional Tools:**
- `gh` CLI (for creating PRs)
- `act` (for local GitHub Actions testing)

---

## Script Testing Checklist

Before using any script:

```bash
# 1. Verify Python version
python --version  # Should be 3.8+

# 2. Test script help
python scripts/validate_folder_structure.py --help

# 3. Dry-run if available
python scripts/archive_old_docs.py --dry-run

# 4. Test on small dataset first
# (Create test directory, run script, verify results)

# 5. Check exit codes
python scripts/validate_folder_structure.py
echo $?  # Should be 0 (success) or 1 (errors found)
```

---

## Error Handling Patterns

**Standard error handling:**

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

def main():
    try:
        # Script logic here
        result = do_work()

        if result.errors:
            print(f"❌ {len(result.errors)} errors found")
            for error in result.errors:
                print(f"  • {error}")
            sys.exit(1)
        else:
            print("✅ Success")
            sys.exit(0)

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Shell script error handling:**

```bash
#!/bin/bash
set -euo pipefail  # Exit on error, undefined var, pipe failure

# Error counter
ERRORS=0

# Check preconditions
if [ ! -f "required-file.txt" ]; then
  echo "❌ Required file not found"
  ((ERRORS++))
fi

# Exit with error count
if [ $ERRORS -gt 0 ]; then
  echo "❌ $ERRORS errors found"
  exit 1
else
  echo "✅ Success"
  exit 0
fi
```

---

## Script Locations

**Permanent Scripts:** `scripts/`
```
scripts/
├── validate_folder_structure.py  # Core validation
├── archive_old_docs.py            # Monthly archival
├── check_links.py                 # Link verification
├── generate_health_report.py      # Metrics generation
├── check_wip_limits.py            # WIP monitoring
└── check_version_consistency.py   # Version tracking
```

**Temporary Scripts:** `/tmp/` or `scripts/migration/`
```
/tmp/
├── rename_batch.sh           # Phase 5 batch renaming
├── update_refs.sh            # Phase 5 reference updates
├── fix_archived_links.sh     # Phase 4 archive links
├── bulk_rename.sh            # Phase 5 bulk rename
├── fix_refs.sh               # Phase 6 reference fixing
└── validate_kebab.py         # Phase 5 name validation
```

---

## Post-Migration Cleanup

**After migration complete:**

```bash
# Delete temporary scripts
rm -f /tmp/rename_batch.sh
rm -f /tmp/update_refs.sh
rm -f /tmp/fix_archived_links.sh
rm -f /tmp/bulk_rename.sh
rm -f /tmp/fix_refs.sh
rm -f /tmp/validate_kebab.py

# Or move useful ones to scripts/utils/
mkdir -p scripts/utils/
mv /tmp/validate_kebab.py scripts/utils/
```

**Archive migration scripts:**

```bash
# Create migration archive directory
mkdir -p docs/_archive/migrations/2026-01/scripts/

# Move temporary scripts (for historical reference)
cp /tmp/*.sh docs/_archive/migrations/2026-01/scripts/
cp /tmp/*.py docs/_archive/migrations/2026-01/scripts/

# Commit archive
git add docs/_archive/migrations/
git commit -m "docs: archive migration scripts for historical reference"
```

---

## Script Maintenance Schedule

**Weekly (Agent 9 Task):**
- Run `validate_folder_structure.py`
- Run `check_links.py`
- Run `generate_health_report.py`
- Run `check_wip_limits.py`

**Monthly (Agent 9 Task):**
- Run `archive_old_docs.py` (1st of month)
- Review and archive `_active/` → `_archive/`
- Update metrics trends

**Before Releases:**
- Run `check_version_consistency.py`
- Update all version references
- Verify documentation accuracy

**After File Moves/Renames:**
- Run `check_links.py` immediately
- Fix any broken links
- Update `LINK-MAP.md` if needed

---

## Adding New Scripts

**Template for new governance scripts:**

```python
#!/usr/bin/env python3
"""Short description of what this script does.

Usage:
    python scripts/new_script.py [options]

Examples:
    python scripts/new_script.py --dry-run
    python scripts/new_script.py --output report.md
"""

import argparse
import sys
from pathlib import Path

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Description of script"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without executing"
    )
    args = parser.parse_args()

    # Script logic here
    print("✅ Script complete")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Add to governance:**

1. Update `scripts/README.md` with script description
2. Add to Agent 9 maintenance workflows
3. Document in this file (MIGRATION-SCRIPTS.md)
4. Test with dry-run first
5. Add to CI/CD if appropriate

---

## Troubleshooting

**Script fails with "Permission denied":**
```bash
# Make script executable
chmod +x scripts/script_name.py
```

**Script can't find files:**
```bash
# Ensure running from project root
cd /path/to/structural_engineering_lib
python scripts/script_name.py
```

**sed not working on macOS:**
```bash
# Install GNU sed
brew install gnu-sed

# Or use BSD sed with different syntax
sed -i '' 's|old|new|g' file  # macOS
sed -i 's|old|new|g' file      # Linux
```

**Python version mismatch:**
```bash
# Use specific Python version
python3 scripts/script_name.py

# Or create virtual environment
python3 -m venv venv
source venv/bin/activate
python scripts/script_name.py
```

---

## Script Performance

**Optimization tips:**

1. **Use `rglob` instead of `os.walk`** (faster, cleaner)
2. **Compile regex patterns once** (avoid re-compiling in loops)
3. **Batch file operations** (don't open/close repeatedly)
4. **Use `--dry-run` for testing** (avoid expensive operations)
5. **Cache results** (if script runs multiple times)

**Example optimization:**

```python
# SLOW:
for file in files:
    if re.match(r"pattern", file.name):  # Compiles every iteration
        process(file)

# FAST:
pattern = re.compile(r"pattern")  # Compile once
for file in files:
    if pattern.match(file.name):
        process(file)
```

---

## Future Script Ideas

**Potential governance scripts:**

1. **`check_duplicate_content.py`** - Find duplicate or near-duplicate docs
2. **`generate_toc.py`** - Auto-generate table of contents for category READMEs
3. **`check_orphaned_files.py`** - Find files with no inbound links
4. **`suggest_archive.py`** - Suggest files to archive based on last-modified
5. **`validate_frontmatter.py`** - Check YAML frontmatter consistency
6. **`check_code_blocks.py`** - Validate code blocks in docs (syntax, examples)

---

**Last Updated:** 2026-01-10
**Related Docs:**
- [FOLDER_STRUCTURE_GOVERNANCE.md](FOLDER_STRUCTURE_GOVERNANCE.md)
- [FULL-MIGRATION-EXECUTION-PLAN.md](FULL-MIGRATION-EXECUTION-PLAN.md)
- [ROLLBACK-PROCEDURES.md](ROLLBACK-PROCEDURES.md)
