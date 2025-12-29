# Public API Maintenance Review (2025-12-29)

Scope: current public APIs (`api.py`, package exports) and planned API targets.
Goal: reduce drift, remove ambiguity, and keep stable entrypoints consistent.

Reviewed surfaces:
- `Python/structural_lib/api.py`
- `Python/structural_lib/__init__.py`
- `Python/structural_lib/beam_pipeline.py`
- `docs/reference/api.md`
- `docs/reference/api-stability.md`
- `docs/planning/library-api-expansion.md`

---

## Findings

### API-01 — Duplicate unit validation (inconsistent behavior)
Two validators exist:
- `_require_is456_units()` in `api.py`
- `beam_pipeline.validate_units()` in `beam_pipeline.py`

They accept different aliases and raise different error types. This can confuse
users and complicate maintenance.

**Fix:** centralize on `beam_pipeline.validate_units()` for public API checks.

---

### API-02 — `get_library_version()` fallback is stale
`api.get_library_version()` returns a hard-coded `"0.11.0"` when metadata is
missing. This will be wrong after future releases.

**Fix:** fall back to `structural_lib.__version__` or parse `pyproject.toml`.

---

### API-03 — Internal modules are exported at top-level
`__init__.__all__` exposes modules like `tables`, `utilities`, `types`,
but `docs/reference/api-stability.md` labels them as internal.

**Fix:** either remove these from `__all__` or document them as public-but-unstable.

---

### API-04 — Stability doc missing public `api.py` entrypoints
`docs/reference/api-stability.md` does not list `design_beam_is456`,
`check_beam_is456`, `check_compliance_report`, or `detail_beam_is456`.

**Fix:** add these to Stable API section.

---

### API-05 — Missing return type annotation
`detail_beam_is456()` lacks a return type annotation.

**Fix:** annotate as `BeamDetailingResult` (from `detailing`).

---

### API-06 — Units expectation not explicit for `check_compliance_report`
The `api.check_compliance_report()` wrapper assumes IS456 units but does not
accept a `units` parameter. This is fine but needs to be explicit in docs.

**Fix:** add a note in `docs/reference/api.md` and `api-stability.md`.

---

### API-07 — `beam_pipeline` marked stable but undocumented
`api-stability.md` lists `beam_pipeline` as stable, but `docs/reference/api.md`
does not document it, and it is not re-exported from `structural_lib`.

**Fix:** either document `beam_pipeline` in `docs/reference/api.md` or remove it
from Stable API.

---

### API-08 — Serviceability function name mismatch in stability doc
`api-stability.md` references `serviceability.check_deflection`, but the module
exposes `check_deflection_span_depth` and `check_deflection_level_b`.

**Fix:** update the stability doc to the correct function names.

---

### API-09 — `report`/`report_svg` exported but not classified
`__init__.__all__` exports `report` and `report_svg`, but `api-stability.md`
does not classify them as stable or experimental.

**Fix:** mark them explicitly (likely experimental) or remove from `__all__`.

---

### API-10 — `get_library_version` undocumented
`api.get_library_version()` is public but missing from `docs/reference/api.md`.

**Fix:** add a short entry in `docs/reference/api.md`.

---

### API-11 — Missing `api.py` helpers in API reference
`docs/reference/api.md` documents `check_beam_ductility`, `check_deflection_span_depth`,
and `check_crack_width`, but does not include `get_library_version()` or a dedicated
public API overview section. This makes the stable surface harder to discover.

**Fix:** add an "API Helpers" section in `docs/reference/api.md`.

---

### API-12 — Stability doc still lists non-existent deflection helper
`api-stability.md` refers to `serviceability.check_deflection`, which does not exist.

**Fix:** replace with `check_deflection_span_depth` and `check_deflection_level_b`.

---

## Recommended Actions (Tasks)

- Centralize unit validation on `beam_pipeline.validate_units`.
- Update version fallback for `get_library_version()`.
- Align `__all__` exports with stability policy.
- Document stable API entrypoints in `api-stability.md`.
- Add return type annotation for `detail_beam_is456()`.
- Clarify units requirement for `check_compliance_report()` in docs.
- Document or demote `beam_pipeline` in stability/docs.
- Fix serviceability function names in `api-stability.md`.
- Classify `report`/`report_svg` stability or stop re-exporting them.
- Document `get_library_version()` in `docs/reference/api.md`.
- Add public API helpers overview to `docs/reference/api.md`.
