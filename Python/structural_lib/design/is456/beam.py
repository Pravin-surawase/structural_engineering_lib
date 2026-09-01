"""Small public facade for the canonical rectangular-beam workflow."""

from __future__ import annotations

from typing import Any, Literal

from structural_lib.core.errors import InputContractError, InputIssueV1
from structural_lib.services.canonical_beam import (
    BeamBBSResultV1,
    BeamDesignAndDetailResultV1,
    BeamDesignResultV1,
    BeamDetailingResultV1,
    check,
    design,
    design_and_detail,
    detail,
    generate_bbs,
)
from structural_lib.services.contracts.beam import (
    BEAM_FIELD_CONTRACTS,
    BeamActionsV1,
    BeamCalculationBasisV1,
    BeamDesignInputV1,
    BeamDetailingOptionsV1,
    BeamServiceabilityV1,
    CentroidCoverDepthRequestV1,
    DetailingStandard,
    EffectiveDepthBasisRequestV1,
    IS456MaterialsV1,
    IS456ReinforcementMaterialsV1,
    MemberIdentityV1,
    RectangularBeamSectionV1,
)
from structural_lib.services.contracts.beam_serviceability import (
    BeamAnnexFCrackCheckV1,
    BeamServiceabilityBasisV1,
    BeamServiceabilityChecksV1,
    BeamSpanDepthCheckV1,
)
from structural_lib.services.contracts.beam_supplied_check import (
    BEAM_SUPPLIED_CHECK_SCHEMA_VERSION,
    BeamBarLayersV2,
    BeamReinforcementSelectionV2,
    BeamSuppliedCheckActionsV2,
    BeamSuppliedCheckRequestV2,
    BeamSuppliedCheckSectionV2,
    BeamSuppliedReinforcementV2,
    BeamSupportBasisV2,
)
from structural_lib.services.contracts.common import model_validate_or_error
from structural_lib.services.supplied_beam_check import (
    BEAM_SUPPLIED_CHECK_RESULT_SCHEMA_VERSION,
    BeamSuppliedCheckResultV2,
    BeamSuppliedShearEvaluationV2,
    check_supplied_beam_v2,
)

__all__ = [
    "BeamActionsV1",
    "BEAM_FIELD_CONTRACTS",
    "BeamBBSResultV1",
    "BeamCalculationBasisV1",
    "BeamDesignAndDetailResultV1",
    "BeamDesignInputV1",
    "BeamDesignResultV1",
    "BeamDetailingOptionsV1",
    "BeamDetailingResultV1",
    "BeamServiceabilityV1",
    "BeamServiceabilityChecksV1",
    "BeamServiceabilityBasisV1",
    "BeamSpanDepthCheckV1",
    "BeamAnnexFCrackCheckV1",
    "BEAM_SUPPLIED_CHECK_SCHEMA_VERSION",
    "BEAM_SUPPLIED_CHECK_RESULT_SCHEMA_VERSION",
    "BeamBarLayersV2",
    "BeamReinforcementSelectionV2",
    "BeamSuppliedCheckActionsV2",
    "BeamSuppliedCheckRequestV2",
    "BeamSuppliedCheckResultV2",
    "BeamSuppliedCheckSectionV2",
    "BeamSuppliedReinforcementV2",
    "BeamSuppliedShearEvaluationV2",
    "BeamSupportBasisV2",
    "DetailingStandard",
    "EffectiveDepthBasisRequestV1",
    "CentroidCoverDepthRequestV1",
    "IS456MaterialsV1",
    "IS456ReinforcementMaterialsV1",
    "InputContractError",
    "InputIssueV1",
    "MemberIdentityV1",
    "RectangularBeamSectionV1",
    "bbs",
    "check",
    "check_supplied",
    "design",
    "design_and_detail",
    "detail",
    "input",
    "load",
    "load_supplied_check",
]


def input(  # noqa: A001 - frozen public facade spelling
    *,
    member_id: str,
    story: str,
    case_id: str,
    span_mm: float,
    b_mm: float,
    D_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    fy_transverse_nmm2: float | None = None,
    mu_knm: float,
    vu_kn: float,
    d_dash_mm: float,
    asv_mm2: float,
    d_mm: float | None = None,
    effective_depth_basis: (
        EffectiveDepthBasisRequestV1 | CentroidCoverDepthRequestV1 | None
    ) = None,
    tu_knm: float = 0.0,
    primary_tension_face: Literal["TOP", "BOTTOM"] | None = None,
    pt_percent: float | None = None,
    ast_mm2_for_shear: float | None = None,
    detailing: BeamDetailingOptionsV1 | None = None,
    serviceability: BeamServiceabilityV1 | BeamServiceabilityChecksV1 | None = None,
    source_provenance: str | None = None,
) -> BeamDesignInputV1:
    """Build one strict rectangular-beam design request.

    Parameters
    ----------
    member_id, story, case_id : str
        Caller-owned member and action-case identity.
    span_mm, b_mm, D_mm : float
        Span, section width, and overall depth in millimetres.
    fck_nmm2, fy_nmm2, fy_transverse_nmm2 : float
        Concrete, longitudinal-steel, and optional transverse-steel strengths.
    mu_knm, vu_kn, tu_knm : float
        Caller-supplied factored bending, shear, and torsion actions.
    d_dash_mm, asv_mm2 : float
        Compression-steel depth and transverse-reinforcement area basis.
    d_mm : float, optional
        Explicit effective depth; mutually exclusive with ``effective_depth_basis``.
    effective_depth_basis : EffectiveDepthBasisRequestV1 or CentroidCoverDepthRequestV1, optional
        Complete typed basis used by the shared effective-depth owner.
    primary_tension_face : {"TOP", "BOTTOM"}, optional
        Physical tension face required for signed/torsional workflows.
    pt_percent, ast_mm2_for_shear : float, optional
        Explicit shear-design longitudinal-steel basis.
    detailing : BeamDetailingOptionsV1, optional
        Complete caller-selected detailing choices.
    serviceability : BeamServiceabilityV1 or BeamServiceabilityChecksV1, optional
        Versioned bounded serviceability evidence.
    source_provenance : str, optional
        Caller-owned source reference for the request.

    Returns
    -------
    BeamDesignInputV1
        Immutable, strictly validated canonical request.

    Raises
    ------
    InputContractError
        If a field or cross-field relationship violates the public contract.

    Examples
    --------
    >>> from structural_lib.design.is456 import beam
    >>> request = beam.input(
    ...     member_id="B1", story="L1", case_id="ULS-1", span_mm=5000,
    ...     b_mm=300, D_mm=500, d_mm=442, fck_nmm2=25, fy_nmm2=500,
    ...     mu_knm=100, vu_kn=60, d_dash_mm=58, asv_mm2=100.53,
    ...     source_provenance="reviewed schedule B1",
    ... )
    >>> request.schema_version
    'beam-design-input/v1'

    Limitations
    -----------
    This builder does not generate loads, infer project criteria, or approve a
    section. Complex evidence remains in the named typed groups.

    Provenance
    ----------
    Field validation is owned by ``BeamDesignInputV1`` and is shared with the
    canonical CLI and REST V2 journey.
    """

    return model_validate_or_error(
        BeamDesignInputV1,
        {
            "identity": {
                "member_id": member_id,
                "story": story,
                "case_id": case_id,
            },
            "section": {
                "span_mm": span_mm,
                "b_mm": b_mm,
                "D_mm": D_mm,
                "d_mm": d_mm,
                "effective_depth_basis": effective_depth_basis,
            },
            "materials": {
                "fck_nmm2": fck_nmm2,
                "fy_nmm2": fy_nmm2,
                **(
                    {"fy_transverse_nmm2": fy_transverse_nmm2}
                    if fy_transverse_nmm2 is not None
                    else {}
                ),
            },
            "actions": {
                "mu_knm": mu_knm,
                "vu_kn": vu_kn,
                "tu_knm": tu_knm,
                **(
                    {"primary_tension_face": primary_tension_face}
                    if primary_tension_face is not None
                    else {}
                ),
            },
            "calculation_basis": {
                "d_dash_mm": d_dash_mm,
                "asv_mm2": asv_mm2,
                "pt_percent": pt_percent,
                "ast_mm2_for_shear": ast_mm2_for_shear,
            },
            "detailing": detailing,
            "serviceability": serviceability,
            "source_provenance": source_provenance,
        },
    )


def load(value: Any) -> BeamDesignInputV1:
    """Parse nested Python or decoded JSON into a canonical beam request.

    Parameters
    ----------
    value : Any
        Mapping-like decoded data for ``beam-design-input/v1``.

    Returns
    -------
    BeamDesignInputV1
        Strict typed request with no coercion of numeric strings or booleans.

    Raises
    ------
    InputContractError
        If input type, fields, values, identity, or cross-field basis is invalid.

    Examples
    --------
    >>> from structural_lib.design.is456 import beam
    >>> request = beam.load({
    ...     "identity": {"member_id": "B1", "story": "L1", "case_id": "ULS"},
    ...     "section": {"span_mm": 5000, "b_mm": 300, "D_mm": 500, "d_mm": 442},
    ...     "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
    ...     "actions": {"mu_knm": 100, "vu_kn": 60, "tu_knm": 0},
    ...     "calculation_basis": {"d_dash_mm": 58, "asv_mm2": 100.53},
    ... })
    >>> request.identity.member_id
    'B1'

    Limitations
    -----------
    Parsing validates caller data only; it does not create actions, geometry,
    reinforcement choices, or qualified-review evidence.

    Provenance
    ----------
    Validation errors are translated by the shared library-owned
    ``model_validate_or_error`` boundary.
    """

    return model_validate_or_error(BeamDesignInputV1, value)


def load_supplied_check(value: Any) -> BeamSuppliedCheckRequestV2:
    """Parse the exact supplied-reinforcement V2 request.

    Parameters
    ----------
    value : Any
        Nested decoded data conforming to ``beam-supplied-check/v2``.

    Returns
    -------
    BeamSuppliedCheckRequestV2
        Strict request that preserves identity, depth, bars, stirrups, and sources.

    Raises
    ------
    InputContractError
        If the request is partial, flat/legacy, coercive, non-finite, or inconsistent.

    Examples
    --------
    >>> from structural_lib.design.is456 import beam
    >>> schema = beam.BeamSuppliedCheckRequestV2.model_json_schema()
    >>> schema["additionalProperties"]
    False

    Limitations
    -----------
    The former flat area-only payload is rejected because it cannot reconstruct
    exact layers, transverse reinforcement, or source evidence.

    Provenance
    ----------
    ``BeamSuppliedCheckRequestV2`` is the shared Python, REST, and WebSocket
    intake owner; the full executable request is in the supplied-check cookbook.
    """

    return model_validate_or_error(BeamSuppliedCheckRequestV2, value)


def check_supplied(
    request: BeamSuppliedCheckRequestV2,
) -> BeamSuppliedCheckResultV2:
    """Evaluate exact supplied longitudinal bars and stirrups for one case.

    Parameters
    ----------
    request : BeamSuppliedCheckRequestV2
        Fully validated section, action, reinforcement, selection, and source basis.

    Returns
    -------
    BeamSuppliedCheckResultV2
        Correlated ``PASS``, ``FAIL``, or ``HOLD`` result and orthogonal envelope.

    Raises
    ------
    InputContractError
        If a non-V2 request reaches the facade boundary.
    CalculationError
        If the maintained calculation owner cannot complete the declared check.

    Examples
    --------
    >>> from structural_lib.design.is456 import beam
    >>> callable(beam.check_supplied)
    True

    Limitations
    -----------
    This rectangular-beam slice does not infer support widths or professional
    acceptance. Missing support evidence returns ``HOLD``.

    Provenance
    ----------
    Delegates without formula duplication to ``check_supplied_beam_v2``; the
    complete valid, invalid, ``FAIL``, and ``HOLD`` vectors are executable in
    the supplied-check cookbook.
    """

    if not isinstance(request, BeamSuppliedCheckRequestV2):
        raise InputContractError(
            (
                InputIssueV1(
                    code="INPUT_TYPE_INVALID",
                    path="request",
                    message="request must be BeamSuppliedCheckRequestV2",
                    received=f"<{type(request).__name__}>",
                ),
            )
        )
    return check_supplied_beam_v2(request)


def bbs(
    result: (
        BeamDesignAndDetailResultV1
        | BeamDetailingResultV1
        | list[BeamDetailingResultV1]
    ),
) -> BeamBBSResultV1:
    """Generate a canonical BBS from exact accepted detailing results.

    Parameters
    ----------
    result : BeamDesignAndDetailResultV1, BeamDetailingResultV1, or list
        One accepted result, or a non-empty list of accepted detailing results.

    Returns
    -------
    BeamBBSResultV1
        All-or-nothing finite bar-bending schedule with source result identities.

    Raises
    ------
    InputContractError
        If the input type, collection, or engineering/detailing status is unaccepted.

    Examples
    --------
    >>> from structural_lib.design.is456 import beam
    >>> callable(beam.bbs)
    True

    Limitations
    -----------
    BBS generation consumes accepted canonical detailing; it does not revise
    bars, invent a span, or convert a failed/held result into an artifact.

    Provenance
    ----------
    The facade delegates to ``generate_bbs`` and preserves the source result
    schema versions in the returned schedule.
    """

    return generate_bbs(result)
