# Deep Project Map (Python + VBA parity)

**Type:** Architecture
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Version:** 1.0.0
**Created:** 2025-12-20
**Last Updated:** 2026-01-13

---

**Project:** IS 456 RC Beam Design Library (Strength + detailing + DXF), with Python + VBA parity.

**Why this doc exists:** a single, layer-aware map of **what lives where**, **how data flows**, and **where to add the next features** (especially v0.8 serviceability) without breaking parity.

---

## 1) Repository topography (what each folder is)

- `Python/` — Python package (`structural_lib`) + tests + examples + packaging config.
- `VBA/` — VBA modules (core calc + Excel app layer + integration + detailing + DXF) + optional VBA tests.
- `Excel/` — flagship workbooks/add-in artifacts (`.xlsm`, `.xlam`).
- `docs/` — canonical documentation set (API contracts, pitfalls, tasks, specs, guides).
- `.github/` — CI workflows (Python tests/lint/typecheck, CodeQL).

---

## 2) Layered architecture (non-negotiable)

This repo enforces a layered architecture. Keep responsibilities separated:

1. **Core calculation layer (pure math):**
   - Deterministic.
   - Units explicit.
   - No file I/O, no Excel access, no UI.

2. **App/orchestration layer (workflow glue):**
   - Coordinates calls to core functions.
   - Validates / normalizes inputs.
   - Aggregates results into tabular outputs.

3. **UI / I-O layer:**
   - Excel UI (sheets, buttons) and integration (ETABS import).
   - Python CLI/scripts or batch utilities.

**Parity rule:** if a behavior is in the “core calculation” path in one language, it should be mirrored in the other (unless explicitly documented as a divergence).

---

## 3) End-to-end data flow

### 3.1 Excel/VBA workflow (flagship)

Source of truth mapping: `docs/specs/v0.7-data-mapping.md`.

```
ETABS CSV (optional)
   │
   ▼
BEAM_INPUT table (tbl_BeamInput)
   │  (geometry + materials + Mu/Vu)
   ▼
App layer reads rows
   │
   ├─▶ Flexure design (core)
   ├─▶ Shear design (core)
   └─▶ Ductility checks (core)
   ▼
BEAM_DESIGN table (tbl_BeamDesign)
   │  (Ast/Asc, stirrups, status, etc.)
   ▼
Detailing module
   │  (Ld/lap/arrangements)
   ▼
DXF export
   │
   ▼
Beam elevation + section drawings (DXF file)
```

Key VBA layers:
- Core calc: `VBA/Modules/M03_Tables.bas`, `M04_Utilities.bas`, `M05_Materials.bas`, `M06_Flexure.bas`, `M07_Shear.bas`, `M10_Ductile.bas`.
- App/orchestration: `VBA/Modules/M11_AppLayer.bas`.
- UI hooks: `VBA/Modules/M12_UI.bas`.
- Integration: `VBA/Modules/M13_Integration.bas`.
- Reporting/schedules: `VBA/Modules/M14_Reporting.bas`.
- Detailing + DXF: `VBA/Modules/M15_Detailing.bas`, `VBA/Modules/M16_DXF.bas`.

### 3.2 Python workflow (library + batch utilities)

Typical usage:

```
User script / batch runner
   │
   ├─▶ Flexure design
   ├─▶ Shear design
   ├─▶ Ductility checks
   ├─▶ Detailing (BeamDetailingResult)
   └─▶ DXF export (optional dependency)
```

Python module groups:
- Core calc: `Python/structural_lib/flexure.py`, `shear.py`, `ductile.py`, `tables.py`, `materials.py`, `utilities.py`.
- Types/contracts: `Python/structural_lib/types.py`.
- Detail + DXF: `Python/structural_lib/detailing.py`, `dxf_export.py`.
- I/O helpers: `Python/structural_lib/excel_integration.py`.
- Thin facade: `Python/structural_lib/api.py`.

---

## 4) Canonical units + conversion points

The library is strict about units because silent unit drift is the #1 failure mode.

- Geometry: **mm**
- Concrete/steel strengths: **N/mm²**
- Shear force: typically input/output as **kN** (convert to N internally when needed)
- Moment: typically input/output as **kN·m** (convert to N·mm internally when needed)

**Rule of thumb:**
- Convert *at the edge* of a function (input normalization) and keep core math consistent.
- Never accept “mixed” units without explicit parameters.

---

## 5) Core calculation responsibilities (Python ↔ VBA)

### 5.1 Tables (IS 456 Table 19/20)

Purpose: concrete shear capacity $\tau_c$ and max shear $\tau_{c,max}$.

Key policy constraints (parity-critical):
- Clamp percentage tension steel $p_t$ to **0.15%–3.0%**.
- Interpolate only in **$p_t$** within a grade column.
- Use **nearest lower grade** column behavior where that policy is documented.
- Table 20 interpolation in $f_{ck}$ may exist (document/keep parity).

Python: `Python/structural_lib/tables.py`
VBA: `VBA/Modules/M03_Tables.bas`

### 5.2 Materials curves

Purpose: $x_{u,max}/d$, $E_c$, cracking stress, steel stress interpolation behavior for Fe415/Fe500.

Python: `Python/structural_lib/materials.py`
VBA: `VBA/Modules/M05_Materials.bas`

### 5.3 Flexure design

Purpose: singly/doubly reinforced and flanged beams (where applicable), returning required steel areas and section classification.

Python: `Python/structural_lib/flexure.py`
VBA: `VBA/Modules/M06_Flexure.bas`

### 5.4 Shear design

Purpose: compute $\tau_v$, choose stirrup dia/spacing per IS 456 constraints (including spacing caps).

Python: `Python/structural_lib/shear.py`
VBA: `VBA/Modules/M07_Shear.bas`

### 5.5 Ductility checks (IS 13920)

Purpose: beam ductility checks (geometry + steel bounds + spacing constraints) used as a validation step.

Python: `Python/structural_lib/ductile.py`
VBA: `VBA/Modules/M10_Ductile.bas`

---

## 6) Detailing + DXF (design → drawing)

### 6.1 What “detailing” means here

Detailing consumes *design results* and produces bar arrangements/callouts with development length and lap rules.

Python:
- `Python/structural_lib/detailing.py` returns `BeamDetailingResult`
- `Python/structural_lib/dxf_export.py` writes a DXF (via optional `ezdxf`)

VBA:
- `VBA/Modules/M15_Detailing.bas` creates a detailing UDT/structures
- `VBA/Modules/M16_DXF.bas` writes a DXF (native R12 writer)

### 6.2 Excel mapping into detailing

The spec mapping is explicit in `docs/specs/v0.7-data-mapping.md`:
- Source table: `tbl_BeamDesign`
- Target: `create_beam_detailing(...)` in Python (and analogous VBA call)

---

## 7) Public API surfaces (what users should call)

### 7.1 Python

- Public-ish functions are documented in `docs/reference/api.md`.
- `Python/structural_lib/api.py` is intentionally thin; most usage is currently module-level.

**Contract rule:** docs are the public contract; if code differs, either fix code or fix docs.

### 7.2 VBA

There are three “surfaces”:
- Core modules called from macros.
- Worksheet UDFs (typically via `M09_UDFs.bas`).
- Add-in packaging (.xlam) described in `docs/contributing/excel-addin-guide.md`.

See `docs/contributing/vba-guide.md` for the current entry points list.

---

## 8) Parity hotspots (where to be extra careful)

These areas commonly drift between Python and VBA:

1. **Unit conversion edges** (kN/kN·m ↔ N/N·mm).
2. **Table lookup policies** (clamp/interp rules, grade selection).
3. **Flanged beam assumptions** (effective flange width, neutral axis solve, classification).
4. **“Sign convention” handling** (Mu sign and tension face logic in Excel reporting).
5. **Rounding / formatting** (bar callouts, spacing rounding, min/max caps).
6. **Mac Excel/VBA stability quirks** (UDT returns, overflow patterns).

When changing any of the above, treat it as a parity change and add/extend Python tests at minimum.

---

## 9) Where v0.8 serviceability plugs in (deflection + crack width)

**Status:** Implemented in v0.8 (Python + VBA parity).

### 9.1 Python insertion points (current)

- Core module: `Python/structural_lib/serviceability.py`
- Result types: `Python/structural_lib/types.py` (`DeflectionResult`, `CrackWidthResult`)
- Tests: `Python/tests/test_serviceability.py`

### 9.2 VBA insertion points (current)

- Core module: `VBA/Modules/M17_Serviceability.bas`
- Result types: `VBA/Modules/M02_Types.bas` (UDTs)
- Tests: `VBA/Tests/Test_Serviceability.bas`

### 9.3 Docs updates that accompany v0.8

- `docs/reference/api.md` — new serviceability functions and units.
- `docs/reference/known-pitfalls.md` — unit traps and typical boundary cases.
- `docs/TASKS.md` / `docs/planning/next-session-brief.md` — update status and acceptance criteria.

---

## 10) How to validate changes (quick checklist)

- Python: run `pytest` in `Python/`.
- If you change core behavior: add/adjust Python tests.
- If you change parity-critical logic: mirror the formula in VBA (or explicitly document divergence).
- If you change any public signature: update `docs/reference/api.md` in the same PR.

---

## 11) Pointers (start here)

- Docs index: `docs/README.md`
- Project scope/architecture: `docs/architecture/project-overview.md`
- API contract: `docs/reference/api.md`
- Pitfalls/unit rules: `docs/reference/known-pitfalls.md`
- v0.7 data mapping: `docs/specs/v0.7-data-mapping.md`
- Next session plan: `docs/planning/next-session-brief.md`
