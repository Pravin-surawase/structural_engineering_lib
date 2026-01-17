# ADRs (Architecture Decision Records)

Use ADRs to capture **non-trivial decisions** in a way that is easy for humans and AI agents to find later.

**Updated:** 2026-01-11

---

## 📋 Current ADRs

| ADR | Title | Status |
|-----|-------|--------|
| *(none yet)* | Create ADRs as needed | - |

---

## ❓ When to Write an ADR

| Scenario | Write ADR? |
|----------|------------|
| Change public API contracts (Python or VBA) | ✅ Yes |
| Choose between algorithms/approaches | ✅ Yes |
| Introduce a new dependency | ✅ Yes |
| Decide unit convention, rounding, or tolerance | ✅ Yes |
| Make compatibility choice (Windows-only vs cross-platform) | ✅ Yes |
| Fix typo, refactor, minor test | ❌ No |

---

## 📝 File Naming

Use sequential numbering:
- `0001-serviceability-level-a.md`
- `0002-dxf-layer-conventions.md`

---

## 📄 ADR Template

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

---

## 📚 Related Documentation

| Document | Purpose |
|----------|---------|
| [Architecture](../architecture/README.md) | System design |
| [Guidelines](../guidelines/README.md) | Development standards |
| [Reference](../reference/README.md) | API documentation |

---

**Parent:** [docs/README.md](../README.md)
