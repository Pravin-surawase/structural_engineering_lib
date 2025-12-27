# Python Quickstart (Beginner-Friendly)

This guide shows how to install, run, and verify the Python library with simple, copy‑paste steps. No prior packaging experience required.

> **📚 New to this?** See [beginners-guide.md](beginners-guide.md) for comprehensive step-by-step instructions with explanations.

## Recommended for early adopters (no repo clone)

If you're sharing with a few users while the project is still evolving, this is the simplest path.

```bash
python3 -m pip install --upgrade pip

# Pin to a released tag for stability (recommended)
python3 -m pip install "structural-lib-is456 @ git+https://github.com/Pravin-surawase/structural_engineering_lib.git@v0.9.4#subdirectory=Python"

# With DXF support
python3 -m pip install "structural-lib-is456[dxf] @ git+https://github.com/Pravin-surawase/structural_engineering_lib.git@v0.9.4#subdirectory=Python"
```

Engineering note: this library is a calculation aid; final responsibility for code-compliant design and detailing remains with the qualified engineer.

## Google Colab quick install

```python
%pip install -q "structural-lib-is456[dxf] @ git+https://github.com/Pravin-surawase/structural_engineering_lib.git@v0.9.4#subdirectory=Python"
```

Then: `Runtime > Restart runtime` and rerun.

---

## 1) Install Python and set up a virtual environment
1. Ensure Python 3.9+ is installed (`python3 --version`).
2. From the repo root:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
3. Upgrade pip and install the library in editable mode with dev tools:
   ```bash
   pip install --upgrade pip
   pip install -e Python/.[dev]
   ```
   - DXF export needs `ezdxf` (optional): `pip install ezdxf`

## 2) Run the unit tests (sanity check)
```bash
python3 -m pytest Python/tests -q
```
All tests should pass. If `ezdxf` is missing, DXF-specific tests are skipped.

## 3) Use the library in a script (flexure + detailing)
Create a file `example.py` (or use a Python REPL):
```python
from structural_lib import flexure, detailing

# Design a singly reinforced beam (230x500, Mu = 150 kN·m, M25/Fe415)
res = flexure.design_singly_reinforced(
    b=230, d=450, d_total=500, mu_knm=150, fck=25, fy=415
)
print("Status:", "OK" if res.is_safe else res.error_message)
print("Ast required (mm²):", round(res.ast_required, 1))

# Detailing helpers
ld = detailing.calculate_development_length(bar_dia=16, fck=25, fy=415)
lap = detailing.calculate_lap_length(bar_dia=16, fck=25, fy=415, is_seismic=False)
print("Ld (mm):", ld, " Lap length (mm):", lap)
```
Run it:
```bash
python3 example.py
```

## 4) Batch process CSV/JSON using the unified CLI
The library provides a unified CLI for all operations:
```bash
# Design beams from CSV
python3 -m structural_lib design path/to/beams.csv -o results.json

# Generate bar bending schedule
python3 -m structural_lib bbs results.json -o schedule.csv

# Generate DXF drawings (requires ezdxf)
python3 -m structural_lib dxf results.json -o drawings.dxf

# Run complete job from spec file
python3 -m structural_lib job job.json -o ./output
```
- Input columns: `BeamID, Story, b, D, Span, Cover, fck, fy, Mu, Vu, Ast_req, Stirrup_Dia, Stirrup_Spacing` (case-insensitive).
- Outputs:
  - `results.json` — Design results with compliance status.
  - `schedule.csv` — Bar bending schedule per IS 2502.
  - DXF files (if `ezdxf` available).

## 5) Minimal “one-liner” example (no files)
```bash
python3 - <<'PY'
from structural_lib import shear
res = shear.design_shear(vu_kn=100, b=300, d=500, fck=25, fy=415, asv=100, pt=0.75)
print("Shear OK?", res.is_safe, "Spacing (mm):", res.spacing)
PY
```

## 6) Packaging notes
- Local editable install is usually enough. To build a wheel: `cd Python && python3 -m build`.
- Current code version is defined in `Python/structural_lib/__init__.py` (sync with `pyproject.toml` before publishing).

## 7) Troubleshooting
- “Module not found”: ensure the venv is activated and you ran `pip install -e Python/.`.
- DXF generation missing: install `ezdxf` (`pip install ezdxf`).
- Tests failing on path issues: run commands from the repo root.
## 8) Sample Files & Examples
- `Python/examples/simple_examples.py` - 7 beginner examples with explanations
- `Python/examples/complete_beam_design.py` - Full design workflow
- `Python/examples/sample_beam_design.csv` - Simple 5-beam sample
- `Python/examples/sample_building_beams.csv` - Complete 12-beam building

## 9) Further Reading
- [beginners-guide.md](beginners-guide.md) - Comprehensive tutorial (Python + Excel)
- [excel-tutorial.md](excel-tutorial.md) - Step-by-step Excel guide
- [../reference/api.md](../reference/api.md) - Full API documentation
- [../reference/is456-formulas.md](../reference/is456-formulas.md) - IS 456 code reference