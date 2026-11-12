"""Supplied-steel column member checks and prescribed section response."""

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
from structural_lib.services.column_member import (
    check_four_corner_member as _check_four_corner_member,
)
from structural_lib.services.column_member import (
    render_four_corner_member_html as _render_four_corner_member_html,
)
from structural_lib.services.column_tied_member import (
    check_tied_rectangular_member as _check_tied_rectangular_member,
)
from structural_lib.services.column_tied_member import (
    render_tied_rectangular_member_html as _render_tied_rectangular_member_html,
)
from structural_lib.services.contracts.column_member import (
    ColumnClosedTieV1,
    ColumnMidpointCrossTieV1,
    FourCornerColumnActionsV1,
    FourCornerColumnGeometryV1,
    FourCornerColumnInputV1,
    FourCornerColumnReinforcementV1,
    RectangularColumnActionsV1,
    RectangularColumnCageV1,
    TiedRectangularColumnInputV1,
)
from structural_lib.services.contracts.column_section import (
    ColumnSectionInputV1,
    ColumnSectionLayerResponseV1,
    ColumnSectionLayerV1,
    ColumnSectionResponseV1,
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
    "ColumnDesignResult",
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
    "RectangularColumnActionsV1",
    "RectangularColumnCageV1",
    "TiedRectangularColumnInputV1",
    "InputContractError",
    "InputIssueV1",
    "check",
    "check_four_corner_member",
    "check_tied_rectangular_member",
    "design",
    "input",
    "layered_section_response",
    "load",
    "load_json",
    "load_layered_section",
    "load_four_corner_member",
    "render_four_corner_member_html",
    "load_tied_rectangular_member",
    "render_tied_rectangular_member_html",
]


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
