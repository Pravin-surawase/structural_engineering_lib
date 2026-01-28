# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Rebar configuration validation and application helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from .codes.is456 import detailing
from .data_types import ValidationReport
from .visualization.geometry_3d import (
    Point3D,
    RebarPath,
    RebarSegment,
    StirrupLoop,
    compute_rebar_positions,
    compute_stirrup_path,
    compute_stirrup_positions,
)


def _coerce_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "model_dump"):
        return value.model_dump()  # type: ignore[no-any-return]
    if hasattr(value, "dict"):
        return value.dict()  # type: ignore[no-any-return]
    return vars(value)  # type: ignore[no-any-return]


def _pick(params: Mapping[str, Any], keys: list[str], default: Any) -> Any:
    for key in keys:
        if key in params and params[key] not in (None, ""):
            return params[key]
    return default


def _to_float(value: Any, default: float) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def validate_rebar_config(
    beam: Any,
    config: Mapping[str, Any],
) -> ValidationReport:
    """Validate a rebar configuration against basic geometry checks.

    Returns ValidationReport with warnings/errors suitable for UI consumption.
    """
    beam_params = _coerce_mapping(beam)
    cfg = dict(config)

    errors: list[str] = []
    warnings: list[str] = []

    b_mm = _to_float(_pick(beam_params, ["b_mm", "width_mm", "width", "b"], 0.0), 0.0)
    d_mm = _to_float(_pick(beam_params, ["D_mm", "depth_mm", "depth", "D"], 0.0), 0.0)
    cover_mm = _to_float(_pick(beam_params, ["cover_mm", "cover"], 40.0), 40.0)
    stirrup_dia_mm = _to_float(
        _pick(cfg, ["stirrup_dia_mm", "stirrup_dia", "stirrup_dia"], 8.0),
        8.0,
    )

    bar_count = int(_pick(cfg, ["bar_count", "bars", "count"], 0) or 0)
    bar_dia_mm = _to_float(_pick(cfg, ["bar_dia_mm", "bar_dia", "diameter"], 0.0), 0.0)
    layers = int(_pick(cfg, ["layers", "layer_count"], 1) or 1)
    agg_size_mm = _to_float(_pick(cfg, ["agg_size_mm", "agg_size"], 20.0), 20.0)

    if b_mm <= 0 or d_mm <= 0:
        errors.append("Beam width/depth must be positive")
    if bar_count <= 0:
        errors.append("bar_count must be positive")
    if bar_dia_mm <= 0:
        errors.append("bar_dia_mm must be positive")
    if layers <= 0:
        errors.append("layers must be at least 1")

    available_width = b_mm - 2 * (cover_mm + stirrup_dia_mm) - bar_dia_mm
    if available_width <= 0:
        errors.append("No available width for bars (check cover/stirrup/bar dia)")

    edge_distance = cover_mm + stirrup_dia_mm + bar_dia_mm / 2
    if edge_distance * 2 >= d_mm:
        errors.append("Bars do not fit within depth given cover/stirrup/bar dia")

    spacing_mm = None
    if bar_count > 1:
        try:
            spacing_mm = detailing.calculate_bar_spacing(
                b=b_mm,
                cover=cover_mm,
                stirrup_dia=stirrup_dia_mm,
                bar_dia=bar_dia_mm,
                bar_count=bar_count,
            )
            ok, msg = detailing.check_min_spacing(spacing_mm, bar_dia_mm, agg_size_mm)
            if not ok:
                warnings.append(msg)
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(str(exc))

    details = {
        "b_mm": b_mm,
        "D_mm": d_mm,
        "cover_mm": cover_mm,
        "stirrup_dia_mm": stirrup_dia_mm,
        "bar_count": bar_count,
        "bar_dia_mm": bar_dia_mm,
        "layers": layers,
        "spacing_mm": spacing_mm,
    }

    return ValidationReport(
        ok=len(errors) == 0, errors=errors, warnings=warnings, details=details
    )


def apply_rebar_config(
    beam: Any,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply a rebar configuration and return geometry + validation.

    This is a lightweight helper intended for UI preview and editor workflows.
    """
    report = validate_rebar_config(beam, config)
    if not report.ok:
        return {
            "success": False,
            "message": "Invalid rebar configuration",
            "validation": report.to_dict(),
            "geometry": None,
        }

    beam_params = _coerce_mapping(beam)
    cfg = dict(config)

    b_mm = _to_float(
        _pick(beam_params, ["b_mm", "width_mm", "width", "b"], 300.0), 300.0
    )
    d_mm = _to_float(
        _pick(beam_params, ["D_mm", "depth_mm", "depth", "D"], 500.0), 500.0
    )
    cover_mm = _to_float(_pick(beam_params, ["cover_mm", "cover"], 40.0), 40.0)
    span_mm = _to_float(
        _pick(beam_params, ["span_mm", "span", "length_mm"], 5000.0), 5000.0
    )

    bar_count = int(_pick(cfg, ["bar_count", "bars", "count"], 2) or 2)
    bar_dia_mm = _to_float(
        _pick(cfg, ["bar_dia_mm", "bar_dia", "diameter"], 16.0), 16.0
    )
    stirrup_dia_mm = _to_float(
        _pick(cfg, ["stirrup_dia_mm", "stirrup_dia", "stirrup_dia"], 8.0),
        8.0,
    )
    layers = int(_pick(cfg, ["layers", "layer_count"], 1) or 1)
    is_top = bool(_pick(cfg, ["is_top", "top"], False))

    stirrup_spacing_start = _to_float(
        _pick(cfg, ["stirrup_spacing_start", "stirrup_spacing"], 150.0),
        150.0,
    )
    stirrup_spacing_mid = _to_float(
        _pick(cfg, ["stirrup_spacing_mid"], 200.0),
        200.0,
    )
    stirrup_spacing_end = _to_float(
        _pick(cfg, ["stirrup_spacing_end"], stirrup_spacing_start),
        stirrup_spacing_start,
    )

    positions = compute_rebar_positions(
        beam_width=b_mm,
        beam_depth=d_mm,
        cover=cover_mm,
        bar_count=bar_count,
        bar_dia=bar_dia_mm,
        stirrup_dia=stirrup_dia_mm,
        is_top=is_top,
        layers=layers,
    )

    rebars: list[RebarPath] = []
    for idx, pos in enumerate(positions):
        start = Point3D(0.0, pos.y, pos.z)
        end = Point3D(span_mm, pos.y, pos.z)
        segment = RebarSegment(start=start, end=end, diameter=bar_dia_mm)
        rebars.append(
            RebarPath(
                bar_id=f"bar_{idx + 1}",
                segments=[segment],
                diameter=bar_dia_mm,
                bar_type="top" if is_top else "bottom",
            )
        )

    stirrup_positions = compute_stirrup_positions(
        span=span_mm,
        stirrup_spacing_start=stirrup_spacing_start,
        stirrup_spacing_mid=stirrup_spacing_mid,
        stirrup_spacing_end=stirrup_spacing_end,
    )

    stirrups: list[StirrupLoop] = []
    for pos_x in stirrup_positions:
        path = compute_stirrup_path(
            beam_width=b_mm,
            beam_depth=d_mm,
            cover=cover_mm,
            stirrup_dia=stirrup_dia_mm,
            position_x=pos_x,
            legs=2,
        )
        stirrups.append(
            StirrupLoop(
                position_x=pos_x,
                path=path,
                diameter=stirrup_dia_mm,
                legs=2,
                hook_type="135",
            )
        )

    ast_provided = bar_count * math.pi * (bar_dia_mm / 2) ** 2

    return {
        "success": True,
        "message": "Rebar configuration applied",
        "ast_provided_mm2": round(ast_provided, 1),
        "validation": report.to_dict(),
        "geometry": {
            "rebars": [bar.to_dict() for bar in rebars],
            "stirrups": [loop.to_dict() for loop in stirrups],
            "metadata": {
                "span_mm": span_mm,
                "bar_count": bar_count,
                "bar_dia_mm": bar_dia_mm,
                "stirrup_dia_mm": stirrup_dia_mm,
            },
        },
    }
