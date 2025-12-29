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

### How Features Evolve

```
Research → Shape → Decide → Implement → Release
   ↓         ↓        ↓         ↓          ↓
 Ideas    Scope    TASKS.md   Code      PyPI
```

### Agent Roles in Research

| Agent | Role in Research |
|-------|------------------|
| **RESEARCHER** | Explore options, identify constraints |
| **CLIENT** | Define user problems, validate solutions |
| **PM** | Scope decisions, prioritize |
| **DEV** | Feasibility, effort estimates |
| **TESTER** | Edge cases, validation criteria |

### Starting New Research

1. Copy `_research-template.md` to `research-{topic}/README.md`
2. Fill in Problem, Constraints, Options
3. Score options using the rubric
4. Make a decision (or park for later)
5. Move approved items to `TASKS.md`

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

---

## Templates

| Template | Use For |
|----------|---------|
| [_research-template.md](_research-template.md) | New research topics |

---

## Rules

1. **WIP=1 applies:** Research doesn't create parallel work
2. **Parking lot is real:** Unapproved ideas stay parked, not "half-in"
3. **Decisions are recorded:** So agents don't re-debate
4. **Scoring is consistent:** Use the rubric for comparability
