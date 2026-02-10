# First Message for New Agents

> **Copy-paste this exact message to any new agent starting work on this project.**

---

## The Message

```
Hi! You're working on structural_engineering_lib — an open-source IS 456 RC beam design library.
Stack: React 19 + FastAPI + Python core library.

FIRST: Read docs/getting-started/agent-bootstrap.md — this is your single onboarding doc.

THEN: Check docs/TASKS.md for current work priorities.

CRITICAL RULE: Always use ./scripts/ai_commit.sh "message" for commits (never manual git).

What would you like me to work on?
```

---

## Why This Works

1. **Single entry point** — `agent-bootstrap.md` contains everything (architecture, hooks, endpoints, rules)
2. **No confusion** — One document instead of 6 competing "read me first" files
3. **Progressive** — Bootstrap links to detailed references only when needed
4. **Safety** — THE ONE RULE (ai_commit.sh) prevents 90% of errors

---

## For Different AI Tools

| AI Tool | Auto-loads | Needs manual bootstrap? |
|---------|-----------|------------------------|
| **Claude Code** | `CLAUDE.md` (repo root) | No — already links to bootstrap |
| **GitHub Copilot** | `.github/copilot-instructions.md` | No — already links to bootstrap |
| **Cursor** | `.cursorrules` (if exists) | Yes — paste the message above |
| **Other** | Nothing | Yes — paste the message above |

---

**Version:** v2.0 (2026-02-09)
