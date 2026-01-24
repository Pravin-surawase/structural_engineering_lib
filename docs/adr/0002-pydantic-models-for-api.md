# ADR 0002: Pydantic Models for API Contracts

**Date:** 2026-01-24
**Status:** Accepted
**Owners:** AI Agent Team

## Context

The structural_lib API exposes 43+ functions with complex input/output types. For V3 migration:
- FastAPI requires typed request/response models
- Schema validation prevents runtime errors
- OpenAPI documentation needs accurate types
- Breaking changes must be detectable in CI

## Decision

Use **Pydantic v2 models** for all API data structures:

```python
from pydantic import BaseModel, Field, computed_field

class BeamGeometry(BaseModel):
    id: str
    label: str
    width_mm: float = Field(gt=0, description="Beam width in mm")
    depth_mm: float = Field(gt=0, description="Total depth in mm")

    @computed_field
    @property
    def effective_depth_mm(self) -> float:
        return self.depth_mm - 40.0 - 12.5  # cover + bar radius
```

### Key conventions:
1. Units in field names: `width_mm`, `mu_knm`, `fck_mpa`
2. Use `Field(gt=0)` for positive constraints
3. Use `computed_field` for derived values
4. All models are frozen (immutable)
5. Extra fields are forbidden (`extra='forbid'`)

## Options Considered

1. **Dataclasses** - Standard library
   - Rejected: No validation, no JSON schema, no OpenAPI
2. **TypedDict** - Lightweight
   - Rejected: No runtime validation
3. **Pydantic v2** - Full-featured
   - Accepted: Validation, serialization, FastAPI native

## Consequences

### Positive
- Automatic input validation
- OpenAPI schema generation
- Contract tests can verify schema stability
- Clear documentation via field descriptions

### Negative
- Learning curve for Pydantic v2 features
- Computed fields excluded from `model_validate()` by default
- Slight runtime overhead (acceptable for our scale)

## Parity Impact (Python ↔ VBA)

- VBA uses VBA types (Single, Double, String)
- Field names must match (VBA has no underscores, uses camelCase)
- Validation logic must be duplicated in VBA

## Test Plan

- Contract tests (`tests/integration/test_api_contracts.py`) verify:
  - Required fields present
  - Default values correct
  - Computed fields work
  - JSON round-trip succeeds
  - Schema stability (no accidental field changes)

## Links

- Tasks: TASK-CI-AUDIT
- Docs: [reference/api.md](../reference/api.md)
- Code: [Python/structural_lib/models.py](../../Python/structural_lib/models.py)
- Tests: [Python/tests/integration/test_api_contracts.py](../../Python/tests/integration/test_api_contracts.py)
