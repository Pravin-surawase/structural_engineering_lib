---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: beginner
tags: [python, cli, beam, external-user]
---

# User Guide — Beam Workflow

**Type:** Guide
**Audience:** Users
**Status:** Active
**Importance:** High
**Version:** 0.24.0
**Last Updated:** 2026-08-28

This guide takes a new user from a clean installation to design results, a bar
bending schedule, detailing JSON, and a review report. Start with the
[Python quick start](python-quickstart.md) if you want a single calculation
without files.

## 1. Install and verify

StructLib 0.24.0 requires Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python3 -m pip install --upgrade pip
python3 -m pip install "structural-lib-is456==0.24.0"
python3 -m structural_lib install-preflight
```

The preflight must report version `0.24.0` and a package origin inside the
active environment's `site-packages` directory.

## 2. Create strict beam input

Create `beams.csv` with these exact columns and rows:

```csv
BeamID,Story,b,D,eff_d,Span,Cover,fck,fy,Mu,Vu,Stirrup_Dia,Stirrup_Spacing
B1,Ground,300,500,450,4000,40,25,500,150,100,8,150
B2,Ground,230,450,400,3500,40,20,415,80,75,8,175
B3,First,350,600,550,5000,40,30,500,250,150,10,125
```

All dimensions are millimetres, actions are kN/kN·m, and material strengths
are N/mm². `Ast_req`, `Asc_req`, and `Status` are outputs and are not valid
input columns. Any unknown, missing, duplicate, malformed, non-finite, or
mixed-validity row blocks the whole file before calculation.

## 3. Run design and exports

```bash
python3 -m structural_lib design beams.csv -o results.json
python3 -m structural_lib detail results.json -o detailing.json
python3 -m structural_lib bbs results.json -o schedule.csv
python3 -m structural_lib report results.json --format=html -o report.html
```

These commands create:

| File | Purpose |
|---|---|
| `results.json` | Inputs, flexure/shear results, provenance, and result envelope |
| `detailing.json` | Selected bars, stirrups, development/lap data, and zones |
| `schedule.csv` | Bar marks, diameters, lengths, quantities, and weights |
| `report.html` | Human-readable review artifact |

For DXF output:

```bash
python3 -m pip install "structural-lib-is456[dxf]==0.24.0"
python3 -m structural_lib dxf results.json -o drawings.dxf
```

## 4. Inspect the result

Create `inspect_results.py` with this content so the check works on Windows,
macOS, and Linux:

```python
import json
from pathlib import Path

result = json.loads(Path("results.json").read_text(encoding="utf-8"))
print(result["summary"])
for member in result["beams"]:
    envelope = member["result_envelope"]
    print(
        member["beam_id"],
        envelope["engineering_status"],
        member["governing_check"],
        round(member["governing_utilization"], 3),
    )
```

Run it:

```bash
python3 inspect_results.py  # Windows: py inspect_results.py
```

A calculation can complete with `PASS`, `FAIL`, or `HOLD`. Do not treat file
creation or intake validity as an engineering pass.

## 5. Use the canonical Python facade

```python
from structural_lib.design.is456 import beam

request = beam.input(
    member_id="B1",
    story="GF",
    case_id="ULS-1",
    span_mm=5000,
    b_mm=300,
    D_mm=550,
    d_mm=500,
    fck_nmm2=25,
    fy_nmm2=500,
    mu_knm=150,
    vu_kn=80,
    d_dash_mm=50,
    asv_mm2=100,
    source_provenance="analysis-envelope:ULS-1",
)
result = beam.design(request)

print(result.intake_status)
print(result.calculation_status)
print(result.engineering_status)
print(result.calculation.flexure.Ast_required)
```

For detailing and BBS composition, use the
[canonical beam recipe](../cookbook/python/beam.md). For columns, slabs,
footings, walls, staircases, deep beams, flat slabs, and torsion, choose a
recipe from the [family facade cookbook](../cookbook/python/family-facades.md).

## 6. Use maintained source examples

Repository examples are not included in the wheel. Clone the repository and
open the [Python examples guide on
GitHub](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/Python/examples/README.md).

The strict CLI sample is `sample_beam_design.csv`. The similarly named
`sample_building_beams.csv` belongs only to the educational
`complete_beam_design.py` script and is intentionally not strict CLI input.

## 7. Troubleshooting and help

```bash
python3 -m structural_lib --help
python3 -m structural_lib design --help
python3 -m structural_lib install-preflight
```

- [Troubleshooting](../reference/troubleshooting.md)
- [Public Python API](../reference/api.md)
- [Current release](release-status.md)
- [Append-only release ledger](releases.md)
- [Ask a question](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new?template=support.yml)
- [Report a bug](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new?template=bug_report.yml)

## Engineering boundary

StructLib is a design aid with case-qualified supported scope. Review source
actions, geometry, materials, assumptions, limitations, `PASS`/`FAIL`/`HOLD`
status, and outputs independently with a qualified structural engineer before
engineering or construction use.
