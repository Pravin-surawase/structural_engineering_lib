"""Curated facades for the three maintained solid-slab route classes."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from structural_lib.codes.is456.slab.models import (
    SlabCapacityFailureResult,
    SlabContractError,
)
from structural_lib.core.errors import InputContractError, InputIssueV1
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    FamilyIdentityV1,
    canonical_family_result,
    require_request_type,
    translate_owner_input_error,
)
from structural_lib.services.contracts.common import (
    StrictPublicModel,
    model_validate_or_error,
)
from structural_lib.services.contracts.family_f1 import (
    ContinuousOneWaySlabActionsV1,
    ContinuousOneWaySlabGeometryV1,
    ContinuousOneWaySlabInputV1,
    ContinuousOneWaySlabReinforcementV1,
    OneWaySlabActionsV1,
    OneWaySlabGeometryV1,
    OneWaySlabInputV1,
    OneWaySlabReinforcementV1,
    SlabMaterialsV1,
    SlabServiceabilityEvidenceV1,
    TwoWaySlabActionsV1,
    TwoWaySlabGeometryV1,
    TwoWaySlabInputV1,
    TwoWaySlabReinforcementV1,
)
from structural_lib.services.slab_api import (
    CompleteOneWaySlabDesignResult,
    ContinuousOneWaySlabDesignResult,
    TwoWaySlabPanelWorkflowResult,
    design_complete_one_way_slab_is456,
    design_continuous_one_way_slab_builtin_is456,
    design_two_way_slab_panel_builtin_is456,
)

__all__ = [
    "ContinuousOneWaySlabActionsV1",
    "ContinuousOneWaySlabGeometryV1",
    "ContinuousOneWaySlabReinforcementV1",
    "FamilyIdentityV1",
    "OneWaySlabActionsV1",
    "OneWaySlabGeometryV1",
    "OneWaySlabReinforcementV1",
    "TwoWaySlabActionsV1",
    "TwoWaySlabGeometryV1",
    "TwoWaySlabReinforcementV1",
    "input_continuous_one_way",
    "input_one_way",
    "input_two_way",
    "CanonicalFamilyResultV1",
    "CompleteOneWaySlabDesignResult",
    "ContinuousOneWaySlabInputV1",
    "ContinuousOneWaySlabDesignResult",
    "InputContractError",
    "InputIssueV1",
    "OneWaySlabInputV1",
    "SlabMaterialsV1",
    "SlabServiceabilityEvidenceV1",
    "TwoWaySlabInputV1",
    "TwoWaySlabPanelWorkflowResult",
    "design_continuous_one_way",
    "design_one_way",
    "design_two_way",
    "load_continuous_one_way",
    "load_one_way",
    "load_two_way",
]


def input_one_way(
    *,
    identity: FamilyIdentityV1 | Mapping[str, object],
    geometry: OneWaySlabGeometryV1 | Mapping[str, object],
    actions: OneWaySlabActionsV1 | Mapping[str, object],
    materials: SlabMaterialsV1 | Mapping[str, object],
    reinforcement: OneWaySlabReinforcementV1 | Mapping[str, object],
    serviceability_evidence: SlabServiceabilityEvidenceV1 | Mapping[str, object],
) -> OneWaySlabInputV1:
    """Build the supported one way slab request from typed groups.

    Parameters
    ----------
    identity : FamilyIdentityV1 or Mapping[str, object]
        Explicit identity group; units are named on its fields.
    geometry : OneWaySlabGeometryV1 or Mapping[str, object]
        Explicit geometry group; units are named on its fields.
    actions : OneWaySlabActionsV1 or Mapping[str, object]
        Explicit actions group; units are named on its fields.
    materials : SlabMaterialsV1 or Mapping[str, object]
        Explicit materials group; units are named on its fields.
    reinforcement : OneWaySlabReinforcementV1 or Mapping[str, object]
        Explicit reinforcement group; units are named on its fields.
    serviceability_evidence : SlabServiceabilityEvidenceV1 or Mapping[str, object]
        Explicit serviceability evidence group; units are named on its fields.

    Returns
    -------
    OneWaySlabInputV1
        Immutable request for ``design_one_way``.

    Raises
    ------
    InputContractError
        A group is missing, has invalid values, or violates the request contract.

    Limitations
    -----------
    No load, support, bar layout or serviceability acceptance is inferred.
    Mapping and typed inputs pass through the same validation owner.

    Examples
    --------
    See the executable slab recipe in ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """
    return model_validate_or_error(OneWaySlabInputV1, locals())


def input_continuous_one_way(
    *,
    identity: FamilyIdentityV1 | Mapping[str, object],
    geometry: ContinuousOneWaySlabGeometryV1 | Mapping[str, object],
    actions: ContinuousOneWaySlabActionsV1 | Mapping[str, object],
    materials: SlabMaterialsV1 | Mapping[str, object],
    reinforcement: ContinuousOneWaySlabReinforcementV1 | Mapping[str, object],
    serviceability_evidence: SlabServiceabilityEvidenceV1 | Mapping[str, object],
) -> ContinuousOneWaySlabInputV1:
    """Build the supported continuous one way slab request from typed groups.

    Parameters
    ----------
    identity : FamilyIdentityV1 or Mapping[str, object]
        Explicit identity group; units are named on its fields.
    geometry : ContinuousOneWaySlabGeometryV1 or Mapping[str, object]
        Explicit geometry group; units are named on its fields.
    actions : ContinuousOneWaySlabActionsV1 or Mapping[str, object]
        Explicit actions group; units are named on its fields.
    materials : SlabMaterialsV1 or Mapping[str, object]
        Explicit materials group; units are named on its fields.
    reinforcement : ContinuousOneWaySlabReinforcementV1 or Mapping[str, object]
        Explicit reinforcement group; units are named on its fields.
    serviceability_evidence : SlabServiceabilityEvidenceV1 or Mapping[str, object]
        Explicit serviceability evidence group; units are named on its fields.

    Returns
    -------
    ContinuousOneWaySlabInputV1
        Immutable request for ``design_continuous_one_way``.

    Raises
    ------
    InputContractError
        A group is missing, has invalid values, or violates the request contract.

    Limitations
    -----------
    No load, support, bar layout or serviceability acceptance is inferred.
    Mapping and typed inputs pass through the same validation owner.

    Examples
    --------
    See the executable slab recipe in ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """
    return model_validate_or_error(ContinuousOneWaySlabInputV1, locals())


def input_two_way(
    *,
    identity: FamilyIdentityV1 | Mapping[str, object],
    geometry: TwoWaySlabGeometryV1 | Mapping[str, object],
    actions: TwoWaySlabActionsV1 | Mapping[str, object],
    materials: SlabMaterialsV1 | Mapping[str, object],
    reinforcement: TwoWaySlabReinforcementV1 | Mapping[str, object],
    serviceability_evidence: SlabServiceabilityEvidenceV1 | Mapping[str, object],
) -> TwoWaySlabInputV1:
    """Build the supported two way slab request from typed groups.

    Parameters
    ----------
    identity : FamilyIdentityV1 or Mapping[str, object]
        Explicit identity group; units are named on its fields.
    geometry : TwoWaySlabGeometryV1 or Mapping[str, object]
        Explicit geometry group; units are named on its fields.
    actions : TwoWaySlabActionsV1 or Mapping[str, object]
        Explicit actions group; units are named on its fields.
    materials : SlabMaterialsV1 or Mapping[str, object]
        Explicit materials group; units are named on its fields.
    reinforcement : TwoWaySlabReinforcementV1 or Mapping[str, object]
        Explicit reinforcement group; units are named on its fields.
    serviceability_evidence : SlabServiceabilityEvidenceV1 or Mapping[str, object]
        Explicit serviceability evidence group; units are named on its fields.

    Returns
    -------
    TwoWaySlabInputV1
        Immutable request for ``design_two_way``.

    Raises
    ------
    InputContractError
        A group is missing, has invalid values, or violates the request contract.

    Limitations
    -----------
    No load, support, bar layout or serviceability acceptance is inferred.
    Mapping and typed inputs pass through the same validation owner.

    Examples
    --------
    See the executable slab recipe in ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """
    return model_validate_or_error(TwoWaySlabInputV1, locals())


def load_one_way(value: Mapping[str, object] | OneWaySlabInputV1) -> OneWaySlabInputV1:
    """Validate decoded JSON/Python data for the one way slab route.

    Parameters
    ----------
    value : Mapping[str, object] or OneWaySlabInputV1
        Explicit grouped fields. Decode JSON text with ``json.loads`` first.

    Returns
    -------
    OneWaySlabInputV1
        Strict typed request; unknown fields and coerced values are rejected.

    Raises
    ------
    InputContractError
        Invalid intake, wrong request type or unsupported owner inputs.

    Limitations
    -----------
    This route does not generate load combinations or independently approve
    caller-supplied serviceability evidence. Read result limitations before use.

    Examples
    --------
    See the executable slab recipe in ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(OneWaySlabInputV1, value)


def load_continuous_one_way(
    value: Mapping[str, object] | ContinuousOneWaySlabInputV1,
) -> ContinuousOneWaySlabInputV1:
    """Validate decoded JSON/Python data for the continuous one way slab route.

    Parameters
    ----------
    value : Mapping[str, object] or ContinuousOneWaySlabInputV1
        Explicit grouped fields. Decode JSON text with ``json.loads`` first.

    Returns
    -------
    ContinuousOneWaySlabInputV1
        Strict typed request; unknown fields and coerced values are rejected.

    Raises
    ------
    InputContractError
        Invalid intake, wrong request type or unsupported owner inputs.

    Limitations
    -----------
    This route does not generate load combinations or independently approve
    caller-supplied serviceability evidence. Read result limitations before use.

    Examples
    --------
    See the executable slab recipe in ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(ContinuousOneWaySlabInputV1, value)


def load_two_way(value: Mapping[str, object] | TwoWaySlabInputV1) -> TwoWaySlabInputV1:
    """Validate decoded JSON/Python data for the two way slab route.

    Parameters
    ----------
    value : Mapping[str, object] or TwoWaySlabInputV1
        Explicit grouped fields. Decode JSON text with ``json.loads`` first.

    Returns
    -------
    TwoWaySlabInputV1
        Strict typed request; unknown fields and coerced values are rejected.

    Raises
    ------
    InputContractError
        Invalid intake, wrong request type or unsupported owner inputs.

    Limitations
    -----------
    This route does not generate load combinations or independently approve
    caller-supplied serviceability evidence. Read result limitations before use.

    Examples
    --------
    See the executable slab recipe in ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(TwoWaySlabInputV1, value)


def _serviceability_arguments(evidence: SlabServiceabilityEvidenceV1) -> dict[str, Any]:
    return evidence.model_dump(mode="python")


def design_one_way(
    request: OneWaySlabInputV1,
) -> CanonicalFamilyResultV1[CompleteOneWaySlabDesignResult]:
    """Check the supported one way slab with supplied reinforcement.

    Parameters
    ----------
    request : OneWaySlabInputV1
        Typed geometry, loads, materials, bars and reviewed serviceability basis.

    Returns
    -------
    CanonicalFamilyResultV1[CompleteOneWaySlabDesignResult]
        Owner calculation plus engineering status, scope and provenance.
        FAIL is a completed calculation, not an input exception.

    Raises
    ------
    InputContractError
        Invalid intake, wrong request type or unsupported owner inputs.

    Limitations
    -----------
    This route does not generate load combinations or independently approve
    caller-supplied serviceability evidence. Read result limitations before use.

    Examples
    --------
    See the executable slab recipe in ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    require_request_type(request, OneWaySlabInputV1)
    g, a, m, r = (
        request.geometry,
        request.actions,
        request.materials,
        request.reinforcement,
    )
    try:
        calculation = design_complete_one_way_slab_is456(
            short_effective_span_mm=g.short_effective_span_mm,
            long_effective_span_mm=g.long_effective_span_mm,
            thickness_mm=g.thickness_mm,
            d_mm=g.effective_depth_mm,
            strip_width_mm=g.strip_width_mm,
            factored_area_load_kn_per_m2=a.factored_area_load_kn_per_m2,
            fck_n_per_mm2=m.fck_nmm2,
            fy_n_per_mm2=m.fy_nmm2,
            main_bar_diameter_mm=r.main_bar_diameter_mm,
            main_bar_spacing_mm=r.main_bar_spacing_mm,
            distribution_bar_diameter_mm=r.distribution_bar_diameter_mm,
            distribution_bar_spacing_mm=r.distribution_bar_spacing_mm,
            **_serviceability_arguments(request.serviceability_evidence),
        )
    except SlabContractError as error:
        translate_owner_input_error(error)
    flexure = calculation.reinforcement.flexure
    passed = (
        not isinstance(flexure, SlabCapacityFailureResult)
        and calculation.reinforcement.is_detailing_adequate
        and calculation.shear is not None
        and calculation.shear.is_safe_without_shear_reinforcement
        and calculation.serviceability is not None
        and calculation.serviceability.is_satisfied
    )
    return _result(request, calculation, "is456.slab.one-way/v1", passed)


def design_continuous_one_way(
    request: ContinuousOneWaySlabInputV1,
) -> CanonicalFamilyResultV1[ContinuousOneWaySlabDesignResult]:
    """Check the supported continuous one way slab with supplied reinforcement.

    Parameters
    ----------
    request : ContinuousOneWaySlabInputV1
        Typed geometry, loads, materials, bars and reviewed serviceability basis.

    Returns
    -------
    CanonicalFamilyResultV1[ContinuousOneWaySlabDesignResult]
        Owner calculation plus engineering status, scope and provenance.
        FAIL is a completed calculation, not an input exception.

    Raises
    ------
    InputContractError
        Invalid intake, wrong request type or unsupported owner inputs.

    Limitations
    -----------
    This route does not generate load combinations or independently approve
    caller-supplied serviceability evidence. Read result limitations before use.

    Examples
    --------
    See the executable slab recipe in ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    require_request_type(request, ContinuousOneWaySlabInputV1)
    g, a, m, r = (
        request.geometry,
        request.actions,
        request.materials,
        request.reinforcement,
    )
    try:
        calculation = design_continuous_one_way_slab_builtin_is456(
            short_effective_span_mm=g.short_effective_span_mm,
            long_effective_span_mm=g.long_effective_span_mm,
            thickness_mm=g.thickness_mm,
            d_mm=g.effective_depth_mm,
            strip_width_mm=g.strip_width_mm,
            number_of_spans=g.number_of_spans,
            maximum_span_variation_percent=g.maximum_span_variation_percent,
            uniform_cross_section_acknowledged=g.uniform_cross_section_acknowledged,
            factored_dead_and_fixed_imposed_load_kn_per_m2=a.factored_dead_and_fixed_imposed_load_kn_per_m2,
            factored_nonfixed_imposed_load_kn_per_m2=a.factored_nonfixed_imposed_load_kn_per_m2,
            positive_location=a.positive_location,
            negative_location=a.negative_location,
            shear_location=a.shear_location,
            substantially_uniform_load_acknowledged=a.substantially_uniform_load_acknowledged,
            redistribution_applied=a.redistribution_applied,
            fck_n_per_mm2=m.fck_nmm2,
            fy_n_per_mm2=m.fy_nmm2,
            positive_bar_diameter_mm=r.positive_bar_diameter_mm,
            positive_bar_spacing_mm=r.positive_bar_spacing_mm,
            negative_bar_diameter_mm=r.negative_bar_diameter_mm,
            negative_bar_spacing_mm=r.negative_bar_spacing_mm,
            distribution_bar_diameter_mm=r.distribution_bar_diameter_mm,
            distribution_bar_spacing_mm=r.distribution_bar_spacing_mm,
            **_serviceability_arguments(request.serviceability_evidence),
        )
    except SlabContractError as error:
        translate_owner_input_error(error)
    passed = (
        calculation.positive_reinforcement.is_adequate
        and calculation.negative_reinforcement.is_adequate
        and calculation.distribution_reinforcement.is_adequate
        and calculation.shear.is_safe_without_shear_reinforcement
        and calculation.serviceability.is_satisfied
    )
    return _result(request, calculation, "is456.slab.continuous-one-way/v1", passed)


def design_two_way(
    request: TwoWaySlabInputV1,
) -> CanonicalFamilyResultV1[TwoWaySlabPanelWorkflowResult]:
    """Check the supported two way slab with supplied reinforcement.

    Parameters
    ----------
    request : TwoWaySlabInputV1
        Typed geometry, loads, materials, bars and reviewed serviceability basis.

    Returns
    -------
    CanonicalFamilyResultV1[TwoWaySlabPanelWorkflowResult]
        Owner calculation plus engineering status, scope and provenance.
        FAIL is a completed calculation, not an input exception.

    Raises
    ------
    InputContractError
        Invalid intake, wrong request type or unsupported owner inputs.

    Limitations
    -----------
    This route does not generate load combinations or independently approve
    caller-supplied serviceability evidence. Read result limitations before use.

    Examples
    --------
    See the executable slab recipe in ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    require_request_type(request, TwoWaySlabInputV1)
    g, a, m, r = (
        request.geometry,
        request.actions,
        request.materials,
        request.reinforcement,
    )
    try:
        calculation = design_two_way_slab_panel_builtin_is456(
            x_effective_span_mm=g.x_effective_span_mm,
            y_effective_span_mm=g.y_effective_span_mm,
            thickness_mm=g.thickness_mm,
            d_x_mm=g.d_x_mm,
            d_y_mm=g.d_y_mm,
            x_min_edge=g.x_min_edge,
            x_max_edge=g.x_max_edge,
            y_min_edge=g.y_min_edge,
            y_max_edge=g.y_max_edge,
            corner_lift_condition=g.corner_lift_condition,
            factored_area_load_kn_per_m2=a.factored_area_load_kn_per_m2,
            fck_n_per_mm2=m.fck_nmm2,
            fy_n_per_mm2=m.fy_nmm2,
            x_positive_bar_diameter_mm=r.x_positive_bar_diameter_mm,
            x_positive_bar_spacing_mm=r.x_positive_bar_spacing_mm,
            x_negative_bar_diameter_mm=r.x_negative_bar_diameter_mm,
            x_negative_bar_spacing_mm=r.x_negative_bar_spacing_mm,
            y_positive_bar_diameter_mm=r.y_positive_bar_diameter_mm,
            y_positive_bar_spacing_mm=r.y_positive_bar_spacing_mm,
            y_negative_bar_diameter_mm=r.y_negative_bar_diameter_mm,
            y_negative_bar_spacing_mm=r.y_negative_bar_spacing_mm,
            edge_strip_bar_diameter_mm=r.edge_strip_bar_diameter_mm,
            edge_strip_bar_spacing_mm=r.edge_strip_bar_spacing_mm,
            torsion_bar_diameter_mm=r.torsion_bar_diameter_mm,
            torsion_bar_spacing_mm=r.torsion_bar_spacing_mm,
            **_serviceability_arguments(request.serviceability_evidence),
        )
    except SlabContractError as error:
        translate_owner_input_error(error)
    panel = calculation.panel
    passed = (
        not isinstance(panel, SlabCapacityFailureResult)
        and panel.provided_reinforcement_is_adequate
        and panel.shear.is_safe_without_shear_reinforcement
        and calculation.serviceability is not None
        and calculation.serviceability.is_satisfied
    )
    return _result(request, calculation, "is456.slab.two-way/v1", passed)


_SlabResultT = TypeVar("_SlabResultT")


def _result(
    request: StrictPublicModel,
    calculation: _SlabResultT,
    workflow_id: str,
    passed: bool,
) -> CanonicalFamilyResultV1[_SlabResultT]:
    return canonical_family_result(
        request,
        calculation,
        workflow_id=workflow_id,
        engineering_status=EngineeringStatus.PASS if passed else EngineeringStatus.FAIL,
        limitations=(
            "One caller-selected factored load boundary; load combinations and envelopes are not generated.",
            "Direct deflection, crack-width calculation, and automatic slab shear reinforcement remain held.",
        ),
        assumptions=(
            "All topology, coefficient-table route, bars, and reviewed serviceability evidence are explicit.",
        ),
        provenance=("structural_lib.services.slab_api",),
    )
