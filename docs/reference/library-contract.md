# Library Contract (v1) - Beam-Only IS 456

This document defines the stability promises for the beam design library.
It is written for developers who want to depend on the library as a core
building block (not a full product).

## 1) Scope (v1.x)

Included:
- IS 456 beam design checks (flexure, shear, serviceability).
- Beam detailing outputs (BBS, DXF) and batch workflows (CSV/JSON).
- Stable JSON schemas for job and results outputs.

Explicitly excluded until after v1.0:
- Frame/structure analysis solver, load generation.
- Multi-code plugins (ACI/EC2).
- Full BIM workflow or drafting replacement.

## 2) Stability Tiers

### 2.1 Stable Core API (frozen)
Pure functions and dataclasses with deterministic behavior:
- `flexure.design_*`
- `flexure.calculate_effective_flange_width`
- `shear.design_shear`
- `serviceability.check_deflection_span_depth`
- `serviceability.check_deflection_level_b`
- `serviceability.check_crack_width`
- `detailing.get_development_length`
- `detailing.get_lap_length`
- `detailing.create_beam_detailing`

### 2.2 Stable Orchestration (public entrypoints)
These are the recommended product-facing entrypoints:
- `api.design_beam_is456`
- `api.check_beam_is456`
- `api.check_compliance_report` (IS456 units only)
- `api.detail_beam_is456`
- `api.check_beam_ductility`
- `beam_pipeline.design_single_beam`
- `beam_pipeline.design_multiple_beams`
- `beam_pipeline.validate_units`

### 2.3 Adapters / Experimental
May evolve faster; prefer APIs or schemas for long-term integrations:
- CLI (`python -m structural_lib`)
- `report` and `report_svg`
- `excel_integration`

## 3) Contracts (non-negotiable)

### 3.1 Schema contracts
Breaking changes require a `schema_version` bump and migration note.
- Job schema: `docs/specs/v0.9-job-schema.md`
- Results schema: `beam_pipeline.SCHEMA_VERSION` + `docs/reference/api.md`
- BBS CSV columns and meanings are stable.
- DXF layer/text contract is stable (documented in DXF/BBS plan).

### 3.2 Error codes
Error codes are part of the public contract.
- `E_*` codes must remain stable across v1.x.
- Any change requires a deprecation note and migration guidance.
See `docs/reference/error-schema.md`.

### 3.3 Determinism
Same inputs must produce the same outputs.
- Stable ordering for batch outputs.
- Fixed formatting (no locale-dependent formats).
- No hidden defaults in public APIs.

## 4) Versioning and Compatibility

- SemVer is used for the Python package.
- v1.x promise: additive changes only in minor versions.
- No renaming/removing required fields without a major bump.
- Deprecations are documented and kept for at least one minor version.

## 5) Guidance for Integrators

If you are building a product on top:
- Prefer `api.py` or `beam_pipeline.py` for stability.
- Treat CLI/report/Excel tools as reference adapters, not the core contract.
- Use schemas for interchange; validate inputs before design runs.
