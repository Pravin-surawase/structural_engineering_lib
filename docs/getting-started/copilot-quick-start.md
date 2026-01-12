# GitHub Copilot Agent Quick Start

> **⚠️ CONSOLIDATED:** This document has been simplified.
>
> **Use instead:** `./scripts/agent_start.sh` (handles everything in one command)
>
> For detailed instructions: See [copilot-instructions.md](../../.github/copilot-instructions.md)

---

## 🚀 Quick Start (One Command)

```bash
# This does everything: git config, env setup, pre-flight, session start
./scripts/agent_start.sh --quick

# With agent-specific guidance:
./scripts/agent_start.sh --agent 9 --quick   # Governance focus
./scripts/agent_start.sh --agent 8 --quick   # Git/automation focus
./scripts/agent_start.sh --agent 6 --quick   # UI focus
```

---

## Git Pager Prevention (Handled by agent_start.sh)

If you're NOT using the unified script, run manually:

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

> **⚠️ USE AUTOMATION INSTEAD OF MANUAL GIT:**
>
> The commands below show the manual process for educational purposes only.
> **Always use `./scripts/ai_commit.sh "message"` for commits.**

### Safe Commit and Push (USE ai_commit.sh INSTEAD)

```bash
# ✅ PREFERRED (one command does everything):
./scripts/ai_commit.sh "feat: implement feature"

# ❌ Manual process (shown for education only - DO NOT USE):
# git status --short
# git add .
# git commit -m "feat: implement feature"
# git pull --ff-only
# git push origin $(git rev-parse --abbrev-ref HEAD)
```

### Safe Merge/Rebase (USE recover_git_state.sh INSTEAD)

```bash
# ✅ PREFERRED (handles all recovery automatically):
./scripts/recover_git_state.sh

# ❌ Manual process (shown for education only - DO NOT USE):
# git merge --abort
# git pull --rebase origin main
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
3. Then run: `./scripts/agent_start.sh --quick` (handles all git pager config)
4. Continue with safe commands

---

## Session Checklist

At the start of every Copilot session:

- [ ] Run `./scripts/agent_start.sh --quick` (handles everything automatically)
- [ ] Verify with `git status --short` (should work without paging)
- [ ] Check current branch: `git rev-parse --abbrev-ref HEAD`
- [ ] Check for uncommitted changes: `git diff --name-only`
- [ ] Check merge state: `test -f .git/MERGE_HEAD && echo "Merge in progress" || echo "Clean"`

<details>
<summary>🔧 Fallback: Manual pager config (if agent_start.sh unavailable)</summary>

```bash
source scripts/copilot_setup.sh
```

</details>

---

## Useful Aliases (Created by Setup Script)

After running `./scripts/agent_start.sh`, you can use:

```bash
git st      # Same as: git status --short
git lg      # Same as: git log --oneline -n 20
git df      # Same as: git diff --stat
git br      # Same as: git branch --list
```

---

## Additional Resources

- **Full pitfalls guide:** [agent-automation-pitfalls.md](../reference/agent-automation-pitfalls.md)
- **Agent 8 automation:** [agent-8-automation.md](../agents/guides/agent-8-automation.md) (quick start + script index)
- **Agent 8 protocol:** [agent-8-git-ops.md](../agents/guides/agent-8-git-ops.md)
- **Copilot instructions:** [copilot-instructions.md](../../.github/copilot-instructions.md)

---

**Last Updated:** 2026-01-10
