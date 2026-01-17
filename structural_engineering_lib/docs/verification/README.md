# Verification

Benchmark examples and verification packs for validating library calculations against IS 456 standards.

**Files:** 5 | **Updated:** 2026-01-11

---

## 📋 Contents

| Document | Description |
|----------|-------------|
| [validation-pack.md](validation-pack.md) | 5 benchmark beams with IS 456 references |
| [insights-verification-pack.md](insights-verification-pack.md) | 10 benchmark cases for insights module (v0.12.0+) |
| [examples.md](examples.md) | Detailed worked examples with hand calculations |
| [pack.md](pack.md) | Test vectors for regression testing |
| [external-cli-test.md](external-cli-test.md) | S-007 checklist for a fresh user run |

---

## 🚀 Quick Start

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

---

## ✅ Why Verification Matters

Engineering software must be verifiable. These documents provide:

| Feature | Purpose |
|---------|---------|
| **Hand calculation comparisons** | Every formula traced to IS 456 clause |
| **SP:16 cross-references** | Design aids table lookups |
| **Tolerance specifications** | Acceptable error bounds (±0.1% areas, ±1mm dimensions) |
| **Reproducible test cases** | Same input → same output (deterministic) |

---

## 📚 Related Documentation

| Document | Purpose |
|----------|---------|
| [IS 456 Formulas](../reference/is456-formulas.md) | Formula quick reference |
| [Testing Strategy](../contributing/testing-strategy.md) | Test writing guidelines |
| [Known Pitfalls](../reference/known-pitfalls.md) | Common calculation traps |

---

**Parent:** [docs/README.md](../README.md)
