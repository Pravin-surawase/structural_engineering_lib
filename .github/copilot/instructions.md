# GitHub Copilot Agent Instructions

> **⚠️ REDIRECT:** This file has been consolidated.
>
> **Canonical location:** [copilot-instructions.md](../copilot-instructions.md)
>
> All agent instructions (900+ lines) are now in the main file.
> This stub exists only for backward compatibility with tools that look here.

---

**Full instructions:** See [.github/copilot-instructions.md](../copilot-instructions.md)

## Critical Commands (Quick Reference Only)

```bash
# Session start
./scripts/agent_start.sh --quick

# Commits (ALWAYS use automation)
./scripts/ai_commit.sh "commit message"

# Git pager prevention
git --no-pager status
git log --oneline -n 10
```

---

*Last updated: 2026-01-11 | See canonical file for all rules*
