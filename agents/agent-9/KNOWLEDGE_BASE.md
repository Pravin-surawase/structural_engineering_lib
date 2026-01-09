# Agent 9: Git & CI Governance Knowledge Base

**Purpose:** Git/CI best practices, troubleshooting guides, and research citations
**Source:** Extracted from `docs/_internal/git-governance.md` + sustainability research
**Last Updated:** 2026-01-10

---

## Table of Contents

1. [Git Workflow Best Practices](#git-workflow-best-practices)
2. [Pre-Commit Hooks & CI](#pre-commit-hooks--ci)
3. [Troubleshooting Common Git Issues](#troubleshooting-common-git-issues)
4. [Branch Management](#branch-management)
5. [Emergency Recovery Procedures](#emergency-recovery-procedures)
6. [Research Citations](#research-citations)

---

## Git Workflow Best Practices

### Core Principles

1. **Clean History** - Linear, readable commit history
2. **Traceability** - Every change links to a Task or Issue
3. **Stability** - Main branch is always deployable
4. **Efficiency** - Use automation to prevent errors

### Recommended Workflow

**For Docs-Only Changes (Any Size):**
```bash
# Direct commit to main (fastest)
./scripts/ai_commit.sh "docs: update guide"
# CI runs automatically
```

**For All Other Changes:**
```bash
# PR workflow (default)
./scripts/create_task_pr.sh TASK-XXX "description"
# Make changes
./scripts/ai_commit.sh "feat: implement X"
./scripts/finish_task_pr.sh TASK-XXX "description"
```

### Commit Message Convention

Follow **Conventional Commits**:
- `feat:` - New feature (MINOR version bump)
- `fix:` - Bug fix (PATCH version bump)
- `docs:` - Documentation only
- `style:` - Formatting, no code change
- `refactor:` - Code change, no bug fix or feature
- `test:` - Adding/fixing tests
- `chore:` - Build, tools, library upgrades

**Examples:**
```
feat(core): implement doubly reinforced beam logic
fix(shear): correct tau_c interpolation for M40
docs(readme): update installation instructions
test(integration): add regression snapshot for B1
```

---

## Pre-Commit Hooks & CI

### Pre-Commit Hooks Setup

```bash
# One-time installation
pre-commit install
```

**Installed Hooks:**
- `black` - Python formatting
- `ruff` - Python linting
- `trailing-whitespace` - Remove trailing spaces
- `end-of-file-fixer` - Ensure files end with newline
- `mixed-line-ending` - Normalize line endings

### Hook Workflow

**Normal Case:**
```bash
git add file.py
git commit -m "feat: add function"
# Hooks run automatically
# If changes made: Files modified by hooks
git add file.py  # Re-stage modified files
git commit --amend --no-edit  # Amend commit
```

**If Hooks Fail:**
```bash
# Read error message carefully
# Fix the issue
git add fixed-file.py
git commit -m "feat: add function"
```

### CI/CD Workflows

**Fast Checks (PRs):**
- Lint (ruff)
- Type check (mypy)
- Contract tests
- Core tests only
- **Duration:** ~2-3 minutes

**Full Tests (Post-Merge):**
- Complete test matrix
- Multiple Python versions
- All test suites
- **Duration:** ~10-15 minutes

**CodeQL Security:**
- Runs on every push
- Not required for merge (informational only)

### Waiting for CI

```bash
# After creating PR
gh pr create --title "..." --body "..."

# WAIT for CI (don't merge immediately!)
gh pr checks <PR_NUMBER> --watch

# Only after all checks pass
gh pr merge <PR_NUMBER> --squash --delete-branch
```

---

## Troubleshooting Common Git Issues

### Issue 1: Push Rejected (Non-Fast-Forward)

**Symptom:**
```
! [rejected] main -> main (non-fast-forward)
```

**Cause:** Remote has commits you don't have locally

**Solution:**
```bash
# Pull and rebase
git pull --rebase origin main
git push

# Alternative: fetch and reset
git fetch origin
git rebase origin/main
git push
```

**Prevention:** Always pull before pushing

---

### Issue 2: CI Fails on Formatting

**Symptom:** PR shows "Format check failed"

**Cause:** Local formatting not applied

**Solution:**
```bash
# Run formatters locally
.venv/bin/python -m black Python/
.venv/bin/python -m ruff check --fix Python/

# Commit fixes
git add -A
git commit -m "style: apply black/ruff formatting"
git push
```

**Prevention:** Use pre-commit hooks

---

### Issue 3: MyPy Type Errors

**Symptom:**
```
error: Item "None" of "Optional[CostBreakdown]" has no attribute "total_cost"
```

**Cause:** Accessing attributes on `Optional[T]` without None check

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

**Prevention:** Run `python -m mypy <file>` locally before committing

---

### Issue 4: Pre-Commit Modified Files

**Symptom:** "Files modified after staging"

**Cause:** Hooks fixed formatting/whitespace automatically

**Solution:**
```bash
# Re-stage modified files and amend commit
git add -A
git commit --amend --no-edit

# OR create new commit
git add -A
git commit -m "chore: apply pre-commit fixes"
```

**Note:** This is NORMAL - hooks are doing their job!

---

### Issue 5: Merge Conflicts

**Symptom:** Git reports conflicts during pull/merge

**Solution:**
```bash
# View conflicted files
git status

# For each file:
# - Open in editor
# - Find conflict markers: <<<<<<< ======= >>>>>>>
# - Manually resolve conflicts
# - Remove conflict markers

# After fixing:
git add <fixed-files>

# If rebasing:
git rebase --continue

# If merging:
git commit --no-edit

# Push resolved changes
git push
```

**Alternative (Ours Strategy):**
```bash
# Keep our version (use with caution!)
git checkout --ours <file>
git add <file>
git commit --no-edit
```

---

## Branch Management

### Branch Protection Rules

**Main Branch Protection:**
- ✅ Required status checks must pass
- ✅ Force pushes disabled
- ✅ Branch deletion disabled
- ✅ PR-first for code/CI/deps
- ✅ Direct commits allowed for docs only

### Branch Naming Convention

- `feat/task-XXX-description` - Feature branches
- `fix/task-XXX-description` - Bug fix branches
- `docs/task-XXX-description` - Documentation branches
- `refactor/task-XXX-description` - Refactoring branches

**Examples:**
```
feat/task-017-etabs-import
fix/task-012-shear-bug
docs/task-025-api-reference
```

### Branch Cleanup

```bash
# Delete local merged branches
git branch --merged | grep -v "\*\|main" | xargs -n 1 git branch -d

# Delete remote merged branches
gh pr list --state merged --limit 20 --json headRefName | \
  jq -r '.[].headRefName' | \
  xargs -I {} git push origin --delete {}

# Prune remote references
git remote prune origin
git fetch --prune
```

### Worktree Management

**Create Worktree:**
```bash
git worktree add ../worktree-agent-6 -b feat/ui-feature
```

**List Worktrees:**
```bash
git worktree list
```

**Remove Worktree:**
```bash
git worktree remove ../worktree-agent-6
```

**Prune Stale Worktrees:**
```bash
git worktree prune
```

---

## Emergency Recovery Procedures

### Scenario 1: Main Branch Broken

**Detection:**
- CI fails on main
- Tests fail
- Application won't run

**Immediate Action:**
```bash
# Option A: Revert last commit
git revert HEAD
git push

# Option B: Revert to specific commit
git revert <bad-commit-hash>
git push
```

**Follow-Up:**
1. Create fix branch
2. Repair issue
3. Test thoroughly
4. Open PR
5. Merge when CI passes

---

### Scenario 2: Accidental Force Push

**Detection:** History rewritten, commits lost

**Recovery:**
```bash
# Find lost commit in reflog
git reflog

# Reset to lost commit
git reset --hard <lost-commit-hash>

# Force push (only if you're sure!)
git push --force-with-lease
```

**Prevention:** Branch protection prevents force push

---

### Scenario 3: Corrupted Git State

**Symptoms:**
- Weird errors
- Commands failing unexpectedly
- Merge states stuck

**Recovery:**
```bash
# Check for unfinished merges
ls .git/MERGE_*

# If unfinished merge exists:
git commit --no-edit  # Complete merge
# OR
git merge --abort     # Abort merge

# Check for unfinished rebases
ls .git/rebase-*

# If unfinished rebase:
git rebase --continue  # Complete rebase
# OR
git rebase --abort     # Abort rebase

# Nuclear option (last resort):
git reset --hard origin/main
```

---

### Scenario 4: Lost Work

**Detection:** Work disappeared after git operation

**Recovery:**
```bash
# Check reflog for lost commits
git reflog

# Find your work (look for commit messages)
git show <commit-hash>

# Recover work
git cherry-pick <commit-hash>

# OR create new branch from lost commit
git checkout -b recovery-branch <commit-hash>
```

---

## Research Citations

### Citation 1: AI Agents Amplify Discipline

**Source:** Intuition Labs - AI Code Assistants for Large Codebases

> "Agentic AI is an amplifier of existing technical and organizational disciplines, not a substitute for them. Organizations with strong foundations can channel agent-driven velocity into predictable productivity gains. Without foundations, they generate chaos quicker."

**Application:**
Strong git workflows (pre-commit hooks, CI/CD, branch protection) are the foundation that allows AI agents to move quickly without breaking things. Agent 9 ensures these foundations remain strong.

---

### Citation 2: 80/20 Technical Debt Rule

**Source:** Statsig - Managing Tech Debt in Fast-Paced Environments

> "Shopify dedicates 25% of its development cycles to addressing technical debt by implementing 'debt sprints' within its agile workflow."

**Application:**
Agent 9's 80/20 rule (20% governance time) is inspired by Shopify's 25% debt cycles, adapted for solo development. This prevents organizational and technical debt accumulation.

---

### Citation 3: Context Management

**Source:** Addy Osmani - AI Coding Workflow 2026

> "LLMs are only as good as the context you provide - show them the relevant code, docs, and constraints. Feed the AI all the information it needs."

**Application:**
Clean git history, organized documentation, and proper commit messages provide the context that makes AI agents effective. Agent 9 maintains this clean context through archival and governance.

---

### Citation 4: Sustainable Pacing

**Source:** Faros AI - Best AI Coding Agents for 2026

> "AI agents are powerful productivity amplifiers for solo developers managing large codebases, but they require proper setup, disciplined workflows, and strong foundational practices to be truly effective."

**Application:**
WIP limits and release cadence provide the disciplined workflows needed to sustain 50-75 commits/day (down from unsustainable 122/day). Velocity channeled sustainably.

---

### Citation 5: Small Iterations

**Source:** Axon - Best Practices for Managing Technical Debt Effectively

> "Work in small iterations. Avoid huge leaps. By iterating in small loops, we greatly reduce the chance of catastrophic errors and we can course-correct quickly."

**Application:**
Weekly governance sessions (small iterations) prevent large cleanup bursts. Monthly reviews allow course correction. Bi-weekly releases provide frequent feedback loops.

---

### Citation 6: WIP Limits

**Source:** Kanban Methodology (implicit in multiple sources)

> "Limiting work in progress reduces context switching, forces completion before starting new work, and makes bottlenecks visible."

**Application:**
Agent 9's WIP limits (2 worktrees, 5 PRs, 10 docs, 3 research) prevent context fragmentation and force completion. Makes sustainability issues visible early.

---

## Best Practices Summary

### ✅ DO

**Git Operations:**
- Use automation scripts (`ai_commit.sh`, etc.)
- Wait for CI before merging PRs
- Pull before push (especially after merging PRs)
- Use feature branches for significant changes
- Amend commits when pre-commit modifies files (if not yet pushed)
- Check git status before committing

**Commit Hygiene:**
- Use conventional commits (`feat:`, `fix:`, `docs:`)
- Link PRs to tasks (mention TASK-XXX)
- Batch related changes into one commit
- Write descriptive commit messages

**CI/CD:**
- Use pre-commit hooks (install once, saves time)
- Run tests locally before pushing
- Check formatting locally: `black Python/ && ruff check Python/`
- Fix CI failures immediately or revert

---

### ❌ DON'T

**Git Operations:**
- Don't merge immediately after creating PR (wait for CI)
- Don't push to PR branch without pulling first
- Don't force-push to main (branch protection prevents this)
- Don't skip pre-commit hooks (they catch issues early)
- Don't commit generated files (use .gitignore)

**CI/CD:**
- Don't ignore CI failures (fix or revert)
- Don't bypass quality gates (they exist for good reason)
- Don't push unformatted code (use pre-commit hooks)
- Don't mix unrelated changes (keep commits focused)

---

## Quick Reference Commands

### Daily Operations
```bash
# Start work
git pull --ff-only

# Commit changes
./scripts/ai_commit.sh "type: description"

# Create PR
./scripts/create_task_pr.sh TASK-XXX "description"

# Wait for CI
gh pr checks <PR_NUM> --watch

# Merge PR
gh pr merge <PR_NUM> --squash --delete-branch

# Sync after merge
git pull --ff-only
```

### Health Checks
```bash
# Check WIP limits
./scripts/check_wip_limits.sh

# Check version consistency
./scripts/check_version_consistency.sh

# Check git state
git status
git worktree list
gh pr list --state open
```

### Cleanup
```bash
# Archive old docs
./scripts/archive_old_sessions.sh

# Clean worktrees
git worktree prune

# Clean branches
git remote prune origin
git fetch --prune
```

### Emergency
```bash
# Check for stuck states
ls .git/MERGE_* .git/rebase-*

# Recovery script
./scripts/recover_git_state.sh

# Revert bad commit
git revert HEAD

# Find lost work
git reflog
```

---

## Related Documentation

- **[README.md](README.md)** - Main specification
- **[WORKFLOWS.md](WORKFLOWS.md)** - Operational procedures
- **[CHECKLISTS.md](CHECKLISTS.md)** - Ready-to-use checklists
- **[docs/_internal/git-governance.md](../../docs/_internal/git-governance.md)** - Complete git governance guide

---

**Last Updated:** 2026-01-10 | **Version:** 1.0.0
