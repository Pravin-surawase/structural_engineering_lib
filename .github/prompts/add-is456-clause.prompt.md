---
description: "Add new IS 456 clause implementation — research, implement, test, verify"
---

# Add IS 456 Clause Implementation

## 1. Research the Clause

Before coding, verify the exact formula from IS 456:2000:

```bash
# Check if this clause is already implemented
grep -r "{{clause_number}}" Python/structural_lib/codes/is456/ --include="*.py"

# Check existing IS 456 modules
ls Python/structural_lib/codes/is456/
# flexure.py, shear.py, detailing.py, torsion.py, serviceability.py, slenderness.py, compliance.py
```

## 2. Identify the Right Module

| Clause Range | Module | Topic |
|-------------|--------|-------|
| Cl 26 | `detailing.py` | Development length, spacing, cover |
| Cl 38 | `flexure.py` | Flexural design (singly/doubly reinforced) |
| Cl 40 | `shear.py` | Shear design, τc tables, stirrups |
| Cl 41 | `torsion.py` | Torsion design |
| Cl 43 | `serviceability.py` | Deflection, crack width |
| General | `compliance.py` | Code compliance validation |

## 3. Get Existing API Signatures

```bash
.venv/bin/python scripts/discover_api_signatures.py --filter {{keyword}}
```

## 4. Implementation Rules

- **Layer:** All IS 456 math goes in `codes/is456/` — pure math, NO I/O
- **Units:** Always explicit — mm, N/mm², kN, kNm
- **Clause reference:** Add `# IS 456:2000 Cl XX.X` comment above every formula
- **Parameter names:** Follow existing convention — `b_mm`, `d_mm`, `fck`, `fy`, `Mu_kNm`, `Vu_kN`
- **Return type:** Use existing dataclass patterns from `core/`
- **Edge cases:** Handle min reinforcement, max spacing, balanced section limits

## 5. Write Tests

```bash
# Check existing test patterns
grep -r "def test_" Python/tests/ --include="*.py" -l | head -10

# Look at similar tests for reference
grep -r "{{keyword}}" Python/tests/ --include="*.py" -l
```

### Test requirements:
- Cite IS 456 clause in test name and comment
- Include at least 3 cases: normal, boundary, edge
- Verify against SP:16 Design Aids within ±0.1%
- Include textbook benchmark if available (Pillai & Menon, Ramamrutham)

## 6. Wire into API (if needed)

If the clause implementation should be exposed via the public API:

```bash
# Check current API surface
grep "^def " Python/structural_lib/services/api.py | head -30
```

Add the function to `services/api.py` (NOT the stub `api.py`).

## 7. Verify

```bash
# Run IS 456 tests
.venv/bin/pytest Python/tests/ -v -k "{{keyword}}"

# Full compliance suite
.venv/bin/pytest Python/tests/unit/test_compliance.py -v

# Architecture check
.venv/bin/python scripts/check_architecture_boundaries.py
```

## 8. Commit

```bash
./scripts/ai_commit.sh "feat(is456): implement Cl {{clause_number}} — {{description}}"
```
