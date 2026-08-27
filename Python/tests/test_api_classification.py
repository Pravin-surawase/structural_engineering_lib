"""Executable truth checks for the Alpha API classification registry."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

_SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "generate_api_classification.py"
)
_SPEC = importlib.util.spec_from_file_location("generate_api_classification", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
classification = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = classification
_SPEC.loader.exec_module(classification)


def test_every_facade_symbol_has_exactly_one_classification() -> None:
    registry = classification.build_registry()

    for surface in registry["surfaces"]:
        names = [record["name"] for record in surface["symbols"]]
        assert len(names) == len(set(names))
        assert surface["classified_symbol_count"] == len(names)
        assert all(
            record["classification"]
            in {"stable", "preview", "compatibility", "internal"}
            for record in surface["symbols"]
        )
        assert all(
            record["claim_disposition"]
            in {"canonical", "advanced", "compatibility", "hold", "internal"}
            for record in surface["symbols"]
        )


def test_alpha_registry_makes_no_stable_export_promise() -> None:
    registry = classification.build_registry()

    assert registry["release_channel"] == "alpha"
    assert registry["stable_exports"] == []
    for surface in registry["surfaces"]:
        assert all(
            record["classification"] != "stable" for record in surface["symbols"]
        )


def test_public_looking_callable_leakage_is_explicitly_internal() -> None:
    registry = classification.build_registry()

    for surface in registry["surfaces"]:
        for record in surface["symbols"]:
            if not record["declared_export"]:
                assert record["classification"] == "internal"
                assert record["claim_disposition"] == "internal"


def test_canonical_task_api_is_capability_bound_and_artifact_scoped() -> None:
    registry = classification.build_registry()

    assert registry["schema_version"] == "2.0"
    assert registry["claim_surface_matrix_schema_version"] == (
        "claim-surface-matrix/v1"
    )
    assert "design_beam_is456" in registry["canonical_task_exports"]
    assert registry["canonical_journey_ids"] == ["is456.beam.design/v1"]
    assert registry["canonical_support_exports"] == [
        "EffectiveDepthBasisV1",
        "EffectiveDepthResolutionV1",
    ]
    assert registry["artifact_boundaries"]["not_in_wheel"] == [
        "fastapi_app",
        "react_app",
        "clients",
    ]
    journey = registry["canonical_reference_journey"]
    assert journey["task_id"] == "is456.beam.design/v1"
    assert journey["input_contract"] == "beam-design-input/v1"
    assert journey["result_contract"] == (
        "beam-design-result/v1 + structural-result-envelope/v2"
    )
    assert {surface["artifact"] for surface in journey["surfaces"]} == {
        "wheel",
        "exact_head_application",
        "repository_clients",
    }
    assert journey["compatibility_holds"] == [
        {
            "surface": "websocket_design",
            "locator": "/ws/design/{session_id}",
            "condition": "missing structural-result-envelope/v2",
            "outcome": "HOLD",
        }
    ]
    service = next(
        surface
        for surface in registry["surfaces"]
        if surface["module"] == "structural_lib.services.api"
    )
    dispositions = {
        record["name"]: record["claim_disposition"] for record in service["symbols"]
    }
    assert dispositions["design_beam_is456"] == "compatibility"
    assert dispositions["create_jobs_from_etabs_csv"] == "hold"
    facade = next(
        surface
        for surface in registry["surfaces"]
        if surface["module"] == "structural_lib.design.is456.beam"
    )
    facade_dispositions = {
        record["name"]: record["claim_disposition"] for record in facade["symbols"]
    }
    assert facade_dispositions["design"] == "canonical"
    assert facade_dispositions["design_and_detail"] == "canonical"
