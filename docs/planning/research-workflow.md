# Multi-Agent Research Workflow

> **Purpose:** Define how AI agents collaborate on research topics from inception to implementation.
> **Scope:** Any feature that starts as an idea and needs exploration before coding.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RESEARCH WORKFLOW                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Stage 1        Stage 2        Stage 3        Stage 4        Stage 5    │
│  ────────       ────────       ────────       ────────       ────────   │
│  INITIATE  →   EXPLORE    →   EVALUATE   →   DECIDE     →   HANDOFF    │
│                                                                          │
│  CLIENT        RESEARCHER     DEV            PM             DOCS        │
│  PM            TESTER         Review         Owner          DEV         │
│                               Agents                                     │
│                                                                          │
│  1-2 hrs       2-4 hrs        1-2 hrs        30 min         1 hr        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Stage 1: Initiate (CLIENT + PM)

**Duration:** 1-2 hours
**Agents:** CLIENT (primary), PM (secondary)
**Output:** Problem statement + initial constraints

### CLIENT Agent Tasks

1. **Define the problem**
   - What pain are we solving?
   - Who feels this pain? (user personas)
   - How do they work around it today?

2. **Gather requirements**
   - What does success look like?
   - What's out of scope?
   - Any hard constraints from users?

3. **Document in template**
   - Fill: Problem Statement, Users & Personas, Success Criteria
   - Leave: Options, Scoring, Decision (for later stages)

### PM Agent Tasks

1. **Check alignment**
   - Does this fit current roadmap phase?
   - What's the WIP impact?
   - Any blockers from other work?

2. **Set boundaries**
   - Timebox the research (e.g., "2 sessions max")
   - Define decision date
   - Assign owner

### Stage 1 Deliverable

```markdown
## Problem Statement
[1-2 sentences from CLIENT]

## Users & Personas
| User | Context | Pain Point |
|------|---------|------------|
| ... | ... | ... |

## Constraints (from PM)
- [ ] Must fit Phase [A/B/C/D/E]
- [ ] No new required dependencies
- [ ] Decision by: [DATE]
- [ ] Owner: [AGENT/PERSON]

## Success Criteria
| Metric | Target |
|--------|--------|
| ... | ... |
```

---

## Stage 2: Explore (RESEARCHER + TESTER)

**Duration:** 2-4 hours
**Agents:** RESEARCHER (primary), TESTER (secondary)
**Output:** Options explored with pros/cons

### RESEARCHER Agent Tasks

1. **Market analysis**
   - What do existing tools do?
   - What's the industry standard?
   - What's novel/differentiated?

2. **Technical options**
   - List 2-4 approaches
   - Pros and cons for each
   - Dependencies and risks

3. **Constraints check**
   - Does each option fit our non-negotiables?
   - Determinism? Dependencies? Units?

### TESTER Agent Tasks

1. **Edge cases**
   - What could go wrong?
   - What inputs would break each option?
   - What's hard to test?

2. **Validation criteria**
   - How would we verify each option works?
   - What tests would we need?
   - Any parity concerns (Python/VBA)?

### Stage 2 Deliverable

```markdown
## Options Explored

### Option A: [Name]
**Description:** ...
**Pros:** ...
**Cons:** ...
**Edge cases (from TESTER):** ...
**Dependencies:** ...

### Option B: [Name]
**Description:** ...
**Pros:** ...
**Cons:** ...
**Edge cases (from TESTER):** ...
**Dependencies:** ...

## Constraints Verification
| Option | Deterministic | No New Deps | Fits Phase | Testable |
|--------|---------------|-------------|------------|----------|
| A | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ |
| B | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ |
```

---

## Stage 3: Evaluate (DEV + Review Agents)

**Duration:** 1-2 hours
**Agents:** DEV (primary), Review agents (critique)
**Output:** Scored options with feasibility notes

### DEV Agent Tasks

1. **Feasibility assessment**
   - Can we actually build each option?
   - What's the effort estimate?
   - Any hidden complexity?

2. **Architecture fit**
   - Does it fit our layer model (Core/App/I-O)?
   - Any schema changes needed?
   - Integration points?

3. **Score the options**
   - Use the standard rubric
   - Add effort estimates
   - Flag blockers

### Review Agent Tasks

1. **Critique each option**
   - What's missing?
   - What assumptions are wrong?
   - What risks are understated?

2. **Challenge the scores**
   - Is effort realistic?
   - Is trust impact justified?
   - Any blind spots?

### Stage 3 Deliverable

```markdown
## Feasibility Notes (from DEV)

### Option A
- Effort: [X days/weeks]
- Complexity: [Low/Medium/High]
- Blockers: [None / W08 / Schema freeze / etc.]
- Architecture notes: ...

### Option B
- Effort: [X days/weeks]
- Complexity: [Low/Medium/High]
- Blockers: [None / W08 / Schema freeze / etc.]
- Architecture notes: ...

## Scoring (Rubric Applied)

| Option | Trust | Value | Effort | Risk | Align | Total | Rank |
|--------|-------|-------|--------|------|-------|-------|------|
| A | /5 | /5 | /5 | /5 | /5 | /25 | |
| B | /5 | /5 | /5 | /5 | /5 | /25 | |

## Review Findings

| Severity | Finding | Option | Resolution |
|----------|---------|--------|------------|
| High | ... | A | ... |
| Medium | ... | B | ... |
```

---

## Stage 4: Decide (PM + Owner)

**Duration:** 30 minutes
**Agents:** PM (primary), designated Owner
**Output:** Decision + parking lot

### PM Agent Tasks

1. **Synthesize findings**
   - What does the scoring say?
   - What do review findings change?
   - Any new blockers surfaced?

2. **Make the call**
   - Choose: Approve / Defer / Split / Reject
   - Document rationale
   - Assign to roadmap phase

3. **Define parking lot**
   - What good ideas aren't for now?
   - When might we revisit?

### Stage 4 Deliverable

```markdown
## Decision

**Chosen option:** [A / B / Defer / Split]
**Rationale:** ...
**Roadmap placement:** [Phase X / v0.Y.Z / Post-v1.0]

## What We Will NOT Do (and why)
- [Option B]: [reason]
- [Idea X]: [reason]

## Parking Lot

| Idea | Why Parked | Revisit When |
|------|------------|--------------|
| ... | ... | ... |

## Approval
- [ ] PM: Approved scope
- [ ] Owner: Accepted assignment
- [ ] No WIP conflict
```

---

## Stage 5: Handoff (DOCS + DEV)

**Duration:** 1 hour
**Agents:** DOCS (primary), DEV (secondary)
**Output:** TASKS.md entries + implementation spec

### DOCS Agent Tasks

1. **Create task entries**
   - Add to `docs/TASKS.md`
   - Link to research doc
   - Set priority and estimates

2. **Update roadmap if needed**
   - Does this affect milestones?
   - Any phase adjustments?

3. **Mark research as Decided**
   - Update status in research doc
   - Add to research index

### DEV Agent Tasks

1. **Write implementation spec**
   - Define file changes
   - Define function signatures
   - Define test requirements

2. **Identify dependencies**
   - What must be done first?
   - Any external blockers?

### Stage 5 Deliverable

```markdown
## Next Steps (in TASKS.md)

| ID | Task | Agent | Est. | Priority | Depends On |
|----|------|-------|------|----------|------------|
| TASK-XXX | ... | DEV | X hr | High | None |
| TASK-XXX | ... | TESTER | X hr | Medium | TASK-XXX |

## Implementation Spec

### Files to Create/Modify
- `Python/structural_lib/xxx.py` — [purpose]
- `Python/tests/test_xxx.py` — [purpose]

### Key Functions
```python
def feature_name(param: Type) -> ReturnType:
    """[docstring draft]"""
```

### Test Requirements
- [ ] Unit tests for [X]
- [ ] Edge case: [Y]
- [ ] Golden file: [Z]

## Research Status Update
- Status: ~~In Review~~ → **Decided**
- Decision date: YYYY-MM-DD
- Implementation target: v0.X.Y
```

---

## Quick Reference: Agent Handoffs

```
CLIENT → RESEARCHER: "Here's the problem, go explore"
RESEARCHER → DEV: "Here are the options, assess feasibility"
DEV → Review: "Here are the scores, critique them"
Review → PM: "Here are the findings, make the call"
PM → DOCS: "Here's the decision, create tasks"
DOCS → DEV: "Here's the spec, start building"
```

---

## Timing Guidelines

| Research Size | Total Time | Stages |
|---------------|------------|--------|
| **Small** (single feature) | 4-6 hours | All 5, compressed |
| **Medium** (feature set) | 8-12 hours | All 5, full |
| **Large** (major direction) | 2-3 sessions | Stage 2 may iterate |

---

## Rules

1. **WIP=1 applies:** Research doesn't create parallel implementation work
2. **Timeboxes are real:** If Stage 2 exceeds 4 hours for small/medium research, force a decision
   (large research may iterate Stage 2 with PM approval)
3. **Parking lot is real:** Unapproved ideas don't sneak into tasks
4. **Decisions are final until revisited:** Don't re-debate in implementation
5. **Each stage has a deliverable:** No "we discussed it" without documentation

---

## Example: Visual Layer Research

| Stage | Agent | Duration | Output |
|-------|-------|----------|--------|
| 1. Initiate | CLIENT | 1 hr | Problem: "Engineers can't see critical beams" |
| 2. Explore | RESEARCHER | 3 hrs | Options: SVG, matplotlib, plotly |
| 3. Evaluate | DEV + Review | 2 hrs | Scored: SVG wins, deferred features identified |
| 4. Decide | PM | 30 min | Phase 1: Critical Set + Ledger + SVG |
| 5. Handoff | DOCS | 1 hr | TASK-100, TASK-101, TASK-102 created |

**Total:** ~7.5 hours across multiple sessions

---

## Templates

- Research template: [`_research-template.md`](_research-template.md)
- Task template: See `TASKS.md` format
- Implementation spec: Include in research doc or separate file

---

*This workflow ensures research is thorough, decisions are recorded, and implementation is well-defined.*
