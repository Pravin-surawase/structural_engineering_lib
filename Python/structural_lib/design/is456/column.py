"""Physical column checks, finite catalogue selection and section response."""

from __future__ import annotations

from collections.abc import Mapping

from structural_lib.codes.is456.column._layered_section import (
    rectangular_layered_section,
)
from structural_lib.codes.is456.column._strain_compatibility import (
    COLUMN_SECTION_METHOD,
)
from structural_lib.core.errors import InputContractError, InputIssueV1, ValidationError
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    FamilyIdentityV1,
    canonical_family_result,
    require_request_type,
    translate_owner_input_error,
)
from structural_lib.services.column_api import ColumnDesignResult, design_column_is456
from structural_lib.services.column_candidate_search import (
    render_column_catalogue_html as _render_column_catalogue_html,
)
from structural_lib.services.column_candidate_search import (
    render_column_catalogue_svg as _render_column_catalogue_svg,
)
from structural_lib.services.column_candidate_search import (
    select_column_from_catalogue as _select_column_from_catalogue,
)
from structural_lib.services.column_circular_detailing import (
    CircularColumnDetailingInputV1,
    check_circular_column_detailing,
    render_circular_detailing_bbs_csv,
    render_circular_detailing_html,
    render_circular_detailing_svg,
)
from structural_lib.services.column_circular_member import (
    check_circular_member as _check_circular_member,
)
from structural_lib.services.column_circular_member import (
    render_circular_member_html as _render_circular_member_html,
)
from structural_lib.services.column_circular_member import (
    render_circular_member_svg as _render_circular_member_svg,
)
from structural_lib.services.column_interaction import (
    check_interaction_slice,
    render_interaction_slice_html,
)
from structural_lib.services.column_member import (
    check_four_corner_member as _check_four_corner_member,
)
from structural_lib.services.column_member import (
    render_four_corner_member_html as _render_four_corner_member_html,
)
from structural_lib.services.column_member_detailing import (
    check_column_member_detailing as _check_column_member_detailing,
)
from structural_lib.services.column_member_outputs import (
    render_column_member_bbs_csv as _render_column_member_bbs_csv,
)
from structural_lib.services.column_member_outputs import (
    render_column_member_detailing_html as _render_column_member_detailing_html,
)
from structural_lib.services.column_member_outputs import (
    render_column_member_detailing_svg as _render_column_member_detailing_svg,
)
from structural_lib.services.column_positioned_member import (
    check_positioned_rectangular_member as _check_positioned_rectangular_member,
)
from structural_lib.services.column_positioned_member import (
    render_positioned_rectangular_member_html as _render_positioned_rectangular_member_html,
)
from structural_lib.services.column_service_section import (
    check_service_section,
    render_service_section_html,
)
from structural_lib.services.column_slender_member import (
    check_slender_rectangular_member as _check_slender_rectangular_member,
)
from structural_lib.services.column_slender_member import (
    render_slender_rectangular_member_html as _render_slender_rectangular_member_html,
)
from structural_lib.services.column_slender_member import (
    render_slender_rectangular_member_svg as _render_slender_rectangular_member_svg,
)
from structural_lib.services.column_tied_member import (
    check_tied_rectangular_member as _check_tied_rectangular_member,
)
from structural_lib.services.column_tied_member import (
    render_tied_rectangular_member_html as _render_tied_rectangular_member_html,
)
from structural_lib.services.contracts.column_catalogue import ColumnCatalogueInputV1
from structural_lib.services.contracts.column_circular import CircularColumnInputV1
from structural_lib.services.contracts.column_member import (
    ColumnClosedTieV1,
    ColumnMidpointCrossTieV1,
    FourCornerColumnActionsV1,
    FourCornerColumnGeometryV1,
    FourCornerColumnInputV1,
    FourCornerColumnReinforcementV1,
    PositionedRectangularColumnInputV1,
    RectangularColumnActionsV1,
    RectangularColumnCageV1,
    TiedRectangularColumnInputV1,
)
from structural_lib.services.contracts.column_member_detailing import (
    ColumnMemberDetailingInputV1,
    PositionedColumnMemberDetailingInputV1,
    SlenderColumnMemberDetailingInputV1,
)
from structural_lib.services.contracts.column_section import (
    ColumnInteractionInputV1,
    ColumnSectionInputV1,
    ColumnSectionLayerResponseV1,
    ColumnSectionLayerV1,
    ColumnSectionResponseV1,
    ColumnServiceSectionInputV1,
)
from structural_lib.services.contracts.column_slender import (
    SlenderRectangularColumnInputV1,
)
from structural_lib.services.contracts.common import (
    model_validate_json_or_error,
    model_validate_or_error,
)
from structural_lib.services.contracts.family_f1 import (
    ColumnActionsV1,
    ColumnDesignInputV1,
    ColumnGeometryV1,
    ColumnMaterialsV1,
    ColumnReinforcementV1,
)

__all__ = [
    "ColumnInteractionInputV1",
    "CircularColumnDetailingInputV1",
    "load_circular_column_detailing",
    "check_circular_column_detailing",
    "render_circular_detailing_bbs_csv",
    "render_circular_detailing_html",
    "render_circular_detailing_svg",
    "ColumnServiceSectionInputV1",
    "load_service_section",
    "check_service_section",
    "render_service_section_html",
    "load_interaction_slice",
    "check_interaction_slice",
    "render_interaction_slice_html",
    "ColumnDesignResult",
    "CircularColumnInputV1",
    "ColumnCatalogueInputV1",
    "ColumnMemberDetailingInputV1",
    "PositionedColumnMemberDetailingInputV1",
    "SlenderColumnMemberDetailingInputV1",
    "load_slender_column_member_detailing",
    "load_positioned_column_member_detailing",
    "FamilyIdentityV1",
    "CanonicalFamilyResultV1",
    "ColumnActionsV1",
    "ColumnDesignInputV1",
    "ColumnGeometryV1",
    "ColumnMaterialsV1",
    "ColumnReinforcementV1",
    "ColumnSectionInputV1",
    "ColumnSectionLayerResponseV1",
    "ColumnSectionLayerV1",
    "ColumnSectionResponseV1",
    "ColumnClosedTieV1",
    "ColumnMidpointCrossTieV1",
    "FourCornerColumnActionsV1",
    "FourCornerColumnGeometryV1",
    "FourCornerColumnInputV1",
    "FourCornerColumnReinforcementV1",
    "PositionedRectangularColumnInputV1",
    "SlenderRectangularColumnInputV1",
    "RectangularColumnActionsV1",
    "RectangularColumnCageV1",
    "TiedRectangularColumnInputV1",
    "InputContractError",
    "InputIssueV1",
    "check",
    "check_four_corner_member",
    "check_circular_member",
    "check_tied_rectangular_member",
    "check_positioned_rectangular_member",
    "design",
    "input",
    "layered_section_response",
    "load",
    "load_json",
    "load_layered_section",
    "load_four_corner_member",
    "load_circular_member",
    "load_column_catalogue",
    "load_column_member_detailing",
    "check_column_member_detailing",
    "render_column_member_detailing_html",
    "render_column_member_detailing_svg",
    "render_column_member_bbs_csv",
    "select_column_from_catalogue",
    "render_column_catalogue_html",
    "render_column_catalogue_svg",
    "render_circular_member_html",
    "render_circular_member_svg",
    "render_four_corner_member_html",
    "load_tied_rectangular_member",
    "load_positioned_rectangular_member",
    "render_tied_rectangular_member_html",
    "render_positioned_rectangular_member_html",
    "load_slender_rectangular_member",
    "check_slender_rectangular_member",
    "render_slender_rectangular_member_html",
    "render_slender_rectangular_member_svg",
]


def load_column_member_detailing(
    value: Mapping[str, object] | str | bytes | ColumnMemberDetailingInputV1,
) -> ColumnMemberDetailingInputV1:
    """Load the physical member, tie grid and supplied actions.

    Parameters
    ----------
    value : Mapping[str, object] or str or bytes or ColumnMemberDetailingInputV1
        Member request or its JSON representation.

    Returns
    -------
    ColumnMemberDetailingInputV1
        Validated immutable member request.

    Raises
    ------
    InputContractError
        The request violates the input contract.

    Examples
    --------
    See Python/examples/column_member_detailing.py.

    Limitations
    -----------
    Uses mm, kN, kNm and N/mm². Member actions and project detail evidence are supplied.

    Provenance
    ----------
    Versioned COL07 member input contract.
    """
    if isinstance(value, ColumnMemberDetailingInputV1):
        return value
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(ColumnMemberDetailingInputV1, value)
    return model_validate_or_error(ColumnMemberDetailingInputV1, value)


def check_column_member_detailing(
    request: (
        ColumnMemberDetailingInputV1
        | PositionedColumnMemberDetailingInputV1
        | SlenderColumnMemberDetailingInputV1
    ),
) -> CanonicalFamilyResultV1[dict[str, object]]:
    """Check the member's supplied actions and physical detailing.

    Parameters
    ----------
    request : ColumnMemberDetailingInputV1, PositionedColumnMemberDetailingInputV1 or SlenderColumnMemberDetailingInputV1
        Validated physical member detailing request.

    Returns
    -------
    CanonicalFamilyResultV1
        Station strength and shear, tie zones, end development, splice checks and BBS disposition.

    Raises
    ------
    InputContractError
        A validated typed request is required.

    Examples
    --------
    See Python/examples/column_member_detailing.py.

    Limitations
    -----------
    Ordinary tied rectangles. Mixed and braced slender profiles use continuous bars. Eight-bar physical laps admit one opposing side-midpoint or C1/C2 group.

    Provenance
    ----------
    IS 456 Cl. 26.2, 26.5.3.2 and Cl. 40, Tables 19 and 20.
    """
    return _check_column_member_detailing(request)


def render_column_member_detailing_html(
    result: CanonicalFamilyResultV1[dict[str, object]],
) -> str:
    """Render the member report and checked reinforcement schedule.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        Result of check_column_member_detailing.

    Returns
    -------
    str
        HTML report including section, signed actions, checks and available BBS.

    Raises
    ------
    TypeError
        The result must come from the column member detailing workflow.

    Examples
    --------
    See Python/examples/column_member_detailing.py.

    Limitations
    -----------
    The report covers only the supplied action and detailing basis.

    Provenance
    ----------
    Projects the checked result without recalculation.
    """
    return _render_column_member_detailing_html(result)


def render_column_member_detailing_svg(
    result: CanonicalFamilyResultV1[dict[str, object]],
) -> str:
    """Draw the section and member elevation with checked tie levels.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        Result of check_column_member_detailing.

    Returns
    -------
    str
        SVG showing the input identity, revisions and engineering status.

    Raises
    ------
    TypeError
        The result must come from the column member detailing workflow.

    Examples
    --------
    See Python/examples/column_member_detailing.py.

    Limitations
    -----------
    The section cuts show the checked contact links. The closed hoop uses a supplied fabrication basis.

    Provenance
    ----------
    Projects checked bar coordinates and transverse stations.
    """
    return _render_column_member_detailing_svg(result)


def render_column_member_bbs_csv(
    result: CanonicalFamilyResultV1[dict[str, object]],
) -> str | None:
    """Export the checked member bar bending schedule.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        Result of check_column_member_detailing.

    Returns
    -------
    str | None
        CSV tied to the checked member or None when mandatory checks are held or failed.

    Raises
    ------
    TypeError
        The result must come from the column member detailing workflow.

    Examples
    --------
    See Python/examples/column_member_detailing.py.

    Limitations
    -----------
    The supplied register supplies the hoop cut. Checked contact links use their centreline lengths.

    Provenance
    ----------
    Checked station quantities and declared cut lengths; steel mass uses the shared BBS calculation.
    """
    return _render_column_member_bbs_csv(result)


def load_column_catalogue(
    value: Mapping[str, object] | str | bytes | ColumnCatalogueInputV1,
) -> ColumnCatalogueInputV1:
    """Load the candidate catalogue, analysis basis and concurrent actions.

    Parameters
    ----------
    value : Mapping[str, object] or str or bytes or ColumnCatalogueInputV1
        Approved oriented sizes, bar diameters and tie options with signed rows.

    Returns
    -------
    ColumnCatalogueInputV1
        Validated immutable request.

    Raises
    ------
    InputContractError
        Invalid inputs, duplicate identifiers or a catalogue outside the bounds.

    Examples
    --------
    See Python/examples/column_catalogue_selection.py for a complete input.

    Limitations
    -----------
    At most 128 candidates and eight supplied action rows. Uses mm, MPa, kN and kNm.

    Provenance
    ----------
    COL06 finite catalogue contract and the physical tied rectangular profile.
    """
    if isinstance(value, ColumnCatalogueInputV1):
        return value
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(ColumnCatalogueInputV1, value)
    return model_validate_or_error(ColumnCatalogueInputV1, value)


def select_column_from_catalogue(
    request: ColumnCatalogueInputV1,
) -> CanonicalFamilyResultV1[dict[str, object]]:
    """Rank the supplied options and check each required action row.

    Parameters
    ----------
    request : ColumnCatalogueInputV1
        Validated catalogue from load_column_catalogue.

    Returns
    -------
    CanonicalFamilyResultV1
        Evaluated candidates, terminal search state, and selection if resolved.

    Raises
    ------
    InputContractError
        A validated typed request is required.

    Examples
    --------
    Pass the result of load_column_catalogue to select_column_from_catalogue.

    Limitations
    -----------
    Short braced eight-bar rectangles only. An incompatible or stale analysis
    basis leaves a locally feasible candidate on HOLD.

    Provenance
    ----------
    COL06 catalogue rank and the existing IS 456 tied rectangular member checks.
    """
    return _select_column_from_catalogue(request)


def render_column_catalogue_html(
    result: CanonicalFamilyResultV1[dict[str, object]],
) -> str:
    """Show the outcome, all evaluated candidates and the governing section.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        Result of select_column_from_catalogue.

    Returns
    -------
    str
        HTML with actions, per-row checks and the selected section when available.

    Raises
    ------
    TypeError
        The result must come from the catalogue workflow.

    Examples
    --------
    See Python/examples/column_catalogue_selection.py.

    Limitations
    -----------
    The report covers the supplied catalogue, combinations and local cage only.

    Provenance
    ----------
    Uses the existing result and the checked governing cage without recalculation.
    """
    return _render_column_catalogue_html(result)


def render_column_catalogue_svg(
    result: CanonicalFamilyResultV1[dict[str, object]],
) -> str | None:
    """Draw the selected local section from its governing check.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        Result of select_column_from_catalogue.

    Returns
    -------
    str or None
        SVG with the result status, or None when no candidate is selected.

    Raises
    ------
    TypeError
        The result must come from the catalogue workflow.

    Examples
    --------
    See Python/examples/column_catalogue_selection.py.

    Limitations
    -----------
    The cross-section shows restraints at their local projected positions.
    A HOLD drawing is provisional; member-wide detailing is outside this scope.

    Provenance
    ----------
    Projects the checked local bar and link coordinates without recalculation.
    """
    return _render_column_catalogue_svg(result)


def load_circular_member(
    value: Mapping[str, object] | str | bytes | CircularColumnInputV1,
) -> CircularColumnInputV1:
    """Load a circular bar cage and its concurrent station actions.

    Parameters
    ----------
    value : Mapping[str, object] or str or bytes or CircularColumnInputV1
        Diameter, uniform bar ring, transverse reinforcement and signed actions.

    Returns
    -------
    CircularColumnInputV1
        Validated immutable request.

    Raises
    ------
    InputContractError
        Invalid fields, circular geometry or a station outside the member.

    Examples
    --------
    Run Python/examples/circular_column_member.py.

    Limitations
    -----------
    One concurrent compression combination at a short braced circular station.

    Provenance
    ----------
    CircularColumnInputV1 owns the versioned input contract.
    """
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(CircularColumnInputV1, value)
    return model_validate_or_error(CircularColumnInputV1, value)


def check_circular_member(
    request: CircularColumnInputV1,
) -> CanonicalFamilyResultV1[dict[str, object]]:
    """Check circular section strength and the actual local restraint.

    Parameters
    ----------
    request : CircularColumnInputV1
        Validated circular cage and simultaneous compression and signed moments.

    Returns
    -------
    CanonicalFamilyResultV1
        Separate restraint and strength results with checked circular geometry.

    Raises
    ------
    InputContractError
        The check requires a typed circular member request.

    Examples
    --------
    Pass the result of load_circular_member.

    Limitations
    -----------
    The spiral factor applies to the admitted short axial method.
    Slender and seismic checks require separate profiles.

    Provenance
    ----------
    IS 456:2000 Cl. 25.1–25.4, 26.5.3.2, 38.1 and 39.1–39.7.
    """
    return _check_circular_member(request)


def render_circular_member_html(
    result: CanonicalFamilyResultV1[dict[str, object]],
) -> str:
    """Render the circular-member result and checked cage.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        Result from check_circular_member.

    Returns
    -------
    str
        HTML report with the same input hash as the checked result.

    Raises
    ------
    TypeError
        The result belongs to another workflow.

    Examples
    --------
    See Python/examples/circular_column_member.py.

    Limitations
    -----------
    The drawing describes the checked local section.

    Provenance
    ----------
    All displayed engineering values come from the supplied result.
    """
    return _render_circular_member_html(result)


def render_circular_member_svg(
    result: CanonicalFamilyResultV1[dict[str, object]],
) -> str:
    """Draw the checked local column section as standalone SVG.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        Result from check_circular_member.

    Returns
    -------
    str
        SVG with bar and transverse identities and the result's input hash.

    Raises
    ------
    TypeError
        The result belongs to another workflow.

    Examples
    --------
    See Python/examples/circular_column_member.py.

    Limitations
    -----------
    Local cross section and projected transverse reinforcement.

    Provenance
    ----------
    The drawing uses the supplied checked cage without recomputing it.
    """
    return _render_circular_member_svg(result)


def load_slender_rectangular_member(
    value: Mapping[str, object] | str | bytes | SlenderRectangularColumnInputV1,
) -> SlenderRectangularColumnInputV1:
    """Load an actual rectangular cage and its slender-member actions.

    Parameters
    ----------
    value : Mapping[str, object] or str or bytes or SlenderRectangularColumnInputV1
        Physical geometry, axis-specific restraint, signed actions and analysis revision.

    Returns
    -------
    SlenderRectangularColumnInputV1
        Validated immutable request.

    Raises
    ------
    InputContractError
        Invalid fields, cage geometry or conflicting action representations.

    Examples
    --------
    Run Python/examples/slender_rectangular_column_member.py.

    Limitations
    -----------
    One concurrent compressive combination on a prismatic braced column.

    Provenance
    ----------
    SlenderRectangularColumnInputV1 owns the versioned input contract.
    """
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(SlenderRectangularColumnInputV1, value)
    return model_validate_or_error(SlenderRectangularColumnInputV1, value)


def check_slender_rectangular_member(
    request: SlenderRectangularColumnInputV1,
) -> CanonicalFamilyResultV1[dict[str, object]]:
    """Check the signed member actions and local reinforcement restraint.

    Parameters
    ----------
    request : SlenderRectangularColumnInputV1
        Validated end actions or supplied deflection-aware station actions.

    Returns
    -------
    CanonicalFamilyResultV1
        Axis classifications, signed checked actions, restraint and governing strength.

    Raises
    ------
    InputContractError
        The check requires a typed slender rectangular request.

    Examples
    --------
    Pass the result of load_slender_rectangular_member.

    Limitations
    -----------
    First-order additions are unreduced and require no transverse member load.
    Global stability and member-wide fabrication are outside this profile.

    Provenance
    ----------
    IS 456:2000 Cl. 25.1–25.4, 26.5.3.2, 38.1 and 39.1–39.7.
    """
    return _check_slender_rectangular_member(request)


def render_slender_rectangular_member_html(
    result: CanonicalFamilyResultV1[dict[str, object]],
) -> str:
    """Render the slender-member result, governing actions and checked cage.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        Result from check_slender_rectangular_member.

    Returns
    -------
    str
        HTML report with the same input hash as the checked result.

    Raises
    ------
    TypeError
        The result belongs to another workflow.

    Examples
    --------
    See Python/examples/slender_rectangular_column_member.py.

    Limitations
    -----------
    The drawing describes the checked local section.

    Provenance
    ----------
    All displayed engineering values come from the supplied result.
    """
    return _render_slender_rectangular_member_html(result)


def render_slender_rectangular_member_svg(
    result: CanonicalFamilyResultV1[dict[str, object]],
) -> str:
    """Draw the checked local column section as standalone SVG.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        Result from check_slender_rectangular_member.

    Returns
    -------
    str
        SVG with checked bar and link identities and the result's input hash.

    Raises
    ------
    TypeError
        The result belongs to another workflow.

    Examples
    --------
    See Python/examples/slender_rectangular_column_member.py.

    Limitations
    -----------
    Local cross section and projected links.

    Provenance
    ----------
    The drawing uses the supplied checked cage without recomputing it.
    """
    return _render_slender_rectangular_member_svg(result)


def load_positioned_rectangular_member(
    value: Mapping[str, object] | str | bytes | PositionedRectangularColumnInputV1,
) -> PositionedRectangularColumnInputV1:
    """Load one explicit mixed-bar cage and signed member demand.

    Parameters
    ----------
    value : Mapping[str, object] or str or bytes or PositionedRectangularColumnInputV1
        Section, individual bars, supplied tie paths and factored station actions.

    Returns
    -------
    PositionedRectangularColumnInputV1
        An immutable versioned request.

    Raises
    ------
    InputContractError
        The request is malformed or contains overlapping bar geometry.

    Examples
    --------
    Run Python/examples/positioned_rectangular_column_member.py.

    Limitations
    -----------
    The profile admits 9–32 positioned bars and aligned open links.

    Provenance
    ----------
    PositionedRectangularColumnInputV1 owns the strict input contract.
    """
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(PositionedRectangularColumnInputV1, value)
    return model_validate_or_error(PositionedRectangularColumnInputV1, value)


def check_positioned_rectangular_member(
    request: PositionedRectangularColumnInputV1,
) -> CanonicalFamilyResultV1[dict[str, object]]:
    """Check strength and restraint for the actual positioned column cage.

    Parameters
    ----------
    request : PositionedRectangularColumnInputV1
        One rectangular cage and its concurrent factored action pair.

    Returns
    -------
    CanonicalFamilyResultV1
        Separate strength and restraint dispositions with checked bar and link data.

    Raises
    ------
    InputContractError
        The operation requires a typed positioned rectangular request.

    Examples
    --------
    Check the result of load_positioned_rectangular_member.

    Limitations
    -----------
    A single short braced station with supported tie geometry is checked.

    Provenance
    ----------
    IS 456:2000 Cl. 25.4, 26.5.3.2, 38.1, 39.1, 39.5 and 39.6.
    """
    return _check_positioned_rectangular_member(request)


def render_positioned_rectangular_member_html(
    result: CanonicalFamilyResultV1[dict[str, object]],
) -> str:
    """Render the checked positioned cage and its section results.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        The positioned rectangular member result.

    Returns
    -------
    str
        HTML with the original identities, cage, local restraint and strength.

    Raises
    ------
    TypeError
        The result belongs to a different workflow.

    Examples
    --------
    Run the positioned rectangular member example with --output-dir.

    Limitations
    -----------
    The drawing covers the checked cross section.

    Provenance
    ----------
    The original canonical result supplies all rendered values.
    """
    return _render_positioned_rectangular_member_html(result)


def load_tied_rectangular_member(
    value: Mapping[str, object] | str | bytes | TiedRectangularColumnInputV1,
) -> TiedRectangularColumnInputV1:
    """Load the eight-bar or either oriented six-bar tied member request.

    Parameters
    ----------
    value : Mapping[str, object] or str or bytes or TiedRectangularColumnInputV1
        Section, checked station, signed factored actions and tie schedule.

    Returns
    -------
    TiedRectangularColumnInputV1
        An immutable versioned request.

    Raises
    ------
    InputContractError
        Invalid JSON, unsupported layout or inadmissible request fields.

    Examples
    --------
    Run Python/examples/tied_rectangular_column_member.py with a layout flag.

    Limitations
    -----------
    The three symmetric equal-bar layouts use one supplied action pair.

    Provenance
    ----------
    TiedRectangularColumnInputV1 owns the strict input contract.
    """
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(TiedRectangularColumnInputV1, value)
    return model_validate_or_error(TiedRectangularColumnInputV1, value)


def check_tied_rectangular_member(
    request: TiedRectangularColumnInputV1,
) -> CanonicalFamilyResultV1[dict[str, object]]:
    """Check a supplied factored action pair and its actual short-member cage.

    Parameters
    ----------
    request : TiedRectangularColumnInputV1
        A validated geometry, cage and simultaneous axial and moment demand.

    Returns
    -------
    CanonicalFamilyResultV1
        Check dispositions, positioned bars, fixed-load capacities and restraint.

    Raises
    ------
    InputContractError
        The operation requires a typed tied rectangular request.

    Examples
    --------
    Pass the result of load_tied_rectangular_member to this check.

    Limitations
    -----------
    The strength profile admits a short braced member in partial compression.

    Provenance
    ----------
    IS 456:2000 Cl. 25.4, Cl. 26.5.3.2, Cl. 39.5 and Cl. 39.6.
    """
    return _check_tied_rectangular_member(request)


def render_tied_rectangular_member_html(
    result: CanonicalFamilyResultV1[dict[str, object]],
) -> str:
    """Render the checked section, restraint paths, inputs and verdict.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        The tied rectangular check result.

    Returns
    -------
    str
        HTML with the result's identities and checked section schematic.

    Raises
    ------
    TypeError
        The result belongs to a different workflow.

    Examples
    --------
    Run the tied rectangular member example with --output-dir.

    Limitations
    -----------
    The schematic covers the checked section and local restraint paths.

    Provenance
    ----------
    The renderer consumes the original canonical result without recalculation.
    """
    return _render_tied_rectangular_member_html(result)


def load_four_corner_member(
    value: Mapping[str, object] | str | bytes | FourCornerColumnInputV1,
) -> FourCornerColumnInputV1:
    """Load one physical four-corner column request from Python or JSON.

    Parameters
    ----------
    value : Mapping[str, object] or str or bytes or FourCornerColumnInputV1
        Explicit geometry, one principal-axis action, four equal bars and actual ties.

    Returns
    -------
    FourCornerColumnInputV1
        An immutable request with a versioned JSON schema.

    Raises
    ------
    InputContractError
        Malformed JSON, duplicate fields, invalid values or unsupported topology.

    Examples
    --------
    Run Python/examples/four_corner_column_member.py with the current source build.

    Limitations
    -----------
    The profile admits a braced rectangle with one selected principal bending axis.

    Provenance
    ----------
    The shared strict decoder and FourCornerColumnInputV1 own input validation.
    """
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(FourCornerColumnInputV1, value)
    return model_validate_or_error(FourCornerColumnInputV1, value)


def check_four_corner_member(
    request: FourCornerColumnInputV1,
) -> CanonicalFamilyResultV1[dict[str, object]]:
    """Check a short braced column with four equal physical corner bars.

    Parameters
    ----------
    request : FourCornerColumnInputV1
        Validated geometry, principal-axis actions and supplied cage in explicit units.

    Returns
    -------
    CanonicalFamilyResultV1
        Bound inputs, physical bars, actual tie checks, principal-axis strength and status.

    Raises
    ------
    InputContractError
        An invalid or unsupported request object is supplied.

    Examples
    --------
    Use check_four_corner_member(load_four_corner_member(payload)).
    See docs/cookbook/python/column-supplied-steel-check.md for the complete recipe.

    Limitations
    -----------
    PASS covers the selected strength and cage checks. The result records the
    remaining joint, splice, serviceability, fire and seismic evidence boundaries.

    Provenance
    ----------
    Reuses the ordinary column P–M owner with two pairs at derived physical centres
    and the four-corner cage owner. Every result carries its source references.
    """
    return _check_four_corner_member(request)


def render_four_corner_member_html(
    result: CanonicalFamilyResultV1[dict[str, object]],
) -> str:
    """Render a report directly from one physical four-corner member result.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        Result from check_four_corner_member, including the original request.

    Returns
    -------
    str
        HTML containing the same inputs, bars, ties, checks, status and input hash.

    Raises
    ------
    TypeError
        The result belongs to another workflow.

    Examples
    --------
    Save render_four_corner_member_html(result) to a UTF-8 report.html file.

    Limitations
    -----------
    The report carries the calculation scope and qualified-review state.

    Provenance
    ----------
    All engineering values are read from the checked result and its request.
    """
    return _render_four_corner_member_html(result)


def input(  # noqa: A001
    *,
    identity: FamilyIdentityV1 | Mapping[str, object],
    geometry: ColumnGeometryV1 | Mapping[str, object],
    actions: ColumnActionsV1 | Mapping[str, object],
    materials: ColumnMaterialsV1 | Mapping[str, object],
    reinforcement: ColumnReinforcementV1 | Mapping[str, object],
) -> ColumnDesignInputV1:
    """Build a validated column request from explicit groups.

    Parameters
    ----------
    identity : FamilyIdentityV1 or Mapping[str, object]
        Member, case and caller-owned source identity. Mapping inputs use the same strict validation.
    geometry : ColumnGeometryV1 or Mapping[str, object]
        Dimensions in mm and the explicit support/topology choices. Mapping inputs use the same strict validation.
    actions : ColumnActionsV1 or Mapping[str, object]
        Factored design actions in the units named by each field. Mapping inputs use the same strict validation.
    materials : ColumnMaterialsV1 or Mapping[str, object]
        Concrete and reinforcement strengths in N/mm². Mapping inputs use the same strict validation.
    reinforcement : ColumnReinforcementV1 or Mapping[str, object]
        Supplied bar areas, positions or dimensions in mm and mm². Mapping inputs use the same strict validation.

    Returns
    -------
    ColumnDesignInputV1
        Immutable typed request, ready for ``design``.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Automatic steel selection, circular sections and arbitrary bar layouts are not supported.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable column recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(
        ColumnDesignInputV1,
        {
            "identity": identity,
            "geometry": geometry,
            "actions": actions,
            "materials": materials,
            "reinforcement": reinforcement,
        },
    )


def load(value: Mapping[str, object] | ColumnDesignInputV1) -> ColumnDesignInputV1:
    """Validate a Python mapping or an existing ColumnDesignInputV1.

    Parameters
    ----------
    value : Mapping[str, object] or ColumnDesignInputV1
        Python fields or a typed request; values are not silently coerced.
        For serialized text or bytes, use ``load_json`` directly.

    Returns
    -------
    ColumnDesignInputV1
        Validated immutable request with field-level issue paths on rejection.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Automatic steel selection, circular sections and arbitrary bar layouts are not supported.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable column recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(ColumnDesignInputV1, value)


def load_json(value: str | bytes) -> ColumnDesignInputV1:
    """Load a validated request directly from JSON text or UTF-8 bytes.

    Parameters
    ----------
    value : str or bytes
        Serialized ColumnDesignInputV1 fields, using the units named by the request.
        UTF-8 byte-order marks are accepted; values are not silently coerced.

    Returns
    -------
    ColumnDesignInputV1
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
    return model_validate_json_or_error(ColumnDesignInputV1, value)


def load_layered_section(
    value: Mapping[str, object] | str | bytes | ColumnSectionInputV1,
) -> ColumnSectionInputV1:
    """Read a prescribed layered column section from Python or JSON.

    Parameters
    ----------
    value : Mapping[str, object] or str or bytes or ColumnSectionInputV1
        Explicit dimensions, strengths, neutral-axis depth and bar layers.

    Returns
    -------
    ColumnSectionInputV1
        An immutable section request with a versioned JSON schema.

    Raises
    ------
    InputContractError
        The input contains invalid fields, duplicate JSON keys or unsupported geometry.

    Examples
    --------
    Use ``load_layered_section(request.model_dump_json())`` to restore a saved
    request. See the layered column section cookbook for a complete example.

    Limitations
    -----------
    The profile admits a solid rectangle and positive ``xu_mm`` with a finite
    depth ratio. Depths are measured from the top compression face. Use
    separate diameter groups at the same depth for mixed bars.

    Provenance
    ----------
    Both entry paths use ColumnSectionInputV1 and the shared strict input contract.
    """
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(ColumnSectionInputV1, value)
    return model_validate_or_error(ColumnSectionInputV1, value)


def layered_section_response(request: ColumnSectionInputV1) -> ColumnSectionResponseV1:
    """Evaluate the raw axial force and centroidal moment for a prescribed strain plane.

    Parameters
    ----------
    request : ColumnSectionInputV1
        Validated rectangular section, one bending axis and depth-wise bar layers.

    Returns
    -------
    ColumnSectionResponseV1
        Compression-positive axial force in kN, signed centroidal moment in kN m,
        strains, force contributions, source references and calculation status.

    Raises
    ------
    InputContractError
        The request has the wrong type. Use load_layered_section for raw inputs.

    Examples
    --------
    Call ``layered_section_response(load_layered_section(payload))``. The
    layered column section cookbook shows full and partial compression and
    mixed diameters.

    Limitations
    -----------
    This operation returns a section response at the supplied neutral axis.
    The result leaves member and detailing acceptance unevaluated.

    Provenance
    ----------
    IS 456:2000 Cl. 38.1, Figs. 21 and 23, and Cl. 39.1(b).
    """
    require_request_type(request, ColumnSectionInputV1)
    result = rectangular_layered_section(
        b_mm=request.b_mm,
        D_mm=request.D_mm,
        xu_mm=request.xu_mm,
        fck_nmm2=request.fck_nmm2,
        fy_nmm2=request.fy_nmm2,
        layer_depths_and_areas=tuple(
            (layer.depth_from_top_mm, layer.area_mm2) for layer in request.layers
        ),
    )
    return ColumnSectionResponseV1(
        request=request,
        method_revision_id=COLUMN_SECTION_METHOD,
        source_references=(
            "IS 456:2000 Cl. 36.4.2 and Cl. 38.1, Figs. 21 and 23",
            "IS 456:2000 Cl. 39.1(b)",
        ),
        top_strain=result.top_strain,
        far_face_strain=result.far_face_strain,
        gross_concrete_axial_kn=result.gross_concrete_force_n / 1000,
        gross_concrete_centroid_moment_knm=result.gross_concrete_centroid_moment_nmm
        / 1e6,
        axial_kn=result.axial_force_n / 1000,
        centroid_moment_knm=result.centroid_moment_nmm / 1e6,
        layers=tuple(
            ColumnSectionLayerResponseV1(
                layer=layer,
                area_mm2=layer.area_mm2,
                strain=response.strain,
                steel_stress_nmm2=response.steel_stress_nmm2,
                displaced_concrete_stress_nmm2=response.displaced_concrete_stress_nmm2,
                net_axial_kn=response.net_force_n / 1000,
                centroid_moment_knm=response.centroid_moment_nmm / 1e6,
            )
            for layer, response in zip(request.layers, result.layers, strict=True)
        ),
    )


def design(request: ColumnDesignInputV1) -> CanonicalFamilyResultV1[ColumnDesignResult]:
    """Check supplied reinforcement for a solid rectangular column.

    Parameters
    ----------
    request : ColumnDesignInputV1
        Validated input from ``input`` or ``load``; all engineering bases are explicit.

    Returns
    -------
    CanonicalFamilyResultV1[ColumnDesignResult]
        ``calculation`` holds the maintained owner result. Read
        ``engineering_status`` for PASS/FAIL/HOLD, ``limitations`` for scope,
        and ``to_dict()`` for finite JSON. Completion is not engineering approval.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Automatic steel selection, circular sections and arbitrary bar layouts are not supported.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable column recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    require_request_type(request, ColumnDesignInputV1)
    geometry = request.geometry
    actions = request.actions
    materials = request.materials
    reinforcement = request.reinforcement
    try:
        calculation = design_column_is456(
            Pu_kN=actions.pu_kn,
            Mux_kNm=actions.mux_knm,
            Muy_kNm=actions.muy_knm,
            b_mm=geometry.b_mm,
            D_mm=geometry.D_mm,
            l_mm=geometry.unsupported_length_mm,
            end_condition=geometry.end_condition,
            fck_nmm2=materials.fck_nmm2,
            fy_nmm2=materials.fy_nmm2,
            Asc_mm2=reinforcement.supplied_steel_area_mm2,
            d_prime_mm=reinforcement.reinforcement_centroid_depth_mm,
            l_unsupported_mm=geometry.minimum_eccentricity_length_mm,
            braced=geometry.braced,
            M1x_kNm=actions.m1x_signed_knm,
            M2x_kNm=actions.m2x_signed_knm,
            M1y_kNm=actions.m1y_signed_knm,
            M2y_kNm=actions.m2y_signed_knm,
        )
    except InputContractError as error:
        from dataclasses import replace

        paths = {
            "Mux_kNm": "actions.mux_knm",
            "Muy_kNm": "actions.muy_knm",
            "M2x_kNm": "actions.m2x_signed_knm",
            "M2y_kNm": "actions.m2y_signed_knm",
        }
        raise InputContractError(
            tuple(
                replace(issue, path=paths.get(issue.path, issue.path))
                for issue in error.issues
            )
        ) from error
    except (ValidationError, TypeError, ValueError) as error:
        translate_owner_input_error(error)
    return canonical_family_result(
        request,
        calculation,
        workflow_id="is456.column.supplied-steel-check/v1",
        engineering_status=(
            EngineeringStatus.PASS if calculation["is_safe"] else EngineeringStatus.FAIL
        ),
        limitations=(
            "Checks one supplied equal-opposite-face steel area for a solid rectangular column.",
            "Automatic steel selection, arbitrary multilayer layouts, circular sections, and professional approval are held.",
        ),
        assumptions=(
            "All end moments and restraint choices are explicit caller inputs.",
        ),
        provenance=("structural_lib.services.column_api.design_column_is456",),
    )


def check(request: ColumnDesignInputV1) -> CanonicalFamilyResultV1[ColumnDesignResult]:
    """Check supplied reinforcement for a solid rectangular column.

    Parameters
    ----------
    request : ColumnDesignInputV1
        Validated input from ``input`` or ``load``; all engineering bases are explicit.

    Returns
    -------
    CanonicalFamilyResultV1[ColumnDesignResult]
        ``calculation`` holds the maintained owner result. Read
        ``engineering_status`` for PASS/FAIL/HOLD, ``limitations`` for scope,
        and ``to_dict()`` for finite JSON. Completion is not engineering approval.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Automatic steel selection, circular sections and arbitrary bar layouts are not supported.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable column recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return design(request)


def load_interaction_slice(
    value: Mapping[str, object] | str | bytes | ColumnInteractionInputV1,
) -> ColumnInteractionInputV1:
    """Parse actual bars, a compression level and a diagram resolution.

    Parameters
    ----------
    value : Mapping, JSON str or bytes, or ColumnInteractionInputV1
        A solid section and its physical bar centres.

    Returns
    -------
    ColumnInteractionInputV1
        The validated request for the fixed-compression section slice.

    Raises
    ------
    InputContractError
        Section dimensions, bars or analysis inputs violate the contract.

    Examples
    --------
    >>> callable(load_interaction_slice)
    True

    Limitations
    -----------
    Nonnegative axial compression on a solid rectangle or circle.

    Provenance
    ----------
    Uses the strict interaction input contract and canonical intake issues.
    """
    if isinstance(value, ColumnInteractionInputV1):
        return value
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(ColumnInteractionInputV1, value)
    return model_validate_or_error(ColumnInteractionInputV1, value)


def load_service_section(
    value: Mapping[str, object] | str | bytes | ColumnServiceSectionInputV1,
) -> ColumnServiceSectionInputV1:
    """Load one concurrent service action row and its physical section.

    Parameters
    ----------
    value : Mapping, JSON str or bytes, or ColumnServiceSectionInputV1
        A solid rectangle or circle, actual bars, actions and elastic material data.

    Returns
    -------
    ColumnServiceSectionInputV1
        The validated column section service request.

    Raises
    ------
    InputContractError
        The section, actions, material data or bars violate the contract.

    Examples
    --------
    >>> callable(load_service_section)
    True

    Limitations
    -----------
    Solid rectangles and circles with one supplied action row, compression positive.

    Provenance
    ----------
    Uses the strict positioned-bar service section contract.
    """
    if isinstance(value, ColumnServiceSectionInputV1):
        return value
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(ColumnServiceSectionInputV1, value)
    return model_validate_or_error(ColumnServiceSectionInputV1, value)


def load_positioned_column_member_detailing(
    value: Mapping[str, object] | str | bytes | PositionedColumnMemberDetailingInputV1,
) -> PositionedColumnMemberDetailingInputV1:
    """Load actual mixed longitudinal bars and the full short member tie grid.

    Parameters
    ----------
    value : Mapping, JSON str or bytes, or PositionedColumnMemberDetailingInputV1
        Physical bar and tie geometry, concurrent station actions and approved hoop cut.

    Returns
    -------
    PositionedColumnMemberDetailingInputV1
        A validated immutable physical member request.

    Raises
    ------
    InputContractError
        The request violates the positioned member detailing contract.

    Examples
    --------
    See Python/examples/column_member_detailing.py with the mixed member fixture.

    Limitations
    -----------
    Ordinary short braced rectangles with continuous straight mixed bars.

    Provenance
    ----------
    Uses the COL03 positioned cage and COL07 member detailing contracts.
    """
    if isinstance(value, PositionedColumnMemberDetailingInputV1):
        return value
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(
            PositionedColumnMemberDetailingInputV1, value
        )
    return model_validate_or_error(PositionedColumnMemberDetailingInputV1, value)


def load_circular_column_detailing(
    value: Mapping[str, object] | str | bytes | CircularColumnDetailingInputV1,
) -> CircularColumnDetailingInputV1:
    """Load the circular cage, supplied actions and full member placement.

    Parameters
    ----------
    value : Mapping, JSON str or bytes, or CircularColumnDetailingInputV1
        Actual ring or spiral, station actions, end projections and cut basis.

    Returns
    -------
    CircularColumnDetailingInputV1
        The validated circular member detailing request.

    Raises
    ------
    InputContractError
        The cage or member evidence violates the request contract.

    Examples
    --------
    See the circular member detailing example.

    Limitations
    -----------
    Short braced circular cages with continuous straight bars.

    Provenance
    ----------
    Uses the COL05 circular cage and checked member placement contract.
    """
    if isinstance(value, CircularColumnDetailingInputV1):
        return value
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(CircularColumnDetailingInputV1, value)
    return model_validate_or_error(CircularColumnDetailingInputV1, value)


def load_slender_column_member_detailing(
    value: Mapping[str, object] | str | bytes | SlenderColumnMemberDetailingInputV1,
) -> SlenderColumnMemberDetailingInputV1:
    """Load a braced slender rectangle and its supplied second-order rows.

    Parameters
    ----------
    value : Mapping, JSON str or bytes, or SlenderColumnMemberDetailingInputV1
        Physical member, current second-order actions and cut register.

    Returns
    -------
    SlenderColumnMemberDetailingInputV1
        A validated immutable physical detailing request.

    Raises
    ------
    InputContractError
        The member or action evidence violates the contract.

    Examples
    --------
    See the slender detailing replay in Python/examples/column_member_detailing.py.

    Limitations
    -----------
    Ordinary tied rectangular cages, continuous bars and zero supplied shear.

    Provenance
    ----------
    Binds COL04 supplied second-order checks to COL07 full-length placement.
    """
    if isinstance(value, SlenderColumnMemberDetailingInputV1):
        return value
    if isinstance(value, (str, bytes)):
        return model_validate_json_or_error(SlenderColumnMemberDetailingInputV1, value)
    return model_validate_or_error(SlenderColumnMemberDetailingInputV1, value)
