---
name: new-structural-element
description: "Step-by-step workflow for adding a new structural element (column, slab, footing) to the library. Covers IS 456 clause research, type definitions, pure math implementation, API wiring, tests, and frontend integration."
argument-hint: "Element name: 'column' | 'slab-oneway' | 'slab-twoway' | 'footing' | 'staircase' | 'shear-wall'"
---

# New Structural Element Skill

Complete workflow for adding a new structural element to the IS 456 library. Covers all layers from math to UI.

## When to Use

- Adding column, slab, footing, staircase, or shear wall design
- Expanding the library beyond beam design
- Any new structural element following IS 456:2000

## Pre-Flight Checks

```bash
# 1. Check if anything already exists for this element
grep -ri "<element>" Python/structural_lib/codes/is456/ --include="*.py"
grep -ri "<element>" Python/structural_lib/core/ --include="*.py"
grep -ri "<element>" Python/structural_lib/services/api.py

# 2. Check for related types
grep -r "class.*<Element>" Python/structural_lib/core/data_types.py
grep -r "class.*<Element>" Python/structural_lib/core/inputs.py

# 3. Verify no duplicate routes
grep -ri "<element>" fastapi_app/routers/ --include="*.py"
```

## IS 456 Clause Reference Map

| Element | Primary Clauses | SP:16 Sections | Key Tables |
|---------|----------------|----------------|------------|
| **Column** | Cl 25 (slenderness), Cl 26 (detailing), Cl 39 (design) | Charts 27-62 | Table 25 (xu_max/d) |
| **One-Way Slab** | Cl 22 (loads), Cl 24 (slabs), Cl 26 (detailing) | Charts 1-26 | Table 12 (span/depth) |
| **Two-Way Slab** | Cl 24, Annex D (moment coefficients) | — | Table 26 (αx, αy) |
| **Footing** | Cl 34 (footings), Cl 31 (flat slabs for punching) | — | — |
| **Staircase** | Cl 33 (stairs) | — | — |
| **Shear Wall** | Cl 32 (walls) | — | — |

## Step-by-Step Pipeline

### Step 1: Define Types (structural-math agent)

Create input/output types in `core/`:

```bash
# Check existing type patterns
grep -A5 "class.*Input" Python/structural_lib/core/inputs.py | head -30
grep -A5 "class.*Result" Python/structural_lib/core/data_types.py | head -30
```

**Files to modify:**
- `Python/structural_lib/core/inputs.py` — add `<Element>GeometryInput`, `<Element>LoadsInput`
- `Python/structural_lib/core/data_types.py` — add `<Element>Result`
- `Python/structural_lib/core/errors.py` — add `E_<ELEMENT>_XXX` error codes

### Step 2: Implement Math (structural-math agent)

Create `Python/structural_lib/codes/is456/<element>.py`:

**Follow the module pattern:**
1. SPDX header + docstring with traceability note
2. Import `@clause` from `traceability`
3. Import result types from `core/data_types`
4. Import error types from `core/errors`
5. Import validators from `core/validation`
6. Define `__all__` exports
7. Implement functions with `@clause("XX.X")` decorator
8. Validate inputs at start of every public function
9. All math in mm, N, N·mm internally — convert at boundaries

```bash
# Verify the module after creation
.venv/bin/python -c "from structural_lib.codes.is456.<element> import *; print('OK')"
.venv/bin/python scripts/validate_imports.py --scope structural_lib
.venv/bin/python scripts/check_architecture_boundaries.py
```

### Step 3: Write Tests (tester agent)

Create `Python/tests/unit/test_<element>.py`:

```bash
# Check existing test patterns
head -50 Python/tests/unit/test_compliance.py
```

**Test requirements:**
- Minimum 3 cases per function: normal, boundary, edge
- Benchmark against SP:16 Design Aids within ±0.1%
- Include textbook references (Pillai & Menon, Ramamrutham)
- Test error cases (invalid dimensions, materials)
- Test min/max reinforcement limits

```bash
# Run tests
.venv/bin/pytest Python/tests/unit/test_<element>.py -v
```

### Step 4: Wire API (backend agent)

Add orchestration function to `Python/structural_lib/services/api.py`:

```bash
# Check current API surface
grep "^def " Python/structural_lib/services/api.py | head -30

# Follow existing pattern (design_beam_is456 is the template)
.venv/bin/python scripts/discover_api_signatures.py design_beam_is456
```

### Step 5: Add Endpoint (api-developer agent)

Create `fastapi_app/routers/<element>.py`:

```bash
# Check existing router patterns
head -50 fastapi_app/routers/design.py

# Register in main.py
grep "include_router" fastapi_app/main.py
```

### Step 6: Add Frontend (frontend agent)

Create hook + component in `react_app/src/`:

```bash
# Check existing hook patterns
ls react_app/src/hooks/
head -30 react_app/src/hooks/useLiveDesign.ts

# Check existing component patterns
ls react_app/src/components/design/
```

### Step 7: Verify Everything

```bash
# Full test suite
.venv/bin/pytest Python/tests/ -v

# Architecture check
.venv/bin/python scripts/check_architecture_boundaries.py
.venv/bin/python scripts/validate_imports.py --scope structural_lib

# React build
cd react_app && npm run build

# Quick validation
./run.sh check --quick
```

## Agent Pipeline for New Element

```
orchestrator → structural-math (types + math)
             → tester (unit tests + benchmarks)
             → structural-engineer (IS 456 verification)
             → backend (services/api.py wiring)
             → api-developer (FastAPI endpoint)
             → frontend (hook + component)
             → reviewer (mandatory gate)
             → doc-master (API docs, WORKLOG)
             → ops (commit + PR)
```

## Benchmark Sources

| Source | Use For | Accuracy |
|--------|---------|----------|
| SP:16 Design Aids | Standard design charts | ±0.1% (authoritative) |
| Pillai & Menon | Textbook examples | ±1% (rounding differences) |
| Ramamrutham | Textbook examples | ±1% |
| IS 456:2000 Tables | Design tables (τc, etc.) | Exact match required |
| Hand calculation | Engineer's verification | ±0.5% |
