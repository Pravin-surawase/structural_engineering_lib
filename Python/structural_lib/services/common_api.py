# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       common_api
Description:  Shared validators, utilities and helper functions for the public API.

Split from services/api.py (ARCH-NEW-12) to support domain-based modules.
"""

from __future__ import annotations

import json
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from structural_lib.core.data_types import ValidationReport
from structural_lib.services import beam_pipeline, job_runner

# ============================================================================
# Unit & plausibility validators
# ============================================================================


def _require_is456_units(units: str) -> None:
    beam_pipeline.validate_units(units)


def _validate_plausibility(
    *,
    fck_nmm2: float | None = None,
    fy_nmm2: float | None = None,
    b_mm: float | None = None,
    d_mm: float | None = None,
    D_mm: float | None = None,
) -> None:
    """Catch common unit-confusion mistakes at the API boundary.

    Guards are deliberately generous (e.g. fck ≤ 120 allows UHPC).
    The goal is to catch Pa-vs-MPa and μm-vs-mm mistakes, not to
    enforce IS 456 material limits.
    """
    if fck_nmm2 is not None and fck_nmm2 <= 0:
        raise ValueError(
            f"fck_nmm2={fck_nmm2} must be positive. "
            "Concrete strength cannot be zero or negative."
        )
    if fck_nmm2 is not None and fck_nmm2 > 120:
        raise ValueError(
            f"fck_nmm2={fck_nmm2} seems too large. "
            "Expected N/mm² (e.g., 25), not Pa or kPa."
        )
    if fy_nmm2 is not None and fy_nmm2 <= 0:
        raise ValueError(
            f"fy_nmm2={fy_nmm2} must be positive. "
            "Steel strength cannot be zero or negative."
        )
    if fy_nmm2 is not None and fy_nmm2 > 700:
        raise ValueError(
            f"fy_nmm2={fy_nmm2} seems too large. "
            "Expected N/mm² (e.g., 415), not Pa or kPa."
        )
    if b_mm is not None and b_mm > 5000:
        raise ValueError(
            f"b_mm={b_mm} seems too large. " "Expected mm (e.g., 300), not μm or m."
        )
    if d_mm is not None and d_mm > 5000:
        raise ValueError(
            f"d_mm={d_mm} seems too large. " "Expected mm (e.g., 450), not μm or m."
        )
    if D_mm is not None and D_mm > 5000:
        raise ValueError(
            f"D_mm={D_mm} seems too large. " "Expected mm (e.g., 500), not μm or m."
        )
    if d_mm is not None and D_mm is not None and d_mm >= D_mm:
        raise ValueError(
            f"Effective depth d_mm ({d_mm}) must be less than overall depth "
            f"D_mm ({D_mm}). Per IS 456 Cl 26.4.1, "
            f"d = D − clear_cover − stirrup_dia − bar_dia/2. "
            f"Typical: d ≈ D − 40 to D − 60 mm."
        )


# ============================================================================
# Version & validation utilities
# ============================================================================


def get_library_version() -> str:
    """Return the installed package version.

    Returns:
        Package version string. Falls back to a default when package metadata
        is unavailable (e.g., running from a source checkout).
    """
    try:
        return version("structural-lib-is456")
    except PackageNotFoundError:
        pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.strip().startswith("version"):
                    return line.split("=", 1)[1].strip().strip('"')
        return "0.0.0-dev"


def validate_job_spec(path: str | Path) -> ValidationReport:
    """Validate a job.json specification file.

    Returns a ValidationReport with errors/warnings and summary details.
    """
    try:
        spec = job_runner.load_job_spec(path)
    except Exception as exc:
        return ValidationReport(ok=False, errors=[str(exc)])

    details = {
        "schema_version": spec.get("schema_version"),
        "job_id": spec.get("job_id"),
        "code": spec.get("code"),
        "units": spec.get("units"),
        "beam_keys": sorted(spec.get("beam", {}).keys()),
        "cases_count": len(spec.get("cases", [])),
    }
    return ValidationReport(ok=True, details=details)


def _beam_has_geometry(beam: dict[str, Any]) -> bool:
    geom = beam.get("geometry")
    if isinstance(geom, dict):
        if all(k in geom for k in ("b_mm", "D_mm", "d_mm")):
            return True
        if all(k in geom for k in ("b", "D", "d")):
            return True
    return all(k in beam for k in ("b", "D", "d"))


def _beam_has_materials(beam: dict[str, Any]) -> bool:
    mats = beam.get("materials")
    if isinstance(mats, dict):
        return any(k in mats for k in ("fck_nmm2", "fck")) and any(
            k in mats for k in ("fy_nmm2", "fy")
        )
    return any(k in beam for k in ("fck_nmm2", "fck")) and any(
        k in beam for k in ("fy_nmm2", "fy")
    )


def _beam_has_loads(beam: dict[str, Any]) -> bool:
    loads = beam.get("loads")
    if isinstance(loads, dict):
        return any(k in loads for k in ("mu_knm", "Mu")) and any(
            k in loads for k in ("vu_kn", "Vu")
        )
    return any(k in beam for k in ("mu_knm", "Mu")) and any(
        k in beam for k in ("vu_kn", "Vu")
    )


def validate_design_results(path: str | Path) -> ValidationReport:
    """Validate a design results JSON file (single or multi-beam)."""
    errors: list[str] = []
    warnings: list[str] = []

    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        return ValidationReport(ok=False, errors=[str(exc)])

    if not isinstance(data, dict):
        return ValidationReport(
            ok=False, errors=["Results file must be a JSON object."]
        )

    schema_version = data.get("schema_version")
    if schema_version is None:
        errors.append("Missing required field 'schema_version'.")
    else:
        try:
            schema_version_int = int(schema_version)
            if schema_version_int != beam_pipeline.SCHEMA_VERSION:
                errors.append(
                    f"Unsupported schema_version: {schema_version_int} "
                    f"(expected {beam_pipeline.SCHEMA_VERSION})."
                )
        except (ValueError, TypeError):
            errors.append(f"Invalid schema_version: {schema_version!r}.")

    code = data.get("code")
    if not code:
        errors.append("Missing required field 'code'.")

    units = data.get("units")
    if not units:
        warnings.append("Missing 'units' field (recommended for stable outputs).")

    beams = data.get("beams")
    if not isinstance(beams, list) or not beams:
        errors.append("Missing or empty 'beams' list.")
        beams = []

    for idx, beam in enumerate(beams):
        if not isinstance(beam, dict):
            errors.append(f"Beam {idx}: expected object, got {type(beam).__name__}.")
            continue
        if not beam.get("beam_id"):
            errors.append(f"Beam {idx}: missing 'beam_id'.")
        if not beam.get("story"):
            errors.append(f"Beam {idx}: missing 'story'.")
        if not _beam_has_geometry(beam):
            errors.append(f"Beam {idx}: missing geometry fields.")
        if not _beam_has_materials(beam):
            errors.append(f"Beam {idx}: missing material fields.")
        if not _beam_has_loads(beam):
            errors.append(f"Beam {idx}: missing load fields.")

    details = {
        "schema_version": schema_version,
        "code": code,
        "units": units,
        "beams_count": len(beams),
    }

    return ValidationReport(
        ok=not errors, errors=errors, warnings=warnings, details=details
    )
