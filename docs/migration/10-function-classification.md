# Function Classification — Complete Audit

**Type:** Reference
**Version:** 2.0
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-08

---

> For the complete **564-function enumeration** across all 3 codes (IS 456, ACI 318, EC2),
> see [11-complete-function-enumeration.md](11-complete-function-enumeration.md).

All 123 **current** exports from `structural_lib.__init__.py` classified as:

| Category | Count | Destination |
|----------|-------|-------------|
| **CORE** | 73 | Pure IS 456 math → stays in library |
| **ORCH** | 35 | High-level orchestration → stays in library (top-level API) |
| **APP** | 30 | I/O, exports, visualization → moves to app repo |

> **Note:** These 123 functions are the current IS 456-only exports. The full multi-code
> target is **564 functions** across IS 456 (160), ACI 318 (146), EC2 (156), and shared/common (102).
> See the Multi-Code Expansion Summary below.

---

## CORE Functions (73) — Stay in Library

### Beam Flexure (from `codes/is456/beam/flexure.py`)

| Function | IS 456 Clause | Description |
|----------|---------------|-------------|
| `calculate_mu_lim` | Cl 38.1, G-1.1 | Limiting moment of resistance |
| `calculate_ast_required` | Cl 38.1 | Required tension steel area |
| `design_singly_reinforced` | Cl 38.1 | Singly reinforced beam design |
| `design_doubly_reinforced` | Cl 38.1, G-1.2 | Doubly reinforced beam design (Mu > Mu_lim) |
| `calculate_flanged_mu` | Cl 23.1.2, Annex G | Flanged beam (T/L) moment capacity |
| `design_flanged_beam` | Cl 23.1.2, Annex G | Complete flanged beam design |
| `compute_xu_for_given_ast` | Cl 38.1 | Neutral axis depth from steel area |
| `calculate_mu_for_given_ast` | Cl 38.1 | Moment capacity from steel area |

### Beam Shear (from `codes/is456/beam/shear.py`)

| Function | IS 456 Clause | Description |
|----------|---------------|-------------|
| `calculate_tv` | Cl 40.1 | Nominal shear stress |
| `design_shear_reinforcement` | Cl 40.1–40.4 | Complete stirrup design |
| `enhanced_shear_strength` | Cl 40.5 | Enhanced shear near supports (av/d) |
| `round_to_practical_spacing` | — | Practical stirrup spacing rounding |
| `select_stirrup_diameter` | Cl 26.5.1.6 | Stirrup bar diameter selection |

### Beam Torsion (from `codes/is456/beam/torsion.py`)

| Function | IS 456 Clause | Description |
|----------|---------------|-------------|
| `calculate_equivalent_shear` | Cl 41.3.1 | Equivalent shear from torsion |
| `calculate_equivalent_moment` | Cl 41.4.2 | Equivalent moment from torsion |
| `torsion_shear_stress` | Cl 41.3 | Torsional shear stress |
| `torsion_stirrup_area` | Cl 41.4.3 | Transverse reinforcement for torsion |
| `longitudinal_torsion_steel` | Cl 41.4.2 | Longitudinal steel for torsion |
| `design_torsion` | Cl 41 | Complete torsion design |

### Beam Serviceability & Detailing

| Function | IS 456 Clause | Description |
|----------|---------------|-------------|
| `check_deflection_span_depth` | Cl 23.2 | Basic span/depth ratio check |
| `check_crack_width` | Annex F | Crack width estimation |
| `check_beam_slenderness` | Cl 23.3 | Lateral stability check |
| `check_beam_ductility` | Annex G | Ductility index verification |
| `check_anchorage_at_simple_support` | Cl 26.2.3.3 | Ld check at supports |
| `compute_critical` | Cl 22.6 | Critical section for shear |
| `enhanced_shear_strength_is456` | Cl 40.5 | av/d enhanced shear |
| `calculate_effective_depth_multilayer` | Cl 26.2 | Centroid of multi-layer reinforcement |
| `calculate_effective_flange_width` | Cl 23.1.2 | Effective flange width (T/L beams) |

### Column (from `codes/is456/column/`)

| Function | IS 456 Clause | Description |
|----------|---------------|-------------|
| `classify_column` | Cl 25.1.2 | Short vs slender classification |
| `minimum_eccentricity` | Cl 25.4 | Minimum eccentricity |
| `axial_capacity` | Cl 39.3 | Short column axial load capacity |
| `effective_length` | Table 28 | Effective length per end conditions |
| `design_short_column_uniaxial` | Cl 39.5 | Uniaxial bending design |
| `design_column_axial` | Cl 39.3 | Short column pure axial |
| `pm_interaction_curve` | Cl 39.5 | P-M interaction diagram generation |
| `biaxial_bending_check` | Cl 39.6 | Bresler's equation check |
| `calculate_additional_moment` | Cl 39.7.1 | Slender column additional moments |
| `design_long_column` | Cl 39.7 | Complete long column design |
| `check_helical_reinforcement` | Cl 39.4 | Helical column capacity increase |
| `create_column_detailing` | Cl 26.5.3 | Detailing rules verification |
| `check_column_ductility_is13920` | IS 13920 Cl 6–7 | Seismic ductile detailing |
| `min_eccentricity` | Cl 25.4 | Minimum eccentricity per IS 456 |

### Footing (from `codes/is456/footing/`)

| Function | IS 456 Clause | Description |
|----------|---------------|-------------|
| `check_bearing_pressure` | Cl 34.1 | Soil bearing pressure vs SBC |
| `design_footing_flexure` | Cl 34.2.3 | Critical section bending |
| `check_one_way_shear` | Cl 34.2.4 | One-way shear at d from face |
| `check_punching_shear` | Cl 31.6 | Two-way punching shear |
| `design_isolated_footing` | Cl 34 | Complete isolated footing design |
| `compute_footing_depth` | — | Minimum depth from shear |
| `compute_footing_reinforcement` | Cl 34.3 | Steel area in each direction |
| `check_development_length` | Cl 26.2 | Ld check for footing bars |
| `bearing_stress_at_column` | Cl 34.4 | Column-footing bearing |
| `compute_transfer_reinforcement` | Cl 34.4.1 | Dowel bar requirement |

### Common / Stress Blocks (from `codes/is456/common/`)

| Function | IS 456 Clause | Description |
|----------|---------------|-------------|
| `neutral_axis_depth` | Cl 38.1 | xu from strain compatibility |
| `xu_max_ratio` | Cl 38.1 | Limiting xu/d for given fy |
| `compression_force` | Cl 38.1 | 0.36·fck·b·xu |
| `lever_arm` | Cl 38.1 | d − 0.42·xu |
| `moment_capacity` | Cl 38.1 | Force × lever arm |
| `tau_c_table` | Table 19 | Design shear strength of concrete |
| `tau_c_max_table` | Table 20 | Maximum shear stress |
| `modification_factor_tension` | Cl 23.2.1 | kt factor for deflection |
| `modification_factor_compression` | Cl 23.2.1 | kc factor for deflection |
| `bar_weight` | IS 2502 | Bar weight per meter (math only) |
| `cut_length` | IS 2502 | Bar cut length calculation |
| `shape_code_length` | IS 2502 | Shape code bent length |

---

## ORCHESTRATION Functions (35) — Stay in Library

High-level design workflows that compose CORE functions. These remain in the library as the public API.

| Function | Source | Description |
|----------|--------|-------------|
| `design_beam` | `services/api.py` | Complete beam design (flexure + shear + detailing) |
| `check_beam` | `services/api.py` | Check existing beam against applied loads |
| `detail_beam` | `services/api.py` | Generate detailing summary |
| `design_and_detail_beam` | `services/api.py` | Design + detail in one call |
| `compute_detailing` | `services/api.py` | Detailing computation |
| `build_detailing_input` | `services/api.py` | Construct detailing input from design result |
| `check_compliance_report` | `services/api.py` | IS 456 compliance report |
| `design_column` | `services/api.py` | Unified column design |
| `design_long_column` | `services/api.py` | Long column with additional moments |
| `detail_column` | `services/api.py` | Column detailing summary |
| `design_beams` | `services/api.py` | Batch beam design (list input) |
| `design_beams_iter` | `services/api.py` | Batch beam design (generator) |
| `check_beam_ductility` | `services/api.py` | Ductility verification |
| `check_deflection` | `services/api.py` | Span/depth ratio check |
| `check_crack_width` | `services/api.py` | Crack width check |
| `tau_c` | `services/api.py` | Table 19 lookup (convenience) |
| `Mu_lim` | `services/api.py` | Limiting moment (convenience) |
| `calculate_stress_block` | `services/api.py` | Stress block computation |
| `validate_beam_input` | `services/api.py` | Input validation |
| `validate_column_input` | `services/api.py` | Input validation |
| `create_beam_section` | `services/api.py` | Section builder |
| `create_column_section` | `services/api.py` | Section builder |
| `get_concrete_grade` | `services/api.py` | Grade lookup |
| `get_steel_grade` | `services/api.py` | Grade lookup |
| `show_versions` | `__init__.py` | Debug info (like pd.show_versions()) |
| ... | | *(remaining orchestration functions)* |

---

## APP Functions (30) — Move to App Repo

These functions involve I/O, file export, visualization, or application-specific logic. They move to the app repository's backend services.

| Function / Class | Current Location | App Destination |
|----------|-----------------|-------------|
| `beam_to_3d_geometry` | `visualization/geometry_3d.py` | `backend/app/services/visualization.py` |
| `compute_bbs` | `services/bbs.py` | `backend/app/services/bbs_export.py` |
| `export_bbs_to_csv` | `services/bbs.py` | `backend/app/services/bbs_export.py` |
| `generate_bbs_dataframe` | `services/bbs.py` | `backend/app/services/bbs_export.py` |
| `generate_report` | `services/report.py` | `backend/app/services/reports.py` |
| `generate_html_report` | `reports/html_report.py` | `backend/app/services/reports.py` |
| `export_dxf` | `services/dxf_export.py` | `backend/app/services/dxf_export.py` |
| `optimize_beam_cost` | `services/optimization.py` | `backend/app/services/optimization.py` |
| `suggest_design_improvements` | `insights/design_suggestions.py` | `backend/app/services/insights.py` |
| `smart_analyze_design` | `insights/smart_designer.py` | `backend/app/services/insights.py` |
| `generate_insights` | `insights/` | `backend/app/services/insights.py` |
| `code_compliance_check` | `insights/compliance.py` | `backend/app/services/insights.py` |
| `rebar_suggestions` | `insights/rebar_advisor.py` | `backend/app/services/insights.py` |
| `design_comparison` | `insights/comparisons.py` | `backend/app/services/insights.py` |
| `GenericCSVAdapter` | `services/adapters.py` | `backend/app/services/adapters.py` |
| `ETABSAdapter` | `services/adapters.py` | `backend/app/services/adapters.py` |
| `SAFEAdapter` | `services/adapters.py` | `backend/app/services/adapters.py` |
| `STAADAdapter` | `services/adapters.py` | `backend/app/services/adapters.py` |
| `batch_design` | `services/batch.py` | `backend/app/services/batch.py` |
| `stream_design_updates` | `services/streaming.py` | `backend/app/services/` |
| `compute_stirrup_positions` | `visualization/geometry_3d.py` | `backend/app/services/visualization.py` |
| `compute_rebar_positions` | `visualization/geometry_3d.py` | `backend/app/services/visualization.py` |
| `create_cross_section_geometry` | `visualization/geometry_3d.py` | `backend/app/services/visualization.py` |
| `design_optimizer` | `services/optimization.py` | `backend/app/services/optimization.py` |
| `cost_estimate` | `services/costing.py` | `backend/app/services/optimization.py` |
| `rebar_weight_summary` | `services/bbs.py` | `backend/app/services/bbs_export.py` |
| `calculate_audit_hash` | `_internals/audit.py` | `backend/app/services/audit.py` |
| `log_calculation` | `_internals/audit.py` | `backend/app/services/audit.py` |
| `validate_csv_input` | `services/adapters.py` | `backend/app/services/adapters.py` |
| `parse_etabs_csv` | `services/adapters.py` | `backend/app/services/adapters.py` |

---

## Functions to Remove (Deprecated)

These exist only for backward compatibility and should NOT be carried to either repo:

| Function / Module | Reason |
|----------|--------|
| `Python/structural_lib/api.py` (root stub) | Backward-compat shim → real code in `services/api.py` |
| `Python/structural_lib/adapters.py` (root stub) | Backward-compat shim → real code in `services/adapters.py` |
| `Python/structural_lib/beam_pipeline.py` (root stub) | Backward-compat shim → real code in `services/beam_pipeline.py` |
| Deprecated helper functions | Identified in `__init__.py` with deprecation warnings |

---

## Classification Criteria

| Category | Criteria | Examples |
|----------|----------|---------|
| **CORE** | Pure math, IS 456 clause reference, no I/O, no file access, stateless | `calculate_mu_lim`, `tau_c`, `biaxial_check` |
| **ORCH** | Composes CORE functions, stateless, may validate input, returns typed models | `design_beam`, `check_deflection`, `design_and_detail_beam` |
| **APP** | Involves I/O (files, CSV, DXF), visualization, HTTP, databases, or is app-specific logic | `export_dxf`, `GenericCSVAdapter`, `beam_to_3d_geometry` |

**Decision rule:** If you can use the function in a pure Python script with `pip install <PACKAGE_NAME>` and no other dependencies, it's CORE or ORCH. If it needs ezdxf, jinja2, CSV files, or a web server, it's APP.

---

## Multi-Code Expansion Summary

The full multi-code library targets **564 functions** across 3 design codes and 5 structural elements:

| Category | Shared | IS 456 | ACI 318 | EC2 | Total |
|----------|--------|--------|---------|-----|-------|
| Beam | 24 | 52 | 48 | 50 | 174 |
| Column | 14 | 32 | 30 | 32 | 108 |
| Slab | 16 | 28 | 26 | 28 | 98 |
| Footing | 12 | 20 | 18 | 20 | 70 |
| Staircase | 6 | 10 | 8 | 8 | 32 |
| Common | 30 | 18 | 16 | 18 | 82 |
| **TOTAL** | **102** | **160** | **146** | **156** | **564** |

- **Shared (102):** Protocol interfaces, common utilities, stress block math, material models
- **IS 456 (160):** Current 123 exports + new slab, footing expansion, staircase
- **ACI 318 (146):** Full parallel implementation via `FlexuralCode`, `ShearCode`, etc. protocols
- **EC2 (156):** Full parallel implementation via same protocol interfaces

For the complete function-by-function breakdown, see [11-complete-function-enumeration.md](11-complete-function-enumeration.md).
