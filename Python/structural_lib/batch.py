# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Batch design helpers for streaming and bulk execution."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from . import api


def _to_float(value: Any, default: float) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _pick_first(params: Mapping[str, Any], keys: list[str], default: Any) -> Any:
    for key in keys:
        if key in params and params[key] not in (None, ""):
            return params[key]
    return default


def _coerce_params(beam: Any) -> dict[str, Any]:
    if isinstance(beam, Mapping):
        return dict(beam)
    if hasattr(beam, "model_dump"):
        return beam.model_dump()
    if hasattr(beam, "dict"):
        return beam.dict()
    return vars(beam)


def _design_single_beam(
    beam_params: Mapping[str, Any],
    idx: int,
    *,
    units: str,
) -> dict[str, Any]:
    width = _to_float(
        _pick_first(beam_params, ["width", "width_mm", "b", "b_mm"], 300.0),
        300.0,
    )
    depth = _to_float(
        _pick_first(beam_params, ["depth", "depth_mm", "D", "D_mm"], 500.0),
        500.0,
    )
    moment = _to_float(
        _pick_first(beam_params, ["moment", "mu_knm", "Mu"], 100.0),
        100.0,
    )
    shear = _to_float(
        _pick_first(beam_params, ["shear", "vu_kn", "Vu"], 50.0),
        50.0,
    )
    fck = _to_float(
        _pick_first(beam_params, ["fck", "fck_mpa", "fck_nmm2"], 25.0),
        25.0,
    )
    fy = _to_float(
        _pick_first(beam_params, ["fy", "fy_mpa", "fy_nmm2"], 500.0),
        500.0,
    )
    cover = _to_float(
        _pick_first(beam_params, ["cover", "cover_mm"], 40.0),
        40.0,
    )
    beam_id = str(
        _pick_first(beam_params, ["id", "beam_id", "beamId"], f"beam_{idx + 1}")
    )

    d_mm = depth - cover - 8.0
    if d_mm <= 0:
        raise ValueError("Effective depth must be positive")

    result = api.design_beam_is456(
        units=units,
        b_mm=float(width),
        D_mm=float(depth),
        d_mm=float(d_mm),
        mu_knm=float(moment),
        vu_kn=float(shear),
        fck_nmm2=float(fck),
        fy_nmm2=float(fy),
    )

    return {
        "beam_id": beam_id,
        "index": idx,
        "input": dict(beam_params),
        "flexure": {
            "ast_required": result.flexure.ast_required,
            "mu_lim": result.flexure.mu_lim,
            "xu": result.flexure.xu,
            "is_safe": result.flexure.is_safe,
        },
        "shear": (
            {
                "tv": result.shear.tv if result.shear else None,
                "tc": result.shear.tc if result.shear else None,
                "is_safe": result.shear.is_safe if result.shear else None,
            }
            if result.shear
            else None
        ),
        "status": "PASS" if result.flexure.is_safe else "FAIL",
    }


def design_beams_iter(
    beams: Iterable[Any],
    *,
    units: str = "IS456",
) -> Iterable[dict[str, Any]]:
    """Yield design results for each beam input.

    Each yielded item is a dict with either:
    - {"success": True, "data": result_dict}
    - {"success": False, "error": {"beam_id", "index", "message"}}
    """
    for idx, beam in enumerate(beams):
        params = _coerce_params(beam)
        try:
            data = _design_single_beam(params, idx, units=units)
            yield {"success": True, "data": data}
        except Exception as exc:  # pragma: no cover - defensive
            beam_id = str(
                _pick_first(params, ["id", "beam_id", "beamId"], f"beam_{idx + 1}")
            )
            yield {
                "success": False,
                "error": {
                    "beam_id": beam_id,
                    "index": idx,
                    "message": str(exc),
                },
            }


def design_beams(
    beams: Iterable[Any],
    *,
    units: str = "IS456",
) -> dict[str, Any]:
    """Design a batch of beams and return results + summary."""
    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for outcome in design_beams_iter(beams, units=units):
        if outcome.get("success"):
            results.append(outcome["data"])
        else:
            errors.append(outcome["error"])

    return {
        "results": results,
        "errors": errors,
        "summary": {
            "total": len(results) + len(errors),
            "passed": sum(1 for r in results if r.get("status") == "PASS"),
            "failed": len(errors),
        },
    }
