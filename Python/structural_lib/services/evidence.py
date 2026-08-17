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
from functools import lru_cache
from pathlib import Path
from typing import Any

from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    IntakeStatus,
    ResultIdentityV1,
    StructuralIssueV1,
    StructuralResultEnvelopeV2,
)
from structural_lib.services.capabilities import (
    IS456_CODE_EDITION,
    get_supported_is456_capabilities,
)
from structural_lib.services.common_api import get_library_version
from structural_lib.services.source_identity import (
    BEAM_STRENGTH_SOURCE_BASIS,
    ControlledSourceBasisV1,
)

BEAM_EVIDENCE_ARTIFACT_SCHEMA = "structural_lib.beam-evidence"
BEAM_EVIDENCE_SCHEMA_VERSION = "3.0"
BEAM_CAPABILITY_ID = "design_beam_is456"
BEAM_RESULT_CONTRACT_VERSION = "canonical-beam-result/v1"
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
        if deflection is None and crack_width is None:
            raise ValueError(
                "Enabled serviceability requires at least one maintained parameter mapping"
            )
        if deflection is not None and not isinstance(deflection, Mapping):
            raise ValueError("deflection_params must be a mapping when supplied")
        if crack_width is not None and not isinstance(crack_width, Mapping):
            raise ValueError("crack_width_params must be a mapping when supplied")
        normalized_deflection = (
            _normalize_nested(deflection) if deflection is not None else None
        )
        if normalized_deflection is not None:
            support = normalized_deflection.get("support_condition")
            if support is not None:
                normalized_deflection["support_condition"] = _SUPPORT_ALIASES.get(
                    support, support
                )
        normalized["deflection_params"] = normalized_deflection
        normalized["crack_width_params"] = (
            _normalize_nested(crack_width) if crack_width is not None else None
        )
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


@lru_cache(maxsize=1)
def get_library_content_identity() -> str:
    """Hash installed package code/data so evidence binds the executing library."""

    package_root = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    paths = sorted(
        path
        for path in package_root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix in {".py", ".json"}
    )
    for path in paths:
        relative = path.relative_to(package_root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        content = path.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _normalize_provenance(value: Any) -> Any:
    """Canonicalize replay metadata without changing its string identity."""

    if isinstance(value, Mapping):
        return {
            str(key): _normalize_provenance(item) for key, item in sorted(value.items())
        }
    if isinstance(value, (list, tuple)):
        return [_normalize_provenance(item) for item in value]
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return float(value)
    return str(value)


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


def build_beam_result_envelope(
    *,
    is_ok: bool,
    evidence: Mapping[str, Any],
) -> StructuralResultEnvelopeV2:
    """Build the one canonical status/identity carrier for the beam route."""

    evidence_status = str(evidence.get("status", "HOLD"))
    issues: tuple[StructuralIssueV1, ...]
    if evidence_status == "HOLD":
        engineering_status = EngineeringStatus.HOLD
        issues = (
            StructuralIssueV1(
                code="BEAM_EVIDENCE_HOLD",
                path="$.evidence",
                message="The beam evidence identity or supported-case basis is held.",
            ),
        )
    elif is_ok:
        engineering_status = EngineeringStatus.PASS
        issues = ()
    else:
        engineering_status = EngineeringStatus.FAIL
        issues = (
            StructuralIssueV1(
                code="BEAM_DESIGN_CHECK_FAILED",
                path="$.calculation",
                message="One or more evaluated beam design checks failed.",
            ),
        )

    source_metadata = evidence.get("source_metadata")
    artifact_sha256 = (
        source_metadata.get("artifact_sha256")
        if isinstance(source_metadata, Mapping)
        and isinstance(source_metadata.get("artifact_sha256"), str)
        else None
    )
    return StructuralResultEnvelopeV2(
        intake_status=IntakeStatus.ACCEPTED,
        calculation_status=CalculationStatus.CALCULATED,
        engineering_status=engineering_status,
        issues=issues,
        result_identity=ResultIdentityV1(
            contract_version=BEAM_RESULT_CONTRACT_VERSION,
            library_version=str(evidence.get("library_version", "UNKNOWN")),
            input_hash=(
                str(evidence["normalized_input_hash"])
                if evidence.get("normalized_input_hash") is not None
                else None
            ),
            calculation_identity=(
                str(evidence["calculation_identity"])
                if evidence.get("calculation_identity") is not None
                else None
            ),
            artifact_sha256=artifact_sha256,
        ),
    )


def build_beam_evidence_envelope(
    *,
    inputs: Mapping[str, Any],
    is_ok: bool,
    governing_utilization: float | None,
    utilizations: Mapping[str, Any] | None = None,
    supported: bool = True,
    generated_at: str | None = None,
    source_metadata: Mapping[str, Any] | None = None,
    source_basis: ControlledSourceBasisV1 = BEAM_STRENGTH_SOURCE_BASIS,
) -> dict[str, Any]:
    """Build the serializable evidence envelope for one beam design result.

    ``supported`` describes route support independently of calculation outcome:
    a supported route may legitimately return ``FAIL``.  A held route returns
    ``HOLD`` and deliberately omits a governing utilization and margin.
    """
    normalized_inputs = normalize_beam_design_inputs(inputs)
    input_hash = _sha256_json(normalized_inputs)
    normalized_provenance = _normalize_provenance(source_metadata or {})
    provenance_hash = _sha256_json(normalized_provenance)
    library_content_identity = get_library_content_identity()
    source_basis_payload = source_basis.to_dict()
    source_basis_hash = _sha256_json(source_basis_payload)
    source_resolved = source_basis.is_resolved
    supported = supported and source_resolved
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
            "library_content_identity": library_content_identity,
            "code_edition": IS456_CODE_EDITION,
            "controlled_source_basis_hash": source_basis_hash,
            "capability_id": BEAM_CAPABILITY_ID,
            "input_hash": input_hash,
            "support_status": "SUPPORTED" if supported else "HELD",
            "governing_check": governing_check,
            "exact_utilization": exact_utilization,
            "status": status,
        }
    )
    replay_receipt = {
        "schema_version": "beam-replay-receipt/v1",
        "normalized_input_hash": input_hash,
        "provenance_hash": provenance_hash,
        "calculation_identity": calculation_identity,
        "library_version": get_library_version(),
        "library_content_identity": library_content_identity,
        "controlled_source_basis_hash": source_basis_hash,
    }
    replay_receipt_hash = _sha256_json(replay_receipt)

    return {
        "artifact_schema": BEAM_EVIDENCE_ARTIFACT_SCHEMA,
        "artifact_schema_version": BEAM_EVIDENCE_SCHEMA_VERSION,
        "library_version": get_library_version(),
        "library_content_identity": library_content_identity,
        "code_edition": IS456_CODE_EDITION,
        "code_amendment_identity": source_basis.amendment_identity,
        "amendment_applicability": source_basis.amendment_applicability.value,
        "amendment_applicability_review_id": source_basis.applicability_review_id,
        "controlled_source_ids": list(source_basis.source_ids),
        "controlled_source_basis_hash": source_basis_hash,
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
        "provenance_hash": provenance_hash,
        "source_metadata": normalized_provenance,
        "calculation_identity": calculation_identity,
        "replay_receipt": replay_receipt,
        "replay_receipt_hash": replay_receipt_hash,
        "governing_check": governing_check,
        "exact_utilization": exact_utilization,
        "margin": None if exact_utilization is None else 1.0 - exact_utilization,
        "status": status,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "qualified_review_required": _beam_qualified_review_required(),
        "qualified_review_requirement": QUALIFIED_REVIEW_REQUIREMENT,
    }
