# Git & GitHub Governance Guide

**Status:** Active
**Owner:** DEVOPS Agent
**Purpose:** Define strict, professional standards for version control, branching, and repository management to ensure long-term maintainability and collaboration.

---

## 1. Repository Philosophy

We treat this repository as a **professional open-source product**, not a personal scratchpad.
*   **Source of Truth:** The code in the repo is the truth. Excel files (`.xlsm`) are *artifacts* generated from the code, not the source itself.
*   **Clean History:** We value a linear, readable commit history.
*   **Traceability:** Every change must link to a Task or Issue.

---

## 2. Branching Strategy (Trunk-Based Development)

We use a simplified **Trunk-Based Development** model suitable for a small, high-velocity team (Human + AI Agents).

### 2.1 Branches
*   **`main` (Protected):**
    *   The "Golden Master". Always deployable.
    *   Contains only tested, verified code.
    *   **Rule (Solo Dev):** Direct pushes allowed for maintainer, but CI must pass.
        *   Use PRs for significant changes (breaking changes, new features, risky refactors).
        *   Use direct push for docs/research updates (any size) and routine fixes/tests.
        *   CI runs on every push — if it fails, fix immediately.
        *   Release tags are created on the merge commit or on main after direct push.
*   **`feat/task-ID-description`:**
    *   Feature branches for specific tasks.
    *   Naming convention: `feat/task-017-etabs-import`, `fix/task-012-shear-bug`.
    *   **Lifespan:** Short (1-2 sessions max). Merge back to `main` quickly.
    *   **Optional** for routine changes; required for significant features/refactors.

### 2.2 Workflow
1.  **Start:** `git checkout -b feat/task-018-schedule`
2.  **Work:** Edit files, run tests.
3.  **Commit:** Frequent, atomic commits.
4.  **Verify:** Run full test suite.
5.  **Merge:** Squash and Merge into `main` (or Rebase and Merge).
6.  **Delete:** Delete the feature branch.

### 2.2.1 Solo Developer Workflow (Simplified)

**For docs-only changes (any size):**

1.  **Direct on main** (fastest)
    ```bash
    # make changes
    ./scripts/ai_commit.sh "docs: update guide"
    # CI runs automatically, watch for failures
    ```

**For all other changes (default):**

1.  **Use PR workflow:**
    ```bash
    ./scripts/create_task_pr.sh TASK-XXX "short description"
    # make changes
    ./scripts/ai_commit.sh "feat: implement X"
    ./scripts/finish_task_pr.sh TASK-XXX "short description"
    ```

**Emergency fixes:**

If CI fails on main:
1.  `git revert HEAD` (immediate rollback)
2.  Fix in branch, test locally, then push fix

**Rule of thumb:** Docs-only → direct push. Everything else → PR.

### 2.3 Branch Protection Baseline (GitHub Settings)

This repo prefers **low-maintenance security**: enforce safety at the repo-settings layer instead of complex workflow tricks.

Implementation note:
* Prefer **GitHub Rulesets** (the newer UI) over legacy branch protection rules.
* If the ruleset enables “Require branches to be up to date”, PR branches must be updated before merge.

Recommended protection rule for `main`:
* Require a pull request before merging
* Require status checks to pass before merging
    * Prefer "Require branches to be up to date" (prevents merging stale PRs)
* Do not allow force pushes
* Do not allow deletions

Solo default:
* Leave "Include administrators" OFF to keep an emergency escape hatch
* Skip "Restrict who can push" and "Require reviews" unless collaborating
---

### 2.3.1 Current Protection Rules (as of 2026-01-06)

**Branch:** `main`

**Rules Enabled:**
- ✅ Required status checks must pass on `main`:
  - `Quick Validation (Python 3.9 only)` — fast PR checks (lint, mypy, contracts, core tests)
- ✅ Force pushes disabled
- ✅ Branch deletion disabled
- ✅ PR-first: required for code/CI/deps; docs-only direct commits allowed

Notes:
- `CodeQL` runs on pushes and PRs, but is not currently configured as a required status check for `main`.

**CI Workflows:**
- `.github/workflows/fast-checks.yml` — runs on PRs and pushes to `main`
- `.github/workflows/python-tests.yml` — full matrix runs after merge to `main`
- OS: ubuntu-latest

**Workflow:**
- Direct push allowed for docs/research-only changes (any size)
- All commits trigger CI (fast checks + full tests after merge)
- Failed CI = immediate notification
- PRs required for production code, CI changes, and dependencies

**Implications:**
- Fast iteration for routine work
- CI quality gate maintained
- Reviews are not required in this repo. If enabled later, GitHub blocks self-approval.
- Clean revert if CI fails
- Tags can be created after direct push to `main` or after PR merge

**Format Check Workflow:**
- `.github/workflows/auto-format.yml` now runs **check-only** on PRs
- No auto-commits are pushed by CI

**Best Practice:**
- ✅ **Use pre-commit hooks** (they run `black` and `ruff` locally)
- ✅ Commit → hooks fix → re-stage → commit (or amend)
- ✅ CI only verifies formatting

---
Supply-chain stance:
* Avoid high-maintenance hardening (e.g., pinning every GitHub Action to a commit SHA) unless there is a clear need.

### 2.4 GitHub CLI (Low-Friction PR Workflow)

When working from the terminal, prefer `gh` to keep the workflow repeatable and fast:

```bash
# Complete PR workflow (recommended)
git checkout -b feat/task-142-new-feature
# ... make changes ...
git add -A
git commit -m "feat: implement new feature"  # Pre-commit hooks run here
# If pre-commit modifies files: git add -A && git commit --amend --no-edit
git push -u origin feat/task-142-new-feature
gh pr create --title "feat: implement new feature" --body "Implements TASK-142..."
./scripts/pr_async_merge.sh status  # WAIT for all CI checks
gh pr merge --squash --delete-branch  # Only after CI passes
```

**Step-by-step:**
1. **Create branch:** `git checkout -b feat/task-142-new-feature`
2. **Make changes & commit:** `git add -A && git commit -m "..."`
3. **Push branch:** `git push -u origin feat/task-142-new-feature`
4. **Create PR:** `gh pr create --title "..." --body "..."`
5. **⚠️ CRITICAL: Wait for CI:** `gh pr checks <PR_NUMBER> --watch`
6. **Merge:** `gh pr merge <PR_NUMBER> --squash --delete-branch`
7. **Sync local:** `git checkout main && git pull --ff-only`

**Common commands:**
* Check PR status: `gh pr checks <PR_NUMBER>`
* Update branch (if behind): `gh pr update-branch <PR_NUMBER>`
* View PR: `gh pr view <PR_NUMBER>`
* List PRs: `gh pr list`

> **Critical:** Never run `gh pr merge` immediately after `gh pr create`. Always wait for CI.

### 2.5 Pre-commit Hooks

This repo uses pre-commit hooks to catch issues before they reach CI:

```bash
# One-time setup
pre-commit install

# Hooks run automatically on git commit
```

**Installed hooks:**
- `black` — Python formatting
- `ruff` — Python linting
- `trailing-whitespace` — Remove trailing spaces
- `end-of-file-fixer` — Ensure files end with newline
- `mixed-line-ending` — Normalize line endings

**If hooks modify files:** Re-stage and commit again.

See `.github/copilot-instructions.md` for agent-specific workflow rules.

---

### 2.6 Local Workflow Guardrails (When PRs are required)

These are the rules that prevent rebase pain and “why can’t I push?” surprises.

**Golden rules:**
- If a ruleset requires PRs for `main` (collaboration mode), **never commit on `main`**. Always branch first.
- **If you accidentally commit on `main` under PR-required rules:**
  1) `git switch -c <branch>`
  2) `git push -u origin <branch>`
  3) Open a PR and merge it normally
- **Sync `main` only after PR merge:** `git fetch origin` + `git rebase origin/main`
- **Delete local branches after merge:** `git branch -d <branch>`

**Why this matters:** When PRs are required, committing on `main` triggers rejected pushes and messy rebases.

---

### 2.7 Quick Local Checks (Before PR)

Use the fast pre-flight checks below to avoid CI failures:

```bash
# Code (fast)
./scripts/quick_check.sh

# Code + coverage gate
./scripts/quick_check.sh --cov

# Docs-only
./scripts/quick_check.sh docs
```

For a full run, use `scripts/ci_local.sh`.

---

### 2.8 Troubleshooting Common Git Issues

#### Issue: `! [rejected] main -> main (non-fast-forward)`

**Cause:** Remote has commits you don't have locally (someone else pushed or branch updated).

**Solution:**
```bash
# Pull and rebase
git pull --rebase origin main
git push

# Alternative: fetch and reset (only if you're sure local changes are safe)
git fetch origin
git rebase origin/main
git push
```

**Prevention:** Always pull before pushing, especially after merging PRs.

#### Issue: CI fails on formatting

**Cause:** Local formatting not applied before push.

**Solution:**
```bash
.venv/bin/python -m black Python/
.venv/bin/python -m ruff check Python/
git add -A
git commit -m "style: format"
git push
```

**Prevention:** Use pre-commit hooks to format code locally before pushing.

#### Issue: mypy type errors on Optional types

**Cause:** Accessing attributes on `Optional[Type]` without checking for `None`.

**Example Error:** `Item "None" of "Optional[CostBreakdown]" has no attribute "total_cost"`

**Solution:**
```python
# BAD - mypy will error
result.cost_breakdown.total_cost

# GOOD - check for None first
if result.cost_breakdown:
    cost = result.cost_breakdown.total_cost
else:
    cost = 0.0

# GOOD - ternary operator
cost = result.cost_breakdown.total_cost if result.cost_breakdown else 0.0

# GOOD - when sorting
sorted(items, key=lambda x: x.cost.total if x.cost else float('inf'))
```

**Prevention:** Run `python -m mypy <file>` locally before committing.

#### Issue: Pre-commit hooks modified files

**Cause:** Hooks fixed formatting/whitespace automatically.

**Solution:**
```bash
# Re-stage modified files and amend commit
git add -A
git commit --amend --no-edit

# OR create new commit
git add -A
git commit -m "chore: apply pre-commit fixes"
```

**This is NORMAL** — hooks are doing their job!

#### Issue: Merge conflicts after `git pull --rebase`

**Cause:** Local and remote changes conflict.

**Solution:**
```bash
# Fix conflicts manually, then:
git add <conflicted-files>
git rebase --continue

# OR abort and try merge instead:
git rebase --abort
git pull --no-rebase origin main
```

#### Issue: Can't push — pre-commit hooks fail

**Cause:** Code doesn't pass pre-commit checks (black, ruff, custom scripts).

**Solution:**
```bash
# Read the error messages carefully
# Fix the issues, then try again
git add <fixed-files>
git commit -m "..."

# OR skip hooks temporarily (NOT RECOMMENDED)
git commit --no-verify -m "..."
```

**Best Practice:** Fix the issues rather than skipping checks.

---

## 3. Commit Message Convention (Conventional Commits)

We follow [Conventional Commits](https://www.conventionalcommits.org/) to enable automated changelogs.

**Format:** `<type>(<scope>): <description>`

### Types
*   **`feat`**: A new feature (corresponds to `MINOR` in SemVer).
*   **`fix`**: A bug fix (corresponds to `PATCH` in SemVer).
*   **`docs`**: Documentation only changes.
*   **`style`**: Formatting, missing semi-colons, etc; no code change.
*   **`refactor`**: A code change that neither fixes a bug nor adds a feature.
*   **`test`**: Adding missing tests or correcting existing tests.
*   **`chore`**: Build process, auxiliary tools, library upgrades.

### Examples
*   `feat(core): implement doubly reinforced beam logic`
*   `fix(shear): correct tau_c interpolation for M40`
*   `docs(readme): update installation instructions`
*   `test(integration): add regression snapshot for B1`

---

## 4. Versioning (SemVer)

We follow **Semantic Versioning 2.0.0** (`MAJOR.MINOR.PATCH`).

*   **MAJOR (v1.0.0):** Breaking changes (e.g., changing function signatures in `M08_API`).
*   **MINOR (v0.5.0):** New features in a backward-compatible manner (e.g., adding Schedule generation).
*   **PATCH (v0.5.1):** Backward-compatible bug fixes.

**Release Process:**
1.  PM approval for version bump (no auto-bumps).
2.  Append to `docs/releases.md` (immutable ledger; never edit past entries).
3.  Update `CHANGELOG.md` (append-only).
4.  Tag the commit: `git tag -a v0.5.0 -m "Release v0.5.0"`
5.  Push tag: `git push origin v0.5.0`

---

## 5. Excel & VBA Specifics

Git handles text well, but hates binary files (`.xlsm`, `.xlam`).

### 5.1 The "Export Rule"
*   **NEVER** rely on the code inside `.xlsm` as the backup.
*   **ALWAYS** export VBA modules to `.bas` / `.cls` files in `VBA/Modules/` before committing.
*   **Why?** You cannot diff a binary Excel file. You *can* diff a `.bas` file.

### 5.2 Binary File Management
*   Treat `.xlsm` files as **binary artifacts**.
*   Commit them only when the structure changes (e.g., new sheets, named ranges).
*   Do not commit them for simple code changes (since the code lives in `VBA/Modules`).
*   `.xlam` outputs live under `VBA/Build/` (whitelisted); other add-ins stay ignored.

---

## 6. Documentation Standards

*   **README.md:** The landing page. Must answer "What is this?", "How do I install it?", "How do I use it?".
*   **CHANGELOG.md:** User-facing history of changes.
*   **docs/**: Technical documentation.
    *   Keep it close to the code.
    *   Update docs *in the same PR* as the code change.

---

## 7. UI/UX Guidelines (for GitHub)

*   **Issues:** Use Issues to track Tasks (`TASK-001`). Label them (`enhancement`, `bug`, `documentation`).
*   **Pull Requests:**
    *   Title: Matches the commit message convention.
    *   Description: Reference the Task ID. Explain *what* changed and *why*.
    *   Screenshots: Mandatory for UI changes (Excel sheets).

---

## 8. Emergency Recovery

If `main` breaks:
1.  **Revert:** `git revert <bad-commit-hash>`
2.  **Fix:** Create a `fix/` branch, repair, test, and merge.
3.  **Post-Mortem:** Document what happened in `logs/` to prevent recurrence.

---

## 9. Pre-Merge Checklist (Agents)

- **Link to Task:** Every PR references a TASK ID and the agent role (DEV/TESTER/etc.).
- **Tests:** Run `.venv/bin/python -m pytest Python/tests -q`; for Excel, run the integration harness or note "not run" with reason.
- **Wait for CI:** Use `gh pr checks <num> --watch` — never merge until all checks pass.
- **Docs:** Update relevant docs (README/API_REFERENCE/CHANGELOG/RELEASES/TASKS) in the same PR.
- **Artifacts:** Do not commit `.xlsm`/`.xlam` unless structure changed; export `.bas`/`.cls` instead.
- **Diff sanity:** Ensure no generated or local config files are included.
- **Branch hygiene:** Keep feature branches short-lived; rebase on `main` before merge if needed.

> **For AI agents:** See `.github/copilot-instructions.md` for complete workflow rules.

---

## 10. Release Governance (PM Rules)

- `docs/releases.md` is append-only and is the ledger of truth. Past entries are immutable.
- Version bumps require explicit PM approval and a tag.
- If `CHANGELOG.md` and `releases.md` conflict, `releases.md` wins.
- Keep `main` deployable; if a release fails validation, revert instead of force-pushing.

---

## 11. Best Practices Summary

### ✅ DO:
- **Use pre-commit hooks** — Install once (`pre-commit install`), saves CI time
- **Wait for CI before merging** — Use `./scripts/pr_async_merge.sh status`
- **Pull before push** — Especially after merging PRs: `git pull --ff-only`
- **Use feature branches for significant changes** — Breaking changes, new features, risky refactors
- **Amend commits when pre-commit modifies files** — `git add -A && git commit --amend --no-edit`
- **Batch related changes** — One PR per feature, not micro-PRs for every tiny change
- **Check git status before committing** — Avoid accidentally committing unrelated files
- **Use conventional commits** — `feat:`, `fix:`, `docs:`, etc.
- **Link PRs to tasks** — Every PR mentions TASK-XXX in title or body

### ❌ DON'T:
- **Don't merge immediately after creating PR** — Wait for CI
- **Don't push to PR branch without pulling first** — Always sync first
- **Don't force-push to main** — Branch protection prevents this anyway
- **Don't skip pre-commit hooks** — They catch issues before CI
- **Don't commit generated files** — `.xlsm` (export `.bas`/`.cls` instead)
- **Don't create PR without running tests** — `.venv/bin/python -m pytest -q`
- **Don't mix unrelated changes** — Keep commits focused on one thing
- **Don't ignore CI failures** — Fix immediately or revert

### 🎯 Recommended Workflow (Solo Dev):

**For docs-only changes (any size):**
```bash
# make changes
./scripts/ai_commit.sh "docs: update guide"
```

**For significant changes (code/CI/deps):**
```bash
./scripts/create_task_pr.sh TASK-142 "implement feature"
# make changes
./scripts/ai_commit.sh "feat: implement feature"
./scripts/finish_task_pr.sh TASK-142 "implement feature"
```

### 🚨 What to Do When Things Go Wrong:

| Problem | Solution |
|---------|----------|
| CI fails on main | `git revert HEAD` → fix in branch → PR |
| Can't push (non-fast-forward) | `git pull --rebase origin main` → `git push` |
| Formatting failure | Run `black`/`ruff` locally → commit → push |
| Pre-commit modified files | `git add -A && git commit --amend --no-edit` |
| Merge conflicts | Fix manually → `git add <files>` → `git rebase --continue` |
| Accidentally committed to main | `git checkout -b feat/fix` → push → PR |

### 📋 Pre-Push Checklist:

- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Tests pass locally (`.venv/bin/python -m pytest -q`)
- [ ] Commit message follows convention (`feat:`, `fix:`, `docs:`)
- [ ] No unrelated files staged (`git status`)
- [ ] Pulled latest changes (`git pull --ff-only` if on main)
- [ ] For PR: Ready to wait for CI (`./scripts/pr_async_merge.sh status`)

---

**Last Updated:** 2026-01-12
