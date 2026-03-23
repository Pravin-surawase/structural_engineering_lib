# Planning

**Type:** Index
**Audience:** All Agents
**Status:** Production Ready
**Importance:** High
**Created:** 2025-01-01
**Last Updated:** 2026-03-24

---

Internal planning documents and research notes.

---

## Quick Links

| Document | Purpose |
|----------|---------|
| [Next Session Brief](next-session-brief.md) | What to work on next |
| [TASKS.md](../TASKS.md) | Canonical task backlog |
| [Folder Audit](folder-audit.md) | Complete repo audit (Session 91) |
| [AI Agent Efficiency Plan](ai-agent-efficiency-and-git-workflow-plan.md) | Agent infra improvements (Session 92) |

## Document Status

### Active (current priorities)
| Document | Last Updated | Status |
|----------|-------------|--------|
| `next-session-brief.md` | 2026-03-24 | ✅ Current handoff |
| `folder-audit.md` | 2026-03-24 | ✅ Complete (11 batches) |
| `ai-agent-efficiency-and-git-workflow-plan.md` | 2026-03-24 | ✅ Partially implemented |
| `agent-workflow-improvements.md` | 2026-03-23 | ✅ Active |
| `democratization-vision.md` | 2026-01-23 | 📋 Long-term vision |
| `v020-stabilization-checklist.md` | 2026-01-23 | 📋 v0.20 checklist |
| `pre-release-checklist.md` | 2026-02-11 | 📋 Release process |

### Historical (completed/superseded — kept for reference)
| Document | Notes |
|----------|-------|
| `8-week-development-plan.md` | Original sprint plan (v0.16–v0.20) |
| `session-30-fragment-crisis-resolution.md` | Streamlit fragment fix (resolved) |
| `hygiene-suggestions-2026-01-07.md` | Superseded by folder-audit.md |
| `project-needs-assessment-2026-01-09.md` | Superseded by current TASKS.md |
| `project-status-deep-dive.md` | January status snapshot |
| `brainstorming-platform-pivot.md` | Superseded by v3 React architecture |
| `icloud-to-local-move-analysis.md` | Infrastructure move (completed) |
| `folder-migration-progress.md` | Module migration tracking (completed) |
| `streamlit-phase-3-implementation-plan.md` | Streamlit phases (v3 supersedes) |
| `ui-layout-implementation-plan.md` | Implemented in React v3 |

---

## Research Process

> **Full workflow:** See [research-workflow.md](../_archive/2026-01/research-workflow.md) for the complete 5-stage process.

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
| [Project Status](../_archive/planning/project-status.md) | Current state summary |
| [Project Status Deep Dive](project-status-deep-dive.md) | Module maps, contracts |
| [Pre-Release Checklist](pre-release-checklist.md) | v1.0 gates |
| [v0.20 Stabilization](v020-stabilization-checklist.md) | Next milestone checklist |
| [v0.12 Plan](../_archive/planning/v0.12-plan.md) | v0.12 scope + milestones |
| [BBS + DXF Improvement Plan](bbs-dxf-improvement-plan.md) | Output contract + DXF/BBS quality plan |
| [Library API Expansion](library-api-expansion.md) | Library-first APIs + CLI helpers |
| [Public API Maintenance Review](../_archive/2026-01/public-api-maintenance-review.md) | Public API risks + fixes |

---

## Templates & Workflow

| Document | Use For |
|----------|---------|
| [research-workflow.md](../_archive/2026-01/research-workflow.md) | Full 5-stage process with agent handoffs |
| [_research-template.md](../_archive/2026-01/_research-template.md) | New research topics |

---

## Rules

1. **WIP=1 applies:** Research doesn't create parallel work
2. **Parking lot is real:** Unapproved ideas stay parked, not "half-in"
3. **Decisions are recorded:** So agents don't re-debate
4. **Scoring is consistent:** Use the rubric for comparability
