# Phase 4: Dated Files Archival

**Duration:** 4-6 hours (mostly automated)
**Complexity:** Low-Medium
**Risk:** Low (uses existing archive script)
**Validation Impact:** ~64 errors → ~41 errors (20% reduction)

---

## Overview

Archive dated files to `docs/_archive/YYYY-MM/` using the existing `scripts/archive_old_docs.py` script.

**What are "dated files"?**
- Files with dates in name matching pattern: `-202[0-9]-` (e.g., `file-2025-12-15.md`)
- Typically session logs, planning snapshots, or time-specific documentation
- Should live in `docs/_active/YYYY-MM/` or `docs/_archive/YYYY-MM/`

**Current State:**
```
23 dated files in wrong locations:
- docs/planning/session-2025-12-15.md ❌
- docs/design-2025-11-20.md ❌
- docs/architecture/decisions-2025-10-10.md ❌
- ... (20 more)
```

**Target State:**
```
docs/_archive/2026-01/
├── session-2025-12-15.md ✅
├── design-2025-11-20.md ✅
├── decisions-2025-10-10.md ✅
└── ... (20 more)
```

---

## Prerequisites

- ✅ Phase 0 complete (backup created, archive script tested)
- ✅ Phase 1 complete (`docs/_archive/` structure exists)
- ✅ Phase 2 complete (agents/ clean)
- ✅ Working tree is clean
- ✅ Migration branch active
- ✅ Freeze window in effect

**Optional:**
- Phase 3 complete (docs/ categorization done) - **recommended but not required**

---

## Step-by-Step Execution

### Step 1: Identify Dated Files

```bash
# Find all files with dates in name
find docs/ -name "*-202[0-9]-*" -type f

# Count dated files
find docs/ -name "*-202[0-9]-*" -type f | wc -l
# Should show ~23 files

# Show detailed list with paths
find docs/ -name "*-202[0-9]-*" -type f -exec ls -lh {} \; | \
  awk '{print $9, "(" $5 ")"}'
```

**Expected output:**
```
docs/planning/session-2025-12-15.md (12K)
docs/design-2025-11-20.md (8K)
docs/architecture/decisions-2025-10-10.md (15K)
docs/planning/analysis-2025-09-05.md (20K)
... (19 more)
```

**Checkpoint 1:** ✅ Dated files identified

---

### Step 2: Review Archive Script

```bash
# Review archive script help
python scripts/archive_old_docs.py --help

# Expected flags:
# --dry-run: Show what would be archived without moving
# --age-days: Archive files older than N days (default: 90)
# --pattern: Custom regex pattern for filenames
# --target-dir: Target archive directory (default: docs/_archive/YYYY-MM/)
```

**Script behavior:**
- Finds dated files matching pattern
- Checks if file is older than threshold (default: 90 days)
- Moves to `docs/_archive/YYYY-MM/` based on file date
- Updates LINK-MAP.md with migration entries
- Creates month subdirectories as needed

**Checkpoint 2:** ✅ Script reviewed

---

### Step 3: Test Archive Script (Dry Run)

```bash
# Run in dry-run mode to preview changes
python scripts/archive_old_docs.py --dry-run

# Expected output:
# 🔍 Scanning for dated files...
# Found 23 files matching pattern: *-202[0-9]-*
#
# Would archive:
#   docs/planning/session-2025-12-15.md
#     → docs/_archive/2025-12/session-2025-12-15.md
#
#   docs/design-2025-11-20.md
#     → docs/_archive/2025-11/design-2025-11-20.md
#
#   ... (21 more)
#
# ✅ Dry run complete. 23 files would be archived.
```

**Review output carefully:**
- Are correct files being archived?
- Are any active/important files included?
- Are target paths correct (YYYY-MM format)?

**If any file should NOT be archived:**
```bash
# Exclude specific files
python scripts/archive_old_docs.py --dry-run --exclude "important-2025-12.md"

# Or move manually later
```

**Checkpoint 3:** ✅ Dry run reviewed and approved

---

### Step 4: Run Archive Script (Actual)

```bash
# Execute archive script (removes --dry-run flag)
python scripts/archive_old_docs.py

# Expected output:
# 🔍 Scanning for dated files...
# Found 23 files matching pattern: *-202[0-9]-*
#
# Archiving files:
#   ✅ docs/planning/session-2025-12-15.md
#      → docs/_archive/2025-12/session-2025-12-15.md
#
#   ✅ docs/design-2025-11-20.md
#      → docs/_archive/2025-11/design-2025-11-20.md
#
#   ... (21 more)
#
# 📝 Updated LINK-MAP.md with 23 entries
# ✅ Archive complete. 23 files archived to docs/_archive/
```

**What the script does:**
1. Moves files using `git mv` (preserves history)
2. Creates month subdirectories (`docs/_archive/2025-12/`, etc.)
3. Updates `agents/agent-9/governance/LINK-MAP.md` with old → new mappings
4. Stages all changes for commit

**Checkpoint 4:** ✅ Files archived

---

### Step 5: Verify Archive Completed

```bash
# Verify no dated files remain in wrong locations
find docs/ -name "*-202[0-9]-*" -type f | \
  grep -v "_archive" | \
  grep -v "_active"

# Should return NOTHING (or only files in _active/ if any)

# Verify files moved to archive
ls -la docs/_archive/2025-12/
ls -la docs/_archive/2025-11/
ls -la docs/_archive/2025-10/
# Should show archived files

# Count archived files
find docs/_archive/ -name "*.md" -type f | wc -l
# Should show ~23 files (may be more if archive already had files)

# Check git status
git status
# Should show:
#   renamed: docs/planning/session-2025-12-15.md → docs/_archive/2025-12/session-2025-12-15.md
#   ... (22 more)
#   modified: agents/agent-9/governance/LINK-MAP.md
```

**Expected git status:**
```
On branch migration/folder-structure-cleanup
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	renamed:    docs/planning/session-2025-12-15.md -> docs/_archive/2025-12/session-2025-12-15.md
	renamed:    docs/design-2025-11-20.md -> docs/_archive/2025-11/design-2025-11-20.md
	... (21 more)
	modified:   agents/agent-9/governance/LINK-MAP.md
```

**Checkpoint 5:** ✅ Archive verified

---

### Step 6: Review LINK-MAP.md Updates

```bash
# View LINK-MAP.md updates
tail -30 agents/agent-9/governance/LINK-MAP.md

# Expected format:
# # Phase 4: Dated Files Archival (2026-01-10)
# docs/planning/session-2025-12-15.md → docs/_archive/2025-12/session-2025-12-15.md
# docs/design-2025-11-20.md → docs/_archive/2025-11/design-2025-11-20.md
# ... (21 more)
```

**Verify:**
- All 23 files listed
- Old path → new path format correct
- Date header matches today (2026-01-10)
- Phase number correct (Phase 4)

**Checkpoint 6:** ✅ LINK-MAP.md updated correctly

---

### Step 7: Update References to Archived Files

**Find references to archived files:**

```bash
# Search for references to old paths
for file in $(cat agents/agent-9/governance/LINK-MAP.md | grep "Phase 4" | awk '{print $1}'); do
  echo "Searching for: $file"
  grep -r "$file" docs/ agents/ --include="*.md" || echo "  (no references)"
done
```

**Update references:**

If references found, update them to new paths:

```bash
# Example: Update reference to session-2025-12-15.md
find docs/ agents/ -name "*.md" -type f -exec sed -i '' \
  's|docs/planning/session-2025-12-15\.md|docs/_archive/2025-12/session-2025-12-15.md|g' {} +

# Repeat for each file with references
```

**Or manually update if few references:**

```bash
# Check specific files
grep -r "session-2025-12-15" docs/ agents/ --include="*.md"

# Edit files manually if < 5 references
```

**Checkpoint 7:** ✅ References updated (if any)

---

### Step 8: Clean Up `docs/planning/`

**After archival, `docs/planning/` should have fewer files.**

```bash
# Count remaining files in docs/planning/
ls -1 docs/planning/*.md | wc -l

# Expected: ~79 → ~56 files (23 fewer)

# Review remaining files
ls -la docs/planning/

# Identify any other files that should be archived
# (non-dated but old/inactive)
```

**Optional cleanup:**
- Review remaining docs/planning/ files
- Archive other inactive files manually
- Move active planning docs to docs/getting-started/ or docs/architecture/

**Checkpoint 8:** ✅ docs/planning/ cleaner

---

### Step 9: Validate Changes

```bash
# Run validation script
python scripts/validate_folder_structure.py

# Expected improvements:
# - Dated files violations: 23 → 0 ✅
# - docs/ root file count: may improve if some dated files were in docs/
# - Total errors: ~64 → ~41 (36% total reduction from baseline)
```

**Expected validation output:**
```
✅ No dated files in wrong locations
⚠️  docs/ root still has ~40 files (will fix in Phase 3/5)
⚠️  Naming violations still present (will fix in Phase 5)

Total errors: ~41 (down from 115 baseline)
```

**If validation fails:**
- Check all dated files moved (Step 5)
- Check no dated files remain outside _archive/_active
- Review error messages for specific issues

**Checkpoint 9:** ✅ Validation improved

---

### Step 10: Commit Changes

```bash
# Stage all changes (should already be staged by script)
git add -A

# Verify staged changes
git diff --cached --stat

# Create commit with descriptive message
git commit -m "$(cat <<'EOF'
feat(migration): Phase 4 - Archive 23 dated files

- Move dated files to docs/_archive/YYYY-MM/ structure
- Use archive_old_docs.py script for automated migration
- Create month subdirectories: 2025-12/, 2025-11/, 2025-10/, etc.
- Update LINK-MAP.md with 23 migration entries
- Update references to archived files (if any)

Validation improvements:
- Dated files violations: 23 → 0 (100% fixed)
- docs/planning/: 79 → ~56 files (29% reduction)
- Total errors: ~64 → ~41 (64% reduction from baseline)

Phase 4 of 8 complete.
Ref: agents/agent-9/governance/FULL-MIGRATION-EXECUTION-PLAN.md

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# Push to migration branch
git push origin migration/folder-structure-cleanup
```

**Checkpoint 10:** ✅ Changes committed and pushed

---

## Validation Checklist

After completing all steps, verify:

- [ ] No dated files (`*-202[0-9]-*`) outside `docs/_archive/` or `docs/_active/`
- [ ] `find docs/ -name "*-202[0-9]-*" | grep -v "_archive" | grep -v "_active"` returns nothing
- [ ] 23 files moved to `docs/_archive/YYYY-MM/` subdirectories
- [ ] Month subdirectories created as needed (2025-12/, 2025-11/, etc.)
- [ ] LINK-MAP.md updated with 23 entries
- [ ] All references to archived files updated (or noted as intentional)
- [ ] Validation errors reduced from ~64 to ~41
- [ ] `python scripts/validate_folder_structure.py` shows no dated file violations
- [ ] Git history preserved (files show as "renamed" not "deleted + added")
- [ ] Changes committed with descriptive message
- [ ] Migration branch pushed to remote

---

## Manual Archive (If Script Fails)

**If `archive_old_docs.py` doesn't exist or fails, archive manually:**

```bash
# Create archive directories
mkdir -p docs/_archive/2025-12
mkdir -p docs/_archive/2025-11
mkdir -p docs/_archive/2025-10
# ... (create as needed)

# Move files manually (example)
git mv docs/planning/session-2025-12-15.md docs/_archive/2025-12/session-2025-12-15.md
git mv docs/design-2025-11-20.md docs/_archive/2025-11/design-2025-11-20.md
# ... (repeat for all 23 files)

# Update LINK-MAP.md manually
cat >> agents/agent-9/governance/LINK-MAP.md << 'EOF'

# Phase 4: Dated Files Archival (2026-01-10)
docs/planning/session-2025-12-15.md → docs/_archive/2025-12/session-2025-12-15.md
docs/design-2025-11-20.md → docs/_archive/2025-11/design-2025-11-20.md
... (21 more)
EOF

# Stage and commit
git add -A
git commit -m "feat(migration): Phase 4 - Archive dated files (manual)"
```

---

## Archive Retention Policy

**Per governance rules:**

- **`docs/_active/YYYY-MM/`**: Current month + last 2 months (3 months total)
- **`docs/_archive/YYYY-MM/`**: Older than 3 months, kept indefinitely

**Example (as of 2026-01-10):**
```
docs/_active/2026-01/  ← Current month
docs/_active/2025-12/  ← Last month
docs/_active/2025-11/  ← 2 months ago

docs/_archive/2025-10/ ← 3+ months ago
docs/_archive/2025-09/
docs/_archive/2025-08/
... (all older months)
```

**Monthly maintenance (Agent 9 task):**
- On 1st of each month, move previous month's files from `_active/` to `_archive/`
- Keep only last 3 months in `_active/`
- Archive has no size limit (Git handles compression)

---

## Rollback Procedure

**If Phase 4 fails or produces wrong results:**

```bash
# Undo last commit
git reset --hard HEAD~1

# Or restore specific files
git checkout HEAD~1 -- docs/planning/session-2025-12-15.md

# Or use backup tag
git reset --hard backup-pre-migration-2026-01-10

# Re-run archive script with fixes
python scripts/archive_old_docs.py --dry-run
# Review output
python scripts/archive_old_docs.py
```

**See:** [ROLLBACK-PROCEDURES.md](ROLLBACK-PROCEDURES.md) for detailed recovery steps.

---

## Expected Error Reduction

**Before Phase 4:**
- ❌ ~64 total errors (after Phases 1-3)
- ❌ Dated files: 23 in wrong locations
- ❌ docs/planning/: 79 files (many dated)

**After Phase 4:**
- ✅ ~41 total errors (64% reduction from baseline)
- ✅ Dated files: 0 violations
- ✅ docs/planning/: ~56 files (29% reduction)

**Progress:** 64% of migration complete (dated files FIXED)

---

## Time Estimates

- **Step 1 (Identify):** 10 minutes
- **Step 2 (Review script):** 5 minutes
- **Step 3 (Dry run):** 10 minutes
- **Step 4 (Archive):** 5 minutes (automated)
- **Step 5 (Verify):** 15 minutes
- **Step 6 (Review LINK-MAP):** 5 minutes
- **Step 7 (Update references):** 30-60 minutes (if references exist)
- **Step 8 (Cleanup planning):** 30 minutes
- **Step 9 (Validate):** 10 minutes
- **Step 10 (Commit):** 10 minutes

**Total:** 2-3 hours (if no references), 4-6 hours (if many references)

**Automation saves time:**
- Manual: 6-8 hours (moving 23 files + updating LINK-MAP)
- Script: 2-3 hours (mostly verification)

---

## Common Issues

### Issue 1: Archive script not found

**Error:** `python scripts/archive_old_docs.py` → `No such file or directory`

**Solution:**
```bash
# Check if script exists
ls -la scripts/archive_old_docs.py

# If missing, create it (see MIGRATION-SCRIPTS.md)
# Or use manual archive procedure above
```

### Issue 2: Script archives active files

**Error:** Script tries to archive important active file

**Solution:**
```bash
# Exclude specific files
python scripts/archive_old_docs.py --exclude "important-2025-12.md"

# Or restore after archive
git mv docs/_archive/2025-12/important-2025-12.md docs/_active/2026-01/important-2025-12.md
```

### Issue 3: Month directories not created

**Error:** Files moved but month subdirectories missing

**Solution:**
```bash
# Create directories manually
mkdir -p docs/_archive/2025-12
mkdir -p docs/_archive/2025-11

# Re-run script or move files manually
```

### Issue 4: LINK-MAP.md format wrong

**Error:** Link map entries don't follow format

**Solution:**
```bash
# Edit LINK-MAP.md manually
# Format: old-path → new-path
# Example: docs/planning/file.md → docs/_archive/2025-12/file.md
```

### Issue 5: Validation still shows dated file errors

**Error:** Some dated files not archived

**Solution:**
```bash
# Find remaining dated files
find docs/ -name "*-202[0-9]-*" -type f | grep -v "_archive" | grep -v "_active"

# Archive manually
git mv <file> docs/_archive/YYYY-MM/<file>
```

---

## Next Steps

After Phase 4 completion:

1. **Update MIGRATION-STATUS.md** to mark Phase 4 complete
2. **Decide on Phase 3 vs Phase 5:**
   - **Phase 3** (docs/ categorization) - largest phase, 12-16 hours
   - **Phase 5** (naming cleanup) - automated, 8-10 hours
3. **Recommended:** Complete Phase 5 next (naming) since it's more automated

**Or proceed directly to Phase 5 if Phase 3 was already completed.**

---

## Success Criteria

Phase 4 is complete when:

1. ✅ Zero dated files outside `docs/_archive/` or `docs/_active/`
2. ✅ All 23 dated files archived to correct YYYY-MM subdirectories
3. ✅ LINK-MAP.md updated with 23 migration entries
4. ✅ All references to archived files updated (or intentionally left)
5. ✅ Validation shows no dated file violations
6. ✅ Error count reduced by ~23 (or more)
7. ✅ Changes committed and pushed
8. ✅ Git history preserved (renames tracked)

---

**Phase 4 Status:** 📋 Ready for execution
**Last Updated:** 2026-01-10
**Next Phase:** [PHASE-5-NAMING-CLEANUP.md](PHASE-5-NAMING-CLEANUP.md) or [PHASE-3-DOCS-MIGRATION.md](PHASE-3-DOCS-MIGRATION.md)
