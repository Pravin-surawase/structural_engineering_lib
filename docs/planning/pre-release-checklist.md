# Pre-Release Checklist

**Type:** Checklist
**Audience:** Maintainers
**Status:** Active
**Importance:** High
**Created:** 2025-06-01
**Last Updated:** 2026-01-21

---

Version: 0.19.0 (current)
Target: Public beta with library-first APIs + DXF/BBS quality gates

---

## Current State (last verified 2026-01-21)

| Area | Status | Evidence |
|------|--------|----------|
| Test Suite | ✅ See CI dashboard | `.venv/bin/python -m pytest Python/tests` |
| PyPI | ✅ Live | `pip install structural-lib-is456` |
| CLI | ✅ Functional | `python -m structural_lib --help` works |
| Excel Integration | ⚠️ Functional (not parity-verified) | CSV/JSON workflows work; VBA outputs not compared |
| API Docs | ✅ Polished | Phases 0–5 complete (see api-docs-ux-plan.md) |
| Version | Pre-1.0 | APIs may change before 1.0 |

---

## Versioning & Release Rules (from now on)

**Policy (pre-1.0):**
- `0.9.x` → fixes/docs/UX updates (no new features)
- `0.10.0`, `0.11.0`, ... → new features
- `1.0.0` → first stable public release
- `2.0.0` → breaking changes after 1.0

**Release discipline:**
- Version bumps happen **only when releasing**, not for every merge.
- Each release must update **releases.md** and **CHANGELOG.md**.
- Tag format: `vX.Y.Z`.

**Beta labeling:**
- All `0.y.z` releases are treated as **beta** in docs.
- Optional strict beta: use pre-release tags like `0.9.6b1` (requires `pip install --pre`).

**Gates:**
- No tag or PyPI publish unless the “Required Before Beta/1.0” sections are satisfied.

---

## Beta Readiness Checklist

### Required Before Beta

- [x] **Run 3–5 real beam designs** and compare to hand calcs or known results
  - [x] Singly reinforced rectangular beam — ✅ PASS (Ast within 0.14%)
  - [x] Doubly reinforced rectangular beam — ✅ PASS (uses SP:16 fsc, Asc within 0.06%)
  - [x] Flanged beam (T-beam) — ✅ PASS (exact match: Mu,lim, Ast, xu)
  - [x] High shear case — ✅ PASS (exact match: τv, τc, Vus, spacing)
  - [ ] Seismic detailing case (if applicable)
- [x] **Document results** in `docs/verification/validation-pack.md` with source refs
- [ ] **One external engineer tries CLI cold** — note friction points
- [x] **All tests pass** (see CI and local runs)
- [ ] **PyPI install verified in clean venv** — `scripts/release.py verify --version X.Y.Z --source pypi`

### Nice-to-Have Before Beta

- [ ] VBA parity harness (automated comparison of Python vs VBA outputs)
- [ ] Edge case spot-checks documented (flanged NA in web, doubly reinforced near Mu,lim)
- [ ] Error messages reviewed for actionability

### Required Before 1.0

- [ ] At least 10 real-world validations documented
- [ ] VBA parity verified (automated or manual)
- [ ] One external user's feedback incorporated
- [ ] Changelog updated with breaking changes (if any)
- [ ] Version bump to 1.0.0

---

## Validation Template

Use this for each real beam design:

```markdown
### Beam [ID]

**Source:** [Textbook/SP16/Hand calc/Project]

| Parameter | Value | Unit |
|-----------|-------|------|
| b | | mm |
| D | | mm |
| d | | mm |
| fck | | N/mm² |
| fy | | N/mm² |
| Mu | | kN·m |
| Vu | | kN |

**Expected Results:**
- Ast: __ mm²
- Asc: __ mm² (if doubly reinforced)
- xu: __ mm
- Stirrup spacing: __ mm

**Library Results:**
```python
result = api.design_beam_is456(...)
```

**Comparison:**
- Ast: Expected __ vs Actual __ (Δ = _%)
- ...

**Verdict:** ✅ PASS / ❌ FAIL / ⚠️ Within tolerance
```

---

## Status Log

| Date | Action | Result |
|------|--------|--------|
| 2025-12-27 | Checklist created | — |
| | | |
