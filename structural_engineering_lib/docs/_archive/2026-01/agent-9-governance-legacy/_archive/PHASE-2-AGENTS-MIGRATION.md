# Phase 2: Agents Migration

**Duration:** 3-4 hours
**Complexity:** Medium
**Risk:** Low
**Validation Impact:** 115 errors → ~103 errors (10% reduction)

---

## Overview

Move all agent role files from `agents/` root to `agents/roles/` subdirectory and rename from UPPERCASE to kebab-case.

**Current State:**
```
agents/
├── README.md (only file allowed in root)
├── AGENT-1-RESEARCH.md ❌ (should be in roles/)
├── AGENT-2-PLANNING.md ❌
├── AGENT-3-IMPLEMENTATION.md ❌
├── AGENT-4-TESTING.md ❌
├── AGENT-5-DOCUMENTATION.md ❌
├── AGENT-6-REFACTORING.md ❌
├── AGENT-7-PERFORMANCE.md ❌
├── AGENT-8-SECURITY.md ❌
├── AGENT-9-GOVERNANCE.md ❌
├── AGENT-10-INTEGRATION.md ❌
├── AGENT-11-DEPLOYMENT.md ❌
└── AGENT-12-MONITORING.md ❌
```

**Target State:**
```
agents/
├── README.md ✅
└── roles/
    ├── README.md ✅
    ├── agent-1-research.md ✅
    ├── agent-2-planning.md ✅
    ├── agent-3-implementation.md ✅
    ├── agent-4-testing.md ✅
    ├── agent-5-documentation.md ✅
    ├── agent-6-refactoring.md ✅
    ├── agent-7-performance.md ✅
    ├── agent-8-security.md ✅
    ├── agent-9-governance.md ✅
    ├── agent-10-integration.md ✅
    ├── agent-11-deployment.md ✅
    └── agent-12-monitoring.md ✅
```

---

## Prerequisites

- ✅ Phase 0 complete (backup created, tools installed)
- ✅ Phase 1 complete (folder structure exists)
- ✅ Working tree is clean
- ✅ Migration branch active
- ✅ Freeze window in effect (no parallel work)

---

## Step-by-Step Execution

### Step 1: Verify Current State

```bash
# Verify Phase 1 completed successfully
ls -la agents/roles/
# Should show README.md created in Phase 1

# Count current files in agents/ root
ls -1 agents/*.md | wc -l
# Should show 13 files (12 agent files + README.md)

# Run validation to confirm baseline
python scripts/validate_folder_structure.py
# Should show ~103-115 errors with agents/ violations
```

**Expected output:**
```
agents/ root has 13 files, max is 1
  Files: ['README.md', 'AGENT-1-RESEARCH.md', 'AGENT-2-PLANNING.md', ...]
```

**Checkpoint 1:** ✅ Current state confirmed

---

### Step 2: Move and Rename Agent Files

**Move all agent role files to agents/roles/ with kebab-case names:**

```bash
# Navigate to project root
cd /path/to/structural_engineering_lib

# Move and rename all agent files (preserving git history)
git mv agents/AGENT-1-RESEARCH.md agents/roles/agent-1-research.md
git mv agents/AGENT-2-PLANNING.md agents/roles/agent-2-planning.md
git mv agents/AGENT-3-IMPLEMENTATION.md agents/roles/agent-3-implementation.md
git mv agents/AGENT-4-TESTING.md agents/roles/agent-4-testing.md
git mv agents/AGENT-5-DOCUMENTATION.md agents/roles/agent-5-documentation.md
git mv agents/AGENT-6-REFACTORING.md agents/roles/agent-6-refactoring.md
git mv agents/AGENT-7-PERFORMANCE.md agents/roles/agent-7-performance.md
git mv agents/AGENT-8-SECURITY.md agents/roles/agent-8-security.md
git mv agents/AGENT-9-GOVERNANCE.md agents/roles/agent-9-governance.md
git mv agents/AGENT-10-INTEGRATION.md agents/roles/agent-10-integration.md
git mv agents/AGENT-11-DEPLOYMENT.md agents/roles/agent-11-deployment.md
git mv agents/AGENT-12-MONITORING.md agents/roles/agent-12-monitoring.md
```

**Why `git mv`?**
- Preserves file history for git blame
- Tracks renames properly
- Better for future archaeology

**Checkpoint 2:** ✅ Files moved and renamed

---

### Step 3: Verify Move Completed

```bash
# Verify agents/ root now has only README.md
ls -1 agents/*.md
# Should show ONLY: agents/README.md

# Verify all files moved to agents/roles/
ls -1 agents/roles/*.md
# Should show 13 files (12 agent files + README.md)

# Check git status
git status
# Should show 12 renamed files
```

**Expected git status:**
```
On branch migration/folder-structure-cleanup
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	renamed:    agents/AGENT-1-RESEARCH.md -> agents/roles/agent-1-research.md
	renamed:    agents/AGENT-2-PLANNING.md -> agents/roles/agent-2-planning.md
	... (10 more)
```

**Checkpoint 3:** ✅ Move verified

---

### Step 4: Update Internal References

**Find all references to old agent file paths:**

```bash
# Search for references to old AGENT-* paths
grep -r "agents/AGENT-" docs/ agents/ --include="*.md"

# Common patterns to find:
# - [Agent 9](agents/AGENT-9-GOVERNANCE.md)
# - See agents/AGENT-9-GOVERNANCE.md
# - Ref: agents/AGENT-9-GOVERNANCE.md
```

**Update all references to new paths:**

Use find-and-replace across all markdown files:

```bash
# Agent 1
find docs/ agents/ -name "*.md" -type f -exec sed -i '' 's|agents/AGENT-1-RESEARCH\.md|agents/roles/agent-1-research.md|g' {} +

# Agent 2
find docs/ agents/ -name "*.md" -type f -exec sed -i '' 's|agents/AGENT-2-PLANNING\.md|agents/roles/agent-2-planning.md|g' {} +

# Agent 3
find docs/ agents/ -name "*.md" -type f -exec sed -i '' 's|agents/AGENT-3-IMPLEMENTATION\.md|agents/roles/agent-3-implementation.md|g' {} +

# Agent 4
find docs/ agents/ -name "*.md" -type f -exec sed -i '' 's|agents/AGENT-4-TESTING\.md|agents/roles/agent-4-testing.md|g' {} +

# Agent 5
find docs/ agents/ -name "*.md" -type f -exec sed -i '' 's|agents/AGENT-5-DOCUMENTATION\.md|agents/roles/agent-5-documentation.md|g' {} +

# Agent 6
find docs/ agents/ -name "*.md" -type f -exec sed -i '' 's|agents/AGENT-6-REFACTORING\.md|agents/roles/agent-6-refactoring.md|g' {} +

# Agent 7
find docs/ agents/ -name "*.md" -type f -exec sed -i '' 's|agents/AGENT-7-PERFORMANCE\.md|agents/roles/agent-7-performance.md|g' {} +

# Agent 8
find docs/ agents/ -name "*.md" -type f -exec sed -i '' 's|agents/AGENT-8-SECURITY\.md|agents/roles/agent-8-security.md|g' {} +

# Agent 9 (most commonly referenced)
find docs/ agents/ -name "*.md" -type f -exec sed -i '' 's|agents/AGENT-9-GOVERNANCE\.md|agents/roles/agent-9-governance.md|g' {} +

# Agent 10
find docs/ agents/ -name "*.md" -type f -exec sed -i '' 's|agents/AGENT-10-INTEGRATION\.md|agents/roles/agent-10-integration.md|g' {} +

# Agent 11
find docs/ agents/ -name "*.md" -type f -exec sed -i '' 's|agents/AGENT-11-DEPLOYMENT\.md|agents/roles/agent-11-deployment.md|g' {} +

# Agent 12
find docs/ agents/ -name "*.md" -type f -exec sed -i '' 's|agents/AGENT-12-MONITORING\.md|agents/roles/agent-12-monitoring.md|g' {} +
```

**Verify no old references remain:**

```bash
# This should return nothing
grep -r "agents/AGENT-" docs/ agents/ --include="*.md"
```

**Checkpoint 4:** ✅ References updated

---

### Step 5: Update LINK-MAP.md

Add entries to track this migration:

```bash
# Append to agents/agent-9/governance/LINK-MAP.md
cat >> agents/agent-9/governance/LINK-MAP.md << 'EOF'

# Phase 2: Agents Migration (2026-01-10)
agents/AGENT-1-RESEARCH.md → agents/roles/agent-1-research.md
agents/AGENT-2-PLANNING.md → agents/roles/agent-2-planning.md
agents/AGENT-3-IMPLEMENTATION.md → agents/roles/agent-3-implementation.md
agents/AGENT-4-TESTING.md → agents/roles/agent-4-testing.md
agents/AGENT-5-DOCUMENTATION.md → agents/roles/agent-5-documentation.md
agents/AGENT-6-REFACTORING.md → agents/roles/agent-6-refactoring.md
agents/AGENT-7-PERFORMANCE.md → agents/roles/agent-7-performance.md
agents/AGENT-8-SECURITY.md → agents/roles/agent-8-security.md
agents/AGENT-9-GOVERNANCE.md → agents/roles/agent-9-governance.md
agents/AGENT-10-INTEGRATION.md → agents/roles/agent-10-integration.md
agents/AGENT-11-DEPLOYMENT.md → agents/roles/agent-11-deployment.md
agents/AGENT-12-MONITORING.md → agents/roles/agent-12-monitoring.md
EOF
```

**Checkpoint 5:** ✅ Link map updated

---

### Step 6: Validate Changes

```bash
# Run validation script
python scripts/validate_folder_structure.py

# Expected improvements:
# - agents/ violations: 13 → 1 (only README.md remains) ✅
# - Naming violations: reduced by 12 (AGENT-* → agent-*) ✅
# - Total errors: ~115 → ~103 (10% reduction) ✅
```

**Expected validation output:**
```
✅ agents/ root has 1 file (within limit)
⚠️  docs/ root still has 44 files (will fix in Phase 3)
⚠️  Dated files still misplaced (will fix in Phase 4)
```

**If validation fails:**
- Check Step 2 completed (all files moved?)
- Check Step 3 verified (agents/ root clean?)
- Review error messages for specific issues

**Checkpoint 6:** ✅ Validation improved

---

### Step 7: Test Agent References

**Manually verify a few agent references work:**

```bash
# Test Agent 9 references (most commonly used)
grep -r "agent-9-governance" docs/ agents/ --include="*.md" | head -5

# Spot-check a few files:
# - agents/agent-9/governance/FULL-MIGRATION-EXECUTION-PLAN.md
# - agents/README.md
# - Any docs/agents/ files
```

**Open 2-3 files in editor and verify links render correctly.**

**Checkpoint 7:** ✅ Links tested

---

### Step 8: Commit Changes

```bash
# Stage all changes (renames + reference updates)
git add -A

# Create commit with descriptive message
git commit -m "$(cat <<'EOF'
feat(migration): Phase 2 - Migrate agent files to agents/roles/

- Move 12 agent role files from agents/ to agents/roles/
- Rename from UPPERCASE (AGENT-N-*) to kebab-case (agent-n-*)
- Update all internal references to new paths
- Update LINK-MAP.md with migration mappings

Validation improvements:
- agents/ violations: 13 → 1 (92% reduction)
- Naming violations: reduced by 12
- Total errors: ~115 → ~103 (10% reduction)

Phase 2 of 8 complete.
Ref: agents/agent-9/governance/FULL-MIGRATION-EXECUTION-PLAN.md

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# Push to migration branch
git push origin migration/folder-structure-cleanup
```

**Checkpoint 8:** ✅ Changes committed and pushed

---

## Validation Checklist

After completing all steps, verify:

- [ ] `agents/` root contains ONLY `README.md` (1 file)
- [ ] `agents/roles/` contains 13 files (12 agent files + README.md)
- [ ] All agent files renamed to kebab-case (agent-1-research.md, etc.)
- [ ] All internal references updated (no broken links)
- [ ] `grep -r "agents/AGENT-" docs/ agents/` returns nothing
- [ ] LINK-MAP.md updated with 12 migration entries
- [ ] Validation errors reduced from ~115 to ~103
- [ ] `python scripts/validate_folder_structure.py` shows agents/ compliance ✅
- [ ] Git history preserved (files show as "renamed" not "deleted + added")
- [ ] Changes committed with descriptive message
- [ ] Migration branch pushed to remote

---

## Rollback Procedure

**If this phase fails, rollback:**

```bash
# Undo last commit (keeps changes in working tree)
git reset --soft HEAD~1

# Or completely reset to pre-Phase 2 state
git reset --hard origin/migration/folder-structure-cleanup

# Or restore from backup tag
git reset --hard backup-pre-migration-2026-01-10
```

**See:** [ROLLBACK-PROCEDURES.md](ROLLBACK-PROCEDURES.md) for detailed recovery steps.

---

## Expected Error Reduction

**Before Phase 2:**
- ❌ 115 total errors
- ❌ agents/ root: 13 files (12 over limit)
- ❌ Naming violations: 92 (includes 12 UPPERCASE agent files)

**After Phase 2:**
- ✅ ~103 total errors (10% reduction)
- ✅ agents/ root: 1 file (compliant)
- ✅ Naming violations: ~80 (12 fewer)

**Progress:** 10% of migration complete (agents/ violations FIXED)

---

## Time Estimates

- **Step 1 (Verify):** 5 minutes
- **Step 2 (Move files):** 10 minutes
- **Step 3 (Verify move):** 5 minutes
- **Step 4 (Update references):** 60-90 minutes (manual checking)
- **Step 5 (Update link map):** 5 minutes
- **Step 6 (Validate):** 10 minutes
- **Step 7 (Test links):** 30 minutes
- **Step 8 (Commit):** 10 minutes

**Total:** 3-4 hours

---

## Common Issues

### Issue 1: `sed` command not working (macOS vs Linux)

**macOS:** Requires `-i ''` flag
**Linux:** Use `-i` without quotes

**Solution:**
```bash
# macOS
sed -i '' 's|old|new|g' file.md

# Linux
sed -i 's|old|new|g' file.md
```

### Issue 2: References not updating

**Cause:** Special characters in filenames not escaped

**Solution:** Use `\.md` instead of `.md` in regex patterns

### Issue 3: Git showing files as "deleted + added" instead of "renamed"

**Cause:** Too many content changes or threshold exceeded

**Solution:**
```bash
# Lower rename detection threshold
git config merge.renameLimit 9999
git add -A
git commit
```

### Issue 4: Validation still shows errors

**Cause:** Cache or stale run

**Solution:**
```bash
# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +

# Re-run validation
python scripts/validate_folder_structure.py
```

---

## Next Steps

After Phase 2 completion:

1. **Update MIGRATION-STATUS.md** to mark Phase 2 complete
2. **Proceed to Phase 3** (docs/ migration - largest phase)
3. **Or proceed to Phase 4** if deferring Phase 3 complexity

**Recommended:** Complete Phase 4 (dated files) next since it's automated and quick.

---

## Success Criteria

Phase 2 is complete when:

1. ✅ `agents/` root has exactly 1 file (README.md)
2. ✅ All 12 agent files in `agents/roles/` with kebab-case names
3. ✅ All internal references updated (no broken links)
4. ✅ Validation shows agents/ compliance
5. ✅ Error count reduced by ~10%
6. ✅ Changes committed and pushed
7. ✅ Git history preserved (renames tracked)

---

**Phase 2 Status:** 📋 Ready for execution
**Last Updated:** 2026-01-10
**Next Phase:** [PHASE-3-DOCS-MIGRATION.md](PHASE-3-DOCS-MIGRATION.md) or [PHASE-4-DATED-FILES.md](PHASE-4-DATED-FILES.md)
