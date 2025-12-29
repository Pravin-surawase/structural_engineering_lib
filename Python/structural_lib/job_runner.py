"""job_runner

Minimal batch/job runner for automation workflows.

Design constraints:
- Deterministic outputs (no timestamps in file contents).
- Explicit units at the boundary.
- No ETABS/Excel dependencies: purely file-in/file-out.

v1 scope:
- One beam per job file.
- Multiple cases/combos per job.
- Outputs: JSON + CSV in a stable folder layout.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from . import api
from . import compliance
from . import beam_pipeline


def load_job_json(path: str | Path) -> Dict[str, Any]:
    """Load a job file (JSON)."""

    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("job.json must contain a JSON object at top level")
    return data


def load_job_spec(path: str | Path) -> Dict[str, Any]:
    """Load and validate a job spec file, returning the beam geometry and metadata.

    This is used by both job_runner and report modules to load job.json.

    Args:
        path: Path to job.json file

    Returns:
        Dict with validated job spec containing:
        - job_id: str
        - schema_version: int
        - code: str
        - units: str (validated)
        - beam: dict with geometry (b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2, etc.)
        - cases: list of load cases

    Raises:
        FileNotFoundError: If job.json doesn't exist
        ValueError: If job.json is malformed or missing required fields
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Job file not found: {path}")

    job = load_job_json(p)

    # Validate schema_version
    schema_version = job.get("schema_version")
    if schema_version is None:
        raise ValueError(
            "Missing required field 'schema_version' in job file. Expected: 1."
        )
    try:
        schema_version_int = int(schema_version)
    except (ValueError, TypeError):
        raise ValueError(
            f"Invalid schema_version: '{schema_version}'. Expected integer (currently supported: 1)."
        )
    if schema_version_int != 1:
        raise ValueError(
            f"Unsupported schema_version: {schema_version_int}. Currently supported: 1."
        )

    # Validate code
    code = str(job.get("code", "") or "")
    if not code:
        raise ValueError("Missing required field 'code' in job file.")

    # Validate job_id
    job_id = str(job.get("job_id", "") or "")
    if job_id.strip() == "":
        raise ValueError("job_id is required")

    # Validate beam
    beam = job.get("beam")
    if not isinstance(beam, dict):
        raise ValueError("beam must be an object")

    # Validate cases
    cases = job.get("cases")
    if not isinstance(cases, list):
        raise ValueError("cases must be an array")

    # Validate units
    units_input = str(job.get("units", "") or "")
    try:
        units = beam_pipeline.validate_units(units_input)
    except beam_pipeline.UnitsValidationError as e:
        raise ValueError(f"units validation failed: {e}") from e

    return {
        "job_id": job_id,
        "schema_version": schema_version_int,
        "code": code,
        "units": units,
        "beam": beam,
        "cases": cases,
    }


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _fmt_cell(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, float):
        # repr() is deterministic across supported CPython versions.
        return repr(v)
    return str(v)


def _write_csv(
    path: Path, rows: Iterable[Mapping[str, Any]], fieldnames: list[str]
) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: _fmt_cell(r.get(k)) for k in fieldnames})


def run_job_is456(
    *,
    job: Dict[str, Any],
    out_dir: str | Path,
    copy_inputs: bool = True,
) -> Dict[str, Any]:
    """Run a single-beam IS456 job and write outputs.

    Returns a small run summary (useful for callers/tests).
    """

    schema_version = job.get("schema_version")
    if schema_version is None:
        raise ValueError(
            "Missing required field 'schema_version' in job file. Expected: 1."
        )
    try:
        schema_version_int = int(schema_version)
    except (ValueError, TypeError):
        raise ValueError(
            f"Invalid schema_version: '{schema_version}'. Expected integer (currently supported: 1)."
        )
    if schema_version_int != 1:
        raise ValueError(
            f"Unsupported schema_version: {schema_version_int}. Currently supported: 1."
        )

    code = str(job.get("code", "") or "")
    if code != "IS456":
        raise ValueError(f"v1 runner supports only code='IS456'. Got: '{code}'.")

    units_input = str(job.get("units", "") or "")

    # Validate units at application boundary (TASK-061)
    # Use canonical units in all downstream outputs
    try:
        units = beam_pipeline.validate_units(units_input)
    except beam_pipeline.UnitsValidationError as e:
        raise ValueError(f"units validation failed: {e}") from e

    job_id = str(job.get("job_id", "") or "")
    if job_id.strip() == "":
        raise ValueError("job_id is required")

    beam = job.get("beam")
    if not isinstance(beam, dict):
        raise ValueError("beam must be an object")

    cases = job.get("cases")
    if not isinstance(cases, list):
        raise ValueError("cases must be an array")

    out_root = Path(out_dir)

    inputs_dir = out_root / "inputs"
    parsed_dir = out_root / "parsed"
    design_dir = out_root / "design"
    deliverables_dir = out_root / "deliverables"
    logs_dir = out_root / "logs"

    for d in (inputs_dir, parsed_dir, design_dir, deliverables_dir, logs_dir):
        _ensure_dir(d)

    # Inputs
    if copy_inputs:
        _write_json(inputs_dir / "job.json", job)

    # Parsed (minimal split; future-proof for ETABS parsing)
    _write_json(parsed_dir / "beam.json", beam)
    _write_json(parsed_dir / "cases.json", cases)

    report = api.check_beam_is456(
        units=units,
        cases=cases,
        b_mm=float(beam["b_mm"]),
        D_mm=float(beam["D_mm"]),
        d_mm=float(beam["d_mm"]),
        fck_nmm2=float(beam["fck_nmm2"]),
        fy_nmm2=float(beam["fy_nmm2"]),
        d_dash_mm=float(beam.get("d_dash_mm", 50.0)),
        asv_mm2=float(beam.get("asv_mm2", 100.0)),
        pt_percent=(
            float(beam["pt_percent"]) if beam.get("pt_percent") is not None else None
        ),
        deflection_defaults=(
            beam.get("deflection_defaults")
            if isinstance(beam.get("deflection_defaults"), dict)
            else None
        ),
        crack_width_defaults=(
            beam.get("crack_width_defaults")
            if isinstance(beam.get("crack_width_defaults"), dict)
            else None
        ),
    )

    # Canonical machine output
    design_results = compliance.report_to_dict(report)
    design_results["job"] = {
        "job_id": job_id,
        "schema_version": schema_version,
        "code": code,
        "units": units,
    }
    _write_json(design_dir / "design_results.json", design_results)

    # Excel-friendly compact summary
    rows = []
    for c in report.cases:
        rows.append(
            {
                "job_id": job_id,
                "case_id": c.case_id,
                "is_ok": c.is_ok,
                "governing_utilization": c.governing_utilization,
                "util_flexure": c.utilizations.get("flexure"),
                "util_shear": c.utilizations.get("shear"),
                "util_deflection": c.utilizations.get("deflection"),
                "util_crack_width": c.utilizations.get("crack_width"),
                "remarks": c.remarks,
            }
        )

    fieldnames = [
        "job_id",
        "case_id",
        "is_ok",
        "governing_utilization",
        "util_flexure",
        "util_shear",
        "util_deflection",
        "util_crack_width",
        "remarks",
    ]
    _write_csv(design_dir / "compliance_summary.csv", rows, fieldnames)

    # Small return summary
    return {
        "job_id": job_id,
        "out_dir": str(out_root),
        "is_ok": report.is_ok,
        "governing_case_id": report.governing_case_id,
        "governing_utilization": report.governing_utilization,
        "num_cases": len(report.cases),
    }


def run_job(
    *,
    job_path: str | Path,
    out_dir: str | Path,
) -> Dict[str, Any]:
    """Dispatch job runner based on job['code']."""

    job = load_job_json(job_path)
    code = str(job.get("code", "") or "").strip()
    if code == "IS456":
        return run_job_is456(job=job, out_dir=out_dir)

    if not code:
        raise ValueError(
            "Missing required field 'code' in job file. "
            "Currently supported: 'IS456'."
        )
    raise ValueError(f"Unsupported code: '{code}'. Currently supported: 'IS456'.")
