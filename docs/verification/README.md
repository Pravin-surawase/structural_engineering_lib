# Verification

Benchmark examples and verification packs for validating library calculations.

## Contents

| Document | Purpose |
|----------|---------|
| [Validation Pack](validation-pack.md) | 5 benchmark beams with IS 456 references |
| [Examples](examples.md) | Detailed worked examples with hand calculations |
| [Verification Pack](pack.md) | Test vectors for regression testing |

## Quick Start

Run the validation pack to verify library accuracy:

```bash
python -c "
from structural_lib import flexure, shear
r = flexure.design_singly_reinforced(b=230, d=450, d_total=500, mu_knm=100, fck=20, fy=415)
print(f'B1: Mu_lim={r.mu_lim:.2f} (expected: 128.51)')
r = shear.design_shear(vu_kn=150, b=230, d=450, fck=20, fy=415, asv=100, pt=1.0)
print(f'B4: τv={r.tv:.3f} (expected: 1.449)')
"
```

## Why verification matters

Engineering software must be verifiable. These documents provide:

- **Hand calculation comparisons** — Every formula traced to IS 456 clause
- **SP:16 cross-references** — Design aids table lookups
- **Tolerance specifications** — Acceptable error bounds
- **Reproducible test cases** — Same input → same output
