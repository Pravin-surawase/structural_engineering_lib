# Day 2: Beam Flexure Design

**Type:** Guide
**Audience:** Developers
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-08
**Last Updated:** 2026-04-08

**Prerequisites:** [Day 1 — Concrete Basics](day-01-concrete-basics.md) (fck, fy, safety factors, stress-strain)\n**Library file:** `Python/structural_lib/codes/is456/beam/flexure.py`\n**IS 456 references:** Cl 38.1 (stress-block assumptions), Cl 23.1.2 (flanged beams), Annex G-1.1/G-1.2/G-2.2

---

## What You'll Learn

By the end of this module you will:
- Understand *why* beams bend and what "flexure" actually means
- Walk through every term in the IS 456 moment capacity formula
- Know the difference between singly, doubly, and T-beam design
- Use the library's `flexure.py` functions to design real beams
- Be able to hand-check library output against the formulas

---

## 📖 Theory

### 1. What is Flexure?

Imagine holding a ruler between two supports and pressing down in the middle. The top surface shortens (compression) and the bottom surface stretches (tension). That's **flexure** — the beam's response to bending.

Now think of a seesaw. Somewhere between the compressed top and the stretched bottom, there's a line that's neither compressed nor stretched. That's the **neutral axis (NA)** — the balancing point where stress equals zero.

```
        ← compression (top fibers shorten)
  ──────────────────  ← top of beam
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ← concrete handles this
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  ─ ─ ─ ─ NA ─ ─ ─   ← neutral axis (stress = 0)
  ░░░░░░░░░░░░░░░░
  ░░░░░░░░░░░░░░░░  ← steel handles this
  ──────────────────  ← bottom of beam
        → tension (bottom fibers stretch)
```

**Key insight:** Concrete is strong in compression but weak in tension (it cracks easily). Steel is strong in tension. So we put steel bars at the bottom where the tension lives. This combination — concrete on top, steel on the bottom — is what makes reinforced concrete work.
