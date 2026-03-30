# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Project Bill of Quantities (BOQ) — Aggregation Module

Aggregates BBSDocument data from multiple beams into a project-level BOQ
with steel by diameter/grade, concrete by grade/story, and cost estimates.

Units:
    Steel weight: kg
    Concrete volume: m³
    Dimensions: mm (inputs)
    Cost: ₹ (INR)
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from structural_lib.services.bbs import BBSDocument

# Default concrete costs per m³ (₹/m³) keyed by fck (N/mm²)
DEFAULT_CONCRETE_COSTS: dict[int, float] = {
    25: 6000.0,
    30: 7000.0,
    35: 8000.0,
    40: 9500.0,
}


@dataclass
class SteelSummary:
    """Steel quantities for one grade."""

    grade: str  # "Fe500", "Fe415"
    total_weight_kg: float = 0.0
    weight_by_diameter: dict[float, float] = field(default_factory=dict)
    count_by_diameter: dict[float, int] = field(default_factory=dict)
    cost_inr: float = 0.0


@dataclass
class ConcreteSummary:
    """Concrete quantities for one grade."""

    grade: str  # "M25", "M30"
    total_volume_m3: float = 0.0
    cost_inr: float = 0.0


@dataclass
class StorySummary:
    """Quantities for one story/floor."""

    story: str
    beam_count: int = 0
    steel_kg: float = 0.0
    concrete_m3: float = 0.0
    cost_inr: float = 0.0


@dataclass
class ProjectBOQ:
    """Complete Bill of Quantities for a project."""

    project_name: str
    total_beams: int
    steel: list[SteelSummary]
    concrete: list[ConcreteSummary]
    by_story: list[StorySummary]
    grand_total_steel_kg: float
    grand_total_concrete_m3: float
    grand_total_cost_inr: float


def aggregate_project_boq(
    bbs_documents: list[BBSDocument],
    beam_metadata: list[dict[str, Any]],
    steel_cost_per_kg: float = 60.0,
    concrete_costs: dict[int, float] | None = None,
    project_name: str = "Project",
) -> ProjectBOQ:
    """Aggregate BBS data from multiple beams into a project-level BOQ.

    Args:
        bbs_documents: BBS documents from batch detailing (one per beam).
        beam_metadata: Per-beam metadata dicts with keys:
            story (str), b_mm (float), D_mm (float), span_mm (float),
            fck (int, default 25), steel_grade (str, default "Fe500").
        steel_cost_per_kg: Steel rate in ₹/kg. Default 60.0 (Fe500, India).
        concrete_costs: Mapping {fck: ₹/m³}. Defaults to DEFAULT_CONCRETE_COSTS.
        project_name: Display name for the project.

    Returns:
        ProjectBOQ with aggregated quantities and costs.

    Units:
        Steel: kg, Concrete: m³, Cost: ₹ (INR), Dimensions: mm (inputs).
    """
    if concrete_costs is None:
        concrete_costs = dict(DEFAULT_CONCRETE_COSTS)

    # Accumulators keyed by grade/story
    steel_acc: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "weight": 0.0,
            "by_dia_wt": defaultdict(float),
            "by_dia_ct": defaultdict(int),
        }
    )
    concrete_acc: dict[int, float] = defaultdict(float)
    story_acc: dict[str, dict[str, float]] = defaultdict(
        lambda: {"beam_count": 0, "steel_kg": 0.0, "concrete_m3": 0.0}
    )

    for bbs_doc, meta in zip(bbs_documents, beam_metadata, strict=False):
        story = meta.get("story", "Unknown")
        b_mm = float(meta.get("b_mm", 0))
        d_mm = float(meta.get("D_mm", 0))
        span_mm = float(meta.get("span_mm", 0))
        fck = int(meta.get("fck", 25))
        steel_grade = meta.get("steel_grade", "Fe500")

        # --- Steel from BBS summary ---
        summary = bbs_doc.summary
        beam_steel_kg = summary.total_weight_kg

        acc = steel_acc[steel_grade]
        acc["weight"] += beam_steel_kg
        for dia, wt in summary.weight_by_diameter.items():
            acc["by_dia_wt"][dia] += wt
        for dia, ct in summary.count_by_diameter.items():
            acc["by_dia_ct"][dia] += ct

        # --- Concrete volume: b × D × span (mm³ → m³) ---
        concrete_m3 = (b_mm * d_mm * span_mm) / 1e9
        concrete_acc[fck] += concrete_m3

        # --- Story accumulation ---
        story_acc[story]["beam_count"] += 1
        story_acc[story]["steel_kg"] += beam_steel_kg
        story_acc[story]["concrete_m3"] += concrete_m3

    # --- Build SteelSummary list ---
    steel_list: list[SteelSummary] = []
    total_steel_kg = 0.0
    total_steel_cost = 0.0
    for grade, acc in sorted(steel_acc.items()):
        cost = acc["weight"] * steel_cost_per_kg
        steel_list.append(
            SteelSummary(
                grade=grade,
                total_weight_kg=round(acc["weight"], 2),
                weight_by_diameter=dict(acc["by_dia_wt"]),
                count_by_diameter=dict(acc["by_dia_ct"]),
                cost_inr=round(cost, 2),
            )
        )
        total_steel_kg += acc["weight"]
        total_steel_cost += cost

    # --- Build ConcreteSummary list ---
    concrete_list: list[ConcreteSummary] = []
    total_concrete_m3 = 0.0
    total_concrete_cost = 0.0
    for fck, vol in sorted(concrete_acc.items()):
        rate = concrete_costs.get(fck, 6000.0)
        cost = vol * rate
        concrete_list.append(
            ConcreteSummary(
                grade=f"M{fck}",
                total_volume_m3=round(vol, 4),
                cost_inr=round(cost, 2),
            )
        )
        total_concrete_m3 += vol
        total_concrete_cost += cost

    # --- Build StorySummary list ---
    story_list: list[StorySummary] = []
    for story, data in sorted(story_acc.items()):
        story_steel_cost = data["steel_kg"] * steel_cost_per_kg
        avg_concrete_rate = sum(
            concrete_costs.get(fck, 6000.0) for fck in concrete_acc
        ) / max(len(concrete_acc), 1)
        story_concrete_cost = data["concrete_m3"] * avg_concrete_rate
        story_list.append(
            StorySummary(
                story=story,
                beam_count=int(data["beam_count"]),
                steel_kg=round(data["steel_kg"], 2),
                concrete_m3=round(data["concrete_m3"], 4),
                cost_inr=round(story_steel_cost + story_concrete_cost, 2),
            )
        )

    return ProjectBOQ(
        project_name=project_name,
        total_beams=len(bbs_documents),
        steel=steel_list,
        concrete=concrete_list,
        by_story=story_list,
        grand_total_steel_kg=round(total_steel_kg, 2),
        grand_total_concrete_m3=round(total_concrete_m3, 4),
        grand_total_cost_inr=round(total_steel_cost + total_concrete_cost, 2),
    )
