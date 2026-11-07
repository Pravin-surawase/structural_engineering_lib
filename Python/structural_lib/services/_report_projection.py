# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Explicit beam-result projection shared by calculation and HTML reports."""

from __future__ import annotations

import html
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from structural_lib.core.data_types import ComplianceCaseResult
from structural_lib.services.api_results import DesignAndDetailResult
from structural_lib.services.beam_api import _detailing_result_to_dict


@runtime_checkable
class _LegacyBeamCheck(Protocol):
    """Retained scalar report protocol; missing input/review basis is unavailable."""

    flexure: Any
    shear: Any
    is_ok: bool


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.name
    if is_dataclass(value) and not isinstance(value, type):
        return _plain(asdict(value))
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    return value


def project_beam_report(result: Any) -> dict[str, Any]:
    """Project supported named results without guessing their object shape."""
    # Runtime import avoids the API/facade initialization cycle.
    from structural_lib.services.canonical_beam import (
        BeamDesignAndDetailResultV1,
        BeamDesignResultV1,
    )

    canonical = isinstance(result, (BeamDesignResultV1, BeamDesignAndDetailResultV1))
    legacy_scalar = False
    source: dict[str, Any] = {}
    geometry: dict[str, Any] = {}
    materials: dict[str, Any] = {}
    detail = None
    if canonical:
        design = (
            result.design if isinstance(result, BeamDesignAndDetailResultV1) else result
        )
        calculation = design.calculation
        request = result.request.model_dump(mode="json")
        identity = request["identity"]
        geometry = {
            **request["section"],
            "d_mm": result.request.section.resolved_d_mm(),
        }
        materials = request["materials"]
        if isinstance(result, BeamDesignAndDetailResultV1):
            detail = result.detailing.detailing
        source = {
            "schema_version": result.schema_version,
            "request": request,
            "identity": identity,
            "envelope": result.envelope.to_dict(),
            "limitations": list(design.limitations),
            "assumptions": list(design.assumptions),
            "provenance": list(design.provenance),
        }
    elif isinstance(result, DesignAndDetailResult):
        calculation = result.design
        geometry, materials = dict(result.geometry), dict(result.materials)
        detail = result.detailing
        identity = {
            "member_id": result.beam_id,
            "story": result.story,
            "case_id": getattr(calculation, "case_id", None),
        }
    elif isinstance(result, ComplianceCaseResult):
        calculation = result
        identity = {"case_id": result.case_id}
    elif (
        isinstance(result, _LegacyBeamCheck)
        and type(result.is_ok) is bool
        and isinstance(getattr(result.flexure, "Ast_required", None), (int, float))
        and type(getattr(result.shear, "is_safe", None)) is bool
    ):
        legacy_scalar = True
        calculation = result
        identity = {"case_id": getattr(result, "case_id", None)}
    else:
        raise TypeError(
            "Beam reports require BeamDesignResultV1, BeamDesignAndDetailResultV1, "
            "DesignAndDetailResult or ComplianceCaseResult."
        )

    retained = dict(getattr(calculation, "design_inputs", {}))
    for key in ("b_mm", "D_mm", "d_mm", "d_dash_mm", "span_mm", "cover_mm"):
        if retained.get(key) is not None:
            geometry.setdefault(key, retained[key])
    for key in ("fck_nmm2", "fy_nmm2", "fy_transverse_nmm2"):
        if retained.get(key) is not None:
            materials.setdefault(key, retained[key])
    if not canonical:
        source = {
            "schema_version": type(result).__name__,
            "request": retained,
            "identity": identity,
            "envelope": dict(getattr(calculation, "result_envelope", None) or {}),
        }
    source["effective_depth_resolution"] = getattr(
        calculation, "effective_depth_resolution", None
    )

    flexure, shear = calculation.flexure, calculation.shear
    shear_values = (
        _plain(shear)
        if is_dataclass(shear)
        else {
            name: getattr(shear, name, None)
            for name in ("tau_v", "tau_c", "tau_c_max", "Vus", "spacing", "is_safe")
        }
    )
    section_type = getattr(flexure, "section_type", None)
    flexure_values = {
        "ast_required": flexure.Ast_required,
        "ast_provided": None,
        "section_type": getattr(section_type, "name", None),
        "is_safe": getattr(flexure, "is_safe", None),
    }
    if isinstance(result, ComplianceCaseResult):
        flexure_values["pt_provided"] = flexure.pt_provided
    elif legacy_scalar:
        flexure_values["pt_provided"] = getattr(flexure, "pt_provided", None)
    else:
        flexure_values["beam_type"] = None
    detailing: dict[str, Any]
    if detail is None:
        detailing = {
            "status": "unavailable",
            "reason": (
                "design_only"
                if isinstance(result, (ComplianceCaseResult, BeamDesignResultV1))
                or legacy_scalar
                else "missing_detailing"
            ),
        }
    elif detail.top_bars or detail.bottom_bars:
        detailing = {"status": "available", **_detailing_result_to_dict(detail)}
    else:
        detailing = {
            "status": "unavailable",
            "reason": "no_bar_rows",
            "is_valid": detail.is_valid,
        }

    serviceability = {
        name: _plain(value)
        for name in ("deflection", "crack_width")
        if (value := getattr(calculation, name, None)) is not None
    }
    envelope = source["envelope"]
    engineering = envelope.get("engineering_status")
    if engineering not in {"PASS", "FAIL", "HOLD", "NOT_EVALUATED"}:
        engineering = "PASS" if result.is_ok else "FAIL"
    # Legacy combined results can fail detailing after a successful design.
    if isinstance(result, DesignAndDetailResult) and not result.is_ok:
        engineering = "FAIL"
    is_ok = True if engineering == "PASS" else False if engineering == "FAIL" else None
    serialized = (
        calculation.to_dict() if isinstance(calculation, ComplianceCaseResult) else {}
    )
    summary = {
        "is_ok": is_ok,
        "engineering_status": engineering,
        "failed_checks": list(getattr(calculation, "failed_checks", ())),
        "remarks": getattr(calculation, "remarks", ""),
        "utilizations": serialized.get("utilizations", {}),
        "unavailable_utilizations": serialized.get("unavailable_utilizations", {}),
        "clause_refs": getattr(calculation, "clause_refs", {}),
    }
    if isinstance(result, DesignAndDetailResult):
        summary["summary"] = result.summary()
    loads = [
        {
            "case_id": identity.get("case_id"),
            "mu_knm": getattr(calculation, "Mu_knm", retained.get("mu_knm")),
            "vu_kn": getattr(calculation, "Vu_kn", retained.get("vu_kn")),
            "tu_knm": getattr(calculation, "Tu_knm", retained.get("tu_knm")),
        }
    ]
    return {
        "report_projection_schema_version": "beam-report-projection/v1",
        "source": _plain(source),
        "inputs": {
            "geometry": geometry,
            "materials": materials,
            "loads": loads,
            "detailing": source["request"].get("detailing") or {},
        },
        "results": {
            "flexure": flexure_values,
            "shear": {"Vu_kn": getattr(calculation, "Vu_kn", None), **shear_values},
            "serviceability": serviceability,
            "torsion": _plain(getattr(calculation, "torsion", None)) or {},
            "detailing": detailing,
            "summary": summary,
        },
        "is_ok": is_ok,
    }


def report_evidence_rows(projection: dict[str, Any]) -> list[tuple[str, str]]:
    """Return the retained input/check/review basis for every visible format."""
    source, inputs, results = (
        projection["source"],
        projection["inputs"],
        projection["results"],
    )
    request = source.get("request") or {}
    basis = request
    if "calculation_basis" in request:
        basis = {
            key: request.get(key)
            for key in (
                "calculation_basis",
                "detailing",
                "serviceability",
                "source_provenance",
            )
        }
        basis["effective_depth_basis"] = request.get("section", {}).get(
            "effective_depth_basis"
        )
    envelope = source.get("envelope") or {}
    detail = results["detailing"]
    provided = {
        key: detail[key] for key in ("status", "reason", "is_valid") if key in detail
    }
    for face in ("top_bars", "bottom_bars"):
        if face in detail:
            provided[face] = [
                {
                    key: row.get(key)
                    for key in (
                        "zone",
                        "count",
                        "diameter_mm",
                        "area_provided_mm2",
                        "spacing_mm",
                        "layers",
                    )
                }
                for row in detail[face]
            ]
    values = {
        "Identity": source.get("identity"),
        "Input geometry (mm)": inputs["geometry"],
        "Input materials (N/mm²)": inputs["materials"],
        "Factored actions (kNm, kN)": inputs["loads"],
        "Calculation request and basis": basis,
        "Effective-depth resolution": source.get("effective_depth_resolution"),
        "Required tension steel (mm²)": results["flexure"].get("ast_required"),
        "Provided reinforcement and detailing (mm, mm²)": provided,
        "Evaluated serviceability checks": results["serviceability"] or "NOT EVALUATED",
        "Evaluated torsion check": results.get("torsion") or "NOT EVALUATED",
        "Check outcomes and failure reasons": {
            key: results["summary"].get(key)
            for key in (
                "engineering_status",
                "failed_checks",
                "remarks",
                "utilizations",
            )
        },
        "Result envelope and review requirement": {
            key: envelope.get(key)
            for key in (
                "intake_status",
                "calculation_status",
                "engineering_status",
                "review_status",
                "qualified_review_required",
                "freshness_status",
                "issues",
            )
        },
        "Result identity": envelope.get("result_identity"),
        "Source provenance and limitations": {
            key: source[key]
            for key in ("provenance", "assumptions", "limitations")
            if key in source
        },
    }
    return [
        (
            name,
            (
                "Unavailable"
                if value is None
                else (
                    value
                    if isinstance(value, str)
                    else json.dumps(
                        value, ensure_ascii=False, allow_nan=False, default=str
                    )
                )
            ),
        )
        for name, value in values.items()
    ]


def report_evidence_html(projection: dict[str, Any]) -> str:
    """Render escaped evidence common to fallback, templates and PDF inputs."""
    rows = "".join(
        f"<tr><th>{html.escape(name)}</th><td style='overflow-wrap:anywhere'>{html.escape(value)}</td></tr>"
        for name, value in report_evidence_rows(projection)
    )
    return f"<section class='section'><h2>Calculation basis and verification</h2><table class='data-table'>{rows}</table></section>"


def report_evidence_markdown(projection: dict[str, Any]) -> str:
    """Render the same retained evidence in Markdown."""
    rows = [
        "\n## Calculation basis and verification\n",
        "| Basis | Retained value |",
        "| --- | --- |",
    ]
    rows.extend(
        f"| {name} | {value.replace('|', '&#124;')} |"
        for name, value in report_evidence_rows(projection)
    )
    return "\n".join(rows)


def report_template_context(projection: dict[str, Any]) -> dict[str, Any]:
    """Adapt one projection to the existing named template field vocabulary."""
    from copy import deepcopy

    context = deepcopy(projection)
    inputs, results = context["inputs"], context["results"]
    inputs.update(inputs["geometry"])
    inputs["fck"] = inputs["materials"].get("fck_nmm2")
    inputs["fy"] = inputs["materials"].get("fy_nmm2")
    inputs["materials"].update(fck=inputs["fck"], fy=inputs["fy"])
    results["flexure"].update(
        ast_required_mm2=results["flexure"]["ast_required"],
        ast_provided_mm2=None,
        mu_knm=inputs["loads"][0]["mu_knm"],
    )
    shear = results["shear"]
    shear.update(
        vu_kn=shear["Vu_kn"],
        tv_nmm2=shear.get("tau_v"),
        tc_nmm2=shear.get("tau_c"),
        tc_max_nmm2=shear.get("tau_c_max"),
        sv_required_mm=shear.get("spacing"),
    )
    if not results["torsion"]:
        # An absent optional check is not a missing required safety section.
        results.pop("torsion")
    for name, check in results["serviceability"].items():
        results[name] = dict(check)
        computed = check.get("computed", {})
        if name == "deflection":
            results[name].update(
                ld_actual=computed.get("ld_ratio"),
                ld_allowable=computed.get("allowable_ld"),
            )
        elif name == "crack_width":
            results[name].update(
                wk_mm=computed.get("wk_mm"), wk_limit_mm=computed.get("wk_limit_mm")
            )
    context["report_projection"] = projection
    return context
