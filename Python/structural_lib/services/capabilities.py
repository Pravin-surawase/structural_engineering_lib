# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Discoverable supported-case registry for the IS 456 public library."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

__all__ = [
    "IS456_STANDARD_ID",
    "IS456_STANDARD_NAMESPACE",
    "IS456AdapterContract",
    "IS456Capability",
    "IS456FieldAlias",
    "IS456FieldContract",
    "IS456SemanticContract",
    "IS456StatusContract",
    "IS456WorkflowContract",
    "get_supported_is456_capability_document",
    "get_supported_is456_capabilities",
    "get_supported_is456_semantic_contract",
]

CAPABILITY_SCHEMA_VERSION = "2.0"
IS456_STANDARD_ID = "IS456"
IS456_STANDARD_NAMESPACE = "IS456:2000"
IS456_CODE_EDITION = "IS 456:2000"


@dataclass(frozen=True)
class IS456Capability:
    """One intentionally supported public workflow and its held boundary."""

    element: str
    public_workflows: tuple[str, ...]
    supported_case: str
    held_cases: tuple[str, ...]
    qualified_review_required: bool


@dataclass(frozen=True)
class IS456FieldAlias:
    """An intentional compatibility spelling outside canonical serialization."""

    name: str
    deprecated_since: str | None
    remove_in: str | None = None


@dataclass(frozen=True)
class IS456FieldContract:
    """Units, domain, and compatibility semantics for one named quantity."""

    canonical_name: str
    quantity: str
    unit: str
    required: bool
    finite_physical_domain: str
    legacy_aliases: tuple[IS456FieldAlias, ...] = ()


@dataclass(frozen=True)
class IS456StatusContract:
    """Meaning of a status field, including boundaries that it does not prove."""

    canonical_name: str
    meaning: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class IS456WorkflowContract:
    """Semantic surface for one capability-listed public workflow only."""

    workflow: str
    element: str
    fields: tuple[IS456FieldContract, ...]
    statuses: tuple[IS456StatusContract, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class IS456AdapterContract:
    """A narrow transport/serialization boundary for the supported subset."""

    adapter: str
    fields: tuple[IS456FieldContract, ...]
    statuses: tuple[IS456StatusContract, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class IS456SemanticContract:
    """Immutable, machine-readable semantics for the supported public subset."""

    workflows: tuple[IS456WorkflowContract, ...]
    adapters: tuple[IS456AdapterContract, ...]


_CAPABILITIES = (
    IS456Capability(
        element="beam",
        public_workflows=(
            "design_beam_is456",
            "design_flanged_beam_is456",
            "check_beam_is456",
            "detail_beam_is456",
        ),
        supported_case=(
            "Ordinary solid rectangular beam primary design for flexure and shear, "
            "with optional IS 456 torsion within fck 15-40 N/mm2 and fy <= 500 "
            "N/mm2, plus maintained Level-A deflection and crack-width checks when "
            "their explicit inputs are supplied; and monolithic sagging T-beam "
            "flexure with effective-flange-width calculation, web shear, and the "
            "same explicit serviceability boundary."
        ),
        held_cases=(
            "L-beam, hogging/flange-in-tension, flanged torsion, hollow/box, deep, prestressed, or axially loaded cases are excluded.",
            "Compatibility-versus-equilibrium torsion redistribution decisions are excluded.",
            "Load-envelope generation and completeness validation are excluded; the flanged route accepts only declared supplied factored actions.",
            "Composed flanged detailing remains excluded.",
            "Beam check, detailing, batch, import, and other automation surfaces that do not accept Tu and serviceability inputs remain outside the combined route.",
            "Serviceability is held unless span, support condition, crack geometry, and service strain or stress are explicitly supplied.",
        ),
        qualified_review_required=True,
    ),
    IS456Capability(
        element="column",
        public_workflows=("design_column_is456", "design_long_column_is456"),
        supported_case=(
            "Solid rectangular tied columns under factored compression with "
            "uniaxial or biaxial bending, using one total longitudinal-steel area "
            "split equally between two opposite faces at one centroidal depth; "
            "short and slender member routes are selected by the declared IS 456 "
            "effective-length inputs."
        ),
        held_cases=(
            "Circular-section column design is excluded; the separate supplied-helix check does not constitute a circular-column design workflow.",
            "Asymmetric, perimeter-resolved, and arbitrary multilayer reinforcement layouts are excluded because the stable routes accept only Asc_mm2 and one d_prime_mm.",
            "The rectangular arbitrary-layout P-M-M fiber module remains experimental, is not exported by the stable service or package facades, and does not return a supported design decision.",
            "Load-envelope generation, frame analysis, effective-length derivation beyond the declared end-condition model, and automatic reinforcement sizing are excluded.",
        ),
        qualified_review_required=True,
    ),
    IS456Capability(
        element="isolated_footing",
        public_workflows=(
            "design_concentric_isolated_footing_is456",
            "size_footing",
            "footing_flexure",
            "footing_one_way_shear",
            "footing_punching_shear",
            "check_bearing_pressure",
            "check_isolated_footing_load_transfer",
        ),
        supported_case=(
            "Centred, concentrically loaded square or rectangular isolated "
            "footings with a uniform trial thickness: service-load sizing from "
            "an externally approved allowable soil pressure, factored flexure, "
            "one-way shear, punching shear, approved-basis bearing/load transfer, "
            "and provided-bar detailing when every detailing input is explicit."
        ),
        held_cases=(
            "Eccentric loading, moment transfer, partial contact or soil tension, and pressure-envelope generation are excluded from the composed route.",
            "Bearing/load-transfer results require an explicitly approved effective supporting-area basis and qualified review of the complete footing design.",
            "Combined, strap, raft, pile-cap, settlement, soil-structure interaction, lateral, sliding, uplift and global-overturning design are excluded.",
            "Stepped, sloped, circular, edge/corner punching and arbitrary footing geometry are excluded.",
        ),
        qualified_review_required=True,
    ),
    IS456Capability(
        element="solid_slab",
        public_workflows=(
            "design_one_way_slab_is456",
            "design_complete_one_way_slab_is456",
            "design_continuous_one_way_slab_is456",
            "design_continuous_one_way_slab_builtin_is456",
            "design_two_way_slab_is456",
            "design_two_way_slab_panel_is456",
            "design_two_way_slab_panel_builtin_is456",
        ),
        supported_case=(
            "Simply supported and coefficient-method continuous one-way solid strips; "
            "common oriented two-way beam/wall-supported panels with built-in bounded "
            "IS 456 coefficient lookup/interpolation or reviewed external coefficients, "
            "strip distribution, corner torsion, provided-bar checks, span/depth "
            "serviceability carriers, and ordinary one-way shear."
        ),
        held_cases=(
            "Direct deflection remains held until a slab-specific route validates explicit service-action combinations, load duration, reinforcement positions, cracking/effective inertia, creep and shrinkage against independent slab benchmarks.",
            "Crack width remains held until explicit bar geometry, cover, neutral-axis depth, exposure limit and service steel stress or strain are validated for supported slab strips and panels.",
            "Each public route consumes one caller-selected factored UDL or one declared coefficient-method action basis; concentrated loads, openings, irregular panels, load-combination/pattern generation and envelope analysis are excluded.",
            "Ordinary one-way concrete shear is checked for beam/wall-supported UDL panels; when capacity is exceeded the result requires increased depth or separate engineering and never automatically designs slab shear reinforcement.",
            "Flat/drop/ribbed slabs, column strips, column-supported punching and FEM require a separately approved extension.",
        ),
        qualified_review_required=True,
    ),
    IS456Capability(
        element="stair",
        public_workflows=("design_straight_flight_staircase_is456",),
        supported_case=(
            "One cast-in-situ solid longitudinal straight waist-slab flight "
            "with two collinear landing effective segments spanning between "
            "outer beam or wall supports; explicit horizontal-plan self-weight, "
            "caller-supplied superimposed service loads and load shares, "
            "three-segment actions, flexure, supplied-bar checks, ordinary "
            "one-way shear, and the basic span/depth serviceability boundary."
        ),
        held_cases=(
            "Dog-legged, open-well, quarter-turn, half-turn, bifurcated, cantilever, spiral, transverse, precast, and stringer-supported stairs are excluded.",
            "IS 875 load generation, project load combinations, load patterns, continuity, redistribution, concentrated actions, and seismic behavior are excluded.",
            "Modification factors, direct deflection, crack width, development-length layout, landing torsion, and automatic bar selection remain held.",
        ),
        qualified_review_required=True,
    ),
    IS456Capability(
        element="wall",
        public_workflows=("design_braced_wall_is456",),
        supported_case=(
            "One regular 100-200 mm thick, one-grid, Clause 32.2 braced "
            "reinforced-concrete wall under caller-supplied factored in-plane "
            "vertical compression, with empirical axial-capacity and Clause "
            "32.5 caller-provided minimum-reinforcement checks."
        ),
        held_cases=(
            "Applied moment, horizontal action, wall shear, combined flexure, openings, and out-of-plane behavior are excluded.",
            "Walls thicker than 200 mm, two reinforcement grids, and transverse-enclosure design are excluded.",
            "Global analysis, load generation, load combinations, bar selection, anchorage, lap, crack width, and direct deflection are excluded.",
            "Seismic/shear-wall provisions and IS 13920 detailing are excluded.",
        ),
        qualified_review_required=True,
    ),
    IS456Capability(
        element="deep_beam",
        public_workflows=("design_simply_supported_deep_beam_is456",),
        supported_case=(
            "One simply supported, single-span, solid rectangular, top-loaded Clause "
            "29 deep beam without openings, dapped ends, or hanging action; the caller "
            "supplies one positive factored moment, provided positive tie/detailing, and "
            "external bearing/compression-nodal verification."
        ),
        held_cases=(
            "Continuous and cantilever deep beams, negative moment, openings, dapped ends, corbels, coupling beams, hollow/flanged/irregular sections, prestress, and hanging action are excluded.",
            "The workflow does not generate loads or reactions and does not calculate bearing, support, compression-strut, or nodal-zone capacity.",
            "Automatic section or bar selection, bundles, splices, transverse-enclosure design, crack width, deflection, fire, and seismic/IS 13920 checks are excluded.",
            "Generalized strut-and-tie modelling, nonlinear analysis, FEM, professional approval, and release authorization are excluded.",
        ),
        qualified_review_required=True,
    ),
    IS456Capability(
        element="flat_slab",
        public_workflows=("design_regular_interior_flat_slab_is456",),
        supported_case=(
            "One equal-span square interior solid flat-slab panel in a grid of at "
            "least three continuous spans each way, designed by the direct design "
            "method under identical full uniform gravity loading, with a square "
            "centred column, no drop or head, caller-provided straight bars, "
            "reviewed span/depth acceptance, and one full-perimeter concrete-only "
            "punching check."
        ),
        held_cases=(
            "Unequal or rectangular panels, fewer than three continuous spans, exterior panels, edge/corner or offset columns, drops, column heads, marginal beams or walls, and openings are excluded.",
            "Patterned or nonuniform loading, point or line loads, load-combination or envelope generation, lateral action, and unbalanced moment transfer are excluded.",
            "Equivalent-frame analysis, FEM, nonlinear analysis, transfer slabs, post-tensioning, prestress, seismic diaphragm/action design, and progressive-collapse design are excluded.",
            "Punching reinforcement, automatic depth/bar selection, bends, splices, anchorage layout, congestion, direct deflection, crack width, fire, and professional approval are excluded.",
        ),
        qualified_review_required=True,
    ),
    IS456Capability(
        element="combined_footing",
        public_workflows=("design_symmetric_combined_footing_is456",),
        supported_case=(
            "Exactly two identical square columns with equal concentric axial "
            "loads on one symmetric rigid rectangular constant-depth footing on "
            "soil, using an externally approved uniform pressure model and "
            "caller-provided reinforcement, supporting-area, and dowel evidence."
        ),
        held_cases=(
            "Unequal or eccentric loads, column moments, horizontal actions, uplift or load reversal, property-line layouts, trapezoidal or irregular plans, alternate columns, pedestals, openings, and variable-depth footings are excluded.",
            "Flexible, variable, nonlinear, or tensile soil pressure; bearing-capacity or settlement calculation; elastic-line, Winkler, plate, finite-element, and soil-structure-interaction analysis are excluded.",
            "Shear or punching reinforcement, coated, bundled, spliced or curtailed bars, automatic sizing or bar selection, durability selection, and construction approval are excluded.",
            "Strap footings, pile caps, raft foundations, React publication, release, professional approval, and complete engineering approval are excluded.",
        ),
        qualified_review_required=True,
    ),
)


def _field(
    canonical_name: str,
    quantity: str,
    unit: str,
    required: bool,
    finite_physical_domain: str,
    *legacy_aliases: IS456FieldAlias,
) -> IS456FieldContract:
    """Keep the static contract compact without weakening its explicit metadata."""
    return IS456FieldContract(
        canonical_name=canonical_name,
        quantity=quantity,
        unit=unit,
        required=required,
        finite_physical_domain=finite_physical_domain,
        legacy_aliases=legacy_aliases,
    )


_MM = "finite positive millimetres where required by the workflow"
_N_PER_MM2 = "finite positive N/mm2 within the workflow material domain"
_BOOLEAN = "literal boolean only"
_REPORT_IS_SAFE_ALIAS = IS456FieldAlias("is_safe", "0.23.0", "0.24.0")
# These are compatibility properties on frozen slab records/results, not input
# aliases scheduled for removal.  They intentionally have no removal target.
_SLAB_REVIEW_ALIAS = IS456FieldAlias("review_status", None)
_SLAB_ACCEPTANCE_ALIAS = IS456FieldAlias(
    "qualified_coefficient_acceptance_acknowledged", None
)
_SLAB_VERIFICATION_ALIAS = IS456FieldAlias("coefficient_correctness_is_verified", None)
_SLAB_SUPPORT_ALIAS = IS456FieldAlias("is_supported", None)

_SEMANTIC_CONTRACT = IS456SemanticContract(
    workflows=(
        IS456WorkflowContract(
            workflow="design_beam_is456",
            element="beam",
            fields=(
                _field("mu_knm", "factored bending moment", "kN m", True, "finite"),
                _field("vu_kn", "factored shear force", "kN", True, "finite"),
                _field(
                    "tu_knm",
                    "factored torsional moment",
                    "kN m",
                    False,
                    "finite non-negative; zero opts out",
                ),
                _field("b_mm", "section width", "mm", True, _MM),
                _field("D_mm", "overall section depth", "mm", True, _MM),
                _field("d_mm", "effective section depth", "mm", True, _MM),
                _field("fck_nmm2", "concrete strength", "N/mm2", True, _N_PER_MM2),
                _field("fy_nmm2", "steel strength", "N/mm2", True, _N_PER_MM2),
                _field("cover_mm", "clear cover for torsion core", "mm", False, _MM),
                _field(
                    "stirrup_dia_mm",
                    "closed stirrup diameter",
                    "mm",
                    False,
                    _MM,
                ),
                _field(
                    "deflection_params",
                    "explicit Level-A deflection inputs",
                    "structured input",
                    False,
                    "span, effective depth, and supported condition",
                ),
                _field(
                    "crack_width_params",
                    "explicit Level-A crack-width inputs",
                    "structured input",
                    False,
                    "complete maintained crack geometry and strain or service stress",
                ),
                _field(
                    "is_ok", "combined compliance outcome", "boolean", True, _BOOLEAN
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "is_ok",
                    "All evaluated flexure, shear, torsion, and enabled serviceability checks passed.",
                    (
                        "It is software evidence, not professional design approval.",
                        "Missing or invalid evidence identity is a HOLD, not a pass.",
                    ),
                ),
            ),
            limitations=(
                "Optional torsion is limited to the ordinary solid rectangular route.",
                "Serviceability requires explicit maintained inputs.",
                "Qualified engineering review remains required.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_flanged_beam_is456",
            element="beam",
            fields=(
                _field(
                    "mu_knm",
                    "supplied factored sagging moment",
                    "kN m",
                    True,
                    "finite non-negative",
                ),
                _field(
                    "vu_kn",
                    "supplied factored shear force",
                    "kN",
                    True,
                    "finite non-negative",
                ),
                _field("bw_mm", "web width", "mm", True, _MM),
                _field("D_mm", "overall section depth", "mm", True, _MM),
                _field("d_mm", "effective section depth", "mm", True, _MM),
                _field("span_mm", "effective span", "mm", True, _MM),
                _field(
                    "flange_thickness_mm",
                    "compression flange thickness",
                    "mm",
                    True,
                    _MM,
                ),
                _field(
                    "flange_overhang_left_mm",
                    "left physical flange overhang",
                    "mm",
                    True,
                    _MM,
                ),
                _field(
                    "flange_overhang_right_mm",
                    "right physical flange overhang",
                    "mm",
                    True,
                    _MM,
                ),
                _field(
                    "bf_effective_mm",
                    "calculated effective flange width",
                    "mm",
                    True,
                    _MM,
                ),
                _field("fck_nmm2", "concrete strength", "N/mm2", True, _N_PER_MM2),
                _field("fy_nmm2", "steel strength", "N/mm2", True, _N_PER_MM2),
                _field(
                    "load_case_basis",
                    "supplied action basis",
                    "enumeration",
                    True,
                    "single factored case or supplied governing envelope",
                ),
                _field(
                    "is_ok", "combined compliance outcome", "boolean", True, _BOOLEAN
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "is_ok",
                    "The supported sagging T-beam flexure, web shear, and every enabled serviceability check pass.",
                    (
                        "Only supplied already-factored actions are evaluated.",
                        "It is software evidence, not professional design approval.",
                    ),
                ),
            ),
            limitations=(
                "Only the independently benchmarked monolithic sagging T-beam route is supported.",
                "L-beam, hogging, flanged torsion, torsion redistribution, load-envelope generation, and composed detailing are held.",
                "Serviceability requires explicit maintained inputs matching the section geometry.",
                "Qualified engineering review remains required.",
            ),
        ),
        IS456WorkflowContract(
            workflow="check_beam_is456",
            element="beam",
            fields=(
                _field(
                    "cases",
                    "declared beam load cases",
                    "structured input",
                    True,
                    "non-empty sequence",
                ),
                _field("b_mm", "section width", "mm", True, _MM),
                _field("D_mm", "overall section depth", "mm", True, _MM),
                _field("d_mm", "effective section depth", "mm", True, _MM),
                _field(
                    "is_ok", "multi-case compliance outcome", "boolean", True, _BOOLEAN
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "is_ok",
                    "All evaluated cases pass.",
                    ("Only supplied cases are evaluated.",),
                ),
            ),
            limitations=("Torsion is not included by this primary combined route.",),
        ),
        IS456WorkflowContract(
            workflow="detail_beam_is456",
            element="beam",
            fields=(
                _field(
                    "beam_id", "beam identifier", "identifier", True, "non-empty text"
                ),
                _field("span_mm", "beam span", "mm", True, _MM),
                _field("cover_mm", "nominal cover", "mm", True, _MM),
                _field("stirrup_dia_mm", "stirrup diameter", "mm", False, _MM),
                _field(
                    "stirrup_spacing_start_mm",
                    "start-zone stirrup spacing",
                    "mm",
                    False,
                    _MM,
                ),
                _field("stirrup_spacing_mid_mm", "stirrup spacing", "mm", False, _MM),
                _field(
                    "stirrup_spacing_end_mm",
                    "end-zone stirrup spacing",
                    "mm",
                    False,
                    _MM,
                ),
                _field(
                    "top_bars",
                    "detailed top reinforcement arrangements",
                    "structured output",
                    True,
                    "three declared beam zones",
                ),
                _field(
                    "bottom_bars",
                    "detailed bottom reinforcement arrangements",
                    "structured output",
                    True,
                    "three declared beam zones",
                ),
                _field(
                    "stirrups",
                    "detailed stirrup arrangements",
                    "structured output",
                    True,
                    "three declared beam zones",
                ),
                _field(
                    "ld_tension",
                    "tension development length",
                    "mm",
                    True,
                    "finite non-negative",
                ),
                _field(
                    "ld_compression",
                    "compression development length",
                    "mm",
                    True,
                    "finite non-negative",
                ),
                _field("is_valid", "detailing validity", "boolean", True, _BOOLEAN),
            ),
            statuses=(
                IS456StatusContract(
                    "is_valid",
                    "The generated detailing satisfies its bounded checks.",
                    ("It does not add torsion design.",),
                ),
            ),
            limitations=("Detailing follows the supplied reinforcement demands.",),
        ),
        IS456WorkflowContract(
            workflow="design_column_is456",
            element="column",
            fields=(
                _field("Pu_kN", "factored axial load", "kN", True, "finite"),
                _field(
                    "Mux_kNm", "factored major-axis moment", "kN m", False, "finite"
                ),
                _field(
                    "Muy_kNm", "factored minor-axis moment", "kN m", False, "finite"
                ),
                _field("b_mm", "section width", "mm", False, _MM),
                _field("D_mm", "section depth", "mm", False, _MM),
            ),
            statuses=(),
            limitations=(
                "Solid rectangular section only, with Asc_mm2 split equally between two opposite faces at one d_prime_mm; circular and arbitrary-layout design are excluded.",
                "The experimental arbitrary-layout P-M-M fiber surface is not a stable design-decision route.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_long_column_is456",
            element="column",
            fields=(
                _field("Pu_kN", "factored axial load", "kN", True, "finite"),
                _field("lex_mm", "effective length about x", "mm", True, _MM),
                _field("ley_mm", "effective length about y", "mm", True, _MM),
                _field("fck_nmm2", "concrete strength", "N/mm2", False, _N_PER_MM2),
                _field("fy_nmm2", "steel strength", "N/mm2", False, _N_PER_MM2),
            ),
            statuses=(),
            limitations=(
                "Solid rectangular section only, with Asc_mm2 split equally between two opposite faces at one d_prime_mm.",
                "Frame analysis, circular sections, arbitrary reinforcement layouts, and the experimental P-M-M surface are excluded.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_concentric_isolated_footing_is456",
            element="isolated_footing",
            fields=(
                _field(
                    "request",
                    "typed concentric isolated-footing request",
                    "ConcentricIsolatedFootingInput",
                    True,
                    "validated explicit input contract",
                ),
                _field(
                    "status",
                    "aggregate workflow disposition",
                    "enumeration",
                    True,
                    "PASS, FAIL or HOLD",
                ),
                _field(
                    "service_axial_load_kN",
                    "echoed service axial action used for sizing",
                    "kN",
                    True,
                    "finite positive",
                ),
                _field(
                    "factored_axial_load_kN",
                    "echoed factored axial action used for structural checks",
                    "kN",
                    True,
                    "finite positive",
                ),
                _field(
                    "selected_overall_thickness_mm",
                    "first passing uniform trial thickness",
                    "mm",
                    True,
                    "positive or null when no candidate passes",
                ),
                _field(
                    "detailing_status",
                    "provided-bar detailing disposition",
                    "enumeration",
                    True,
                    "PASS, FAIL or HOLD",
                ),
                _field(
                    "qualified_review_required",
                    "qualified review boundary",
                    "boolean",
                    True,
                    "always true",
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "status",
                    "All composed calculation and detailing checks passed without a retained hold.",
                    (
                        "PASS is bounded software evidence, not professional design approval.",
                        "Missing explicit detailing inputs return HOLD rather than a complete-design PASS.",
                    ),
                ),
            ),
            limitations=(
                "Centred concentric square/rectangular isolated footing with uniform thickness only.",
                "Service and factored actions are independent supplied inputs; the service action must include footing self-weight and overburden.",
                "Allowable soil pressure and effective supporting-area geometry must be externally established and explicitly approved.",
                "Eccentric/contact-pressure envelopes and all other foundation systems remain excluded.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_straight_flight_staircase_is456",
            element="stair",
            fields=(
                _field(
                    "request",
                    "typed straight-flight staircase request",
                    "StraightFlightStaircaseInput",
                    True,
                    "validated explicit input contract",
                ),
                _field(
                    "status",
                    "aggregate bounded design disposition",
                    "enumeration",
                    True,
                    "PASS, REVIEW_REQUIRED or FAIL",
                ),
                _field(
                    "geometry.effective_span_mm",
                    "horizontal effective support span",
                    "mm",
                    True,
                    _MM,
                ),
                _field(
                    "actions.maximum_factored_moment_knm_per_m",
                    "maximum factored sagging moment per metre width",
                    "kN m/m",
                    True,
                    "finite non-negative",
                ),
                _field(
                    "complete_engineering_design_approved",
                    "complete engineering approval",
                    "boolean",
                    True,
                    "always false",
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "status",
                    "PASS only when represented strength, supplied-bar, ordinary-shear, and basic span/depth checks pass.",
                    (
                        "REVIEW_REQUIRED preserves an unresolved basic serviceability boundary.",
                        "PASS is bounded software evidence, not professional design approval.",
                    ),
                ),
            ),
            limitations=(
                "Only the declared cast-in-situ longitudinal straight-flight waist-slab case is supported.",
                "Loads, shares, and ultimate factor are caller supplied; IS 875 actions and project combinations are not generated.",
                "Alternate stair systems, continuity, modification factors, direct deflection, crack width, landing torsion, and automatic bar selection remain held.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_braced_wall_is456",
            element="wall",
            fields=(
                _field(
                    "request",
                    "typed braced-wall request",
                    "BracedWallDesignInput",
                    True,
                    "validated explicit input contract",
                ),
                _field(
                    "status",
                    "aggregate axial and reinforcement disposition",
                    "enumeration",
                    True,
                    "PASS or FAIL",
                ),
                _field(
                    "request.wall_thickness_mm",
                    "wall thickness",
                    "mm",
                    True,
                    "finite from 100 through 200",
                ),
                _field(
                    "request.factored_axial_load_kn",
                    "caller-supplied factored vertical compression",
                    "kN",
                    True,
                    "finite positive",
                ),
                _field(
                    "request.supplied_eccentricity_mm",
                    "caller-supplied transverse load eccentricity",
                    "mm",
                    True,
                    "finite non-negative",
                ),
                _field(
                    "axial.utilization_ratio",
                    "empirical axial demand-to-capacity ratio",
                    "dimensionless",
                    True,
                    "finite non-negative",
                ),
                _field(
                    "reinforcement.status",
                    "provided minimum-reinforcement disposition",
                    "enumeration",
                    True,
                    "PASS or FAIL",
                ),
                _field(
                    "qualified_review_required",
                    "qualified review boundary",
                    "boolean",
                    True,
                    "always true",
                ),
                _field(
                    "complete_engineering_design_approved",
                    "complete engineering approval",
                    "boolean",
                    True,
                    "always false",
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "status",
                    "PASS only when empirical axial capacity and both provided-reinforcement directions pass within the one-grid scope.",
                    (
                        "PASS is bounded software evidence, not professional design approval.",
                        "Load generation, moments, horizontal actions, shear, openings, and seismic detailing are not represented.",
                    ),
                ),
            ),
            limitations=(
                "Only the declared regular 100-200 mm one-grid Clause 32.2 braced wall is supported.",
                "Factored compression, eccentricity, bracing assertions, and provenance are caller supplied.",
                "Two-grid and transverse-enclosure design, combined flexure, shear, openings, and seismic provisions remain held.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_simply_supported_deep_beam_is456",
            element="deep_beam",
            fields=(
                _field(
                    "request",
                    "typed simply supported deep-beam request",
                    "SimplySupportedDeepBeamDesignInput",
                    True,
                    "validated explicit input contract",
                ),
                _field(
                    "status",
                    "aggregate positive tie and detailing disposition",
                    "enumeration",
                    True,
                    "PASS or FAIL",
                ),
                _field(
                    "request.centre_to_centre_span_mm",
                    "centre-to-centre support span",
                    "mm",
                    True,
                    _MM,
                ),
                _field(
                    "request.clear_span_mm",
                    "clear support span",
                    "mm",
                    True,
                    _MM,
                ),
                _field(
                    "request.overall_depth_mm",
                    "overall member depth",
                    "mm",
                    True,
                    _MM,
                ),
                _field(
                    "request.beam_width_mm",
                    "solid rectangular web width",
                    "mm",
                    True,
                    _MM,
                ),
                _field(
                    "request.factored_positive_moment_knm",
                    "caller-supplied positive factored moment",
                    "kN m",
                    True,
                    "finite positive",
                ),
                _field(
                    "request.bearing_nodal_zone_verified",
                    "external bearing and compression-nodal prerequisite",
                    "boolean",
                    True,
                    "literal true only",
                ),
                _field(
                    "reinforcement.geometry",
                    "Clause 29 classification, effective span, and lever arm",
                    "DeepBeamGeometryResult",
                    True,
                    "typed finite geometry result with mm quantities",
                ),
                _field(
                    "reinforcement.positive_tie",
                    "required and provided positive tie check",
                    "DeepBeamTieResult",
                    True,
                    "typed PASS or FAIL result with mm2 areas",
                ),
                _field(
                    "reinforcement.placement",
                    "positive tie placement-zone check",
                    "DeepBeamPlacementResult",
                    True,
                    "typed PASS or FAIL result with mm distances",
                ),
                _field(
                    "reinforcement.anchorage",
                    "both-support 0.8Ld anchorage disposition",
                    "DeepBeamAnchorageResult",
                    True,
                    "typed PASS or FAIL result with mm lengths and N/mm2 stresses",
                ),
                _field(
                    "reinforcement.vertical_side_face",
                    "vertical side-face area and spacing disposition",
                    "DeepBeamSideFaceDirectionResult",
                    True,
                    "typed PASS or FAIL result with ratio, mm2/m, and mm quantities",
                ),
                _field(
                    "reinforcement.horizontal_side_face",
                    "horizontal side-face area and spacing disposition",
                    "DeepBeamSideFaceDirectionResult",
                    True,
                    "typed PASS or FAIL result with ratio, mm2/m, and mm quantities",
                ),
                _field(
                    "reinforcement.status",
                    "composed Clause 29 reinforcement disposition",
                    "enumeration",
                    True,
                    "PASS or FAIL",
                ),
                _field(
                    "qualified_review_required",
                    "qualified review boundary",
                    "boolean",
                    True,
                    "always true",
                ),
                _field(
                    "complete_engineering_design_approved",
                    "complete engineering approval",
                    "boolean",
                    True,
                    "always false",
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "status",
                    "PASS only when classification, positive tie, placement, continuity, both anchorages, both side-face directions, and the external prerequisite pass.",
                    (
                        "The bounded Clause 29 shear-deemed-satisfied statement is not a bearing or nodal-zone capacity approval.",
                        "PASS is bounded software evidence, not professional design approval.",
                    ),
                ),
            ),
            limitations=(
                "Only the declared simply supported solid rectangular top-loaded Clause 29 case is supported.",
                "The positive factored moment and bearing/compression-nodal verification are caller supplied; loads, reactions, and those capacities are not generated.",
                "Continuous beams, openings, hanging action, automatic sizing, transverse enclosure, generalized strut-and-tie, seismic design, nonlinear analysis, and FEM remain held.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_regular_interior_flat_slab_is456",
            element="flat_slab",
            fields=(
                _field(
                    "request",
                    "typed regular interior flat-slab request",
                    "RegularInteriorFlatSlabDesignInput",
                    True,
                    "validated explicit input contract",
                ),
                _field(
                    "status",
                    "aggregate flexure, detailing, reviewed span/depth, and punching disposition",
                    "enumeration",
                    True,
                    "PASS or FAIL",
                ),
                _field(
                    "request.panel.geometry",
                    "equal-span square interior-panel geometry",
                    "FlatSlabGridGeometry",
                    True,
                    "explicit dimensions in mm and literal topology assertions",
                ),
                _field(
                    "request.panel.gravity_load.factored_uniform_load_kn_per_m2",
                    "approved-basis factored uniform gravity action",
                    "kN/m2",
                    True,
                    "finite positive and consistent with 1.5 times service dead plus live load",
                ),
                _field(
                    "request.x",
                    "caller-provided x-direction bars and support extension",
                    "FlatSlabDirectionDetailingInput",
                    True,
                    "positive bar diameters, spacings, and extension in mm",
                ),
                _field(
                    "request.y",
                    "caller-provided y-direction bars and support extension",
                    "FlatSlabDirectionDetailingInput",
                    True,
                    "positive bar diameters, spacings, and extension in mm",
                ),
                _field(
                    "request.factored_support_reaction_kn",
                    "caller-supplied factored interior-column reaction",
                    "kN",
                    True,
                    "finite positive and equal to the frozen uniform tributary reaction",
                ),
                _field(
                    "reinforcement.moments",
                    "both-direction direct-design moments and strip distribution",
                    "FlatSlabMomentResult",
                    True,
                    "typed finite kN, kN m, and span results",
                ),
                _field(
                    "reinforcement.x",
                    "x-direction flexure and provided-bar disposition",
                    "FlatSlabDirectionReinforcementResult",
                    True,
                    "typed required/provided mm2 and mm2/m plus spacing and extension limits",
                ),
                _field(
                    "reinforcement.y",
                    "y-direction flexure and provided-bar disposition",
                    "FlatSlabDirectionReinforcementResult",
                    True,
                    "typed required/provided mm2 and mm2/m plus spacing and extension limits",
                ),
                _field(
                    "reinforcement.x_serviceability",
                    "reviewed x-direction span/depth comparison",
                    "SlabServiceabilityResult",
                    True,
                    "reviewed limit only; direct deflection and crack width remain held",
                ),
                _field(
                    "reinforcement.y_serviceability",
                    "reviewed y-direction span/depth comparison",
                    "SlabServiceabilityResult",
                    True,
                    "reviewed limit only; direct deflection and crack width remain held",
                ),
                _field(
                    "punching.status",
                    "centred full-perimeter concrete-only punching disposition",
                    "enumeration",
                    True,
                    "safe without reinforcement, reinforcement or redesign required, or redesign required",
                ),
                _field(
                    "qualified_review_required",
                    "qualified review boundary",
                    "boolean",
                    True,
                    "always true",
                ),
                _field(
                    "complete_engineering_design_approved",
                    "complete engineering approval",
                    "boolean",
                    True,
                    "always false",
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "status",
                    "PASS only when both-direction reinforcement/detailing, the reviewed span/depth comparison, and the concrete-only centred punching check pass.",
                    (
                        "PASS is bounded software evidence, not professional design approval.",
                        "Direct deflection, crack width, punching reinforcement, moment transfer, alternate topologies, and load-envelope generation are not represented.",
                    ),
                ),
            ),
            limitations=(
                "Only the equal-span square interior direct-design topology declared by the capability is supported.",
                "The caller supplies approved gravity actions, provided bars, review references, and the factored support reaction.",
                "Punching reinforcement is never designed; any concrete-only exceedance fails this route.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_symmetric_combined_footing_is456",
            element="combined_footing",
            fields=(
                _field(
                    "request",
                    "typed symmetric combined-footing request",
                    "SymmetricCombinedFootingDesignInput",
                    True,
                    "validated explicit input contract",
                ),
                _field(
                    "status",
                    "aggregate bearing, strength, detailing, and transfer disposition",
                    "enumeration",
                    True,
                    "PASS or FAIL",
                ),
                _field(
                    "request.footing.analysis.geometry",
                    "symmetric two-column rigid-footing geometry and eligibility",
                    "CombinedFootingGeometryInput",
                    True,
                    "explicit dimensions in mm and literal topology assertions",
                ),
                _field(
                    "request.footing.analysis.actions",
                    "approved service, factored, carrier, bearing, and cancellation bases",
                    "CombinedFootingActionInput",
                    True,
                    "finite positive kN and kN/m2 quantities with literal approval assertions",
                ),
                _field(
                    "request.footing.material",
                    "footing, column, and reinforcement material basis",
                    "CombinedFootingMaterialInput",
                    True,
                    "supported N/mm2 grades and uncoated deformed bars",
                ),
                _field(
                    "request.footing.reinforcement",
                    "caller-provided longitudinal and transverse bars and anchorage",
                    "CombinedFootingReinforcementInput",
                    True,
                    "supported diameters and finite positive mm quantities",
                ),
                _field(
                    "request.footing.transfer",
                    "approved supporting-area and dowel-transfer evidence",
                    "CombinedFootingTransferInput",
                    True,
                    "approved frustum basis, supported bars, counts, areas, and mm lengths",
                ),
                _field(
                    "strength.actions",
                    "service bearing, factored pressure, equilibrium, and section actions",
                    "CombinedFootingActionResult",
                    True,
                    "typed kN, kN m, kN/m2, mm, and residual results",
                ),
                _field(
                    "strength.top_longitudinal_flexure",
                    "governing inter-column top-steel disposition",
                    "CombinedFootingFlexureResult",
                    True,
                    "typed required/provided mm2, spacing, cover, and anchorage checks",
                ),
                _field(
                    "strength.longitudinal_one_way_shear",
                    "four concrete-only longitudinal one-way shear dispositions",
                    "CombinedFootingOneWayShearResult tuple",
                    True,
                    "typed demand, capacity, and utilization results",
                ),
                _field(
                    "strength.punching",
                    "two full-perimeter concrete-only punching dispositions",
                    "CombinedFootingPunchingResult tuple",
                    True,
                    "typed demand, capacity, and utilization results",
                ),
                _field(
                    "strength.load_transfer",
                    "two identical-column bearing and dowel-transfer dispositions",
                    "CombinedFootingLoadTransferResult tuple",
                    True,
                    "typed concrete bearing, required/provided steel, and development checks",
                ),
                _field(
                    "qualified_review_required",
                    "qualified review boundary",
                    "boolean",
                    True,
                    "always true",
                ),
                _field(
                    "complete_engineering_design_approved",
                    "complete engineering approval",
                    "boolean",
                    True,
                    "always false",
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "status",
                    "PASS only when service bearing and every represented flexure, detailing, concrete-only shear and punching, bearing, dowel, and anchorage comparison pass.",
                    (
                        "PASS is bounded software evidence, not professional design approval.",
                        "Soil capacity, settlement, pressure generation beyond the approved uniform model, shear or punching reinforcement design, and alternate foundation systems are not represented.",
                    ),
                ),
            ),
            limitations=(
                "Only the declared equal-load symmetric two-column rigid rectangular constant-depth footing is supported.",
                "The caller supplies approved soil, pressure, load, material, reinforcement, supporting-area, transfer, and review bases.",
                "Unequal or eccentric loading, alternate topology, nonlinear soil response, automatic sizing, strap, pile-cap, raft, and professional approval remain held.",
            ),
        ),
        IS456WorkflowContract(
            workflow="size_footing",
            element="isolated_footing",
            fields=(
                _field(
                    "P_service_kN", "service axial load", "kN", True, "finite positive"
                ),
                _field(
                    "q_safe_kPa",
                    "safe bearing pressure",
                    "kPa",
                    True,
                    "finite positive",
                ),
                _field("a_mm", "loaded-area dimension", "mm", True, _MM),
                _field("b_mm", "loaded-area dimension", "mm", True, _MM),
            ),
            statuses=(),
            limitations=("Settlement and lateral stability are excluded.",),
        ),
        IS456WorkflowContract(
            workflow="check_bearing_pressure",
            element="isolated_footing",
            fields=(
                _field("Pu_kN", "factored axial load", "kN", True, "finite positive"),
                _field(
                    "effective_supporting_area_A1_mm2",
                    "approved effective supporting area",
                    "mm2",
                    False,
                    "finite positive when supplied",
                ),
                _field(
                    "effective_supporting_area_is_approved",
                    "supporting-area review acknowledgement",
                    "boolean",
                    False,
                    _BOOLEAN,
                ),
                _field(
                    "is_safe",
                    "bearing-pressure check outcome",
                    "boolean",
                    True,
                    _BOOLEAN,
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "is_safe",
                    "The bounded bearing-pressure check passed.",
                    (
                        "It requires qualified review of the supporting-area basis and complete footing design.",
                    ),
                ),
            ),
            limitations=(
                "The check does not cover settlement, lateral stability, or other footing systems.",
            ),
        ),
        IS456WorkflowContract(
            workflow="footing_flexure",
            element="isolated_footing",
            fields=(
                _field(
                    "overall_thickness_mm", "overall footing thickness", "mm", True, _MM
                ),
                _field("d_mm", "effective footing depth", "mm", True, _MM),
                _field("Pu_kN", "factored axial load", "kN", True, "finite positive"),
                _field("fck", "concrete strength", "N/mm2", True, _N_PER_MM2),
            ),
            statuses=(),
            limitations=(
                "Overall thickness is intentionally distinct from effective depth.",
            ),
        ),
        IS456WorkflowContract(
            workflow="footing_one_way_shear",
            element="isolated_footing",
            fields=(
                _field("d_mm", "effective footing depth", "mm", True, _MM),
                _field(
                    "pt", "tension-steel percentage", "%", False, "finite non-negative"
                ),
                _field("is_safe", "one-way shear outcome", "boolean", True, _BOOLEAN),
            ),
            statuses=(
                IS456StatusContract(
                    "is_safe",
                    "The evaluated one-way shear check passed.",
                    ("Other footing checks remain separate.",),
                ),
            ),
            limitations=("Punching shear is a separate workflow.",),
        ),
        IS456WorkflowContract(
            workflow="footing_punching_shear",
            element="isolated_footing",
            fields=(
                _field("d_mm", "effective footing depth", "mm", True, _MM),
                _field("Pu_kN", "factored axial load", "kN", True, "finite positive"),
                _field("is_safe", "punching-shear outcome", "boolean", True, _BOOLEAN),
            ),
            statuses=(
                IS456StatusContract(
                    "is_safe",
                    "The evaluated punching-shear check passed.",
                    ("Flexure and one-way shear remain separate.",),
                ),
            ),
            limitations=("The workflow is limited to its isolated-footing geometry.",),
        ),
        IS456WorkflowContract(
            workflow="check_isolated_footing_load_transfer",
            element="isolated_footing",
            fields=(
                _field(
                    "dowel_count",
                    "provided dowel bar count",
                    "count",
                    True,
                    "positive integer",
                ),
                _field("dowel_diameter_mm", "provided dowel diameter", "mm", True, _MM),
                _field(
                    "available_dowel_development_length_into_footing_mm",
                    "available dowel development length",
                    "mm",
                    True,
                    _MM,
                ),
                _field(
                    "available_dowel_development_length_into_supported_member_mm",
                    "available dowel development length",
                    "mm",
                    True,
                    _MM,
                ),
                _field(
                    "is_safe",
                    "bounded load-transfer outcome",
                    "boolean",
                    True,
                    _BOOLEAN,
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "is_safe",
                    "The declared concentric load-transfer check passed.",
                    ("It does not approve a complete footing design.",),
                ),
            ),
            limitations=(
                "The effective supporting-area basis requires explicit qualified approval.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_one_way_slab_is456",
            element="solid_slab",
            fields=(
                _field("thickness_mm", "overall slab thickness", "mm", True, _MM),
                _field("d_mm", "effective slab depth", "mm", True, _MM),
                _field(
                    "factored_area_load_kn_per_m2",
                    "factored area load",
                    "kN/m2",
                    True,
                    "finite positive",
                ),
                _field(
                    "detailing.detailing_adequacy",
                    "bounded provided-bar detailing status",
                    "enumeration",
                    True,
                    "adequate or inadequate",
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "detailing.detailing_adequacy",
                    "The supplied bars satisfy bounded one-way detailing checks.",
                    ("Qualified review remains required.",),
                ),
            ),
            limitations=(
                "The route is a simply supported one-way slab strip and checks flexure plus supplied bars only.",
                "Use the complete route for reviewed span/depth serviceability and ordinary concrete shear; direct deflection, crack width and automatic shear reinforcement remain held.",
                "One caller-supplied factored UDL is consumed; load combinations, patterns, concentrated loads, openings and envelope generation are not performed.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_two_way_slab_is456",
            element="solid_slab",
            fields=(
                _field(
                    "alpha_x",
                    "externally supplied x-direction coefficient",
                    "dimensionless",
                    True,
                    "finite in (0, 1]",
                ),
                _field(
                    "alpha_y",
                    "externally supplied y-direction coefficient",
                    "dimensionless",
                    True,
                    "finite in (0, 1]",
                ),
                _field(
                    "coefficient_review_status",
                    "coefficient review state",
                    "enumeration",
                    True,
                    "review_required",
                    _SLAB_REVIEW_ALIAS,
                ),
                _field(
                    "qualified_acceptance_recorded",
                    "qualified acceptance provenance",
                    "boolean",
                    True,
                    _BOOLEAN,
                    _SLAB_ACCEPTANCE_ALIAS,
                ),
                _field(
                    "coefficient_correctness_verified_by_library",
                    "library coefficient-verification claim",
                    "boolean",
                    True,
                    "always false",
                    _SLAB_VERIFICATION_ALIAS,
                ),
                _field(
                    "complete_engineering_design_approved",
                    "complete engineering approval",
                    "boolean",
                    True,
                    "always false",
                ),
                _field(
                    "bounded_flexure_computation_supported",
                    "bounded computation support",
                    "boolean",
                    True,
                    "always true for this result",
                    _SLAB_SUPPORT_ALIAS,
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "status",
                    "externally accepted coefficient, flexure-only supported case",
                    ("It is not complete two-way slab design approval.",),
                ),
            ),
            limitations=(
                "This compatibility route is flexure-only; reinforcement detailing, span/depth serviceability and ordinary shear require a complete panel route.",
                "Direct deflection, crack width, automatic shear reinforcement, concentrated loads, openings and load-envelope generation remain held.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_complete_one_way_slab_is456",
            element="solid_slab",
            fields=(
                _field("d_mm", "effective slab depth", "mm", True, _MM),
                _field(
                    "reviewed_base_span_depth_limit",
                    "reviewed serviceability base limit",
                    "dimensionless",
                    True,
                    "finite positive",
                ),
                _field(
                    "shear.status",
                    "ordinary one-way shear disposition",
                    "enumeration",
                    True,
                    "explicit capacity state",
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "complete_engineering_design_approved",
                    "Always false for this software result.",
                    ("Qualified project review remains required.",),
                ),
            ),
            limitations=(
                "Only reviewed span/depth serviceability and ordinary concrete shear are evaluated.",
                "Direct deflection and crack width require separately validated slab-specific service actions, duration, reinforcement/geometry and service-stress inputs.",
                "Automatic slab shear reinforcement is not designed; increase depth or perform separate engineering when concrete capacity is exceeded.",
                "One caller-supplied factored UDL is checked; load combinations, patterns, concentrated loads, openings and envelope generation are not performed.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_continuous_one_way_slab_is456",
            element="solid_slab",
            fields=(
                _field(
                    "positive_moment_coefficient",
                    "reviewed external positive coefficient",
                    "dimensionless",
                    True,
                    "finite in (0, 1]",
                ),
                _field(
                    "negative_moment_coefficient",
                    "reviewed external negative coefficient",
                    "dimensionless",
                    True,
                    "finite in (0, 1]",
                ),
                _field(
                    "redistribution_applied",
                    "moment redistribution declaration",
                    "boolean",
                    True,
                    "must be false",
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "flexure.coefficient_correctness_verified_by_library",
                    "Always false for external coefficients.",
                    ("The source and qualified acceptance references remain visible.",),
                ),
            ),
            limitations=(
                "Requires at least three spans, no more than 15 percent span variation, a uniform section, substantially uniform load, and no redistribution.",
                "Only reviewed span/depth serviceability and ordinary concrete shear are evaluated; direct deflection, crack width and automatic slab shear reinforcement remain held.",
                "One declared coefficient-method action basis is checked; load-combination/pattern generation, concentrated loads, openings and envelope analysis are not performed.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_continuous_one_way_slab_builtin_is456",
            element="solid_slab",
            fields=(
                _field(
                    "positive_location",
                    "one-way positive-action location",
                    "enumeration",
                    True,
                    "supported Table 12 action location",
                ),
                _field(
                    "shear_location",
                    "one-way shear-action location",
                    "enumeration",
                    True,
                    "supported Table 13 action location",
                ),
                _field(
                    "flexure.coefficient_correctness_verified_by_library",
                    "library coefficient-verification claim",
                    "boolean",
                    True,
                    "always true for normalized built-in records",
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "flexure.coefficient_correctness_verified_by_library",
                    "True when the normalized built-in coefficient record resolved successfully.",
                    (
                        "The coefficient provenance remains visible and qualified project review remains required.",
                    ),
                ),
            ),
            limitations=(
                "Requires at least three spans, no more than 15 percent span variation, a uniform section, substantially uniform load, and no redistribution.",
                "Built-in action-location coefficients do not generate project load combinations or an envelope; the caller supplies the governing factored load components.",
                "Only reviewed span/depth serviceability and ordinary concrete shear are evaluated; direct deflection, crack width and automatic slab shear reinforcement remain held.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_two_way_slab_panel_is456",
            element="solid_slab",
            fields=(
                _field(
                    "support_topology_kind",
                    "physical edge topology identity",
                    "enumeration",
                    True,
                    "must match declared physical edges",
                ),
                _field(
                    "alpha_x_positive",
                    "reviewed external x positive coefficient",
                    "dimensionless",
                    True,
                    "finite in (0, 1]",
                ),
                _field(
                    "alpha_y_positive",
                    "reviewed external y positive coefficient",
                    "dimensionless",
                    True,
                    "finite in (0, 1]",
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "coefficient_correctness_verified_by_library",
                    "Always false for external coefficients.",
                    ("No protected table lookup or interpolation is performed.",),
                ),
            ),
            limitations=(
                "Flat slabs and column-supported punching are a separate held extension.",
                "Only reviewed span/depth serviceability and ordinary concrete shear are evaluated; direct deflection, crack width and automatic slab shear reinforcement remain held.",
                "One caller-supplied factored UDL and coefficient basis are checked; concentrated loads, openings and load-envelope generation are not performed.",
            ),
        ),
        IS456WorkflowContract(
            workflow="design_two_way_slab_panel_builtin_is456",
            element="solid_slab",
            fields=(
                _field(
                    "x_min_edge",
                    "physical x-min edge continuity",
                    "enumeration",
                    True,
                    "continuous or discontinuous",
                ),
                _field(
                    "corner_lift_condition",
                    "physical corner lift condition",
                    "enumeration",
                    True,
                    "restrained or free_to_lift",
                ),
                _field(
                    "panel.coefficient_correctness_verified_by_library",
                    "library coefficient-verification claim",
                    "boolean",
                    True,
                    "always true for normalized built-in records",
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "panel.coefficient_correctness_verified_by_library",
                    "True when exact lookup or bounded interpolation resolved successfully.",
                    (
                        "The physical support topology and coefficient provenance remain visible.",
                    ),
                ),
            ),
            limitations=(
                "Flat slabs and column-supported punching are a separate held extension.",
                "Built-in panel coefficients do not generate project load combinations or an envelope; one caller-supplied factored UDL is checked.",
                "Direct deflection, crack width, automatic slab shear reinforcement, concentrated loads and openings remain held.",
            ),
        ),
    ),
    adapters=(
        IS456AdapterContract(
            adapter="batch_design_sse",
            fields=(
                _field(
                    "design_succeeded",
                    "calculation completion",
                    "boolean",
                    True,
                    _BOOLEAN,
                ),
                _field(
                    "is_safe",
                    "combined engineering check outcome",
                    "boolean",
                    True,
                    _BOOLEAN,
                ),
                _field(
                    "status", "engineering status", "enumeration", True, "PASS or FAIL"
                ),
                _field(
                    "tau_v",
                    "nominal shear stress",
                    "N/mm2",
                    True,
                    "finite non-negative",
                ),
                _field(
                    "tau_c",
                    "concrete shear strength",
                    "N/mm2",
                    True,
                    "finite non-negative",
                ),
                _field(
                    "tau_c_max",
                    "maximum shear stress",
                    "N/mm2",
                    True,
                    "finite non-negative",
                ),
                _field(
                    "stirrup_spacing",
                    "stirrup spacing",
                    "mm",
                    True,
                    "finite non-negative",
                ),
                _field(
                    "utilization_ratio",
                    "governing utilization",
                    "ratio",
                    True,
                    "finite non-negative",
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "status",
                    "PASS only when the server result is safe; calculation completion alone is not PASS.",
                    ("Unsafe and exception outcomes are FAIL.",),
                ),
            ),
            limitations=(
                "Legacy tv/tc transport names are not canonical batch fields.",
            ),
        ),
        IS456AdapterContract(
            adapter="report_context",
            fields=(
                _field(
                    "is_ok",
                    "normalized report safety outcome",
                    "boolean",
                    True,
                    _BOOLEAN,
                    _REPORT_IS_SAFE_ALIAS,
                ),
            ),
            statuses=(
                IS456StatusContract(
                    "is_ok",
                    "Canonical normalized report outcome, derived fail-closed from evaluated sections.",
                    (
                        "A legacy is_safe input is accepted only at the adapter boundary.",
                    ),
                ),
            ),
            limitations=("Missing section status renders NOT EVALUATED, never PASS.",),
        ),
        IS456AdapterContract(
            adapter="fastapi_library_core_requests",
            fields=(
                _field(
                    "dowel_count",
                    "provided dowel bar count",
                    "count",
                    True,
                    "positive strict integer",
                ),
                _field("dowel_diameter_mm", "provided dowel diameter", "mm", True, _MM),
                _field(
                    "thickness_mm", "overall one-way slab thickness", "mm", True, _MM
                ),
            ),
            statuses=(),
            limitations=(
                "Footing overall_thickness_mm belongs to footing_flexure; it is not a FastAPI load-transfer request field.",
            ),
        ),
    ),
)


def get_supported_is456_capabilities() -> tuple[IS456Capability, ...]:
    """Return the immutable supported-case registry for this library version."""
    return _CAPABILITIES


def get_supported_is456_semantic_contract() -> IS456SemanticContract:
    """Return immutable units, aliases, statuses, and limits for supported routes."""
    return _SEMANTIC_CONTRACT


def _json_ready(value: Any) -> Any:
    """Normalize immutable tuple-based records to JSON-native containers."""
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def get_supported_is456_capability_document() -> dict[str, Any]:
    """Return the canonical JSON-safe capability and semantic contract.

    The immutable dataclasses above remain the structural source of truth. This
    document is the transport contract used by Python callers, the CLI, and
    FastAPI so those public discovery surfaces cannot silently diverge.
    """
    capabilities = []
    for capability in _CAPABILITIES:
        serialized = _json_ready(asdict(capability))
        serialized["capability_id"] = capability.element
        capabilities.append(serialized)

    return {
        "schema_version": CAPABILITY_SCHEMA_VERSION,
        "code_edition": IS456_CODE_EDITION,
        "capabilities": capabilities,
        "semantic_contract": _json_ready(asdict(_SEMANTIC_CONTRACT)),
    }
