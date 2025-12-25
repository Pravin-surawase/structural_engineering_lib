"""Rebar arrangement optimizer (deterministic).

This module provides a deterministic, bounded search that converts a required
steel area (Ast) into a buildable bar arrangement under simple spacing rules.

Design goals:
- Deterministic: same inputs -> same result
- Explicit units: all lengths in mm, areas in mm^2
- No hidden defaults: constraints are parameters

Note: This is intentionally "Level A" constructability. It currently checks
horizontal bar spacing using the same helper functions used by the detailing
module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Literal, Optional, Tuple

import math

from .detailing import (
    BarArrangement,
    STANDARD_BAR_DIAMETERS,
    calculate_bar_spacing,
    check_min_spacing,
)


Objective = Literal["min_area", "min_bar_count", "max_spacing"]


@dataclass(frozen=True)
class RebarOptimizerResult:
    is_feasible: bool
    arrangement: Optional[BarArrangement]
    objective: Objective
    candidates_considered: int
    checks: Dict[str, Any]
    remarks: str


def _bar_area_mm2(dia_mm: float) -> float:
    return math.pi * (dia_mm / 2.0) ** 2


def _spacing_ok(
    *,
    b_mm: float,
    cover_mm: float,
    stirrup_dia_mm: float,
    bar_dia_mm: float,
    bars_in_layer: int,
    agg_size_mm: float,
) -> Tuple[bool, float, str]:
    spacing = calculate_bar_spacing(
        b_mm, cover_mm, stirrup_dia_mm, bar_dia_mm, bars_in_layer
    )
    ok, msg = check_min_spacing(spacing, bar_dia_mm, agg_size_mm)
    return ok, float(spacing), msg


def optimize_bar_arrangement(
    *,
    ast_required_mm2: float,
    b_mm: float,
    cover_mm: float,
    stirrup_dia_mm: float = 8.0,
    allowed_dia_mm: Optional[Iterable[float]] = None,
    max_layers: int = 2,
    objective: Objective = "min_area",
    agg_size_mm: float = 20.0,
    min_total_bars: int = 2,
    max_bars_per_layer: Optional[int] = None,
) -> RebarOptimizerResult:
    """Find a feasible bar arrangement.

    Args:
        ast_required_mm2: Required Ast in mm^2.
        b_mm: Beam width in mm.
        cover_mm: Clear cover in mm.
        stirrup_dia_mm: Stirrup diameter in mm.
        allowed_dia_mm: Iterable of allowable main bar diameters in mm.
        max_layers: Maximum number of layers (1..max_layers).
        objective: Selection objective.
        agg_size_mm: Maximum aggregate size in mm (for min spacing check).
        min_total_bars: Minimum total bars to provide.
        max_bars_per_layer: Optional hard cap on bars per layer.

    Returns:
        RebarOptimizerResult with either a feasible BarArrangement or a structured
        failure.
    """

    if b_mm <= 0 or cover_mm < 0 or stirrup_dia_mm <= 0:
        return RebarOptimizerResult(
            is_feasible=False,
            arrangement=None,
            objective=objective,
            candidates_considered=0,
            checks={
                "inputs": {
                    "b_mm": b_mm,
                    "cover_mm": cover_mm,
                    "stirrup_dia_mm": stirrup_dia_mm,
                }
            },
            remarks="Invalid geometry inputs.",
        )

    if max_layers < 1:
        return RebarOptimizerResult(
            is_feasible=False,
            arrangement=None,
            objective=objective,
            candidates_considered=0,
            checks={"inputs": {"max_layers": max_layers}},
            remarks="max_layers must be >= 1.",
        )

    if ast_required_mm2 <= 0:
        # Keep behavior explicit: return the minimum nominal arrangement.
        arrangement = BarArrangement(
            count=min_total_bars,
            diameter=12.0,
            area_provided=round(min_total_bars * _bar_area_mm2(12.0), 0),
            spacing=0.0,
            layers=1,
        )
        return RebarOptimizerResult(
            is_feasible=True,
            arrangement=arrangement,
            objective=objective,
            candidates_considered=1,
            checks={"note": "ast_required_mm2 <= 0; returned minimum arrangement"},
            remarks="OK",
        )

    diameters: List[float] = (
        list(allowed_dia_mm)
        if allowed_dia_mm is not None
        else list(STANDARD_BAR_DIAMETERS)
    )
    diameters = sorted({float(d) for d in diameters})

    candidates_considered = 0
    feasible: List[
        Tuple[Tuple[float, float, float, float, float], BarArrangement, Dict[str, Any]]
    ] = []

    for dia_mm in diameters:
        if dia_mm <= 0:
            continue

        bar_area = _bar_area_mm2(dia_mm)
        count_needed = max(min_total_bars, int(math.ceil(ast_required_mm2 / bar_area)))

        for layers in range(1, max_layers + 1):
            bars_per_layer = int(math.ceil(count_needed / layers))

            if max_bars_per_layer is not None and bars_per_layer > max_bars_per_layer:
                candidates_considered += 1
                continue

            ok, spacing_mm, spacing_msg = _spacing_ok(
                b_mm=b_mm,
                cover_mm=cover_mm,
                stirrup_dia_mm=stirrup_dia_mm,
                bar_dia_mm=dia_mm,
                bars_in_layer=bars_per_layer,
                agg_size_mm=agg_size_mm,
            )
            candidates_considered += 1

            if not ok:
                continue

            area_provided = count_needed * bar_area
            arrangement = BarArrangement(
                count=count_needed,
                diameter=float(dia_mm),
                area_provided=round(area_provided, 0),
                spacing=round(spacing_mm, 0),
                layers=layers,
            )

            # Deterministic scoring with explicit tie-breakers.
            # Keep a stable score shape for type-checking and reproducibility.
            if objective == "min_area":
                score = (
                    float(area_provided),
                    float(layers),
                    float(count_needed),
                    float(dia_mm),
                    0.0,
                )
            elif objective == "min_bar_count":
                score = (
                    float(count_needed),
                    float(layers),
                    float(area_provided),
                    float(dia_mm),
                    0.0,
                )
            elif objective == "max_spacing":
                score = (
                    -float(spacing_mm),
                    float(area_provided),
                    float(layers),
                    float(count_needed),
                    float(dia_mm),
                )
            else:
                raise ValueError(f"Unknown objective: {objective}")

            checks: Dict[str, Any] = {
                "inputs": {
                    "ast_required_mm2": ast_required_mm2,
                    "b_mm": b_mm,
                    "cover_mm": cover_mm,
                    "stirrup_dia_mm": stirrup_dia_mm,
                    "agg_size_mm": agg_size_mm,
                    "max_layers": max_layers,
                    "min_total_bars": min_total_bars,
                    "max_bars_per_layer": max_bars_per_layer,
                },
                "candidate": {
                    "bar_dia_mm": float(dia_mm),
                    "count": int(count_needed),
                    "layers": int(layers),
                    "bars_per_layer": int(bars_per_layer),
                    "spacing_mm": float(spacing_mm),
                    "spacing_check": spacing_msg,
                },
            }

            feasible.append((score, arrangement, checks))

    if not feasible:
        return RebarOptimizerResult(
            is_feasible=False,
            arrangement=None,
            objective=objective,
            candidates_considered=candidates_considered,
            checks={
                "inputs": {
                    "ast_required_mm2": ast_required_mm2,
                    "b_mm": b_mm,
                    "cover_mm": cover_mm,
                    "stirrup_dia_mm": stirrup_dia_mm,
                    "agg_size_mm": agg_size_mm,
                    "max_layers": max_layers,
                    "min_total_bars": min_total_bars,
                    "max_bars_per_layer": max_bars_per_layer,
                }
            },
            remarks=(
                "No feasible bar layout found within constraints "
                f"(candidates_considered={candidates_considered})."
            ),
        )

    feasible.sort(key=lambda item: item[0])
    best_score, best_arrangement, best_checks = feasible[0]

    # Small, stable explanation payload.
    best_checks["selection"] = {
        "objective": objective,
        "score": best_score,
        "candidates_considered": candidates_considered,
        "feasible_candidates": len(feasible),
    }

    return RebarOptimizerResult(
        is_feasible=True,
        arrangement=best_arrangement,
        objective=objective,
        candidates_considered=candidates_considered,
        checks=best_checks,
        remarks="OK",
    )
