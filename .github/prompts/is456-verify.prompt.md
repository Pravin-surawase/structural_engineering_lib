---
description: "IS 456 formula verification — validate structural calculations against the standard"
---

# IS 456 Verification Workflow

Use this when modifying or reviewing code in `Python/structural_lib/codes/is456/`.

## Step 1: Identify What Changed

```bash
git diff --name-only HEAD~1 | grep -E "codes/is456|flexure|shear|detailing|torsion|serviceability"
```

## Step 2: Cross-Check Formula Against Standard

For each modified formula, verify:
- [ ] Clause reference is cited (e.g., "IS 456 Cl 38.1")
- [ ] Formula matches the published standard exactly
- [ ] Units are explicit — mm, N/mm², kN, kNm
- [ ] Edge cases handled (min reinforcement, max spacing, balanced section)
- [ ] Results match SP:16 design aids within ±0.1%

## Step 3: Run Targeted Tests

```bash
# By module
.venv/bin/pytest Python/tests/unit/test_compliance.py -v
.venv/bin/pytest Python/tests/unit/test_detailing.py -v
.venv/bin/pytest Python/tests/unit/test_rebar.py -v

# By keyword
.venv/bin/pytest Python/tests/ -v -k "{{keyword}}"

# Full regression
.venv/bin/pytest Python/tests/regression/ -v
```

## Step 4: Check Against Benchmarks

Known benchmark problems (Pillai & Menon, Ramamrutham):
- Singly reinforced: b=300mm, d=500mm, M25, Fe415, Mu=150kNm
- Doubly reinforced: Mu exceeds Mu_lim
- Shear design: τv > τc (stirrups required)

```bash
.venv/bin/python scripts/discover_api_signatures.py design_beam_is456
```

## Step 5: Review Key Edge Cases

| Category | Test |
|----------|------|
| Mu = 0 | Should return minimum reinforcement |
| Mu = Mu_lim | Balanced section, no compression steel |
| Mu > Mu_lim | Doubly reinforced required |
| τv < τc | Minimum stirrups only |
| τv > τc_max | Section is unsafe — reject |
| pt < 0.15% | Below minimum — flag warning |

## Step 6: Commit with Clause Reference

```bash
./scripts/ai_commit.sh "fix: correct IS 456 Cl {{clause}} implementation"
```
