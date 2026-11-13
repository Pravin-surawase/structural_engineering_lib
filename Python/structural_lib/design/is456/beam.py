"""Small public facade for the canonical rectangular-beam workflow."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from structural_lib.core.errors import InputContractError, InputIssueV1
from structural_lib.services.beam_continuous import (
    BeamCantileverCheckResultV1,
    BeamContinuousCheckResultV1,
    BeamSectionCheckResultV1,
    check_cantilever_beam,
    check_continuous_beam,
    check_section_beam,
    render_continuous_beam_html,
    render_station_beam_html,
)
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
from structural_lib.services.contracts.beam_continuous import (
    BeamCantileverCheckRequestV1,
    BeamContinuousActionV1,
    BeamContinuousBarV1,
    BeamContinuousCheckRequestV1,
    BeamContinuousCombinationV1,
    BeamContinuousStationV1,
    BeamContinuousStraightBarsV1,
    BeamContinuousSupportV1,
    BeamSectionBarV1,
    BeamSectionCheckRequestV1,
    BeamSectionFlangeV1,
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
from structural_lib.services.contracts.common import (
    model_validate_json_or_error,
    model_validate_or_error,
)
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
    "BeamCantileverCheckRequestV1",
    "BeamCantileverCheckResultV1",
    "BeamContinuousActionV1",
    "BeamContinuousBarV1",
    "BeamContinuousCheckRequestV1",
    "BeamContinuousCheckResultV1",
    "BeamContinuousCombinationV1",
    "BeamContinuousStationV1",
    "BeamContinuousStraightBarsV1",
    "BeamContinuousSupportV1",
    "BeamDesignAndDetailResultV1",
    "BeamSectionBarV1",
    "BeamSectionCheckRequestV1",
    "BeamSectionCheckResultV1",
    "BeamSectionFlangeV1",
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
    "check_cantilever",
    "check_continuous",
    "check_section",
    "check_supplied",
    "design",
    "design_and_detail",
    "detail",
    "input",
    "load",
    "load_json",
    "load_cantilever",
    "load_continuous",
    "load_section",
    "render_cantilever_html",
    "render_continuous_html",
    "render_section_html",
    "load_supplied_check",
    "load_supplied_check_json",
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
        Longitudinal steel for the concrete shear-strength lookup: supply its
        percentage or area in mm². With neither, use flexure-required steel.
        If both are supplied, they must agree with ``pt = 100 * Ast / (b * d)``
        (relative tolerance 1e-9, absolute area tolerance 1e-6 mm²). Generated
        detailing must supply at least this area; these inputs do not select bars.
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


def load(value: Mapping[str, object] | BeamDesignInputV1) -> BeamDesignInputV1:
    """Parse nested Python or decoded JSON into a canonical beam request.

    Parameters
    ----------
    value : Mapping[str, object] or BeamDesignInputV1
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


def load_json(value: str | bytes) -> BeamDesignInputV1:
    """Load a validated request directly from JSON text or UTF-8 bytes.

    Parameters
    ----------
    value : str or bytes
        Serialized BeamDesignInputV1 fields, using the units named by the request.
        UTF-8 byte-order marks are accepted; values are not silently coerced.

    Returns
    -------
    BeamDesignInputV1
        The same immutable request produced by ``load`` for a mapping.

    Raises
    ------
    InputContractError
        Malformed JSON, duplicate fields, non-finite numbers, invalid fields,
        or unsupported scope. ``error.issues`` supplies stable codes and paths.

    Examples
    --------
    Read a saved request with ``load_json(Path("request.json").read_bytes())``.
    A typed request round-trips with ``load_json(request.model_dump_json())``.
    See the family facade cookbook for complete valid and rejected requests.

    Limitations
    -----------
    Loading validates intake; it does not calculate or approve a design.
    Engineering assumptions and review requirements belong to the operation.

    Provenance
    ----------
    The shared JSON decoder preserves one value per field; the canonical
    request model owns field, unit, and supported-scope validation.
    """
    return model_validate_json_or_error(BeamDesignInputV1, value)


def load_supplied_check(
    value: Mapping[str, object] | BeamSuppliedCheckRequestV2,
) -> BeamSuppliedCheckRequestV2:
    """Parse the exact supplied-reinforcement V2 request.

    Parameters
    ----------
    value : Mapping[str, object] or BeamSuppliedCheckRequestV2
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


def load_supplied_check_json(value: str | bytes) -> BeamSuppliedCheckRequestV2:
    """Load a validated request directly from JSON text or UTF-8 bytes.

    Parameters
    ----------
    value : str or bytes
        Serialized BeamSuppliedCheckRequestV2 fields, using the units named by the request.
        UTF-8 byte-order marks are accepted; values are not silently coerced.

    Returns
    -------
    BeamSuppliedCheckRequestV2
        The same immutable request produced by ``load_supplied_check`` for a mapping.

    Raises
    ------
    InputContractError
        Malformed JSON, duplicate fields, non-finite numbers, invalid fields,
        or unsupported scope. ``error.issues`` supplies stable codes and paths.

    Examples
    --------
    Read a saved request with ``load_supplied_check_json(Path("request.json").read_bytes())``.
    A typed request round-trips with ``load_supplied_check_json(request.model_dump_json())``.
    See the family facade cookbook for complete valid and rejected requests.

    Limitations
    -----------
    Loading validates intake; it does not calculate or approve a design.
    Engineering assumptions and review requirements belong to the operation.

    Provenance
    ----------
    The shared JSON decoder preserves one value per field; the canonical
    request model owns field, unit, and supported-scope validation.
    """
    return model_validate_json_or_error(BeamSuppliedCheckRequestV2, value)


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


def load_continuous(
    value: Mapping[str, object] | str | bytes | BeamContinuousCheckRequestV1,
) -> BeamContinuousCheckRequestV1:
    """Parse a strict supplied two-span beam request.

    Parameters
    ----------
    value : Mapping, JSON str or bytes, or BeamContinuousCheckRequestV1
        Physical supports, bar positions and revision-bound station actions.

    Returns
    -------
    BeamContinuousCheckRequestV1
        The immutable request to pass to :func:`check_continuous`.

    Raises
    ------
    InputContractError
        Duplicate rows, inconsistent topology or other invalid intake.

    Examples
    --------
    >>> callable(load_continuous)
    True

    Limitations
    -----------
    Accepts already normalized mm, kN and kN·m. The worked example shows
    the complete request and how to run PASS, FAIL and HOLD cases.

    Provenance
    ----------
    Uses the strict IS 456 continuous-beam request model and canonical issues.
    """
    if isinstance(value, BeamContinuousCheckRequestV1):
        return value
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(BeamContinuousCheckRequestV1, value)
    return model_validate_or_error(BeamContinuousCheckRequestV1, value)


def check_continuous(
    request: BeamContinuousCheckRequestV1,
) -> BeamContinuousCheckResultV1:
    """Check signed flexure, shear and straight anchorage on a two-span beam.

    Parameters
    ----------
    request : BeamContinuousCheckRequestV1
        Two spans of a prismatic rectangular beam, both physical bar faces,
        three supports and concurrent actions at the declared stations.

    Returns
    -------
    BeamContinuousCheckResultV1
        Supplied ultimate disposition, exact source rows, governing checks
        and separately held service evidence.

    Raises
    ------
    TypeError
        The input is not a validated continuous-beam request.

    Examples
    --------
    >>> callable(check_continuous)
    True

    Limitations
    -----------
    The check consumes already supplied actions. It holds stale, incomplete
    or unsupported evidence. Fabrication, lateral stability and service
    deflection or cracking require separate checks.

    Provenance
    ----------
    Composes the maintained IS 456 physical flexure, shear, geometry and
    anchorage checks. The result records their identities and the input hash.
    """
    return check_continuous_beam(request)


def render_continuous_html(result: BeamContinuousCheckResultV1) -> str:
    """Render the checked rows, governing cases and limits in a review report.

    Parameters
    ----------
    result : BeamContinuousCheckResultV1
        A result from :func:`check_continuous`.

    Returns
    -------
    str
        Self-contained UTF-8 HTML.

    Raises
    ------
    TypeError
        The input is not a continuous-beam result.

    Examples
    --------
    >>> callable(render_continuous_html)
    True

    Limitations
    -----------
    The report preserves the bounded disposition and qualified-review status.

    Provenance
    ----------
    Reads the exact result and input identity without recalculating any row.
    """
    if not isinstance(result, BeamContinuousCheckResultV1):
        raise TypeError("result must be BeamContinuousCheckResultV1")
    return render_continuous_beam_html(result)


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


def load_cantilever(
    value: Mapping[str, object] | str | bytes | BeamCantileverCheckRequestV1,
) -> BeamCantileverCheckRequestV1:
    """Parse a strict supplied-action cantilever request.

    Parameters
    ----------
    value : Mapping, JSON str or bytes, or BeamCantileverCheckRequestV1
        Physical section, fixed-support geometry and revision-bound actions.

    Returns
    -------
    BeamCantileverCheckRequestV1
        A validated request for :func:`check_cantilever`.

    Raises
    ------
    InputContractError
        The payload violates the request contract.

    Examples
    --------
    >>> callable(load_cantilever)
    True

    Limitations
    -----------
    Coordinates are in mm from the fixed face toward the free end. Supply
    actions in kN and kN·m, including both sides of each discontinuity.

    Provenance
    ----------
    Uses the strict IS 456 cantilever request model and canonical input issues.
    """
    if isinstance(value, BeamCantileverCheckRequestV1):
        return value
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(BeamCantileverCheckRequestV1, value)
    return model_validate_or_error(BeamCantileverCheckRequestV1, value)


def check_cantilever(
    request: BeamCantileverCheckRequestV1,
) -> BeamCantileverCheckResultV1:
    """Check signed flexure, shear and straight fixed-face anchorage.

    Parameters
    ----------
    request : BeamCantileverCheckRequestV1
        Validated section, bars and supplied station actions.

    Returns
    -------
    BeamCantileverCheckResultV1
        Checked rows, governing row IDs and revision-bound dispositions.

    Raises
    ------
    TypeError
        The request is not a validated cantilever request.

    Examples
    --------
    >>> callable(check_cantilever)
    True

    Limitations
    -----------
    Ordinary prismatic rectangular section, one bar layer per face and a
    zero-action free end. Serviceability and fabrication need separate checks.

    Provenance
    ----------
    Composes the maintained IS 456 section, shear and direct anchorage checks.
    """
    return check_cantilever_beam(request)


def render_cantilever_html(result: BeamCantileverCheckResultV1) -> str:
    """Render the checked cantilever result and its input identity.

    Parameters
    ----------
    result : BeamCantileverCheckResultV1
        A result from :func:`check_cantilever`.

    Returns
    -------
    str
        Standalone HTML retaining station sides and result dispositions.

    Raises
    ------
    TypeError
        The result is not a cantilever check result.

    Examples
    --------
    >>> callable(render_cantilever_html)
    True

    Limitations
    -----------
    Renders the supplied result without rechecking or creating a schedule.

    Provenance
    ----------
    Uses the same result and analysis revision as the JSON projection.
    """
    if not isinstance(result, BeamCantileverCheckResultV1):
        raise TypeError("result must be BeamCantileverCheckResultV1")
    return render_station_beam_html(result)


def load_section(
    value: Mapping[str, object] | str | bytes | BeamSectionCheckRequestV1,
) -> BeamSectionCheckRequestV1:
    """Parse a strict signed beam-section request.

    Parameters
    ----------
    value : Mapping, JSON str or bytes, or BeamSectionCheckRequestV1
        One physical section with actual bar layers and supplied action rows.

    Returns
    -------
    BeamSectionCheckRequestV1
        Validated section geometry and revision-bound actions.

    Raises
    ------
    InputContractError
        Section topology, reinforcement or action inventory is inconsistent.

    Examples
    --------
    >>> callable(load_section)
    True

    Limitations
    -----------
    Bars use web-local x and top-down y in mm. The optional monolithic
    flange has one overhang for an L or two for a T.

    Provenance
    ----------
    Uses the strict beam-section request model and canonical input issues.
    """
    if isinstance(value, BeamSectionCheckRequestV1):
        return value
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(BeamSectionCheckRequestV1, value)
    return model_validate_or_error(BeamSectionCheckRequestV1, value)


def check_section(request: BeamSectionCheckRequestV1) -> BeamSectionCheckResultV1:
    """Check actual reinforcement at a signed rectangular, T or L section.

    Parameters
    ----------
    request : BeamSectionCheckRequestV1
        Validated section and concurrent actions at one physical station.

    Returns
    -------
    BeamSectionCheckResultV1
        Section resistance, bar strains and governing action rows.

    Raises
    ------
    TypeError
        The request is not a validated section request.

    Examples
    --------
    >>> callable(check_section)
    True

    Limitations
    -----------
    Flanges contribute in sagging only. Shear uses the web width.
    Anchorage, fabrication and serviceability need separate checks.

    Provenance
    ----------
    Composes the maintained IS 456 effective width, flexure and shear checks.
    """
    return check_section_beam(request)


def render_section_html(result: BeamSectionCheckResultV1) -> str:
    """Render a signed section result without recalculation.

    Parameters
    ----------
    result : BeamSectionCheckResultV1
        A result from :func:`check_section`.

    Returns
    -------
    str
        HTML with the checked actions, bars, layers and input identity.

    Raises
    ------
    TypeError
        The result is not a signed section result.

    Examples
    --------
    >>> callable(render_section_html)
    True

    Limitations
    -----------
    The report covers the supplied section. Member outputs are separate.

    Provenance
    ----------
    Uses the same result and revisions as the JSON projection.
    """
    if not isinstance(result, BeamSectionCheckResultV1):
        raise TypeError("result must be BeamSectionCheckResultV1")
    return render_station_beam_html(result)
