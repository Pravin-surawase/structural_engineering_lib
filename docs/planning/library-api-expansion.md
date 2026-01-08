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

## Future Required Functions (v0.17+)

These are **library-first helpers** to power interactive UI and professional
visuals. They return structured data only (no rendering, no UI code).
All functions live in `structural_lib.api` and must require explicit units.

### Visualization Data (2D/3D Ready)
- `compute_beam_geometry(*, units: str, b_mm: float, D_mm: float, cover_mm: float, span_mm: float) -> BeamGeometry`
  - Normalized geometry for previews and diagrams
- `compute_rebar_layout(*, units: str, b_mm: float, D_mm: float, cover_mm: float, bars: list[BarSpec]) -> RebarLayout`
  - Coordinates, bar marks, and clear spacing for drawings
- `compute_bmd_sfd(*, units: str, span_mm: float, loads: list[LoadCase]) -> LoadDiagramResult`
  - BMD/SFD arrays + key points (supports charts and reports)
- `compute_section_properties(*, units: str, b_mm: float, D_mm: float) -> SectionProperties`
  - Area, I, Z, neutral axis, and derived metrics
- `build_preview_payload(*, units: str, inputs: BeamInput) -> PreviewPayload`
  - Compact payload for live preview (safe even before full analysis)

### Variants and Exploration
- `generate_design_variants(*, units: str, base_inputs: BeamInput, limits: VariantLimits) -> list[DesignVariant]`
  - Deterministic variant generation for comparison UI
- `evaluate_variants(*, units: str, variants: list[DesignVariant]) -> list[VariantScore]`
  - Scores on safety, cost, constructability, and compliance
- `sensitivity_analysis(*, units: str, inputs: BeamInput, params: list[str]) -> SensitivityResult`
  - Local sensitivity for "play with beams" workflows
- `compare_designs(*, units: str, a: BeamDesignOutput, b: BeamDesignOutput) -> ComparisonResult`
  - Field-by-field comparison plus deltas and winners

### Traceability and Explanations
- `list_clause_checks(*, units: str, result: BeamDesignOutput) -> list[ClauseCheck]`
  - Clause references with pass/fail and brief rationale
- `explain_design(*, units: str, result: BeamDesignOutput) -> ExplanationResult`
  - Structured explanation (inputs, governing checks, key ratios)
- `get_clause_reference(*, clause_id: str) -> ClauseReference`
  - Retrieve clause text and metadata (code-clause database)

### Fast UI Utilities (Deterministic, No I/O)
- `validate_inputs_quick(*, units: str, inputs: BeamInput) -> ValidationSummary`
  - Lightweight validation for interactive sliders
- `estimate_cost_quick(*, units: str, inputs: BeamInput) -> CostEstimate`
  - Fast cost proxy for live previews (not final costing)
- `derive_default_inputs(*, units: str, context: DesignContext) -> BeamInput`
  - Smart defaults based on typical spans/materials

**Notes:**
- These functions do **not** replace core math; they expose structured data.
- Any new dataclasses should live in `structural_lib/types.py` (or similar).
- Keep results deterministic and testable; no caching or side effects.
- Compatibility checklist: `docs/planning/data-model-compatibility-checklist.md`

---

## Milestones, Owners, and Tests (Future API List)

**Milestone A: Visualization Data Foundations**
- **Scope:** compute_beam_geometry, compute_rebar_layout, compute_bmd_sfd, compute_section_properties
- **Owner:** DEV
- **Tests:** unit tests for each output field + one integration test per function
- **Docs:** update `docs/reference/api.md` (planned section) + `docs/cookbook/python-recipes.md`

**Milestone B: Preview Payload + Quick Utilities**
- **Scope:** build_preview_payload, validate_inputs_quick, estimate_cost_quick, derive_default_inputs
- **Owner:** DEV + TESTER
- **Tests:** fast validation suite + determinism checks
- **Docs:** usage examples for "live preview" workflows

**Milestone C: Exploration + Sensitivity**
- **Scope:** generate_design_variants, evaluate_variants, sensitivity_analysis, compare_designs
- **Owner:** DEV + TESTER
- **Tests:** reproducibility + ranking consistency + boundary behavior
- **Docs:** comparison/sensitivity examples with expected outputs

**Milestone D: Traceability + Explanations**
- **Scope:** list_clause_checks, explain_design, get_clause_reference
- **Owner:** DEV + DOCS
- **Tests:** clause mapping coverage + schema validation
- **Docs:** clause traceability guide and API reference updates

---

## Draft Data Models (Proposed, v0.17+)

These dataclasses are **drafts** to support the planned APIs. Final fields may evolve.

### BeamGeometry
- `span_mm: float`
- `b_mm: float`
- `D_mm: float`
- `cover_mm: float`
- `d_mm: float`
- `effective_span_mm: float`

### RebarLayout
- `bars: list[BarSpec]`
- `positions_mm: list[tuple[float, float]]`
- `clear_spacing_mm: float`
- `cover_mm: float`

### LoadDiagramResult
- `positions_mm: list[float]`
- `bmd_knm: list[float]`
- `sfd_kn: list[float]`
- `critical_points: list[CriticalPoint]`

### SectionProperties
- `area_mm2: float`
- `ixx_mm4: float`
- `zxx_mm3: float`
- `neutral_axis_mm: float`

### PreviewPayload
- `geometry: BeamGeometry`
- `rebar: RebarLayout | None`
- `bmd: LoadDiagramResult | None`
- `checks: list[ClauseCheck]`
- `status: str`

### ValidationSummary
- `is_valid: bool`
- `issues: list[ValidationIssue]`

### CostEstimate
- `material_cost: float`
- `labor_cost: float`
- `total_cost: float`

### SensitivityResult
- `parameter: str`
- `delta_inputs: dict[str, float]`
- `delta_outputs: dict[str, float]`

### ComparisonResult
- `summary: str`
- `deltas: dict[str, float]`
- `winner: str`

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
