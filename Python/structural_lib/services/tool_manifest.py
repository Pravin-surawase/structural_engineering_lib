# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Deterministic AI-tool descriptors projected from the workflow catalogue."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from structural_lib.services.workflow_catalog import (
    WorkflowCapability,
    get_workflow_catalog,
    serialize_workflow_catalog,
    validate_example_input,
)

MANIFEST_SCHEMA_VERSION = "1.0"
MANIFEST_VERSION = "1.1.0"
_TOOL_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


class ToolManifestError(ValueError):
    """Raised when a requested capability cannot form an approved tool."""


def _tool_name(capability_id: str) -> str:
    name = capability_id.replace(".", "_").replace("-", "_")
    if _TOOL_NAME_PATTERN.fullmatch(name) is None:
        raise ToolManifestError(
            f"Capability ID cannot form a tool name: {capability_id}"
        )
    return name


def _field_schema(field: Any) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "type": "number",
        "title": field.label,
        "description": f"{field.label} in {field.unit}.",
        "x-unit": field.unit,
        "x-semantic-ref": field.semantic_ref,
    }
    if field.default is not None:
        schema["default"] = field.default
    if field.minimum is not None:
        schema["minimum"] = field.minimum
    if field.maximum is not None:
        schema["maximum"] = field.maximum
    if field.choices:
        schema["enum"] = list(field.choices)
    return schema


def _input_schema(capability: WorkflowCapability) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"urn:structural-lib:schema:{capability.request_schema_id}",
        "x-schema-id": capability.request_schema_id,
        "type": "object",
        "additionalProperties": False,
        "required": [
            field.transport_name for field in capability.fields if field.required
        ],
        "properties": {
            field.transport_name: _field_schema(field) for field in capability.fields
        },
    }


def _tool_document(capability: WorkflowCapability) -> dict[str, Any]:
    return {
        "tool_name": _tool_name(capability.capability_id),
        "capability_id": capability.capability_id,
        "capability_version": capability.capability_version,
        "title": capability.title,
        "description": capability.summary,
        "input_schema_id": capability.request_schema_id,
        "input_schema": _input_schema(capability),
        "result_schema_id": capability.result_schema_id,
        "status_semantic_ref": capability.status_semantic_ref,
        "limitations": list(capability.limitations),
        "review_boundary": {
            "qualified_review_required": capability.qualified_review_required,
            "user_acknowledgement_required_before_execution": True,
            "statement": (
                "This descriptor does not authorize autonomous execution. "
                "Outputs remain software evidence requiring qualified engineering review."
            ),
        },
        "execution": {
            "adapter_id": capability.service_adapter_id,
            "allowlisted": True,
            "enabled_by_default": False,
        },
    }


def get_tool_manifest_document(
    capability_ids: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Project selected approved capabilities into a deterministic manifest."""
    catalog = get_workflow_catalog()
    available = {item.capability_id: item for item in catalog.capabilities}
    requested = capability_ids or tuple(sorted(available))
    if len(requested) != len(set(requested)):
        raise ToolManifestError("Duplicate capability requested for tool manifest")
    unknown = sorted(set(requested) - set(available))
    if unknown:
        raise ToolManifestError(f"Unknown capability: {', '.join(unknown)}")
    tools = [_tool_document(available[capability_id]) for capability_id in requested]
    tool_names = [tool["tool_name"] for tool in tools]
    if len(tool_names) != len(set(tool_names)):
        raise ToolManifestError("Capability IDs produce duplicate tool names")
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "manifest_version": MANIFEST_VERSION,
        "manifest_id": "structural-lib.workflow-tools",
        "source": {
            "catalog_schema_version": catalog.schema_version,
            "catalog_version": catalog.catalog_version,
            "catalog_sha256": hashlib.sha256(
                serialize_workflow_catalog().encode("utf-8")
            ).hexdigest(),
        },
        "activation": {
            "model_integration": False,
            "chat_ui": False,
            "autonomous_execution": False,
        },
        "tools": tools,
    }


def serialize_tool_manifest(
    capability_ids: tuple[str, ...] | None = None,
    *,
    indent: int | None = None,
) -> str:
    """Serialize the generated manifest with stable key ordering."""
    separators = None if indent is not None else (",", ":")
    return json.dumps(
        get_tool_manifest_document(capability_ids),
        ensure_ascii=False,
        indent=indent,
        separators=separators,
        sort_keys=True,
    )


def validate_tool_input(capability_id: str, values: dict[str, Any]) -> dict[str, float]:
    """Validate tool inputs through the same canonical catalogue constraints."""
    catalog = get_workflow_catalog()
    capability = next(
        (item for item in catalog.capabilities if item.capability_id == capability_id),
        None,
    )
    if capability is None:
        raise ToolManifestError(f"Unknown capability: {capability_id}")
    validate_example_input(capability, values)
    return {name: float(value) for name, value in values.items()}
