---
owner: Main Agent
status: active
last_updated: 2026-08-07
doc_type: tutorial
complexity: beginner
tags: [learning, foundations]
---

# Module 9: Git and Version Control

> Repository-specific rule: use the canonical Codex-native workflow for live
> work. `scripts/git_state.py` is the sole local-state authority; Codex owns
> branch, commit, push, pull-request, and merge mutations after inspection.

## The Big Idea

**Git** tracks every change to every file in your project. It's like an infinite undo button — you can go back to any point in history. More importantly, it lets multiple people work on the same project without overwriting each other's work.

---

## Part 1: What Is Version Control?

### Without version control:
```
project/
├── beam_design.py
├── beam_design_v2.py
├── beam_design_v2_fixed.py
├── beam_design_v2_fixed_FINAL.py
├── beam_design_v2_fixed_FINAL_v2.py    ← Which one is current?
└── beam_design_v2_fixed_FINAL_v2_USE_THIS.py
```

### With version control (Git):
```
project/
└── beam_design.py   ← Always the current version

Git history:
  commit abc123  "fix: correct shear calculation"         ← latest
  commit def456  "feat: add column design"
  commit 789abc  "fix: unit conversion bug"
  commit 012def  "feat: initial beam design"              ← oldest

  You can see, compare, or restore ANY of these versions.
```

---

## Part 2: Git Concepts

### Repository (repo)
A folder tracked by Git. Contains all your code + full history.

### Commit
A snapshot of your code at a point in time. Each commit has:
- A unique ID (hash): `abc123def456`
- A message: "fix: correct shear calculation"
- The author and timestamp
- The actual changes (diff)

```
Commit abc123
  Author: developer@email.com
  Date:   2024-01-15 14:30
  Message: fix: correct shear calculation

  Changed files:
    M  Python/structural_lib/codes/is456/shear.py   (+5, -3)
    M  Python/tests/test_shear.py                    (+12, -0)
```

### Branch
A separate line of development. Like making a copy of the project to experiment on.

```
main:     A ── B ── C ── D ── E        ← stable, released code
                    │
feature:            └── F ── G ── H    ← new feature being developed
```

### Merge / Pull Request
Combining changes from one branch into another.

```
Before merge:
main:     A ── B ── C ── D
feature:            └── E ── F

After merge:
main:     A ── B ── C ── D ── M    ← M includes changes from E and F
```

---

## Part 3: Basic Git Commands

| Command | What It Does | When |
|---------|-------------|------|
| `git status` | Show changed files | Before committing |
| `git log --oneline -10` | Show recent history | Understanding what happened |
| `git diff` | Show exact changes | Before committing |
| `git branch` | List branches | See where you are |
| `./scripts/python_runtime.sh scripts/git_state.py --json` | Inspect bounded local state | Before any Git mutation |
| `git add -- path/to/owned-file` | Stage one verified owned path | Only after inspecting the exact diff |
| Codex commit | Save the reviewed scoped snapshot | After focused and quick gates |
| Codex push/PR | Publish without rewriting history | After exact branch/head recheck |
| Fresh remote evidence | Establish current hosted state | Never infer it from `NOT_CHECKED` |

### Example workflow:
```bash
# 1. Check current state
./scripts/python_runtime.sh scripts/git_state.py --json
git diff -- path/to/owned-file

# 2. Make changes
# ... edit files ...

# 3. Stage and commit
git add -- path/to/owned-file # Stage only the inspected owned path
# Codex creates the conventional commit after the required gates.

# 4. Push to remote
# Codex rechecks the exact head, then pushes and opens/updates the PR.
```

---

## Part 4: Conventional Commits — Meaningful Messages

A commit message should explain WHAT changed and WHY. Conventional commits add structure:

```
type(scope): description

Examples:
  feat(beam): add doubly reinforced beam design
  fix(shear): correct tau_c lookup table for M25
  docs(api): update API reference for column endpoints
  test(flexure): add benchmark tests from SP-16
  refactor(core): simplify BeamSection dataclass
  chore(deps): update Pydantic to 2.6
  ci(tests): run tests in parallel
```

### Types:

| Type | When | Example |
|------|------|---------|
| `feat` | New feature | `feat: add column design` |
| `fix` | Bug fix | `fix: correct unit conversion` |
| `docs` | Documentation | `docs: update API reference` |
| `test` | Tests only | `test: add shear benchmarks` |
| `refactor` | Code restructure (no behavior change) | `refactor: split flexure module` |
| `chore` | Maintenance | `chore: update dependencies` |
| `ci` | CI/CD changes | `ci: add Python 3.12 to matrix` |

### Why this format?
- Auto-generate changelogs
- Determine version bumps (feat = minor, fix = patch)
- Easy to scan in `git log`

---

## Part 5: Branches — Working in Parallel

### Branch strategy:
```
main (stable)
├── codex/task-042-column-design      ← Feature branch
├── codex/task-043-fix-shear-table    ← Bug fix branch
└── codex/task-044-update-docs        ← Docs branch
```

**Rules:**
- `main` is always stable and deployable
- Each task gets its own branch
- Work on your branch, then merge via Pull Request
- Never commit directly to `main`

### Create a branch:
```bash
# Create and switch to a new branch
git switch -c codex/task-042-column-design

# Work on it...
git commit -m "feat(column): add axial capacity calculation"
git commit -m "test(column): add benchmark tests"

# Push the branch
git push -u origin codex/task-042-column-design
```

---

## Part 6: Pull Requests — Code Review Gateway

A **Pull Request** (PR) is a request to merge your branch into `main`. It's where code review happens.

```
Your Branch (TASK-042)              main
  │                                  │
  │  1. Push commits                 │
  │  2. Open PR on GitHub            │
  │  3. CI tests run automatically   │
  │  4. Reviewer reads your code     │
  │  5. Reviewer approves            │
  │  6. Merge into main              │
  │ ────────────────────────────────→│
```

### PR contents:
- **Title:** "feat(column): add axial capacity calculation"
- **Description:** What changed, why, how to test
- **Changes:** Diff of all modified files
- **CI status:** ✅ All tests pass or ❌ Failures
- **Review:** Comments from other developers

### What CI checks on a PR:
```
✅ Python tests pass (pytest)
✅ React builds (npm run build)
✅ Type checks pass (pyright, tsc)
✅ Linting passes (ruff, eslint)
✅ Architecture boundaries respected
✅ No broken imports
```

---

## Part 7: Git Hooks — Automatic Checks

**Git hooks** are scripts that run automatically at certain Git events.

```
You type: git commit -m "feat: ..."
                │
                ▼
    ┌─────────────────────┐
    │  pre-commit hook     │ ← Runs BEFORE commit
    │  • Format code       │
    │  • Check types       │
    │  • Run quick tests   │
    │  • Validate imports  │
    └──────────┬──────────┘
               │ passes?
     ┌─────────┴─────────┐
     │ YES               │ NO
     ▼                   ▼
  Commit saved      Commit blocked
                    "Fix errors first"
```

### Common hooks:

| Hook | When | What It Does |
|------|------|-------------|
| `pre-commit` | Before commit is saved | Lint, format, quick checks |
| `commit-msg` | After message is written | Validate conventional commit format |
| `pre-push` | Before push to remote | Run tests |
| `post-commit` | After commit succeeds | Optional follow-up automation |

### This project's maintained controls

The former repository hook framework is archived. Normal commit hooks come from
the checked-in pre-commit configuration, while prompt routing and tool
permissions are enforced by `prompt_router.py` and `tool_permissions.py`.

---

## Part 8: Repository Git Control Plane

This project deliberately does not wrap the Git/GitHub lifecycle in a script.
That prevents a helper from silently staging unrelated files, rewriting a
branch, compressing failed evidence into success, or coupling merge to cleanup.

Start with the read-only authority:

```bash
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

The output keeps local branch, head, upstream, default base, tree, operation,
locks, and `NOT_CHECKED` remote freshness separate. A failed or missing query is
`UNKNOWN` and therefore a hold. After reviewing that evidence, Codex creates a
`codex/<task-slug>` lane, stages only intended paths, commits conventionally,
pushes without rewriting history, and opens or updates a draft pull request.
Merge and later branch/worktree retention are separate decisions.

---

## Part 9: .gitignore — What NOT to Track

Some files should never be in Git:

```
# .gitignore

# Virtual environments
.venv/
node_modules/

# Build outputs
dist/
build/
*.egg-info/

# Secrets
.env
*.key
*.pem

# OS files
.DS_Store
Thumbs.db

# IDE settings
.vscode/settings.json
.idea/

# Cache
__pycache__/
.pytest_cache/
```

**Rule:** Never commit secrets, build outputs, or dependency folders.

---

## Part 10: Common Git Mistakes and Fixes

| Mistake | What Happens | Fix |
|---------|-------------|-----|
| Committed secrets | Secrets in public history | Rotate credentials immediately; preserve the exact state and obtain an authorized, reviewed history-remediation plan |
| Committed to wrong branch | Changes on main instead of feature | Stop, inspect exact state with `git_state.py`, preserve the commit/tree, and choose an authorized fresh-lane recovery path |
| Bad commit message | "fix stuff" in history | Stop before publication; preserve and inspect the exact commit, then let Codex apply the authorized correction |
| Merge conflicts | Two people changed same line | Hold the operation, inspect owned paths and operation markers, then resolve through the canonical Codex workflow |
| Accidentally deleted file | File gone | Inspect the exact path diff and ownership; preserve current evidence before an authorized path-scoped restoration |
| Want to undo last commit | Realize mistake after commit | Preserve the commit/tree, inspect with `git_state.py`, and recover compatible intent on an authorized fresh `codex/*` lane |

### Merge conflict example:
```
<<<<<<< HEAD
def calculate_shear(b_mm, d_mm, fck):
=======
def calculate_shear(b_mm: float, d_mm: float, fck: float):
>>>>>>> feature-branch
```

**Fix:** Choose which version to keep (or combine), remove the markers, save, and commit.

---

## Part 11: GitHub — Remote Hosting

```
Your Computer          GitHub (cloud)
┌──────────┐    push   ┌──────────┐
│  Local    │ ────────→│  Remote  │
│  Repo     │ ←────────│  Repo    │
│  (.git/)  │   pull   │          │
└──────────┘           └──────────┘
```

### GitHub adds on top of Git:
- **Pull Requests** — Code review workflow
- **Issues** — Bug and feature tracking
- **Actions** — Automated CI/CD (see Module 10)
- **Pages** — Host documentation sites
- **Releases** — Versioned downloads

---

## Part 12: Exercises

1. **Read history:** Run `git log --oneline -20`. What were the last 20 changes?
2. **Check status:** Run `git status`. Are there uncommitted changes?
3. **Read a diff:** Run `git diff` (if there are changes). What exactly changed?
4. **Find a file's history:** Run `git log --oneline -- Python/structural_lib/codes/is456/flexure.py`. How many times was this file changed?

---

## Part 13: Self-Check

1. **What is a commit?** A snapshot of your code at a point in time with a message.
2. **What is a branch?** A parallel line of development that can be merged later.
3. **What is a Pull Request?** A request to merge a branch into main, with code review.
4. **What does `pre-commit` hook do?** Runs checks automatically before allowing a commit.
5. **Why conventional commits?** Consistent format, auto-changelogs, semantic versioning.
6. **What goes in .gitignore?** Secrets, build outputs, dependencies, OS files, caches.

---

## Key Takeaway

> Git is your **safety net** and **collaboration tool**. Every commit is a savepoint. Every branch is an experiment. Every PR is a quality gate. Learn git well — it's the most universally useful tool in software development.

**Next:** [Module 10 — CI/CD](10-ci-cd.md) explains how to automate testing, checking, and deploying your code.
