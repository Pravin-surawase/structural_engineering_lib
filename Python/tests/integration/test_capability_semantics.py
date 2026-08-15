# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Cross-layer checks for the supported-workflow semantic contract."""

from __future__ import annotations

import dataclasses
import inspect
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, get_type_hints

import structural_lib
from structural_lib.reports.generator import _normalize_report_context
from structural_lib.services import api as services_api
from structural_lib.services.capabilities import (
    get_supported_is456_capabilities,
    get_supported_is456_semantic_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi_app.models.library_core import (  # noqa: E402
    FootingLoadTransferRequest,
    OneWaySlabDesignRequest,
)


def _adapter(name: str):
    contract = get_supported_is456_semantic_contract()
    return next(adapter for adapter in contract.adapters if adapter.adapter == name)


def _published_field_names(workflow: Callable[..., Any]) -> set[str]:
    """Return public input/result names, including one typed nested level."""
    names = set(inspect.signature(workflow).parameters)
    type_hints = get_type_hints(workflow)
    for parameter_name in inspect.signature(workflow).parameters:
        parameter_type = type_hints.get(parameter_name)
        if parameter_type and dataclasses.is_dataclass(parameter_type):
            names.update(
                f"{parameter_name}.{field.name}"
                for field in dataclasses.fields(parameter_type)
            )
            names.update(
                f"{parameter_name}.{name}"
                for name, value in vars(parameter_type).items()
                if isinstance(value, property) and not name.startswith("_")
            )

    result_type = type_hints.get("return")
    if not result_type or not dataclasses.is_dataclass(result_type):
        return names

    for result_field in dataclasses.fields(result_type):
        names.add(result_field.name)
        nested_type = get_type_hints(result_type).get(result_field.name)
        if nested_type and dataclasses.is_dataclass(nested_type):
            names.update(
                f"{result_field.name}.{field.name}"
                for field in dataclasses.fields(nested_type)
            )
            names.update(
                f"{result_field.name}.{name}"
                for name, value in vars(nested_type).items()
                if isinstance(value, property) and not name.startswith("_")
            )
    return names


def test_capability_workflows_match_semantic_contract_and_public_facades() -> None:
    capabilities = get_supported_is456_capabilities()
    semantic_contract = get_supported_is456_semantic_contract()
    capability_workflows = {
        workflow
        for capability in capabilities
        for workflow in capability.public_workflows
    }
    contract_workflows = {workflow.workflow for workflow in semantic_contract.workflows}

    assert contract_workflows == capability_workflows
    for workflow in contract_workflows:
        assert workflow in services_api.__all__
        assert getattr(structural_lib, workflow) is getattr(services_api, workflow)
        assert workflow in structural_lib.__all__


def test_contract_workflow_field_names_match_public_function_or_result() -> None:
    for workflow_contract in get_supported_is456_semantic_contract().workflows:
        workflow = getattr(services_api, workflow_contract.workflow)
        published_names = _published_field_names(workflow)
        for field in workflow_contract.fields:
            assert field.canonical_name in published_names, (
                f"{workflow_contract.workflow}: {field.canonical_name} is not a "
                "public input or result field"
            )


def test_isolated_footing_capability_includes_bearing_with_review_boundary() -> None:
    footing = next(
        item
        for item in get_supported_is456_capabilities()
        if item.element == "isolated_footing"
    )
    bearing = next(
        item
        for item in get_supported_is456_semantic_contract().workflows
        if item.workflow == "check_bearing_pressure"
    )

    assert "check_bearing_pressure" in footing.public_workflows
    assert footing.qualified_review_required is True
    assert bearing.statuses[0].canonical_name == "is_safe"
    assert "qualified review" in bearing.statuses[0].limitations[0]


def test_batch_contract_matches_canonical_hook_result_field_names() -> None:
    hook_path = REPO_ROOT / "react_app/src/hooks/useBatchDesign.ts"
    hook_text = hook_path.read_text(encoding="utf-8")
    batch_interface = hook_text.split("export interface BatchResult {", 1)[1].split(
        "export type BatchStatus", 1
    )[0]

    for field in _adapter("batch_design_sse").fields:
        assert re.search(
            rf"^\s*{re.escape(field.canonical_name)}\??:",
            batch_interface,
            flags=re.MULTILINE,
        ), field.canonical_name
    assert "tv:" not in batch_interface
    assert "tc:" not in batch_interface


def test_report_context_normalizes_legacy_is_safe_to_one_is_ok_field() -> None:
    normalized = _normalize_report_context(
        {
            "results": {
                "flexure": {"is_safe": True},
                "shear": {"is_safe": False},
            },
            "is_ok": True,
        }
    )
    report_field = _adapter("report_context").fields[0]

    assert report_field.canonical_name == "is_ok"
    assert report_field.legacy_aliases[0].name == "is_safe"
    assert report_field.legacy_aliases[0].deprecated_since == "0.23.0"
    assert report_field.legacy_aliases[0].remove_in == "0.24.0"
    assert normalized["is_ok"] is False
    assert normalized["results"]["flexure"] == {
        "is_ok": True,
        "status_text": "PASS",
        "status_class": "status-pass",
        "status_symbol": "✓",
    }
    assert normalized["results"]["shear"]["is_ok"] is False
    assert "is_safe" not in normalized["results"]["shear"]


def test_fastapi_footing_and_slab_models_match_contract_field_names() -> None:
    request_adapter = _adapter("fastapi_library_core_requests")
    footing_properties = FootingLoadTransferRequest.model_json_schema()["properties"]
    slab_properties = OneWaySlabDesignRequest.model_json_schema()["properties"]
    fields = {field.canonical_name: field for field in request_adapter.fields}

    assert fields["dowel_count"].unit == "count"
    assert fields["dowel_diameter_mm"].unit == "mm"
    assert fields["thickness_mm"].unit == "mm"
    assert {"dowel_count", "dowel_diameter_mm"} <= footing_properties.keys()
    assert "thickness_mm" in slab_properties


def test_slab_compatibility_aliases_are_intentionally_indefinite() -> None:
    slab = next(
        workflow
        for workflow in get_supported_is456_semantic_contract().workflows
        if workflow.workflow == "design_two_way_slab_is456"
    )
    aliases = {
        alias.name: alias for field in slab.fields for alias in field.legacy_aliases
    }

    assert aliases["review_status"].deprecated_since is None
    assert aliases["qualified_coefficient_acceptance_acknowledged"].remove_in is None
    assert aliases["coefficient_correctness_is_verified"].remove_in is None
    assert aliases["is_supported"].remove_in is None
