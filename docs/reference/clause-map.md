# IS 456 Clause-to-Function Mapping

**Type:** Reference
**Audience:** All Agents
**Status:** Active
**Importance:** High
**Created:** 2026-04-04
**Last Updated:** 2026-04-04

---

Maps IS 456:2000 (and IS 13920:2016) clauses to their implementing functions in `structural_lib`.

**Legend:**
- **Decorator:** `@clause` = function uses traceability decorator; `clause_ref` = clause referenced in errors; `implicit` = implements clause without explicit annotation; `—` = not implemented
- **Notes:** Additional context about the implementation

---

## Beam — Flexure (`codes/is456/beam/flexure.py`)

| Clause | Title | Function | Decorator | Notes |
|--------|-------|----------|-----------|-------|
| 38.1 | Assumptions in Design | `calculate_mu_lim()` | `@clause` | Also 38.1.1 |
| 38.1.1 | Neutral Axis Depth | `calculate_mu_lim()` | `@clause` | With 38.1 |
| 38.1.2 | Stress Block Parameters | — | — | Used implicitly in flexure calculations |
| 38.2 | Singly Reinforced Sections | `calculate_ast_required()` | `@clause` | |
| 38.1, 38.2 | Flexure Design (Singly) | `design_singly_reinforced()` | `@clause` | Combined check |
| 38.1, 38.2, G-1.1 | Flexure Design (Doubly) | `design_doubly_reinforced()` | `@clause` | SP:16 charts |
| 38.3 | Doubly Reinforced Sections | `design_doubly_reinforced()` | `@clause` | Via G-1.1 |
| 38.4 | Flanged Beams | `design_flanged_beam()` | `@clause` | With G-2.2 |
| 38.1, G-2.2 | Flanged Beam Mu_lim | `calculate_mu_lim_flanged()` | `@clause` | |
| 23.1.2 | Effective Span — Continuous | `calculate_effective_flange_width()` | `@clause` | With 36.4.2 |
| 36.1 | Limit State of Collapse — Flexure | `design_singly_reinforced()` | implicit | General principle |
| 36.4.2 | Effective Width of Flange | `calculate_effective_flange_width()` | `@clause` | With 23.1.2 |

## Beam — Shear (`codes/is456/beam/shear.py`)

| Clause | Title | Function | Decorator | Notes |
|--------|-------|----------|-----------|-------|
| 40.1 | Limit State of Collapse: Shear | `calculate_tv()` | `@clause` | Nominal shear stress |
| 40.2 | Design Shear Strength of Concrete | `design_shear()` | `@clause` | Table 19 lookup |
| 40.3 | Enhanced Shear Strength Near Supports | `enhanced_shear_strength()` | `@clause` | |
| 40.4 | Shear Reinforcement Design | `design_shear()` | `@clause` | Combined with 40.1, 40.2 |
| 40.5.1 | Maximum Shear Stress | `design_shear()` | implicit | Table 20 limit |
| 26.5.1.5 | Stirrup Legs | `design_shear()` | `@clause` | |
| 26.5.1.6 | Bent-up Bars | `design_shear()` | `@clause` | |

## Beam — Torsion (`codes/is456/beam/torsion.py`)

| Clause | Title | Function | Decorator | Notes |
|--------|-------|----------|-----------|-------|
| 41.1 | General — Design for Torsion | `design_torsion()` | `@clause` | Master function |
| 41.3 | Critical Section for Torsion | `calculate_torsion_shear_stress()` | `@clause` | |
| 41.3.1 | Equivalent Shear | `calculate_equivalent_shear()` | `@clause` | |
| 41.4 | Reinforcement for Torsion | `design_torsion()` | `@clause` | Combined |
| 41.4.2 | Longitudinal Reinforcement for Torsion | `calculate_equivalent_moment()`, `calculate_longitudinal_torsion_steel()` | `@clause` | Two functions |
| 41.4.3 | Transverse Reinforcement for Torsion | `calculate_torsion_stirrup_area()` | `@clause` | |

## Beam — Detailing (`codes/is456/beam/detailing.py`)

| Clause | Title | Function | Decorator | Notes |
|--------|-------|----------|-----------|-------|
| 26.2.1 | Development Length of Bars | `calculate_development_length()` | `@clause` | |
| 26.2.1.1 | Design Bond Stress | `get_bond_stress()` | `@clause` | |
| 26.2.2 | Anchoring Reinforcement | `calculate_standard_hook()` | `@clause` | |
| 26.2.2.1 | Minimum Bend Radius | `get_min_bend_radius()` | `@clause` | |
| 26.2.2.2 | Stirrup Anchorage | `calculate_stirrup_anchorage()` | `@clause` | |
| 26.2.3 | Standard Hooks and Bends | `calculate_anchorage_length()` | `@clause` | |
| 26.2.3.3 | Anchorage at Simple Supports | `check_anchorage_at_simple_support()` | `@clause` | |
| 26.2.5 | Lap Splices | `calculate_lap_length()` | `@clause` | |
| 26.5.1.3 | Side Face Reinforcement | `check_side_face_reinforcement()` | `@clause` | |

## Beam — Serviceability (`codes/is456/beam/serviceability.py`)

| Clause | Title | Function | Decorator | Notes |
|--------|-------|----------|-----------|-------|
| 43.1 | Limit State of Serviceability: Deflection | `check_deflection_span_depth()` | implicit | Level A check |
| 43.2 | Control of Deflection — Span/Depth Ratios | `check_deflection_span_depth()` | implicit | L/d method |
| 43.2.1 | Modification Factors | `check_deflection_level_b()` | implicit | Level B (Ieff method) |
| 43.3 | Crack Control | `check_crack_width()` | implicit | Crack width calculation |
| 43.4 | Minimum Reinforcement | `check_deflection_span_depth()` | implicit | Referenced in checks |

## Common (`codes/is456/common/`)

| Clause | Title | Function | Module | Decorator | Notes |
|--------|-------|----------|--------|-----------|-------|
| Fig. 23 | Stress-Strain Curve for Steel | `steel_stress_from_strain_5point()` | `stress_blocks.py` | `@clause` | 5-point linearization |
| 6.2 | Properties of Concrete | — | `validation.py` | `clause_ref` | Material validation |
| 6.2.2 | Modulus of Elasticity | — | — | — | Used in serviceability |

## Column — Axial (`codes/is456/column/axial.py`)

| Clause | Title | Function | Decorator | Notes |
|--------|-------|----------|-----------|-------|
| 25.1.2 | Slenderness Limits for Columns | `classify_column()` | `@clause` | Short vs slender |
| 25.2 | Effective Length | `effective_length()` | `@clause` | Table 28 |
| 25.4 | Minimum Eccentricity | `min_eccentricity()` | `@clause` | |
| 39.3 | Short Axially Loaded Members | `short_axial_capacity()` | `@clause` | |

## Column — Uniaxial (`codes/is456/column/uniaxial.py`)

| Clause | Title | Function | Decorator | Notes |
|--------|-------|----------|-----------|-------|
| 39.5 | Uniaxial Bending | `design_short_column_uniaxial()` | `@clause` | |
| 39.5 | P-M Interaction Curve | `pm_interaction_curve()` | `@clause` | Strain compatibility |

## Column — Biaxial (`codes/is456/column/biaxial.py`)

| Clause | Title | Function | Decorator | Notes |
|--------|-------|----------|-----------|-------|
| 39.6 | Biaxial Bending | `biaxial_bending_check()` | `@clause` | Bresler equation |

## Column — Slenderness (`codes/is456/column/slenderness.py`)

| Clause | Title | Function | Decorator | Notes |
|--------|-------|----------|-----------|-------|
| 39.7 | Slender Compression Members | `design_long_column()` | `@clause` | In `long_column.py` |
| 39.7.1 | Additional Moment in Slender Columns | `calculate_additional_moment()` | `@clause` | |

## Column — Other

| Clause | Title | Function | Module | Decorator | Notes |
|--------|-------|----------|--------|-----------|-------|
| 39.4 | Helical Reinforcement | `check_helical_reinforcement()` | `column/helical.py` | `@clause` | 5% strength increase |
| 26.5.3 | Column Detailing | `create_column_detailing()` | `column/detailing.py` | `@clause` | Ties, spacing, cover |

## Footing (`codes/is456/footing/`)

| Clause | Title | Function | Module | Decorator | Notes |
|--------|-------|----------|--------|-----------|-------|
| 34.1 | General Requirements for Footings | `size_footing()` | `footing/bearing.py` | `clause_ref` | Service loads |
| 34.2.3.1 | Bending at Column Face | `footing_flexure()` | `footing/flexure.py` | `clause_ref` | Factored loads |
| 34.2.4.1(a) | One-Way Shear | `footing_one_way_shear()` | `footing/one_way_shear.py` | `clause_ref` | Both directions |
| 34.3.1 | Steel Distribution (Central Band) | `footing_flexure()` | `footing/flexure.py` | `clause_ref` | Rectangular footings |
| 31.6.1 | Punching Shear Critical Section | `footing_punching_shear()` | `footing/punching_shear.py` | `clause_ref` | Two-way shear |
| 31.6.3 | ks Factor | `footing_punching_shear()` | `footing/punching_shear.py` | `clause_ref` | Aspect ratio correction |
| 26.5.2.1 | Minimum Steel | `footing_flexure()` | `footing/flexure.py` | `clause_ref` | Min reinforcement |
| 34.4 | Transfer of Load at Base | — | — | — | **Not implemented** |

## IS 13920:2016 — Ductile Detailing (`codes/is13920/`)

| Clause | Title | Function | Module | Notes |
|--------|-------|----------|--------|-------|
| IS13920 6.1.1 | Flexural Members — Dimensional Limits | `check_beam_ductility()` | `is13920/beam.py` | Geometry checks |
| IS13920 6.1.2 | Flexural Members — Longitudinal Steel | `check_beam_ductility()` | `is13920/beam.py` | Steel limits |
| IS13920 6.2.1 | Flexural Members — Shear Reinforcement | `check_beam_ductility()` | `is13920/beam.py` | Confinement spacing |
| IS13920 6.3 | Lap Splices in Flexural Members | `check_beam_ductility()` | `is13920/beam.py` | |
| IS13920 7.1 | Columns — General Requirements | `check_column_ductility()` | `is13920/column.py` | Geometry constraints |
| IS13920 7.2 | Columns — Longitudinal Steel | `check_column_ductility()` | `is13920/column.py` | Steel limits |
| IS13920 7.3 | Columns — Transverse Reinforcement | `check_column_ductility()` | `is13920/column.py` | Spacing |
| IS13920 7.4 | Special Confining Reinforcement | `check_column_ductility()` | `is13920/column.py` | |
| IS13920 7.4.1 | Area of Special Confining Reinforcement | `calculate_ash_required()` | `is13920/column.py` | Ash formula |

---

## Not Implemented Clauses

The following clauses are defined in `clauses.json` but have **no implementing function** yet:

| Clause | Title | Category |
|--------|-------|----------|
| 5.1–5.6 | Materials (Cement, Admixtures, Aggregates, Water, Reinforcement) | Materials |
| 6.1 | Grades of Concrete | Materials |
| 21.1 | Cover to Reinforcement | Cover |
| 23.1, 23.1.1 | Effective Span — General, Simply Supported | Span |
| 23.2.1 | Slenderness Limits — Beams | Beams |
| 24.1–24.4 | Slab Spans and Reinforcement (Cl 24.1–24.4) | Slabs |
| 25.1, 25.1.1, 25.3 | Column General, Unsupported Length, Classification | Columns |
| 26.3.2, 26.3.3 | Min/Max Spacing of Reinforcement | Detailing |
| 26.5.1.1, 26.5.1.2 | Minimum Shear Reinforcement, Stirrup Spacing | Shear |
| 26.5.3.1, 26.5.3.2 | Column Longitudinal/Transverse Reinforcement | Column detailing |
| 31.6, 31.6.2 | Two-Way Shear (General, Nominal Stress) | Punching |
| 32.1–32.5 | Wall Design | Walls |
| 33.1–33.3 | Stair Design | Stairs |
| 34.2, 34.2.1, 34.2.2, 34.2.4, 34.3 | Footing Moments/Forces (General) | Footings |
| 34.4 | Transfer of Load at Base of Column | Footings |
| 39.1 | Minimum Eccentricity for Column Design | Columns |
| AnnexD-1 to AnnexD-2 | Slab Moment Coefficients | Slabs |
| IS13920 5.1 | General Requirements | Ductile |
| IS13920 8.1 | Beam-Column Joint Requirements | Ductile |
| IS13920 9.1–9.4 | Shear Wall Design | Ductile |
| IS13920 10.1 | Foundation — General | Ductile |

---

*Total clauses in registry: 119. Mapped to functions: 63. Not implemented: 65.*
*Generated: 2026-04-04*
