# Planning

Internal planning documents and research notes.

---

## Quick Links

| Document | Purpose |
|----------|---------|
| [Next Session Brief](next-session-brief.md) | What to work on next |
| [Production Roadmap](production-roadmap.md) | 52-week plan to v1.0 |
| [TASKS.md](../TASKS.md) | Canonical task backlog |

---

## Research Process

> **Full workflow:** See [research-workflow.md](research-workflow.md) for the complete 5-stage process.

### How Features Evolve

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Stage 1        Stage 2        Stage 3        Stage 4        Stage 5    │
│  ────────       ────────       ────────       ────────       ────────   │
│  INITIATE  →   EXPLORE    →   EVALUATE   →   DECIDE     →   HANDOFF    │
│                                                                          │
│  CLIENT        RESEARCHER     DEV            PM             DOCS        │
│  PM            TESTER         Review         Owner          DEV         │
│                               Agents                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### Agent Roles in Research

| Agent | Stage | Role |
|-------|-------|------|
| **CLIENT** | 1. Initiate | Define problems, user personas |
| **PM** | 1. Initiate, 4. Decide | Scope, constraints, final call |
| **RESEARCHER** | 2. Explore | Options, market analysis |
| **TESTER** | 2. Explore | Edge cases, validation criteria |
| **DEV** | 3. Evaluate | Feasibility, effort, architecture |
| **Review agents** | 3. Evaluate | Critique, find gaps |
| **DOCS** | 5. Handoff | Create tasks, update roadmap |

### Starting New Research

1. Copy `_research-template.md` to `research-{topic}/README.md` (folder-only)
2. **Stage 1:** CLIENT fills Problem, Personas; PM sets constraints
3. **Stage 2:** RESEARCHER explores options; TESTER adds edge cases
4. **Stage 3:** DEV scores feasibility; Review agents critique
5. **Stage 4:** PM makes decision, defines parking lot
6. **Stage 5:** DOCS creates tasks, DEV writes implementation spec

### Research Status Lifecycle

| Status | Meaning |
|--------|---------|
| **Draft** | Still gathering ideas |
| **In Review** | Scoring and evaluating options |
| **Decided** | Decision made, items moved to TASKS |
| **Archived** | Completed or superseded |

---

## Active Research

| Topic | Status | Location |
|-------|--------|----------|
| [Visual Layer](research-visual-design/) | In Review | `research-visual-design/` |
| [Platform Access](research-platform/) | Decided (post-v1.0) | `research-platform/` |
| [AI Enhancements](research-ai-enhancements.md) | Draft | Single file |
| [Detailing](research-detailing.md) | Draft | Single file |

---

## Planning Documents

| Document | Purpose |
|----------|---------|
| [Project Status](project-status.md) | Current state summary |
| [Project Status Deep Dive](project-status-deep-dive.md) | Module maps, contracts |
| [Pre-Release Checklist](pre-release-checklist.md) | v1.0 gates |
| [v0.20 Stabilization](v0.20-stabilization-checklist.md) | Next milestone checklist |
| [BBS + DXF Improvement Plan](bbs-dxf-improvement-plan.md) | Output contract + DXF/BBS quality plan |
| [Library API Expansion](library-api-expansion.md) | Library-first APIs + CLI helpers |
| [Public API Maintenance Review](public-api-maintenance-review.md) | Public API risks + fixes |

---

## Templates & Workflow

| Document | Use For |
|----------|---------|
| [research-workflow.md](research-workflow.md) | Full 5-stage process with agent handoffs |
| [_research-template.md](_research-template.md) | New research topics |

---

## Rules

1. **WIP=1 applies:** Research doesn't create parallel work
2. **Parking lot is real:** Unapproved ideas stay parked, not "half-in"
3. **Decisions are recorded:** So agents don't re-debate
4. **Scoring is consistent:** Use the rubric for comparability
