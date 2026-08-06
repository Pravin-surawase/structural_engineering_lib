# Day 22: Git Automation — Why Every Commit Goes Through ONE Script

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-08
**Last Updated:** 2026-04-08
**Prerequisites:** Day 12 (Testing Patterns), Day 16 (FastAPI Advanced)
**Library files:** `scripts/ai_commit.sh`, `scripts/should_use_pr.sh`, `scripts/hooks/pre_commit.py`, `scripts/hooks/post_commit.py`
**Related scripts:** `scripts/safe_file_move.py`, `scripts/safe_file_delete.py`, `scripts/finish_task_pr.sh`, `scripts/create_task_pr.sh`

---

## What You'll Learn Today

By the end of this module you'll understand:
- Why every commit goes through ONE script — and what happens if you don't
- How `ai_commit.sh` validates, stages, commits, and pushes in a single command
- Conventional commit message format and why consistency matters
- Every flag available: `--preview`, `--undo`, `--finish`, `--branch`, and more
- How git hooks catch mistakes before they reach the repository
- The PR workflow: when you need one, how to create and finish it
- Safe file operations that preserve 870+ internal documentation links

---

## Part 1: The ONE RULE

This project has one non-negotiable rule for version control:

```bash
./scripts/ai_commit.sh "type: message"    # ALWAYS use this
```

**Never** run manual `git add`, `git commit`, or `git push`. Not even once.

Why? Because this single script does **seven things** that manual git doesn't:

| Step | What `ai_commit.sh` does | What manual git misses |
|------|--------------------------|------------------------|
| 1 | Validates commit message format | You might type `"fixed stuff"` |
| 2 | Runs pre-commit hooks (lint, types, imports) | No checks — broken code ships |
| 3 | Checks if a PR is required | Direct push to `main` bypasses review |
| 4 | Stages all changes (`git add -A`) | You might forget unstaged files |
| 5 | Commits with verified message | — |
| 6 | Handles `git pull --rebase` automatically | Merge conflicts from stale branch |
| 7 | Pushes via `safe_push.sh` (with retries) | Push errors leave work stranded |

Historical context: manual git commands have caused **10+ hours of rework** in this project. Merge conflicts, force-pushed branches, bypassed hooks — every one of these incidents led to a new safeguard in the script.

---

## Part 2: Conventional Commit Format

Every commit message follows a strict format:

```
type(scope): description
```

The subject line must be ≤72 characters, no period at the end.

| Type | When to Use | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: add column interaction curve` |
| `fix` | Bug fix | `fix: correct shear capacity formula` |
| `docs` | Documentation only | `docs: update Day 22 learning module` |
| `refactor` | Code restructuring (no behavior change) | `refactor: extract helper from beam_pipeline` |
| `test` | Adding or fixing tests | `test: add biaxial bending tests` |
| `chore` | Maintenance | `chore: bump version to 0.22.0` |
| `ci` | CI/CD changes | `ci: add Docker build workflow` |

The optional `(scope)` narrows down where:
```bash
feat(column): add helical reinforcement check     # Python core
fix(api): correct parameter name in design_beam    # FastAPI
docs(learning): add Day 22 module                  # Documentation
```

The pre-commit hook **enforces** this format:
```python
# scripts/hooks/pre_commit.py
pattern = r"^(feat|fix|docs|refactor|test|chore|ci|perf|style|build)(\(.+\))?: .+"
if not re.match(pattern, message):
    return False, f"WARN: Commit message doesn't match conventional format"
```

---

## Part 3: The Flags

| Flag | Purpose | Example |
|------|---------|---------|
| *(none)* | Standard commit + push | `ai_commit.sh "docs: update README"` |
| `--preview` | Show diff without committing | `ai_commit.sh "msg" --preview` |
| `--dry-run` | Full workflow preview | `ai_commit.sh "msg" --dry-run` |
| `--status` | Branch, files, stashes, PRs | `ai_commit.sh --status` |
| `--undo` | Soft-reset last commit | `ai_commit.sh --undo` |
| `--amend` | Add changes to previous commit | `ai_commit.sh --amend` |
| `--push` | Push without new commit | `ai_commit.sh --push` |
| `--pr-check` | Check if PR is required | `ai_commit.sh --pr-check` |
| `--branch` | Create task branch + PR | `ai_commit.sh --branch TASK-042 "desc"` |
| `--finish` | CI poll → merge → cleanup | `ai_commit.sh --finish "desc"` |
| `--signoff` | DCO sign-off | `ai_commit.sh "msg" --signoff` |

---

## Part 4: Git Hooks Framework

Hooks are scripts that run automatically at specific points in the git workflow:

```
scripts/hooks/
├── __init__.py      # HookRunner — discovers and runs hooks
├── __main__.py      # CLI entry point
├── pre_commit.py    # Runs BEFORE commit (can block it)
├── post_commit.py   # Runs AFTER commit (informational only)
└── pre_route.py     # Runs BEFORE task routing
```

**Pre-commit hooks (gatekeepers):**

| Priority | Hook | Action |
|:---:|------|--------|
| 10 | `check_no_force_flags` | Blocks if `--force` or `--no-verify` detected |
| 20 | `check_commit_message_format` | Blocks if message doesn't match format |
| 30 | `check_no_stub_edits` | Blocks if editing `api.py` stub instead of `services/api.py` |

**Post-commit hooks (reporters):**

| Priority | Hook | Action |
|:---:|------|--------|
| 50 | `log_commit_to_costs` | Logs commit to cost tracking |
| 60 | `update_test_stats` | Reminds to update `test_stats.json` if tests changed |

---

## Part 5: PR Workflow

Not every change can go directly to `main`. Production code requires a Pull Request.

**When is a PR required?**

| Change Type | PR Required? | Why |
|-------------|:---:|------|
| `Python/structural_lib/` | **Yes** | Production math — needs review |
| `fastapi_app/routers/` | **Yes** | API changes affect all consumers |
| `react_app/src/` | **Yes** | Frontend needs build verification |
| `docs/*.md` | No | Documentation is low-risk |
| `scripts/` (minor) | No | Small script tweaks |
| CI/Docker configs | **Yes** | Infrastructure affects everyone |

**The full PR lifecycle:**
```bash
./scripts/ai_commit.sh --status                        # 1. Check state
./scripts/ai_commit.sh --branch TASK-042 "add column"  # 2. Create branch + PR
./scripts/ai_commit.sh "feat(column): add capacity"    # 3. Commit work
./scripts/ai_commit.sh "test(column): add tests"       # 4. More commits
./scripts/ai_commit.sh --finish "column design done"   # 5. CI → merge → cleanup
```

The `--finish` command:
1. Pushes your branch to remote
2. Creates PR (or reuses existing)
3. Polls CI every 15s until all checks pass
4. Squash-merges when CI is green
5. Switches back to main, pulls, prunes
6. Deletes the task branch (local + remote)

---

## Part 6: Safe File Operations

This project has **870+ internal documentation links**. Moving or deleting a file can break dozens of cross-references.

```bash
# Move a file — updates all references across the repo
.venv/bin/python scripts/safe_file_move.py old/path.md new/path.md --dry-run
.venv/bin/python scripts/safe_file_move.py old/path.md new/path.md

# Delete a file — checks for incoming references first
.venv/bin/python scripts/safe_file_delete.py path/to/file.md
```

**Never use bare `mv` or `rm` on documentation files.** A manual `mv docs/guide.md docs/guides/guide.md` silently breaks every link pointing to the old path.

---

## Part 7: FORBIDDEN Commands

| Command | Why Banned | What Happened |
|---------|-----------|---------------|
| `git add` / `git commit` / `git push` | Bypasses hooks, validation, safe push | 10+ hours of merge conflict rework |
| `--force` / `--no-verify` | Bypasses all safety checks | CI failures within minutes |
| `gh pr merge --admin` | Bypasses required CI checks | Broken code merged to main |
| `git rebase --skip` | Silently drops conflicting commits | Lost work, never recovered |
| `rm file.md` | Breaks documentation links | Dozens of broken links |
| `mv old.md new.md` | Doesn't update references | Same |

Every ban has a story — a real incident that cost real hours to fix.

---

## Part 8: Exercises

### Exercise 1: Check project status
```bash
./scripts/ai_commit.sh --status
# Look for: branch, uncommitted changes, stashes, open PRs
```

### Exercise 2: Preview a commit
Edit any `.md` file, then:
```bash
./scripts/ai_commit.sh "docs: test preview" --preview
# Confirms nothing was committed, shows the diff
```

### Exercise 3: Explore the hooks
```bash
cat scripts/hooks/pre_commit.py    # Three pre-commit checks
cat scripts/hooks/post_commit.py   # Two post-commit reporters
```

---

## Part 9: Self-Check Q&A

1. **Why ban manual `git commit`?** The script runs 7 safety steps (validate, hooks, PR check, stage, commit, pull, push). Manual git skips all of them.
2. **What happens if your message is `"fixed the thing"`?** Pre-commit hook rejects it — doesn't match `type(scope): desc` pattern.
3. **What's `--preview` vs `--dry-run`?** Preview shows the diff; dry-run simulates the full workflow without executing.
4. **When does `should_use_pr.sh` require a PR?** When files in `Python/structural_lib/`, `fastapi_app/`, or `react_app/src/` are changed.
5. **What does `--finish` do?** 6 steps: push → create PR → poll CI → merge → switch to main → delete branch.
6. **Why can't you `mv docs/a.md docs/b.md`?** Breaks 870+ internal links. Use `safe_file_move.py` which updates all references.
7. **A pre-commit hook returns False — what happens?** The commit is blocked. Fix the issue, then try again.
8. **What does priority 10 vs 60 mean in hooks?** Lower number runs first. Priority 10 (force flag check) runs before priority 60 (test stats reminder).
9. **How does `--undo` work?** Soft-resets the last commit — changes go back to working directory, commit is removed.
10. **Why `safe_push.sh` instead of plain `git push`?** It handles retries, checks remote state, and avoids overwriting others' work.

---

## Part 10: Things to Know — Deep Insights

### 10.1: The script does `git add -A` automatically
This means ALL changes are staged — including files you didn't intend to commit. If you have debugging files or scratch notes, they'll be included. Use `--preview` to verify what's being staged before committing.

### 10.2: `--finish` can take 5-20 minutes
The CI polling waits for ALL checks to pass. If a CI check is slow (Docker build, full test suite), the command blocks. This is intentional — it prevents merging with failing CI. Never interrupt it with Ctrl+C.

### 10.3: The stub-edit hook saves hours
Hook priority 30 blocks edits to `Python/structural_lib/api.py` (the backward-compat stub). The real code is in `services/api.py`. Without this hook, developers edit the stub, wonder why nothing changes, and waste hours debugging.

### 10.4: Safe file move does a full regex scan
`safe_file_move.py` scans every `.md` file in the repo for references to the old path. It handles relative paths, anchors, and even partial matches. A manual `mv` would require manually checking 870+ files.

### 10.5: The rebase in `ai_commit.sh` is non-interactive
When the script does `git pull --rebase`, it's automatic. If there are conflicts, it aborts the rebase and tells you to resolve manually. It never silently resolves conflicts — that's how code gets corrupted.

### 10.6: `--amend` is only for unpushed commits
If you amend a pushed commit, you need force-push to update the remote. The script blocks this because force-push is forbidden. Only amend commits that haven't been pushed yet.

---

## Part 11: What Can Be Done Better

### 11.1: No commit message body template
The script validates the subject line but doesn't suggest a body template. For complex changes, a body with "What changed", "Why", and "Testing" sections would improve the commit log.

### 11.2: No automatic changelog generation
Conventional commits enable automated changelog generation (e.g., `standard-version` or `release-please`). Currently, CHANGELOG.md is updated manually. Auto-generation would save time and ensure consistency.

### 11.3: No commit signing (GPG/SSH)
Commits aren't cryptographically signed, so there's no proof they actually came from the claimed author. Adding `--gpg-sign` or SSH signing would verify commit authenticity.

### 11.4: No pre-push hook for test verification
The hooks run before commit, but there's no pre-push hook that runs the full test suite. A failing test can be committed and pushed before CI catches it.

### 11.5: No branch naming enforcement
The `--branch` flag creates branches like `TASK-042`, but there's no validation that the task ID exists in TASKS.md. Typos create orphan branches.

---

## Part 12: Innovation Directions

### 12.1: AI-powered commit message generation
Analyze the diff and auto-suggest a conventional commit message. The developer confirms or edits. Tools like `aicommits` or `commitizen-ai` do this.

### 12.2: Semantic PR size limits
Instead of counting lines, analyze the semantic scope of changes. A 500-line change that adds one new IS 456 clause is focused; a 50-line change touching 10 files is scattered. Block the scattered one.

### 12.3: Automatic PR description from commits
Combine all conventional commit messages on a branch into a structured PR description. `feat` commits become "Features added", `fix` becomes "Bugs fixed", `test` becomes "Tests added".

### 12.4: Git bisect integration
When a test fails, automatically run `git bisect` with the test as the predicate. The script finds the exact commit that introduced the failure — even across hundreds of commits.

### 12.5: Branch-based feature flags
Instead of long-lived feature branches, use trunk-based development with feature flags. Every commit goes to main, but new features are behind flags. CI tests with flag on AND off.

---

## Part 13: Next Repo Must-Add

### Concrete items

1. **Auto-changelog from conventional commits** — `standard-version` or `release-please` integration
2. **Pre-push hook with test suite** — Block push if tests fail locally
3. **Commit signing** — GPG or SSH signatures for commit authenticity
4. **Commit message body template** — Prompt for "What/Why/Testing" on non-trivial changes
5. **Branch name validation** — Verify TASK-XXX exists in TASKS.md
6. **AI commit message suggestion** — Diff analysis → suggested type(scope): description
7. **PR template auto-fill** — Generate PR description from branch commits

### Day-1 checklist for a new automated git workflow

```
□ 1. Wrap all git operations in a single entry-point script
□ 2. Enforce conventional commit format with a pre-commit hook
□ 3. Add git add -A with --preview to verify staging
□ 4. Add pull --rebase before push (abort on conflict, never auto-resolve)
□ 5. Use safe_push.sh with retry logic
□ 6. Check if PR is required based on changed file paths
□ 7. Add --undo for soft-reset of last commit
□ 8. Add --status for quick project state overview
□ 9. Document FORBIDDEN commands with reasons
□ 10. Test the script: commit docs, commit code (PR required), --preview, --undo
```

---

## References

- `scripts/ai_commit.sh` — The ONE RULE script
- `scripts/should_use_pr.sh` — PR decision logic
- `scripts/hooks/pre_commit.py` — Pre-commit hooks
- `scripts/hooks/post_commit.py` — Post-commit hooks
- `scripts/safe_file_move.py` — Safe file move with link updates
- `scripts/safe_file_delete.py` — Safe file delete
- [Conventional Commits](https://www.conventionalcommits.org/) — The format standard
- **Previous:** Day 21 covers Docker containerization
- **Next:** Day 23 covers CI/CD with GitHub Actions
- **Day 23** — CI/CD Pipeline (what happens after you commit)