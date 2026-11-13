"""Replay the slab and footing worked cases from an installed wheel or sdist."""

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
    "slab_coefficient_references.py": (
        "b02-external",
        "b02-builtin",
        "b02-redistribution",
        "b04-external",
        "b04-builtin",
        "b04-topology-conflict",
        "b04-capacity-fail",
    ),
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


def verify_slab_coefficients(cases: dict[str, dict]) -> None:
    """Check the frozen B02/B04 slab ledger for both coefficient sources."""
    load_boundary = (
        "not_generated_single_caller_supplied_factored_udl_or_coefficient_basis"
    )

    for case in ("b02-external", "b02-builtin"):
        result = cases[case]["result"]
        flexure = result["flexure"]
        for region, moment, steel in (
            ("positive_midspan", 10.6875, 270.835),
            ("negative_support", 12.825, 328.665),
        ):
            near(flexure[region], "factored_moment_knm_per_m", moment, tolerance=1e-12)
            near(flexure[region], "ast_required_mm2_per_m", steel, tolerance=0.001)
        near(flexure, "factored_shear_kn_per_m", 17.1, tolerance=1e-12)
        near(result["shear"], "tau_v_n_per_mm2", 0.148, tolerance=0.001)
        built_in = case == "b02-builtin"
        assert flexure["coefficient_correctness_verified_by_library"] is built_in
        if built_in:
            assert flexure["input"]["coefficients"]["table_id"] == "IS456_TABLE_12_13"

    for case in ("b04-external", "b04-builtin"):
        result = cases[case]["result"]
        panel = result["panel"]
        for region, moment in (
            ("x_negative", 18.6),
            ("x_positive", 13.888),
            ("y_negative", 11.656),
            ("y_positive", 8.68),
        ):
            near(panel[region], "factored_moment_knm_per_m", moment, tolerance=0.01)
        near(panel["shear"], "tau_v_n_per_mm2", 31 / 125, tolerance=1e-12)
        corner_torsion = panel["corner_torsion"]
        assert [corner["torsion_class"] for corner in corner_torsion] == [
            "full",
            "half",
            "half",
            "none",
        ]
        near(corner_torsion[0], "zone_extent_from_each_edge_mm", 800, tolerance=1e-12)
        built_in = case == "b04-builtin"
        assert panel["coefficient_correctness_verified_by_library"] is built_in
        if built_in:
            coefficients = panel["input"]["coefficients"]
            assert coefficients["case_id"] == "table_26_case_4"
            assert coefficients["method"] == "built_in_exact"
            assert coefficients["interpolation_bounds"] == [1.5, 1.5]

    for case in ("b02-external", "b02-builtin", "b04-external", "b04-builtin"):
        result = cases[case]["result"]
        assert result["load_envelope_status"] == load_boundary
        assert not result["complete_engineering_design_approved"]
        serviceability = result["serviceability"]
        assert serviceability["direct_deflection_status"].startswith("held_")
        assert serviceability["crack_width_status"].startswith("held_")

    assert "redistribution_applied" in cases["b02-redistribution"]["rejection"]
    assert "must match" in cases["b04-topology-conflict"]["rejection"]
    overloaded = cases["b04-capacity-fail"]["result"]
    panel = overloaded["panel"]
    assert panel["status"] == panel["result_envelope"]["engineering_status"] == "FAIL"
    assert panel["governing_region"] == "x_negative_continuous_edge"
    assert overloaded["serviceability"] is None
    assert overloaded["load_envelope_status"] == load_boundary
    assert not overloaded["complete_engineering_design_approved"]


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
    verifiers = {
        "slab_one_way_reference.py": verify_slab,
        "isolated_footing_reference.py": verify_footing,
        "slab_coefficient_references.py": verify_slab_coefficients,
    }
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
        verifiers[name](observed)
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
