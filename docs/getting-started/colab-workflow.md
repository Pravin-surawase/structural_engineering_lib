---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: beginner
tags: [colab, python, cli, beam]
---

# Google Colab Workflow

**Type:** Guide
**Audience:** Users
**Status:** Active
**Importance:** Medium
**Version:** 0.24.0
**Last Updated:** 2026-08-28

This guide runs the published package in a clean Google Colab runtime. It does
not require ETABS or a repository clone.

## 1. Install the exact release

Run this in the first cell:

```python
%pip install -q "structural-lib-is456[dxf]==0.24.0"
```

Choose **Runtime → Restart session**, then verify the environment:

```python
!python -m structural_lib install-preflight
```

The output must show `structural_lib: 0.24.0` and a package origin under
`site-packages`.

## 2. Run a canonical beam calculation

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
    source_provenance="colab:ULS-1",
)
result = beam.design(request)

print("Intake:", result.intake_status)
print("Calculation:", result.calculation_status)
print("Engineering:", result.engineering_status)
print("Ast required (mm²):", round(result.calculation.flexure.Ast_required))
```

Expected engineering status for this supplied case: `PASS`.

## 3. Create strict CLI input

```python
from pathlib import Path

Path("beams.csv").write_text(
    """BeamID,Story,b,D,eff_d,Span,Cover,fck,fy,Mu,Vu,Stirrup_Dia,Stirrup_Spacing
B1,Ground,300,500,450,4000,40,25,500,150,100,8,150
B2,Ground,230,450,400,3500,40,20,415,80,75,8,175
B3,First,350,600,550,5000,40,30,500,250,150,10,125
""",
    encoding="utf-8",
)
```

The CLI treats requested/reported steel and status as outputs. Do not add
`Ast_req`, `Asc_req`, or `Status` to this input.

## 4. Run design, BBS, detailing, DXF, and report

```python
!python -m structural_lib design beams.csv -o results.json
!python -m structural_lib detail results.json -o detailing.json
!python -m structural_lib bbs results.json -o schedule.csv
!python -m structural_lib dxf results.json -o drawings.dxf
!python -m structural_lib report results.json --format=html -o report.html
```

Any malformed or mixed-validity row blocks the full design command and returns a
non-zero exit code. Fix the input instead of using a partial output.

## 5. Inspect and download outputs

```python
import json
from pathlib import Path

data = json.loads(Path("results.json").read_text(encoding="utf-8"))
print(data["summary"])
for member in data["beams"]:
    print(
        member["beam_id"],
        member["result_envelope"]["engineering_status"],
        member["governing_check"],
        round(member["governing_utilization"], 3),
    )
```

Download artifacts from the Colab Files panel, or run:

```python
from google.colab import files

for name in [
    "results.json",
    "detailing.json",
    "schedule.csv",
    "drawings.dxf",
    "report.html",
]:
    files.download(name)
```

## 6. Continue with other families

Use the [family facade cookbook](../cookbook/python/family-facades.md) for
copy-paste column, slab, footing, wall, staircase, deep-beam, flat-slab, and
torsion journeys. For a repository-based single-file demonstration, see
[`Python/examples/colab_workflow.py`](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/Python/examples/colab_workflow.py).

## Engineering boundary

A successful Colab run demonstrates installed software behavior for the
supplied case. It is not complete-code coverage, an independent calculation,
professional approval, or authorization for construction use.
