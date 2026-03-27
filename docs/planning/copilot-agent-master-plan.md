# Copilot Agent Master Plan — structural_engineering_lib

**Type:** Architecture
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Created:** 2026-03-27
**Last Updated:** 2026-03-27

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Audit](#2-current-state-audit)
3. [VS Code Copilot Agent System — How It Works](#3-vs-code-copilot-agent-system--how-it-works)
4. [Agent Roster — 9 Agents We Need](#4-agent-roster--9-agents-we-need)
5. [Agent Implementation Plan](#5-agent-implementation-plan)
6. [Document Maintenance & File Structure Strategy](#6-document-maintenance--file-structure-strategy)
7. [Daily Work Log & Archive System](#7-daily-work-log--archive-system)
8. [Handoff Workflow Between Agents](#8-handoff-workflow-between-agents)
9. [Best Practices, Tips & Mistakes to Avoid](#9-best-practices-tips--mistakes-to-avoid)
10. [Implementation Roadmap](#10-implementation-roadmap)

---

## 1. Executive Summary

This project (IS 456 RC beam design library) has grown to a full-stack app with:
- **Python core** (structural_lib) — 23 public API functions, 4-layer architecture
- **FastAPI backend** — 38 endpoints, 12 routers
- **React 19 frontend** — R3F 3D visualization, Tailwind, 18+ hooks
- **100+ docs**, 80+ scripts, 870+ internal links

The project already has 12 conceptual agent roles defined in `agents/roles/` (ARCHITECT, DEV, DOCS, PM, etc.) but **zero VS Code `.agent.md` files** actually created. The existing roles are prompt-template documents, not real VS Code agents.

**Goal:** Create a practical VS Code Copilot agent system that:
- Has purpose-built agents for each development domain
- Uses handoffs for multi-step workflows
- Maintains docs, archives, and logs automatically
- Follows VS Code's official `.agent.md` format (March 2025+)

---

## 2. Current State Audit

### What Exists Today

| Category | Location | Count | Status |
|----------|----------|-------|--------|
| Always-on instructions | `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` | 3 | ✅ Active |
| File-based instructions | `.github/instructions/*.instructions.md` | 4 | ✅ Active (docs, fastapi, python-core, react) |
| Claude rules | `.claude/rules/*.md` | 4 | ✅ Active (mirroring .github/instructions) |
| Prompt files | `.github/prompts/*.prompt.md` | 5 | ✅ Active (new-feature, bug-fix, code-review, session-end, add-api-endpoint) |
| VS Code custom agents (`.agent.md`) | `.github/agents/` | **0** | ❌ Missing — folder doesn't even exist |
| Agent skills (SKILL.md) | `.github/skills/` | **0** | ❌ Missing |
| Conceptual role docs | `agents/roles/*.md` | 12 | ⚠️ Exist as docs only, not VS Code agents |
| Agent-9 governance docs | `agents/agent-9/` | 10 | ⚠️ Detailed docs, no VS Code agent |

### Gap Analysis

| Gap | Impact | Priority |
|-----|--------|----------|
| No `.agent.md` files | Can't switch agents via VS Code dropdown | 🔴 Critical |
| No agent skills | No reusable workflows with scripts | 🟡 High |
| Conceptual roles not wired to VS Code | 12 role docs unused | 🟡 High |
| No handoff chains defined | Manual context passing | 🟡 High |
| Docs/archive done manually | Inconsistent, things get stale | 🟡 High |
| No structured daily logging agent | WORKLOG updates sporadic | 🟡 High |

### What Works Well

- **Instructions system** — 4 file-based `.instructions.md` + 4 `.claude/rules/` cover all code domains
- **Prompt files** — 5 reusable prompts for common workflows
- **Session workflow** — `run.sh session` automates session start/end
- **Git safety** — `ai_commit.sh`, PR enforcement scripts
- **Bootstrap doc** — comprehensive `agent-bootstrap.md`

---

## 3. VS Code Copilot Agent System — How It Works

### The Four Customization Layers

```
Layer 1: Instructions (always-on rules)
  └── copilot-instructions.md, AGENTS.md, CLAUDE.md
  └── *.instructions.md (file-pattern scoped)

Layer 2: Prompt Files (invoke with /)
  └── .github/prompts/*.prompt.md
  └── Reusable task templates

Layer 3: Custom Agents (switch personas)
  └── .github/agents/*.agent.md       ← WE NEED THESE
  └── Specialized roles with tool restrictions
  └── Handoffs between agents

Layer 4: Agent Skills (portable capabilities)
  └── .github/skills/*/SKILL.md       ← WE NEED THESE
  └── Instructions + scripts + examples
  └── Slash-command invocable
```

### Key Concepts

| Concept | What It Is | File Format |
|---------|-----------|-------------|
| **Custom Agent** | A persona with specific tools, model, and instructions | `.agent.md` in `.github/agents/` |
| **Agent Skill** | A reusable capability with scripts/resources | `SKILL.md` in `.github/skills/<name>/` |
| **Prompt File** | A one-shot task template | `.prompt.md` in `.github/prompts/` |
| **Instructions** | Always-on rules applied to every request | `.instructions.md` or `copilot-instructions.md` |
| **Handoff** | Guided transition from one agent to another | `handoffs:` in agent YAML frontmatter |

### Agent File Format (`.agent.md`)

```markdown
---
description: What this agent does
tools: ['search', 'editFiles', 'runInTerminal', 'web']
model: Claude Sonnet 4.5 (copilot)
handoffs:
  - label: Next Step
    agent: another-agent
    prompt: Continue with...
    send: false
---

# Agent Instructions

Your detailed instructions here...
```

### Key Tool Names for VS Code Agents

| Tool Name | What It Does |
|-----------|-------------|
| `search` | Code search (semantic + text) |
| `editFiles` | Create and edit files |
| `runInTerminal` | Execute terminal commands |
| `web` | Fetch web pages |
| `listFiles` | List directory contents |
| `readFile` | Read file contents |
| `agent` | Invoke subagents |

---

## 4. Agent Roster — 9 Agents We Need

After analyzing the project workflow, codebase, and VS Code capabilities, here are the **9 agents** to create, organized by domain:

### Agent Architecture Overview

```
                    ┌──────────────┐
                    │  Orchestrator │  (PM/Planning agent)
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │  Frontend  │   │  Backend  │   │ Structural │
    │  Developer │   │ Developer │   │  Engineer  │
    └─────┬─────┘   └─────┬─────┘   └───────────┘
          │                │
    ┌─────▼─────┐   ┌─────▼─────┐
    │    UI     │   │  API Dev  │
    │  Designer │   │           │
    └───────────┘   └───────────┘
          │
    ┌─────▼─────────────────────────┐
    │  Reviewer  │  DocMaster │ Ops │
    └────────────┴────────────┴─────┘
```

### Agent 1: Orchestrator (PM)

| Property | Value |
|----------|-------|
| **File** | `.github/agents/orchestrator.agent.md` |
| **Purpose** | Plan, triage, scope, delegate, manage sessions |
| **Tools** | `search`, `readFile`, `listFiles`, `web`, `agent` |
| **Model** | Claude Sonnet 4.5 (reasoning-heavy) |
| **Handoffs** | → frontend, backend, structural-engineer, doc-master |
| **When to use** | Session start, planning, task breakdown, session end |

**Why:** Every session starts with planning. The orchestrator reads `TASKS.md`, `next-session-brief.md`, understands priorities, then hands off to the right specialist.

### Agent 2: Frontend Developer

| Property | Value |
|----------|-------|
| **File** | `.github/agents/frontend.agent.md` |
| **Purpose** | React 19, R3F, Tailwind, hooks, components, Zustand stores |
| **Tools** | `search`, `editFiles`, `runInTerminal`, `listFiles`, `readFile` |
| **Model** | Claude Sonnet 4.5 (copilot) |
| **Handoffs** | → reviewer, ui-designer, orchestrator |
| **When to use** | New React components, hooks, state management, R3F 3D |

**Key rules loaded:**
- React instructions (`.github/instructions/react.instructions.md`)
- Tailwind only — no CSS files
- Data flows through FastAPI (never local math)
- Check existing hooks before creating new ones
- 18+ hooks already exist (CSV, geometry, export, insights)

### Agent 3: Backend Developer

| Property | Value |
|----------|-------|
| **File** | `.github/agents/backend.agent.md` |
| **Purpose** | Python structural_lib core, IS 456 math, services layer |
| **Tools** | `search`, `editFiles`, `runInTerminal`, `listFiles`, `readFile` |
| **Model** | Claude Sonnet 4.5 (copilot) |
| **Handoffs** | → api-developer, reviewer, structural-engineer |
| **When to use** | Core math, services, adapters, insights, optimization |

**Key rules loaded:**
- 4-layer architecture strictly enforced
- Units always explicit (mm, N/mm², kN, kNm)
- `api.py` is a stub — real code in `services/api.py`
- Run `discover_api_signatures.py` before wrapping functions
- Always `.venv/bin/python`, never bare `python`

### Agent 4: API Developer

| Property | Value |
|----------|-------|
| **File** | `.github/agents/api-developer.agent.md` |
| **Purpose** | FastAPI routers, endpoints, OpenAPI, WebSocket |
| **Tools** | `search`, `editFiles`, `runInTerminal`, `listFiles`, `readFile` |
| **Model** | Claude Sonnet 4.5 (copilot) |
| **Handoffs** | → reviewer, frontend, backend |
| **When to use** | New API routes, Pydantic models, middleware, auth |

**Key rules loaded:**
- FastAPI instructions
- Check existing routes before adding (`grep -r "@router"`)
- 38 endpoints across 12 routers already exist
- Routers import from structural_lib directly — no logic duplication
- Docker testing required

### Agent 5: UI Designer

| Property | Value |
|----------|-------|
| **File** | `.github/agents/ui-designer.agent.md` |
| **Purpose** | Visual design, UX flow, component layout, accessibility |
| **Tools** | `search`, `readFile`, `listFiles`, `web` |
| **Model** | Claude Sonnet 4.5 (copilot) |
| **Handoffs** | → frontend (to implement) |
| **When to use** | Layout decisions, UX flow, visual hierarchy, component design |

**Note:** Read-only tools — this agent designs but doesn't code. Hands off to frontend for implementation.

### Agent 6: Structural Engineer

| Property | Value |
|----------|-------|
| **File** | `.github/agents/structural-engineer.agent.md` |
| **Purpose** | IS 456 code compliance, formula validation, design verification |
| **Tools** | `search`, `readFile`, `listFiles`, `web`, `runInTerminal` |
| **Model** | Claude Sonnet 4.5 (copilot) |
| **Handoffs** | → backend (to implement), reviewer (to verify) |
| **When to use** | New IS 456 clauses, formula correctness, benchmark validation |

**Key domain knowledge:**
- IS 456:2000 clause references
- SP:16 design aids validation
- Edge cases: min reinforcement, max spacing
- Units: mm, N/mm², kN, kNm — always explicit
- flexure.py, shear.py, detailing.py, torsion.py, serviceability.py

### Agent 7: Reviewer

| Property | Value |
|----------|-------|
| **File** | `.github/agents/reviewer.agent.md` |
| **Purpose** | Code review, architecture validation, security, testing |
| **Tools** | `search`, `readFile`, `listFiles`, `runInTerminal` |
| **Model** | Claude Sonnet 4.5 (copilot) |
| **Handoffs** | → orchestrator (approve/reject) |
| **When to use** | Pre-commit review, PR review, architecture checks |

**Read-heavy, write-light:** Runs tests, checks architecture boundaries, validates units. Can run terminal commands for tests but restricts file editing.

### Agent 8: Doc Master

| Property | Value |
|----------|-------|
| **File** | `.github/agents/doc-master.agent.md` |
| **Purpose** | Documentation maintenance, archives, indexes, session logs |
| **Tools** | `search`, `editFiles`, `runInTerminal`, `listFiles`, `readFile` |
| **Model** | Claude Sonnet 4.5 (copilot) |
| **Handoffs** | → orchestrator |
| **When to use** | Session end, doc updates, index regeneration, archive cleanup |

**Key responsibilities:**
- Update SESSION_LOG.md, WORKLOG.md
- Maintain next-session-brief.md
- Run `safe_file_move.py`, `safe_file_delete.py`
- Generate indexes via `generate_all_indexes.sh`
- Check/fix links via `check_links.py`
- Archive stale docs to `_archive/`
- Never manual `mv` or `rm` — always use scripts

### Agent 9: Ops (DevOps/Git)

| Property | Value |
|----------|-------|
| **File** | `.github/agents/ops.agent.md` |
| **Purpose** | Git workflow, CI/CD, Docker, environment, deployments |
| **Tools** | `search`, `editFiles`, `runInTerminal`, `listFiles`, `readFile` |
| **Model** | Claude Sonnet 4.5 (copilot) |
| **Handoffs** | → orchestrator |
| **When to use** | Commits, PRs, Docker builds, CI fixes, environment issues |

**Key rules:**
- ALWAYS `ai_commit.sh` — never manual git
- PR enforcement via `should_use_pr.sh`
- Docker uses Colima, not Docker Desktop
- `--host "::"` for uvicorn (IPv6 dual-stack)

### Agent Count Summary

| # | Agent | Domain | Tools Profile |
|---|-------|--------|---------------|
| 1 | Orchestrator | Planning, delegation | Read-only + subagents |
| 2 | Frontend | React, R3F, Tailwind | Full edit |
| 3 | Backend | Python core, IS 456 | Full edit |
| 4 | API Developer | FastAPI, endpoints | Full edit |
| 5 | UI Designer | Visual design, UX | Read-only |
| 6 | Structural Engineer | IS 456 compliance | Read + terminal |
| 7 | Reviewer | Code review, testing | Read + terminal |
| 8 | Doc Master | Docs, archives, logs | Full edit |
| 9 | Ops | Git, CI/CD, Docker | Full edit |

**Why 9?** Could be fewer (merge API Dev into Backend, merge UI Designer into Frontend = 7), but the granularity helps because:
- Different tools restrictions prevent accidents (UI Designer can't edit code)
- Handoff chains create audit trails
- Specialization improves instruction quality (each agent gets focused context)

---

## 5. Agent Implementation Plan

### File Structure to Create

```
.github/
├── agents/                          ← NEW: VS Code custom agents
│   ├── orchestrator.agent.md
│   ├── frontend.agent.md
│   ├── backend.agent.md
│   ├── api-developer.agent.md
│   ├── ui-designer.agent.md
│   ├── structural-engineer.agent.md
│   ├── reviewer.agent.md
│   ├── doc-master.agent.md
│   └── ops.agent.md
├── skills/                          ← NEW: Agent skills
│   ├── session-management/
│   │   └── SKILL.md
│   ├── is456-verification/
│   │   └── SKILL.md
│   ├── safe-file-ops/
│   │   └── SKILL.md
│   └── api-discovery/
│       └── SKILL.md
├── instructions/                    ← EXISTS: keep as-is
│   ├── docs.instructions.md
│   ├── fastapi.instructions.md
│   ├── python-core.instructions.md
│   └── react.instructions.md
├── prompts/                         ← EXISTS: keep as-is
│   ├── add-api-endpoint.prompt.md
│   ├── bug-fix.prompt.md
│   ├── code-review.prompt.md
│   ├── new-feature.prompt.md
│   └── session-end.prompt.md
└── copilot-instructions.md          ← EXISTS: keep as-is
```

### Key Agent Skills to Create

| Skill | Purpose | Contains |
|-------|---------|----------|
| `session-management` | Start/end sessions, update logs, create handoffs | SKILL.md + checklist |
| `is456-verification` | Validate IS 456 formulas against SP:16 benchmarks | SKILL.md + test data |
| `safe-file-ops` | Safe file move/delete preserving 870+ links | SKILL.md references to scripts |
| `api-discovery` | Discover API signatures before wrapping | SKILL.md + examples |

---

## 6. Document Maintenance & File Structure Strategy

### Current Doc Structure

```
docs/
├── TASKS.md              ← Task board (single source of truth)
├── WORKLOG.md             ← Compact change log (one line per change)
├── SESSION_LOG.md         ← Detailed session history (400KB+)
├── _active/               ← Work-in-progress docs
├── _archive/              ← Completed/stale docs
├── _internal/             ← Internal notes
├── planning/              ← Plans, briefs, research
│   └── next-session-brief.md  ← Handoff to next session
├── architecture/          ← Architecture docs
├── reference/             ← API reference, tech stack
├── agents/                ← Agent guides and sessions
├── guidelines/            ← Governance, folder structure
└── getting-started/       ← Bootstrap, setup guides
```

### Maintenance Rules (Enforced by Doc Master Agent)

| Rule | What | How | Frequency |
|------|------|-----|-----------|
| **Session logging** | Every session logged in SESSION_LOG.md | `./run.sh session summary` | Every session end |
| **Work log** | One line per change in WORKLOG.md | Manual append | Every change |
| **Task board** | Mark done, add new items | Edit TASKS.md | Every session end |
| **Handoff brief** | What the next agent should do | Edit next-session-brief.md | Every session end |
| **Index regeneration** | Update folder indexes after file moves | `./run.sh generate indexes` | After structural changes |
| **Link checking** | Verify 870+ internal links | `./run.sh check --category docs` | Weekly |
| **Archive stale docs** | Move old docs to _archive/ | `scripts/archive_old_files.sh` | Monthly |
| **Duplicate check** | Check docs-canonical.json before creating | `scripts/find_automation.py` | Before creating any doc |

### Archive Policy

| Age | Action |
|-----|--------|
| Active (referenced in TASKS.md) | Keep in main location |
| Completed (done, no references) | Move to `_archive/` after 30 days |
| Session logs older than 3 months | Summarize key points, archive detail |
| Planning docs for shipped features | Archive after release |

### Daily Work Log Format (WORKLOG.md)

```markdown
| Date | Task ID | What Changed | Commit |
|------|---------|-------------|--------|
| 2026-03-27 | TASK-XXX | Added frontend agent | a1b2c3d |
```

---

## 7. Daily Work Log & Archive System

### Session Workflow (Enforced by Orchestrator + Doc Master)

```
┌──────────────────────────────────────────────────────────┐
│                    SESSION START                          │
│                                                          │
│  1. Orchestrator reads next-session-brief.md             │
│  2. Orchestrator reads TASKS.md                          │
│  3. Orchestrator runs ./run.sh session start             │
│  4. Orchestrator plans → hands off to specialist agent   │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                    DURING SESSION                         │
│                                                          │
│  5. Specialist agent(s) do the work                      │
│  6. Each commit via ai_commit.sh (Ops agent)             │
│  7. Each change → one line in WORKLOG.md                 │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                    SESSION END                            │
│                                                          │
│  8.  Doc Master runs ./run.sh session summary            │
│  9.  Doc Master updates WORKLOG.md                       │
│  10. Doc Master updates next-session-brief.md            │
│  11. Doc Master updates TASKS.md                         │
│  12. Ops agent commits "docs: session end"               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Automated Checks (Doc Master Skill)

- [ ] SESSION_LOG.md updated
- [ ] WORKLOG.md has entry for every commit
- [ ] next-session-brief.md reflects current state
- [ ] TASKS.md has no stale "in progress" items
- [ ] All new files have metadata headers
- [ ] No orphaned docs (unreferenced)

---

## 8. Handoff Workflow Between Agents

### Common Handoff Chains

| Workflow | Chain | Description |
|----------|-------|-------------|
| **New Feature** | Orchestrator → Backend → API Dev → Frontend → Reviewer → Doc Master | Full-stack feature |
| **Bug Fix** | Orchestrator → (Backend \| Frontend) → Reviewer → Doc Master | Fix and verify |
| **IS 456 Change** | Orchestrator → Structural Engineer → Backend → Reviewer | Formula + implementation |
| **UX Redesign** | Orchestrator → UI Designer → Frontend → Reviewer | Design then build |
| **Session End** | Any Agent → Doc Master → Ops | Log, archive, commit |
| **Docs Only** | Orchestrator → Doc Master | Update docs |
| **Release** | Orchestrator → Reviewer → Ops → Doc Master | Ship and document |

### Handoff Protocol

1. **Sender** summarizes what was done and what needs to happen next
2. **Handoff button** in VS Code switches to the next agent with context
3. **Receiver** reads the handoff prompt and picks up from there
4. **Each handoff preserves conversation history**

---

## 9. Best Practices, Tips & Mistakes to Avoid

### Best Practices (from VS Code docs + project experience)

| # | Practice | Why |
|---|----------|-----|
| 1 | **Keep instruction files concise** | They load on every request — bloat slows responses |
| 2 | **Scope with `applyTo` patterns** | Different rules for frontend vs backend |
| 3 | **Limit tools per agent** | Fewer tools = faster, more focused responses |
| 4 | **Use read-only agents for review/design** | Prevents accidental edits |
| 5 | **Pin models in agent files** | Consistent behavior across sessions |
| 6 | **Use handoffs for multi-step workflows** | Guided transitions preserve context |
| 7 | **Start new sessions for unrelated tasks** | Context pollution degrades quality |
| 8 | **Use subagents for investigation** | Keeps main context clean |
| 9 | **Plan first, then implement** | Use Plan agent before coding |
| 10 | **Include test cases in prompts** | AI can verify its own work |

### Tips for This Project Specifically

| Tip | Detail |
|-----|--------|
| **Always run `discover_api_signatures.py`** | Never guess param names (`b_mm` not `width`) |
| **Check hooks before creating** | 18+ React hooks exist — duplication is the #1 mistake |
| **Use `safe_file_move.py`** | Manual `mv` breaks 870+ internal links |
| **Verify with `./run.sh check --quick`** | Fast validation before committing |
| **Start sessions with context** | Read `next-session-brief.md` first |
| **Use `/compact` for long conversations** | Keeps context focused |
| **Parallel sessions for independent tasks** | Frontend + backend can run simultaneously |

### Mistakes to Avoid

| Mistake | Impact | Historical Cost |
|---------|--------|-----------------|
| ❌ Manual git (add/commit/push) | Merge conflicts | 10-30 min per incident |
| ❌ Using `--force` to bypass PR | Broken CI, lost work | 10+ hours total |
| ❌ Duplicating React hooks | Broken features, bugs | Multiple sessions wasted |
| ❌ Guessing API params | Failed tests | Hours debugging |
| ❌ Editing stub `api.py` | Changes have no effect | Sessions wasted |
| ❌ Manual file move/delete | Broken links | 870+ links at risk |
| ❌ Skipping session logging | Lost context | 10+ hours rework |
| ❌ `docker` without `colima start` | Permission errors | Debug time |
| ❌ `uvicorn --host 0.0.0.0` | IPv6 issues on Mac | Browser can't connect |
| ❌ Bare `python` instead of `.venv/bin/python` | Wrong env | Import errors |
| ❌ Creating docs without metadata | Ungoverned content | Archive confusion |
| ❌ Mixing architecture layers | Import errors | Refactor cost |
| ❌ Too many tools on an agent | Slow, unfocused responses | Quality issues |
| ❌ One giant conversation for everything | Context degradation | Bad responses |

### Things to Always Do

| ✅ Do | Why |
|-------|-----|
| Search before coding | Prevent duplication |
| Use `ai_commit.sh` | Safe git workflows |
| Run tests before commit | Catch regressions |
| Update WORKLOG.md | Compact history prevents rework |
| Pin models in agents | Consistent behavior |
| Read indexes before files | Faster context loading |
| Use handoffs between agents | Guided workflow |
| Archive completed docs | Keep docs current |
| Check `docs-canonical.json` | Prevent duplicate docs |
| Use `/session-end` prompt | Never forget session logging |

---

## 10. Implementation Roadmap

### Phase 1: Core Agents (Do First)

Create the 9 `.agent.md` files in `.github/agents/`:

| Priority | Agent | Estimated Effort |
|----------|-------|-----------------|
| P0 | `orchestrator.agent.md` | Small — planning + read-only |
| P0 | `frontend.agent.md` | Medium — React rules + existing hooks list |
| P0 | `backend.agent.md` | Medium — 4-layer rules + IS 456 |
| P0 | `doc-master.agent.md` | Medium — doc maintenance rules |
| P0 | `ops.agent.md` | Small — git + docker rules |

### Phase 2: Specialist Agents

| Priority | Agent | Estimated Effort |
|----------|-------|-----------------|
| P1 | `api-developer.agent.md` | Small — FastAPI rules |
| P1 | `reviewer.agent.md` | Small — checklist-driven |
| P1 | `structural-engineer.agent.md` | Medium — IS 456 domain knowledge |
| P1 | `ui-designer.agent.md` | Small — read-only design agent |

### Phase 3: Skills ✅ COMPLETE

| Priority | Skill | Status |
|----------|-------|--------|
| P2 | `session-management/SKILL.md` | ✅ Created — session start/end/check workflow |
| P2 | `safe-file-ops/SKILL.md` | ✅ Created — safe move/delete/migrate with link preservation |
| P2 | `api-discovery/SKILL.md` | ✅ Created — discover_api_signatures wrapper |
| P2 | `is456-verification/SKILL.md` | ✅ Created — IS 456 test categories and benchmarks |

### Phase 4: Optimization ✅ COMPLETE

**Completed optimizations:**

1. **Agent consistency audit** — All 9 agents reviewed for cross-reference gaps
2. **Git commit rule propagated** — Added `ai_commit.sh` rule to all 4 editing agents (frontend, backend, api-developer, doc-master) — previously only ops had it
3. **PR workflow propagated** — Added `./run.sh pr status` check to frontend, backend, api-developer
4. **Skills wired into agents:**
   - backend → `/api-discovery`, `/is456-verification`
   - api-developer → `/api-discovery`
   - structural-engineer → `/is456-verification`, `/api-discovery`
   - doc-master → `/safe-file-ops`, `/session-management`
   - ops → `/session-management`, `/safe-file-ops`
5. **Missing handoffs added:**
   - api-developer → backend ("Backend Function Needed")
   - structural-engineer → api-developer ("Update API Contract")
6. **3 new prompt files** created (total now 8):
   - `session-start.prompt.md` — Session start checklist (paired with existing session-end)
   - `file-move.prompt.md` — Safe file migration workflow
   - `is456-verify.prompt.md` — IS 456 formula verification workflow
7. **AGENTS.md updated** — Now includes full agent roster, skills table, prompt file table, and handoff chains

**Ongoing optimization (manual review over time):**

- Monitor which agents get used vs. ignored
- If `api-developer` is rarely invoked separately, fold into `backend`
- If `ui-designer` never generates actionable designs, simplify to a prompt file
- Track common mistakes not yet covered by agent instructions
- Review handoff friction — are agents passing context cleanly?

---

## Appendix A: VS Code Copilot Customization Reference

### Official Documentation Links

| Topic | URL |
|-------|-----|
| Custom Agents | https://code.visualstudio.com/docs/copilot/customization/custom-agents |
| Agent Skills | https://code.visualstudio.com/docs/copilot/customization/agent-skills |
| Custom Instructions | https://code.visualstudio.com/docs/copilot/customization/custom-instructions |
| Prompt Files | https://code.visualstudio.com/docs/copilot/customization/prompt-files |
| Best Practices | https://code.visualstudio.com/docs/copilot/best-practices |
| Customization Overview | https://code.visualstudio.com/docs/copilot/customization/overview |
| Awesome Copilot (examples) | https://github.com/github/awesome-copilot |

### Quick Commands for Agent Management

| Action | Command |
|--------|---------|
| Create an agent | Type `/create-agent` in chat or `/agents` to open menu |
| Create a skill | Type `/create-skill` in chat or `/skills` to open menu |
| Create instructions | Type `/create-instruction` in chat |
| Generate workspace config | Type `/init` in chat |
| Open customization editor | Gear icon in Chat view or `Chat: Open Chat Customizations` |
| View diagnostics | Right-click Chat view → Diagnostics |
| Debug agent logs | Ellipsis menu → Show Agent Debug Logs |

### Customization Priority Order

1. Personal instructions (user-level, highest)
2. Repository instructions (`.github/copilot-instructions.md` or `AGENTS.md`)
3. Organization instructions (lowest)

### Tool Sets Available

| Tool | Description |
|------|-------------|
| `search` | Workspace code search |
| `editFiles` | Create/edit/delete files |
| `runInTerminal` | Execute shell commands |
| `web` / `web/fetch` | Fetch web content |
| `listFiles` | List directory contents |
| `readFile` | Read file contents |
| `agent` | Invoke subagents |
| `browser` | Integrated browser (experimental) |

---

## Appendix B: Mapping Existing Roles to New Agents

| Old Role (agents/roles/) | New Agent (.agent.md) | Notes |
|--------------------------|----------------------|-------|
| ARCHITECT | orchestrator | Merged with PM for planning |
| PM | orchestrator | Combined planning + architecture |
| DEV | backend, frontend | Split by stack |
| UI | ui-designer, frontend | Design vs implementation |
| CLIENT | (removed) | User proxy — not an AI agent role |
| RESEARCHER | structural-engineer | Domain-specific research |
| TESTER | reviewer | Code review + testing |
| DOCS | doc-master | Documentation steward |
| DEVOPS | ops | Git + CI/CD + Docker |
| GOVERNANCE | doc-master | Merged — governance is doc maintenance |
| INTEGRATION | api-developer | Schema + API integration |
| SUPPORT | (removed) | User support — not an AI agent role |

---

*This plan is the canonical reference for the VS Code Copilot agent system. Update it as agents are created and refined.*
