"""Replay the two 0.28 worked cases from an installed wheel or sdist."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

EXAMPLES = {
    "slab_one_way_reference.py": ("baseline", "capacity-fail", "review-limit-fail"),
    "isolated_footing_reference.py": ("baseline", "transfer-fail", "assumption-hold"),
}


def input_paths(repo: Path) -> tuple[Path, ...]:
    return (
        Path(__file__),
        *(repo / "Python/examples" / name for name in EXAMPLES),
    )


def near(record: dict, field: str, expected: float, *, tolerance: float = 1e-8) -> None:
    actual = record[field]
    if not math.isclose(actual, expected, rel_tol=0, abs_tol=tolerance):
        raise ValueError(f"{field}: {actual!r} differs from {expected!r}")


def verify_slab(cases: dict[str, dict]) -> None:
    # B01: 1 m strip, 3 m effective span, M20/Fe415 and d=125 mm.
    result = cases["baseline"]["result"]
    reinforcement = result["reinforcement"]
    flexure = reinforcement["flexure"]
    detailing = reinforcement["detailing"]
    shear = result["shear"]
    serviceability = result["serviceability"]
    moment = 10 * 3**2 / 8
    stress_block = 0.36 * 20 * 1000
    moment_ratio = moment * 1e6 / stress_block
    neutral_axis = (
        2 * moment_ratio / (125 + math.sqrt(125**2 - 4 * 0.42 * moment_ratio))
    )
    main_area = math.pi * 10**2 / 4 * (1000 / 250)
    distribution_area = math.pi * 8**2 / 4 * (1000 / 250)
    pt = 100 * main_area / (1000 * 125)
    # IS 456 Table 19 M20 at pt 0.25 and 0.50%, and Table 20 M20.
    tau_c = 0.36 + (0.48 - 0.36) * (pt - 0.25) / (0.50 - 0.25)
    near(flexure, "factored_moment_knm", moment, tolerance=1e-12)
    near(flexure, "limiting_moment_knm", stress_block * 60 * (125 - 0.42 * 60) / 1e6)
    near(flexure, "neutral_axis_depth_mm", neutral_axis)
    near(flexure, "ast_required_mm2", stress_block * neutral_axis / (0.87 * 415))
    near(detailing, "main_reinforcement_provided_mm2", main_area)
    near(detailing, "distribution_reinforcement_provided_mm2", distribution_area)
    near(detailing, "distribution_reinforcement_required_mm2", 0.0012 * 1000 * 150)
    near(shear, "tau_v_n_per_mm2", (10 * 3 / 2) * 1000 / (1000 * 125))
    near(shear, "tension_steel_percentage", pt)
    near(shear, "base_tau_c_n_per_mm2", tau_c)
    near(shear, "design_tau_c_n_per_mm2", tau_c * 1.3)
    near(shear, "tau_c_max_n_per_mm2", 2.8 / 2)
    near(serviceability, "actual_span_depth_ratio", 3000 / 125)
    near(serviceability, "reviewed_modified_span_depth_limit", 20 * 1.2)
    near(serviceability, "utilization", 1.0)
    assert shear["status"] == "concrete_capacity_satisfied"
    assert shear["shear_reinforcement_design_status"] == "not_automatically_designed"
    assert serviceability["verified_by_library"] is False
    assert serviceability["direct_deflection_status"].startswith("held_")
    assert serviceability["crack_width_status"].startswith("held_")
    assert result["load_envelope_status"].startswith("not_generated_")
    assert not result["complete_engineering_design_approved"]

    overloaded = cases["capacity-fail"]["result"]
    failure = overloaded["reinforcement"]["flexure"]
    assert failure["result_envelope"]["engineering_status"] == "FAIL"
    assert overloaded["reinforcement"]["detailing"] is None
    assert overloaded["shear"] is None and overloaded["serviceability"] is None
    assert overloaded["punching_shear_disposition"] == (
        "not_evaluated_due_to_flexural_capacity_failure"
    )
    review_limit = cases["review-limit-fail"]["result"]["serviceability"]
    assert review_limit["status"] == "limit_exceeded"
    assert review_limit["utilization"] > 1.0


def verify_footing(cases: dict[str, dict]) -> None:
    # INDIA-1C: service and factored concentric loads act on the same square.
    positive = cases["baseline"]
    result = positive["result"]
    side = math.sqrt(800 / 200) * 1000
    q_uls = 1200 * 1000 / side**2
    column_side = 400.0
    depth = 400.0
    projection = (side - column_side) / 2
    moment = q_uls * side * projection**2 / 2 / 1e6
    shear_kN = q_uls * side * (projection - depth) / 1000
    punching_side = column_side + depth
    punching_force = q_uls * (side**2 - punching_side**2) / 1000
    bottom_steel = 13 * math.pi * 12**2 / 4
    pt = 100 * bottom_steel / (side * depth)
    # IS 456 Table 19 M25 at pt 0.15 and 0.25%; the maximum-shear
    # classification for this footing remains open in the amendment ledger.
    shear_capacity = 0.29 + (0.36 - 0.29) * (pt - 0.15) / (0.25 - 0.15)

    assert (
        result["status"]
        == result["calculation_status"]
        == result["detailing_status"]
        == "PASS"
    )
    near(result, "selected_overall_thickness_mm", 500.0)
    near(result, "selected_effective_depth_L_mm", depth)
    near(result, "selected_effective_depth_B_mm", depth)
    near(result["bearing"], "L_mm", side)
    near(result["bearing"], "B_mm", side)
    near(result["bearing"], "q_max_kPa", 800 / (side / 1000) ** 2)
    near(result["flexure"], "Mu_L_kNm", moment)
    near(result["flexure"], "Mu_B_kNm", moment)
    near(result["one_way_shear"], "Vu_kN", shear_kN)
    near(result["one_way_shear"], "tau_v_nmm2", shear_kN * 1000 / (side * depth))
    near(result["one_way_shear"], "tau_c_nmm2", shear_capacity)
    assert result["one_way_shear_basis"] == "actual_provided_pt_final"
    for direction in result["reinforcement_demands"]:
        near(direction, "provided_steel_area_mm2", bottom_steel)
    near(result["punching"], "perimeter_mm", 4 * punching_side)
    near(result["punching"], "Vu_punch_kN", punching_force)
    near(
        result["punching"],
        "tau_v_nmm2",
        punching_force * 1000 / (4 * punching_side * depth),
    )
    near(result["punching"], "tau_c_nmm2", 0.25 * math.sqrt(25))
    near(result["punching"], "utilization_ratio", 0.63)
    near(
        result["load_transfer"],
        "provided_transfer_steel_area_mm2",
        4 * math.pi * 20**2 / 4,
    )
    near(
        result["load_transfer"],
        "actual_bearing_stress_nmm2",
        1200 * 1000 / column_side**2,
    )
    assert result["qualified_review_required"] is True
    provenance = result["provenance"]
    assert provenance["allowable_soil_pressure_origin"] == "verified"
    assert provenance["allowable_soil_pressure_is_externally_approved"] is True
    assert (
        provenance["allowable_soil_pressure_source_reference"]
        == positive["request"]["allowable_soil_pressure_source_reference"]
    )
    assert (
        provenance["service_load_combination_id"]
        != provenance["factored_load_combination_id"]
    )
    assert provenance["clause_bases"] and provenance["source_ids"]

    transfer_failure = cases["transfer-fail"]["result"]
    assert (
        transfer_failure["status"] == transfer_failure["calculation_status"] == "FAIL"
    )
    assert "load_transfer" in transfer_failure["failed_checks"]
    near(
        transfer_failure["load_transfer"],
        "provided_transfer_steel_area_mm2",
        4 * math.pi * 10**2 / 4,
    )
    held = cases["assumption-hold"]["result"]
    assert held["status"] == "HOLD"
    assert held["provenance"]["allowable_soil_pressure_origin"] == "assumed"
    assert (
        "ASSUMED_BASIS_REQUIRES_VERIFICATION:allowable_soil_pressure_origin"
        in held["hold_reasons"]
    )


def qualify(config: dict[str, Any]) -> dict[str, Any]:
    """Copy the public drivers to a neutral directory and retain their results."""
    repo = Path(config["repo"])
    output = Path(config["output"])
    drivers = Path.cwd() / "slab-footing-drivers"
    drivers.mkdir()
    records = {}
    for name, cases in EXAMPLES.items():
        driver = drivers / name
        shutil.copyfile(repo / "Python/examples" / name, driver)
        observed = {}
        for case in cases:
            completed = subprocess.run(
                [sys.executable, "-I", str(driver), "--case", case],
                cwd=drivers,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if completed.returncode:
                raise ValueError(f"{name} {case} failed: {completed.stderr}")
            payload = json.loads(completed.stdout)
            assert payload["case"] == case
            observed[case] = payload
        verifier = (
            verify_slab if name == "slab_one_way_reference.py" else verify_footing
        )
        verifier(observed)
        filename = f"{driver.stem}.json"
        evidence = output / filename
        evidence.write_text(json.dumps(observed, indent=2, allow_nan=False) + "\n")
        records[name] = {
            "cases": list(cases),
            "driver_sha256": hashlib.sha256(driver.read_bytes()).hexdigest(),
            "evidence": filename,
            "evidence_sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
        }
    return records
