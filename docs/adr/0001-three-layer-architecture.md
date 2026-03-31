---
owner: Main Agent
status: active
last_updated: 2026-03-30
doc_type: guide
complexity: intermediate
tags: []
---

# ADR 0001: 3-Layer Architecture

**Date:** 2026-01-24
**Status:** Accepted
**Owners:** AI Agent Team

## Context

The structural_engineering_lib codebase needs a clear separation between calculation logic, orchestration, and user interfaces. Without boundaries:
- Core calculation functions may accidentally import UI libraries
- Unit conversions get hidden in unexpected places
- Testing becomes difficult due to tight coupling
- V3 migration (FastAPI + React) becomes risky

## Decision

Adopt a strict **3-layer architecture** (now expanded to 4 layers in V3):

| Layer | Location | Rules |
|-------|----------|-------|
| **Core** | `Python/structural_lib/codes/` | Pure calculation functions. NO I/O, NO UI imports. Units always explicit. |
| **Application** | `services/api.py`, `services/adapters.py`, `services/beam_pipeline.py` | Orchestrates core functions. Can use pandas. NO UI imports. |
| **UI** | `react_app/`, `fastapi_app/` | Presentation and API layer. React 19 + FastAPI (V3 stack). |

## Options Considered

1. **Flat structure** - All code in one layer
   - Rejected: Makes testing difficult, high coupling
2. **Hexagonal architecture** - Ports and adapters
   - Rejected: Overkill for current scale, adds complexity
3. **3-Layer architecture** - Clear separation
   - Accepted: Simple, enforceable, scales well

## Consequences

### Positive
- Clear boundaries for testing
- Core layer is pure and predictable
- V3 migration is safe (FastAPI only touches Application layer)
- Architecture linter can enforce rules automatically

### Negative
- Some code duplication between layers is necessary
- Developers must understand layer rules
- Refactoring existing code takes time

## Test Plan

- Architecture linter (`scripts/check_architecture_boundaries.py`) runs in CI
- Violations block merge
- Core layer tests run without UI dependencies installed

## Links

- Tasks: TASK-CI-AUDIT
- Docs: [architecture/project-overview.md](../architecture/project-overview.md)
- Code: [scripts/check_architecture_boundaries.py](../../scripts/check_architecture_boundaries.py)
