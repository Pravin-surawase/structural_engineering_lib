# Library API Expansion Plan (Beam-Only)

Goal: make the library easy to embed by exposing stable, composable functions
and thin CLI wrappers. This is library-first, not product-first.

**Status:** Planned (v0.12)

---

## Scope (v1.x)
- Beam-only (IS 456).
- Keep current 3-layer architecture.
- Add public APIs + CLI helpers without changing core math.

## Non-Goals (v1.x)
- No new analysis/solver engine.
- No multi-code plugins.
- No UI or web app features.

---

## Proposed Public API (Stable Surface)

All functions live in `structural_lib.api` and wrap existing modules.

### Validation
- `validate_job_spec(path) -> ValidationReport`
  - Uses `job_runner.load_job_spec`
  - Returns ok/errors + normalized units
- `validate_design_results(path) -> ValidationReport`
  - Confirms required keys + schema_version

### Detailing + Outputs
- `compute_detailing(design_results, *, config=None) -> BeamDetailingResult`
  - Wrapper around `detailing.create_beam_detailing`
- `compute_bbs(detailing_list, *, project_name="Beam BBS") -> BBSDocument`
  - Wrapper around `bbs.generate_bbs_document`
- `export_bbs(doc, *, path, fmt="csv|json") -> Path`
  - Wrapper around `bbs.export_bbs_to_csv/json`
- `compute_dxf(detailing_list, *, output, multi=False, **opts) -> Path`
  - Wrapper around `dxf_export.generate_beam_dxf` / `generate_multi_beam_dxf`

### Reports
- `compute_report(source, *, format="html|json", **opts) -> ReportResult`
  - Wrapper around `report.py`
- `compute_critical(job_out, *, top=10, format="csv|html") -> CriticalSet`
  - Wrapper around `critical` logic in CLI/report module

---

## CLI Additions (Thin Wrappers)

These are convenience commands for library users, not new features.

- `validate <job.json|results.json>` → schema + units checks
- `detail <results.json>` → detailing JSON output
- `bbs <results.json>` → schedule CSV/JSON
- `dxf <results.json>` → drawings DXF (already exists)
- `report <job_out|results.json>` → HTML/JSON (already exists)
- `critical <job_out>` → top-N CSV/HTML (already exists)

---

## Work Bundles (one focused pass each)

### Bundle A — API Contract + Docs
- Define stable function list + signatures.
- Document in `docs/reference/api.md` and `docs/cookbook/python-recipes.md`.

### Bundle B — Validation APIs + CLI
- Implement `validate_job_spec` + `validate_design_results`.
- Add `validate` CLI subcommand.

### Bundle C — Detailing + Output APIs
- Implement `compute_detailing`, `compute_bbs`, `export_bbs`.
- Add `detail` CLI subcommand.

### Bundle D — DXF + Report APIs
- Implement `compute_dxf`, `compute_report`, `compute_critical`.
- Ensure CLI uses these wrappers (no behavior change).

### Bundle E — Tests + Stability
- API unit tests.
- CLI smoke tests for `validate` + `detail`.
- Update `docs/reference/api-stability.md` with stable/experimental labels.

---

## Suggested Order
Bundle A → Bundle B → Bundle C → Bundle D → Bundle E

This keeps contracts stable before adding commands.
