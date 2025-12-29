# structural-lib-is456

IS 456 RC Beam Design Library (Python package).

**Version:** 0.10.7 (development preview)
**Status:** [![Python tests](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml)

> ⚠️ **Development Preview:** APIs may change until v1.0. For reproducible results, pin to a release tag.

For full project overview and usage examples, see the repository root `README.md`.

## Install

```bash
# Recommended (pinned to release tag)
pip install "structural-lib-is456 @ git+https://github.com/Pravin-surawase/structural_engineering_lib.git@v0.10.7#subdirectory=Python"

# With DXF support (pinned)
pip install "structural-lib-is456[dxf] @ git+https://github.com/Pravin-surawase/structural_engineering_lib.git@v0.10.7#subdirectory=Python"

# PyPI (latest — may differ from pinned tag)
pip install structural-lib-is456

# PyPI with DXF support
pip install "structural-lib-is456[dxf]"
```

## Quick Start: CLI Usage

The library provides a unified command-line interface:

```bash
# Run beam design from CSV input
python -m structural_lib design input.csv -o results.json

# Generate bar bending schedule
python -m structural_lib bbs results.json -o bbs.csv

# Generate DXF drawings (requires ezdxf)
python -m structural_lib dxf results.json -o drawings.dxf

# Run complete job from specification
python -m structural_lib job job.json -o output/
```

Run `python -m structural_lib --help` for more options.

## Quick Start: Python API

```python
from structural_lib import flexure, shear, api

# Single beam design
result = flexure.design_singly_reinforced(
    b=230, d=450, d_total=500, mu_knm=100, fck=25, fy=500
)
print(f"Ast required: {result.ast_required:.0f} mm²")

# Multi-case compliance check
report = api.check_beam_is456(
    units="IS456",
    b_mm=230, D_mm=500, d_mm=450,
    fck_nmm2=25, fy_nmm2=500,
    cases=[{"case_id": "ULS-1", "mu_knm": 100, "vu_kn": 80}]
)
print(f"Governing case: {report.governing_case_id}")
```

## New in v0.10.7

- **Critical Set export (V03):** `python -m structural_lib critical` writes sorted utilization tables (CSV/HTML) with `--top` slicing and `data-source` traces.
- **Report scaffolding (V01/V02):** `report.py` skeleton + `load_job_spec()` helper and `report` CLI stub to support Visual v0.11 deliverables.
- **Docs refresh:** Version sync + context updates for the Visual v0.11 rollout.
