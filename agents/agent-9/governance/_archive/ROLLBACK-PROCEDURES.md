# Migration Rollback Procedures

**Purpose:** Emergency recovery procedures if migration phases fail
**Risk Level:** Safety-critical document
**Last Updated:** 2026-01-10

---

## Overview

This document provides step-by-step rollback procedures for each migration phase. Use these if:
- A phase fails validation
- You need to undo changes
- Breaking changes occur
- You want to start over

**Golden Rule:** Always prefer forward fixes over rollback, but know how to rollback safely.

---

## Backup Verification

**Before ANY rollback, verify backups exist:**

```bash
# Check backup tag exists
git tag -l "backup-pre-migration-*"
# Should show: backup-pre-migration-2026-01-10

# Check local backup exists
ls -la ../structural_engineering_lib-backup-2026-01-10/
# Should show backup directory

# Check migration branch exists
git branch -a | grep migration
# Should show: migration/folder-structure-cleanup
```

**If backups don't exist, STOP. Create backups before proceeding.**

---

## Rollback Levels

### Level 1: Undo Last Commit (Soft Reset)

**Use when:**
- Last commit has issues but work is salvageable
- You want to re-commit with fixes
- Working tree changes are valuable

```bash
# Undo last commit, keep changes in staging area
git reset --soft HEAD~1

# Or undo last commit, keep changes in working tree (unstaged)
git reset HEAD~1

# Review changes
git status
git diff

# Fix issues, then re-commit
git add -A
git commit -m "Fixed commit message"
```

**Risk:** Low (no work lost)

---

### Level 2: Hard Reset to Previous Commit

**Use when:**
- Last commit is completely wrong
- You want to discard all changes
- Working tree is corrupted

```bash
# WARNING: This discards all uncommitted changes!

# Hard reset to previous commit
git reset --hard HEAD~1

# Or reset to specific commit
git reset --hard <commit-sha>

# Force push if already pushed (use with caution)
git push origin migration/folder-structure-cleanup --force
```

**Risk:** Medium (uncommitted work lost)

---

### Level 3: Reset to Pre-Phase State

**Use when:**
- Entire phase failed
- Multiple commits need undoing
- Want to retry phase from start

```bash
# Find commit hash before phase started
git log --oneline | head -20

# Reset to that commit
git reset --hard <commit-before-phase>

# Or use backup tag
git reset --hard backup-pre-migration-2026-01-10

# Force push if needed
git push origin migration/folder-structure-cleanup --force
```

**Risk:** Medium-High (phase work lost)

---

### Level 4: Nuclear Option (Full Backup Restore)

**Use when:**
- Migration branch is completely broken
- Git history is corrupted
- Want to start migration from scratch

```bash
# Delete migration branch
git checkout main
git branch -D migration/folder-structure-cleanup

# Restore from backup tag
git checkout -b migration/folder-structure-cleanup backup-pre-migration-2026-01-10

# Or restore from local backup
rm -rf .git
cp -r ../structural_engineering_lib-backup-2026-01-10/.git .
git status

# Force push new branch
git push origin migration/folder-structure-cleanup --force
```

**Risk:** High (all migration work lost)

---

## Phase-Specific Rollback Procedures

### Phase 0: Preparation Rollback

**Rarely needed** (no file changes, only setup)

**If backup tag failed:**
```bash
# Delete bad tag
git tag -d backup-pre-migration-2026-01-10

# Recreate tag
git tag backup-pre-migration-2026-01-10 main
git push origin backup-pre-migration-2026-01-10
```

**If migration branch exists but shouldn't:**
```bash
git checkout main
git branch -D migration/folder-structure-cleanup
```

---

### Phase 1: Structure Creation Rollback

**Symptoms:**
- Directories created incorrectly
- README.md files have wrong content
- Validation fails after structure creation

**Rollback Steps:**

```bash
# Option A: Undo last commit (if just committed)
git reset --soft HEAD~1

# Remove created directories
rm -rf agents/roles agents/guides agents/templates
rm -rf docs/agents/roles docs/agents/guides docs/agents/sessions
rm -rf docs/getting-started docs/reference docs/contributing
rm -rf docs/architecture agents/agent-9/governance docs/images
rm -rf docs/_active docs/_archive

# Verify clean state
git status
# Should show: nothing to commit, working tree clean

# Option B: Hard reset if already pushed
git reset --hard backup-pre-migration-2026-01-10
```

**Re-execute Phase 1:**
- Fix issues identified
- Re-run [PHASE-1-STRUCTURE-CREATION.md](PHASE-1-STRUCTURE-CREATION.md)
- Validate before committing

---

### Phase 2: Agents Migration Rollback

**Symptoms:**
- Agent files moved to wrong location
- References broken
- Naming incorrect
- Validation shows agents/ violations

**Rollback Steps:**

```bash
# Undo commits (adjust count as needed)
git reset --hard HEAD~1

# Or reset to before Phase 2
git log --oneline | grep "Phase 1"
# Note the commit hash
git reset --hard <phase-1-commit-hash>

# Verify agents/ state
ls -la agents/
# Should show 13 files (AGENT-*.md files back)

# Verify agents/roles/ is empty or doesn't exist
ls -la agents/roles/
```

**Re-execute Phase 2:**
- Review [PHASE-2-AGENTS-MIGRATION.md](PHASE-2-AGENTS-MIGRATION.md)
- Fix identified issues (check sed syntax, reference patterns)
- Re-run with corrections

---

### Phase 3: Docs Migration Rollback

**Symptoms:**
- Docs moved to wrong subdirectories
- Critical files missing
- Categorization incorrect
- Validation worse after migration

**Rollback Steps:**

```bash
# This phase has MANY commits, reset carefully
git log --oneline | grep "Phase 3"
# Find first commit of Phase 3

# Reset to before Phase 3
git reset --hard <commit-before-phase-3>

# Verify docs/ root restored
ls -la docs/*.md | wc -l
# Should show ~44 files back

# Verify subdirectories emptied
ls -la docs/getting-started/
ls -la docs/reference/
# Should show only README.md in each
```

**Re-execute Phase 3:**
- Review categorization decisions
- Use more conservative approach (move fewer files first)
- Validate after each batch of 10 files

---

### Phase 4: Dated Files Rollback

**Symptoms:**
- Dated files archived incorrectly
- Active files archived by mistake
- Archive structure wrong

**Rollback Steps:**

```bash
# Undo archive commits
git reset --hard HEAD~1

# Or if using archive script, reverse moves manually
# Check LINK-MAP.md for moved files
cat agents/agent-9/governance/LINK-MAP.md | grep "Phase 4"

# Restore each file (example)
git mv docs/_archive/2026-01/file-2025-12-15.md docs/planning/file-2025-12-15.md

# Verify dated files restored
find docs/ -name "*-202[0-9]-*" -type f
```

**Re-execute Phase 4:**
- Review dated file criteria (is it truly inactive?)
- Test archive script with `--dry-run` first
- Archive in smaller batches

---

### Phase 5: Naming Cleanup Rollback

**Symptoms:**
- Files renamed incorrectly
- References broken
- Validation shows new naming violations

**Rollback Steps:**

```bash
# Undo rename commits (may be many)
git log --oneline | grep "Phase 5"
# Count commits

# Reset to before Phase 5
git reset --hard <commit-before-phase-5>

# Or cherry-pick successful renames
git reset --hard <before-phase-5>
git cherry-pick <good-commit-1>
git cherry-pick <good-commit-2>
# Skip bad commits
```

**Re-execute Phase 5:**
- Rename in smaller batches (5-10 files at a time)
- Validate after each batch
- Update references immediately after rename

---

### Phase 6: Link Fixing Rollback

**Symptoms:**
- Links broken after fixing
- Wrong link patterns used
- References point to non-existent files

**Rollback Steps:**

```bash
# Undo link fixing commits
git reset --hard HEAD~1

# Or restore specific files
git checkout HEAD~1 -- docs/path/to/file.md

# Verify links restored
grep -r "\[.*\](.*)" docs/ | grep "broken-link"
```

**Re-execute Phase 6:**
- Use link checker first: `python scripts/check_links.py`
- Fix links in batches (one subdirectory at a time)
- Validate each batch before moving to next

---

### Phase 7: Script Updates Rollback

**Symptoms:**
- Scripts broken after update
- Hardcoded paths wrong
- CI/CD failing

**Rollback Steps:**

```bash
# Undo script update commits
git reset --hard HEAD~1

# Or restore individual scripts
git checkout HEAD~1 -- scripts/validate_folder_structure.py
git checkout HEAD~1 -- scripts/archive_old_docs.py

# Test scripts
python scripts/validate_folder_structure.py
python scripts/archive_old_docs.py --dry-run
```

**Re-execute Phase 7:**
- Update one script at a time
- Test each script after update
- Don't commit until all scripts tested

---

### Phase 8: Final Validation Rollback

**Rarely needed** (no file changes, only validation)

**If final report incorrect:**
```bash
# Re-run validation
python scripts/validate_folder_structure.py --report

# Re-generate metrics
python scripts/generate_health_report.py
```

---

## Emergency Recovery Procedures

### Scenario 1: Accidentally Deleted Files

```bash
# If not yet committed
git checkout -- <file-path>

# If committed but not pushed
git reset --hard HEAD~1

# If already pushed
git revert <commit-hash>

# Or restore from backup
cp ../structural_engineering_lib-backup-2026-01-10/path/to/file .
```

### Scenario 2: Git History Corrupted

```bash
# Clone fresh from remote
cd ..
git clone https://github.com/user/structural_engineering_lib.git structural_engineering_lib-fresh
cd structural_engineering_lib-fresh

# Or restore .git from backup
rm -rf .git
cp -r ../structural_engineering_lib-backup-2026-01-10/.git .
git status
```

### Scenario 3: Merge Conflicts During Rollback

```bash
# Abort merge
git merge --abort

# Or force reset
git reset --hard origin/migration/folder-structure-cleanup
```

### Scenario 4: Lost Commit (Dangling)

```bash
# Find lost commits
git reflog

# Restore lost commit
git checkout <commit-hash>
git checkout -b recovery-branch

# Cherry-pick lost work
git checkout migration/folder-structure-cleanup
git cherry-pick <lost-commit-hash>
```

### Scenario 5: Backup Tag Deleted

```bash
# Check remote tags
git ls-remote --tags origin

# Fetch remote tag
git fetch origin backup-pre-migration-2026-01-10

# Or recreate from known good commit
git tag backup-pre-migration-2026-01-10 <commit-hash>
git push origin backup-pre-migration-2026-01-10
```

---

## Verification After Rollback

**Always verify rollback success:**

```bash
# 1. Check git status
git status
# Should be clean or show expected state

# 2. Run validation
python scripts/validate_folder_structure.py
# Should show expected error count

# 3. Verify file counts
ls -la docs/*.md | wc -l
ls -la agents/*.md | wc -l

# 4. Check critical files exist
test -f README.md && echo "✅ Root README exists"
test -f docs/README.md && echo "✅ Docs README exists"
test -f agents/README.md && echo "✅ Agents README exists"

# 5. Verify no broken links (if link checker exists)
python scripts/check_links.py
```

---

## Prevention Best Practices

**Avoid needing rollback:**

1. **Validate before committing** - Always run `python scripts/validate_folder_structure.py` before commit
2. **Commit often** - Small commits are easier to rollback
3. **Test in batches** - Don't move 50 files at once
4. **Read phase docs carefully** - Follow step-by-step procedures
5. **Use dry-run flags** - Test scripts with `--dry-run` first
6. **Keep backup tag** - Don't delete backup tag until migration complete
7. **Branch protection** - Don't merge to main until all phases complete
8. **Freeze window** - No parallel work during migration

---

## Rollback Decision Tree

```
Issue Detected
    │
    ├─ Just committed? (< 5 min ago)
    │   └─> Level 1: Soft Reset (git reset --soft HEAD~1)
    │
    ├─ Wrong changes, need to discard?
    │   └─> Level 2: Hard Reset (git reset --hard HEAD~1)
    │
    ├─ Entire phase failed?
    │   └─> Level 3: Reset to Pre-Phase (git reset --hard <phase-N-1-commit>)
    │
    ├─ Migration completely broken?
    │   └─> Level 4: Backup Restore (git reset --hard backup-pre-migration-2026-01-10)
    │
    └─ Not sure?
        └─> Ask for help, read this doc carefully
```

---

## Common Rollback Mistakes

### Mistake 1: Using `git reset --hard` without backup

**Problem:** Loses all uncommitted work

**Solution:** Always `git stash` or commit before hard reset

```bash
# Save work first
git stash save "WIP before rollback"

# Do rollback
git reset --hard HEAD~1

# Restore work if needed
git stash pop
```

### Mistake 2: Force pushing to main branch

**Problem:** Rewrites shared history, breaks team

**Solution:** Only force push to migration branch

```bash
# NEVER do this
git push origin main --force  # ❌

# OK for migration branch
git push origin migration/folder-structure-cleanup --force  # ✅
```

### Mistake 3: Deleting backup tag too early

**Problem:** Can't recover if something goes wrong later

**Solution:** Keep backup tag until migration 100% complete and merged

```bash
# Don't delete tag until after merge to main
git tag -d backup-pre-migration-2026-01-10  # ❌ Too early

# Wait until migration merged and validated on main
git checkout main
python scripts/validate_folder_structure.py  # ✅ All green
git tag -d backup-pre-migration-2026-01-10  # ✅ Now safe
```

### Mistake 4: Not verifying rollback succeeded

**Problem:** May roll back to wrong state

**Solution:** Always run validation after rollback

```bash
# After any rollback
python scripts/validate_folder_structure.py
git log --oneline | head -10
git status
```

---

## Rollback Communication

**If rollback needed, communicate to team:**

1. **Announce rollback:**
   ```
   "Rolling back Phase 3 due to categorization errors.
   Will re-execute after fixing decision logic.
   Migration branch reset to commit abc123."
   ```

2. **Document reason:**
   - Update MIGRATION-STATUS.md with rollback note
   - Add entry to SESSION_LOG.md
   - Note lessons learned

3. **Plan re-execution:**
   - Identify root cause
   - Fix issue
   - Schedule retry

---

## Recovery Time Estimates

| Rollback Level | Time to Execute | Recovery Time | Total Downtime |
|----------------|----------------|---------------|----------------|
| Level 1 (Soft) | 2 minutes | 10-30 minutes | 15-35 minutes |
| Level 2 (Hard) | 2 minutes | 30-60 minutes | 35-65 minutes |
| Level 3 (Phase) | 5 minutes | 1-4 hours | 1-4 hours |
| Level 4 (Nuclear) | 10 minutes | 2-6 hours | 2-6 hours |

**"Recovery Time"** = Time to fix issue and re-execute

---

## Testing Rollback Procedures

**Before migration, test rollback:**

```bash
# Create test commit
echo "test" > test-rollback.txt
git add test-rollback.txt
git commit -m "Test rollback"

# Test Level 1 rollback
git reset --soft HEAD~1
git status  # Should show test-rollback.txt staged

# Clean up
git reset --hard HEAD

# Test Level 2 rollback
echo "test" > test-rollback.txt
git add test-rollback.txt
git commit -m "Test rollback"
git reset --hard HEAD~1
ls test-rollback.txt  # Should not exist

# Test tag restore
git reset --hard backup-pre-migration-2026-01-10
git log --oneline | head -5
```

---

## When to Abandon Rollback

**Sometimes forward fixes are better:**

- Rollback loses significant work (> 4 hours)
- Issue is minor and fixable in < 30 minutes
- Rollback would affect other team members
- Multiple phases completed successfully

**Forward fix examples:**
- Rename single file: `git mv old.md new.md`
- Fix broken link: Edit file directly
- Add missing README: `echo "# Title" > README.md`

**Decision criteria:**
- **Time to fix forward** < **Time to rollback + re-execute** → Fix forward
- **Risk of fix** > **Risk of rollback** → Rollback
- **Work preserved** > **Work redone** → Fix forward

---

## Success Criteria for Rollback

Rollback is successful when:

1. ✅ Git status shows expected state (clean or pre-phase)
2. ✅ Validation shows expected error count
3. ✅ File counts match pre-phase state
4. ✅ No broken links or missing files
5. ✅ Can re-execute phase from known good state
6. ✅ Team aware of rollback and reason
7. ✅ Root cause identified and documented

---

## Final Safety Reminder

**Before any rollback:**

1. **Pause and think** - Is rollback necessary or can you fix forward?
2. **Check backups exist** - Verify tag and local backup
3. **Document reason** - Why are you rolling back?
4. **Choose right level** - Don't nuke when soft reset would work
5. **Verify after** - Always validate rollback succeeded
6. **Communicate** - Tell team what happened
7. **Learn** - Update procedures to prevent repeat

---

**Last Updated:** 2026-01-10
**Status:** 📋 Ready for reference during migration
**Related:** [FULL-MIGRATION-EXECUTION-PLAN.md](FULL-MIGRATION-EXECUTION-PLAN.md)
