# Complete Function Enumeration — Multi-Code RC Design Library

**Type:** Reference
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-08
**Last Updated:** 2026-04-08

---

## Summary

Exhaustive enumeration of every function required for a multi-code reinforced concrete design library supporting **IS 456:2000**, **ACI 318-19**, and **Eurocode 2 (EN 1992-1-1)**.

### Total Function Counts

| Category | Shared | IS 456 | ACI 318 | EC2 | Total |
|----------|--------|--------|---------|-----|-------|
| **Beam** | 24 | 52 | 48 | 50 | 174 |
| **Column** | 14 | 32 | 30 | 32 | 108 |
| **Slab** | 16 | 28 | 26 | 28 | 98 |
| **Footing** | 12 | 20 | 18 | 20 | 70 |
| **Staircase** | 6 | 10 | 8 | 8 | 32 |
| **Common infra** | 30 | 18 | 16 | 18 | 82 |
| **TOTAL** | **102** | **160** | **146** | **156** | **564** |

### Legend

- ✅ = Implemented in current codebase
- 🔲 = Not yet implemented
- `(mm)` / `(N/mm²)` / `(kN)` / `(kNm)` = explicit unit annotations

---

## 0. PROTOCOL INTERFACES

Every design code MUST implement these abstract protocols. Code-specific modules provide the concrete implementations.

### 0.1 MaterialCode Protocol

```python
class MaterialCode(Protocol):
    """Material property lookups per design code."""
    def elastic_modulus_concrete(self, fck: float) -> float: ...
    def elastic_modulus_steel(self) -> float: ...
    def flexural_tensile_strength(self, fck: float) -> float: ...
    def design_concrete_strength(self, fck: float) -> float: ...
    def design_steel_strength(self, fy: float) -> float: ...
    def ultimate_concrete_strain(self) -> float: ...
    def modular_ratio(self, fck: float) -> float: ...
    def creep_coefficient(self, age_days: int, rh: float) -> float: ...
    def shrinkage_strain(self, age_days: int, rh: float) -> float: ...
```

### 0.2 FlexuralCode Protocol

```python
class FlexuralCode(Protocol):
    """Flexural design per any design code."""
    def stress_block_depth(self, fck: float, fy: float) -> float: ...
    def stress_block_force(self, fck: float, b: float, xu: float) -> float: ...
    def moment_capacity_rectangular(self, fck: float, fy: float, b: float, d: float, xu: float) -> float: ...
    def limiting_neutral_axis(self, fy: float) -> float: ...
    def tension_steel_area(self, Mu: float, fck: float, fy: float, b: float, d: float) -> float: ...
    def compression_steel_area(self, Mu: float, Mu_lim: float, fck: float, fy: float, b: float, d: float, d_prime: float) -> float: ...
    def effective_flange_width(self, span: float, bf: float, bw: float, Df: float) -> float: ...
    def flanged_moment_capacity(self, fck: float, fy: float, bf: float, bw: float, Df: float, d: float) -> float: ...
    def min_tension_steel(self, b: float, d: float, fck: float, fy: float) -> float: ...
    def max_tension_steel(self, b: float, D: float) -> float: ...
```

### 0.3 ShearCode Protocol

```python
class ShearCode(Protocol):
    """Shear design per any design code."""
    def nominal_shear_stress(self, Vu: float, b: float, d: float) -> float: ...
    def concrete_shear_capacity(self, fck: float, pt: float, b: float, d: float) -> float: ...
    def max_shear_stress(self, fck: float) -> float: ...
    def stirrup_area_required(self, Vu: float, Vc: float, fy: float, d: float, sv: float) -> float: ...
    def min_shear_reinforcement(self, b: float, fy: float) -> float: ...
    def max_stirrup_spacing(self, d: float) -> float: ...
    def critical_section_distance(self, d: float) -> float: ...
```

### 0.4 TorsionCode Protocol

```python
class TorsionCode(Protocol):
    """Torsion design per any design code."""
    def torsional_shear_stress(self, Tu: float, b: float, d: float) -> float: ...
    def equivalent_shear(self, Vu: float, Tu: float, b: float) -> float: ...
    def transverse_torsion_steel(self, Tu: float, fy: float, b1: float, d1: float, sv: float) -> float: ...
    def longitudinal_torsion_steel(self, Tu: float, Mu: float, fy: float, b1: float, d1: float) -> float: ...
    def min_torsion_threshold(self, fck: float, b: float, d: float) -> float: ...
```

### 0.5 ColumnCode Protocol

```python
class ColumnCode(Protocol):
    """Column design per any design code."""
    def classify_column(self, le: float, D: float) -> str: ...
    def axial_capacity(self, fck: float, fy: float, Ag: float, Ast: float) -> float: ...
    def min_eccentricity(self, length: float, D: float) -> float: ...
    def moment_capacity_uniaxial(self, fck: float, fy: float, b: float, D: float, d_prime: float, Ast: float, Pu: float) -> float: ...
    def biaxial_check(self, Pu: float, Mux: float, Muy: float, Mux1: float, Muy1: float, Puz: float) -> bool: ...
    def slenderness_moment(self, le: float, D: float, Pu: float) -> float: ...
    def pm_interaction_curve(self, fck: float, fy: float, b: float, D: float, d_prime: float, Ast: float, n_points: int) -> list: ...
    def min_steel_ratio(self) -> float: ...
    def max_steel_ratio(self) -> float: ...
```

### 0.6 SlabCode Protocol

```python
class SlabCode(Protocol):
    """Slab design per any design code."""
    def min_thickness(self, span: float, support_type: str) -> float: ...
    def moment_coefficients_twoway(self, Lx: float, Ly: float, edge_conditions: int) -> dict: ...
    def distribution_steel(self, b: float, D: float) -> float: ...
    def punching_shear_capacity(self, fck: float, d: float, perimeter: float) -> float: ...
    def max_bar_spacing(self, D: float) -> float: ...
```

### 0.7 FootingCode Protocol

```python
class FootingCode(Protocol):
    """Footing design per any design code."""
    def size_footing(self, load: float, sbc: float) -> tuple[float, float]: ...
    def bearing_pressure_check(self, load: float, area: float, sbc: float) -> bool: ...
    def critical_section_flexure(self, col_dim: float) -> float: ...
    def one_way_shear_check(self, fck: float, pt: float, Vu: float, b: float, d: float) -> bool: ...
    def punching_shear_check(self, fck: float, Vu: float, perimeter: float, d: float) -> bool: ...
    def development_length(self, bar_dia: float, fck: float, fy: float) -> float: ...
```

### 0.8 DetailingCode Protocol

```python
class DetailingCode(Protocol):
    """Detailing rules per any design code."""
    def development_length(self, bar_dia: float, fck: float, fy: float, bar_type: str) -> float: ...
    def lap_length(self, bar_dia: float, fck: float, fy: float, bar_type: str) -> float: ...
    def min_clear_spacing(self, bar_dia: float, agg_size: float) -> float: ...
    def max_bar_spacing(self, D: float, element: str) -> float: ...
    def min_bend_radius(self, bar_dia: float) -> float: ...
    def clear_cover(self, exposure: str, element: str) -> float: ...
```

### 0.9 ServiceabilityCode Protocol

```python
class ServiceabilityCode(Protocol):
    """Serviceability checks per any design code."""
    def span_depth_ratio(self, span: float, support: str, pt: float, pc: float, fck: float, fy: float) -> float: ...
    def crack_width(self, bar_dia: float, spacing: float, cover: float, strain: float) -> float: ...
    def immediate_deflection(self, M: float, Ig: float, Icr: float, Mcr: float, Ec: float, L: float) -> float: ...
    def long_term_deflection_factor(self, rho_prime: float, duration_months: int) -> float: ...
    def allowable_crack_width(self, exposure: str) -> float: ...
```

---

## 1. BEAM Functions

### 1.1 Shared / Code-Agnostic (`codes/common/beam/`)

Pure structural mechanics — identical math regardless of design code.

| # | Function | Signature | Return | Description |
|---|----------|-----------|--------|-------------|
| 1 | `strain_at_depth` | `(epsilon_cu: float, xu: float, depth: float) -> float` | `float` | Linear strain from similar triangles |
| 2 | `neutral_axis_from_strain` | `(epsilon_cu: float, epsilon_s: float, d: float) -> float` | `float (mm)` | NA depth from concrete/steel strains |
| 3 | `lever_arm` | `(d: float, xu: float, k: float) -> float` | `float (mm)` | Internal lever arm = d − k·xu |
| 4 | `moment_from_couple` | `(force: float, lever_arm: float) -> float` | `float (N·mm)` | M = C × z or T × z |
| 5 | `section_modulus` | `(b: float, D: float) -> float` | `float (mm³)` | S = b·D²/6 |
| 6 | `gross_moment_of_inertia` | `(b: float, D: float) -> float` | `float (mm⁴)` | Ig = b·D³/12 |
| 7 | `cracked_moment_of_inertia` | `(b: float, d: float, xu: float, m: float, Ast: float, Asc: float, d_prime: float) -> float` | `float (mm⁴)` | Transformed cracked section Icr |
| 8 | `effective_moment_of_inertia` | `(Mcr: float, Ma: float, Ig: float, Icr: float) -> float` | `float (mm⁴)` | Branson's equation: Ieff |
| 9 | `cracking_moment` | `(fr: float, Ig: float, yt: float) -> float` | `float (N·mm)` | Mcr = fr·Ig/yt |
| 10 | `steel_area_from_bars` | `(n_bars: int, dia: float) -> float` | `float (mm²)` | As = n·π·d²/4 |
| 11 | `reinforcement_ratio` | `(Ast: float, b: float, d: float) -> float` | `float` | ρ = Ast/(b·d) |
| 12 | `compression_reinforcement_ratio` | `(Asc: float, b: float, d: float) -> float` | `float` | ρ' = Asc/(b·d) |
| 13 | `effective_depth_multilayer` | `(layers: list[tuple[float,float]], total_area: float) -> float` | `float (mm)` | Centroid of multi-layer rebar |
| 14 | `bar_weight_per_meter` | `(dia: float) -> float` | `float (kg/m)` | ρ_steel·π·d²/4 (7850 kg/m³) |
| 15 | `cut_length` | `(gross_length: float, bends: list[float]) -> float` | `float (mm)` | Total cut length incl. bends |
| 16 | `deflection_simply_supported` | `(w: float, L: float, EI: float) -> float` | `float (mm)` | 5wL⁴/(384EI) |
| 17 | `deflection_cantilever` | `(w: float, L: float, EI: float) -> float` | `float (mm)` | wL⁴/(8EI) |
| 18 | `deflection_fixed_fixed` | `(w: float, L: float, EI: float) -> float` | `float (mm)` | wL⁴/(384EI) |
| 19 | `moment_udl_ss` | `(w: float, L: float) -> float` | `float (N·mm)` | wL²/8 |
| 20 | `moment_udl_fixed` | `(w: float, L: float) -> float` | `float (N·mm)` | wL²/12 (midspan) |
| 21 | `shear_udl_ss` | `(w: float, L: float) -> float` | `float (N)` | wL/2 |
| 22 | `select_bar_combination` | `(Ast_req: float, available_dias: list[float]) -> list[tuple[int,float]]` | `list` | Optimal bar selection |
| 23 | `check_bar_fit` | `(n_bars: int, dia: float, b: float, cover: float, min_spacing: float) -> bool` | `bool` | Can bars fit in width? |
| 24 | `interpolate_table` | `(x: float, x_vals: list[float], y_vals: list[float]) -> float` | `float` | Linear interpolation (clamped) |

### 1.2 IS 456:2000 (`codes/is456/beam/`)

| # | Function | Clause | Formula | Key Params | Benchmark | Status |
|---|----------|--------|---------|------------|-----------|--------|
| **Flexure** (`flexure.py`) | | | | | |
| 1 | `calculate_mu_lim` | Cl 38.1, G-1.1 | $M_{u,lim} = 0.36 \cdot \frac{x_{u,max}}{d} \left(1 - 0.42 \cdot \frac{x_{u,max}}{d}\right) \cdot b \cdot d^2 \cdot f_{ck}$ | `b, d, fck, fy (mm, N/mm²)` | SP:16 Table C | ✅ |
| 2 | `calculate_ast_required` | Cl 38.1 | $A_{st} = \frac{M_u}{0.87 \cdot f_y \cdot (d - 0.42 \cdot x_u)}$ | `Mu_Nmm, b, d, fck, fy` | SP:16 Table 2 | ✅ |
| 3 | `design_singly_reinforced` | Cl 38.1 | Singly reinforced design flow | `b, d, fck, fy, Mu_kNm` | SP:16 Ex. 1 | ✅ |
| 4 | `design_doubly_reinforced` | Cl 38.1, G-1.2 | $A_{sc} = \frac{M_u - M_{u,lim}}{(f_{sc} - 0.446 f_{ck})(d - d')}$ | `b, d, d_prime, fck, fy, Mu_kNm` | SP:16 Ex. 3 | ✅ |
| 5 | `calculate_effective_flange_width` | Cl 23.1.2 | $b_f = \frac{l_0}{6} + b_w + 6D_f$ (T-beam) | `span, bw, Df, beam_type` | SP:24 | ✅ |
| 6 | `calculate_mu_lim_flanged` | Annex G, G-2.2 | Flanged beam limiting moment | `b, bw, Df, d, fck, fy` | SP:16 Table 58 | ✅ |
| 7 | `design_flanged_beam` | Annex G | T/L beam complete design | `bw, bf, Df, d, fck, fy, Mu` | Pillai & Menon | ✅ |
| 8 | `calculate_effective_depth_multilayer` | Cl 26.2 | Centroid depth of multi-layer bars | `layers: list[(area, depth)]` | — | ✅ |
| 9 | `compute_xu_for_given_ast` 🔲 | Cl 38.1 | $0.87 f_y A_{st} = 0.36 f_{ck} b \cdot x_u$ → $x_u$ | `Ast, b, fck, fy` | — | 🔲 |
| 10 | `calculate_mu_for_given_ast` 🔲 | Cl 38.1 | $M_u = 0.87 f_y A_{st} (d - 0.42 x_u)$ | `Ast, b, d, fck, fy` | — | 🔲 |
| **Shear** (`shear.py`) | | | | | |
| 11 | `calculate_tv` | Cl 40.1 | $\tau_v = V_u / (b \cdot d)$ | `Vu_kN, b, d` | — | ✅ |
| 12 | `design_shear` | Cl 40.1–40.4 | Complete stirrup design | `b, d, fck, fy, Vu_kN, Ast` | SP:16 Table 62 | ✅ |
| 13 | `enhanced_shear_strength` | Cl 40.5 | $\tau_c' = \tau_c \cdot 2d/a_v$ for $a_v < 2d$ | `tau_c, av, d` | — | ✅ |
| 14 | `round_to_practical_spacing` | Cl 26.5.1.5 | Round to standard spacing | `spacing_mm` | — | ✅ |
| 15 | `select_stirrup_diameter` | Cl 26.5.1.6 | Select stirrup bar | `Asv_req, n_legs` | — | ✅ |
| 16 | `calculate_vc` 🔲 | Cl 40.2 | $V_c = \tau_c \cdot b \cdot d$ | `fck, pt, b, d` | Table 19 | 🔲 |
| 17 | `calculate_vs_required` 🔲 | Cl 40.4 | $V_{us} = V_u - V_c$ | `Vu, Vc` | — | 🔲 |
| 18 | `stirrup_spacing_from_vs` 🔲 | Cl 40.4(a) | $s_v = \frac{0.87 f_y A_{sv} d}{V_{us}}$ | `fy, Asv, d, Vus` | — | 🔲 |
| 19 | `inclined_bar_shear_capacity` 🔲 | Cl 40.4(b) | $V_{us} = 0.87 f_y A_{sv} d (\sin\alpha + \cos\alpha) / s_v$ | `fy, Asv, d, alpha, sv` | — | 🔲 |
| **Torsion** (`torsion.py`) | | | | | |
| 20 | `calculate_equivalent_shear` | Cl 41.3.1 | $V_e = V_u + 1.6 \cdot T_u / b$ | `Vu_kN, Tu_kNm, b` | — | ✅ |
| 21 | `calculate_equivalent_moment` | Cl 41.4.2 | $M_e = M_u + M_t$; $M_t = T_u(1 + D/b)/1.7$ | `Mu_kNm, Tu_kNm, b, D` | — | ✅ |
| 22 | `calculate_torsion_shear_stress` | Cl 41.3 | $\tau_{ve} = V_e / (b \cdot d)$ | `Ve_kN, b, d` | — | ✅ |
| 23 | `calculate_torsion_stirrup_area` | Cl 41.4.3 | $A_{sv} = \frac{T_u \cdot s_v}{b_1 \cdot d_1 \cdot 0.87 f_y} + \frac{V_u \cdot s_v}{2.5 d_1 \cdot 0.87 f_y}$ | `Tu, Vu, sv, b1, d1, fy` | SP:34 | ✅ |
| 24 | `calculate_longitudinal_torsion_steel` | Cl 41.4.2 | $A_{sl} = \frac{M_e}{0.87 f_y (d - 0.42 x_u)}$ | `Me, d, fck, fy` | — | ✅ |
| 25 | `design_torsion` | Cl 41 | Complete torsion design | `b, D, d, fck, fy, Mu, Vu, Tu` | SP:34 Ex. | ✅ |
| **Detailing** (`detailing.py`) | | | | | |
| 26 | `get_bond_stress` | Cl 26.2.1.1 | Table 26.2.1.1 lookup | `fck, bar_type` | IS 456 Table | ✅ |
| 27 | `calculate_development_length` | Cl 26.2.1 | $L_d = \frac{\phi \cdot \sigma_s}{4 \cdot \tau_{bd}}$ | `bar_dia, fck, fy, bar_type` | SP:16 Table 65 | ✅ |
| 28 | `calculate_lap_length` | Cl 26.2.5 | $L_s = k \cdot L_d$ (k = 1.0 for < 50% lapped) | `bar_dia, fck, fy, percent_lapped` | — | ✅ |
| 29 | `get_min_bend_radius` | Cl 26.2.2.1 | 4d for ≤ 20mm, 5d for > 20mm | `bar_dia, bar_type` | — | ✅ |
| 30 | `calculate_standard_hook` | Cl 26.2.2.1 | Hook dimensions per bend angle | `bar_dia, hook_angle` | — | ✅ |
| 31 | `calculate_anchorage_length` | Cl 26.2.2 | $L_a = L_d - \text{hook allowance}$ | `Ld, hook_type` | — | ✅ |
| 32 | `calculate_stirrup_anchorage` | Cl 26.5.1.6 | Stirrup end anchorage | `bar_dia, enclosed_by_hook` | — | ✅ |
| 33 | `check_anchorage_at_simple_support` | Cl 26.2.3.3 | $L_d \leq \frac{M_1}{V} + L_0$ | `Ld, M1, V, L0` | — | ✅ |
| 34 | `calculate_bar_spacing` | Cl 26.3.3 | Spacing from geometry | `b, n_bars, bar_dia, cover` | — | ✅ |
| 35 | `check_min_spacing` | Cl 26.3.3 | $s_{min} \geq \max(d_b, d_{agg}+5, 25)$ | `spacing, bar_dia, agg_size` | — | ✅ |
| 36 | `check_side_face_reinforcement` | Cl 26.5.1.3 | Required when D > 750mm | `D, bw` | — | ✅ |
| 37 | `select_bar_arrangement` | Cl 26.3 | Optimal bars for req'd area | `Ast_req, b, cover` | — | ✅ |
| 38 | `get_stirrup_legs` | — | Legs needed for beam width | `b` | — | ✅ |
| 39 | `format_bar_callout` | — | "4T20" format | `count, diameter` | — | ✅ |
| 40 | `format_stirrup_callout` | — | "2L8@150" format | `legs, dia, spacing` | — | ✅ |
| 41 | `create_beam_detailing` | Cl 26 | Complete detailing result | `flexure_result, shear_result, ...` | — | ✅ |
| 42 | `clear_cover_for_exposure` 🔲 | Cl 26.4.1, Table 16 | Cover from exposure class | `exposure_class` | IS 456 Table 16 | 🔲 |
| 43 | `curtailment_point` 🔲 | Cl 26.2.3 | Bar cutoff location | `span, Mu_diag, Mu_bar` | SP:34 Fig. 5 | 🔲 |
| **Serviceability** (`serviceability.py`) | | | | | |
| 44 | `check_deflection_span_depth` | Cl 23.2 | Basic L/d ratio with modifiers | `span, d, pt, pc, fs, fy, support` | IS 456 Fig. 4–6 | ✅ |
| 45 | `check_crack_width` | Annex F | Annex F crack width formula | `bar_dia, spacing, cover, strain` | Annex F Ex. | ✅ |
| 46 | `calculate_cracking_moment` | Cl 43.1 | $M_{cr} = f_r \cdot I_g / y_t$ | `fck, b, D` | — | ✅ |
| 47 | `calculate_gross_moment_of_inertia` | — | $I_g = bD^3/12$ | `b, D` | — | ✅ |
| 48 | `calculate_cracked_moment_of_inertia` | Cl 43.1 | Transformed section calculation | `b, d, xu, m, Ast, Asc` | — | ✅ |
| 49 | `calculate_effective_moment_of_inertia` | Cl 43.1 | Branson's equation | `Mcr, Ma, Ig, Icr` | — | ✅ |
| 50 | `get_long_term_deflection_factor` | Cl 43.1 | Kcp factor | `Asc, Ast, duration_months` | IS 456 Fig. 6 | ✅ |
| 51 | `calculate_short_term_deflection` | Cl 43.1 | $δ_{st}$ from Ieff | `M, L, EI_eff, support` | — | ✅ |
| 52 | `check_deflection_level_b` | Cl 43.1 | Full elastic deflection (Level B) | `detailed params` | ACI 318 14.0 | ✅ |
| 53 | `check_deflection_level_c` | Cl 43.1 | Long-term (creep+shrinkage) Level C | `detailed params` | — | ✅ |
| 54 | `get_creep_coefficient` | Cl 6.2.5.1 | θ from age at loading | `age_days` | IS 456 Table 6 | ✅ |
| 55 | `calculate_shrinkage_curvature` | Cl 43.1(d) | Shrinkage curvature | `epsilon_sh, Ast, Asc, b, d` | — | ✅ |
| 56 | `calculate_creep_deflection` | Cl 43.1(c) | Long-term creep deflection | `delta_i, theta` | — | ✅ |
| 57 | `calculate_shrinkage_deflection` | Cl 43.1(d) | Shrinkage-induced deflection | `ψ_sh, L, support` | — | ✅ |

### 1.3 ACI 318-19 (`codes/aci318/beam/`)

| # | Function | Section | Formula | Key Params | Benchmark |
|---|----------|---------|---------|------------|-----------|
| **Flexure** (`flexure.py`) | | | | |
| 1 | `calculate_phi_mn` | §21.2, §22.2 | $\phi M_n = \phi \cdot [A_s f_y (d - a/2)]$; $a = A_s f_y / (0.85 f'_c b)$ | `b, d, fc_prime, fy, As (in, psi or mm, MPa)` | ACI Handbook Ex. |
| 2 | `stress_block_depth_a` | §22.2.2 | $a = \beta_1 \cdot c$ | `c, fc_prime` | — |
| 3 | `beta_1` | §22.2.2.4.3 | $\beta_1 = 0.85 - 0.05(f'_c - 28)/7 \geq 0.65$ | `fc_prime (MPa)` | Table 22.2.2.4.3 |
| 4 | `neutral_axis_depth_c` | §22.2 | $c = a / \beta_1$ | `a, fc_prime` | — |
| 5 | `tension_steel_required` | §22.2 | $A_s = M_u / [\phi f_y(d - a/2)]$ (iterative) | `Mu, b, d, fc_prime, fy` | — |
| 6 | `compression_steel_required` | §22.2 | When $M_u > \phi M_{n,max}$ | `Mu, b, d, d_prime, fc_prime, fy` | — |
| 7 | `maximum_steel_strain_check` | §9.3.3 | $\varepsilon_t \geq 0.004$ (tension-controlled) | `c, d` | — |
| 8 | `design_singly_reinforced_aci` | §9.5 | Complete singly reinforced design | `b, d, fc_prime, fy, Mu` | ACI SP-17 |
| 9 | `design_doubly_reinforced_aci` | §9.5 | Compression steel design | `b, d, d_prime, fc_prime, fy, Mu` | ACI SP-17 |
| 10 | `effective_flange_width_aci` | §6.3.2 | $b_e = \min(L/4, b_w + 16h_f, \text{center-to-center})$ | `L, bw, hf, spacing` | — |
| 11 | `design_flanged_beam_aci` | §22.2 | T-beam design | `bw, be, hf, d, fc_prime, fy, Mu` | — |
| 12 | `min_tension_steel_aci` | §9.6.1.2 | $A_{s,min} = \max(\frac{3\sqrt{f'_c}}{f_y}, \frac{200}{f_y}) b_w d$ | `bw, d, fc_prime, fy` | — |
| 13 | `max_reinforcement_ratio_aci` | §9.3.3 | $\rho_{max}$ for tension-controlled | `fc_prime, fy` | — |
| 14 | `strength_reduction_factor` | §21.2 | $\phi$ from strain (0.65–0.90) | `epsilon_t` | Table 21.2.2 |
| **Shear** (`shear.py`) | | | | |
| 15 | `concrete_shear_vc` | §22.5.5 | $V_c = 0.17\lambda\sqrt{f'_c} b_w d$ (simplified) | `fc_prime, bw, d, lambda_factor` | — |
| 16 | `concrete_shear_detailed` | §22.5.5.1 | $V_c = [0.16\lambda\sqrt{f'_c} + 17\rho_w V_u d/M_u] b_w d$ | `fc_prime, bw, d, rho_w, Vu, Mu` | — |
| 17 | `stirrup_capacity_vs` | §22.5.10 | $V_s = A_v f_{yt} d / s$ | `Av, fyt, d, s` | — |
| 18 | `required_stirrup_spacing` | §22.5.10 | $s = A_v f_{yt} d / V_s$ | `Av, fyt, d, Vs` | — |
| 19 | `max_vs_limit` | §22.5.1.2 | $V_s \leq 0.66\sqrt{f'_c} b_w d$ | `fc_prime, bw, d` | — |
| 20 | `min_shear_reinforcement_aci` | §9.6.3 | $A_{v,min} = \max(0.062\sqrt{f'_c}, 0.35) b_w s / f_{yt}$ | `fc_prime, bw, s, fyt` | — |
| 21 | `max_stirrup_spacing_aci` | §9.7.6.2 | $s_{max} = \min(d/2, 600)$ or $d/4$ if $V_s > 0.33\sqrt{f'_c}b_wd$ | `d, Vs, fc_prime, bw` | — |
| 22 | `design_shear_aci` | §22.5 | Complete shear design | `bw, d, fc_prime, fy, Vu, As` | ACI Handbook |
| **Torsion** (`torsion.py`) | | | | |
| 23 | `torsion_threshold_aci` | §22.7.4 | $T_{th} = \phi\lambda\sqrt{f'_c}(A_{cp}^2/p_{cp})/12$ | `fc_prime, Acp, pcp` | — |
| 24 | `torsional_cracking_torque` | §22.7.5 | $T_{cr} = 0.33\lambda\sqrt{f'_c}(A_{cp}^2/p_{cp})$ | `fc_prime, Acp, pcp` | — |
| 25 | `transverse_torsion_reinf_aci` | §22.7.6 | $A_t/s = T_n/(2 A_o f_{yt} \cot\theta)$ | `Tn, Ao, fyt, theta` | — |
| 26 | `longitudinal_torsion_reinf_aci` | §22.7.6 | $A_l = T_n p_h/(2 A_o f_y \cot\theta)$ | `Tn, ph, Ao, fy, theta` | — |
| 27 | `combined_shear_torsion_check` | §22.7.7 | Interaction check | `Vu, Tu, Vc, b, d, Aoh` | — |
| 28 | `design_torsion_aci` | §22.7 | Complete torsion design | `b, D, d, fc_prime, fy, Mu, Vu, Tu` | — |
| **Detailing** (`detailing.py`) | | | | |
| 29 | `development_length_tension_aci` | §25.4.2 | $l_d = \frac{f_y \psi_t \psi_e \psi_s \psi_g}{1.1\lambda\sqrt{f'_c}} \cdot \frac{d_b}{c_b + K_{tr}/d_b}$ | `db, fc_prime, fy, cover, spacing, ψ-factors` | — |
| 30 | `development_length_compression_aci` | §25.4.9 | $l_{dc} = \max(0.24 f_y d_b / (\lambda\sqrt{f'_c}), 0.043 f_y d_b)$ | `db, fc_prime, fy` | — |
| 31 | `lap_splice_length_aci` | §25.5 | Class A/B splice length | `db, fc_prime, fy, splice_class` | — |
| 32 | `standard_hook_development_aci` | §25.4.3 | $l_{dh} = f_y \psi_e \psi_r \psi_o \psi_c d_b / (55\lambda\sqrt{f'_c})$ | `db, fc_prime, fy` | — |
| 33 | `min_clear_spacing_aci` | §25.2.1 | $s_{min} = \max(d_b, 25\text{mm}, 4/3 d_{agg})$ | `db, agg_size` | — |
| 34 | `clear_cover_aci` | Table 20.6.1.3.1 | Cover from exposure/element | `exposure_class, element` | — |
| 35 | `create_beam_detailing_aci` | §25 | Complete detailing result | Multi | — |
| **Serviceability** (`serviceability.py`) | | | | |
| 36 | `min_thickness_aci` | Table 9.3.1.1 | Minimum thickness (deflection) | `span, support_condition` | — |
| 37 | `immediate_deflection_aci` | §24.2.3 | Branson's equation (ACI variant) | `Ma, Mcr, Ig, Icr, Ec, L, support` | ACI SP-17 |
| 38 | `long_term_deflection_factor_aci` | §24.2.4 | $\lambda_\Delta = \xi / (1 + 50\rho')$ | `rho_prime, xi` | — |
| 39 | `check_crack_width_aci` | §24.3 | $s_{max} = \min(380 \cdot 280/f_s - 2.5c_c, 300 \cdot 280/f_s)$ | `fs, cc` | Frosch method |
| 40 | `steel_stress_under_service_aci` | §24.3 | $f_s = M_a / (j d A_s)$ or $2/3 f_y$ | `Ma, jd, As, fy` | — |
| 41 | `check_deflection_aci` | §24.2 | Complete deflection check | Multi | — |

### 1.4 Eurocode 2 — EN 1992-1-1 (`codes/ec2/beam/`)

| # | Function | Section | Formula | Key Params | Benchmark |
|---|----------|---------|---------|------------|-----------|
| **Flexure** (`flexure.py`) | | | | |
| 1 | `calculate_mrd` | §6.1 | $M_{Rd} = A_s f_{yd} (d - 0.4x)$; parabolic-rectangular block | `b, d, fck, fyk, As` | Worked examples |
| 2 | `stress_block_factor_lambda` | §3.1.7(3) | $\lambda = 0.8$ for $f_{ck} \leq 50$, else $0.8 - (f_{ck}-50)/400$ | `fck` | — |
| 3 | `stress_block_factor_eta` | §3.1.7(3) | $\eta = 1.0$ for $f_{ck} \leq 50$, else $1.0 - (f_{ck}-50)/200$ | `fck` | — |
| 4 | `limiting_xu_d` | §5.5(4) | $x_u/d \leq 0.45$ for $f_{ck} \leq \text{C50}$, else $0.35$ | `fck` | — |
| 5 | `tension_steel_required_ec2` | §6.1 | Iterative from $M_{Ed} \leq M_{Rd}$ | `Med, b, d, fck, fyk` | — |
| 6 | `compression_steel_required_ec2` | §6.1 | When $M_{Ed} > M_{Rd,lim}$ | `Med, b, d, d_prime, fck, fyk` | — |
| 7 | `design_singly_reinforced_ec2` | §6.1 | Complete singly reinforced | `b, d, fck, fyk, Med` | Mosley et al. |
| 8 | `design_doubly_reinforced_ec2` | §6.1 | Doubly reinforced design | `b, d, d_prime, fck, fyk, Med` | — |
| 9 | `effective_flange_width_ec2` | §5.3.2.1 | $b_{eff} = b_w + \sum b_{eff,i}$; $b_{eff,i} = 0.2 b_i + 0.1 l_0 \leq 0.2 l_0 \leq b_i$ | `bw, b1, b2, l0` | — |
| 10 | `design_flanged_beam_ec2` | §6.1 | T/L beam design | `bw, beff, hf, d, fck, fyk, Med` | — |
| 11 | `min_tension_steel_ec2` | §9.2.1.1 | $A_{s,min} = \max(0.26 \frac{f_{ctm}}{f_{yk}}, 0.0013) b_t d$ | `bt, d, fctm, fyk` | — |
| 12 | `max_tension_steel_ec2` | §9.2.1.1 | $A_{s,max} = 0.04 A_c$ | `b, D` | — |
| **Shear** (`shear.py`) | | | | |
| 13 | `concrete_shear_vrd_c` | §6.2.2 | $V_{Rd,c} = [C_{Rd,c} k (100\rho_l f_{ck})^{1/3} + k_1 \sigma_{cp}] b_w d$ | `fck, bw, d, Asl, Ncp` | — |
| 14 | `concrete_shear_minimum` | §6.2.2 | $V_{Rd,c,min} = (v_{min} + k_1 \sigma_{cp}) b_w d$ | `fck, d, bw` | — |
| 15 | `max_shear_vrd_max` | §6.2.3 | $V_{Rd,max} = \alpha_{cw} b_w z \nu_1 f_{cd} / (\cot\theta + \tan\theta)$ | `fck, bw, z, theta` | — |
| 16 | `required_shear_reinforcement_ec2` | §6.2.3 | $A_{sw}/s = V_{Ed} / (z f_{ywd} \cot\theta)$ | `Ved, z, fywd, theta` | — |
| 17 | `min_shear_reinforcement_ec2` | §9.2.2(5) | $\rho_{w,min} = 0.08\sqrt{f_{ck}} / f_{yk}$ | `fck, fyk` | — |
| 18 | `max_stirrup_spacing_ec2` | §9.2.2(6) | $s_{l,max} = 0.75d(1 + \cot\alpha)$ | `d, alpha` | — |
| 19 | `strut_angle_theta_ec2` | §6.2.3(2) | $1.0 \leq \cot\theta \leq 2.5$ (optimize) | `Ved, VRd_max_range` | — |
| 20 | `design_shear_ec2` | §6.2 | Complete shear design | `bw, d, fck, fyk, Ved, Asl` | EC2 Worked Ex. |
| **Torsion** (`torsion.py`) | | | | |
| 21 | `torsion_cracking_trd_c` | §6.3.2(5) | $T_{Rd,c}$ from thin-wall analogy | `fck, tef, Ak` | — |
| 22 | `max_torsion_trd_max` | §6.3.2(4) | $T_{Rd,max} = 2 \nu \alpha_{cw} f_{cd} A_k t_{ef,i} \sin\theta\cos\theta$ | `fck, Ak, tef, theta` | — |
| 23 | `torsion_shear_interaction` | §6.3.2(4) | $T_{Ed}/T_{Rd,max} + V_{Ed}/V_{Rd,max} \leq 1.0$ | `Ted, Trd_max, Ved, Vrd_max` | — |
| 24 | `transverse_torsion_reinf_ec2` | §6.3.2(2) | $A_{sw}/s = T_{Ed} / (2 A_k f_{ywd} \cot\theta)$ | `Ted, Ak, fywd, theta` | — |
| 25 | `longitudinal_torsion_reinf_ec2` | §6.3.2(3) | $\sum A_{sl} f_{yd} / u_k = T_{Ed} \cot\theta / (2 A_k)$ | `Ted, Ak, uk, fyd, theta` | — |
| 26 | `design_torsion_ec2` | §6.3 | Complete torsion design | `b, D, d, fck, fyk, Med, Ved, Ted` | — |
| **Detailing** (`detailing.py`) | | | | |
| 27 | `bond_strength_fbd` | §8.4.2 | $f_{bd} = 2.25 \eta_1 \eta_2 f_{ctd}$ | `fck, eta1, eta2` | — |
| 28 | `basic_anchorage_length` | §8.4.3 | $l_{b,rqd} = (\phi/4)(\sigma_{sd}/f_{bd})$ | `phi, sigma_sd, fbd` | — |
| 29 | `design_anchorage_length_ec2` | §8.4.4 | $l_{bd} = \alpha_1\alpha_2\alpha_3\alpha_4\alpha_5 l_{b,rqd} \geq l_{b,min}$ | `lb_rqd, alpha_factors` | — |
| 30 | `lap_length_ec2` | §8.7.3 | $l_0 = \alpha_1\alpha_2\alpha_3\alpha_5\alpha_6 l_{b,rqd} \geq l_{0,min}$ | `lb_rqd, alpha_factors` | — |
| 31 | `min_mandrel_diameter_ec2` | §8.3 | $\phi_{m,min} = 4\phi$ for $\phi \leq 16$, $7\phi$ otherwise | `phi` | — |
| 32 | `min_clear_spacing_ec2` | §8.2 | $s_{min} = \max(\phi, d_g + 5, 20)$ | `phi, dg` | — |
| 33 | `cover_from_exposure_ec2` | §4.4.1 | Minimum cover from exposure class table | `exposure_class, structural_class` | Table 4.4N |
| 34 | `create_beam_detailing_ec2` | §8,§9 | Complete detailing result | Multi | — |
| **Serviceability** (`serviceability.py`) | | | | |
| 35 | `span_depth_ratio_ec2` | §7.4.2 | $l/d = K[11 + 1.5\sqrt{f_{ck}}\rho_0/\rho + 3.2\sqrt{f_{ck}}(\rho_0/\rho - 1)^{3/2}]$ | `fck, rho, rho_prime, K` | Table 7.4N |
| 36 | `crack_width_wk_ec2` | §7.3.4 | $w_k = s_{r,max}(\varepsilon_{sm} - \varepsilon_{cm})$ | `sr_max, epsilon_sm, epsilon_cm` | — |
| 37 | `max_crack_spacing_sr_max` | §7.3.4(3) | $s_{r,max} = k_3 c + k_1 k_2 k_4 \phi / \rho_{p,eff}$ | `c, phi, rho_p_eff, k_factors` | — |
| 38 | `mean_strain_difference` | §7.3.4(2) | $\varepsilon_{sm} - \varepsilon_{cm} = [\sigma_s - k_t f_{ct,eff}(1+\alpha_e\rho_{p,eff})/\rho_{p,eff}] / E_s$ | Complex | — |
| 39 | `check_crack_control_ec2` | §7.3 | Table 7.2N/7.3N check or direct calc | `exposure, wk, bar_dia, spacing` | — |
| 40 | `deflection_by_integration_ec2` | §7.4.3 | Rigorous method via curvature integration | `M_diagram, EI_1, EI_2, L` | — |
| 41 | `creep_coefficient_ec2` | §3.1.4, Annex B | $\varphi(\infty, t_0) = \varphi_{RH} \beta(f_{cm}) \beta(t_0)$ | `fck, RH, h0, t0, cement_class` | Table 3.1 |
| 42 | `shrinkage_strain_ec2` | §3.1.4(6) | $\varepsilon_{cs} = \varepsilon_{cd} + \varepsilon_{ca}$ | `fck, RH, h0, age, cement_class` | — |
| 43 | `check_deflection_ec2` | §7.4 | Complete deflection check | Multi | EC2 Handbook |

---

## 2. COLUMN Functions

### 2.1 Shared / Code-Agnostic (`codes/common/column/`)

| # | Function | Signature | Return | Description |
|---|----------|-----------|--------|-------------|
| 1 | `gross_area_rectangular` | `(b: float, D: float) -> float` | `float (mm²)` | Ag = b × D |
| 2 | `gross_area_circular` | `(diameter: float) -> float` | `float (mm²)` | Ag = π·d²/4 |
| 3 | `slenderness_ratio` | `(le: float, r: float) -> float` | `float` | λ = le/r |
| 4 | `radius_of_gyration` | `(I: float, A: float) -> float` | `float (mm)` | r = √(I/A) |
| 5 | `euler_buckling_load` | `(Ec_I: float, le: float) -> float` | `float (N)` | Pcr = π²EI/le² |
| 6 | `area_from_bars` | `(n_bars: int, dia: float) -> float` | `float (mm²)` | Asc = n·π·d²/4 |
| 7 | `reinforcement_ratio_column` | `(Ast: float, Ag: float) -> float` | `float` | p = Ast/Ag |
| 8 | `second_moment_rectangular` | `(b: float, D: float) -> float` | `float (mm⁴)` | I = bD³/12 |
| 9 | `second_moment_circular` | `(diameter: float) -> float` | `float (mm⁴)` | I = πd⁴/64 |
| 10 | `pm_point_from_strain` | `(strain_profile, section, bars, fck, fy, stress_fn) -> tuple[float,float]` | `(P, M)` | Single P-M point from strain |
| 11 | `generate_pm_curve` | `(section, bars, fck, fy, stress_fn, n_points) -> list[tuple]` | `list` | N points on P-M curve |
| 12 | `bresler_reciprocal` | `(Pux: float, Puy: float, Pu0: float) -> float` | `float (kN)` | 1/Pu = 1/Pux + 1/Puy − 1/Pu0 |
| 13 | `bresler_load_contour` | `(Mux: float, Muy: float, Mux1: float, Muy1: float, alpha_n: float) -> float` | `float` | (Mux/Mux1)^αn + (Muy/Muy1)^αn |
| 14 | `effective_length_factor` | `(top_restraint: str, bottom_restraint: str) -> float` | `float` | k from end conditions |

### 2.2 IS 456:2000 (`codes/is456/column/`)

| # | Function | Clause | Formula | Key Params | Benchmark | Status |
|---|----------|--------|---------|------------|-----------|--------|
| **Classification & Geometry** | | | | | |
| 1 | `effective_length` | Table 28 | k·L (7 end conditions) | `L_unsupported, end_condition` | IS 456 Table 28 | ✅ |
| 2 | `classify_column` | Cl 25.1.2 | Short if le/D < 12 | `le, D` | — | ✅ |
| 3 | `min_eccentricity` | Cl 25.4 | $e_{min} = \max(l/500 + D/30, 20)$ | `l_unsupported, D` | — | ✅ |
| **Axial** | | | | | |
| 4 | `short_axial_capacity` | Cl 39.3 | $P_u = 0.4 f_{ck} A_c + 0.67 f_y A_{sc}$ | `fck, fy, Ag, Ast` | SP:16 Chart 25 | ✅ |
| 5 | `design_column_axial` 🔲 | Cl 39.3 | Find Ast for given Pu | `b, D, fck, fy, Pu` | SP:16 | 🔲 |
| **Uniaxial Bending** | | | | | |
| 6 | `design_short_column_uniaxial` | Cl 39.5 | P-M interaction check + Ast | `b, D, d_prime, fck, fy, Pu, Mu` | SP:16 Charts 27–38 | ✅ |
| 7 | `pm_interaction_curve` | Cl 39.5 | N points on P-M diagram | `b, D, d_prime, fck, fy, Ast` | SP:16 | ✅ |
| **Biaxial Bending** | | | | | |
| 8 | `biaxial_bending_check` | Cl 39.6 | $(M_{ux}/M_{ux1})^{\alpha_n} + (M_{uy}/M_{uy1})^{\alpha_n} \leq 1.0$ | `Pu, Mux, Muy, Mux1, Muy1, Puz` | SP:16 Chart 64 | ✅ |
| 9 | `calculate_puz` | Cl 39.6 | $P_{uz} = 0.45 f_{ck} A_c + 0.75 f_y A_{sc}$ | `fck, fy, Ag, Ast` | — | ✅ (internal `_calculate_puz`) |
| 10 | `calculate_alpha_n` | Cl 39.6 | $\alpha_n = f(P_u/P_{uz})$, 1.0–2.0 linear | `Pu, Puz` | — | ✅ (embedded) |
| **Slenderness** | | | | | |
| 11 | `calculate_additional_moment` | Cl 39.7.1 | $M_{ax} = P_u \cdot D \cdot (l_e/D)^2 / 2000$ | `Pu, le, D` | SP:16 | ✅ |
| 12 | `design_long_column` | Cl 39.7 | Complete slender column design | `b, D, fck, fy, Pu, Mu, le` | SP:16 | ✅ |
| 13 | `moment_reduction_factor` 🔲 | Cl 39.7.1.1 | $k = \frac{P_{uz} - P_u}{P_{uz} - P_b} \leq 1$ | `Pu, Puz, Pb` | — | 🔲 |
| **Helical** | | | | | |
| 14 | `check_helical_reinforcement` | Cl 39.4 | 5% capacity increase check | `pitch, Dcore, helix_dia, fck, fy` | — | ✅ |
| 15 | `helical_pitch_limits` 🔲 | Cl 26.5.3.2 | $25 \leq p \leq 75$ mm, $p \leq D_c/6$ | `Dcore` | — | 🔲 |
| **Detailing** | | | | | |
| 16 | `check_longitudinal_limits` | Cl 26.5.3.1 | 0.8% ≤ p ≤ 4% (6% at laps) | `Ast, Ag` | — | ✅ |
| 17 | `get_min_bar_count` | Cl 26.5.3.1 | 4 (rect) or 6 (circular) | `is_circular` | — | ✅ |
| 18 | `check_min_bar_diameter` | Cl 26.5.3.1 | ≥ 12mm | `bar_dia` | — | ✅ |
| 19 | `calculate_tie_diameter` | Cl 26.5.3.2(c) | $\max(\phi_{long}/4, 6)$ | `max_long_bar_dia` | — | ✅ |
| 20 | `calculate_tie_spacing` | Cl 26.5.3.2(c) | $\min(D_{least}, 16\phi_{long}, 300)$ | `D_least, min_bar_dia` | — | ✅ |
| 21 | `check_bar_spacing` | Cl 26.5.3.1 | ≤ 300mm face-to-face | `bar_positions, b, D` | — | ✅ |
| 22 | `needs_cross_ties` | Cl 26.5.3.2 | When spacing > 48·tie_dia | `bar_spacing, tie_dia` | — | ✅ |
| 23 | `create_column_detailing` | Cl 26.5.3 | Complete detailing result | Multi | — | ✅ |
| **Ductile (IS 13920)** | | | | | |
| 24 | `check_column_geometry` | IS 13920 Cl 7.1 | Min 300mm, b/D > 0.4 | `b, D` | — | ✅ |
| 25 | `get_min_longitudinal_steel` | IS 13920 Cl 7.2 | 0.8% of Ag | — | — | ✅ |
| 26 | `get_max_longitudinal_steel` | IS 13920 Cl 7.2 | 4% of Ag | — | — | ✅ |
| 27 | `calculate_special_confining_spacing` | IS 13920 Cl 7.4 | $\leq \min(B/4, 75)$ | `b, bar_dia` | — | ✅ |
| 28 | `calculate_confining_length` | IS 13920 Cl 7.4 | $l_o \geq \max(D, H_{clear}/6, 450)$ | `D, H_clear` | — | ✅ |
| 29 | `calculate_ash_required` | IS 13920 Cl 7.4 | $A_{sh} = 0.18 s h f_{ck}/f_y (A_g/A_k - 1)$ | `s, h, fck, fy, Ag, Ak` | — | ✅ |
| 30 | `check_column_ductility` | IS 13920 Cl 7 | Complete ductility check | Multi | — | ✅ |
| 31 | `check_scwb` | IS 13920 Cl 7.2.1 | Strong-column-weak-beam | `Mc_sum, Mb_sum` | — | ✅ |
| 32 | `design_unified_column` 🔲 | Cl 39 | Single entry: axial→uniaxial→biaxial→slender | All | — | 🔲 |

### 2.3 ACI 318-19 (`codes/aci318/column/`)

| # | Function | Section | Formula | Key Params | Benchmark |
|---|----------|---------|---------|------------|-----------|
| **Classification & Geometry** | | | | |
| 1 | `classify_column_aci` | §6.2.5 | Nonsway: $kl_u/r \leq 22$; Sway: $kl_u/r \leq 22$ | `k, lu, r` | — |
| 2 | `effective_length_factor_aci` | §R6.2.5 | k from alignment charts (Jackson-Moreland) | `EI_col, EI_beam, psi_top, psi_bottom` | — |
| 3 | `slenderness_effects_needed` | §6.2.5 | Check if slenderness can be neglected | `klu_r, M1_M2` | — |
| **Axial** | | | | |
| 4 | `axial_capacity_aci` | §22.4.2 | $\phi P_{n(max)} = \phi \cdot 0.80[0.85 f'_c (A_g - A_{st}) + f_y A_{st}]$ | `fc_prime, fy, Ag, Ast` | ACI SP-17 |
| 5 | `design_column_axial_aci` | §22.4 | Find Ast for given Pu | `b, D, fc_prime, fy, Pu` | — |
| **Uniaxial Bending** | | | | |
| 6 | `phi_pn_mn_aci` | §22.4 | P-M capacity from strain compatibility | `b, D, d_prime, fc_prime, fy, Ast, strain` | — |
| 7 | `pm_interaction_curve_aci` | §22.4 | Full P-M diagram | `b, D, d_prime, fc_prime, fy, Ast, n_points` | ACI SP-17 |
| 8 | `strength_reduction_factor_column` | §21.2.2 | $\phi$ = 0.65 (tied), 0.75 (spiral); transition | `Pn, Ag, fc_prime, column_type` | — |
| 9 | `design_uniaxial_aci` | §22.4 | Find Ast for (Pu, Mu) | `b, D, d_prime, fc_prime, fy, Pu, Mu` | ACI Handbook |
| **Biaxial Bending** | | | | |
| 10 | `biaxial_reciprocal_aci` | §R22.4 | Bresler reciprocal: $1/\phi P_n = 1/\phi P_{nx} + 1/\phi P_{ny} - 1/\phi P_0$ | `Pu, Pux, Puy, Pu0` | — |
| 11 | `biaxial_load_contour_aci` | §R22.4 | $(M_{ux}/M_{ux0})^{1.5} + (M_{uy}/M_{uy0})^{1.5} \leq 1.0$ | `Mux, Muy, Mux0, Muy0` | — |
| **Slenderness** | | | | |
| 12 | `moment_magnifier_nonsway` | §6.6.4.5 | $\delta_{ns} = C_m / (1 - P_u/(0.75 P_c)) \geq 1.0$ | `Cm, Pu, Pc` | — |
| 13 | `moment_magnifier_sway` | §6.6.4.6 | $\delta_s = \Delta_o P_u / (V_{us} l_c)$ or Q-factor | `Q, delta_0, Pu, Vus, lc` | — |
| 14 | `calculate_cm` | §6.6.4.5.3 | $C_m = 0.6 + 0.4 M_1/M_2 \geq 0.4$ | `M1, M2` | — |
| 15 | `critical_buckling_load_aci` | §6.6.4.4 | $P_c = \pi^2 EI_{eff} / (kl_u)^2$ | `EI_eff, k, lu` | — |
| 16 | `effective_ei_aci` | §6.6.4.4.2 | $EI = \frac{0.2 E_c I_g + E_s I_{se}}{1 + \beta_{dns}}$ or $0.4 E_c I_g / (1+\beta_{dns})$ | `Ec, Ig, Es, Ise, beta_dns` | — |
| 17 | `design_slender_column_aci` | §6.6.4 | Complete slender column | Multi | ACI SP-17 |
| **Detailing** | | | | |
| 18 | `min_steel_ratio_aci` | §10.6.1 | $A_{st,min} = 0.01 A_g$ | `Ag` | — |
| 19 | `max_steel_ratio_aci` | §10.6.1 | $A_{st,max} = 0.08 A_g$ | `Ag` | — |
| 20 | `tie_size_aci` | §25.7.2 | #3 for ≤ #32, #4 for > #32 | `long_bar_size` | — |
| 21 | `tie_spacing_aci` | §25.7.2 | $s \leq \min(16 d_b, 48 d_{tie}, b_{least})$ | `db_long, db_tie, b_least` | — |
| 22 | `spiral_pitch_aci` | §25.7.3 | $25 \leq s \leq 75$ mm; $\rho_s \geq 0.45(A_g/A_{ch}-1)f'_c/f_{yt}$ | `Ag, Ach, fc_prime, fyt` | — |
| 23 | `splice_length_column_aci` | §10.7 | Compression splice | `db, fy` | — |
| 24 | `create_column_detailing_aci` | §10, §25 | Complete detailing | Multi | — |
| **Seismic (ACI 318 Ch. 18)** | | | | |
| 25 | `check_column_geometry_aci_seismic` | §18.7.2 | Min dimension, b/D ≥ 0.4, D ≥ 300mm | `b, D` | — |
| 26 | `confinement_hoop_spacing_aci` | §18.7.5.3 | $s_o \leq \min(b/4, 6d_b, s_x)$ | `b, db_long` | — |
| 27 | `ash_required_aci` | §18.7.5.4 | $A_{sh} = 0.3 s b_c f'_c / f_{yt} (A_g/A_{ch}-1)$ or $0.09 s b_c f'_c / f_{yt}$ | `s, bc, fc_prime, fyt, Ag, Ach` | — |
| 28 | `check_strong_column_weak_beam_aci` | §18.7.3 | $\sum M_{nc} \geq 1.2 \sum M_{nb}$ | `Mnc_sum, Mnb_sum` | — |
| 29 | `check_column_shear_aci_seismic` | §18.7.6 | Capacity-design shear | `Mpr_top, Mpr_bottom, lu` | — |
| 30 | `design_seismic_column_aci` | Ch. 18 | Complete seismic column | Multi | FEMA P-751 |

### 2.4 Eurocode 2 — EN 1992-1-1 (`codes/ec2/column/`)

| # | Function | Section | Formula | Key Params | Benchmark |
|---|----------|---------|---------|------------|-----------|
| **Classification & Geometry** | | | | |
| 1 | `effective_length_ec2` | §5.8.3.2 | $l_0 = f(k_1, k_2) \cdot l$ | `l, k1, k2, braced` | — |
| 2 | `slenderness_limit_ec2` | §5.8.3.1 | $\lambda_{lim} = 20 A B C / \sqrt{n}$ | `A, B, C, n_rel` | — |
| 3 | `classify_column_ec2` | §5.8.3.1 | $\lambda \leq \lambda_{lim}$? | `lambda, lambda_lim` | — |
| 4 | `geometric_imperfection` | §5.2(7) | $e_i = \theta_i \cdot l_0 / 2$ | `l0, theta_i` | — |
| **Axial** | | | | |
| 5 | `axial_capacity_ec2` | §6.1 | $N_{Rd} = f_{cd} A_c + f_{yd} A_s$ | `fck, fyk, Ac, As` | — |
| 6 | `design_column_axial_ec2` | §6.1 | Find As for given NEd | `b, D, fck, fyk, NEd` | — |
| **Uniaxial Bending** | | | | |
| 7 | `pm_interaction_curve_ec2` | §6.1 | Strain-compatibility P-M | `b, D, d_prime, fck, fyk, As, n_points` | EC2 Handbook |
| 8 | `design_uniaxial_ec2` | §6.1 | Find As for (NEd, MEd) | `b, D, d_prime, fck, fyk, NEd, MEd` | Mosley |
| **Biaxial Bending** | | | | |
| 9 | `biaxial_check_ec2` | §5.8.9 | $(M_{Edx}/M_{Rdx})^a + (M_{Edy}/M_{Rdy})^a \leq 1.0$ | `MEdx, MEdy, MRdx, MRdy, a` | — |
| 10 | `biaxial_exponent_a` | §5.8.9(4) | a from NED/NRd ratio (1.0–2.0) | `NEd, NRd` | — |
| **Slenderness** | | | | |
| 11 | `nominal_stiffness_method` | §5.8.7 | $EI = K_c E_{cd} I_c + K_s E_s I_s$ | `Ecd, Ic, Es, Is, Kc, Ks` | — |
| 12 | `nominal_curvature_method` | §5.8.8 | $M_{Ed} = M_{0Ed} + N_{Ed} \cdot e_2$ | `M0Ed, NEd, e2` | — |
| 13 | `curvature_e2` | §5.8.8.3 | $e_2 = (1/r) \cdot l_0^2 / c$; $c = \pi^2$ | `l0, 1_over_r` | — |
| 14 | `design_curvature_1_over_r` | §5.8.8.3 | $1/r = K_r K_\varphi (1/r_0)$ | `Kr, Kphi, fyd, d, Es` | — |
| 15 | `correction_factor_kr` | §5.8.8.3(3) | $K_r = (n_u - n)/(n_u - n_{bal})$ | `n, nu, n_bal` | — |
| 16 | `creep_factor_kphi` | §5.8.8.3(4) | $K_\varphi = 1 + \beta \varphi_{ef} \geq 1$ | `beta, phi_ef` | — |
| 17 | `design_slender_column_ec2` | §5.8 | Complete slender design | Multi | EC2 Handbook |
| **Detailing** | | | | |
| 18 | `min_steel_ratio_ec2` | §9.5.2(2) | $A_{s,min} = \max(0.1 N_{Ed}/f_{yd}, 0.002 A_c)$ | `NEd, fyd, Ac` | — |
| 19 | `max_steel_ratio_ec2` | §9.5.2(3) | $A_{s,max} = 0.04 A_c$ (0.08 at laps) | `Ac` | — |
| 20 | `link_diameter_ec2` | §9.5.3(1) | $\phi_{link} \geq \max(6, \phi_{long}/4)$ | `phi_long` | — |
| 21 | `link_spacing_ec2` | §9.5.3(3) | $s_{cl,max} = \min(20\phi_{long}, b_{min}, 400)$ | `phi_long, b_min` | — |
| 22 | `lap_length_column_ec2` | §8.7 | α₆ factor for compression laps | `lb_rqd, alpha_factors` | — |
| 23 | `create_column_detailing_ec2` | §9.5 | Complete detailing | Multi | — |
| **Seismic (EC8)** | | | | |
| 24 | `check_column_geometry_ec8` | EC8 §5.4.1.2 | Min b ≥ 250mm (DCM) | `b, D` | — |
| 25 | `confinement_zone_ec8` | EC8 §5.4.3.2 | $l_{cr} = \max(D, l_{cl}/6, 450)$ | `D, l_cl` | — |
| 26 | `confining_reinforcement_ec8` | EC8 §5.4.3.2 | $\omega_{wd} \geq 30\mu_\phi\nu_d\varepsilon_{sy,d}(b_c/b_0) - 0.035$ | Complex | — |
| 27 | `check_scwb_ec8` | EC8 §4.4.2.3 | $\sum M_{Rc} \geq 1.3 \sum M_{Rb}$ | `MRc_sum, MRb_sum` | — |
| 28 | `design_seismic_column_ec8` | EC8 §5.4 | Complete seismic column | Multi | — |
| **Circular** | | | | |
| 29 | `pm_interaction_circular_ec2` | §6.1 | Strain compatibility for circular | `diameter, cover, n_bars, bar_dia, fck, fyk` | — |
| 30 | `spiral_reinforcement_ec2` | §9.5.3 | Spiral pitch and area | `Dcore, fck, fyk` | — |
| 31 | `design_unified_column_ec2` | §6.1, §5.8 | Single entry for all column types | All | EC2 Handbook |
| 32 | `fire_resistance_column_ec2` | EN 1992-1-2 | Tabulated/simplified method | `b, D, cover, load_level` | — |

---

## 3. SLAB Functions

### 3.1 Shared / Code-Agnostic (`codes/common/slab/`)

| # | Function | Signature | Return | Description |
|---|----------|-----------|--------|-------------|
| 1 | `slab_self_weight` | `(D: float, unit_wt: float) -> float` | `float (kN/m²)` | w_sw = D × γ / 1000 |
| 2 | `total_slab_load` | `(DL: float, LL: float, gamma_DL: float, gamma_LL: float) -> float` | `float (kN/m²)` | Factored load |
| 3 | `strip_moment` | `(w: float, L: float, coeff: float) -> float` | `float (kNm/m)` | M = coeff × w × L² |
| 4 | `min_slab_depth_deflection` | `(span: float, ratio: float) -> float` | `float (mm)` | D_min = span / ratio |
| 5 | `distribution_steel_area` | `(Ast_main: float, ratio: float) -> float` | `float (mm²/m)` | Ast_dist = ratio × Ast_main |
| 6 | `punching_perimeter` | `(a: float, b: float, d: float) -> float` | `float (mm)` | bo = 2(a+d + b+d) |
| 7 | `punching_area` | `(a: float, b: float, d: float) -> float` | `float (mm²)` | (a+d)(b+d) |
| 8 | `yield_line_moment` | `(pattern: str, w: float, Lx: float, Ly: float) -> float` | `float (kNm/m)` | Yield-line theory moment |
| 9 | `hillerborg_strip_moment` | `(w: float, L: float, strip_width: float) -> float` | `float (kNm)` | Strip method moment |
| 10 | `edge_beam_torsion` | `(w: float, L: float) -> float` | `float (kNm/m)` | Torsion from slab restraint |
| 11 | `panel_aspect_ratio` | `(Lx: float, Ly: float) -> float` | `float` | r = Ly/Lx ≥ 1.0 |
| 12 | `slab_bar_spacing` | `(Ast_req: float, bar_dia: float) -> float` | `float (mm)` | s = Ab × 1000 / Ast_req |
| 13 | `effective_depth_slab` | `(D: float, cover: float, bar_dia: float) -> float` | `float (mm)` | d = D − cover − ϕ/2 |
| 14 | `temperature_shrinkage_steel` | `(b: float, D: float) -> float` | `float (mm²)` | Generic temp steel calc |
| 15 | `moment_redistribution` | `(M_elastic: float, percent: float) -> float` | `float (kNm)` | M_redistributed |
| 16 | `flat_slab_equivalent_frame` | `(w: float, L1: float, L2: float) -> dict` | `dict` | Column/middle strip moments |

### 3.2 IS 456:2000 (`codes/is456/slab/`)

| # | Function | Clause | Formula | Key Params | Benchmark |
|---|----------|--------|---------|------------|-----------|
| **One-way Slab** | | | | |
| 1 | `classify_slab` | Cl 24.1 | One-way if Ly/Lx > 2 | `Lx, Ly` | — |
| 2 | `min_thickness_oneway` | Cl 23.2, Table 4 | From L/d ratios (7, 20, 26) | `span, support, fy` | — |
| 3 | `design_oneway_slab` | Cl 24, 38 | Complete one-way slab design | `span, loads, fck, fy, support` | SP:16 |
| 4 | `bending_moment_coefficients_oneway` | Table 12 | Moment coefficients for continuous | `n_spans, end_conditions` | IS 456 Table 12 |
| 5 | `shear_force_coefficients_oneway` | Table 13 | Shear coefficients for continuous | `n_spans, end_conditions` | IS 456 Table 13 |
| 6 | `distribution_steel_is456` | Cl 26.5.2.1 | Min 0.12% (HYSD) or 0.15% (mild) | `b, D, bar_type` | — |
| 7 | `max_spacing_oneway` | Cl 26.3.3(b) | $s \leq \min(3d, 300)$ for main bars | `d` | — |
| 8 | `check_oneway_shear` | Cl 40 | τv ≤ τc (no stirrups typically) | `Vu, b, d, fck, pt` | — |
| **Two-way Slab** | | | | |
| 9 | `moment_coefficients_twoway` | Annex D, Table 26 | $M_x = \alpha_x w L_x^2$, $M_y = \alpha_y w L_x^2$ | `Ly_Lx_ratio, edge_condition` | IS 456 Table 26 |
| 10 | `design_twoway_slab` | Annex D | Complete two-way slab design | `Lx, Ly, loads, fck, fy, edges` | SP:16 |
| 11 | `torsion_reinforcement_corners` | D-1.8 | Corner torsion steel at discontinuous edges | `Ast_midspan, Lx` | — |
| 12 | `edge_strip_width` | D-1.1 | Edge strip = 0.75Lx/2 (but not > D-1.2) | `Lx` | — |
| 13 | `deflection_check_slab` | Cl 23.2 | Span/depth ratio with modifiers | `span, d, pt, pc, fy, support` | IS 456 Table 4 |
| **Flat Slab** | | | | |
| 14 | `design_flat_slab` | Cl 31 | Direct design / equivalent frame | `L1, L2, loads, fck, fy` | — |
| 15 | `flat_slab_drop_panel` | Cl 31.2.2 | Drop panel size requirements | `L1, L2, D_drop` | — |
| 16 | `column_strip_width` | Cl 31.1.2 | Width = 0.25L or 0.25L' | `L1, L2` | — |
| 17 | `punching_shear_slab` | Cl 31.6.1 | $\tau_v = V_e / (b_o d)$; $\tau_c = k_s \tau_c'$ | `Ve, bo, d, fck` | SP:34 |
| 18 | `flat_slab_moment_transfer` | Cl 31.3.3 | Unbalanced moment to column | `Mu_unbal, gamma_f` | — |
| **Continuous Slab** | | | | |
| 19 | `coefficient_method_moments` | Table 12, 13 | IS 456 coefficient method | `w, L, n_spans, end_cond` | IS 456 Tables |
| 20 | `moment_redistribution_is456` | Cl 37.1.1 | Max 30% redistribution | `M_elastic, percent, xu_d` | — |
| 21 | `curtailment_slab_bars` | Cl 26.2.3 | Bar cutoff rules for slabs | `bar_profile, span` | SP:34 |
| **General** | | | | |
| 22 | `min_steel_slab` | Cl 26.5.2.1 | 0.12% for HYSD, 0.15% for mild | `b, D, bar_type` | — |
| 23 | `max_bar_spacing_slab` | Cl 26.3.3(b) | $s \leq \min(3d, 300)$ main; $\min(5d, 450)$ dist | `d, bar_type` | — |
| 24 | `slab_cover` | Cl 26.4.1 | Table 16 cover values | `exposure, mild_or_moderate` | IS 456 Table 16 |
| 25 | `check_slab_serviceability` | Cl 23.2, 43 | Span/depth + crack width | `span, d, pt, pc, fy, support` | — |
| 26 | `slab_load_combination` | Table 18 | $1.5(DL+LL)$ or $1.2(DL+LL+EQ)$ | `DL, LL, EQ` | IS 456 Table 18 |
| 27 | `waffle_slab_rib_design` | Cl 30 | Rib design for waffle slab | `rib_b, rib_D, spacing, fck, fy, loads` | — |
| 28 | `precast_slab_connection` 🔲 | Cl 33 | Precast connection checks | — | — |

### 3.3 ACI 318-19 (`codes/aci318/slab/`)

| # | Function | Section | Formula | Key Params | Benchmark |
|---|----------|---------|---------|------------|-----------|
| 1 | `classify_slab_aci` | §8.10 | One-way vs two-way | `L_short, L_long` | — |
| 2 | `min_thickness_oneway_aci` | Table 7.3.1.1 | L/20 to L/28 based on support | `span, support, fy` | — |
| 3 | `min_thickness_twoway_aci` | §8.3.1, Table 8.3.1.1 | $h = L_n (0.8 + f_y/1400) / (36 + 5\beta(\alpha_{fm}-0.2))$ | `Ln, beta, alpha_fm, fy` | — |
| 4 | `design_oneway_slab_aci` | §7 | Complete one-way design | `span, loads, fc_prime, fy, support` | ACI Handbook |
| 5 | `moment_coefficients_aci` | §6.5 | ACI moment coefficients | `pattern_loading, n_spans` | — |
| 6 | `direct_design_method` | §8.10 | DDM for two-way slabs | `L1, L2, loads, fc_prime, fy` | ACI SP-17 |
| 7 | `equivalent_frame_method` | §8.11 | EFM for two-way slabs | `L1, L2, loads, fc_prime, fy` | — |
| 8 | `strip_moments_ddm` | §8.10.4 | Column/middle strip distribution | `M0, strip_type, alpha_f` | — |
| 9 | `min_steel_slab_aci` | §7.6.1 / §8.6.1 | $A_{s,min} = 0.0018 b h$ for Grade 60 | `b, h, fy` | — |
| 10 | `max_bar_spacing_slab_aci` | §7.7.2 / §8.7.2 | $s \leq \min(3h, 450)$ or $\min(2h, 450)$ | `h, critical_section` | — |
| 11 | `punching_shear_capacity_aci` | §22.6.5 | $v_c = \min(\lambda\sqrt{f'_c}/3, ...)$ (3 equations) | `fc_prime, b0, d, beta_c, alpha_s` | — |
| 12 | `punching_shear_with_studs_aci` | §22.6.8 | Shear stud reinforcement | `fc_prime, Av, fyt, b0, d, s` | — |
| 13 | `moment_transfer_punching_aci` | §8.4.2.3 | $\gamma_f M_u$ at slab-column joint | `Mu_unbal, b1, b2, d` | — |
| 14 | `temperature_reinforcement_aci` | §24.4 | Shrinkage & temperature steel | `b, h, fy` | — |
| 15 | `redistribution_aci` | §6.6.5 | Max 1000ε_t % redistribution | `epsilon_t, M_elastic` | — |
| 16 | `design_twoway_slab_aci` | §8 | Complete two-way design | Multi | ACI SP-17 |
| 17 | `shear_check_slab_aci` | §22.5 | Beam-action shear in slab | `Vu, b, d, fc_prime` | — |
| 18 | `deflection_slab_aci` | §24.2 | Branson for slabs | Multi | — |
| 19 | `post_tensioned_slab_check` 🔲 | §8.6.2 | PT slab minimum prestress | — | — |
| 20 | `flat_plate_opening_aci` | §8.5.4.2 | Opening limitations | `opening_size, column_strip` | — |
| 21 | `check_slab_serviceability_aci` | §24 | Complete serviceability | Multi | — |
| 22 | `slab_load_combination_aci` | §5.3 | $1.2D + 1.6L$ etc. | `DL, LL, other` | — |
| 23 | `shear_cap_design_aci` | §22.6 | Shear capital for flat slab | `column_size, Vu, fc_prime, d` | — |
| 24 | `effective_beam_width_aci` | §8.4 | For equivalent frame | `c1, c2, L2, alpha` | — |
| 25 | `slab_cover_aci` | Table 20.6.1 | Cover requirements | `exposure, bar_size` | — |
| 26 | `design_flat_slab_aci` | §8 | Complete flat slab design | Multi | ACI Handbook |

### 3.4 Eurocode 2 — EN 1992-1-1 (`codes/ec2/slab/`)

| # | Function | Section | Formula | Key Params | Benchmark |
|---|----------|---------|---------|------------|-----------|
| 1 | `classify_slab_ec2` | — | One-way vs two-way by geometry | `Lx, Ly` | — |
| 2 | `min_thickness_slab_ec2` | §7.4.2 | Span/depth from Table 7.4N | `span, support, fck, rho` | — |
| 3 | `design_oneway_slab_ec2` | §6.1, §9.3 | One-way slab design | `span, loads, fck, fyk, support` | EC2 Handbook |
| 4 | `moment_coefficients_twoway_ec2` | — | Based on elastic analysis / yield-line | `Lx, Ly, edges` | — |
| 5 | `design_twoway_slab_ec2` | §6.1, §9.3 | Two-way slab design | `Lx, Ly, loads, fck, fyk, edges` | — |
| 6 | `punching_shear_vrd_c_slab` | §6.4.4 | $v_{Rd,c} = C_{Rd,c} k (100\rho_l f_{ck})^{1/3}$ along control perimeter | `fck, d, rho_l, u1` | — |
| 7 | `punching_shear_vrd_max_slab` | §6.4.5 | $v_{Rd,max} = 0.4 \nu f_{cd}$ at column face | `fck, d, u0` | — |
| 8 | `punching_shear_reinforcement_ec2` | §6.4.5 | Shear stud/link design for punching | `vEd, vRd_c, d, sr, fyw` | — |
| 9 | `control_perimeter_ec2` | §6.4.2 | $u_1$ at $2d$ from column face | `column_dims, d, opening` | — |
| 10 | `beta_eccentricity_ec2` | §6.4.3 | $\beta$ for eccentric punching | `MEd, VEd, u1, d, W1` | — |
| 11 | `min_steel_slab_ec2` | §9.3.1.1 | $A_{s,min} = \max(0.26 f_{ctm}/f_{yk}, 0.0013) b d$ | `b, d, fctm, fyk` | — |
| 12 | `max_bar_spacing_slab_ec2` | §9.3.1.1(3) | $s \leq \min(3h, 400)$ main; $\min(3.5h, 450)$ secondary | `h` | — |
| 13 | `flat_slab_design_ec2` | §9.4 | Flat slab (with/without drops) | Multi | EC2 Handbook |
| 14 | `moment_transfer_punching_ec2` | §6.4.3 | Unbalanced moment via β | `MEd, column_type` | — |
| 15 | `loading_arrangement_ec2` | §5.1.3 | Alternate/checkerboard patterns | `DL, LL, n_spans` | — |
| 16 | `redistribution_ec2` | §5.5 | δ ≥ 0.44 + 1.25·xu/d (Class B/C) | `xu_d, steel_class` | — |
| 17 | `design_twoway_slab_ec2_full` | §6.1, §6.4, §7 | Complete design + punching + serviceability | Multi | — |
| 18 | `deflection_slab_ec2` | §7.4 | Span/depth or integration | Multi | — |
| 19 | `crack_control_slab_ec2` | §7.3 | Max bar dia or spacing tables | `wk, sigma_s` | — |
| 20 | `waffle_slab_ec2` | §9.2.1 | Ribbed/waffle slab rules | `rib_dims, spacing, fck, fyk` | — |
| 21 | `slab_load_combination_ec2` | EN 1990 §6.4 | $1.35G_k + 1.5Q_k$ | `Gk, Qk, psi_0` | — |
| 22 | `effective_width_slab_ec2` | §5.3.2.1 | For one-way action near column | `L, support` | — |
| 23 | `shear_check_slab_ec2` | §6.2.2 | One-way (beam) shear in slab | `VEd, bw, d, fck, Asl` | — |
| 24 | `slab_cover_ec2` | §4.4.1 | Nominal cover from exposure | `exposure, structural_class` | Table 4.4N |
| 25 | `slab_fire_resistance_ec2` | EN 1992-1-2 | Axis distance/min thickness | `REI, span, slab_type` | — |
| 26 | `torsion_reinforcement_corner_ec2` | — | Corner torsion reinforcement | `Ast_midspan, Lx` | — |
| 27 | `column_head_check_ec2` | §9.4.1 | Column head/capital geometry | `D_head, D_col, D_slab` | — |
| 28 | `design_flat_slab_ec2` | §9.4, §6.4 | Complete flat slab + punching | Multi | EC2 Handbook |

---

## 4. FOOTING Functions

### 4.1 Shared / Code-Agnostic (`codes/common/footing/`)

| # | Function | Signature | Return | Description |
|---|----------|-----------|--------|-------------|
| 1 | `footing_area_required` | `(P: float, sbc: float) -> float` | `float (mm²)` | A_req = P / q_a |
| 2 | `square_footing_side` | `(area: float) -> float` | `float (mm)` | L = √A |
| 3 | `rectangular_footing_dims` | `(area: float, ratio: float) -> tuple[float,float]` | `(L, B) (mm)` | L×B = A, L/B = ratio |
| 4 | `net_upward_pressure` | `(P: float, L: float, B: float) -> float` | `float (N/mm²)` | q_net = P/(L×B) |
| 5 | `bearing_pressure_with_moment` | `(P: float, Mx: float, My: float, L: float, B: float) -> tuple[float,float]` | `(q_max, q_min)` | q = P/A ± M/Z |
| 6 | `punching_perimeter_rect` | `(a: float, b: float, d: float) -> float` | `float (mm)` | bo = 2(a+d + b+d) |
| 7 | `punching_perimeter_circular` | `(D_col: float, d: float) -> float` | `float (mm)` | bo = π(D+d) |
| 8 | `one_way_shear_section` | `(col_dim: float, footing_dim: float, d: float) -> float` | `float (mm)` | Critical section location |
| 9 | `bending_moment_at_face` | `(q: float, L: float, col_dim: float) -> float` | `float (N·mm/mm)` | Cantilever moment |
| 10 | `transfer_steel_area` | `(P_excess: float, fy: float) -> float` | `float (mm²)` | Dowel area from excess bearing |
| 11 | `depth_for_shear` | `(Vu: float, b: float, vc: float) -> float` | `float (mm)` | Min d from shear governs |
| 12 | `combined_footing_pressures` | `(P1: float, P2: float, M: float, L: float, B: float) -> tuple` | `tuple` | Trapezoidal pressure check |

### 4.2 IS 456:2000 (`codes/is456/footing/`)

| # | Function | Clause | Formula | Key Params | Benchmark | Status |
|---|----------|--------|---------|------------|-----------|--------|
| 1 | `size_footing` | Cl 34.1 | A_req = P_service / q_a (unfactored) | `P_service_kN, sbc_kPa, col_dims` | — | ✅ |
| 2 | `bearing_stress_enhancement` | Cl 34.4 | $f_{br} = 0.45 f_{ck} \sqrt{A_1/A_2} \leq 2 \cdot 0.45 f_{ck}$ | `fck, A1, A2` | — | ✅ |
| 3 | `check_bearing_pressure` | Cl 34.1 | q_net ≤ SBC (service), factored for design | `P_factored, L, B, sbc` | — | ✅ |
| 4 | `footing_flexure` | Cl 34.2.3.1 | Critical section at column face | `q_net, L, B, col_b, col_D, d, fck, fy` | SP:16 | ✅ |
| 5 | `footing_one_way_shear` | Cl 34.2.4.1(a) | Critical at d from column face | `q_net, L, B, col_b, col_D, d, fck, pt` | SP:16 | ✅ |
| 6 | `footing_punching_shear` | Cl 31.6.1 | $\tau_v = V_u / (b_o \cdot d) \leq k_s \tau_c$ | `q_net, L, B, col_b, col_D, d, fck` | SP:16 | ✅ |
| 7 | `validate_footing_inputs` | — | Input checks | `all dims, loads` | — | ✅ |
| 8 | `net_upward_pressure_nmm2` | — | q = P / (L×B) in N/mm² | `Pu_kN, L_mm, B_mm` | — | ✅ |
| 9 | `punching_perimeter_mm` | — | bo = 2(a+d + b+d) | `a, b, d` | — | ✅ |
| 10 | `punching_area_mm2` | — | (a+d)(b+d) | `a, b, d` | — | ✅ |
| 11 | `design_isolated_footing` 🔲 | Cl 34 | Complete isolated footing design | All | SP:16 | 🔲 |
| 12 | `design_combined_footing` 🔲 | Cl 34 | Two-column strip footing | Multi | SP:34 | 🔲 |
| 13 | `footing_development_length` 🔲 | Cl 26.2 | Bar anchorage in footing | `bar_dia, fck, fy` | — | 🔲 |
| 14 | `transfer_reinforcement` 🔲 | Cl 34.4.1 | Dowel bar requirement | `Pu, bearing_capacity, fy` | — | 🔲 |
| 15 | `pedestal_check` 🔲 | Cl 34.1.3 | Pedestal sizing | `col_dims, footing_depth` | — | 🔲 |
| 16 | `footing_settlement_check` 🔲 | Cl 34.1 | Differential settlement limit | `delta, L` | — | 🔲 |
| 17 | `eccentric_footing` 🔲 | Cl 34.1 | One-way/two-way eccentricity | `P, Mx, My, L, B` | — | 🔲 |
| 18 | `strap_footing` 🔲 | — | Strap beam between footings | Multi | — | 🔲 |
| 19 | `footing_detailing` 🔲 | Cl 26, 34 | Min steel, cover, spacing | Multi | — | 🔲 |
| 20 | `footing_depth_from_shear` 🔲 | Cl 34.2.4 | Governing depth | `Vu, b, fck, pt` | — | 🔲 |

### 4.3 ACI 318-19 (`codes/aci318/footing/`)

| # | Function | Section | Formula | Key Params | Benchmark |
|---|----------|---------|---------|------------|-----------|
| 1 | `size_footing_aci` | §13.3 | Service load / q_a | `P_service, q_allowable` | — |
| 2 | `bearing_strength_aci` | §22.8 | $\phi B_n = \phi 0.85 f'_c A_1 \sqrt{A_2/A_1} \leq 2 \cdot \phi 0.85 f'_c A_1$ | `fc_prime, A1, A2` | — |
| 3 | `one_way_shear_footing_aci` | §22.5 | At d from face; $\phi V_c = \phi \cdot 0.17\sqrt{f'_c} b d$ | `fc_prime, b, d, Vu` | — |
| 4 | `two_way_shear_footing_aci` | §22.6.5 | 3-equation punching check | `fc_prime, bo, d, Vu, beta_c, alpha_s` | ACI Handbook |
| 5 | `flexure_footing_aci` | §13.2.7 | Critical at column face | `q_net, L, col_dim, d, fc_prime, fy` | — |
| 6 | `development_length_footing_aci` | §25.4 | Straight bar + hook | `bar_dia, fc_prime, fy, cover` | — |
| 7 | `dowel_reinforcement_aci` | §16.3 | Transfer reinforcement | `Pu, bearing_cap, fy` | — |
| 8 | `design_spread_footing_aci` | §13 | Complete spread footing | Multi | ACI SP-17 |
| 9 | `min_steel_footing_aci` | §13.2.8 | 0.0018bh (Grade 60) | `b, h, fy` | — |
| 10 | `footing_cover_aci` | §20.6.1 | 75mm cast against soil | — | — |
| 11 | `combined_footing_aci` | §13 | Design for 2+ columns | Multi | — |
| 12 | `mat_foundation_check_aci` | §13 | Mat/raft checks | Multi | — |
| 13 | `load_transfer_at_base_aci` | §16.3 | Column → footing interface | Multi | — |
| 14 | `eccentric_footing_aci` | §13 | Eccentric loading check | `P, M, L, B` | — |
| 15 | `pedestal_design_aci` | §14 | Short pedestal design | `P, fc_prime, Ag` | — |
| 16 | `footing_depth_governed_by_shear_aci` | §22.5, §22.6 | Minimize depth | Multi | — |
| 17 | `strip_footing_aci` | §13 | Wall footing design | `w_wall, fc_prime, fy, sbc` | — |
| 18 | `design_isolated_footing_aci` | §13 | Complete isolated footing | Multi | ACI Handbook |

### 4.4 Eurocode 2 — EN 1992-1-1 (`codes/ec2/footing/`)

| # | Function | Section | Formula | Key Params | Benchmark |
|---|----------|---------|---------|------------|-----------|
| 1 | `size_footing_ec2` | EN 1997 §6 | SLS bearing from geotechnical code | `NEd_sls, q_Rd` | — |
| 2 | `bearing_check_ec2` | EN 1997 | Bearing resistance verification | `NEd, A_eff, q_Rd` | — |
| 3 | `one_way_shear_footing_ec2` | §6.2.2 | $V_{Rd,c}$ at d from face | `fck, b, d, Asl, VEd` | — |
| 4 | `punching_shear_footing_ec2` | §6.4 | Control perimeter at 2d | `fck, d, u1, VEd, column_dims` | EC2 Handbook |
| 5 | `flexure_footing_ec2` | §6.1, §9.8 | Critical at column face | `q_net, L, col_dim, d, fck, fyk` | — |
| 6 | `anchorage_footing_ec2` | §8.4, §9.8.2 | Bends / straight bars in footing | `bar_dia, fck, fyk` | — |
| 7 | `min_steel_footing_ec2` | §9.8.2 | Same as slab min steel rules | `b, d, fctm, fyk` | — |
| 8 | `strut_and_tie_footing_ec2` | §6.5 | Deep footing (D > half-spread) | `geometry, loads, fck, fyk` | — |
| 9 | `design_pad_footing_ec2` | §6.1, §6.4, §9.8 | Complete pad footing design | Multi | EC2 Handbook |
| 10 | `combined_footing_ec2` | §9.8 | Multi-column footing | Multi | — |
| 11 | `pile_cap_design_ec2` | §9.8.1 | Strut-and-tie model for pile caps | Multi | — |
| 12 | `eccentric_footing_ec2` | — | With moment | `NEd, MEd, L, B` | — |
| 13 | `footing_cover_ec2` | §4.4.1 | 40mm min (cast against blinding) | `exposure` | — |
| 14 | `bearing_at_column_base_ec2` | §6.7 | Partly loaded area enhancement | `fck, Ac0, Ac1` | — |
| 15 | `dowel_requirement_ec2` | §9.8.4 | Starter bars from footing | `NEd, fck, fyk` | — |
| 16 | `raft_foundation_check_ec2` | §9.8 | Raft/mat design checks | Multi | — |
| 17 | `design_retaining_wall_footing_ec2` | §9.8, EN 1997 | Retaining wall toe/heel | Multi | — |
| 18 | `settlement_check_ec2` | EN 1997 | Differential settlement | `delta, L` | — |
| 19 | `punching_with_eccentricity_ec2` | §6.4.3 | Beta factor for eccentric columns | `MEd, VEd, u1, d` | — |
| 20 | `design_isolated_footing_ec2` | §6, §9.8 | Complete isolated footing | Multi | EC2 Handbook |

---

## 5. STAIRCASE Functions

### 5.1 Shared / Code-Agnostic (`codes/common/staircase/`)

| # | Function | Signature | Return | Description |
|---|----------|-----------|--------|-------------|
| 1 | `going_riser_check` | `(G: float, R: float) -> bool` | `bool` | 2R + G ≈ 600mm |
| 2 | `effective_span_staircase` | `(support1: str, support2: str, dims: dict) -> float` | `float (mm)` | Span from support conditions |
| 3 | `waist_slab_self_weight` | `(t_waist: float, R: float, G: float) -> float` | `float (kN/m²)` | Weight on plan incl. slope |
| 4 | `step_self_weight` | `(R: float, G: float) -> float` | `float (kN/m²)` | Triangular step weight on plan |
| 5 | `inclined_to_plan_factor` | `(R: float, G: float) -> float` | `float` | √(R² + G²) / G |
| 6 | `number_of_steps` | `(floor_height: float, riser: float) -> int` | `int` | n = H / R |

### 5.2 IS 456:2000 (`codes/is456/staircase/`)

| # | Function | Clause | Formula | Key Params | Benchmark |
|---|----------|--------|---------|------------|-----------|
| 1 | `design_waist_slab_staircase` | Cl 33 | Simply supported waist slab | `span, loads, fck, fy, t_waist` | SP:34 |
| 2 | `design_dog_legged_staircase` | Cl 33 | Dog-legged with landing | Multi | SP:34 |
| 3 | `design_open_well_staircase` | Cl 33 | Open-well staircase | Multi | — |
| 4 | `effective_span_stair_is456` | Cl 33.1 | Effective span rules | `support_conditions, dims` | — |
| 5 | `stair_loading_is456` | Table 18, IS 875 | Load combinations for stairs | `DL, LL, finishes` | IS 875 |
| 6 | `distribution_steel_stair` | Cl 26.5.2.1 | Min distribution steel | `b, D, bar_type` | — |
| 7 | `detailing_staircase` | Cl 26, SP:34 | Bar bending, anchorage | Multi | SP:34 |
| 8 | `deflection_check_stair` | Cl 23.2 | Span/depth ratio | `span, d, pt, fy` | — |
| 9 | `landing_design` | Cl 33 | Landing slab design | `landing_span, loads, fck, fy` | — |
| 10 | `tread_slab_staircase` 🔲 | — | Tread slab (cantilevered) type | Multi | — |

### 5.3 ACI 318-19 (`codes/aci318/staircase/`)

| # | Function | Section | Formula | Key Params | Benchmark |
|---|----------|---------|---------|------------|-----------|
| 1 | `design_staircase_aci` | §7 | Treated as one-way slab | Multi | — |
| 2 | `effective_span_stair_aci` | — | Center-to-center support | `dims` | — |
| 3 | `min_thickness_stair_aci` | Table 7.3.1.1 | Based on slab L/d ratios | `span, support` | — |
| 4 | `stair_loading_aci` | ASCE 7 | $1.2D + 1.6L$ | `DL, LL` | — |
| 5 | `detailing_staircase_aci` | §25, §7.7 | Min cover, spacing, bar sizes | Multi | — |
| 6 | `deflection_check_stair_aci` | §24 | Min thickness or calculation | Multi | — |
| 7 | `design_dog_legged_aci` | §7 | With landing | Multi | — |
| 8 | `landing_connection_aci` | — | Landing to flight connection | Multi | — |

### 5.4 Eurocode 2 — EN 1992-1-1 (`codes/ec2/staircase/`)

| # | Function | Section | Formula | Key Params | Benchmark |
|---|----------|---------|---------|------------|-----------|
| 1 | `design_staircase_ec2` | §6.1, §9.3 | Waist slab type | Multi | — |
| 2 | `effective_span_stair_ec2` | §5.3 | Effective span rules | `dims` | — |
| 3 | `stair_loading_ec2` | EN 1991 | $1.35G_k + 1.5Q_k$ | `Gk, Qk` | — |
| 4 | `min_steel_stair_ec2` | §9.3.1 | Same as slab rules | `b, d, fctm, fyk` | — |
| 5 | `detailing_staircase_ec2` | §8, §9.3 | Bar scheduling | Multi | — |
| 6 | `deflection_check_stair_ec2` | §7.4 | Span/depth ratio | `span, d, rho, fck` | — |
| 7 | `design_dog_legged_ec2` | §6.1 | With landing | Multi | — |
| 8 | `fire_resistance_stair_ec2` | EN 1992-1-2 | Min cover/thickness for REI | `REI, t_waist` | — |

---

## 6. COMMON INFRASTRUCTURE Functions

### 6.1 Material Properties

#### IS 456:2000 Constants & Material Functions

| # | Function | Clause | Formula | Status |
|---|----------|--------|---------|--------|
| 1 | `get_xu_max_d(fy)` | Cl 38.1 | $x_{u,max}/d = 700/(1100 + 0.87 f_y)$ | ✅ |
| 2 | `get_ec(fck)` | Cl 6.2.3.1 | $E_c = 5000\sqrt{f_{ck}}$ | ✅ |
| 3 | `get_fcr(fck)` | Cl 6.2.2 | $f_{cr} = 0.7\sqrt{f_{ck}}$ | ✅ |
| 4 | `get_steel_stress(strain, fy)` | Fig. 23 | Bilinear/5-point model | ✅ |
| 5 | `design_steel_stress(fy)` | Cl 36.1 | $f_d = 0.87 f_y$ | ✅ |
| 6 | `modular_ratio(fck)` 🔲 | Cl 43.1 | $m = 280/(3\sigma_{cbc})$ | 🔲 |
| 7 | `sigma_cbc(fck)` 🔲 | Annex B | Working stress $\sigma_{cbc}$ | 🔲 |
| 8 | `concrete_density()` 🔲 | Cl 6.2.1 | 24 kN/m³ (normal weight) | 🔲 |

#### ACI 318-19 Material Functions

| # | Function | Section | Formula |
|---|----------|---------|---------|
| 1 | `elastic_modulus_aci(fc_prime)` | §19.2.2 | $E_c = 0.043 w_c^{1.5} \sqrt{f'_c}$ (MPa) or $4700\sqrt{f'_c}$ for normal weight |
| 2 | `modulus_of_rupture_aci(fc_prime)` | §19.2.3 | $f_r = 0.62\lambda\sqrt{f'_c}$ |
| 3 | `beta1_aci(fc_prime)` | §22.2.2.4.3 | $\beta_1 = 0.85 - 0.05(f'_c - 28)/7 \geq 0.65$ |
| 4 | `design_concrete_strength_aci(fc_prime)` | §22.2.2 | $0.85 f'_c$ |
| 5 | `design_steel_strength_aci(fy)` | §20.2.2 | $f_y$ (no reduction) |
| 6 | `epsilon_cu_aci()` | §22.2.2.1 | 0.003 |
| 7 | `modular_ratio_aci(fc_prime)` | — | $n = E_s / E_c$ |
| 8 | `concrete_density_aci(wc)` | §19.2.2 | wc or 2400 kg/m³ default |

#### EC2 Material Functions

| # | Function | Section | Formula |
|---|----------|---------|---------|
| 1 | `elastic_modulus_ec2(fck)` | Table 3.1 | $E_{cm} = 22(f_{cm}/10)^{0.3}$ (GPa); $f_{cm} = f_{ck} + 8$ |
| 2 | `fctm_ec2(fck)` | Table 3.1 | $f_{ctm} = 0.30 f_{ck}^{2/3}$ for ≤ C50; $2.12\ln(1+f_{cm}/10)$ for > C50 |
| 3 | `fctk_005_ec2(fck)` | Table 3.1 | $f_{ctk,0.05} = 0.7 f_{ctm}$ |
| 4 | `fcd_ec2(fck, alpha_cc)` | §3.1.6 | $f_{cd} = \alpha_{cc} f_{ck} / \gamma_c$; $\alpha_{cc} = 1.0$ (recommended) |
| 5 | `fyd_ec2(fyk)` | §3.2.7 | $f_{yd} = f_{yk} / \gamma_s$ |
| 6 | `epsilon_cu2_ec2(fck)` | Table 3.1 | 0.0035 for ≤ C50; $2.6 + 35[(90-f_{ck})/100]^4 \times 10^{-3}$ for > C50 |
| 7 | `epsilon_cu3_ec2(fck)` | Table 3.1 | 0.0035 for ≤ C50; $2.6 + 35[(90-f_{ck})/100]^4 \times 10^{-3}$ for > C50 |
| 8 | `lambda_ec2(fck)` | §3.1.7 | 0.8 for ≤ C50; $0.8 - (f_{ck}-50)/400$ |
| 9 | `eta_ec2(fck)` | §3.1.7 | 1.0 for ≤ C50; $1.0 - (f_{ck}-50)/200$ |
| 10 | `parabolic_rectangular_n(fck)` | Table 3.1 | $n = 2.0$ for ≤ C50; $1.4 + 23.4[(90-f_{ck})/100]^4$ |
| 11 | `epsilon_c2_ec2(fck)` | Table 3.1 | 0.002 for ≤ C50; $2.0 + 0.085(f_{ck}-50)^{0.53} \times 10^{-3}$ |
| 12 | `creep_coefficient_ec2(fck, RH, h0, t0, cement)` | §3.1.4, Annex B | $\varphi(\infty,t_0)$ per Annex B |
| 13 | `shrinkage_strain_drying_ec2(fck, RH, h0, age)` | §3.1.4(6) | $\varepsilon_{cd}$ per Table 3.2 |
| 14 | `shrinkage_strain_autogenous_ec2(fck, age)` | §3.1.4(6) | $\varepsilon_{ca}(\infty) = 2.5(f_{ck}-10) \times 10^{-6}$ |
| 15 | `effective_modulus_ec2(Ecm, phi)` | §5.8.6 | $E_{c,eff} = E_{cm}/(1+\varphi)$ |
| 16 | `modular_ratio_ec2(fck, phi)` | — | $n = E_s / E_{c,eff}$ |
| 17 | `concrete_density_ec2()` | §11.3 | 25 kN/m³ (reinforced normal weight) |
| 18 | `steel_stress_strain_ec2(epsilon, fyk)` | §3.2.7 | Bilinear (class B/C) |

### 6.2 IS 456 Table Lookups (existing `tables.py`)

| # | Function | Table | Status |
|---|----------|-------|--------|
| 1 | `get_tc_value(fck, pt)` | Table 19 | ✅ |
| 2 | `get_tc_max_value(fck)` | Table 20 | ✅ |
| 3 | `XU_MAX_RATIO` dict | Table 21.1 (SP:16) | ✅ |
| 4 | `TAU_BD` dict 🔲 | Table 26.2.1.1 | 🔲 |
| 5 | `DEFLECTION_BASIC_RATIOS` dict 🔲 | Table 4 (Cl 23.2) | 🔲 |
| 6 | `LOAD_FACTORS` dict 🔲 | Table 18 | 🔲 |
| 7 | `EFFECTIVE_LENGTH_FACTORS` dict | Table 28 | ✅ (in column/axial.py) |
| 8 | `CLEAR_COVER_TABLE` dict 🔲 | Table 16 | 🔲 |
| 9 | `MOMENT_COEFFICIENTS_CONTINUOUS` dict 🔲 | Table 12 | 🔲 |
| 10 | `SHEAR_COEFFICIENTS_CONTINUOUS` dict 🔲 | Table 13 | 🔲 |
| 11 | `TWOWAY_MOMENT_COEFFICIENTS` dict 🔲 | Table 26 (Annex D) | 🔲 |
| 12 | `EXPOSURE_REQUIREMENTS` dict 🔲 | Table 5 | 🔲 |

### 6.3 Validation Functions

| # | Function | Scope | Status |
|---|----------|-------|--------|
| 1 | `validate_beam_dimensions(b, d, D)` | IS 456 beams | ✅ |
| 2 | `validate_material_grades(fck, fy)` | IS 456 | ✅ |
| 3 | `validate_column_dimensions(b, D)` 🔲 | All codes | 🔲 |
| 4 | `validate_slab_inputs(Lx, Ly, D)` 🔲 | All codes | 🔲 |
| 5 | `validate_footing_inputs(L, B, D)` | IS 456 footings | ✅ |
| 6 | `validate_staircase_inputs(R, G, t)` 🔲 | All codes | 🔲 |
| 7 | `validate_loads(DL, LL, EQ)` 🔲 | All codes | 🔲 |
| 8 | `validate_reinforcement(Ast, b, d)` 🔲 | All codes | 🔲 |

### 6.4 Load Combinations

| Code | Function | Reference | Formula |
|------|----------|-----------|---------|
| IS 456 | `load_combo_is456(DL, LL, EQ, WL)` | Table 18 | 1.5(D+L), 1.2(D+L±E), 1.5(D±E), 0.9D±1.5E |
| ACI 318 | `load_combo_aci(DL, LL, EQ, WL, SL)` | §5.3 | 1.4D, 1.2D+1.6L, 1.2D+L+E, 0.9D+E ... |
| EC2 | `load_combo_ec2(Gk, Qk, AEd, psi)` | EN 1990 §6.4 | γ_G·Gk + γ_Q·Qk·ψ₀ ... |

### 6.5 Error Types

| Error Class | Usage | Module |
|-------------|-------|--------|
| `DimensionError` | Section too small, invalid geometry | ✅ `core/errors.py` |
| `MaterialError` | Invalid fck, fy, out-of-range grade | ✅ `core/errors.py` |
| `ConfigurationError` | Invalid settings, contradictory inputs | ✅ `core/errors.py` |
| `DesignError` | Design fails (Mu < applied, section inadequate) | ✅ `core/errors.py` |
| `ComplianceError` | Code compliance violation | ✅ `core/errors.py` |
| `CalculationError` | NaN, Inf, division by zero | ✅ `core/errors.py` |
| `SlendernessError` 🔲 | Exceeds max slenderness ratio | 🔲 |
| `StabilityError` 🔲 | Buckling failure | 🔲 |
| `ServiceabilityError` 🔲 | Deflection/crack width exceeded | 🔲 |

---

## 7. REFERENCE TABLES

### 7.1 Concrete Grade Mapping

| IS 456 Grade | $f_{ck}$ (MPa) | EC2 Class | $f_{ck}$ (MPa) | ACI f'c (MPa) | ACI f'c (psi) |
|-------------|------|-----------|------|------------|------------|
| M15 | 15 | C12/15 | 12 | 12 | 1740 |
| M20 | 20 | C16/20 | 16 | 20 | 2900 |
| M25 | 25 | C20/25 | 20 | 25 | 3625 |
| M30 | 30 | C25/30 | 25 | 28 | 4060 |
| M35 | 35 | C28/35 | 28 | 35 | 5075 |
| M40 | 40 | C32/40 | 32 | 35 | 5075 |
| M45 | 45 | C35/45 | 35 | 40 | 5800 |
| M50 | 50 | C40/50 | 40 | 42 | 6090 |
| M55 | 55 | C45/55 | 45 | 48 | 6960 |
| M60 | 60 | C50/60 | 50 | 55 | 7975 |
| M65 | 65 | C55/67 | 55 | 60 | 8700 |
| M70 | 70 | C60/75 | 60 | 62 | 8990 |
| M75 | 75 | C70/85 | 70 | 69 | 10005 |
| M80 | 80 | C80/95 | 80 | 76 | 11020 |

**Notes:**
- IS 456 $f_{ck}$ = characteristic cube strength (150mm cube).
- EC2 $f_{ck}$ = characteristic cylinder strength (150×300mm).
- ACI $f'_c$ = specified cylinder strength (6×12 in / 150×300mm).
- Conversion: $f_{ck,cyl} \approx 0.8 \cdot f_{ck,cube}$ (approximate).

### 7.2 Steel Grade Mapping

| IS 456 | $f_y$ (MPa) | ACI | $f_y$ (MPa) | $f_y$ (ksi) | EC2 | $f_{yk}$ (MPa) |
|--------|------|-----|------|-------|-----|------|
| Fe 250 | 250 | Grade 40 | 280 | 40 | B500A* | 500 |
| Fe 415 | 415 | Grade 60 | 420 | 60 | B500B | 500 |
| Fe 500 | 500 | Grade 75 | 520 | 75 | B500C | 500 |
| Fe 550 | 550 | Grade 80 | 550 | 80 | B600 | 600 |

*\*EC2 standardizes on 500 MPa; variation is in ductility class (A/B/C), not strength.*

### 7.3 Safety / Strength Reduction Factors

| Factor | IS 456 | ACI 318 | EC2 |
|--------|--------|---------|-----|
| **Concrete** | $\gamma_c = 1.5$ | — | $\gamma_c = 1.5$ |
| **Steel** | $\gamma_s = 1.15$ | — | $\gamma_s = 1.15$ |
| **Flexure** | Built into γc, γs | $\phi = 0.90$ (tension-controlled) | Built into γc, γs |
| **Shear** | Built into γc, γs | $\phi = 0.75$ | Built into γc, γs |
| **Axial (tied)** | Built into 0.4/0.67 | $\phi = 0.65$ × 0.80 max | Built into γc, γs |
| **Axial (spiral)** | Built into 0.4/0.67 × 1.05 | $\phi = 0.75$ × 0.85 max | Built into γc, γs |
| **Bearing** | Built into factors | $\phi = 0.65$ | Built into γc |
| **Load DL** | $\gamma_f = 1.5$ | $\gamma_D = 1.2$ or $1.4$ | $\gamma_G = 1.35$ |
| **Load LL** | $\gamma_f = 1.5$ | $\gamma_L = 1.6$ | $\gamma_Q = 1.5$ |
| **Load EQ** | $\gamma_f = 1.5$ or $1.2$ | $\gamma_E = 1.0$ | $\gamma_E = 1.0$ |

### 7.4 Key Stress-Block Parameters

| Parameter | IS 456 | ACI 318 | EC2 (≤ C50) | EC2 (> C50) |
|-----------|--------|---------|-------------|-------------|
| **$\varepsilon_{cu}$** | 0.0035 | 0.003 | 0.0035 | $2.6 + 35[(90-f_{ck})/100]^4 \times 10^{-3}$ |
| **$\varepsilon_{c0}$** | 0.002 | — | 0.002 | $2.0 + 0.085(f_{ck}-50)^{0.53} \times 10^{-3}$ |
| **Block factor** | 0.36 fck | 0.85 f'c | η·fcd (η=1.0) | η·fcd (η reduced) |
| **Centroid** | 0.42·xu | a/2 (= β₁c/2) | λ·x/2 (λ=0.8) | λ·x/2 (λ reduced) |
| **xu_max/d** | $700/(1100+0.87f_y)$ | c/d at $\varepsilon_t$ = 0.004 | 0.45 (Class B/C) | 0.35 |
| **$E_s$** | 200,000 MPa | 200,000 MPa | 200,000 MPa | 200,000 MPa |

### 7.5 Constants per Code

#### IS 456:2000 Constants (✅ mostly in `common/constants.py`)

| Constant | Value | Clause | Status |
|----------|-------|--------|--------|
| `GAMMA_C` | 1.5 | Cl 36.4.2 | ✅ |
| `GAMMA_S` | 1.15 | Cl 36.4.2 | ✅ |
| `STRESS_RATIO` | 0.87 (= 1/1.15) | Cl 36.1 | ✅ |
| `STRESS_BLOCK_FACTOR` | 0.36 | Cl 38.1, Fig 22 | ✅ |
| `STRESS_BLOCK_DEPTH` | 0.42 | Cl 38.1 | ✅ |
| `STRESS_BLOCK_PEAK` | 0.446 | Cl 38.1 | ✅ |
| `FLANGE_STRESS_FACTOR` | 0.45 | Annex G | ✅ |
| `EPSILON_CU` | 0.0035 | Cl 38.1, Fig 21 | ✅ |
| `EPSILON_C0` | 0.002 | Cl 38.1, Fig 21 | ✅ |
| `ES_STEEL_MPA` | 200,000 | Cl 5.6.3 | ✅ |
| `CONCRETE_EC_FACTOR` | 5000 | Cl 6.2.3.1 | ✅ |
| `CONCRETE_FCR_FACTOR` | 0.7 | Cl 6.2.2 | ✅ |
| `MIN_STEEL_FACTOR` | 0.85 | Cl 26.5.1.1 | ✅ |
| `MAX_STEEL_RATIO` | 0.04 | Cl 26.5.1.1 | ✅ |
| `MAX_SPACING_FACTOR` | 0.75 | Cl 26.5.1.5 | ✅ |
| `MAX_SPACING_MM` | 300 | Cl 26.5.1.5 | ✅ |
| `MIN_SHEAR_REINF_FACTOR` | 0.4 | Cl 26.5.1.6 | ✅ |
| `TORSION_SHEAR_FACTOR` | 1.6 | Cl 41.3.1 | ✅ |
| `TORSION_MOMENT_DIVISOR` | 1.7 | Cl 41.4.2 | ✅ |
| `COLUMN_CONCRETE_COEFF` | 0.4 | Cl 39.3 | ✅ |
| `COLUMN_STEEL_COEFF` | 0.67 | Cl 39.3 | ✅ |
| `COLUMN_MIN_STEEL_RATIO` | 0.008 | Cl 26.5.3.1 | ✅ |
| `COLUMN_MAX_STEEL_RATIO` | 0.04 | Cl 26.5.3.1 | ✅ |
| `MIN_ECCENTRICITY_MM` | 20 | Cl 25.4 | ✅ |
| `SHORT_COLUMN_SLENDERNESS_LIMIT` | 12 | Cl 25.1.2 | ✅ |
| `MAX_SLENDERNESS_RATIO` | 60 | Cl 25.3.1 | ✅ |
| `COLUMN_AXIAL_EMIN_FACTOR` | 0.05 | Cl 39.3 | ✅ |
| `SIDE_FACE_DEPTH_THRESHOLD_MM` | 750 | Cl 26.5.1.3 | ✅ |
| `SIDE_FACE_AREA_RATIO` | 0.001 | Cl 26.5.1.3 | ✅ |
| `MIN_CLEAR_COVER_MM` | 25 | Cl 26.4.1 | ✅ |

#### ACI 318-19 Constants (🔲 all needed)

| Constant | Value | Section |
|----------|-------|---------|
| `EPSILON_CU_ACI` | 0.003 | §22.2.2.1 |
| `ALPHA_1_ACI` | 0.85 | §22.2.2.4.1 |
| `BETA_1_MAX` | 0.85 | §22.2.2.4.3 |
| `BETA_1_MIN` | 0.65 | §22.2.2.4.3 |
| `PHI_FLEXURE_TENSION` | 0.90 | §21.2.2 |
| `PHI_SHEAR` | 0.75 | §21.2.1 |
| `PHI_AXIAL_TIED` | 0.65 | §21.2.2 |
| `PHI_AXIAL_SPIRAL` | 0.75 | §21.2.2 |
| `PHI_BEARING` | 0.65 | §21.2.1 |
| `MAX_AXIAL_TIED` | 0.80 | §22.4.2.1 |
| `MAX_AXIAL_SPIRAL` | 0.85 | §22.4.2.1 |
| `ES_ACI` | 200,000 MPa | §20.2.2.2 |
| `MIN_TENSION_CONTROLLED_STRAIN` | 0.005 | §21.2.2 |
| `COMPRESSION_CONTROLLED_STRAIN` | 0.002 | §21.2.2 |
| `MIN_SHEAR_REINF_FACTOR_1` | 0.062 | §9.6.3.3 |
| `MIN_SHEAR_REINF_FACTOR_2` | 0.35 | §9.6.3.3 |

#### EC2 Constants (🔲 all needed)

| Constant | Value | Section |
|----------|-------|---------|
| `GAMMA_C_EC2` | 1.5 | §2.4.2.4 |
| `GAMMA_S_EC2` | 1.15 | §2.4.2.4 |
| `ALPHA_CC_EC2` | 1.0 | §3.1.6 (recommended) |
| `ALPHA_CT_EC2` | 1.0 | §3.1.6 |
| `EPSILON_CU2_50` | 0.0035 | Table 3.1 |
| `EPSILON_C2_50` | 0.002 | Table 3.1 |
| `LAMBDA_50` | 0.8 | §3.1.7(3) |
| `ETA_50` | 1.0 | §3.1.7(3) |
| `ES_EC2` | 200,000 MPa | §3.2.7(4) |
| `CRD_C` | 0.18/γc = 0.12 | §6.2.2(1) |
| `K1_SHEAR` | 0.15 | §6.2.2(1) |
| `K3_CRACK` | 3.4 | §7.3.4 (recommended) |
| `K4_CRACK` | 0.425 | §7.3.4 (recommended) |
| `CONCRETE_DENSITY_EC2` | 25 kN/m³ | §11.3 |

---

## 8. IMPLEMENTATION PRIORITY

### Phase 1 — Shared Infrastructure (codes/common/)
1. `codes/common/mechanics.py` — strain, lever arm, moment couple (24 beam + 14 column shared fns)
2. `codes/common/sections.py` — Ig, Icr, Ieff, section properties
3. `codes/common/reinforcement.py` — bar selection, spacing checks, weight
4. ACI 318 constants module
5. EC2 constants module
6. Material property functions for all 3 codes

### Phase 2 — IS 456 Completion
1. Slab module (28 functions)
2. Remaining footing functions (10 missing)
3. Staircase module (10 functions)
4. Missing beam functions (compute_xu, curtailment, etc.)
5. IS 456 table lookup completions

### Phase 3 — ACI 318 Implementation
1. Beam flexure + shear (22 functions)
2. Column design (30 functions)
3. Slab design (26 functions)
4. Footing + staircase (26 functions)
5. Detailing + serviceability

### Phase 4 — EC2 Implementation
1. Beam flexure + shear (20 functions)
2. Column design (32 functions)
3. Slab + footing (48 functions)
4. Staircase (8 functions)
5. Fire resistance checks (unique to EC2)

---

*This document is the definitive function reference for the library. Total: **564 functions** across 3 codes and 5 structural elements.*
