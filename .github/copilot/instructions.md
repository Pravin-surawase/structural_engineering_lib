# GitHub Copilot Agent Instructions

## CRITICAL: Git Pager Prevention

**IMPORTANT:** Always use `--no-pager` or short-format flags to prevent terminal lockup.

### Required for ALL Git Commands

```bash
# ✅ CORRECT - Safe for Copilot Agent
git --no-pager status
git status --short
git status --porcelain
git --no-pager log --oneline -n 20
git --no-pager diff --stat
git --no-pager branch -a

# ❌ WRONG - Will lock terminal
git status       # Opens pager if output long
git log          # Always opens pager
git diff         # Opens pager on changes
git branch -a    # Opens pager if many branches
```

### Commands to ALWAYS Use

Replace bare git commands with these:

| Instead of | Use |
|------------|-----|
| `git status` | `git status --short` or `git --no-pager status` |
| `git log` | `git log --oneline -n 20` or `git --no-pager log` |
| `git diff` | `git diff --stat` or `git --no-pager diff` |
| `git branch -a` | `git --no-pager branch -a` |
| `git show` | `git --no-pager show` |

### Session Start Checklist

At the start of EVERY session, run:

```bash
# Verify git pager is disabled
git config core.pager

# If not "cat", fix it:
git config --global core.pager cat
git config --global pager.status false
git config --global pager.branch false
git config --global pager.diff false
```

### If Terminal Gets Stuck

If you see "The command opened the alternate buffer", you're stuck in a pager. Recovery requires manual intervention:

1. User must press `q` in the terminal
2. Or press `Ctrl+C` to force quit
3. Then re-run with `--no-pager` flag

### Common Safe Patterns

```bash
# Check git status
git status --short

# View recent commits
git log --oneline -n 10

# See what changed
git diff --name-only
git diff --stat

# View current branch
git rev-parse --abbrev-ref HEAD

# Check for uncommitted changes
git diff-index --quiet HEAD -- || echo "Uncommitted changes"

# Get remote status
git fetch --dry-run

# List branches
git branch --list
```

## Other Terminal Best Practices

### Avoid Interactive Commands

```bash
# ❌ WRONG - Prompts for input
rm -i file.txt
git clean -i
git rebase -i HEAD~5

# ✅ CORRECT - Non-interactive
rm -f file.txt
git clean -fd
git rebase HEAD~5  # With GIT_EDITOR=:
```

### Always Provide Commit Messages Inline

```bash
# ❌ WRONG - Opens editor
git commit

# ✅ CORRECT - Inline message
git commit -m "message"
git commit --amend --no-edit
```

### Use Short Output Formats

```bash
# Prefer machine-readable formats
git status --porcelain   # vs git status
git branch --list        # vs git branch
ls -1                    # vs ls (one file per line)
```

## References

- [Agent Automation Pitfalls](../../docs/reference/agent-automation-pitfalls.md)
- [Agent 8 Quick Start](../../docs/agents/guides/agent-8-quick-start.md)
- [Agent 8 Git Operations Protocol](../../docs/agents/guides/agent-8-git-ops.md)
- [Agent 8 Automation Index](../../docs/agents/guides/agent-8-automation.md)
- [Agent 8 Mistakes Prevention](../../docs/agents/guides/agent-8-mistakes-prevention-guide.md)
