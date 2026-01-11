# Phase 0: Preparation & Pre-Flight Checklist

**Duration:** 2-3 hours
**Complexity:** Low
**Risk:** Very Low
**Prerequisites:** User approval received

---

## 🎯 Phase Objectives

1. ✅ Create comprehensive backup (git tag + optional local copy)
2. ✅ Install and verify all required tools
3. ✅ Verify working environment is clean
4. ✅ Create migration tracking documents
5. ✅ Audit existing structure and create file inventory
6. ✅ Generate link map for later phases

**Success Criteria:**
- All prerequisites verified ✅
- Backup tag created and pushed ✅
- Tools installed and tested ✅
- Migration dashboard created ✅
- Ready to start Phase 1 ✅

---

## 📋 Pre-Flight Checklist

### Section 1: User Approval Verification (5 min)

**Verify these decisions with user:**

```
✅ User Decisions (2026-01-10):
- Option: D (Full Migration)
- Duration: 6-8 days authorized
- Start Date: 2026-01-10
- Open PRs: PR #318 merged
- Priorities: Focus on migration (pause features)
- Review: End of each phase
- Version naming: Keep v0.16 (don't change dots)
- Link checker: Yes, create during this phase
```

**If ANY decision unclear:** Ask user before proceeding.

---

### Section 2: Git Working Tree Status (10 min)

**Step 1: Check working tree is clean**

```bash
cd /Users/Pravin/Library/Mobile\ Documents/com~apple~CloudDocs/pravin/projects/project_21_dec_25/structural_engineering_lib

git status
```

**Expected output:**
```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

**If you see modified/untracked files:**

```bash
# Option 1: Commit them first
git add -A
git commit -m "chore: commit pending changes before migration"
git push

# Option 2: Stash them (if experimental)
git stash save "pre-migration stash $(date +%Y-%m-%d)"

# Option 3: Review and decide file by file
git status --short
# For each file, decide: commit, stash, or delete
```

**Checkpoint:** Working tree must be clean before proceeding ✅

---

### Section 3: Sync with Remote (10 min)

**Step 2: Verify sync with origin**

```bash
# Fetch latest from remote
git fetch origin

# Check if local is behind remote
git log origin/main..HEAD
```

**Expected output:** `(empty)` - No unpushed commits

**If you have unpushed commits:**

```bash
# Push them first
git push origin main

# Verify pushed
git log origin/main..HEAD
# Should now be empty
```

**Step 3: Check if remote has new commits**

```bash
git log HEAD..origin/main
```

**Expected output:** `(empty)` - Local is up to date

**If remote is ahead:**

```bash
# Pull latest changes
git pull origin main

# Verify up to date
git status
```

**Checkpoint:** Local and remote are in sync ✅

---

### Section 4: Open Pull Requests (10 min)

**Step 4: Review open PRs**

```bash
gh pr list --state open --json number,title,headRefName
```

**Expected:** Empty or only unrelated PRs

**Current status (from user):**
```
PR #318: Merged ✅
PR #305: FIX-002 (Streamlit test mocks)
```

**Decision needed for PR #305:**

Option A: Merge it before migration
```bash
gh pr view 305
gh pr merge 305 --squash
git pull origin main
```

Option B: Pause it (don't merge until after migration)
```bash
# Just note it exists, don't touch
# After migration, may need rebase
```

Option C: Close it (if no longer needed)
```bash
gh pr close 305 --comment "Closing due to migration; will recreate if needed"
```

**User preference:** Merge PR #305 before starting

**Action:**
```bash
# Merge PR #305
gh pr view 305
# Review changes
gh pr merge 305 --squash --delete-branch
git pull origin main

# Verify merged
gh pr list --state open
# Should be empty
```

**Checkpoint:** No open PRs blocking migration ✅

---

### Section 5: CI Status (5 min)

**Step 5: Verify CI is green**

```bash
# Check latest CI run
gh run list --limit 5
```

**Expected:** Latest run status = "completed" and conclusion = "success"

**If CI is failing:**

```bash
# View failed run
gh run view <run-id>

# Fix issues before migration
# Migration requires clean baseline
```

**Checkpoint:** CI is passing ✅

---

### Section 6: Test Suite Baseline (10 min)

**Step 6: Run full test suite locally**

```bash
cd Python
../.venv/bin/python -m pytest -q --tb=short
```

**Expected output:**
```
2370+ passed in X.XXs
```

**If tests fail:**

```bash
# Run with verbose output
../.venv/bin/python -m pytest -v --tb=short

# Fix failing tests before migration
# Migration assumes tests pass
```

**Checkpoint:** All tests passing ✅

---

## 🔒 Backup Creation (30 min)

### Backup 1: Git Tag (Mandatory)

**Step 7: Create backup tag**

```bash
# Create dated backup tag
git tag backup-pre-migration-2026-01-10

# Verify tag created
git tag | grep backup

# Push tag to remote
git push origin backup-pre-migration-2026-01-10

# Verify tag on remote
gh api repos/:owner/:repo/tags | jq '.[].name' | grep backup
```

**Checkpoint:** Backup tag created and pushed ✅

**Recovery Command (if needed later):**
```bash
# To restore to this point
git reset --hard backup-pre-migration-2026-01-10
```

---

### Backup 2: Local Copy (Optional but Recommended)

**Step 8: Create local backup**

```bash
# Navigate to parent directory
cd ..

# Create compressed backup
tar -czf backup-structural-lib-pre-migration-2026-01-10.tar.gz \
  --exclude='structural_engineering_lib/.git' \
  --exclude='structural_engineering_lib/Python/.venv' \
  --exclude='structural_engineering_lib/Python/__pycache__' \
  --exclude='structural_engineering_lib/Python/**/__pycache__' \
  structural_engineering_lib/

# Verify backup created
ls -lh backup-structural-lib-pre-migration-2026-01-10.tar.gz
```

**Expected:** File size ~50-100MB

**Move to safe location:**
```bash
# Move to external drive or cloud storage
mv backup-structural-lib-pre-migration-2026-01-10.tar.gz ~/Backups/
# Or wherever you keep backups
```

**Checkpoint:** Local backup created ✅

---

### Backup 3: Migration Branch (Recommended)

**Step 9: Create migration feature branch**

```bash
# Return to project directory
cd structural_engineering_lib

# Create and checkout migration branch
git checkout -b migration-full-cleanup-2026-01

# Push branch to remote
git push origin migration-full-cleanup-2026-01

# Verify branch created
git branch -a | grep migration
```

**Strategy:**
- All migration work happens on this branch
- Validate and test thoroughly
- Merge to main when 100% complete
- Allows easy rollback (just delete branch)

**Checkpoint:** Migration branch created ✅

---

## 🛠️ Tool Installation & Verification (30 min)

### Tool 1: Validation Script (Already Exists)

**Step 10: Verify validation script works**

```bash
cd Python
../.venv/bin/python ../scripts/validate_folder_structure.py --report | head -20
```

**Expected output:**
```
Project root: /Users/Pravin/...

🔍 Validating folder structure...

============================================================
❌ 115 ERROR(S) FOUND:
  • Root directory has 16 files, max is 10
  • docs/ root has 44 files, max is 5
  ...
```

**If script fails:**
```bash
# Check if script exists
ls -la ../scripts/validate_folder_structure.py

# Check Python path
which python
../.venv/bin/python --version
```

**Checkpoint:** Validation script working ✅

---

### Tool 2: Link Checker (Need to Create)

**Step 11: Create link checker script**

Create `scripts/check_links.py`:

```python
#!/usr/bin/env python3
"""
Check for broken internal links in markdown files.
Validates relative links to other docs and code files.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Set

def find_markdown_files(root_dir: Path) -> List[Path]:
    """Find all markdown files in directory tree."""
    md_files = []
    for path in root_dir.rglob("*.md"):
        # Skip hidden directories and virtual environments
        if not any(part.startswith('.') for part in path.parts):
            if '.venv' not in path.parts:
                md_files.append(path)
    return md_files

def extract_links(md_file: Path) -> List[Tuple[str, int]]:
    """Extract markdown links from file with line numbers."""
    links = []
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'

    with open(md_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            for match in re.finditer(link_pattern, line):
                link_text = match.group(1)
                link_url = match.group(2)
                # Only check relative links (skip http://, https://, mailto:, #anchors)
                if not link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                    links.append((link_url, line_num))

    return links

def resolve_link(md_file: Path, link_url: str) -> Path:
    """Resolve relative link to absolute path."""
    # Remove anchor if present
    link_path = link_url.split('#')[0]

    # Resolve relative to markdown file location
    target = (md_file.parent / link_path).resolve()

    return target

def check_links(root_dir: Path) -> Tuple[int, int, List[str]]:
    """Check all links in markdown files. Returns (total, broken, errors)."""
    md_files = find_markdown_files(root_dir)

    total_links = 0
    broken_links = 0
    errors = []

    print(f"Checking links in {len(md_files)} markdown files...")
    print()

    for md_file in md_files:
        links = extract_links(md_file)

        for link_url, line_num in links:
            total_links += 1
            target = resolve_link(md_file, link_url)

            if not target.exists():
                broken_links += 1
                rel_md_file = md_file.relative_to(root_dir)
                error_msg = f"❌ {rel_md_file}:{line_num} -> {link_url} (NOT FOUND)"
                errors.append(error_msg)
                print(error_msg)

    return total_links, broken_links, errors

def main():
    # Get project root (3 levels up from scripts/)
    root_dir = Path(__file__).parent.parent

    print(f"Project root: {root_dir}")
    print(f"Checking markdown links...")
    print("=" * 60)
    print()

    total, broken, errors = check_links(root_dir)

    print()
    print("=" * 60)
    print(f"Total links checked: {total}")
    print(f"Broken links: {broken}")

    if broken == 0:
        print()
        print("✅ All links valid!")
        return 0
    else:
        print()
        print(f"❌ Found {broken} broken links")
        print()
        print("Fix these links before proceeding with migration.")
        return 1

if __name__ == "__main__":
    exit(main())
```

**Save and make executable:**

```bash
cd ..
# File should be at scripts/check_links.py

chmod +x scripts/check_links.py

# Test it
.venv/bin/python scripts/check_links.py | head -30
```

**Expected:** May show broken links (we'll fix in Phase 6)

**Checkpoint:** Link checker created and working ✅

---

### Tool 3: Archive Script (Already Exists)

**Step 12: Verify archive script exists**

```bash
ls -la scripts/archive_old_sessions.sh
```

**Expected:** File exists (265 lines, created earlier)

**Test in dry-run mode:**
```bash
DRY_RUN=1 ./scripts/archive_old_sessions.sh | head -20
```

**Expected:** Shows what would be archived (doesn't actually move files)

**Checkpoint:** Archive script exists and works ✅

---

## 📊 Baseline Metrics Collection (20 min)

### Step 13: Collect Current State Metrics

**Create migration tracking document:**

```bash
cat > agents/agent-9/governance/MIGRATION-PROGRESS.md << 'EOF'
# Migration Progress Dashboard

**Started:** 2026-01-10
**Target Completion:** 2026-01-18
**Status:** Phase 0 - Preparation ✅

---

## Phase Completion

- [x] Phase 0: Preparation ✅ (2026-01-10)
- [ ] Phase 1: Structure Creation
- [ ] Phase 2: Agents Migration
- [ ] Phase 3: Docs Migration
- [ ] Phase 4: Dated Files
- [ ] Phase 5: Naming Cleanup
- [ ] Phase 6: Link Fixing
- [ ] Phase 7: Script Updates
- [ ] Phase 8: Final Validation

---

## Baseline Metrics (Phase 0)

**Date:** 2026-01-10
**Branch:** migration-full-cleanup-2026-01
**Commit:** $(git rev-parse --short HEAD)

### Validation Errors
```
Total: 115 errors

Breakdown:
- Root directory: 16 files (limit: 10) = 6 over
- docs/ root: 44 files (limit: 5) = 39 over
- agents/ root: 13 files (limit: 1) = 12 over
- Dated files: 23 misplaced
- Naming violations: 92 files
```

### File Counts
```
Total markdown files: $(find . -name "*.md" -type f | wc -l | tr -d ' ')
Root directory files: $(find . -maxdepth 1 -type f \( -name "*.md" -o -name "*.txt" -o -name "*.sh" \) | wc -l | tr -d ' ')
docs/ root files: $(find docs -maxdepth 1 -name "*.md" -type f | wc -l | tr -d ' ')
agents/ root files: $(find agents -maxdepth 1 -name "*.md" -type f | wc -l | tr -d ' ')
docs/planning/ files: $(find docs/planning -name "*.md" -type f | wc -l | tr -d ' ')
```

### Test Status
```
Test suite: 2370+ tests
Status: All passing ✅
Coverage: 86%
Ruff errors: 0
Mypy errors: 0
```

### Git Status
```
Branch: migration-full-cleanup-2026-01
Commits ahead of main: 0
Working tree: Clean ✅
Backup tag: backup-pre-migration-2026-01-10 ✅
```

---

## Error Reduction Progress

| Phase | Errors Before | Errors After | Reduction | Status |
|-------|---------------|--------------|-----------|--------|
| Start | 115 | 115 | 0% | ✅ Baseline |
| Phase 1 | 115 | TBD | TBD% | Pending |
| Phase 2 | TBD | TBD | TBD% | Pending |
| Phase 3 | TBD | TBD | TBD% | Pending |
| Phase 4 | TBD | TBD | TBD% | Pending |
| Phase 5 | TBD | TBD | TBD% | Pending |
| Phase 6 | TBD | TBD | TBD% | Pending |
| Phase 7 | TBD | TBD | TBD% | Pending |
| Phase 8 | TBD | 0 | 100% | Target |

---

## Time Tracking

| Phase | Planned | Actual | Status |
|-------|---------|--------|--------|
| Phase 0 | 2-3h | TBD | In Progress |
| Phase 1 | 3-4h | TBD | Pending |
| Phase 2 | 3-4h | TBD | Pending |
| Phase 3 | 12-16h | TBD | Pending |
| Phase 4 | 4-6h | TBD | Pending |
| Phase 5 | 8-10h | TBD | Pending |
| Phase 6 | 6-8h | TBD | Pending |
| Phase 7 | 3-4h | TBD | Pending |
| Phase 8 | 2-3h | TBD | Pending |
| **Total** | **30-40h** | **TBD** | **In Progress** |

---

## Issues Log

### Phase 0 Issues
- (None yet)

---

## Next Session

**Date:** 2026-01-10 (later today or tomorrow)
**Phase:** Phase 1 - Structure Creation
**Estimated Duration:** 3-4 hours
**Preparation:** Read PHASE-1-STRUCTURE-CREATION.md

EOF
```

**Substitute actual values:**

```bash
# Get actual counts and update document
TOTAL_MD=$(find . -name "*.md" -type f | wc -l | tr -d ' ')
ROOT_FILES=$(find . -maxdepth 1 -type f \( -name "*.md" -o -name "*.txt" -o -name "*.sh" \) | wc -l | tr -d ' ')
DOCS_ROOT=$(find docs -maxdepth 1 -name "*.md" -type f | wc -l | tr -d ' ')
AGENTS_ROOT=$(find agents -maxdepth 1 -name "*.md" -type f | wc -l | tr -d ' ')
PLANNING_FILES=$(find docs/planning -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')

# Update the document with actual values (or do manually)
echo "Total markdown files: $TOTAL_MD"
echo "Root files: $ROOT_FILES"
echo "docs/ root: $DOCS_ROOT"
echo "agents/ root: $AGENTS_ROOT"
echo "docs/planning/: $PLANNING_FILES"
```

**Checkpoint:** Baseline metrics collected ✅

---

## 🗺️ File Inventory & Link Map Generation (20 min)

### Step 14: Generate Complete File Inventory

**Create inventory of all files to be moved:**

```bash
cat > agents/agent-9/governance/FILE-INVENTORY.md << 'EOF'
# File Inventory for Migration

**Generated:** 2026-01-10
**Purpose:** Track all files that will be moved during migration

---

## Root Directory Files (16 total, need to reduce to ≤10)

```
$(find . -maxdepth 1 -type f \( -name "*.md" -o -name "*.txt" -o -name "*.sh" \) -exec basename {} \; | sort)
```

**Canonical files (keep in root):**
- README.md
- CHANGELOG.md
- CONTRIBUTING.md
- LICENSE*
- AUTHORS.md
- CODE_OF_CONDUCT.md
- SECURITY.md

**To archive/move:** (TBD - will decide in Phase 4)

---

## agents/ Root Files (13 total, need to reduce to 1)

```
$(find agents -maxdepth 1 -name "*.md" -type f -exec basename {} \; | sort)
```

**Keep:**
- README.md

**Move to agents/roles/:**
- ARCHITECT.md → agents/roles/architect.md
- CLIENT.md → agents/roles/client.md
- DEV.md → agents/roles/dev.md
- DEVOPS.md → agents/roles/devops.md
- DOCS.md → agents/roles/docs.md
- GOVERNANCE.md → agents/roles/governance.md
- INTEGRATION.md → agents/roles/integration.md
- PM.md → agents/roles/pm.md
- RESEARCHER.md → agents/roles/researcher.md
- SUPPORT.md → agents/roles/support.md
- TESTER.md → agents/roles/tester.md
- UI.md → agents/roles/ui.md

---

## docs/ Root Files (44 total, need to reduce to ≤5)

```
$(find docs -maxdepth 1 -name "*.md" -type f -exec basename {} \; | sort)
```

**(Will categorize these in Phase 3 - most complex part)**

---

## Dated Files to Archive (23 total)

```
$(cd Python && ../.venv/bin/python ../scripts/validate_folder_structure.py --report 2>&1 | grep "Dated file in wrong location" | sed 's/.*: //')
```

**All will move to:** docs/_archive/2026-01/

---

## Files with Naming Violations (92 total)

```
$(cd Python && ../.venv/bin/python ../scripts/validate_folder_structure.py --report 2>&1 | grep "Invalid doc filename" | sed 's/.*: //' | head -20)
... (92 files total)
```

**Naming fix:** UPPERCASE/underscores → kebab-case

---

EOF
```

**Checkpoint:** File inventory created ✅

---

### Step 15: Initialize Link Map

**Create link mapping document (will populate during migration):**

```bash
cat > agents/agent-9/governance/LINK-MAP.md << 'EOF'
# Link Map: Old Paths → New Paths

**Generated:** 2026-01-10
**Purpose:** Track all file moves for automated link fixing

**Usage:**
```bash
# This file is used by Phase 6 link fixing script
# Each line: OLD_PATH → NEW_PATH
```

---

## Phase 2: Agent Files

agents/ARCHITECT.md → agents/roles/architect.md
agents/CLIENT.md → agents/roles/client.md
agents/DEV.md → agents/roles/dev.md
agents/DEVOPS.md → agents/roles/devops.md
agents/DOCS.md → agents/roles/docs.md
agents/GOVERNANCE.md → agents/roles/governance.md
agents/INTEGRATION.md → agents/roles/integration.md
agents/PM.md → agents/roles/pm.md
agents/RESEARCHER.md → agents/roles/researcher.md
agents/SUPPORT.md → agents/roles/support.md
agents/TESTER.md → agents/roles/tester.md
agents/UI.md → agents/roles/ui.md

---

## Phase 3: docs/ Root Files

**(Will populate during Phase 3 as files are categorized and moved)**

---

## Phase 4: Dated Files

**(Will populate during Phase 4 as files are archived)**

---

## Phase 5: Naming Fixes

**(Will populate during Phase 5 as files are renamed)**

---

**Last Updated:** Phase 0
**Next Update:** Phase 2

EOF
```

**Checkpoint:** Link map initialized ✅

---

## ✅ Phase 0 Completion Checklist

**Go through this checklist before proceeding to Phase 1:**

### Pre-Flight Checks
- [ ] User approval verified (Option D, 6-8 days, start 2026-01-10)
- [ ] Git working tree clean (`git status`)
- [ ] Local and remote synced (`git log origin/main..HEAD` empty)
- [ ] Open PRs handled (PR #318 merged, PR #305 merged)
- [ ] CI is green (all tests passing)
- [ ] Test suite passing locally (2370+ tests)

### Backups Created
- [ ] Git backup tag created (`backup-pre-migration-2026-01-10`)
- [ ] Backup tag pushed to remote (`git push origin --tags`)
- [ ] Migration branch created (`migration-full-cleanup-2026-01`)
- [ ] Migration branch pushed (`git push origin migration-full-cleanup-2026-01`)
- [ ] Optional: Local backup created (tar.gz)

### Tools Installed
- [ ] Validation script verified (`validate_folder_structure.py --report`)
- [ ] Link checker created (`check_links.py`)
- [ ] Archive script verified (`archive_old_sessions.sh`)

### Documentation Created
- [ ] Migration progress dashboard (`MIGRATION-PROGRESS.md`)
- [ ] File inventory (`FILE-INVENTORY.md`)
- [ ] Link map initialized (`LINK-MAP.md`)

### Baseline Metrics
- [ ] Validation errors counted (115 errors)
- [ ] File counts recorded
- [ ] Test status documented
- [ ] Git status recorded

**If ALL boxes are checked ✅:** Phase 0 is complete! Proceed to Phase 1.

**If ANY box is unchecked ❌:** Complete that task before proceeding.

---

## 📝 Phase 0 Completion Summary

**Time Spent:** ___ hours (target: 2-3 hours)

**Checklist Status:** ___/25 items completed

**Issues Encountered:**
- (List any issues and how they were resolved)

**Ready for Phase 1:** YES / NO

**If YES:**
```bash
# Commit Phase 0 preparation work
git add agents/agent-9/governance/MIGRATION-PROGRESS.md
git add agents/agent-9/governance/FILE-INVENTORY.md
git add agents/agent-9/governance/LINK-MAP.md
git add scripts/check_links.py

git commit -m "docs(migration): Phase 0 preparation complete

- Created backup tag: backup-pre-migration-2026-01-10
- Created migration branch: migration-full-cleanup-2026-01
- Installed tools: link checker, validation, archive scripts
- Generated baseline metrics (115 errors)
- Created tracking documents

Phase 0 Duration: X hours
Next: Phase 1 - Structure Creation

Ref: agents/agent-9/governance/PHASE-0-PREPARATION.md"

git push origin migration-full-cleanup-2026-01
```

**Next Step:** Read [PHASE-1-STRUCTURE-CREATION.md](PHASE-1-STRUCTURE-CREATION.md)

---

**Phase 0 Status:** ✅ COMPLETE (if all checkboxes marked)
**Date Completed:** 2026-01-10
**Next Phase:** [PHASE-1-STRUCTURE-CREATION.md](PHASE-1-STRUCTURE-CREATION.md)

---

**Document End**
