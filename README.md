# IS 456 RC Beam Design Library

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/structural-lib-is456.svg)](https://pypi.org/project/structural-lib-is456/)
[![Python tests](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Run 500 ETABS beams → get compliant rebar + DXF + schedules in minutes.**

[Quick Start](#30-second-user-demo-no-clone-required) • [Documentation](docs/README.md) • [AI Summary](llms.txt) • [Examples](Python/examples/) • [API Reference](docs/reference/api.md)

</div>

---

## Status

🚀 **Active (v0.10.6)** — Now on PyPI! Unified CLI + strength design + detailing + DXF export + serviceability (Level A+B) + compliance + batch runner + cutting-stock optimizer.

**What's new in v0.10.6:**
- **Structured error schema:** Machine-readable `DesignError` with code/severity/hint/clause
- **Full input validation:** 16+ error codes covering all design functions
- **Doubly/flanged beam validation:** Structured errors in `design_doubly_reinforced()`, `design_flanged_beam()`
- **Improved CLI:** Better error messages for user-facing feedback

See [CHANGELOG.md](CHANGELOG.md) for full release history.

## What makes it different

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

| Feature | Description |
|---------|-------------|
| **End-to-end pipeline** | Design → Compliance → Detailing → Drawings (DXF) |
| **Governing-case traceability** | Utilization ratios + summary per load case |
| **Dual implementation** | VBA + Python with matching inputs/outputs |
| **Unified CLI** | Single command interface for all operations |

## Outputs you get

| Output | Format | Description |
|--------|--------|-------------|
| Reinforcement schedules | CSV/JSON | Bar callouts with weights |
| Detail drawings | DXF | CAD-ready bar layouts |
| Compliance reports | JSON | Strength + serviceability checks |
| Bar bending schedules | CSV | Per IS 2502 with cutting lengths |

## Who it helps

- Consultants running 100+ beams from ETABS exports
- Detailers generating DXF + schedules quickly
- Students verifying hand calculations and code limits

## Trust & Verification

| Aspect | Status |
|--------|--------|
| **Determinism** | Same input → same output (JSON/CSV/DXF) across runs and machines |
| **Units** | Explicit: mm, N/mm², kN, kN·m — converted at layer boundaries |
| **Test coverage** | 1900+ tests, 92% branch coverage (see CI for live status) |
| **Clause traceability** | Core design formulas reference IS 456 clause/table |
| **Verification pack** | Benchmark examples in [`Python/examples/`](Python/examples/) |

## What this is NOT

- ❌ **Not a full building design tool** — beams only (columns, slabs, foundations are out of scope)
- ❌ **Not a replacement for engineer judgment** — final responsibility remains with the qualified engineer

## Adoption (Early Users)

This repository is public, so anyone can read the code, docs, and examples.

- **Engineering note:** This library is a calculation aid. Final responsibility for code-compliant design, detailing, and drawing checks remains with the qualified engineer.
- **Stability note:** While in active development, prefer pinning to a release version (example: `structural-lib-is456==0.10.6`) rather than installing latest.

### Install from PyPI

```bash
# Base install
pip install structural-lib-is456

# With DXF export support (recommended)
pip install "structural-lib-is456[dxf]"
```

### Install (Google Colab)

```python
%pip install -q "structural-lib-is456[dxf]"
```

Then: `Runtime > Restart runtime` and rerun your notebook cells.

## 30-second user demo (no clone required)

Try the library immediately — no repo clone needed:

```bash
# 1. Install
python3 -m venv .venv && source .venv/bin/activate
pip install "structural-lib-is456[dxf]"

# 2. Design a beam (one-liner)
python3 - <<'PY'
from structural_lib import flexure
result = flexure.design_singly_reinforced(b=300, d=450, d_total=500, mu_knm=150, fck=25, fy=500)
print(f"Ast required: {result.ast_required:.0f} mm² | Status: {'OK' if result.is_safe else result.error_message}")
PY
```

Expected output:
```
Ast required: 942 mm² | Status: OK
```

## 60-second demo (CSV → schedule + DXF)

**For developers** — clone the repo and run the full pipeline:

- `Python/examples/sample_beam_design.csv`
- Required columns: `BeamID, Story, b, D, Span, Cover, fck, fy, Mu, Vu, Ast_req, Asc_req, Stirrup_Dia, Stirrup_Spacing` (case-insensitive)

Run the unified CLI:

```bash
cd Python
python3 -m pip install -e ".[dxf]"  # optional, for DXF export support

# Design beams from CSV
python3 -m structural_lib design examples/sample_beam_design.csv -o results.json

# Generate bar bending schedule
python3 -m structural_lib bbs results.json -o schedule.csv

# Generate DXF drawings (requires ezdxf)
python3 -m structural_lib dxf results.json -o drawings.dxf
```

Outputs:
- `results.json` — Design results with compliance status
- `schedule.csv` — Bar bending schedule per IS 2502
- `drawings.dxf` — CAD-ready reinforcement drawings

<details>
<summary><b>Sample BBS output (schedule.csv)</b></summary>

```csv
bar_mark,member_id,location,diameter_mm,no_of_bars,cut_length_mm,total_weight_kg,remarks
B1-01,B1,bottom-start,16,3,2600,12.33,Bottom start - 3-16φ
B1-02,B1,bottom-mid,16,4,3400,21.52,Bottom mid - 4-16φ
B1-03,B1,top-start,12,2,2000,3.56,Top start - 2-12φ
S1-01,B1,stirrup-start,8,11,1440,6.27,2L-8φ@100
S1-02,B1,stirrup-mid,8,15,1440,8.54,2L-8φ@150

SUMMARY: 5 items | Total weight: 52.22 kg
```

</details>

ETABS exports can be normalized into this schema. See `docs/architecture/project-overview.md` and `docs/specs/ETABS_INTEGRATION.md` for the ETABS CSV import flow.

## Advanced: Batch job runner

For automated pipelines, use the JSON job schema:

```bash
# Create a sample job file
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

# Run the job
python3 -m structural_lib job job.json -o ./out_demo
```

## Features

### Core Design
| Feature | Description |
|---------|-------------|
| ✅ **Limit state design** | As per IS 456:2000 |
| ✅ **Flexural design** | Singly, Doubly, and Flanged (T/L) beams |
| ✅ **Shear design** | Stirrup design with Table 19/20 lookup |
| ✅ **Ductile Detailing** | IS 13920:2016 checks (Geometry, Min/Max steel, Confinement) |
| ✅ **Serviceability** | Level A (span/depth) + Level B (curvature-based deflection) |

### Output Generation
| Feature | Description |
|---------|-------------|
| ✅ **Reinforcement detailing** | Bar patterns / drafting-ready schedules |
| ✅ **DXF export** | CAD drawings for reinforcement detailing |
| ✅ **Bar bending schedule** | Per IS 2502 with weights and cut lengths |
| ✅ **Cutting-stock optimizer** | Rebar nesting to minimize waste |

### Integration & Tooling
| Feature | Description |
|---------|-------------|
| ✅ **Unified CLI** | `python -m structural_lib` with design/bbs/dxf/job subcommands |
| ✅ **Batch runner** | Deterministic file-in/file-out (`job.json` → JSON/CSV) |
| ✅ **Compliance checker** | Multi-check summary (strength + serviceability) across load cases |
| ✅ **ETABS Integration** | Import CSV with header normalization and sign preservation |
| ✅ **Dual implementation** | VBA (Excel) + Python with identical API |
| ✅ **Pure functions** | No UI dependencies (no MsgBox, no worksheet access) |
| ✅ **Mac Compatible** | Hardened against Mac VBA stack corruption issues |

## 📚 Getting Started

**New to this library?** Start here:

- **[Beginner's Guide](docs/getting-started/beginners-guide.md)** — Complete tutorial covering Python AND Excel paths
- **[Python Quickstart](docs/getting-started/python-quickstart.md)** — Install, run, and verify in 5 minutes
- **[Excel Quickstart](docs/getting-started/excel-quickstart.md)** — Load the `.xlam` and try a function in 5 minutes
- **[Excel Tutorial](docs/getting-started/excel-tutorial.md)** — Step-by-step Excel/VBA guide with formulas
- **Sample files** in `Python/examples/` — Ready-to-run scripts and CSV data

## Community

- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Support: [SUPPORT.md](SUPPORT.md)
- Security: [SECURITY.md](SECURITY.md)

## Contributing (Dev Setup)

| Task | Command | Where |
| --- | --- | --- |
| Install dev deps | `cd Python && python3 -m pip install -e ".[dev]"` | repo root |
| Install hooks | `pre-commit install` | repo root |
| Run tests | `cd Python && python3 -m pytest` | repo root |
| Format check | `cd Python && python3 -m black --check .` | repo root |
| Type check | `cd Python && python3 -m mypy` | repo root |
| Local CI check (all checks + wheel import) | `./scripts/ci_local.sh` | repo root |

```bash
# Install dev dependencies
cd Python
python3 -m pip install -e ".[dev]"

# Install git hooks (recommended)
cd ..
pre-commit install

# Run checks locally
cd Python
python3 -m pytest
python3 -m black --check .
python3 -m mypy
```

## Install (Developers)

This repo is a monorepo; the Python package lives under `Python/`.

```bash
cd Python
python3 -m pip install -e .
```

Optional dependencies:

- DXF export (ezdxf):

```bash
cd Python
python3 -m pip install -e ".[dxf]"
```

## Scope

| Version | Features | Status |
|---------|----------|--------|
| **v0.1** | Rectangular beams, singly reinforced flexure, shear design | ✅ Completed |
| **v0.2** | Doubly reinforced flexure | ✅ Completed |
| **v0.3** | Flanged beams (T, L) | ✅ Completed |
| **v0.4** | IS 13920 ductile detailing, packaging | ✅ Completed |
| **v0.5** | Excel workbook integration | ✅ Completed |
| **v0.6** | ETABS Integration, Beam Schedule Generation | ✅ Completed |
| **v0.7** | Reinforcement Detailing, DXF Export | ✅ Completed |
| **v0.8** | Serviceability (deflection + crack width), Compliance checker | ✅ Completed |
| **v0.9** | Batch runner (job.json → JSON/CSV), docs + QA hardening | ✅ Completed |
| **v0.9.4** | Unified CLI, cutting-stock optimizer, VBA BBS/Compliance parity | ✅ Completed |
| **v0.9.5** | PyPI publishing, docs restructure, release hardening | ✅ Completed |
| **v0.9.6** | Verification pack, API docs UX, pre-release checklist | ✅ Completed |
| **v0.10.0** | Level B serviceability (curvature-based deflection), CLI help | ✅ Completed |
| **v0.10.1–0.10.3** | CLI serviceability flags, 45 critical IS 456 tests, governance docs | ✅ Completed |

## Directory Structure (current)

```
structural_engineering_lib/
├── VBA/
│   ├── Modules/            ← Core .bas modules (import into Excel)
│   └── Tests/              ← VBA test suites (Test_RunAll.bas)
├── Python/
│   ├── structural_lib/     ← Python package (flexure, shear, compliance, serviceability, pipeline, BBS, DXF, job runner)
│   ├── tests/
│   ├── examples/           ← Worked examples and sample data
│   └── scripts/            ← Utility scripts (bump_version.py)
├── Excel/                  ← Excel workbooks (see Excel/README.md)
├── scripts/                ← Release, version sync, and CI scripts
├── docs/
│   ├── README.md           ← Docs index (start here)
│   ├── reference/          ← API, formulas, troubleshooting
│   ├── getting-started/    ← Quickstart guides
│   ├── verification/       ← Benchmark examples
│   ├── TASKS.md            ← Task backlog and status
│   └── ...                 ← More folders (see docs/README.md)
├── agents/                 ← Role docs for AI prompts
├── logs/                   ← Runtime logs
├── CHANGELOG.md
└── README.md
```

## Using the VBA Library in Excel

### Method 1: Import .bas Files (Recommended)

1. Open your Excel workbook.
2. Press `Alt + F11` to open the VBA Editor.
3. Right-click on "VBAProject (YourWorkbook)" > Import File.
4. Select all `.bas` files from `VBA/Modules/`.
5. You can now use functions like `=IS456_MuLim(...)` directly in cells or call `Design_Singly_Reinforced` from your macros.

### Method 2: Excel Add-in (Recommended for Distribution)

1. Install the add-in: `Excel/StructEngLib.xlam` (or a GitHub Release asset, if published)
2. Functions available automatically in all workbooks

### Example Usage (VBA)

```vba
Sub DesignBeam()
    Dim result As Variant

    ' Design a beam: b=300, d=450, d'=50, D=500, Mu=150 kN·m, M25/Fe415
    result = IS456_Design_Rectangular(300, 450, 50, 500, 150, 25, 415)

    ' result is an array: [status, Ast, Asc, design_type, message]
    If result(0) = "OK" Then
        Debug.Print "Ast required: " & result(1) & " mm²"
    End If
End Sub
```

More worked examples in `VBA/Examples/Example_Usage.bas`.

## Using the Python Library

```python
from structural_lib import flexure

result = flexure.design_singly_reinforced(
    b=230,
    d=450,
    d_total=500,
    mu_knm=100,
    fck=20,
    fy=415,
)

if result.is_safe:
    print(f"Ast Required: {result.ast_required:.1f} mm²")
else:
    print(f"Design not safe: {result.error_message}")
```

### CLI Commands

```bash
# Full pipeline
python3 -m structural_lib design input.csv -o results.json
python3 -m structural_lib bbs results.json -o schedule.csv
python3 -m structural_lib dxf results.json -o drawings.dxf
python3 -m structural_lib job job.json -o ./output
```

For full options, inputs/outputs, and exit codes, see the [CLI Reference](docs/cookbook/cli-reference.md) or run:
`python3 -m structural_lib --help`

### Python API

| Module | Import | Purpose |
|--------|--------|--------|
| BBS | `from structural_lib.bbs import generate_bbs_from_detailing` | Bar bending schedule |
| DXF | `from structural_lib.dxf_export import generate_beam_dxf` | CAD drawings |
| CSV Import | `from structural_lib.excel_integration import load_beam_data_from_csv` | ETABS/CSV import |
| Cutting-stock | `from structural_lib.bbs import optimize_cutting_stock` | Stock-length nesting |
| Bar layout | `from structural_lib.rebar_optimizer import optimize_bar_arrangement` | Bar selection |

See [Python examples](Python/examples/) for complete workflows.

## Documentation

- **[Docs Index](docs/README.md)** — Start here (who should read what)
- **[CLI Reference](docs/cookbook/cli-reference.md)** — Full command list, inputs/outputs, examples
- **[AI Summary](llms.txt)** — Compact overview for tools and indexing
- **[Project Overview](docs/architecture/project-overview.md)** — High-level scope, architecture, and workflows
- **[Research and Findings (archived)](docs/_archive/RESEARCH_AND_FINDINGS.md)** — Historical research document with formulas, tables, and early API design notes
- **[API Reference](docs/reference/api.md)** — Public function signatures, inputs/outputs, units
- **[Development Guide](docs/contributing/development-guide.md)** — Coding standards, naming conventions, testing guidelines
- **[IS 456 Quick Reference](docs/reference/is456-formulas.md)** — Formulas cheat sheet for quick lookup
- **[Known Pitfalls](docs/reference/known-pitfalls.md)** — Common traps (units, tables, limits)

## Testing

| Platform | Command | Coverage |
|----------|---------|----------|
| Python | `python3 -m pytest Python/tests -q` | 1900+ tests, 92% branch coverage |
| VBA | `Test_RunAll.RunAllVBATests` in Excel VBA Editor | 9 test suites |

Run the full suite locally to verify:
```bash
cd Python && python3 -m pytest --cov=structural_lib --cov-fail-under=92
```

## Packaging

- Python: `cd Python && python3 -m build` (outputs to `Python/dist/`)

## References

- IS 456:2000 — Plain and Reinforced Concrete — Code of Practice
- SP:16-1980 — Design Aids for Reinforced Concrete to IS 456
- IS 13920:2016 — Ductile Design and Detailing of RC Structures

## License

MIT License — Free to use, modify, and distribute.

## Author

Pravin Surawase (GitHub: https://github.com/Pravin-surawase)
