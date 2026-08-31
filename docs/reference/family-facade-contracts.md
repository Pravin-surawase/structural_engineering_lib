---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: reference
complexity: advanced
tags: [canonical-api, field-contracts, lib-pro-012-r0]
---

# Family Facade Contracts

This file is generated from the live 13-journey registry and strict request
models. It covers 562 advertised request-field leaves. The full JSON
schemas and per-field decisions are in `api-classification.json`.

## Exact signatures and schema identities

| Journey | Constructor | Operation | Fields | Schema SHA-256 |
|---|---|---|---:|---|
| `is456.beam.design/v1` | `input(*, member_id: 'str', story: 'str', case_id: 'str', span_mm: 'float', b_mm: 'float', D_mm: 'float', fck_nmm2: 'float', fy_nmm2: 'float', fy_transverse_nmm2: 'float | None' = None, mu_knm: 'float', vu_kn: 'float', d_dash_mm: 'float', asv_mm2: 'float', d_mm: 'float | None' = None, effective_depth_basis: 'EffectiveDepthBasisRequestV1 | CentroidCoverDepthRequestV1 | None' = None, tu_knm: 'float' = 0.0, pt_percent: 'float | None' = None, ast_mm2_for_shear: 'float | None' = None, detailing: 'BeamDetailingOptionsV1 | None' = None, serviceability: 'BeamServiceabilityV1 | BeamServiceabilityChecksV1 | None' = None, source_provenance: 'str | None' = None) -> 'BeamDesignInputV1'`<br>`load(value: 'Any') -> 'BeamDesignInputV1'` | `design(request: 'BeamDesignInputV1') -> 'BeamDesignResultV1'` | `28` | `afb92bb35bc9ccb0fd19c3c5fee5c548273efef21453af390293a16ee939b01b` |
| `is456.torsion.design/v1` | `input(*, identity: 'Any', geometry: 'Any', actions: 'Any', materials: 'Any', reinforcement: 'Any') -> 'TorsionDesignInputV1'`<br>`load(value: 'Any') -> 'TorsionDesignInputV1'` | `design(request: 'TorsionDesignInputV1') -> 'CanonicalFamilyResultV1'` | `21` | `6fc17a274b7f91760a6129e336e0ff30400b318ebf802c9ed25e071baffec278` |
| `is456.column.supplied-steel-check/v1` | `input(*, identity: 'Any', geometry: 'Any', actions: 'Any', materials: 'Any', reinforcement: 'Any') -> 'ColumnDesignInputV1'`<br>`load(value: 'Any') -> 'ColumnDesignInputV1'` | `design(request: 'ColumnDesignInputV1') -> 'CanonicalFamilyResultV1'`<br>`check(request: 'ColumnDesignInputV1') -> 'CanonicalFamilyResultV1'` | `23` | `9974b5c7f061f55be6a85627211558145485483eeb7ee6b86e5fb4069685fa48` |
| `is456.slab.one-way/v1` | `load_one_way(value: 'Any') -> 'OneWaySlabInputV1'` | `design_one_way(request: 'OneWaySlabInputV1') -> 'CanonicalFamilyResultV1'` | `24` | `230f08e5dd24fa358bb23b834f33ddff90a9a90c9633a8effe5f4f8d7c4e722c` |
| `is456.slab.continuous-one-way/v1` | `load_continuous_one_way(value: 'Any') -> 'ContinuousOneWaySlabInputV1'` | `design_continuous_one_way(request: 'ContinuousOneWaySlabInputV1') -> 'CanonicalFamilyResultV1'` | `35` | `1c92a1c65481924231d351e3c992dfc9dc986e95e880981134c161420752ebd0` |
| `is456.slab.two-way/v1` | `load_two_way(value: 'Any') -> 'TwoWaySlabInputV1'` | `design_two_way(request: 'TwoWaySlabInputV1') -> 'CanonicalFamilyResultV1'` | `37` | `356fd792eb3220b1b960b5560b43548d534bfe34b9fc3556bd7e828adbf32291` |
| `is456.wall.braced-axial/v1` | `input(*, identity_source: 'Any', geometry_topology: 'Any', actions: 'Any', materials_reinforcement: 'Any', evidence_review: 'Any') -> 'BracedWallInputV1'`<br>`load(value: 'Any') -> 'BracedWallInputV1'` | `design(request: 'BracedWallInputV1') -> 'CanonicalFamilyResultV1'` | `27` | `80fbc1565e430256fd6e5d6e2d6a00fdafc051cf7ed775e4943700a67007133d` |
| `is456.staircase.straight-flight/v1` | `input(*, identity_source: 'Any', geometry_topology: 'Any', actions: 'Any', materials_reinforcement: 'Any', evidence_review: 'Any') -> 'StaircaseInputV1'`<br>`load(value: 'Any') -> 'StaircaseInputV1'` | `design(request: 'StaircaseInputV1') -> 'CanonicalFamilyResultV1'` | `35` | `5a619d7bae6f8b518ff8420e20e9501123710cb5967c59c9e0f363ba7b67d46b` |
| `is456.deep-beam.simply-supported/v1` | `input(*, identity_source: 'Any', geometry_topology: 'Any', actions: 'Any', materials_reinforcement: 'Any', evidence_review: 'Any') -> 'DeepBeamInputV1'`<br>`load(value: 'Any') -> 'DeepBeamInputV1'` | `design(request: 'DeepBeamInputV1') -> 'CanonicalFamilyResultV1'` | `38` | `a776607cbee9b5ccf1266e637efeeac00d3c329350f2b26cbefe7d46675f1bdb` |
| `is456.flat-slab.regular-interior/v1` | `input(*, identity_source: 'Any', geometry_topology: 'Any', actions: 'Any', materials_reinforcement: 'Any', evidence_review: 'Any') -> 'FlatSlabInputV1'`<br>`load(value: 'Any') -> 'FlatSlabInputV1'` | `design(request: 'FlatSlabInputV1') -> 'CanonicalFamilyResultV1'` | `69` | `23320e1815a33144d64d27f7612ddbaac0e0e5e6558685f08f9cde2b36d5e505` |
| `is456.isolated-footing.concentric/v1` | `input(*, identity_source: 'Any', geometry_topology: 'Any', actions: 'Any', materials_reinforcement: 'Any', evidence_review: 'Any') -> 'IsolatedFootingInputV1'`<br>`load(value: 'Any') -> 'IsolatedFootingInputV1'` | `design(request: 'IsolatedFootingInputV1') -> 'CanonicalFamilyResultV1'` | `47` | `04dfe10c6788809bd950e72ea5ad9b968658dd807ce1f2ebd0adca63c23cd178` |
| `is456.combined-footing.symmetric/v1` | `input(*, identity_source: 'Any', geometry_topology: 'Any', actions: 'Any', materials_reinforcement: 'Any', evidence_review: 'Any') -> 'CombinedFootingInputV1'`<br>`load(value: 'Any') -> 'CombinedFootingInputV1'` | `design(request: 'CombinedFootingInputV1') -> 'CanonicalFamilyResultV1'` | `72` | `e1d4a20637acad84ff942f52a38bfff3716e37b1d2030d4a1f30fd728869fe31` |
| `is456.strap-footing.property-line/v1` | `input(*, identity_source: 'Any', geometry_topology: 'Any', actions: 'Any', materials_reinforcement: 'Any', evidence_review: 'Any') -> 'StrapFootingInputV1'`<br>`load(value: 'Any') -> 'StrapFootingInputV1'` | `design(request: 'StrapFootingInputV1') -> 'CanonicalFamilyResultV1'` | `106` | `810a37b0d9d343f505cf19a7a4d175e9be1ee034a27c424486472e687154e81b` |

## Validation dimensions

Every advertised field has a decision in the generated classification. A
dimension absent from a route is recorded there as `not_applicable`, never
`UNPROVEN`. The classification also distinguishes a strict request-model
cross-field validator from an explicit delegation to the maintained owner;
generated metadata is not promoted into independent arithmetic evidence.

- `TYPE_AND_FINITE_VALUE`
- `RANGE_AND_ZERO_POLICY`
- `UNIT_AND_QUANTITY`
- `CODE_AND_MATERIAL_DOMAIN`
- `CROSS_FIELD_RELATION`
- `IDENTITY_AND_PROVENANCE`
- `ENUM_AND_TOPOLOGY`
- `COLLECTION_CARDINALITY_AND_UNIQUENESS`
- `DOWNSTREAM_CONSUMABILITY`
- `COMPATIBILITY_ALIAS_AND_MIGRATION_TARGET`

## Units

Units are read from field contracts; `dimensionless` is an explicit quantity
decision rather than a hidden conversion.

| Unit | Field contracts |
|---|---:|
| `%` | 3 |
| `N/mm2` | 28 |
| `dimensionless` | 25 |
| `kN` | 13 |
| `kN.m` | 11 |
| `kN/m` | 2 |
| `kN/m2` | 18 |
| `kPa` | 1 |
| `mm` | 181 |
| `mm2` | 4 |

## Enum and topology values

### `is456.beam.design/v1`

- `detailing.standard`: `IS456`, `IS13920`
### `is456.torsion.design/v1`

- `schema_version`: `torsion-design-input/v1`
### `is456.column.supplied-steel-check/v1`

- `schema_version`: `column-supplied-steel-check-input/v1`
- `geometry.end_condition`: `FIXED_FIXED`, `FIXED_HINGED`, `FIXED_FIXED_SWAY`, `FIXED_FREE`, `HINGED_HINGED`, `FIXED_PARTIAL`, `HINGED_PARTIAL`
- `geometry.braced`: `False`, `True`
### `is456.slab.one-way/v1`

- `schema_version`: `one-way-slab-input/v1`
- `materials.fy_nmm2`: `250`, `415`, `500`
- `serviceability_evidence.serviceability_limit_source_is_approved`: `True`
- `serviceability_evidence.qualified_serviceability_acceptance_acknowledged`: `True`
### `is456.slab.continuous-one-way/v1`

- `schema_version`: `continuous-one-way-slab-input/v1`
- `geometry.uniform_cross_section_acknowledged`: `True`
- `actions.positive_location`: `end_span_positive`, `interior_span_positive`
- `actions.negative_location`: `next_to_end_support_negative`, `other_interior_support_negative`
- `actions.shear_location`: `end_support`, `next_to_end_support_outer`, `next_to_end_support_inner`, `other_interior_support`
- `actions.substantially_uniform_load_acknowledged`: `True`
- `actions.redistribution_applied`: `False`
- `materials.fy_nmm2`: `250`, `415`, `500`
- `serviceability_evidence.serviceability_limit_source_is_approved`: `True`
- `serviceability_evidence.qualified_serviceability_acceptance_acknowledged`: `True`
### `is456.slab.two-way/v1`

- `schema_version`: `two-way-slab-input/v1`
- `geometry.x_min_edge`: `continuous`, `discontinuous`
- `geometry.x_max_edge`: `continuous`, `discontinuous`
- `geometry.y_min_edge`: `continuous`, `discontinuous`
- `geometry.y_max_edge`: `continuous`, `discontinuous`
- `geometry.corner_lift_condition`: `restrained`, `free_to_lift`
- `materials.fy_nmm2`: `250`, `415`, `500`
- `serviceability_evidence.serviceability_limit_source_is_approved`: `True`
- `serviceability_evidence.qualified_serviceability_acceptance_acknowledged`: `True`
### `is456.wall.braced-axial/v1`

- `schema_version`: `braced-wall-input/v1`
- `geometry_topology.rotation_restraint`: `restrained_both_ends`, `not_restrained_both_ends`
- `geometry_topology.bracing_elements_in_two_directions`: `True`
- `geometry_topology.lateral_forces_resisted_by_bracing_system`: `True`
- `geometry_topology.diaphragm_transfer_confirmed`: `True`
- `geometry_topology.lateral_connection_capacity_confirmed`: `True`
- `materials_reinforcement.concrete_grade_nmm2`: `20`, `25`, `30`, `35`, `40`, `45`, `50`, `55`, `60`
- `materials_reinforcement.reinforcement_kind`: `deformed_415_or_greater`, `other_bars`, `welded_wire_fabric`
- `evidence_review.qualified_review_required`: `True`
### `is456.staircase.straight-flight/v1`

- `schema_version`: `straight-flight-staircase-input/v1`
- `geometry_topology.support_case`: `landings_span_with_flight`
- `geometry_topology.span_direction`: `longitudinal`
- `geometry_topology.landings_collinear`: `True`
- `geometry_topology.has_stringer_beams`: `False`
- `geometry_topology.is_cast_in_situ_solid`: `True`
- `materials_reinforcement.fy_nmm2`: `250`, `415`, `500`
- `evidence_review.qualified_review_required`: `True`
### `is456.deep-beam.simply-supported/v1`

- `schema_version`: `simply-supported-deep-beam-input/v1`
- `geometry_topology.support_type`: `simply_supported`
- `geometry_topology.solid_rectangular_section`: `True`
- `geometry_topology.openings_present`: `False`
- `geometry_topology.dapped_ends_present`: `False`
- `geometry_topology.top_loaded`: `True`
- `geometry_topology.hanging_action_required`: `False`
- `materials_reinforcement.concrete_grade_nmm2`: `20`, `25`, `30`, `35`, `40`, `45`, `50`, `55`, `60`
- `materials_reinforcement.steel_grade_nmm2`: `415`, `500`
- `materials_reinforcement.main_bars_continuous_between_supports`: `False`, `True`
- `materials_reinforcement.main_bars_bundled`: `False`
- `materials_reinforcement.main_bar_splices_present`: `False`
- `materials_reinforcement.face_grid_count`: `1`, `2`
- `evidence_review.bearing_nodal_zone_verified`: `True`
- `evidence_review.qualified_review_required`: `True`
### `is456.flat-slab.regular-interior/v1`

- `schema_version`: `regular-interior-flat-slab-input/v1`
- `geometry_topology.analysis_method`: `direct_design`
- `geometry_topology.panel_location`: `interior`
- `geometry_topology.all_spans_equal_x`: `True`
- `geometry_topology.all_spans_equal_y`: `True`
- `geometry_topology.columns_offset_from_grid`: `False`
- `geometry_topology.solid_slab`: `True`
- `geometry_topology.drop_present`: `False`
- `geometry_topology.column_head_present`: `False`
- `geometry_topology.marginal_beam_or_wall_present`: `False`
- `geometry_topology.openings_present`: `False`
- `actions.self_weight_included`: `True`
- `actions.identical_full_loading_on_represented_panels`: `True`
- `actions.patterned_loading_required`: `False`
- `actions.unbalanced_or_lateral_moment_transfer_present`: `False`
- `actions.load_combination_approved`: `True`
- `materials_reinforcement.concrete_grade_nmm2`: `20`, `25`, `30`, `35`, `40`, `45`, `50`, `55`, `60`
- `materials_reinforcement.steel_grade_nmm2`: `415`, `500`
- `materials_reinforcement.uncoated_deformed_bars`: `True`
- `evidence_review.straight_bars_only`: `True`
- `evidence_review.all_bottom_bars_continuous`: `True`
- `evidence_review.splices_present`: `False`
- `evidence_review.serviceability_acceptance_acknowledged`: `True`
- `evidence_review.centred_concentric_reaction`: `True`
- `evidence_review.full_critical_perimeter_available`: `True`
- `evidence_review.no_punching_reinforcement_provided`: `True`
- `evidence_review.qualified_review_required`: `True`
### `is456.isolated-footing.concentric/v1`

- `schema_version`: `concentric-isolated-footing-input/v1`
- `identity_source.service_load_basis`: `includes_footing_self_weight_and_overburden`
- `identity_source.service_load_origin`: `provided`, `assumed`, `verified`
- `identity_source.allowable_soil_pressure_origin`: `provided`, `assumed`, `verified`
- `geometry_topology.footing_type`: `ISOLATED_SQUARE`, `ISOLATED_RECTANGULAR`
- `materials_reinforcement.dowel_bar_type`: `deformed`, `plain`
- `materials_reinforcement.lower_bottom_bar_direction`: `L`, `B`
- `materials_reinforcement.upper_bottom_bar_direction`: `L`, `B`
- `materials_reinforcement.footing_bottom_bar_type`: `deformed`, `plain`
- `materials_reinforcement.bottom_bar_end_arrangement`: `straight`, `bend_90`, `u_hook_180`, `bend_135`, `mechanical`
- `evidence_review.allowable_soil_pressure_is_externally_approved`: `True`
- `evidence_review.effective_supporting_area_basis`: `largest_frustum_1v_2h`
- `evidence_review.effective_supporting_area_origin`: `provided`, `assumed`, `verified`
- `evidence_review.effective_supporting_area_is_approved`: `True`
- `evidence_review.cover_exposure_basis_is_approved`: `True`
- `evidence_review.qualified_review_required`: `True`
### `is456.combined-footing.symmetric/v1`

- `schema_version`: `symmetric-combined-footing-input/v1`
- `geometry_topology.column_count`: `2`
- `geometry_topology.columns_identical`: `True`
- `geometry_topology.columns_square`: `True`
- `geometry_topology.columns_centered_across_width`: `True`
- `geometry_topology.foundation_on_soil`: `True`
- `geometry_topology.constant_depth`: `True`
- `geometry_topology.openings_present`: `False`
- `geometry_topology.pedestals_present`: `False`
- `geometry_topology.analysis_method`: `conventional_rigid`
- `geometry_topology.pressure_model`: `uniform`
- `geometry_topology.rigid_footing_verified`: `True`
- `actions.load_combination_approved`: `True`
- `actions.bearing_and_settlement_approved`: `True`
- `actions.pressure_uniformity_approved`: `True`
- `actions.distributed_carrier_cancellation_approved`: `True`
- `actions.column_moments_present`: `False`
- `actions.horizontal_actions_present`: `False`
- `actions.uplift_or_load_reversal_present`: `False`
- `materials_reinforcement.footing_concrete_grade_nmm2`: `20`, `25`, `30`, `35`, `40`
- `materials_reinforcement.column_concrete_grade_nmm2`: `20`, `25`, `30`, `35`, `40`
- `materials_reinforcement.steel_grade_nmm2`: `415`, `500`
- `materials_reinforcement.uncoated_deformed_bars`: `True`
- `materials_reinforcement.top_longitudinal_diameter_mm`: `8`, `10`, `12`, `16`, `20`, `25`, `32`, `36`
- `materials_reinforcement.bottom_longitudinal_diameter_mm`: `8`, `10`, `12`, `16`, `20`, `25`, `32`, `36`
- `materials_reinforcement.transverse_diameter_mm`: `8`, `10`, `12`, `16`, `20`, `25`, `32`, `36`
- `materials_reinforcement.straight_uncoated_deformed_bars`: `True`
- `materials_reinforcement.effective_depth_basis_approved`: `True`
- `materials_reinforcement.reinforcement_schedule_approved`: `True`
- `materials_reinforcement.effective_supporting_area_basis`: `largest_frustum_1v_2h`
- `materials_reinforcement.effective_supporting_area_approved`: `True`
- `materials_reinforcement.dowel_diameter_mm`: `8`, `10`, `12`, `16`, `20`, `25`, `32`, `36`
- `materials_reinforcement.column_longitudinal_bar_diameter_mm`: `8`, `10`, `12`, `16`, `20`, `25`, `32`, `36`
- `materials_reinforcement.uncoated_deformed_dowels`: `True`
- `evidence_review.qualified_review_required`: `True`
### `is456.strap-footing.property-line/v1`

- `schema_version`: `property-line-strap-footing-input/v1`
- `geometry_topology.footing_count`: `2`
- `geometry_topology.column_count`: `2`
- `geometry_topology.footings_rectangular`: `True`
- `geometry_topology.footings_parallel`: `True`
- `geometry_topology.footings_constant_depth`: `True`
- `geometry_topology.columns_square`: `True`
- `geometry_topology.columns_and_strap_share_centerline`: `True`
- `geometry_topology.interior_column_centered_on_footing`: `True`
- `geometry_topology.strap_straight_and_prismatic`: `True`
- `geometry_topology.strap_centered_across_footings`: `True`
- `geometry_topology.foundation_on_soil`: `True`
- `geometry_topology.strap_soil_contact`: `False`
- `geometry_topology.openings_present`: `False`
- `geometry_topology.pedestals_present`: `False`
- `geometry_topology.analysis_method`: `rigid_equal_pressure`
- `geometry_topology.pressure_model`: `equal_uniform_net`
- `actions.load_combination_approved`: `True`
- `actions.bearing_and_settlement_approved`: `True`
- `actions.equal_uniform_pressure_approved`: `True`
- `actions.footing_carrier_basis_approved`: `True`
- `actions.strap_line_load_basis_approved`: `True`
- `actions.load_pattern_compatible`: `True`
- `actions.column_moments_present`: `False`
- `actions.horizontal_actions_present`: `False`
- `actions.uplift_or_load_reversal_present`: `False`
- `actions.independently_factored_or_patterned_actions_present`: `False`
- `materials_reinforcement.strap_concrete_grade_nmm2`: `20`, `25`, `30`, `35`, `40`
- `materials_reinforcement.steel_grade_nmm2`: `415`, `500`
- `materials_reinforcement.uncoated_deformed_bars`: `True`
- `materials_reinforcement.top_bar_diameter_mm`: `8`, `10`, `12`, `16`, `20`, `25`, `32`, `36`
- `materials_reinforcement.bottom_bar_diameter_mm`: `8`, `10`, `12`, `16`, `20`, `25`, `32`, `36`
- `materials_reinforcement.side_face_bar_diameter_mm`: `8`, `10`, `12`, `16`, `20`, `25`, `32`, `36`
- `materials_reinforcement.stirrup_diameter_mm`: `8`, `10`, `12`, `16`, `20`, `25`, `32`, `36`
- `materials_reinforcement.vertical_closed_stirrups`: `True`
- `materials_reinforcement.straight_anchorage`: `True`
- `materials_reinforcement.bars_bundled`: `False`
- `materials_reinforcement.bars_spliced`: `False`
- `materials_reinforcement.bars_curtailed`: `False`
- `materials_reinforcement.reinforcement_schedule_approved`: `True`
- `materials_reinforcement.effective_depth_basis_approved`: `True`
- `materials_reinforcement.durability_cover_basis_approved`: `True`
- `evidence_review.exterior_footing_design_verified`: `True`
- `evidence_review.interior_footing_design_verified`: `True`
- `evidence_review.column_and_strap_transfer_verified`: `True`
- `evidence_review.footing_reinforcement_and_anchorage_verified`: `True`
- `evidence_review.supporting_areas_verified`: `True`
- `evidence_review.construction_clearances_verified`: `True`
- `evidence_review.qualified_review_required`: `True`

## Structured input issues

Invalid intake raises `InputContractError`. Each issue uses `input-issue/v1`;
transport projection uses `structural-problem/v1`.

- `INPUT_NOT_FINITE`
- `INPUT_TYPE_INVALID`
- `EXTRA_FIELD_FORBIDDEN`
- `REQUIRED_FIELD_MISSING`
- `ENUM_VALUE_INVALID`
- `INPUT_OUT_OF_RANGE`
- `IDENTITY_INVALID`
- `CROSS_FIELD_CONTRACT_INVALID`
- `SERVICEABILITY_SCOPE_HOLD`
- `INPUT_CONTRACT_INVALID`

## Result and review status

- `intake_status`: `VALID` only after strict construction.
- `calculation_status`: `COMPLETED` only after the maintained owner returns.
- `engineering_status`: `PASS`, `FAIL`, or `HOLD`; this is not intake validity.
- `review_status`: remains `QUALIFIED_REVIEW_REQUIRED` for every recipe.
- Result consumption is finite JSON through `to_dict()` and
  `structural-result-envelope/v2`.

No calculation or review status is professional approval, engineering-use
approval, construction-use approval, or Windows application acceptance. The
`v0.24.0` software-release status is tracked separately in the release ledger.
