---
name: is456-verification
description: "Run IS 456:2000 compliance verification tests and benchmark checks. Use to validate structural calculations, verify code compliance, run regression tests, and check design results against known benchmarks."
---

# IS 456:2000 Verification Skill

Run structural engineering verification tests to validate IS 456:2000 compliance, design calculations, and benchmark results.

## When to Use

- After modifying any file in `Python/structural_lib/codes/is456/`
- After changing design functions in `services/api.py`
- To verify a specific calculation (flexure, shear, detailing, rebar)
- Before merging any PR that touches structural calculations
- When a user reports incorrect design results

## Run All Tests

```bash
.venv/bin/pytest Python/tests/ -v
```

**Required coverage:** 85% branch coverage minimum.

## Run Specific Test Categories

### Core design tests:
```bash
.venv/bin/pytest Python/tests/test_core.py -v              # Core types and classes
.venv/bin/pytest Python/tests/test_design_from_input.py -v # End-to-end design
.venv/bin/pytest Python/tests/test_api_results.py -v       # API result validation
```

### IS 456 compliance:
```bash
.venv/bin/pytest Python/tests/unit/test_compliance.py -v            # Compliance checks
.venv/bin/pytest Python/tests/unit/test_compliance_validation.py -v # Validation rules
.venv/bin/pytest Python/tests/unit/test_detailing.py -v             # Detailing rules
.venv/bin/pytest Python/tests/unit/test_ductile.py -v               # Ductile detailing
```

### Rebar and reinforcement:
```bash
.venv/bin/pytest Python/tests/unit/test_rebar.py -v          # Rebar calculations
.venv/bin/pytest Python/tests/unit/test_anchorage_check.py -v # Anchorage length
```

### Geometry and visualization:
```bash
.venv/bin/pytest Python/tests/test_visualization_geometry_3d.py -v # 3D geometry
.venv/bin/pytest Python/tests/unit/test_building_geometry.py -v    # Building geometry
.venv/bin/pytest Python/tests/unit/test_flange_width.py -v        # T-beam flange
```

### Import and adapters:
```bash
.venv/bin/pytest Python/tests/unit/test_adapters.py -v           # Adapter tests
.venv/bin/pytest Python/tests/unit/test_generic_csv_adapter.py -v # CSV adapter
.venv/bin/pytest Python/tests/unit/test_etabs_import.py -v       # ETABS import
.venv/bin/pytest Python/tests/test_etabs_import_integration.py -v # Integration
```

### Batch and performance:
```bash
.venv/bin/pytest Python/tests/unit/test_batch.py -v      # Batch operations
.venv/bin/pytest Python/tests/performance/ -v            # Performance benchmarks
```

### Regression:
```bash
.venv/bin/pytest Python/tests/regression/ -v             # Regression suite
```

## Run by Keyword

```bash
.venv/bin/pytest Python/tests/ -v -k "beam"       # All beam-related tests
.venv/bin/pytest Python/tests/ -v -k "shear"      # Shear design tests
.venv/bin/pytest Python/tests/ -v -k "flexure"    # Flexure tests
.venv/bin/pytest Python/tests/ -v -k "rebar"      # Rebar tests
.venv/bin/pytest Python/tests/ -v -k "detailing"  # Detailing tests
.venv/bin/pytest Python/tests/ -v -k "compliance" # Compliance tests
```

## IS 456 Code Files (what you're verifying)

| File | Coverage |
|------|----------|
| `codes/is456/flexure.py` | Bending moment capacity, neutral axis |
| `codes/is456/shear.py` | Shear strength, stirrup design |
| `codes/is456/detailing.py` | Spacing, cover, bar arrangement |
| `codes/is456/slenderness.py` | Slenderness checks |
| `codes/is456/compliance.py` | Code compliance validation |

## Units Reference (IS 456)

| Quantity | Unit | Parameter Suffix |
|----------|------|-----------------|
| Length | mm | `_mm` |
| Concrete strength | N/mm² (MPa) | `fck` |
| Steel yield strength | N/mm² (MPa) | `fy` |
| Moment | kNm | `_kNm` |
| Shear force | kN | `_kN` |
| Area | mm² | `_mm2` |
| Stress | N/mm² | `_Nmm2` |

## Full Validation Suite

For comprehensive pre-merge validation:
```bash
./run.sh check          # 28 checks including tests, linting, architecture
./run.sh check --quick  # Fast subset (<30s)
./run.sh test           # Just tests
```

## Interpreting Failures

- **Compliance test failure:** Check if IS 456 clause references changed in code
- **Detailing test failure:** Verify spacing/cover rules match IS 456 Table 26
- **Rebar test failure:** Check bar diameter tables and area calculations
- **Regression failure:** Compare with previous known-good results — may need benchmark update if intentional change
