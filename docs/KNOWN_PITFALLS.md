# IS 456 RC Beam Design Library — Known Pitfalls and Traps

Use this as a checklist to avoid common mistakes when implementing or reviewing code.

---

## Units and Conversions
- Always convert Vu to N and Mu to N·mm before combining with b×d or τc.
- Do not mix kN·m with mm in the same formula; keep internal units as N, N·mm, mm.
- Shear flow: τv = Vu / (b×d) with Vu in N; convert back to kN only for reporting.
- Stirrup spacing formulas expect Vus in N; be explicit about conversions.

## Table 19/20 Usage
- Table 19: Clamp pt to 0.15–3.0%; use nearest lower concrete grade column (no fck interpolation).
- Table 20: If τv > τc,max, section is inadequate — do not proceed to stirrup design.
- Test exact table points exactly; use bounds for interpolation cases.

## Minimum/Maximum Reinforcement
- Minimum shear reinforcement is required even if τv ≤ 0.5 τc (IS 456 Cl. 26.5.1.6).
- Minimum flexural steel per Cl. 26.5.1.1; maximum 4% bD per Cl. 26.5.1.2.

## Sign and Geometry
- Core calculations use absolute values of Mu/Vu; UI/app layer must handle sign and tension face.
- Validate geometry: b > 0, d > 0, D > d, cover < D; reject impossible sections early.

## Integer vs Floating Division (VBA)
- Use `/` for floating division; `\` truncates (integer division) and will corrupt results.

## Neutral Axis Limits
- Use Annex G ratios: Fe250=0.53, Fe415=0.48, Fe500=0.46; cap xu at xu_max for singly reinforced design.

## Rounding and Tolerances
- Keep full precision internally; round only for presentation (stresses/capacities to 3 dp, spacing to 1 dp).
- Tests: use explicit tolerances; avoid equality on floats except at table points.

## Naming and Units
- Suffix variables with units (b_mm, Vu_kN, tau_Nmm2, ast_mm2) to avoid unit mix-ups.
- Document inputs/outputs and clause references in headers; align naming across VBA/Python.

---

Use this sheet alongside `docs/DEVELOPMENT_GUIDE.md` and `docs/PROJECT_OVERVIEW.md` when coding, testing, or reviewing.
