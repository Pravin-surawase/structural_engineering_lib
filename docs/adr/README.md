# ADRs (Architecture Decision Records)

Use ADRs to capture **non-trivial decisions** in a way that is easy for humans and AI agents to find later.

## When to write an ADR
Write one when you:
- Change public API contracts (Python or VBA)
- Choose between two algorithms/approaches (e.g., deflection method A vs B)
- Introduce a new dependency (Python package, Excel tooling, etc.)
- Decide a unit convention, rounding rule, or tolerance rule
- Make a compatibility choice (Windows-only vs cross-platform)

If it’s small and local (typo, refactor, minor test), no ADR needed.

## File naming
Use sequential numbering:
- `0001-serviceability-level-a.md`
- `0002-dxf-layer-conventions.md`

## ADR template (copy-paste)

```markdown
# ADR 000X: <title>

**Date:** YYYY-MM-DD  
**Status:** Proposed | Accepted | Superseded  
**Owners:** <name/role>  

## Context
What problem are we solving? What constraints matter (IS clauses, units, parity, platform)?

## Decision
What did we decide?

## Options considered
- Option A
- Option B

## Consequences
- Positive
- Negative / risks

## Parity impact (Python ↔ VBA)
- What must match exactly?
- Any tolerances?

## Test plan
- What tests prove this decision is correct?

## Links
- Tasks: TASK-XXX
- Docs: <relevant docs>
- Code: <paths>
```
