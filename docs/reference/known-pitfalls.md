# IS 456 RC Beam Design Library — Known Pitfalls and Traps

Use this as a checklist to avoid common mistakes when implementing or reviewing code.

---

## Units and Conversions
- Always convert Vu to N and Mu to N·mm before combining with b×d or τc.
- Do not mix kN·m with mm in the same formula; keep internal units as N, N·mm, mm.
- Shear flow: τv = Vu / (b×d) with Vu in N; convert back to kN only for reporting.
- Stirrup spacing formulas expect Vus in N; be explicit about conversions.
- Boundary contract (public -> internal):
  - kN -> N: multiply by 1,000
  - kN·m -> N·mm: multiply by 1,000,000
  - mm stays mm; N/mm² stays N/mm²

## Table 19/20 Usage
- Table 19: Clamp pt to 0.15–3.0%; use nearest lower concrete grade column (no fck interpolation).
- Table 19 range: fck is 15–40 only; values outside are clamped to bounds with a warning.
- Table 20: If τv > τc,max, section is inadequate — do not proceed to stirrup design.
- Test exact table points exactly; use bounds for interpolation cases.

## Minimum/Maximum Reinforcement
- Minimum shear reinforcement is required even if τv ≤ 0.5 τc (IS 456 Cl. 26.5.1.6).
- Minimum flexural steel per Cl. 26.5.1.1; maximum 4% bD per Cl. 26.5.1.2.

## Sign and Geometry
- Core calculations use absolute values of Mu/Vu; UI/app layer must handle sign and tension face.
- Validate geometry: b > 0, d > 0, D > d, cover < D; reject impossible sections early.

## Flanged Beams
- Effective flange width helpers expect **effective span** (center-to-center) and explicit flange overhangs; do not pass a single total width without splitting left/right.

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

## Serviceability (v0.8+)
- Deflection checks use **mm/mm** ratios (L/d); do not mix mm and m.
- Crack width calculations output **mm**; keep stresses in **N/mm²**.
- Avoid silent defaults: if a base limit, modifier, or crack limit is assumed, record it explicitly in outputs.
- Be strict about required parameters (especially crack width): fail with a reason rather than guessing missing geometry/state inputs.

## Bar Bending Schedule (v0.10+)
- Steel density: Use IS 1786 value of 7850 kg/m³ (not 7860 or 7800).
- Length rounding: Round cut lengths to nearest 10mm per IS 2502.
- Weight rounding: Round weights to 0.01 kg.
- Stirrup hook allowance: 10φ per hook (20φ total for 2 hooks).
- Stirrup corner bends: Use 0.57×hook_diameter per corner (4 corners).

## ETABS Integration
- ETABS uses **M3** for major axis moment (typically Mu) and **V2** for major axis shear (Vu).
- Station values in ETABS are relative distances along element; normalize to absolute positions if needed.
- ETABS sign convention may differ from IS 456 (compression positive vs tension positive).
- Always verify units: ETABS can export in kN-m or kip-ft; ensure CSV headers indicate units.

## Parity (Python ↔ VBA)
- Tolerances: Ast ±1 mm², stress ±0.01 N/mm², length ±1 mm, ratio ±0.0001.
- Function signatures differ: Python uses snake_case, VBA uses PascalCase.
- Ensure both platforms use identical Table 19/20 interpolation logic.
- When updating one platform, update the other and run parity tests.

## Platform/VBA Quirks
- Mac/Excel/VBA quirks (overflow patterns, debug/printing pitfalls, import-order errors) are tracked in [troubleshooting.md](troubleshooting.md).

---

Use this sheet alongside `docs/contributing/development-guide.md` and `docs/architecture/project-overview.md` when coding, testing, or reviewing.
