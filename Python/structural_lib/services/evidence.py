# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Canonical evidence identity for the supported IS 456 beam design route.

This module deliberately identifies the inputs consumed by
``design_beam_is456``.  It is not a certificate or an engineering approval.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from structural_lib.services.capabilities import (
    IS456_CODE_EDITION,
    get_supported_is456_capabilities,
)
from structural_lib.services.common_api import get_library_version

BEAM_EVIDENCE_ARTIFACT_SCHEMA = "structural_lib.beam-evidence"
BEAM_EVIDENCE_SCHEMA_VERSION = "2.0"
BEAM_CAPABILITY_ID = "design_beam_is456"
CODE_AMENDMENT_IDENTITY = "not-declared-in-artifact"
QUALIFIED_REVIEW_REQUIREMENT = (
    "Independent review by a qualified structural engineer is required before "
    "engineering or construction use."
)

_CONSUMED_INPUT_DEFAULTS: dict[str, Any] = {
    "units": "IS456",
    "case_id": "CASE-1",
    "d_dash_mm": 50.0,
    "asv_mm2": 100.0,
    "pt_percent": None,
    "ast_mm2_for_shear": None,
    "tu_knm": 0.0,
    "include_serviceability": False,
}
_REQUIRED_CONSUMED_INPUTS = (
    "mu_knm",
    "vu_kn",
    "b_mm",
    "D_mm",
    "d_mm",
    "fck_nmm2",
    "fy_nmm2",
)

_SUPPORT_ALIASES = {
    "cant": "cantilever",
    "cantilever": "cantilever",
    "cont": "continuous",
    "continuous": "continuous",
    "simply": "simply_supported",
    "simply_supported": "simply_supported",
    "ss": "simply_supported",
}


def _normalize_nested(value: Any) -> Any:
    """Normalize a JSON-compatible calculation input without dropping keys."""
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_nested(item) for key, item in sorted(value.items())
        }
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return float(value)
    return str(value).strip().lower()


def normalize_beam_design_inputs(inputs: Mapping[str, Any]) -> dict[str, Any]:
    """Return the canonical, consumed input subset for beam identity hashing.

    Presentation-only keys are ignored, while every value passed to the
    supported beam design entrypoint is retained.  Numeric values are coerced
    to ``float`` so equivalent JSON number spellings hash identically.
    """
    missing = [name for name in _REQUIRED_CONSUMED_INPUTS if name not in inputs]
    if missing:
        raise ValueError(f"Missing consumed beam inputs: {', '.join(missing)}")

    normalized: dict[str, Any] = {
        "workflow": BEAM_CAPABILITY_ID,
        "units": str(inputs.get("units", _CONSUMED_INPUT_DEFAULTS["units"])),
        "case_id": str(inputs.get("case_id", _CONSUMED_INPUT_DEFAULTS["case_id"])),
    }
    for name in _REQUIRED_CONSUMED_INPUTS + ("d_dash_mm", "asv_mm2"):
        value = inputs.get(name, _CONSUMED_INPUT_DEFAULTS.get(name))
        normalized[name] = float(value)
    for name in ("pt_percent", "ast_mm2_for_shear"):
        value = inputs.get(name, _CONSUMED_INPUT_DEFAULTS[name])
        normalized[name] = None if value is None else float(value)
    normalized["tu_knm"] = float(
        inputs.get("tu_knm", _CONSUMED_INPUT_DEFAULTS["tu_knm"])
    )
    if normalized["tu_knm"] > 0:
        for name in ("cover_mm", "stirrup_dia_mm"):
            if name not in inputs:
                raise ValueError(f"Missing consumed torsion input: {name}")
            normalized[name] = float(inputs[name])
    else:
        normalized["cover_mm"] = None
        normalized["stirrup_dia_mm"] = None

    include_serviceability = inputs.get(
        "include_serviceability",
        _CONSUMED_INPUT_DEFAULTS["include_serviceability"],
    )
    if not isinstance(include_serviceability, bool):
        raise ValueError("include_serviceability must be a boolean")
    normalized["include_serviceability"] = include_serviceability
    if include_serviceability:
        deflection = inputs.get("deflection_params")
        crack_width = inputs.get("crack_width_params")
        if not isinstance(deflection, Mapping) or not isinstance(crack_width, Mapping):
            raise ValueError(
                "Enabled serviceability requires deflection_params and "
                "crack_width_params mappings"
            )
        normalized_deflection = _normalize_nested(deflection)
        support = normalized_deflection.get("support_condition")
        if support is not None:
            normalized_deflection["support_condition"] = _SUPPORT_ALIASES.get(
                support, support
            )
        normalized["deflection_params"] = normalized_deflection
        normalized["crack_width_params"] = _normalize_nested(crack_width)
    else:
        normalized["deflection_params"] = None
        normalized["crack_width_params"] = None
    return normalized


def _sha256_json(value: Mapping[str, Any]) -> str:
    serialized = json.dumps(
        value,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _governing_check(utilizations: Mapping[str, Any]) -> str:
    numeric = []
    for name, value in utilizations.items():
        try:
            numeric.append((str(name), float(value)))
        except (TypeError, ValueError):
            continue
    if not numeric:
        return "combined_compliance"
    return max(numeric, key=lambda item: (item[1], item[0]))[0]


def _beam_qualified_review_required() -> bool:
    """Read the requirement from the canonical supported-case registry."""
    return next(
        capability.qualified_review_required
        for capability in get_supported_is456_capabilities()
        if capability.element == "beam"
    )


def build_beam_evidence_envelope(
    *,
    inputs: Mapping[str, Any],
    is_ok: bool,
    governing_utilization: float | None,
    utilizations: Mapping[str, Any] | None = None,
    supported: bool = True,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build the serializable evidence envelope for one beam design result.

    ``supported`` describes route support independently of calculation outcome:
    a supported route may legitimately return ``FAIL``.  A held route returns
    ``HOLD`` and deliberately omits a governing utilization and margin.
    """
    normalized_inputs = normalize_beam_design_inputs(inputs)
    input_hash = _sha256_json(normalized_inputs)
    exact_utilization = (
        None
        if not supported or governing_utilization is None
        else float(governing_utilization)
    )
    status = "HOLD" if not supported else ("PASS" if is_ok else "FAIL")
    governing_check = _governing_check(utilizations or {})
    calculation_identity = _sha256_json(
        {
            "artifact_schema": BEAM_EVIDENCE_ARTIFACT_SCHEMA,
            "artifact_schema_version": BEAM_EVIDENCE_SCHEMA_VERSION,
            "library_version": get_library_version(),
            "code_edition": IS456_CODE_EDITION,
            "capability_id": BEAM_CAPABILITY_ID,
            "input_hash": input_hash,
            "support_status": "SUPPORTED" if supported else "HELD",
            "governing_check": governing_check,
            "exact_utilization": exact_utilization,
            "status": status,
        }
    )

    return {
        "artifact_schema": BEAM_EVIDENCE_ARTIFACT_SCHEMA,
        "artifact_schema_version": BEAM_EVIDENCE_SCHEMA_VERSION,
        "library_version": get_library_version(),
        "code_edition": IS456_CODE_EDITION,
        "code_amendment_identity": CODE_AMENDMENT_IDENTITY,
        "capability_id": BEAM_CAPABILITY_ID,
        "support_status": "SUPPORTED" if supported else "HELD",
        "unit_system": normalized_inputs["units"],
        "explicit_units": {
            "length": "mm",
            "moment": "kN·m",
            "force": "kN",
            "stress": "N/mm²",
        },
        "normalized_input_hash": input_hash,
        "calculation_identity": calculation_identity,
        "governing_check": governing_check,
        "exact_utilization": exact_utilization,
        "margin": None if exact_utilization is None else 1.0 - exact_utilization,
        "status": status,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "qualified_review_required": _beam_qualified_review_required(),
        "qualified_review_requirement": QUALIFIED_REVIEW_REQUIREMENT,
    }
