# Research: [Topic Name]

> **Template version:** 1.0
> Copy this file to `research-{topic}/README.md` or `research-{topic}.md`

**Last Updated:** YYYY-MM-DD
**Status:** Draft | In Review | Decided | Archived
**Owner:** [Agent role or person]
**Decision Date:** [Target date]

---

## Problem Statement

*1-2 sentences. What pain are we solving? Who feels it?*

---

## Context

*What triggered this research? Link to issue, user feedback, or roadmap item.*

---

## Users & Personas

| User | Context | Pain Point |
|------|---------|------------|
| *e.g., Design Engineer* | *Designing 500 beams* | *"Can't find critical beams"* |

---

## Constraints (Non-Negotiables)

- [ ] Deterministic (same input → same output)
- [ ] No new required dependencies (stdlib only for core)
- [ ] Python/VBA parity where applicable
- [ ] Explicit units, no hidden defaults
- [ ] *Add project-specific constraints*

---

## Success Criteria

*How do we know this worked? Measurable outcomes.*

| Metric | Target |
|--------|--------|
| *e.g., Time to find critical beam* | *< 10 seconds* |

---

## Options Explored

### Option A: [Name]

**Description:** ...

**Pros:** ...

**Cons:** ...

### Option B: [Name]

**Description:** ...

**Pros:** ...

**Cons:** ...

---

## Scoring Rubric

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Trust Impact** | High | Does this increase engineer confidence? |
| **User Value** | High | Does this solve a real pain point? |
| **Effort** | Medium | How much work? (1=low, 5=high) |
| **Dependency Risk** | Medium | New deps? Schema changes? Blockers? |
| **Alignment** | Low | Fits current roadmap phase? |

### Scored Options

| Option | Trust | Value | Effort | Risk | Alignment | Total | Rank |
|--------|-------|-------|--------|------|-----------|-------|------|
| A | /5 | /5 | /5 | /5 | /5 | /25 | |
| B | /5 | /5 | /5 | /5 | /5 | /25 | |

*Lower effort/risk is better. Invert scores when totaling.*

---

## Decision

**Chosen option:** [A/B/Defer/Split]

**Rationale:** ...

**What we will NOT do (and why):**
- ...

---

## Parking Lot

*Good ideas that aren't for now. May revisit post-v1.0.*

| Idea | Why Parked | Revisit When |
|------|------------|--------------|
| *e.g., AI summaries* | *Non-deterministic* | *Post-v1.0, optional* |

---

## Next Steps

- [ ] Create TASK-XXX in `docs/TASKS.md`
- [ ] Update roadmap if affects milestones
- [ ] Assign to agent role: DEV / TESTER / DOCS / etc.

---

## Changelog

| Date | Change |
|------|--------|
| YYYY-MM-DD | Initial draft |

---

*End of template.*
