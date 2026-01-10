# GitHub Copilot Agent Quick Start

**IMPORTANT:** Copilot runs in its own shell environment, not VSCode terminal. You must configure git for each session.

---

## ⚠️ CRITICAL: Run This First (Every Session)

```bash
# Option 1: Source the setup script (RECOMMENDED)
source scripts/copilot_setup.sh

# Option 2: Manual setup
git config --global core.pager cat
git config --global pager.status false
git config --global pager.branch false
git config --global pager.diff false
export GIT_EDITOR=":"
export PAGER=cat
```

**Why?** Without this, git commands will open a pager and **lock your terminal**.

---

## Safe Git Commands Reference

### Always Use These Formats:

```bash
# Status
git status --short              # ✅ Safe
git status --porcelain          # ✅ Safe
git --no-pager status           # ✅ Safe
git status                      # ❌ DANGEROUS - May lock terminal

# Log
git log --oneline -n 20         # ✅ Safe
git --no-pager log              # ✅ Safe
git log                         # ❌ DANGEROUS - Will lock terminal

# Diff
git diff --stat                 # ✅ Safe
git diff --name-only            # ✅ Safe
git --no-pager diff             # ✅ Safe
git diff                        # ❌ DANGEROUS - May lock terminal

# Branch
git branch --list               # ✅ Safe
git --no-pager branch -a        # ✅ Safe
git branch -a                   # ❌ DANGEROUS - May lock terminal
```

---

## Quick Commands

```bash
# Check status
git status --short

# View recent commits
git log --oneline -n 10

# See what changed
git diff --name-only

# Current branch
git rev-parse --abbrev-ref HEAD

# Pull and push safely
git pull --ff-only
git push origin $(git rev-parse --abbrev-ref HEAD)

# Commit with inline message (NEVER without -m)
git commit -m "feat: your message"
git commit --amend --no-edit
```

---

## Common Workflows

### Safe Commit and Push

```bash
# 1. Check status
git status --short

# 2. Add files
git add .

# 3. Commit with message
git commit -m "feat: implement feature"

# 4. Pull before push
git pull --ff-only

# 5. Push
git push origin $(git rev-parse --abbrev-ref HEAD)
```

### Safe Merge/Rebase

```bash
# Check if merge in progress
test -f .git/MERGE_HEAD && echo "Merge in progress" || echo "No merge"

# Abort merge if stuck
git merge --abort

# Pull with rebase
git pull --rebase origin main
```

---

## What NOT to Do

### ❌ Commands That Lock Terminal:

```bash
git log                    # Opens pager
git diff                   # Opens pager
git status                 # Opens pager if long output
git branch -a              # Opens pager if many branches
git show [commit]          # Opens pager
git blame [file]           # Opens pager on large files
```

### ❌ Interactive Commands:

```bash
git commit                 # Opens editor (use -m flag)
git rebase -i              # Opens editor (use non-interactive)
git clean -i               # Prompts for input (use -fd)
rm -i [file]              # Prompts for input (use -f)
```

---

## If Terminal Gets Stuck

**Symptoms:**
```
> git status
The command opened the alternate buffer.

[All commands now blocked]
```

**Recovery:**
1. User must press `q` in the terminal to quit pager
2. Or press `Ctrl+C` to force quit
3. Then run: `source scripts/copilot_setup.sh`
4. Continue with safe commands

---

## Session Checklist

At the start of every Copilot session:

- [ ] Run `source scripts/copilot_setup.sh`
- [ ] Verify with `git status --short` (should work without paging)
- [ ] Check current branch: `git rev-parse --abbrev-ref HEAD`
- [ ] Check for uncommitted changes: `git diff --name-only`
- [ ] Check merge state: `test -f .git/MERGE_HEAD && echo "Merge in progress" || echo "Clean"`

---

## Useful Aliases (Created by Setup Script)

After running `scripts/copilot_setup.sh`, you can use:

```bash
git st      # Same as: git status --short
git lg      # Same as: git log --oneline -n 20
git df      # Same as: git diff --stat
git br      # Same as: git branch --list
```

---

## Additional Resources

- **Full pitfalls guide:** [agent-automation-pitfalls.md](../reference/agent-automation-pitfalls.md)
- **Agent 8 quick start:** [agent-8-quick-start.md](../agents/guides/agent-8-quick-start.md)
- **Agent 8 protocol:** [agent-8-git-ops.md](../agents/guides/agent-8-git-ops.md)
- **Agent 8 automation:** [agent-8-automation.md](../agents/guides/agent-8-automation.md)
- **Copilot instructions:** [copilot-instructions.md](../../.github/copilot-instructions.md)

---

**Last Updated:** 2026-01-10
