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
        public_workflows=("design_beam_is456", "check_beam_is456", "detail_beam_is456"),
        supported_case=(
            "Ordinary solid rectangular beam primary design for flexure and shear, "
            "with optional IS 456 torsion within fck 15-40 N/mm2 and fy <= 500 "
            "N/mm2, plus maintained Level-A deflection and crack-width checks when "
            "their explicit inputs are supplied."
        ),
        held_cases=(
            "Flanged, hollow/box, deep, prestressed, or axially loaded torsion cases are excluded.",
            "Compatibility-versus-equilibrium torsion redistribution decisions are excluded.",
            "Beam check, detailing, batch, import, and other automation surfaces that do not accept Tu and serviceability inputs remain outside the combined route.",
            "Serviceability is held unless span, support condition, crack geometry, and service strain or stress are explicitly supplied.",
        ),
        qualified_review_required=True,
    ),
    IS456Capability(
        element="column",
        public_workflows=("design_column_is456", "design_long_column_is456"),
        supported_case="Rectangular columns with the declared symmetric/two-face reinforcement assumptions.",
        held_cases=(
            "Circular, asymmetric and arbitrary multilayer layouts are excluded.",
        ),
        qualified_review_required=True,
    ),
    IS456Capability(
        element="isolated_footing",
        public_workflows=(
            "size_footing",
            "footing_flexure",
            "footing_one_way_shear",
            "footing_punching_shear",
            "check_bearing_pressure",
            "check_isolated_footing_load_transfer",
        ),
        supported_case="Square/rectangular isolated footing checks, including bounded bearing pressure and concentric dowel transfer.",
        held_cases=(
            "Bearing-pressure results remain bounded checks requiring qualified review of the approved supporting-area basis and the complete footing design.",
            "Combined, strap, raft, pile-cap, settlement and lateral stability design are excluded.",
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
            "Direct deflection, crack width, concentrated loads, openings, irregular panels, load-envelope analysis and automatic slab shear reinforcement are excluded.",
            "Flat/drop/ribbed slabs, column strips, column-supported punching and FEM require a separately approved extension.",
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
                "Only declared rectangular reinforcement assumptions are supported.",
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
                "The public route remains bounded to its declared section assumptions.",
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
            limitations=("The route is a simply supported one-way slab strip.",),
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
                "Reinforcement detailing, serviceability, shear/punching, load combinations/patterning, and other panel cases remain incomplete.",
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
                "Direct deflection and automatic shear reinforcement are not implemented.",
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
