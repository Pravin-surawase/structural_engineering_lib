# Configuration Precedence

**Type:** Architecture
**Audience:** All Agents
**Status:** Active
**Importance:** High
**Created:** 2026-04-02
**Last Updated:** 2026-04-02

---

## 3-Tier Precedence (Highest → Lowest)

| Tier | Location | Scope | Example |
|------|----------|-------|---------|
| **1 — Agent-specific** | `.github/agents/*.agent.md` | Per-agent rules | `backend.agent.md` |
| **2 — File-type scoped** | `.github/instructions/*.instructions.md` | By glob pattern (`applyTo`) | `python-core.instructions.md` |
| **3 — Global** | `.github/copilot-instructions.md` | All conversations | Git rules, architecture |

**Rule:** Higher tiers override lower tiers on conflict.

## How Conflicts Resolve

When two tiers specify contradictory rules, the higher tier wins:

- **Agent > File-type:** If `backend.agent.md` says "use 4 spaces" but `python-core.instructions.md` says "use 2 spaces", the agent file wins (4 spaces).
- **File-type > Global:** If `react.instructions.md` says "Tailwind only" but `copilot-instructions.md` doesn't mention styling, the file-type rule applies in `react_app/` files.
- **Non-conflicting rules merge:** Rules from all tiers apply together when they don't conflict. A global git rule and an agent-specific testing rule both apply simultaneously.

## Additional Context Layers

These provide supplementary rules but do not override the 3-tier hierarchy:

| Layer | Location | Loaded By |
|-------|----------|-----------|
| Claude rules | `.claude/rules/*.md` | Claude only (not Copilot) |
| Cross-agent instructions | `AGENTS.md` | All AI assistants |
| Claude-specific instructions | `CLAUDE.md` | Claude only |

These layers add context (e.g., session workflow, terminal rules) but agent-specific `.agent.md` files always take precedence when there's a conflict.

## File-Type Scoping (`applyTo`)

File-type instructions use `applyTo` glob patterns in YAML frontmatter:

```yaml
---
applyTo: "**/structural_lib/**"
---
```

| Instructions File | Glob Pattern | Applies To |
|-------------------|-------------|------------|
| `python-core.instructions.md` | `**/structural_lib/**` | Python core library |
| `fastapi.instructions.md` | `**/fastapi_app/**` | FastAPI backend |
| `react.instructions.md` | `**/react_app/**` | React frontend |
| `docs.instructions.md` | `**/docs/**`, `**/*.md` | Documentation |
| `terminal-rules.instructions.md` | `**` | Everything (terminal rules) |

## Agent-Specific Overrides

Each of the 16 agents in `.github/agents/` has its own `.agent.md` that can:

- Restrict available tools (e.g., `reviewer` is read-only)
- Set permission levels (`ReadOnly`, `WorkspaceWrite`, `DangerFullAccess`)
- Define handoff chains to other agents
- Specify which skills are available

## Validation

Run `scripts/config_precedence.py` to check for:

- Conflicting rules across tiers
- Missing `applyTo` patterns
- Orphaned instruction files not referenced by any agent

```bash
.venv/bin/python scripts/config_precedence.py
```

## Quick Reference

```
Agent .agent.md          ← WINS on conflict (per-agent overrides)
  ↓ falls through to
File-type .instructions.md  ← Scoped by glob (applyTo)
  ↓ falls through to
Global copilot-instructions.md  ← Baseline for all conversations
  +
Context layers (AGENTS.md, .claude/rules/) ← Additive, never override
```
