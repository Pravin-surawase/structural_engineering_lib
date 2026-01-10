# Phase 5: Naming Convention Cleanup

**Duration:** 8-10 hours (2 days, or 10 sessions of 1 hour each)
**Complexity:** Medium-High
**Risk:** Medium (many files, many references)
**Validation Impact:** ~41 errors → ~6 errors (85% reduction)

---

## Overview

Rename 92 files from non-standard naming to kebab-case convention.

**Naming Convention Rules (from governance):**
- **Preferred:** kebab-case (`task-specs.md`, `agent-guide.md`)
- **Allowed:** snake_case for Python (`validate_structure.py`)
- **Not Allowed:** UPPERCASE, PascalCase, mixed case

**Current State:**
```
92 naming violations:
- TASKS.md ✅ (exception - allowed in docs/ root)
- SESSION_LOG.md ✅ (exception - allowed)
- Task-Specs.md ❌ (PascalCase → task-specs.md)
- planning_2025.md ❌ (snake_case → planning-2025.md)
- NEW_FEATURE.md ❌ (UPPERCASE → new-feature.md)
- ... (89 more)
```

**Special Cases:**
- `TASKS.md`, `SESSION_LOG.md`, `CHANGELOG.md`, `README.md` → **Keep as-is** (explicitly allowed)
- `v0.16-task-specs.md` → **Keep version dots** (user preference) or convert to `v0-16-task-specs.md`
- Python files → **Use snake_case** (PEP 8)

---

## Prerequisites

- ✅ Phase 0 complete (backup created)
- ✅ Phase 1 complete (folder structure exists)
- ✅ Phase 2 complete (agents/ files renamed)
- ✅ Phase 4 complete (dated files archived) - **recommended**
- ✅ Working tree is clean
- ✅ Migration branch active
- ✅ Freeze window in effect

**Optional:**
- Phase 3 complete (docs/ categorization) - helps reduce scope

---

## Strategy

**Approach: Incremental batches (5-10 files per batch)**

Why incremental?
- ✅ Lower risk (isolate errors to small batches)
- ✅ Easier rollback (undo single batch vs all 92)
- ✅ Staged validation (catch reference errors early)
- ✅ Sustainable pace (1 hour sessions vs 8-hour marathon)

**Recommended schedule:**
- **Option A:** 10 sessions over 2 weeks (1 hour/day, 9-10 files/session)
- **Option B:** 2 days dedicated (4-5 hours/day, 45 files/day)

---

## Step-by-Step Execution

### Step 1: Generate Naming Violations Report

```bash
# Run validation to get naming violations
python scripts/validate_folder_structure.py | grep -A 200 "naming"

# Or create custom report script
cat > /tmp/list_naming_violations.py << 'EOF'
#!/usr/bin/env python3
import re
from pathlib import Path

docs_pattern = re.compile(r"^[a-z0-9\-]+\.md$")
exceptions = ["README.md", "TASKS.md", "SESSION_LOG.md", "CHANGELOG.md", "TODO.md"]

print("# Naming Violations Report\n")

for md_file in Path("docs").rglob("*.md"):
    if md_file.name in exceptions:
        continue
    if not docs_pattern.match(md_file.name):
        print(f"❌ {md_file}")

print("\nTotal violations: ", end="")
EOF

python /tmp/list_naming_violations.py | tee /tmp/naming-violations.txt
```

**Expected output:**
```
# Naming Violations Report

❌ docs/Task-Specs.md
❌ docs/planning/Analysis_Report.md
❌ docs/architecture/Design_Decisions.md
❌ docs/NEW_FEATURE.md
... (88 more)

Total violations: 92
```

**Checkpoint 1:** ✅ Violations identified and documented

---

### Step 2: Categorize Files by Rename Complexity

**Group files into batches by complexity:**

**Batch 1: Simple renames (no references expected)**
- Isolated docs with few/no inbound links
- Examples: old planning docs, archive candidates
- Count: ~20 files

**Batch 2: Medium renames (some references)**
- Docs with moderate linking
- Examples: architecture docs, guides
- Count: ~30 files

**Batch 3: High-impact renames (many references)**
- Frequently referenced docs
- Examples: core specs, agent guides
- Count: ~20 files

**Batch 4: Special cases**
- Version-prefixed files (v0.16-*, v0.15-*)
- Files needing manual review
- Count: ~22 files

**Create batch list:**
```bash
cat > /tmp/rename-batches.txt << 'EOF'
# BATCH 1: Simple (20 files)
docs/planning/Old_Analysis.md → docs/planning/old-analysis.md
docs/planning/Draft_Ideas.md → docs/planning/draft-ideas.md
... (18 more)

# BATCH 2: Medium (30 files)
docs/architecture/Design_Patterns.md → docs/architecture/design-patterns.md
docs/reference/API_Guide.md → docs/reference/api-guide.md
... (28 more)

# BATCH 3: High-Impact (20 files)
docs/Task_Specifications.md → docs/task-specifications.md
docs/Agent_Coordination.md → docs/agent-coordination.md
... (18 more)

# BATCH 4: Special Cases (22 files)
docs/v0.16-Task_Specs.md → docs/v0.16-task-specs.md
docs/v0.15-Design_Doc.md → docs/v0.15-design-doc.md
... (20 more)
EOF
```

**Checkpoint 2:** ✅ Files grouped into batches

---

### Step 3: Execute Batch 1 (Simple Renames)

**For each file in Batch 1:**

```bash
# Example: Rename Old_Analysis.md → old-analysis.md
OLD_PATH="docs/planning/Old_Analysis.md"
NEW_NAME="old-analysis.md"
NEW_PATH="docs/planning/${NEW_NAME}"

# Check if file exists
if [ -f "$OLD_PATH" ]; then
  # Search for references (should be none or few)
  grep -r "Old_Analysis.md" docs/ agents/ --include="*.md" || echo "No references found"

  # Rename using git mv
  git mv "$OLD_PATH" "$NEW_PATH"

  # Update LINK-MAP.md
  echo "$OLD_PATH → $NEW_PATH" >> agents/agent-9/governance/LINK-MAP.md
else
  echo "File not found: $OLD_PATH"
fi
```

**Automated batch script:**

```bash
cat > /tmp/rename_batch.sh << 'EOF'
#!/bin/bash
# Rename batch of files

BATCH_FILE=$1  # File with "old → new" pairs

while IFS='→' read -r old_path new_path; do
  # Trim whitespace
  old_path=$(echo "$old_path" | xargs)
  new_path=$(echo "$new_path" | xargs)

  # Skip comments and empty lines
  [[ "$old_path" =~ ^# ]] && continue
  [[ -z "$old_path" ]] && continue

  echo "Renaming: $old_path → $new_path"

  # Check file exists
  if [ ! -f "$old_path" ]; then
    echo "  ❌ File not found, skipping"
    continue
  fi

  # Rename
  git mv "$old_path" "$new_path"

  # Update LINK-MAP
  echo "$old_path → $new_path" >> agents/agent-9/governance/LINK-MAP.md

  echo "  ✅ Renamed"
done < "$BATCH_FILE"

echo ""
echo "Batch complete. Run: git status"
EOF

chmod +x /tmp/rename_batch.sh
```

**Execute Batch 1:**

```bash
# Create batch 1 file with old → new pairs
cat > /tmp/batch-1.txt << 'EOF'
docs/planning/Old_Analysis.md → docs/planning/old-analysis.md
docs/planning/Draft_Ideas.md → docs/planning/draft-ideas.md
... (18 more - insert actual files)
EOF

# Run batch rename
/tmp/rename_batch.sh /tmp/batch-1.txt

# Check git status
git status
# Should show 20 renamed files

# Stage and commit
git add -A
git commit -m "feat(migration): Phase 5 Batch 1 - Rename 20 simple files to kebab-case

Files renamed:
- Old_Analysis.md → old-analysis.md
- Draft_Ideas.md → draft-ideas.md
... (18 more)

Naming violations reduced: 92 → 72

Phase 5 Batch 1/4 complete.
Ref: agents/agent-9/governance/PHASE-5-NAMING-CLEANUP.md

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push
git push origin migration/folder-structure-cleanup
```

**Checkpoint 3:** ✅ Batch 1 complete (20 files renamed)

---

### Step 4: Update References for Batch 1

**Search for broken references:**

```bash
# Find references to old filenames
for file in Old_Analysis Draft_Ideas ...; do
  echo "Checking: $file"
  grep -r "$file\.md" docs/ agents/ --include="*.md"
done
```

**Update references (automated):**

```bash
# Example: Update references to Old_Analysis.md
find docs/ agents/ -name "*.md" -type f -exec sed -i '' \
  's|Old_Analysis\.md|old-analysis.md|g' {} +

# Repeat for each renamed file
```

**Or use batch update script:**

```bash
cat > /tmp/update_refs.sh << 'EOF'
#!/bin/bash
# Update references based on LINK-MAP.md

# Extract Phase 5 Batch 1 entries from LINK-MAP
grep -A 25 "Phase 5 Batch 1" agents/agent-9/governance/LINK-MAP.md | \
while IFS='→' read -r old_path new_path; do
  [[ "$old_path" =~ ^# ]] && continue
  [[ -z "$old_path" ]] && continue

  old_name=$(basename "$old_path")
  new_name=$(basename "$new_path")

  echo "Updating refs: $old_name → $new_name"

  find docs/ agents/ -name "*.md" -type f -exec sed -i '' \
    "s|$old_name|$new_name|g" {} +
done

echo "References updated. Run: git diff"
EOF

chmod +x /tmp/update_refs.sh
/tmp/update_refs.sh
```

**Verify and commit:**

```bash
# Check what changed
git diff

# Stage and commit reference updates
git add -A
git commit -m "fix(migration): Phase 5 Batch 1 - Update references to renamed files

Updated references from:
- Old_Analysis.md → old-analysis.md
- Draft_Ideas.md → draft-ideas.md
... (18 more)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push origin migration/folder-structure-cleanup
```

**Checkpoint 4:** ✅ References updated for Batch 1

---

### Step 5: Validate Batch 1

```bash
# Run validation
python scripts/validate_folder_structure.py

# Expected:
# - Naming violations: 92 → 72 (20 fewer)
# - No new errors introduced
# - Total errors: ~41 → ~38

# Check for broken links (if link checker exists)
python scripts/check_links.py docs/ || echo "Link checker not found, manual check needed"
```

**If validation fails:**
- Review error messages
- Check for typos in renames
- Verify references updated correctly
- Rollback batch if needed: `git reset --hard HEAD~2`

**Checkpoint 5:** ✅ Batch 1 validated

---

### Step 6: Repeat for Batches 2-4

**Execute remaining batches using same process:**

**Batch 2: Medium complexity (30 files)**
- Follow Steps 3-5
- More references expected, spend more time on Step 4
- Commit per batch: "Phase 5 Batch 2/4"

**Batch 3: High-impact (20 files)**
- Extra careful with reference updates
- May need manual verification of critical links
- Consider splitting into 2 sub-batches (10 files each)

**Batch 4: Special cases (22 files)**
- Version-prefixed files: decide on `v0.16` vs `v0-16` format
- Manual review for edge cases
- Update any version-specific references

**Recommended pace:**
- **Batch 1:** Day 1 Session 1 (1-2 hours)
- **Batch 2:** Day 1 Session 2 + Day 2 Session 1 (3-4 hours total)
- **Batch 3:** Day 2 Session 2 + Day 3 Session 1 (3-4 hours total)
- **Batch 4:** Day 3 Session 2 (2-3 hours)

**Checkpoint 6:** ✅ All 4 batches complete (92 files renamed)

---

### Step 7: Final Validation

```bash
# Run full validation
python scripts/validate_folder_structure.py

# Expected improvements:
# - Naming violations: 92 → 0 ✅
# - Total errors: ~41 → ~6 (95% reduction from baseline)
# - Only docs/ root file count errors remain

# Verify LINK-MAP.md complete
grep "Phase 5" agents/agent-9/governance/LINK-MAP.md | wc -l
# Should show 92 entries

# Check for broken links
python scripts/check_links.py docs/ agents/ --report

# Manual spot-check
# Open 5-10 renamed files in editor, click links, verify they work
```

**Expected validation output:**
```
✅ Naming conventions: all files compliant (kebab-case)
⚠️  docs/ root still has ~40 files (requires manual cleanup)
✅  agents/ compliant
✅  Dated files compliant

Total errors: ~6 (95% reduction from baseline 115)
```

**Checkpoint 7:** ✅ Final validation passed

---

### Step 8: Consolidate Commits (Optional)

**If you made many small commits (10-20), consider squashing:**

```bash
# View commit history
git log --oneline | head -20

# Interactive rebase to squash (example: last 10 commits)
git rebase -i HEAD~10

# In editor, change "pick" to "squash" for all but first commit
# Save and exit

# Edit consolidated commit message
# Final message:
feat(migration): Phase 5 - Rename 92 files to kebab-case

Renamed 92 files in 4 batches:
- Batch 1: 20 simple files (isolated docs)
- Batch 2: 30 medium files (moderate references)
- Batch 3: 20 high-impact files (many references)
- Batch 4: 22 special cases (version-prefixed)

Updated all internal references to new filenames.
Updated LINK-MAP.md with 92 migration entries.

Validation improvements:
- Naming violations: 92 → 0 (100% fixed)
- Total errors: ~41 → ~6 (95% reduction from baseline)

Phase 5 of 8 complete.
Ref: agents/agent-9/governance/FULL-MIGRATION-EXECUTION-PLAN.md

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

# Force push (only safe on migration branch)
git push origin migration/folder-structure-cleanup --force
```

**Warning:** Only squash if commits not already merged/reviewed.

**Checkpoint 8:** ✅ Commits consolidated (optional)

---

## Validation Checklist

After completing all steps, verify:

- [ ] All 92 files renamed to kebab-case
- [ ] No naming violations in `python scripts/validate_folder_structure.py`
- [ ] LINK-MAP.md has 92 entries for Phase 5
- [ ] All references updated (no broken links)
- [ ] `python scripts/check_links.py` passes (if script exists)
- [ ] Manual spot-check of 10 files confirms links work
- [ ] Validation errors reduced from ~41 to ~6
- [ ] Git history preserved (files show as "renamed")
- [ ] Changes committed with descriptive messages
- [ ] Migration branch pushed to remote
- [ ] Special files (TASKS.md, README.md, etc.) NOT renamed

---

## Special Cases Handling

### Case 1: Version-Prefixed Files

**Example:** `v0.16-Task_Specs.md`

**Option A: Keep version dots (recommended)**
```
v0.16-Task_Specs.md → v0.16-task-specs.md
v0.15-Design_Doc.md → v0.15-design-doc.md
```

**Option B: All kebab-case**
```
v0.16-Task_Specs.md → v0-16-task-specs.md
v0.15-Design_Doc.md → v0-15-design-doc.md
```

**Recommendation:** Option A (preserve semantic versioning dots)

### Case 2: Acronyms

**Example:** `API_Design.md`, `HTTP_Guide.md`

**Correct kebab-case:**
```
API_Design.md → api-design.md  (lowercase acronym)
HTTP_Guide.md → http-guide.md
```

**Not:** `API-Design.md`, `HTTP-Guide.md` (violates kebab-case)

### Case 3: Numbers in Names

**Example:** `Phase_3_Plan.md`, `Step1_Guide.md`

**Correct kebab-case:**
```
Phase_3_Plan.md → phase-3-plan.md
Step1_Guide.md → step-1-guide.md  (add hyphen before number)
```

### Case 4: Multiple Underscores

**Example:** `New_Feature_Implementation_Guide.md`

**Correct kebab-case:**
```
New_Feature_Implementation_Guide.md → new-feature-implementation-guide.md
```

**Single pass conversion:** Replace all `_` with `-`, then lowercase

### Case 5: Mixed Case Files

**Example:** `TaskSpecs.md` (PascalCase)

**Correct kebab-case:**
```
TaskSpecs.md → task-specs.md
```

**Conversion:** Insert hyphens before capitals, lowercase all

---

## Automation Scripts

### Script 1: Bulk Rename with Validation

```bash
cat > /tmp/bulk_rename.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Bulk rename with validation
# Usage: ./bulk_rename.sh <batch-file>

BATCH_FILE=$1
ERRORS=0

while IFS='→' read -r old new; do
  old=$(echo "$old" | xargs)
  new=$(echo "$new" | xargs)

  [[ "$old" =~ ^# ]] && continue
  [[ -z "$old" ]] && continue

  # Validate new name is kebab-case
  if ! [[ $(basename "$new") =~ ^[a-z0-9\-]+\.md$ ]]; then
    echo "❌ Invalid kebab-case: $new"
    ((ERRORS++))
    continue
  fi

  # Check file exists
  if [ ! -f "$old" ]; then
    echo "❌ File not found: $old"
    ((ERRORS++))
    continue
  fi

  # Rename
  git mv "$old" "$new"
  echo "✅ $old → $new"

  # Update LINK-MAP
  echo "$old → $new" >> agents/agent-9/governance/LINK-MAP.md
done < "$BATCH_FILE"

if [ $ERRORS -gt 0 ]; then
  echo ""
  echo "⚠️  $ERRORS errors found. Review before committing."
  exit 1
else
  echo ""
  echo "✅ Batch complete. No errors."
  exit 0
fi
EOF

chmod +x /tmp/bulk_rename.sh
```

### Script 2: Find and Update References

```bash
cat > /tmp/fix_refs.sh << 'EOF'
#!/bin/bash
# Fix references based on LINK-MAP.md

PHASE_SECTION="Phase 5 Batch"

grep "$PHASE_SECTION" agents/agent-9/governance/LINK-MAP.md -A 100 | \
while IFS='→' read -r old new; do
  [[ "$old" =~ ^# ]] && continue
  [[ -z "$old" ]] && continue

  old_name=$(basename "$old")
  new_name=$(basename "$new")

  # Skip if same
  [[ "$old_name" == "$new_name" ]] && continue

  echo "Updating: $old_name → $new_name"

  # Update references (case-sensitive)
  find docs/ agents/ -name "*.md" -type f -exec sed -i '' \
    "s|$old_name|$new_name|g" {} +
done

echo "References updated."
EOF

chmod +x /tmp/fix_refs.sh
```

### Script 3: Validate Kebab-Case Name

```python
#!/usr/bin/env python3
# /tmp/validate_kebab.py

import re
import sys

def is_valid_kebab(name):
    """Check if filename is valid kebab-case."""
    # Pattern: lowercase letters, numbers, hyphens, .md extension
    pattern = r'^[a-z0-9\-]+\.md$'

    # Exceptions
    exceptions = ['README.md', 'TASKS.md', 'SESSION_LOG.md', 'CHANGELOG.md', 'TODO.md']
    if name in exceptions:
        return True

    return bool(re.match(pattern, name))

def to_kebab_case(name):
    """Convert filename to kebab-case."""
    base, ext = name.rsplit('.', 1)

    # Replace underscores with hyphens
    base = base.replace('_', '-')

    # Insert hyphens before capitals (PascalCase → kebab-case)
    base = re.sub(r'([a-z])([A-Z])', r'\1-\2', base)

    # Lowercase
    base = base.lower()

    return f"{base}.{ext}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_kebab.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    if is_valid_kebab(filename):
        print(f"✅ Valid kebab-case: {filename}")
    else:
        suggestion = to_kebab_case(filename)
        print(f"❌ Invalid: {filename}")
        print(f"💡 Suggest: {suggestion}")
        sys.exit(1)
```

---

## Rollback Procedure

**If Phase 5 fails or produces wrong results:**

```bash
# Undo all Phase 5 commits
git log --oneline | grep "Phase 5"
# Count commits (e.g., 12 commits)

# Reset to before Phase 5
git reset --hard HEAD~12

# Or reset to specific commit
git reset --hard <commit-before-phase-5>

# Or use backup tag if needed
git reset --hard backup-pre-migration-2026-01-10

# Force push
git push origin migration/folder-structure-cleanup --force
```

**See:** [ROLLBACK-PROCEDURES.md](ROLLBACK-PROCEDURES.md) for detailed recovery.

---

## Expected Error Reduction

**Before Phase 5:**
- ❌ ~41 total errors (after Phases 1-4)
- ❌ Naming violations: 92

**After Phase 5:**
- ✅ ~6 total errors (95% reduction from baseline)
- ✅ Naming violations: 0

**Progress:** 95% of migration complete (only docs/ root cleanup remains)

---

## Time Estimates (Per Batch)

**Batch 1 (20 files, simple):**
- Rename: 30 minutes
- Update refs: 20 minutes (few references)
- Validate: 10 minutes
- Commit: 10 minutes
- **Total:** 1-1.5 hours

**Batch 2 (30 files, medium):**
- Rename: 45 minutes
- Update refs: 60 minutes (moderate references)
- Validate: 15 minutes
- Commit: 10 minutes
- **Total:** 2-2.5 hours

**Batch 3 (20 files, high-impact):**
- Rename: 30 minutes
- Update refs: 90 minutes (many references)
- Validate: 20 minutes
- Commit: 10 minutes
- **Total:** 2.5-3 hours

**Batch 4 (22 files, special cases):**
- Rename: 45 minutes (manual decisions)
- Update refs: 60 minutes
- Validate: 15 minutes
- Commit: 10 minutes
- **Total:** 2-2.5 hours

**Phase Total:** 8-10 hours

---

## Common Issues

### Issue 1: `sed` not updating references

**Cause:** Special characters in filename not escaped

**Solution:**
```bash
# Escape dots
sed -i '' 's|Old_File\.md|old-file.md|g' *.md

# Use different delimiter if path has slashes
sed -i '' 's@docs/Old_File.md@docs/old-file.md@g' *.md
```

### Issue 2: Case-sensitive filesystem issues

**Cause:** Renaming `File.md` → `file.md` on case-insensitive filesystem

**Solution:**
```bash
# Two-step rename
git mv File.md File-temp.md
git mv File-temp.md file.md
```

### Issue 3: References still broken after update

**Cause:** References use different path formats (relative vs absolute)

**Solution:**
```bash
# Update all path formats
sed -i '' 's|docs/Old_File\.md|docs/old-file.md|g' *.md
sed -i '' 's|/docs/Old_File\.md|/docs/old-file.md|g' *.md
sed -i '' 's|\.\./Old_File\.md|../old-file.md|g' *.md
```

### Issue 4: Git shows "deleted + added" instead of "renamed"

**Cause:** Too many content changes or large files

**Solution:**
```bash
# Increase rename detection threshold
git config merge.renameLimit 9999
git config diff.renameLimit 9999

# Re-stage files
git add -A
```

---

## Next Steps

After Phase 5 completion:

1. **Update MIGRATION-STATUS.md** to mark Phase 5 complete
2. **Proceed to Phase 6** (link fixing) - critical to fix all broken links
3. **Or proceed to Phase 3** if skipped earlier (docs/ categorization)

**Recommended:** Complete Phase 6 next since naming changes likely broke some links.

---

## Success Criteria

Phase 5 is complete when:

1. ✅ All 92 files renamed to kebab-case
2. ✅ Zero naming violations in validation
3. ✅ All references updated (no broken links)
4. ✅ LINK-MAP.md has 92 entries
5. ✅ Validation errors reduced to ~6
6. ✅ Special files (TASKS.md, README.md, etc.) preserved
7. ✅ Git history preserved (renames tracked)
8. ✅ Changes committed and pushed

---

**Phase 5 Status:** 📋 Ready for execution
**Last Updated:** 2026-01-10
**Next Phase:** [PHASE-6-LINK-FIXING.md](PHASE-6-LINK-FIXING.md)
