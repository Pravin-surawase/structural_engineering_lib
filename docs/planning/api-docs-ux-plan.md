# API and CLI Docs UX Plan

Goal: Make public commands and APIs professional, accurate, and easy to use.

Scope
- CLI: `python -m structural_lib` commands and help text.
- Public Python API: `structural_lib/api.py` and module-level functions used in docs.
- Docs: `docs/cookbook/python-recipes.md`, key getting-started pages, and API reference.

Non-goals
- No new features or refactors.
- No breaking API changes unless explicitly approved.
- No VBA parity changes in this pass.

Principles
- Explicit units and assumptions.
- Required vs optional parameters are clear.
- Examples are copy-paste runnable.
- Errors are actionable for users.
- Consistent naming across CLI, API, and docs.

Phases
0) Inventory and baseline
   - List public entrypoints and their current signatures.
   - Map docs and examples to each entrypoint.
1) CLI pass
   - Review help output and usage examples.
   - Update doc examples to match actual CLI flags.
2) Python API pass
   - Review docstrings and parameter names.
   - Add minimal usage examples with correct units.
3) Cookbook pass
   - Fix example signatures and outputs.
4) Cross-link and consistency scan
   - Ensure docs align with code and versions.
5) Wrap-up
   - Summarize changes and update session log.

Checklist
- [x] Phase 0: Inventory entrypoints and doc references.
- [x] Phase 1: CLI help and example alignment.
- [x] Phase 2: Python API docstrings and examples.
- [x] Phase 3: Cookbook fixes.
- [x] Phase 4: Cross-link and consistency scan.
- [x] Phase 5: Wrap-up notes in session log.

Status
- 2025-12-27: Phase 0 inventory completed.
- 2025-12-27: Phase 1 complete (CLI reference aligned with actual CLI behavior).
- 2025-12-27: Phase 2 complete (API docstrings updated with args, returns, examples).
- 2025-12-27: Phase 3 complete (python-recipes aligned with real signatures).
- 2025-12-27: Phase 4 complete (docs examples synced to real functions).
- 2025-12-27: Phase 5 complete (session log updated).

Phase 0 Inventory
CLI entrypoints
- `Python/structural_lib/__main__.py`: unified CLI (`design`, `bbs`, `dxf`, `job`).
- `Python/structural_lib/job_cli.py`: legacy job runner CLI (`run --job --out`).
- `Python/structural_lib/excel_integration.py`: legacy CLI for CSV/JSON + DXF.
- `Python/structural_lib/dxf_export.py`: legacy DXF CLI.

Public Python API (`Python/structural_lib/api.py`)
- `get_library_version()`
- `check_beam_ductility(...)`
- `check_deflection_span_depth(...)`
- `check_crack_width(...)`
- `check_compliance_report(...)`
- `design_beam_is456(...)`
- `check_beam_is456(...)`
- `detail_beam_is456(...)`

Docs that mention CLI/API usage (primary)
- CLI: `docs/README.md`, `docs/reference/api.md`, `docs/cookbook/cli-reference.md`,
  `docs/getting-started/beginners-guide.md`, `docs/getting-started/python-quickstart.md`.
- Legacy CLI mentions: `docs/specs/ETABS_INTEGRATION.md`, `docs/specs/v0.9_JOB_SCHEMA.md`,
  `docs/RELEASES.md`, `docs/planning/current-state-and-goals.md`, `docs/TASKS.md`.
