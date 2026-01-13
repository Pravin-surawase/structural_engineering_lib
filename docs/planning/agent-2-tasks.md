# Background Agent 2 Tasks (PROJECT HYGIENE & MAINTENANCE)
<!-- lint-ignore-git -->

**Agent Role:** PROJECT HYGIENE SPECIALIST
**Primary Focus:** Repository cleanliness, file organization, duplicate removal, archival, documentation structure
**Status:** Active
**Last Updated:** 2026-01-07

---

## Mission Statement

Keep the repository **clean, compact, and efficient** by:
- 🗂️ Archiving obsolete content
- 🔍 Finding and removing duplicates
- 🔗 Fixing broken links
- 📁 Maintaining clear folder structure
- 🧹 Removing build artifacts and cruft
- 📏 Enforcing naming conventions
- 📊 Monitoring repository health metrics

---

## Work Modes

Agent 2 operates in **TWO modes** (MAIN agent decides which):

### Mode 1: AUDIT & DOCUMENT (Recommended - Safer)
**What:** Create detailed reports with suggestions, no file changes
**Output:** `docs/planning/hygiene-suggestions-YYYY-MM-DD.md`
**MAIN reviews → approves → implements**

**Pros:**
- ✅ Zero risk of breaking changes
- ✅ MAIN has full visibility before execution
- ✅ Can batch multiple suggestions for efficiency
- ✅ Easy to reject/modify recommendations

**Workflow:**
```bash
# 1. Create audit report branch (local only)
git checkout -b audit/hygiene-YYYY-MM-DD

# 2. Run hygiene checks and document findings
# ... create suggestions document ...

# 3. Commit locally
git add docs/planning/hygiene-suggestions-*.md
git commit -m "docs: hygiene audit and recommendations YYYY-MM-DD"

# 4. Handoff to MAIN (do NOT push)
# MAIN reviews → approves → implements
```

### Mode 2: IMPLEMENT ON BRANCH (Execute Changes)
**What:** Make actual file changes (archive, delete, rename, fix links)
**Output:** Feature branch with all changes applied
**Agent 2 executes → MAIN reviews → pushes/merges**

**Pros:**
- ✅ Faster execution (no double work)
- ✅ Changes tested before merge
- ✅ MAIN still reviews before merge

**Cons:**
- ⚠️ Higher risk (file deletions/moves)
- ⚠️ Need careful testing

**Workflow:**
```bash
# 1. Create feature branch (local only)
git checkout -b hygiene/cleanup-YYYY-MM-DD

# 2. Execute hygiene tasks (archive, remove, fix)
# ... make changes ...

# 3. Run quality checks
scripts/check_links.py                    # Verify no new broken links
rg "TODO\|FIXME" docs/ | grep -v _archive  # Check for unresolved TODOs
git status -sb                            # Review changes

# 4. Commit locally
git add -A
git commit -m "chore: archive old files, remove duplicates, fix links"

# 5. Handoff to MAIN (do NOT push)
# MAIN reviews → tests → pushes → merges
```

---

## Active Tasks

### HYGIENE-001: Fix Broken Links (P0 - Critical)
**Priority:** 🔴 HIGH
**Status:** 🟡 TODO
**Mode:** Mode 2 (Implement)
**Estimated Effort:** 1-2 hours

**Objective:** Fix 8 broken internal links identified in project-hygiene-audit.md

**Broken Links to Fix:**
1. `docs/ai-context-pack.md` → `.github/copilot-instructions.md` (fix: `../.github/copilot-instructions.md`)
2. `docs/research/documentation-handoff-analysis.md` → `reference/automation-catalog.md` (fix: `../reference/automation-catalog.md`)
3. `docs/research/session-2026-01-06-documentation-enhancement.md` → `reference/automation-catalog.md` (fix: `../reference/automation-catalog.md`)
4. `docs/research/research-methodology.md` → "Paper title (link placeholder)" (fix: remove or add proper citation)
5. `docs/troubleshooting/merge-conflict-prevention.md` → `/.github/copilot-instructions.md` (fix: `../.github/copilot-instructions.md`)
6. `docs/troubleshooting/merge-conflict-prevention.md` → `/scripts/check_unfinished_merge.sh` (fix: remove reference or create script)
7. `docs/getting-started/design-suggestions-guide.md` → `./cost-optimization-guide.md` (fix: verify file exists or remove link)

**Acceptance Criteria:**
- [ ] All 7-8 broken links fixed
- [ ] Run `scripts/check_links.py` → zero errors
- [ ] Verify linked files exist
- [ ] Commit with descriptive message

**File Boundaries:**
- ✅ Edit: Any doc files with broken links
- ✅ Verify: `scripts/check_links.py` passes
- ❌ Do NOT edit: Production code, tests

**Handoff Template:**
```markdown
## Handoff: HYGIENE (Agent 2) → MAIN
**Task:** HYGIENE-001
**Branch:** hygiene/fix-broken-links
**Status:** ✅ Complete

### Summary
Fixed 7-8 broken internal links across docs/ directory.

### Changes
- `docs/ai-context-pack.md`: Fixed relative path to copilot-instructions
- `docs/research/*.md`: Fixed 2 links to automation-catalog
- `docs/troubleshooting/*.md`: Fixed paths, removed dead references
- `docs/getting-started/*.md`: Verified/fixed file references

### Verification
```bash
./scripts/check_links.py
# Result: ✅ Zero broken links
```

### Action Required by MAIN
1. Review: `git checkout hygiene/fix-broken-links`
2. Test: `./scripts/check_links.py`
3. Push: `git push origin hygiene/fix-broken-links`
4. Merge direct (docs-only): `git switch main && git merge hygiene/fix-broken-links && git push`
```

---

### HYGIENE-002: Archive Obsolete Planning Docs (P1)
**Priority:** 🟠 MEDIUM-HIGH
**Status:** 🟡 TODO
**Mode:** Mode 2 (Implement)
**Estimated Effort:** 2-3 hours

**Objective:** Move outdated planning docs (v0.7-v0.12) to `docs/_archive/` with redirect stubs

**Files to Archive:**
1. `docs/v0.7-requirements.md` → `docs/_archive/v0.7-requirements.md`
2. `docs/v0.8-execution-checklist.md` → `docs/_archive/v0.8-execution-checklist.md`
3. `docs/planning/v0.12-plan.md` → `docs/_archive/planning/v0.12-plan.md`
4. `docs/planning/production-roadmap.md` → `docs/_archive/planning/production-roadmap-v0.10.md`
5. `docs/planning/project-status.md` → `docs/_archive/planning/project-status-v0.11.md`

**Process for Each File:**
1. Check if file is linked from other docs: `rg -l "v0.7-requirements.md"`
2. Move to archive: `git mv docs/v0.7-requirements.md docs/_archive/v0.7-requirements.md`
3. Create redirect stub at original location:
```markdown
# [Original Filename]

> **Note:** This document has been archived as it pertains to v0.X development.

**Archived location:** docs/_archive/original-filename.md

---

For current planning, see:
- [TASKS.md](../TASKS.md)
- Next Session Brief: next-session-brief.md
```
4. Update links in referring docs
5. Test: `scripts/check_links.py`

**Acceptance Criteria:**
- [ ] 5 files moved to `docs/_archive/`
- [ ] Redirect stubs created at original locations
- [ ] All referencing docs updated
- [ ] `check_links.py` passes
- [ ] Archive directory has clear README explaining purpose

**File Boundaries:**
- ✅ Move: Old planning docs to `docs/_archive/`
- ✅ Create: Redirect stubs
- ✅ Edit: Docs with links to archived files
- ❌ Do NOT delete: Keep archived files (history important)

---

### HYGIENE-003: Remove Build Artifacts & OS Cruft (P0)
**Priority:** 🔴 HIGH
**Status:** 🟡 TODO
**Mode:** Mode 2 (Implement)
**Estimated Effort:** 30 minutes

**Objective:** Remove tracked build artifacts and OS metadata files

**Files to Remove:**
```bash
# Find and remove (if present in git):
find . -name ".DS_Store" -type f
find . -name ".coverage" -type f -not -path "./.venv/*"
find . -name "*.pyc" -type f
find . -name "__pycache__" -type d

# Specific files identified:
.coverage                    # Root coverage file
Python/.coverage             # Python coverage file
.DS_Store                    # macOS metadata
Excel/.DS_Store
VBA/.DS_Store
```

**Process:**
1. Remove from git tracking: `git rm --cached .DS_Store .coverage Python/.coverage`
2. Update `.gitignore` to prevent future commits:
```gitignore
# OS metadata
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes

# Coverage files (keep in Python/ only, not root)
/.coverage
*.coverage.*

# Python cache
__pycache__/
*.pyc
*.pyo
```
3. Verify: `git status` should not show these files
4. Commit: `git commit -m "chore: remove build artifacts and OS metadata"`

**Acceptance Criteria:**
- [ ] All `.DS_Store`, root `.coverage` removed from git
- [ ] `.gitignore` updated to prevent future commits
- [ ] Test: `git status` shows no tracked artifacts
- [ ] Verify: `git ls-files | grep -E '\.DS_Store|\.coverage'` returns nothing

---

### HYGIENE-004: Clean Up Git Worktrees (P1)
**Priority:** 🟠 MEDIUM-HIGH
**Status:** 🟡 TODO
**Mode:** Mode 1 (Audit first)
**Estimated Effort:** 1 hour

**Objective:** Identify and document stale git worktrees for cleanup

**Process:**
1. List all worktrees: `git worktree list`
2. Check `.worktrees/` directory (if exists):
```bash
find .worktrees -type d -maxdepth 1
ls -lah .worktrees/
```
3. For each worktree, check:
   - Is branch still active? `git branch --list <branch>`
   - Is branch merged? `git branch --merged main | grep <branch>`
   - Any uncommitted changes? `cd .worktrees/<name> && git status`

**Deliverable (Mode 1):**
`docs/planning/hygiene-suggestions-worktrees-YYYY-MM-DD.md`:
```markdown
# Git Worktrees Cleanup Recommendations

## Summary
Found X worktrees, Y are stale and can be removed.

## Worktrees Status

### Safe to Remove (Merged/Abandoned)
1. `.worktrees/worktree-2026-01-07T07-28-08/`
   - Branch: feature/old-branch (merged to main on 2026-01-07)
   - Status: Clean (no uncommitted changes)
   - Command: `git worktree remove .worktrees/worktree-2026-01-07T07-28-08`

### Keep (Active Work)
1. `.worktrees/current-feature/`
   - Branch: feature/active (not merged)
   - Status: 3 uncommitted files
   - Action: Keep until branch merged

## Recommended Actions
```bash
# Remove stale worktrees
git worktree remove .worktrees/worktree-2026-01-07T07-28-08
git worktree remove .worktrees/worktree-2026-01-07T08-14-04
# ... etc

# Prune deleted worktrees
git worktree prune
```

## Follow-up
- Add `.worktrees/` to `.gitignore` if not already present
- Consider adding pre-commit hook to warn about stale worktrees
```

**Acceptance Criteria:**
- [ ] All worktrees documented with status
- [ ] Clear removal recommendations for stale worktrees
- [ ] Verification commands provided
- [ ] MAIN approves before deletion

---

### HYGIENE-005: Duplicate Content Audit (P2)
**Priority:** 🟡 LOW-MEDIUM
**Status:** 🟡 TODO
**Mode:** Mode 1 (Audit & Document)
**Estimated Effort:** 3-4 hours

**Objective:** Document all duplicate content and recommend consolidation strategy

**Duplicates Identified (from audit):**
1. **LICENSE files:**
   - `LICENSE` (root) - **KEEP as canonical**
   - `Python/LICENSE` - **Recommendation:** Replace with stub pointing to root

2. **README.md files (25 locations):**
   - Audit each: Is it an index (keep) or duplicate content (consolidate)?
   - `docs/README.md` - Index (keep)
   - `docs/reference/README.md` - Index (keep)
   - Others: TBD based on content

3. **SUPPORT.md files:**
   - `SUPPORT.md` (root) - **KEEP as canonical**
   - `agents/SUPPORT.md` - **Replace with link**

4. **Type definition files:**
   - `Python/structural_lib/types.py`
   - `Python/structural_lib/insights/types.py`
   - `Python/structural_lib/data_types.py`
   - `Python/structural_lib/insights/data_types.py`
   - **Recommendation:** Document intentional separation vs accidental duplication

5. **Project overview docs:**
   - `docs/project-overview.md` (UPPERCASE)
   - `docs/architecture/project-overview.md` (kebab-case)
   - **Recommendation:** Canonicalize one, create redirect for other

**Deliverable:**
`docs/planning/hygiene-suggestions-duplicates-YYYY-MM-DD.md`:
```markdown
# Duplicate Content Consolidation Plan

## Priority 1: Clear Duplicates (Safe to Consolidate)
...

## Priority 2: Ambiguous Cases (Need Review)
...

## Priority 3: Intentional Duplication (Document Only)
...

## Implementation Plan
1. Phase 1: Replace duplicate SU PPORT/LICENSE with stubs
2. Phase 2: Canonicalize project overview docs
3. Phase 3: Audit README files
4. Phase 4: Document type definition separation

## Commands
```bash
# Example consolidation
git mv agents/SUPPORT.md agents/SUPPORT.md.bak
echo "See SUPPORT.md at ../../SUPPORT.md" > agents/SUPPORT.md
git add agents/SUPPORT.md
```
```

---

### HYGIENE-006: Standardize Naming Conventions (P2)
**Priority:** 🟡 LOW-MEDIUM
**Status:** 🔵 BACKLOG
**Mode:** Mode 1 (Audit first, then Mode 2 if approved)
**Estimated Effort:** 4-6 hours

**Objective:** Convert all doc filenames to kebab-case standard

**Current Issues:**
- Mixed case: `ai-context-pack.md`, `project-overview.md`, `TASKS.md`
- Inconsistent: `v0.7-requirements.md` vs `project-overview.md`

**Proposed Standard:**
- **Docs:** kebab-case (`project-overview.md`, `ai-context-pack.md`)
- **Special files:** Keep UPPERCASE for visibility (`README.md`, `LICENSE`, `CHANGELOG.md`)
- **Planning docs:** Keep UPPERCASE for important files (`TASKS.md`, `SESSION_LOG.md`)

**Process (Mode 1 - Audit):**
1. List all non-standard filenames
2. Propose renames with link update plan
3. Estimate effort (many links to update)
4. Get MAIN approval before execution

**Process (Mode 2 - Execute, if approved):**
1. For each file: `git mv OLD.md new-name.md`
2. Update all links: `rg -l "OLD.md" | xargs sed -i 's/OLD.md/new-name.md/g'`
3. Test: `scripts/check_links.py`
4. Commit in batches (e.g., "chore: rename docs/ to kebab-case")

---

## Backlog

### HYGIENE-007: Repository Size Optimization
**Objective:** Analyze and reduce repository size (large files, git history bloat)

### HYGIENE-008: Documentation Structure Audit
**Objective:** Propose canonical doc structure (reduce docs/ root clutter)

### HYGIENE-009: Code Duplication Analysis
**Objective:** Find duplicate code patterns in Python modules

### HYGIENE-010: Dependency Audit
**Objective:** Check for unused dependencies in `pyproject.toml`

---

## Completed

None yet.

---

## Guidelines for Agent 2 (HYGIENE SPECIALIST)

### Core Responsibilities

**DO:**
- ✅ Archive obsolete files with redirect stubs
- ✅ Remove build artifacts and OS metadata
- ✅ Fix broken links
- ✅ Find and document duplicates
- ✅ Audit folder structure and naming
- ✅ Check for stale worktrees
- ✅ Monitor repo health (size, file count, link validity)
- ✅ Propose consolidation strategies

**DON'T:**
- ❌ Edit production code (`Python/structural_lib/*.py`)
- ❌ Edit tests (`Python/tests/*.py`)
- ❌ Edit CI workflows (`.github/workflows/`)
- ❌ Delete files without archiving first
- ❌ Rename files without updating all links
- ❌ Make changes without documenting rationale

### Working Locally (No Remote Operations)

**Mode 1 Workflow (Audit & Document):**
```bash
# 1. Create audit branch
git checkout -b audit/hygiene-TASK-NAME

# 2. Run checks and create suggestions document
rg --files -g "*.DS_Store"           # Find OS files
find . -name ".coverage" -type f      # Find build artifacts
./scripts/check_links.py              # Check broken links
git worktree list                     # List worktrees

# 3. Document findings in docs/planning/hygiene-suggestions-*.md

# 4. Commit locally
git add docs/planning/hygiene-suggestions-*.md
git commit -m "docs: hygiene audit TASK-XXX"

# 5. Handoff to MAIN (do NOT push)
```

**Mode 2 Workflow (Implement Changes):**
```bash
# 1. Create feature branch
git checkout -b hygiene/cleanup-TASK-NAME

# 2. Make changes (archive, remove, fix)
git mv old.md docs/_archive/old.md           # Archive
git rm --cached .DS_Store                    # Remove from git
sed -i 's|old-link.md|new-link.md|g' file.md # Fix links

# 3. Run verification
./scripts/check_links.py                     # No new broken links
rg "TODO\|FIXME" docs/ | grep -v _archive   # Check TODOs
git status -sb                               # Review changes

# 4. Commit locally
git add -A
git commit -m "chore: hygiene cleanup TASK-XXX"

# 5. Handoff to MAIN (do NOT push)
```

### Handoff Template (Mode 1 - Audit)

```markdown
## Handoff: HYGIENE (Agent 2) → MAIN

**Task:** HYGIENE-XXX (Audit Mode)
**Branch:** audit/hygiene-topic-name
**Status:** ✅ Audit complete, suggestions documented

### Summary
[2-3 sentences: what was audited, key findings]

### Findings Document
- `docs/planning/hygiene-suggestions-topic-YYYY-MM-DD.md` - [line count, sections]

### Key Issues Found
- **Issue 1:** [description] - [severity: P0/P1/P2]
- **Issue 2:** [description] - [severity]
- **Issue 3:** [description] - [severity]

### Recommendations Summary
- **Priority 0 (Critical):** X items - [brief list]
- **Priority 1 (High):** Y items - [brief list]
- **Priority 2 (Medium):** Z items - [brief list]

### Estimated Effort for Implementation
- P0 fixes: [hours]
- P1 fixes: [hours]
- P2 fixes: [hours]

### Action Required by MAIN
1. Review suggestions: `git checkout audit/hygiene-topic-name`
2. Approve/modify recommendations
3. If approved:
   - Option A: Assign back to Agent 2 (Mode 2 - implement)
   - Option B: Implement yourself
   - Option C: Defer (add to backlog)
```

### Handoff Template (Mode 2 - Implementation)

```markdown
## Handoff: HYGIENE (Agent 2) → MAIN

**Task:** HYGIENE-XXX (Implementation)
**Branch:** hygiene/cleanup-topic-name
**Status:** ✅ Complete, all changes tested locally

### Summary
[2-3 sentences: what was changed, why]

### Files Changed
**Archived** (moved to `docs/_archive/`):
- `docs/old-file-1.md`
- `docs/planning/old-plan.md`

**Deleted** (removed from git):
- `.DS_Store` (3 files)
- `.coverage` (root)

**Modified** (link fixes, stub creation):
- `docs/ai-context-pack.md` - Fixed 1 broken link
- `docs/old-file-1.md` - Created redirect stub

### Verification Results
```bash
# Broken links check
./scripts/check_links.py
# ✅ Result: 0 broken links (was 8)

# Git artifacts check
git ls-files | grep -E '\.DS_Store|\.coverage'
# ✅ Result: No matches

# Repo size
du -sh .git/
# 📊 Result: [size] (reduced by [amount])
```

### Safety Checks
- [ ] No production code modified
- [ ] No tests modified
- [ ] All archived files have redirect stubs
- [ ] All link updates verified
- [ ] `.gitignore` updated to prevent recurrence

### Action Required by MAIN
1. Review changes: `git checkout hygiene/cleanup-topic-name`
2. Test: Run verification commands above
3. Push: `git push origin hygiene/cleanup-topic-name`
4. Merge direct (hygiene-only): `git switch main && git merge hygiene/cleanup-topic-name && git push`
```

### File Boundaries (Agent 2 - HYGIENE)

**✅ Safe to Edit/Create:**

- `docs/planning/hygiene-suggestions-*.md` (audit reports)
- `docs/_archive/**/*` (archived files - move only, don't edit)
- Create redirect stubs at original locations
- Fix broken links in any doc files
- Update `.gitignore` (to prevent artifact commits)

**✅ Safe to Read (for context):**
- Any docs, code, tests (read-only for reference)
- `docs/research/project-hygiene-audit.md` (baseline audit)
- `docs/planning/memory.md` (current project state)
- `.gitignore` (current ignore rules)

**✅ Safe to Delete (Mode 2 only):**
- `.DS_Store`, `.coverage` (OS/build artifacts)
- Tracked build artifacts NOT needed for builds
- Stale git worktrees (after verification)

**❌ NEVER Edit:**
- `docs/TASKS.md` (MAIN agent owns this)
- `docs/SESSION_LOG.md` (MAIN agent owns this)
- `docs/planning/next-session-brief.md` (MAIN agent owns this)
- Production code (`Python/structural_lib/*.py`)
- Tests (`Python/tests/*.py`)
- CI workflows (`.github/workflows/*.yml`)
- Dependencies (`pyproject.toml`, `requirements*.txt`)

**⚠️ Caution (Ask MAIN first):**
- Renaming files (affects many links)
- Moving canonical docs (high impact)
- Deleting files not clearly obsolete
- Large-scale restructuring

### Quality Checklist (Before Handoff - Mode 2)

**REQUIRED for Implementation Mode:**

```bash
# 1. Verify no broken links introduced
cd "/path/to/repo" && ./scripts/check_links.py
# Expect: Zero new broken links

# 2. Check for unresolved TODOs (excluding archive)
rg "TODO\|FIXME" docs/ | grep -v "_archive"
# Expect: No new TODOs left unresolved

# 3. Verify archived files have redirects
find docs/_archive/ -name "*.md" -type f
# For each, check if redirect stub exists at original location

# 4. Check git artifacts not re-introduced
git ls-files | grep -E '\.DS_Store|\.coverage|\.pyc|__pycache__'
# Expect: No matches

# 5. Review changes summary
git status -sb
git diff --stat
# Sanity check: Only hygiene changes, no code/test edits
```

**If ANY check fails:**
- Fix the issue locally
- Re-run checks
- Do NOT hand off until all checks pass

---

## Useful Commands & Scripts

### Hygiene Audit Commands


```bash
# Find OS metadata files
find . -name ".DS_Store" -type f
find . -name "._*" -type f

# Find build artifacts
find . -name ".coverage" -type f -not -path "./.venv/*"
find . -name "*.pyc" -type f
find . -name "__pycache__" -type d
find . -name "*.egg-info" -type d

# Find backup files
rg --files -g "*.bak"
rg --files -g "*.old"
rg --files -g "*~"

# Check for duplicate filenames
find . -type f -not -path "./.venv/*" -not -path "./.git/*" | \
  awk -F/ '{print $NF}' | sort | uniq -c | sort -rn | head -20

# Find large files (>1MB)
find . -type f -size +1M -not -path "./.venv/*" -not -path "./.git/*" | \
  xargs du -h | sort -rh | head -20

# Check broken links
./scripts/check_links.py

# List git worktrees
git worktree list

# Check repo size
du -sh .git/
du -sh .

# Find files with inconsistent naming
find docs/ -type f -name "*[A-Z]*[A-Z]*" | grep -v "README\|LICENSE\|CHANGELOG\|TASKS\|SESSION"
```

### Link Fixing Commands

```bash
# Find broken links to specific file
rg -l "path/to/old-file.md"

# Fix links (example - test on one file first!)
sed -i 's|old-path/file.md|new-path/file.md|g' docs/somefile.md

# Batch fix (be careful!)
rg -l "old-path/file.md" | xargs sed -i 's|old-path/file.md|new-path/file.md|g'

# Verify fix
./scripts/check_links.py
```

### Archival Commands

```bash
# Move file to archive with git
git mv docs/old-file.md docs/_archive/old-file.md

# Create redirect stub
cat > docs/old-file.md << 'EOF'
# Old File Title

> **Note:** This document has been archived.

**Archived location:** docs/_archive/old-file.md

For current information, see current-file.md.
EOF

# Update links in referring docs
rg -l "old-file.md" | xargs sed -i 's|old-file.md|_archive/old-file.md|g'
```

### Duplicate Removal Commands

```bash
# Remove file from git tracking (keeps local copy)
git rm --cached file-to-remove

# Remove completely
git rm file-to-remove

# Update .gitignore
echo ".DS_Store" >> .gitignore
echo "*.pyc" >> .gitignore
```

---

## Coordination with Agent 1 (RESEARCHER)

**File Scope Separation:**
- **Agent 1:** `docs/research/`, `docs/blog-drafts/`, `docs/guidelines/`
- **Agent 2:** `docs/planning/hygiene-*`, `docs/_archive/`, any doc for link fixes

**Potential Conflicts:**
- Both might edit same doc file to fix different issues
- Solution: Agent 2 checks Agent 1's active branch before editing shared files

**Communication:**
```markdown
## Notice: Agent 2 → Agent 1

I need to fix broken links in `docs/research/documentation-handoff-analysis.md`.

Are you currently editing this file? If yes, I'll wait for your handoff before fixing links.

If no, I'll proceed with link fixes on my hygiene branch.
```

---

## Metrics & Success Criteria

### Repository Health Targets

**File Count:**
- `docs/`: < 50 top-level files (move to subfolders)
- `docs/_archive/`: Clearly labeled historical content
- Zero `.DS_Store`, `.coverage` in git

**Link Health:**
- `./scripts/check_links.py` → Zero broken links
- All redirected stubs point to valid locations

**Naming Consistency:**
- 95%+ docs in kebab-case
- All directories in lowercase
- Clear naming patterns documented

**Repository Size:**
- .git/ size: Monitor for bloat (track in hygiene reports)
- No files >5MB in docs/ (images in `docs/images/` only)

**Worktree Hygiene:**
- Zero stale worktrees >7 days old
- Clear worktree cleanup process

### Deliverable Quality (Audit Mode)

**Hygiene Report Standards:**
- Executive summary (5 top issues)
- Categorized findings (P0/P1/P2)
- Actionable recommendations with commands
- Effort estimates for each recommendation
- Clear acceptance criteria

**Typical Report Structure:**
```markdown
# Hygiene Audit: [Topic] - YYYY-MM-DD

## Executive Summary
Found X issues across Y categories. Top priority: [P0 issue].

## Findings by Priority

### P0 (Critical - Fix Immediately)
1. [Issue] - [Impact] - [Effort: Xh]
   - **Commands:** ...
   - **Files affected:** ...

### P1 (High - Fix Soon)
...

### P2 (Medium - Nice to Have)
...

## Implementation Plan
Phase 1: [P0 fixes] - [total effort]
Phase 2: [P1 fixes] - [total effort]
Phase 3: [P2 fixes] - [total effort]

## Commands Summary
```bash
# Copy-paste ready commands
...
```
```

---

## Quick Reference

### Agent 2 Workflow Summary

**Mode 1 (Audit):** Document → Handoff → MAIN approves → Execute (Mode 2 or MAIN)
**Mode 2 (Implement):** Execute → Verify → Handoff → MAIN reviews → Push/Merge

### Priority Levels

- **P0 (Critical):** Broken links, tracked artifacts, security issues → Fix immediately
- **P1 (High):** Archive obsolete docs, duplicate removal → Fix within sprint
- **P2 (Medium):** Naming standardization, structure improvements → Nice to have

### Key Scripts

```bash
./scripts/check_links.py                    # Verify no broken links
rg --files -g "*.DS_Store"                  # Find OS metadata
git worktree list                           # List worktrees
find . -name ".coverage" -not -path ".venv" # Find build artifacts
```

---

**Version:** 2.0
**Created:** 2026-01-07
**Agent:** PROJECT HYGIENE & MAINTENANCE (Agent 2)
**Status:** Active - Ready for hygiene tasks
