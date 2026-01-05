# IS 456 RC Beam Design Library

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/structural-lib-is456.svg)](https://pypi.org/project/structural-lib-is456/)
[![Python tests](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Run ETABS beam exports through IS 456 checks/design and get compliant rebar + DXF + schedules in minutes. Now with advisory insights for design validation.**

## Quick Links

📚 [Documentation](docs/README.md) • 🚀 [Quick Start](#quick-start) • 💡 [Examples](Python/examples/) • 🔧 [API Reference](docs/reference/api.md) • 📊 [Insights Guide](docs/getting-started/insights-guide.md) • 🤖 [AI Summary](llms.txt)

</div>

---

## At a glance

- **Scope:** Beam-only IS 456 RC design library (Python + VBA parity)
- **Outputs:** Deterministic, auditable `results.json`, `schedule.csv`, `drawings.dxf`, HTML reports
- **Automation:** Batch-ready CLI + public API wrappers for validation/detailing/export
- **Insights:** Advisory precheck, sensitivity analysis, constructability scoring (preview)

---

## Features

### Core Capabilities
- **Design & Compliance:** Flexure, shear, serviceability (deflection Level A+B, crack width) per IS 456:2000
- **Detailing:** Bar layouts, stirrup configuration, development/lap lengths per IS 13920
- **Bar Bending Schedule:** IS 2502-compliant CSV/JSON with weights, cut lengths, bar marks
- **DXF Export:** CAD-ready reinforcement drawings with title blocks and annotations
- **Batch Processing:** CSV/JSON job runner for 100+ beams, critical set reports, HTML summaries

### Advisory Tools (Preview - v0.13.0+)
- **Quick Precheck:** Heuristic validation (deflection risk, width adequacy, steel estimates) in <1ms
- **Sensitivity Analysis:** Identify critical parameters (depth, width, fck) with normalized coefficients
- **Constructability Scoring:** 0-100 scale based on bar spacing, stirrup spacing, layer count, standard sizes

### Quality & Trust
- **Deterministic:** Same input → same output (JSON/CSV/DXF) across runs
- **Tested:** ~2,000 tests, ~92% branch coverage, 10 insights benchmark cases
- **Traceable:** IS 456 clause references in design formulas
- **Dual Implementation:** Python + VBA with matching I/O

---

## Status

🚀 **Active (v0.14.0)** — Published on PyPI. Unified CLI + design + detailing + DXF export + serviceability (Level A+B).

**What's new in v0.14.0:**
- **Advisory Insights Module (Preview):** `quick_precheck()`, `sensitivity_analysis()`, `calculate_constructability_score()` for design validation and parameter sensitivity. CLI: `--insights` flag.
- **Insights Verification Pack:** 10 benchmark cases with automated regression tests for insights accuracy.
- **Library-first API wrappers:** `validate_*`, `compute_detailing`, `compute_bbs`, `export_bbs`, `compute_dxf`, `compute_report`, `compute_critical`.
- **New CLI helpers:** `validate` for schema checks and `detail` for detailing JSON export.
- **DXF/BBS quality gates:** bar mark consistency checks, DXF content tests, title block context.

See [CHANGELOG.md](CHANGELOG.md) for full release history.

**Stability note:** While in active development, prefer pinning to a release version (example: `structural-lib-is456==0.14.0`).

## Quick Start

### 1) Install

```bash
# Base install
pip install structural-lib-is456

# With DXF export support (recommended)
pip install "structural-lib-is456[dxf]"
```

Colab:
```python
%pip install -q "structural-lib-is456[dxf]"
```

> **Naming:** Install `structural-lib-is456` · Import `structural_lib` · CLI `python3 -m structural_lib`

### 2) API in 30 seconds

```bash
python3 - <<'PY'
from structural_lib import flexure
res = flexure.design_singly_reinforced(
    b=300, d=450, d_total=500, mu_knm=150, fck=25, fy=500
)
print(f"Ast required: {res.ast_required:.0f} mm^2 | Status: {'OK' if res.is_safe else res.error_message}")
PY
```

Example output:
```
Ast required: 942 mm^2 | Status: OK
```
Exact Ast (mm²) may vary slightly by version due to rounding/table refinements.

### 3) CLI pipeline (CSV -> detailing -> BBS -> DXF)

Required for design (case-insensitive): `BeamID, Story, b, D, Span, Cover, fck, fy, Mu, Vu`
Optional overrides (used by `detail` / forced detailing): `Ast_req, Asc_req, Stirrup_Dia, Stirrup_Spacing`

PyPI (no clone):
```bash
pip install "structural-lib-is456[dxf]"
python3 -m structural_lib design input.csv -o results.json
python3 -m structural_lib detail results.json -o detailing.json
python3 -m structural_lib bbs results.json -o schedule.csv
python3 -m structural_lib dxf results.json -o drawings.dxf
```

Repo dev (editable install):
```bash
cd Python
python3 -m pip install -e ".[dxf]"

python3 -m structural_lib design examples/sample_beam_design.csv -o results.json
python3 -m structural_lib detail results.json -o detailing.json
python3 -m structural_lib bbs results.json -o schedule.csv
python3 -m structural_lib dxf results.json -o drawings.dxf
```

Optional review outputs:
```bash
python3 -m structural_lib report results.json --format=html -o report/ --batch-threshold 80
```

Optional schema validation:
```bash
python3 -m structural_lib validate results.json
```

Optional insights analysis:
```bash
python3 -m structural_lib design input.csv -o results.json --insights
# Creates: results.json + <output_stem>_insights.json
# Example: -o results.json         -> results_insights.json
# Example: -o results_insights.json -> results_insights_insights.json
# Note: CLI insights currently export precheck + sensitivity + robustness;
# constructability may be null until CLI integration is completed.
```

Design writes per-beam status in `results.json`; failed beams are flagged with `is_safe=false` (plus an error message).

ETABS exports can be normalized into this schema. See `docs/specs/ETABS_INTEGRATION.md` for the mapping rules.

---

## How it works

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         IS 456 DESIGN PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   CSV/JSON ──► Design ──► Compliance ──► Detailing ──► DXF/Schedule    │
│      │           │            │             │              │            │
│   ETABS      Flexure      Strength      Bar Layout     Drawings        │
│   Import      Shear     Serviceability   Stirrups       BBS            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Highlights**
- End-to-end pipeline from input -> design -> detailing -> DXF/BBS
- Governing-case traceability with utilization summaries
- Dual implementation (VBA + Python) with matching inputs/outputs
- Unified CLI for batch automation

## Outputs

| Output | Format | Description |
|--------|--------|-------------|
| Design results | JSON | Strength + serviceability checks per beam/case |
| Detailing output | JSON | Bars/stirrups + Ld/lap from design results |
| Bar bending schedule | CSV | IS 2502 columns with weights and cut lengths |
| DXF drawings | DXF | CAD-ready reinforcement drawings |
| Critical set | CSV/HTML | Sorted utilization table from job outputs |
| Visual reports | HTML/JSON | Report with SVG, sanity heatmap, scorecard |

## Public API surface (stable wrappers)

See `docs/reference/api-stability.md` for stability labels and guarantees.

| Function | Purpose |
|----------|---------|
| `api.validate_job_spec(path)` | Validate job JSON against schema |
| `api.validate_design_results(path)` | Validate results JSON against schema |
| `api.compute_detailing(results)` | Detailing from design results (bars, stirrups, Ld/lap) |
| `api.compute_bbs(detailing)` | BBS rows from detailing data |
| `api.export_bbs(bbs, path)` | Write BBS to CSV |
| `api.compute_dxf(results)` | DXF drawing data from results |
| `api.compute_report(results_or_job)` | Report data from results/job output |
| `api.compute_critical(job_output)` | Critical set table from job output |

## Trust & Verification

| Aspect | Status |
|--------|--------|
| **Determinism** | Same input -> same output (JSON/CSV/DXF) across runs |
| **Units** | Explicit: mm, N/mm^2, kN, kN*m — converted at layer boundaries |
| **Test coverage** | ~2,000 tests, ~92% branch coverage (see CI for current) |
| **Clause traceability** | Core design formulas reference IS 456 clause/table |
| **Verification pack** | Benchmark examples in `Python/examples/` + insights verification pack (10 cases) |
| **Performance** | Quick precheck: <1ms, Full design: ~200-500ms/beam, Batch 100 beams: <1 min |

## Who it helps

- Consultants running 100+ beams from ETABS exports
- Detailers generating DXF + schedules quickly
- Students verifying hand calculations and code limits

## Scope / Non-goals

- ✅ Beam design and detailing per IS 456
- ✅ Batch automation (CSV/JSON -> outputs)
- ❌ Not a full building design tool (columns, slabs, foundations out of scope)
- ❌ Not a replacement for engineer judgment

## VBA usage (Excel)

Import `.bas` files from `VBA/Modules/` or use the add-in in `Excel/StructEngLib.xlam`.

```vba
Sub DesignBeam()
    Dim result As Variant
    result = IS456_Design_Rectangular(300, 450, 50, 500, 150, 25, 415)
    If result(0) = "OK" Then
        Debug.Print "Ast required: " & result(1) & " mm^2"
    End If
End Sub
```

More in `VBA/Examples/Example_Usage.bas`.

## Batch job runner (JSON)

For automated pipelines, use the JSON job schema:

```bash
cat > job.json <<'JSON'
{
  "schema_version": 1,
  "code": "IS456",
  "units": "IS456",
  "job_id": "demo-001",
  "beam": {
    "b_mm": 230,
    "D_mm": 500,
    "d_mm": 450,
    "fck_nmm2": 25,
    "fy_nmm2": 500
  },
  "cases": [
    {"case_id": "ULS-1", "mu_knm": 120, "vu_kn": 90}
  ]
}
JSON

python3 -m structural_lib job job.json -o ./out_demo
python3 -m structural_lib critical ./out_demo --top 10 --format=csv -o critical.csv
python3 -m structural_lib report ./out_demo --format=html -o report.html
```

## Troubleshooting (quick fixes)

- CLI not found: use `python3 -m structural_lib --help` to avoid PATH issues
- Wrong Python env: prefer `.venv/bin/python` or `python3 -m pip`
- DXF export fails: install optional dependency with `pip install "structural-lib-is456[dxf]"`
- Schema errors: run `python3 -m structural_lib validate results.json`

## Documentation

**Getting Started:**
- [Beginner's Guide](docs/getting-started/beginners-guide.md) - Start here for first-time users
- [Python Quickstart](docs/getting-started/python-quickstart.md) - API usage examples
- [Insights Guide](docs/getting-started/insights-guide.md) - Advisory insights (precheck, sensitivity, constructability)

**Reference:**
- [CLI Reference](docs/cookbook/cli-reference.md) - All CLI commands
- [API Reference](docs/reference/api.md) - Function signatures and examples
- [Insights API Reference](docs/reference/insights-api.md) - Insights module technical reference
- [API Stability](docs/reference/api-stability.md) - Stability labels and versioning
- [Known Pitfalls](docs/reference/known-pitfalls.md) - Common issues and solutions

**Excel/VBA:**
- [Excel Quickstart](docs/getting-started/excel-quickstart.md)
- [Excel Tutorial](docs/getting-started/excel-tutorial.md)

**Verification:**
- [Validation Pack](docs/verification/validation-pack.md) - IS 456/SP:16 benchmark cases
- [Insights Verification Pack](docs/verification/insights-verification-pack.md) - Insights module regression tests

**Index:** [docs/README.md](docs/README.md) - Complete documentation index

## Community

- Contributing: `CONTRIBUTING.md`
- Support: `SUPPORT.md`
- Security: `SECURITY.md`

## Developer setup

| Task | Command | Where |
| --- | --- | --- |
| Install dev deps | `cd Python && python3 -m pip install -e ".[dev]"` | repo root |
| Install hooks | `pre-commit install` | repo root |
| Run tests | `cd Python && python3 -m pytest` | repo root |
| Format check | `cd Python && python3 -m black --check .` | repo root |
| Type check | `cd Python && python3 -m mypy` | repo root |
| Local CI check | `./scripts/ci_local.sh` | repo root |

## Directory structure

```
structural_engineering_lib/
├── VBA/           # VBA modules + tests
├── Python/        # Python package + tests + examples
├── Excel/         # Excel add-in and workbooks
├── scripts/       # Release and CI tooling
├── docs/          # Documentation
└── README.md
```

## License

MIT License — Free to use, modify, and distribute.

## References

- IS 456:2000 — Plain and Reinforced Concrete — Code of Practice
- SP:16-1980 — Design Aids for Reinforced Concrete to IS 456
- IS 13920:2016 — Ductile Design and Detailing of RC Structures

## Author

Pravin Surawase (GitHub: https://github.com/Pravin-surawase)
