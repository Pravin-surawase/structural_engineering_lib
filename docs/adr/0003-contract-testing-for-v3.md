# ADR 0003: Contract Testing for V3 Migration

**Date:** 2026-01-24
**Status:** Accepted
**Owners:** AI Agent Team

## Context

V3 migration will:
- Replace Streamlit with React + FastAPI
- Keep the Python calculation library unchanged
- Require API compatibility between old and new frontends

Without contract tests:
- Breaking changes go undetected until production
- Schema drift between Python models and API responses
- Serialization issues surface late

## Decision

Implement **contract tests** that verify API stability:

1. **Schema Stability Tests** - Verify Pydantic model fields don't change
2. **Serialization Tests** - JSON round-trip works correctly
3. **Computed Field Tests** - Derived properties calculate correctly
4. **Validation Tests** - Constraints are enforced

```python
class TestBeamGeometryContract:
    EXPECTED_FIELDS = {"id", "label", "width_mm", "depth_mm", ...}

    def test_schema_has_required_fields(self):
        schema = BeamGeometry.model_json_schema()
        actual = set(schema.get("properties", {}).keys())
        assert actual == self.EXPECTED_FIELDS
```

### Test categories:
| Category | Purpose | Example |
|----------|---------|---------|
| Schema stability | Detect field additions/removals | Required fields unchanged |
| Validation rules | Constraints work | width_mm > 0 enforced |
| Computed fields | Derivations correct | effective_depth calculated |
| Serialization | JSON works | model_dump_json() round-trips |

## Options Considered

1. **No contract tests** - Rely on integration tests
   - Rejected: Changes invisible until frontend breaks
2. **Snapshot testing** - Compare JSON snapshots
   - Rejected: Brittle, fails on any change
3. **Contract tests** - Structured schema verification
   - Accepted: Precise, maintainable, good error messages

## Consequences

### Positive
- Breaking changes detected immediately in CI
- Clear errors: "Field X removed" vs cryptic failures
- Documentation of expected API behavior
- Supports V3 parallel development

### Negative
- Contract tests must be updated when API intentionally changes
- Some duplication between contract tests and unit tests
- Initial setup effort

## Parity Impact (Python ↔ VBA)

- VBA API doesn't have contract tests (manual verification)
- Field name mapping must be documented
- Any Python API change requires VBA review

## Test Plan

- Contract tests run in CI (GitHub Actions)
- 685+ lines of contract tests in `test_api_contracts.py`
- Coverage of all public Pydantic models
- Schema versioning tests detect drift

## Links

- Tasks: TASK-CI-AUDIT
- Docs: [research/automation-audit-readiness-research.md](../research/automation-audit-readiness-research.md)
- Code: [Python/tests/integration/test_api_contracts.py](../../Python/tests/integration/test_api_contracts.py)
