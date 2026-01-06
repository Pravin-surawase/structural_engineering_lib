# Git Workflow for AI Agents (Canonical)

**Purpose:** Single source of truth for safe Git usage.

---

## One Rule
**Never use manual git commit/push.** Always use the workflow scripts.

---

## Decision Path

### 1) Should this be a PR?
Run:
```bash
./scripts/should_use_pr.sh --explain
```
- If it recommends a PR, use the PR workflow below.
- If it recommends direct commit, use the direct workflow below.

### 2) Direct Commit (Docs-only or very small changes)
```bash
./scripts/ai_commit.sh "docs: update guide"
```
This script stages changes, enforces PR rules, and delegates to safe_push.sh.

### 3) PR Workflow (Code/CI/Dependencies)
```bash
./scripts/create_task_pr.sh TASK-XXX "short description"
# make changes
./scripts/ai_commit.sh "feat: implement X"
./scripts/finish_task_pr.sh TASK-XXX "short description"
```
Note: Reviews are not required in this repo. If reviews are enabled later, PR authors cannot self-approve.

---

## What safe_push.sh Does (Important)
- Syncs with the latest `main` before commit.
- On `main`: uses `git pull --ff-only` (no merge commits).
- On feature branches: rebases on `origin/main` before first push, otherwise merges `origin/main` (avoids force pushes).
- Handles pre-commit changes and amends automatically.

---

## Recovery (When Git Is Broken)
Run:
```bash
./scripts/recover_git_state.sh
```
It prints the exact recovery command for your current state.

---

## Formatting Policy
- **Local:** pre-commit hooks run `black` and `ruff`.
- **CI:** format checks only (no auto-commits on PRs).
- Fix formatting locally before pushing.

---

## FAQ

**Q: Can I commit directly on main?**
A: Only for very small docs-only changes. Otherwise use PR.

**Q: Do I need to `git add` manually?**
A: No. `ai_commit.sh` and `safe_push.sh` stage changes for you.

**Q: How do I choose PR vs direct?**
A: Use `./scripts/should_use_pr.sh --explain`.

**Q: Why can’t I approve my own PR (if reviews are enabled)?**
A: GitHub blocks self-approval. Request another reviewer, or use an admin merge override when allowed.

---

**Related:**
- `scripts/safe_push.sh`
- `scripts/ai_commit.sh`
- `scripts/recover_git_state.sh`
- `scripts/should_use_pr.sh`
- `scripts/create_task_pr.sh`
- `scripts/finish_task_pr.sh`
