# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Import helpers for multi-format CSV ingestion.

These helpers provide a stable, library-first API for dual-file imports
(geometry + forces). They wrap existing adapters and return canonical models.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .adapters import (
    ETABSAdapter,
    GenericCSVAdapter,
    InputAdapter,
    SAFEAdapter,
    STAADAdapter,
)
from structural_lib.core.data_types import ValidationReport
from structural_lib.core.models import BeamBatchInput, BeamForces, BeamGeometry, DesignDefaults


@dataclass(frozen=True)
class ImportWarnings:
    """Warnings produced during import parsing/merge."""

    warnings: list[str]
    unmatched_beams: list[str]
    unmatched_forces: list[str]


def _build_adapters() -> list[InputAdapter]:
    return [ETABSAdapter(), SAFEAdapter(), STAADAdapter(), GenericCSVAdapter()]


def _select_adapter(
    *,
    geometry_csv: Path | str,
    forces_csv: Path | str,
    format_hint: str | None,
) -> InputAdapter:
    format_key = (format_hint or "auto").strip().lower()

    adapter_map: dict[str, InputAdapter] = {
        "etabs": ETABSAdapter(),
        "safe": SAFEAdapter(),
        "staad": STAADAdapter(),
        "generic": GenericCSVAdapter(),
        "auto": GenericCSVAdapter(),
    }

    if format_key in adapter_map and format_key != "auto":
        return adapter_map[format_key]

    # Auto-detect: prefer adapter that can handle either file
    for adapter in _build_adapters():
        if adapter.can_handle(geometry_csv) or adapter.can_handle(forces_csv):
            return adapter

    return GenericCSVAdapter()


def parse_dual_csv(
    geometry_csv: Path | str,
    forces_csv: Path | str,
    *,
    format_hint: str | None = None,
    defaults: DesignDefaults | None = None,
) -> tuple[BeamBatchInput, ImportWarnings]:
    """Parse dual CSV inputs (geometry + forces) into canonical models.

    Args:
        geometry_csv: Path to geometry CSV
        forces_csv: Path to forces CSV
        format_hint: Optional format hint ("etabs", "safe", "staad", "generic")
        defaults: Optional DesignDefaults override

    Returns:
        (BeamBatchInput, ImportWarnings)
    """
    defaults = defaults or DesignDefaults()  # type: ignore[call-arg]
    adapter = _select_adapter(
        geometry_csv=geometry_csv, forces_csv=forces_csv, format_hint=format_hint
    )

    beams = adapter.load_geometry(geometry_csv, defaults)
    forces = adapter.load_forces(forces_csv)

    batch = BeamBatchInput(beams=beams, forces=forces, defaults=defaults)

    unmatched_beams = batch.get_unmatched_beams()
    unmatched_forces = batch.get_unmatched_forces()
    warnings: list[str] = []

    if not beams:
        warnings.append("No geometry records found in geometry CSV")
    if not forces:
        warnings.append("No force records found in forces CSV")
    if unmatched_beams:
        warnings.append(f"{len(unmatched_beams)} beams have no matching forces")
    if unmatched_forces:
        warnings.append(f"{len(unmatched_forces)} forces have no matching beams")

    return batch, ImportWarnings(
        warnings=warnings,
        unmatched_beams=unmatched_beams,
        unmatched_forces=unmatched_forces,
    )


def merge_geometry_forces(
    geometry_list: Iterable[BeamGeometry],
    forces_list: Iterable[BeamForces],
) -> list[tuple[BeamGeometry, BeamForces]]:
    """Merge geometry and forces by beam ID.

    Returns only matched pairs.
    """
    forces_by_id = {force.id: force for force in forces_list}
    return [
        (geom, forces_by_id[geom.id])
        for geom in geometry_list
        if geom.id in forces_by_id
    ]


def validate_import(batch: BeamBatchInput) -> ValidationReport:
    """Validate import results and surface warnings/errors.

    This is a soft validation intended for UI and API layers. It only
    fails when there are zero usable beams.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not batch.beams:
        errors.append("No geometry records found")
    if not batch.forces:
        errors.append("No force records found")

    matched = batch.get_merged_data()
    if not matched:
        errors.append("No matching beam IDs between geometry and forces")

    unmatched_beams = batch.get_unmatched_beams()
    unmatched_forces = batch.get_unmatched_forces()
    if unmatched_beams:
        warnings.append(f"{len(unmatched_beams)} beams have no matching forces")
    if unmatched_forces:
        warnings.append(f"{len(unmatched_forces)} forces have no matching beams")

    details = {
        "total_beams": len(batch.beams),
        "total_forces": len(batch.forces),
        "matched": len(matched),
        "unmatched_beams": unmatched_beams,
        "unmatched_forces": unmatched_forces,
    }

    return ValidationReport(
        ok=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        details=details,
    )
