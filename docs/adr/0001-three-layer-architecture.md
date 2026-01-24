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

Adopt a strict **3-layer architecture**:

| Layer | Location | Rules |
|-------|----------|-------|
| **Core** | `Python/structural_lib/codes/` | Pure calculation functions. NO I/O, NO Streamlit, NO pandas imports. Units always explicit. |
| **Application** | `api.py`, `job_runner.py`, `adapters.py` | Orchestrates core functions. Can use pandas. NO Streamlit. |
| **UI** | `streamlit_app/` | Presentation only. Can import from any layer. Should NOT import core internals directly. |

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

## Parity Impact (Python ↔ VBA)

- VBA has similar structure but simpler (no "application layer")
- Core calculations must match exactly
- UI layer in VBA is Excel-native, no overlap

## Test Plan

- Architecture linter (`scripts/check_architecture_boundaries.py`) runs in CI
- Violations block merge
- Core layer tests run without Streamlit installed

## Links

- Tasks: TASK-CI-AUDIT
- Docs: [architecture/project-overview.md](../architecture/project-overview.md)
- Code: [scripts/check_architecture_boundaries.py](../../scripts/check_architecture_boundaries.py)
