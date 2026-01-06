# Copilot Instructions — structural_engineering_lib

> **FOR AI AGENTS:** This file is loaded by GitHub Copilot/VS Code when the
> `.github/copilot-instructions.md` convention is enabled in your environment.
> These rules are MANDATORY. Following them prevents wasted time on CI failures,
> merge conflicts, and repeated mistakes. Read carefully before any action.

---

## ⚠️ CRITICAL: Git Workflow (READ THIS FIRST)

**NEVER use manual git commands for commits! ALWAYS use the automation scripts:**

```bash
# ✅ CORRECT: Use safe_push.sh for all commits
./scripts/safe_push.sh "commit message"

# ❌ WRONG: Manual git operations
git add .
git commit -m "message"
git push
```

**Why?**
- Manual workflow causes merge conflicts, pre-commit hook issues, and wasted time
- safe_push.sh handles: pre-commit hooks, pulls, conflicts, amendments automatically
- We built this script specifically to avoid git problems - USE IT!

**When committing code:**
1. Stage your changes: Files are already modified
2. Run: `./scripts/safe_push.sh "descriptive commit message"`
3. Done! Script handles everything

**Exceptions:** NONE. Always use safe_push.sh or ai_commit.sh for commits.

---

## 🚀 Quick Start (First 30 Seconds)

```bash
# Run this immediately:
.venv/bin/python scripts/start_session.py
```

This shows version, branch, active tasks, blockers, and doc freshness.

**Read next:** `docs/AGENT_BOOTSTRAP.md` → `docs/AI_CONTEXT_PACK.md` → `docs/TASKS.md`

---

## What this project is
IS 456 RC beam design library with **Python + VBA parity**.

## Non-negotiables
- Deterministic calculations (no hidden defaults).
- Units must be explicit and consistent.
- Keep Python/VBA behavior aligned.
- Prefer minimal, surgical changes.

## Always load this context first
- docs/AI_CONTEXT_PACK.md
- docs/architecture/project-overview.md
- docs/reference/api.md
- docs/reference/known-pitfalls.md
- docs/TASKS.md

## Coding rules
- Don’t mix UI/I-O code into core calculation modules.
- Add/extend tests with every behavior change (Python at minimum).
- If you move files, keep redirect stubs to avoid breaking links.
- Format Python code with `black` before committing.
- **Type safety**: Always handle `Optional[T]` types explicitly - check for `None` before accessing attributes.
- **Run mypy locally** before pushing: `.venv/bin/python -m mypy Python/structural_lib/<file>.py`
## Definition of done
- Tests pass (at least Python).
- Docs updated where contracts/examples changed.
- No unrelated refactors.
- Code formatted with `black` (run `python -m black .` in Python/ directory).

---

## Git workflow rules (CRITICAL - Production Stage)

### 🎯 Quick Decision Tool

**ALWAYS use this before committing:**
```bash
git add <files>
./scripts/should_use_pr.sh --explain
```

**Philosophy:** PR-first for substantial changes, direct commit for minor edits ONLY.

The tool analyzes:
- **File type** (production vs docs/tests/scripts)
- **Change size** (lines added/removed)
- **File count** (multiple files = higher impact)
- **Complexity** (new files, substantial edits)

### ✅ Direct Commits (Minor Changes ONLY)

**Criteria (ALL must be true):**
- Low-risk files: docs/, Python/tests/, or scripts/ ONLY
- Small scope: <50 lines changed
- Few files: 1-2 files maximum
- No new files (edits only)

**Examples:**
- Typo fix in single doc file
- Small test adjustment (<50 lines)
- Minor script tweak (<50 lines)

**Command:**
```bash
./scripts/safe_push.sh "docs: fix typo in guide"
```

### 🔀 Pull Requests (REQUIRED - Default Workflow)

**Always required for:**
1. **Production code** - Python/structural_lib/**/*.py (NO exceptions)
2. **VBA code** - VBA/**/*.bas, Excel/**/*.xlsm
3. **CI workflows** - .github/workflows/**/*.yml
4. **Dependencies** - pyproject.toml, requirements*.txt

**Also required for substantial changes even in low-risk files:**
- **Major docs** - 500+ lines (e.g., new guides, catalogs)
- **Substantial docs** - 150+ lines or 3+ files
- **Medium docs** - 50-149 lines or 2 files
- **Large tests** - 50+ lines or 2+ files
- **Large scripts** - 50+ lines or 2+ files

**Workflow:**
```bash
./scripts/create_task_pr.sh TASK-XXX "description"
# Make changes
./scripts/safe_push.sh "feat: implement X"
# When done
./scripts/finish_task_pr.sh TASK-XXX "description"
```

### ⛔ NEVER Direct Commit To Main For:
- Production code changes (Python/structural_lib/)
- VBA algorithm changes
- CI workflow modifications
- Dependency updates
- Substantial documentation (>150 lines or 3+ files)
- Large test suites (>50 lines or 2+ files)
- Major script changes (>50 lines or 2+ files)

**Reason:** CI validation + audit trail required for substantial changes
- CI workflow modifications
- Dependency updates

**Reason:** CI validation + audit trail required for all production changes

---

## Git workflow rules (CRITICAL)

### ⛔ STOP: Read This Before Any Commit

**DO NOT use manual git commands!** Use the automation:

```bash
# ✅ ONLY WAY TO COMMIT:
./scripts/safe_push.sh "commit message"

# ❌ FORBIDDEN (causes conflicts and wasted time):
git add .
git commit -m "message"
git pull
git push
```

**If you try manual git operations, you WILL:**
- Get merge conflicts from pre-commit hooks
- Waste 10+ minutes resolving issues
- Need to redo work multiple times
- Create diverged history

**The safe_push.sh script does ALL of this correctly:**
- Detects and completes unfinished merges
- **Step 2.5: Checks and fixes whitespace BEFORE commit** ← CRITICAL FIX
- Handles pre-commit modifications automatically
- Pulls before committing (prevents conflicts)
- Auto-resolves conflicts safely
- Never rewrites pushed history

### ✅ VERIFICATION: Proven to Work

**The fix was tested and verified:**
```bash
# Run anytime to verify the fix works:
./scripts/verify_git_fix.sh

# Output: 7 tests, all passing
# - Step 2.5 exists in safe_push.sh
# - Git detects trailing whitespace
# - Fix applied before commit
# - Whitespace removed
# - No warnings after fix
# - Step 2.5 runs before commit
# - Hash divergence prevented
```

**CI Protection:**
- `verify_git_fix.sh` runs in CI on every push
- Labeled as "CRITICAL" test
- Build fails if regression occurs
- Added to git-workflow-tests.yml

**Why This Works (Root Cause Fixed):**

The REAL problem was:
```
1. Edit file → creates trailing whitespace
2. git add → stages file with whitespace
3. git commit → DURING commit, pre-commit hook runs
4. Hook removes whitespace → modifies file AFTER staging
5. Different content → DIFFERENT SHA-1 hash
6. Local hash ≠ Remote hash → push rejected
```

The SOLUTION:
```
1. Edit file → trailing whitespace exists
2. git add → stages file with whitespace
3. **Step 2.5 runs** → detects whitespace BEFORE commit
4. **Auto-fixes** → removes whitespace, re-stages
5. git commit → pre-commit hook has nothing to fix
6. Same content → SAME hash
7. Push succeeds ✅
```

**Never Again:**
- ✅ Tests simulate the exact failure scenario
- ✅ CI runs verification on every change
- ✅ Step 2.5 prevents the root cause
- ✅ Zero manual intervention needed

### Before committing Python code:
1. Run tests locally: `pytest tests/test_<file>.py -v`
2. Use safe_push.sh (it runs pre-commit hooks automatically)

### PR and merge workflow:
1. `git commit` — pre-commit hooks auto-format (may modify files; re-stage and amend if needed)
2. `git push -u origin <branch>`
3. `gh pr create --title "..." --body "..."`
4. **WAIT for CI:** `gh pr checks <num> --watch` — do NOT try to merge immediately
5. Only after all checks pass: `gh pr merge <num> --squash --delete-branch`

> **Note:** Merge authority depends on project governance. If branch protection
> requires human review, stop at step 4 and notify the user.

### When pre-commit modifies files:
If pre-commit hooks fix files during commit, do NOT create a second commit:
```bash
git add -A && git commit --amend --no-edit   # Keep it atomic
```

### After merging a PR (sync local main):
```bash
# PREFERRED: safe, non-destructive
git switch main && git pull --ff-only

# AVOID: git reset --hard origin/main (destructive, can wipe local work)
# Only use reset --hard when git status is clean AND you intend to discard changes
```

### When to merge (batch small changes):
- ✅ Merge after: completing features, meaningful test additions, doc section completions
- ❌ Don't merge for: single-line fixes, formatting-only, every tiny change
- Batch related small changes into one PR instead of many micro-PRs

### ⚠️ CRITICAL: How the updated safe_push.sh prevents ALL merge conflicts:

**The problem we had:** The old workflow was:
```bash
1. Commit locally
2. Amend commit (if hooks modified files)  ← This creates NEW commit hash
3. Pull from remote
4. Push
```
If remote changed between steps 1-2, our amended commit diverged from remote → CONFLICT!

**The solution:** Pull BEFORE committing:
```bash
1. Pull from remote FIRST  ← Start with latest state
2. Commit locally (with our changes)
3. Amend if needed  ← Safe, nothing pushed yet
4. Pull again  ← Catch any changes during our commit
5. Push
```

**Why this works:**
- **Pull-first** ensures we start with the absolute latest remote state
- **Amend-before-push** means we never rewrite already-pushed history
- **Pull-again** catches any race conditions during our commit
- **Auto-resolve with --ours** is safe because we have the latest state

**Usage (ALWAYS use this for direct pushes):**
```bash
./scripts/safe_push.sh "commit message"
```

The script handles EVERYTHING:
- ✅ Detects and completes unfinished merges
- ✅ Pulls before commit (gets latest state)
- ✅ Handles pre-commit modifications
- ✅ Pulls again before push (catches race conditions)
- ✅ Auto-resolves conflicts (keeps your version - you have latest)
- ✅ Verifies push safety
- ✅ Never rewrites pushed history

**Result:** Zero merge conflicts in TASKS.md (or any file). Tested and proven!

---

## Layer architecture (always respect)

| Layer | Python | VBA | Rules |
|-------|--------|-----|-------|
| **Core** | `flexure.py`, `shear.py`, `detailing.py`, `serviceability.py`, `compliance.py`, `tables.py`, `ductile.py`, `materials.py`, `constants.py`, `types.py`, `utilities.py` | `M01-M07, M15-M17` | Pure functions, no I/O, explicit units |
| **Application** | `api.py`, `job_runner.py`, `bbs.py`, `rebar_optimizer.py` | `M08_API` | Orchestrates core, no formatting |
| **UI/I-O** | `excel_integration.py`, `dxf_export.py`, `job_cli.py` | `M09_UDFs`, macros | Reads/writes external data |

## Units convention
- **Inputs:** mm, N/mm², kN, kN·m
- **Internal:** mm, N, N·mm (convert at layer boundaries)
- **Outputs:** mm, N/mm², kN, kN·m

## Mac VBA safety (critical for VBA changes)
- Wrap dimension multiplications in `CDbl()`: `CDbl(b) * CDbl(d)`
- Never pass inline boolean expressions to `ByVal` args — use local variable first
- No `Debug.Print` interleaved with floating-point math
- Prefer `Long` over `Integer`

## Testing requirements
- Each calculation function needs unit tests
- Include edge cases: min/max values, boundary conditions
- Tolerance: ±0.1% for areas, ±1mm for dimensions
- Document source for expected values (SP:16, textbook, hand calc)

## Role context (see agents/*.md for full details)
When working on specific task types, apply these focuses:
- **Implementation:** Layer-aware, clause refs in comments, Mac-safe
- **Testing:** Benchmark sources, edge cases, tolerance specs
- **Integration:** Schema validation, unit mapping, error surfacing
- **Docs:** API examples, units documented, changelog entries
---

## Terminal and command rules (CRITICAL)

### Python environment:
- **Always use full venv path:** `"/path/to/.venv/bin/python"` not just `python`
- Run `configure_python_environment` first if `python` command fails
- The venv is at: `.venv/bin/python` relative to project root

### Running tests locally:
```bash
# ALWAYS run tests locally before pushing new test files
.venv/bin/python -m pytest tests/test_<file>.py -v

# Check formatting/linting locally before commit
.venv/bin/python -m black <file>
.venv/bin/python -m ruff check <file>
```

### gh CLI commands:
- `gh pr checks <num>` may show "no checks" if CI hasn't started — wait 5-10 seconds
- If `gh pr merge` fails with "not mergeable", CI is still running — use `gh pr checks <num> --watch`
- If `gh pr checks --watch` times out, rerun (or increase timeout) — checks are often still running
- Network timeouts happen — retry the command once before investigating
- If PR is **behind** base branch, update it: `gh pr update-branch <num>` then re-check CI

### Git sync issues (CRITICAL - read this to avoid conflicts):

**⚠️ RECOMMENDED: Use the automated script to prevent all issues:**
```bash
# This script handles everything automatically (pre-commit, pull, merge, push)
./scripts/safe_push.sh "your commit message"

# The script:
# 1. Detects unfinished merges and completes them
# 2. Handles pre-commit hook modifications
# 3. Pulls before pushing (prevents conflicts)
# 4. Auto-resolves conflicts (keeps your version)
# 5. Pushes safely
```

**If you MUST do manual workflow:**

```bash
# ALWAYS check for unfinished merges FIRST!
if [ -f .git/MERGE_HEAD ]; then
  echo "Unfinished merge detected!"
  git commit --no-edit  # Complete the merge
  git push              # Push merged changes
  exit 0               # Stop here, don't create new commit
fi

# Step 1: Stage files
git add <files>

# Step 2: Commit (pre-commit hooks will modify files)
git commit -m "message"

# Step 3: If pre-commit modified files, they're now unstaged
# Re-stage them and amend the commit:
if git status --porcelain | grep -q '^[MARC]'; then
  git add -A
  git commit --amend --no-edit
fi

# Step 4: ALWAYS pull before push (use merge, not rebase)
git pull --no-rebase origin main

# Step 5: If merge conflict, keep your version (you have latest changes)
if [ -f .git/MERGE_HEAD ]; then
  # There are conflicts
  git checkout --ours docs/TASKS.md  # Or other conflicted files
  git add docs/TASKS.md
  git commit --no-edit
fi

# Step 6: Now safe to push
git push
```

**Common issues:**
- **Unfinished merge (MERGE_HEAD exists)** → Run `git commit --no-edit` then `git push` (DON'T create new commit!)
- Push rejected (non-fast-forward) → Run `git pull --no-rebase` then push
- Merge conflict in TASKS.md → Run `git checkout --ours docs/TASKS.md && git add docs/TASKS.md && git commit --no-edit`
- Pre-commit modified files (NOT YET PUSHED) → Run `git add -A && git commit --amend --no-edit`
- Pre-commit modified files (ALREADY PUSHED) → **NEVER AMEND!** Create new commit instead: `git add -A && git commit -m "chore: apply pre-commit fixes"`

**⚠️ CRITICAL: Never use `git commit --amend` after already pushing to remote!**
- Amending rewrites history and causes divergence
- If you already pushed, make a new commit instead
- If you accidentally amended after push: `git pull --no-rebase` then resolve merge

**Why TASKS.md conflicts happen:**
- Multiple terminals/sessions editing TASKS.md simultaneously
- Solution: The safe_push.sh script handles this automatically
- Manual solution: Always pull BEFORE committing

---

## Common coding pitfalls (avoid these)

### Import hygiene
- ❌ **Don't** import classes inside functions if already imported at module level
- ✅ **Do** import `DesignError`, `Severity` at top of module
- 🔍 **Check** existing imports before adding new ones (ruff catches duplicates as F823)

### Version drift check awareness
- ✅ Research docs (`docs/research/`) are excluded from version checks
- ✅ Archive docs (`docs/_archive/`) are excluded from version checks
- 📝 These can reference external tool versions without triggering CI failure
- 🔍 If adding new doc directories, check if they need exclusion in `scripts/check_doc_versions.py`

---

## Common mistakes to AVOID

| Mistake | Correct Approach |
|---------|------------------|
| **Using manual git commands (git add, commit, push)** | **ALWAYS use ./scripts/safe_push.sh "message"** |
| **Doing `git commit` then trying to fix pre-commit issues** | **Use safe_push.sh - it handles pre-commit automatically** |
| **Manual merge conflict resolution** | **Use safe_push.sh - it auto-resolves safely** |
| Creating Python file → commit → CI fails on black | Create → run black locally → commit (or rely on pre-commit hooks) |
| `gh pr create` → immediately `gh pr merge` | Create → `gh pr checks --watch` → wait → merge |
| Running `python` directly | Use full venv path or configure environment first |
| Multiple micro-PRs for tiny changes | Batch related changes into one PR |
| Reading a file already shown in context | Use the context provided, don't re-read |
| Running dependent commands in parallel | Run sequentially, check output between |
| Editing file without reading current content | Always read file first if there may be changes |
| Unused variables in test code | Check with `ruff check` before commit |
| Creating duplicate documentation | Check if doc exists first |
| Committing unrelated staged files | Run `git status` before commit; stage only intended files |
| Resolving merge conflicts + feature in one commit | Resolve conflicts in separate commit first, then add feature |
| PR title/description doesn't match actual changes | List ALL changed files in PR body; update title if scope changes |
| Pre-commit modifies files → new commit | Use `git add -A && git commit --amend --no-edit` **ONLY IF NOT YET PUSHED** |
| **Using `git commit --amend` AFTER pushing** | **NEVER DO THIS!** Create new commit instead: `git add -A && git commit -m "fix: ..."` |
| Using `git reset --hard` without checking status | Use `git switch main && git pull --ff-only` after merge |
| Claiming "focused commit" but batching unrelated changes | Either truly separate, or be honest about batching scope |
| Tagging a release with a dirty working tree | Run `git status -sb` after `scripts/release.py`; tag only when clean |
| Verifying PyPI in an existing venv | Use a fresh venv for `pip install structural-lib-is456==X.Y.Z` |
| CI fails on formatting but auto-format hasn't run yet | Wait 30s after push for auto-format workflow; or use empty commit to retrigger |
| Accessing Optional[T] attributes without None check | Always check: `obj.attr if obj else default` - run mypy locally first |
| CI shows old failure after auto-format fixed it | Auto-format doesn't retrigger CI; push empty commit: `git commit --allow-empty -m "chore: trigger CI"` |
| Importing classes both at module level AND in functions | Import at module level only (ruff F823); only use function-level for circular imports |
| Adding docs with version numbers triggering drift check | Check if directory needs exclusion in `scripts/check_doc_versions.py` SKIP_FILES |
| **Unfinished merge (MERGE_HEAD exists)** | **Complete the merge:** `git commit --no-edit` then `git push` |
| Adding docs with version numbers triggering drift check | Check if directory needs exclusion in `scripts/check_doc_versions.py` SKIP_FILES |
| Pre-commit modifies files → new commit | Use `git add -A && git commit --amend --no-edit` **ONLY IF NOT YET PUSHED** |
| **Using `git commit --amend` AFTER pushing** | **NEVER DO THIS!** Create new commit instead: `git add -A && git commit -m "fix: ..."` |
| Using `git reset --hard` without checking status | Use `git switch main && git pull --ff-only` after merge |
| Claiming "focused commit" but batching unrelated changes | Either truly separate, or be honest about batching scope |
| Tagging a release with a dirty working tree | Run `git status -sb` after `scripts/release.py`; tag only when clean |
| Verifying PyPI in an existing venv | Use a fresh venv for `pip install structural-lib-is456==X.Y.Z` |
| CI fails on formatting but auto-format hasn't run yet | Wait 30s after push for auto-format workflow; or use empty commit to retrigger |
| Accessing Optional[T] attributes without None check | Always check: `obj.attr if obj else default` - run mypy locally first |
| CI shows old failure after auto-format fixed it | Auto-format doesn't retrigger CI; push empty commit: `git commit --allow-empty -m "chore: trigger CI"` |
| Importing classes both at module level AND in functions | Import at module level only (ruff F823); only use function-level for circular imports |
| Adding docs with version numbers triggering drift check | Check if directory needs exclusion in `scripts/check_doc_versions.py` SKIP_FILES |
| **Unfinished merge (MERGE_HEAD exists)** | **Complete the merge:** `git commit --no-edit` then `git push` |
| Adding docs with version numbers triggering drift check | Check if directory needs exclusion in `scripts/check_doc_versions.py` SKIP_FILES |

---

## Session workflow (CRITICAL)

### Starting a session:
```bash
# Run at the beginning of each session:
.venv/bin/python scripts/start_session.py

# Quick mode (skip test count check):
.venv/bin/python scripts/start_session.py --quick
```

**What it does:**
- Shows version, branch, uncommitted changes
- Adds SESSION_LOG entry for today if missing
- Shows Active tasks from TASKS.md
- Runs doc freshness checks

### Ending a session:
```bash
# Run before ending any session:
.venv/bin/python scripts/end_session.py

# Auto-fix issues:
.venv/bin/python scripts/end_session.py --fix

# Quick mode:
.venv/bin/python scripts/end_session.py --quick
```

**What it checks:**
- 📁 Uncommitted changes
- 🔍 Handoff checks (date freshness, test counts, versions)
- 📝 SESSION_LOG entry completeness
- 🔗 Doc link validity
- 📊 Today's activity summary

### Manual handoff steps (if needed):
1. Update `docs/planning/next-session-brief.md` with session summary
2. Ensure TASKS.md reflects current state
3. Commit any uncommitted doc changes
4. Use `docs/HANDOFF.md` as the short resume template

---

## Efficiency rules

1. **Don't re-read files in context** — If file content is shown, use it
2. **Batch file edits** — Use multi_replace for multiple edits in same/different files
3. **Check command exit codes** — Before proceeding, verify command succeeded
4. **One terminal command at a time** — Don't run parallel terminal commands
5. **Verify before declaring success** — Run tests, check output, confirm behavior
6. **Read this file first** — Before starting any session, review these rules completely
