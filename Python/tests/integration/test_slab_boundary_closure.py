# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Executable INDIA-1D slab serviceability, shear and load boundaries."""

from __future__ import annotations

import dataclasses
import inspect
import json

import pytest

from structural_lib.codes.is456.slab.shear import (
    SlabShearInput,
    SlabShearStatus,
    check_solid_slab_one_way_shear,
)
from structural_lib.services import api


def _complete_simply_supported(**overrides: object):
    values: dict[str, object] = {
        "short_effective_span_mm": 3000.0,
        "long_effective_span_mm": 7500.0,
        "thickness_mm": 150.0,
        "d_mm": 125.0,
        "factored_area_load_kn_per_m2": 10.0,
        "fck_n_per_mm2": 20.0,
        "fy_n_per_mm2": 415.0,
        "main_bar_diameter_mm": 10.0,
        "main_bar_spacing_mm": 250.0,
        "distribution_bar_diameter_mm": 8.0,
        "distribution_bar_spacing_mm": 250.0,
        "reviewed_base_span_depth_limit": 20.0,
        "reviewed_aggregate_modification_factor": 1.2,
        "serviceability_limit_source_reference": "reviewed-limit:INDIA-1D",
        "serviceability_limit_source_is_approved": True,
        "qualified_serviceability_acceptance_reference": "review:INDIA-1D",
        "qualified_serviceability_acceptance_acknowledged": True,
    }
    values.update(overrides)
    return api.design_complete_one_way_slab_is456(**values)  # type: ignore[arg-type]


def test_complete_route_serializes_explicit_retained_boundaries() -> None:
    result = _complete_simply_supported()

    assert result.serviceability.is_satisfied is True
    assert result.serviceability.verified_by_library is False
    assert result.serviceability.direct_deflection_status.startswith(
        "held_requires_slab_specific_service_actions"
    )
    assert result.serviceability.crack_width_status.startswith(
        "held_requires_explicit_bar_geometry"
    )
    assert result.shear.is_safe_without_shear_reinforcement is True
    assert result.shear.shear_reinforcement_design_status == (
        "not_automatically_designed"
    )
    assert result.load_envelope_status == (
        "not_generated_single_caller_supplied_factored_udl_or_coefficient_basis"
    )
    json.dumps(dataclasses.asdict(result))


def test_ordinary_shear_failure_never_claims_automatic_reinforcement() -> None:
    result = check_solid_slab_one_way_shear(
        SlabShearInput(
            factored_shear_kn=100.0,
            strip_width_mm=1000.0,
            effective_depth_mm=115.0,
            overall_depth_mm=140.0,
            fck_n_per_mm2=20.0,
            tension_reinforcement_mm2=300.0,
            uniformly_distributed_load_only=True,
            beam_or_wall_supported=True,
        )
    )

    assert result.status in {
        SlabShearStatus.INCREASE_DEPTH_OR_ENGINEER_REINFORCEMENT,
        SlabShearStatus.EXCEEDS_MAXIMUM_SHEAR_STRESS,
    }
    assert result.is_safe_without_shear_reinforcement is False
    assert result.shear_reinforcement_design_status == "not_automatically_designed"


def test_public_slab_routes_have_no_hidden_load_or_geometry_envelope_inputs() -> None:
    forbidden_fragments = (
        "load_cases",
        "load_envelope",
        "concentrated",
        "opening",
        "service_load",
    )
    workflows = (
        "design_one_way_slab_is456",
        "design_complete_one_way_slab_is456",
        "design_continuous_one_way_slab_is456",
        "design_continuous_one_way_slab_builtin_is456",
        "design_two_way_slab_is456",
        "design_two_way_slab_panel_is456",
        "design_two_way_slab_panel_builtin_is456",
    )

    for workflow in workflows:
        parameters = inspect.signature(getattr(api, workflow)).parameters
        assert not any(
            fragment in parameter
            for parameter in parameters
            for fragment in forbidden_fragments
        )

    with pytest.raises(TypeError, match="concentrated_load_kn"):
        _complete_simply_supported(concentrated_load_kn=25.0)


def test_capability_and_semantic_contract_state_the_decision_ceiling() -> None:
    slab = next(
        item
        for item in api.get_supported_is456_capabilities()
        if item.element == "solid_slab"
    )
    holds = " ".join(slab.held_cases)

    assert "slab-specific route" in holds
    assert "service steel stress or strain" in holds
    assert "one caller-selected factored UDL" in holds
    assert "never automatically designs slab shear reinforcement" in holds

    complete_workflows = {
        "design_complete_one_way_slab_is456",
        "design_continuous_one_way_slab_is456",
        "design_continuous_one_way_slab_builtin_is456",
        "design_two_way_slab_panel_is456",
        "design_two_way_slab_panel_builtin_is456",
    }
    contracts = {
        item.workflow: " ".join(item.limitations)
        for item in api.get_supported_is456_semantic_contract().workflows
        if item.workflow in complete_workflows
    }
    assert set(contracts) == complete_workflows
    assert all("load" in limitations.lower() for limitations in contracts.values())
    assert all(
        "direct deflection" in limitations.lower() for limitations in contracts.values()
    )
    assert all("shear" in limitations.lower() for limitations in contracts.values())
