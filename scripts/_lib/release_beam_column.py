"""Copied-driver qualification of the selected 0.27 beam/column corpus.

This owner runs inside a fresh archive installation with declared dev/dxf/report
extras. Verification tools are separate from the base-only installed profiles.
No package source or repository conftest is copied into the neutral driver tree.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

TESTS = tuple(
    f"Python/tests/integration/{name}.py"
    for name in (
        "test_beam_comparator_example",
        "test_beam_instantaneous_service",
        "test_beam_finite_service_history",
        "test_beam_unequal_service_history",
        "test_cantilever_beam_check",
        "test_continuous_beam_check",
        "test_beam_continuous_detailing",
        "test_beam_physical_flange_reference",
        "test_signed_beam_section_check",
        "test_beam_section_catalogue",
        "test_layered_column_section",
        "test_beam_section_closure",
        "test_four_corner_column_member",
        "test_tied_rectangular_column_member",
        "test_positioned_rectangular_column_member",
        "test_slender_rectangular_column_member",
        "test_circular_column_member",
        "test_circular_column_detailing",
        "test_column_candidate_search",
        "test_column_interaction_slice",
        "test_column_service_section",
        "test_column_result_transport",
        "test_flexure_edges_additional",
        "test_column_member_detailing",
        "test_column_contact_splice",
        "test_etabs_paired_forces",
        "test_torsion_corner_geometry",
        "test_beam_primary_route_torsion",
        "test_physical_torsion_member",
        "test_beam_edge_torsion",
        "test_torsional_serviceability",
        "test_t_beam_member",
        "test_complete_member_workflow",
        "test_flanged_branch_equilibrium",
        "test_release_027_consumer_repairs",
    )
) + (
    "Python/tests/test_calculation_report.py",
    "Python/tests/test_public_examples.py",
    "Python/tests/unit/test_structural_engineering_wp07.py",
    "Python/tests/unit/test_structural_engineering_wp08.py",
)
EXAMPLES = tuple(
    f"Python/examples/{name}.py"
    for name in (
        "beam_comparator_reference",
        "beam_instantaneous_service",
        "beam_finite_service_history",
        "cantilever_beam_check",
        "continuous_beam_check",
        "beam_continuous_detailing",
        "signed_beam_section_check",
        "beam_section_catalogue",
        "layered_column_section",
        "beam_section_closure",
        "four_corner_column_member",
        "tied_rectangular_column_member",
        "positioned_rectangular_column_member",
        "slender_rectangular_column_member",
        "circular_column_member",
        "circular_column_detailing",
        "column_catalogue_selection",
        "column_interaction_slice",
        "column_service_section",
        "column_member_detailing",
        "etabs_paired_forces",
        "torsion_station_reference",
        "physical_torsion_member",
        "t_beam_member",
        "complete_member_workflow",
        "canonical_workflows",
        "full_pipeline_synthetic",
    )
)
CHECKERS = tuple(
    f"docs/verification/check_library_027_{name}.py"
    for name in (
        "references",
        "beam_section_reference",
        "four_corner_reference",
        "torsion_reference",
        "torsion_physical_reference",
        "torsion_serviceability_reference",
        "t_beam_reference",
    )
) + (
    "docs/verification/check_library_029_beam01_reference.py",
    "docs/verification/check_library_029_beam02_reference.py",
    "docs/verification/check_library_029_beam_sections_reference.py",
    "docs/verification/check_library_029_beam05_reference.py",
    "docs/verification/check_library_029_beam05_flanged_reference.py",
    "docs/verification/check_library_029_beam05_cutoff_reference.py",
    "docs/verification/check_library_029_beam05_lap_reference.py",
    "docs/verification/check_library_029_beam07_reference.py",
    "docs/verification/check_library_029_flow02_reference.py",
    "docs/verification/check_library_029_flow03_beam_reference.py",
    "docs/verification/check_library_030_flow03_two_layer_reference.py",
    "docs/verification/check_library_029_flow04_reference.py",
    "docs/verification/check_library_029_sec02_reference.py",
    "docs/verification/check_library_029_sec03_reference.py",
    "docs/verification/check_library_029_serv01_reference.py",
    "docs/verification/check_library_029_serv02_reference.py",
    "docs/verification/check_library_030_serv02_unequal_span_reference.py",
    "docs/verification/check_library_029_col02_reference.py",
    "docs/verification/check_library_029_col03_reference.py",
    "docs/verification/check_library_029_col04_reference.py",
    "docs/verification/check_library_029_col05_reference.py",
    "docs/verification/check_library_029_col06_reference.py",
    "docs/verification/check_library_029_col07_reference.py",
    "docs/verification/check_library_029_col07_mixed_reference.py",
    "docs/verification/check_library_029_col07_circular_reference.py",
    "docs/verification/check_library_029_col07_slender_reference.py",
    "docs/verification/check_library_029_col07_splice_reference.py",
    "docs/verification/check_library_029_col07_corner_reference.py",
    "docs/verification/check_library_030_beam05_cutoff_reference.py",
    "docs/verification/check_library_030_beam05_lap_reference.py",
    "docs/verification/check_library_030_beam05_t_lap_reference.py",
    "docs/verification/check_library_030_beam05_l_lap_reference.py",
    "docs/verification/check_library_030_beam05_span2_lap_reference.py",
    "docs/verification/check_library_030_beam05_span2_lap_restraint_reference.py",
    "docs/verification/check_library_030_beam05_flanged_lap_restraint_reference.py",
    "docs/verification/check_library_030_beam05_lap_placement_reference.py",
    "docs/verification/check_library_030_beam05_rectangular_lap_placement_reference.py",
    "docs/verification/check_library_030_beam05_support_top_lap_reference.py",
    "docs/verification/check_library_030_beam05_varied_links_reference.py",
    "docs/verification/check_library_030_beam05_haunch_reference.py",
    "docs/verification/check_library_030_beam05_physical_flange_reference.py",
)
BEAM01_REFERENCE = "docs/verification/library-029-beam01-flow01.json"
BEAM02_REFERENCE = "docs/verification/library-029-beam02-cantilever.json"
BEAM_SECTION_REFERENCE = "docs/verification/library-029-beam03-beam04-sections.json"
BEAM05_REFERENCE = "docs/verification/library-029-beam05-member-detailing.json"
BEAM05_FLANGED_REFERENCE = "docs/verification/library-029-beam05-flanged-detailing.json"
BEAM05_CUTOFF_REFERENCE = "docs/verification/library-029-beam05-cutoff.json"
BEAM05_LAYERED_CUTOFF_REFERENCE = (
    "docs/verification/library-030-beam05-layered-cutoff.json"
)
BEAM05_LAYERED_LAP_REFERENCE = "docs/verification/library-030-beam05-layered-lap.json"
BEAM05_T_LAP_REFERENCE = "docs/verification/library-030-beam05-t-lap-reference.json"
BEAM05_L_LAP_REFERENCE = "docs/verification/library-030-beam05-l-lap-reference.json"
BEAM05_SPAN2_LAP_REFERENCE = (
    "docs/verification/library-030-beam05-span2-lap-reference.json"
)
BEAM05_LAP_RESTRAINT_REFERENCE = (
    "docs/verification/library-030-beam05-span2-lap-restraint-reference.json"
)
BEAM05_FLANGED_LAP_RESTRAINT_REFERENCE = (
    "docs/verification/library-030-beam05-flanged-lap-restraint-reference.json"
)
BEAM05_LAP_PLACEMENT_REFERENCE = (
    "docs/verification/library-030-beam05-lap-placement-reference.json"
)
BEAM05_RECTANGULAR_LAP_PLACEMENT_REFERENCE = (
    "docs/verification/library-030-beam05-rectangular-lap-placement-reference.json"
)
BEAM05_SUPPORT_TOP_LAP_REFERENCE = (
    "docs/verification/library-030-beam05-support-top-lap-reference.json"
)
BEAM05_VARIED_LINKS_REFERENCE = "docs/verification/library-030-beam05-varied-links.json"
BEAM05_HAUNCH_REFERENCE = "docs/verification/library-030-beam05-haunch.json"
BEAM05_PHYSICAL_FLANGE_REFERENCE = (
    "docs/verification/library-030-beam05-physical-flange.json"
)
BEAM05_LAP_REFERENCE = "docs/verification/library-029-beam05-lap.json"
BEAM07_REFERENCE = "docs/verification/library-029-beam07-equilibrium-torsion.json"
FLOW02_REFERENCE = "docs/verification/library-029-flow02-beam-catalogue.json"
FLOW03_BEAM_REFERENCE = "docs/verification/library-029-flow03-beam-edit.json"
FLOW03_LAYERED_REFERENCE = "docs/verification/library-030-flow03-two-layer-edit.json"
FLOW03_LAYERED_EXAMPLE = "Python/examples/beam_layered_cage_edit.py"
FLOW03_LAYERED_TEST = (
    "Python/tests/integration/test_beam_layered_cage_edit_reference.py"
)
WORKBENCH_TEST = "Python/tests/integration/test_workbench_beam_layout.py"
SL04_SL05_TEST = "Python/tests/codes/is456/slab/test_built_in_coefficients.py"
SL06_TEST = "Python/tests/integration/test_slab_supplied_actions.py"
SL06_EXAMPLE = "Python/examples/slab_supplied_action_references.py"
SL06_CHECKER = "docs/verification/check_library_030_sl06_reference.py"
SL06_REFERENCE = "docs/verification/library-030-sl06-actions.json"
DUCT01_REFERENCE = "docs/verification/library-030-duct01-interior-joint.json"
DUCT01_CHECKER = "docs/verification/check_library_030_duct01_interior_reference.py"
DUCT01_EXAMPLE = "Python/examples/ductile_interior_joint.py"
DUCT01_TEST = "Python/tests/integration/test_ductile_interior_joint_reference.py"
DUCT02_REFERENCE = "docs/verification/library-030-duct02-exterior-joint.json"
DUCT02_CHECKER = "docs/verification/check_library_030_duct02_exterior_reference.py"
DUCT02_TEST = "Python/tests/integration/test_ductile_exterior_joint_reference.py"
PROJECT03_ACTIONS = "docs/verification/library-030-project03-frame-actions.json"
PROJECT03_REFERENCE = "docs/verification/library-030-project03-ductile-frame.json"
PROJECT03_CHECKER = "docs/verification/check_library_030_project03_frame_reference.py"
PROJECT03_EXAMPLE = "Python/examples/ductile_frame_cut.py"
PROJECT03_TEST = "Python/tests/integration/test_ductile_frame_cut_reference.py"
FLOW04_REFERENCE = "docs/verification/library-029-flow04-paired-intake.json"
SEC02_REFERENCE = "docs/verification/library-029-sec02-column-interaction.json"
SEC03_REFERENCE = "docs/verification/library-029-sec03-column-service.json"
SERV01_REFERENCE = "docs/verification/library-029-serv01-beam-service.json"
SERV02_REFERENCE = "docs/verification/library-029-serv02-beam-history.json"
SERV02_UNEQUAL_REFERENCE = "docs/verification/library-030-serv02-unequal-span.json"
COL03_REFERENCE = "docs/verification/library-029-col03-mixed-column.json"
COL04_REFERENCE = "docs/verification/library-029-col04-slender-column.json"
COL05_REFERENCE = "docs/verification/library-029-col05-circular-column.json"
COL06_REFERENCE = "docs/verification/library-029-col06-column-catalogue.json"
COL07_REFERENCE = "docs/verification/library-029-col07-column-member.json"
COL07_MIXED_REFERENCE = "docs/verification/library-029-col07-mixed-member.json"
COL07_CIRCULAR_REFERENCE = "docs/verification/library-029-col07-circular-member.json"
COL07_SLENDER_REFERENCE = "docs/verification/library-029-col07-slender-member.json"
COL07_SPLICE_REFERENCE = "docs/verification/library-029-col07-contact-splice.json"
COL07_CORNER_REFERENCE = "docs/verification/library-029-col07-corner-splice.json"
COL07_030_REFERENCES = tuple(
    f"docs/verification/library-030-col07-{name}.json"
    for name in (
        "mixed-splice",
        "two-plane-shear",
        "circular-shear",
        "slender-lap-reference",
        "circular-lap-reference",
    )
)
COL07_030_CHECKERS = tuple(
    f"docs/verification/check_library_030_col07_{name}_reference.py"
    for name in (
        "mixed_splice",
        "two_plane_shear",
        "circular_shear",
        "slender_lap",
        "circular_lap",
    )
)
COL07_030_TESTS = tuple(
    f"Python/tests/integration/test_{name}.py"
    for name in (
        "column_mixed_contact_splice",
        "circular_column_shear",
        "column_slender_contact_splice",
        "circular_column_contact_lap",
    )
)


def input_paths(repo: Path) -> tuple[Path, ...]:
    """Exact transitive driver/fixture inventory; never a source-package glob."""
    return tuple(
        sorted(
            {
                *(repo / name for name in (*TESTS, *EXAMPLES, *CHECKERS)),
                *(repo / "docs/verification").glob("library-027-*.json"),
                repo / "docs/verification/library-029-col02-rectangular-column.json",
                repo / BEAM01_REFERENCE,
                repo / BEAM02_REFERENCE,
                repo / BEAM_SECTION_REFERENCE,
                repo / BEAM05_REFERENCE,
                repo / BEAM05_FLANGED_REFERENCE,
                repo / BEAM05_CUTOFF_REFERENCE,
                repo / BEAM05_LAYERED_CUTOFF_REFERENCE,
                repo / BEAM05_LAYERED_LAP_REFERENCE,
                repo / BEAM05_T_LAP_REFERENCE,
                repo / BEAM05_L_LAP_REFERENCE,
                repo / BEAM05_SPAN2_LAP_REFERENCE,
                repo / BEAM05_LAP_RESTRAINT_REFERENCE,
                repo / BEAM05_FLANGED_LAP_RESTRAINT_REFERENCE,
                repo / BEAM05_LAP_PLACEMENT_REFERENCE,
                repo / BEAM05_RECTANGULAR_LAP_PLACEMENT_REFERENCE,
                repo / BEAM05_SUPPORT_TOP_LAP_REFERENCE,
                repo / BEAM05_VARIED_LINKS_REFERENCE,
                repo / BEAM05_HAUNCH_REFERENCE,
                repo / BEAM05_PHYSICAL_FLANGE_REFERENCE,
                repo / BEAM05_LAP_REFERENCE,
                repo / BEAM07_REFERENCE,
                repo / FLOW02_REFERENCE,
                repo / FLOW03_BEAM_REFERENCE,
                repo / FLOW03_LAYERED_REFERENCE,
                repo / FLOW03_LAYERED_EXAMPLE,
                repo / FLOW03_LAYERED_TEST,
                repo / WORKBENCH_TEST,
                repo / SL04_SL05_TEST,
                repo / SL06_TEST,
                repo / SL06_EXAMPLE,
                repo / SL06_CHECKER,
                repo / SL06_REFERENCE,
                *(
                    repo / name
                    for name in (
                        DUCT01_REFERENCE,
                        DUCT01_CHECKER,
                        DUCT01_EXAMPLE,
                        DUCT01_TEST,
                        "docs/verification/_duct01_cage_reference.py",
                        "docs/verification/_duct01_section_reference.py",
                        DUCT02_REFERENCE,
                        DUCT02_CHECKER,
                        DUCT02_TEST,
                        "docs/verification/_duct02_cage_reference.py",
                        PROJECT03_ACTIONS,
                        PROJECT03_REFERENCE,
                        PROJECT03_CHECKER,
                        PROJECT03_EXAMPLE,
                        PROJECT03_TEST,
                        "docs/verification/_project03_frame_statics.py",
                        "docs/verification/_project03_member_reference.py",
                    )
                ),
                repo / FLOW04_REFERENCE,
                repo / SEC02_REFERENCE,
                repo / SEC03_REFERENCE,
                repo / SERV01_REFERENCE,
                repo / SERV02_REFERENCE,
                repo / SERV02_UNEQUAL_REFERENCE,
                repo / COL03_REFERENCE,
                repo / COL04_REFERENCE,
                repo / COL05_REFERENCE,
                repo / COL06_REFERENCE,
                repo / COL07_REFERENCE,
                repo / COL07_MIXED_REFERENCE,
                repo / COL07_SLENDER_REFERENCE,
                repo / COL07_CIRCULAR_REFERENCE,
                repo / COL07_SPLICE_REFERENCE,
                repo / COL07_CORNER_REFERENCE,
                *(
                    repo / name
                    for name in (
                        *COL07_030_REFERENCES,
                        *COL07_030_CHECKERS,
                        *COL07_030_TESTS,
                    )
                ),
                repo / "docs/verification/replay_library_027_members.py",
                repo / "docs/verification/replay_library_027_t_member.py",
                repo / "Python/examples/sample_beam_design.csv",
                repo
                / "Python/tests/data/benchmark_vectors/flanged_branch_reference.json",
                repo
                / "contracts/structural-engineering/conformance/wp01-per-bar-vectors.json",
                repo / "docs/reference/api.md",
                repo / "docs/developers/platform-guide.md",
                repo / "scripts/external_cli_test.py",
                *(
                    repo / "docs/getting-started" / name
                    for name in (
                        "python-quickstart.md",
                        "beginners-guide.md",
                        "colab-workflow.md",
                    )
                ),
            }
        )
    )


def qualify_consumer_journeys(
    config: dict[str, Any], *, drawing: bool = False, pdf: bool = False
) -> dict[str, Any]:
    """Replay the copied developer guide and accepted report controls."""
    import contextlib
    import re
    import shutil
    from dataclasses import replace

    from structural_lib import api
    from structural_lib.reports import generator

    target = Path(config["output"]) / "consumer-journeys"
    target.mkdir(parents=True, exist_ok=True)
    guide = target / "platform-guide.md"
    shutil.copyfile(Path(config["repo"]) / "docs/developers/platform-guide.md", guide)
    blocks = re.findall(r"```python\n(.*?)```", guide.read_text(encoding="utf-8"), re.S)
    namespace: dict[str, Any] = {}
    markers = ["# quick_start_example.py", "# verify_quickstart_outputs"]
    if drawing:
        markers.append("# optional_dxf_export")
    if pdf:
        markers.append("# optional_pdf_export")
    with contextlib.chdir(target):
        for marker in markers:
            block = next(block for block in blocks if marker in block)
            exec(compile(block, str(guide), "exec"), namespace)
    if len(namespace["schedule"].items) != 9:
        raise AssertionError("Developer quickstart schedule changed")
    template_html = (target / "beam_B1_outputs/beam_B1.template.html").read_text(
        encoding="utf-8"
    )
    badge = re.search(
        r'<span class="(?:status-badge [^"]+|status)">\s*([^<]+)', template_html
    )
    if badge is None or badge[1].strip() != "PASS":
        raise AssertionError(
            "Canonical overall report badge disagrees with the source PASS"
        )
    common = dict(
        units="IS456",
        b_mm=300,
        D_mm=500,
        d_mm=444,
        fck_nmm2=25,
        fy_nmm2=500,
        mu_knm=150,
        vu_kn=100,
    )
    controls = {}
    combined = api.design_and_detail_beam_is456(
        **common, beam_id="B-FAIL", story="L1", span_mm=6000, cover_mm=40
    )
    invalid_detail = replace(
        combined.detailing,
        is_valid=False,
        remarks="Controlled source detailing failure",
    )
    invalid_report = api.generate_calculation_report(
        replace(combined, detailing=invalid_detail, is_ok=False)
    )
    invalid_data = invalid_report.to_dict()
    if (
        invalid_data["result_envelope"]["engineering_status"] != "FAIL"
        or "detailing_invalid"
        not in invalid_data["results"]["summary"]["failed_checks"]
    ):
        raise AssertionError(
            "Invalid detailing exported a contradictory aggregate envelope"
        )
    invalid_report.export_json(target / "detailing-failure.json")
    invalid_report.export_html(target / "detailing-failure.html")
    invalid_report.export_markdown(target / "detailing-failure.markdown")
    if pdf:
        from weasyprint import HTML

        HTML(filename=str(target / "detailing-failure.html")).write_pdf(
            target / "detailing-failure.pdf"
        )
    controls["detailing-failure"] = {
        "engineering_status": "FAIL",
        "failed_checks": invalid_report.results.summary["failed_checks"],
    }
    for name, params, expected in (
        ("design-only", {}, "PASS"),
        (
            "deflection-failure",
            {
                "deflection_params": {
                    "span_mm": 10000,
                    "d_mm": 444,
                    "support_condition": "simply_supported",
                    "mf_tension_steel": 0.5,
                }
            },
            "FAIL",
        ),
    ):
        result = api.design_beam_is456(**common, **params)
        report = api.generate_calculation_report(result)
        if report.results.summary["engineering_status"] != expected:
            raise AssertionError(f"{name} report changed engineering status")
        if expected == "FAIL" and report.results.summary["failed_checks"] != [
            "deflection"
        ]:
            raise AssertionError("Evaluated serviceability failure disappeared")
        if (
            report.inputs.loads[0]["mu_knm"] != 150
            or report.inputs.materials["fck_nmm2"] != 25
        ):
            raise AssertionError("Report lost retained action/material basis")
        for fmt in ("json", "html", "markdown"):
            getattr(report, f"export_{fmt}")(target / f"{name}.{fmt}")
        (target / f"{name}.template.html").write_text(
            generator.generate_html_report(result), encoding="utf-8"
        )
        if pdf:
            from weasyprint import HTML

            HTML(filename=str(target / f"{name}.html")).write_pdf(
                target / f"{name}.pdf"
            )
        controls[name] = {
            "engineering_status": expected,
            "failed_checks": report.results.summary["failed_checks"],
        }
    return {
        "status": "PASS",
        "guide_sha256": hashlib.sha256(guide.read_bytes()).hexdigest(),
        "source_status": namespace["result"].engineering_status.value,
        "review_status": namespace["report"].source["envelope"]["review_status"],
        "bbs_rows": len(namespace["schedule"].items),
        "jinja2_available": generator.JINJA2_AVAILABLE,
        "drawing": drawing,
        "pdf": pdf,
        "controls": controls,
        "files": {
            str(path.relative_to(target)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(target.rglob("*"))
            if path.is_file()
        },
    }


def _check_varied_link_replay(
    expected: dict[str, Any], calculation: dict[str, Any]
) -> None:
    if expected.get("transitions"):
        transitions = calculation["link_zones"]["transitions"]
        for actual, target in zip(transitions, expected["transitions"], strict=True):
            for key in ("station_mm", "row_id", "owner_zone_id", "shear_kn"):
                assert actual[key] == target[key]
            for side, reference in zip(
                actual["adjacent"], target["adjacent"], strict=True
            ):
                assert side["zone_id"] == reference["zone_id"]
                assert side["spacing_mm"] == reference["spacing_mm"]
                assert math.isclose(
                    side["capacity_kn"], reference["capacity_kn"], abs_tol=1e-7
                )

    if expected["status"] == "PASS":
        output = calculation["bbs"]["outputs"]["bbs"]
        for zone, target in zip(output["link_zones"], expected["zones"], strict=True):
            assert zone["count"] == target["quantity"]
            assert zone["stations_x_mm"] == target["stations_mm"]
        (link,) = [row for row in output["rows"] if row["role"] == "transverse_link"]
        assert link["scheduled_bar_count"] == expected["bbs"]["link_count"]
        assert math.isclose(
            link["fabrication_cut_length_each_mm"],
            expected["bbs"]["link_cut_mm"],
            abs_tol=1e-7,
        )
        assert math.isclose(
            sum(row["theoretical_mass_kg"] for row in output["rows"]),
            expected["bbs"]["mass_kg"],
            abs_tol=1e-7,
        )


def _check_haunch_replay(expected: dict[str, Any], calculation: dict[str, Any]) -> None:
    if expected["status"] != "PASS":
        return
    haunch = calculation["haunch"]
    for actual, target in zip(haunch["rows"], expected["rows"], strict=True):
        assert actual["row_id"] == target["row_id"]
        for field in (
            "shear_adjustment_kn",
            "shear_capacity_kn",
            "moment_capacity_knm",
        ):
            assert math.isclose(actual[field], target[field], abs_tol=1e-7)
    for actual, target in zip(
        haunch["bend_checks"], expected["bend_checks"], strict=True
    ):
        assert actual["node_id"] == target["node_id"]
        assert actual["link_stations_mm"] == target["link_stations_mm"]
    bbs = calculation["bbs"]["outputs"]["bbs"]
    fields = {row["bar_mark"]: row for row in bbs["rows"]}
    assert len(fields) == len(expected["bbs"]["rows"])
    for cut in expected["bbs"]["rows"]:
        row = fields[cut["bar_mark"]]
        assert row["scheduled_bar_count"] == cut["quantity"]
        assert math.isclose(
            row["fabrication_cut_length_each_mm"], cut["cut_mm"], abs_tol=1e-7
        )
    assert math.isclose(
        bbs["scheduled_steel_mass_kg"], expected["bbs"]["mass_kg"], abs_tol=1e-7
    )


def _check_physical_flange_replay(
    expected: dict[str, Any], result: dict[str, Any]
) -> None:
    if expected["status"] != "PASS":
        code = {
            "web_flange_link_intersection": "BEAM.FLANGE_LINK_CLASH_FAIL",
            "flange_link_closure": "BEAM.FLANGE_CAP_CLOSURE_FAIL",
            "flange_bar_support_development": "BEAM.FLANGE_DEVELOPMENT_FAIL",
            "slab_strip_action_basis": "BEAM.FLANGE_STRIP_ACTIONS_HELD",
            "slab_strip_geometry_revision": "BEAM.FLANGE_STRIP_REVISION_HELD",
        }[expected["check"]]
        assert code in {issue["code"] for issue in result["envelope"]["issues"]}
        return
    calculation = result["calculation"]
    assembly = calculation["physical_flange"]
    engineering = assembly["engineering"]
    strength = engineering["strength"]
    assert strength["governing_rows"]["hogging"] == expected["governing_moment_row"]
    assert strength["governing_rows"]["shear"] == expected["governing_shear_row"]
    for face, capacity in expected["adverse_placement_capacity_knm"].items():
        assert math.isclose(strength["adverse_capacity_knm"][face], capacity)
    for actual, target in zip(
        engineering["strip"]["strip_checks"], expected["strip_checks"], strict=True
    ):
        for key, value in target.items():
            assert (
                actual[key] == value
                if isinstance(value, str)
                else math.isclose(actual[key], value, abs_tol=1e-9)
            )
    assert math.isclose(
        engineering["geometry"]["axial_access_mm"],
        expected["minimum_clearances_mm"]["cap_to_next_main_access_mm"],
    )
    assert math.isclose(
        engineering["geometry"]["flange_hook_plane_clearance_mm"],
        expected["flange_hook_plane_clearance_mm"],
    )
    bbs = calculation["bbs"]["outputs"]["bbs"]
    rows = {row["bar_mark"]: row for row in bbs["rows"]}
    assert len(rows) == len(expected["schedule"])
    for expected_row in expected["schedule"]:
        mark = expected_row["mark"]
        row = rows[mark]
        assert assembly["owners_by_mark"][mark] == expected_row["owner"]
        assert row["scheduled_bar_count"] == expected_row["quantity"]
        assert math.isclose(
            row["fabrication_cut_length_each_mm"], expected_row["cut_length_mm"]
        )
    assert math.isclose(bbs["scheduled_steel_mass_kg"], expected["mass_kg"])


def _check_unequal_service_replay(
    expected: dict[str, Any], result: dict[str, Any]
) -> None:
    status = result["envelope"]["engineering_status"]
    assert status == expected["status"]
    actual = result["calculation"]["history"]
    if "issue" in expected:
        assert expected["issue"] in {
            issue["code"] for issue in result["envelope"]["issues"]
        }
    if status == "HOLD":
        assert actual is None
        return
    for field in (
        "governing_deflection_station_id",
        "governing_after_finishes_station_id",
        "governing_crack_station_id",
    ):
        if field in expected:
            assert actual[field] == expected[field]
    if status != "PASS":
        assert (
            actual["crack_checks"][expected["governing_crack_station_id"]][
                "engineering"
            ]
            == "fail"
        )
        return
    assert {row["row_id"]: row for row in actual["signed_rows"]} == {
        row["row_id"]: row for row in expected["signed_rows"]
    }
    for field in ("span_deflections", "deflection_extrema", "crack_sections"):
        rows = {row["station_id"]: row for row in actual[field]}
        assert len(rows) == len(expected[field])
        for target in expected[field]:
            row = rows[target["station_id"]]
            for key, value in target.items():
                assert (
                    math.isclose(row[key], value, abs_tol=1e-6)
                    if isinstance(value, float)
                    else row[key] == value
                )


def qualify(config: dict[str, Any]) -> dict[str, Any]:
    """Replay all selected references, tests and public drivers from installation."""
    import shutil

    import pytest

    repo, output = Path(config["repo"]), Path(config["output"])
    version_at_least_030 = tuple(map(int, config["version"].split(".")[:2])) >= (0, 30)
    clone = Path.cwd() / "beam-column-drivers"
    hashes = {}
    for source in input_paths(repo):
        relative = source.relative_to(repo)
        target = clone / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        hashes[str(relative)] = hashlib.sha256(source.read_bytes()).hexdigest()
    if (clone / "Python/structural_lib").exists():
        raise AssertionError("Qualification drivers contain package source")
    output.mkdir(parents=True, exist_ok=True)
    commands = []

    def run(label: str, script: str, *args: str, expected_code: int = 0) -> str:
        command = [sys.executable, "-I"]
        if script in (*CHECKERS, *COL07_030_CHECKERS) or script in (
            DUCT01_CHECKER,
            DUCT02_CHECKER,
            PROJECT03_CHECKER,
        ):
            # -I deliberately excludes the script directory. These arithmetic
            # drivers share sibling helpers; expose only their copied folder.
            command.extend(
                (
                    "-c",
                    "import runpy,sys;from pathlib import Path;"
                    "sys.argv=sys.argv[1:];"
                    "sys.path.insert(0,str(Path(sys.argv[0]).parent));"
                    "runpy.run_path(sys.argv[0],run_name='__main__')",
                )
            )
        command.extend((str(clone / script), *args))
        completed = subprocess.run(
            command,
            cwd=clone,
            capture_output=True,
            text=True,
            timeout=300,
        )
        (output / f"{label}.stdout.log").write_text(completed.stdout)
        (output / f"{label}.stderr.log").write_text(completed.stderr)
        if completed.returncode != expected_code:
            raise AssertionError(
                f"Installed {label} failed: {completed.returncode}\n"
                f"{completed.stderr[-4000:]}\n{completed.stdout[-4000:]}"
            )
        commands.append({"id": label, "script": script, "status": "PASS"})
        return completed.stdout

    for checker in CHECKERS:
        run(Path(checker).stem, checker)
    if version_at_least_030:
        run(Path(SL06_CHECKER).stem, SL06_CHECKER)
        for checker in COL07_030_CHECKERS:
            run(Path(checker).stem, checker)
    for profile, reference, example in (
        ("continuous", BEAM01_REFERENCE, "continuous_beam_check"),
        ("cantilever", BEAM02_REFERENCE, "cantilever_beam_check"),
        ("section", BEAM_SECTION_REFERENCE, "signed_beam_section_check"),
    ):
        cases = json.loads((clone / reference).read_text())["cases"]
        for case, entry in cases.items():
            label = f"{profile}-beam-{case}"
            directory = output / label
            expected = entry.get("ultimate_status", entry.get("status", "FAIL"))
            stdout = run(
                label,
                f"Python/examples/{example}.py",
                "--reference",
                str(clone / reference),
                "--case",
                case,
                "--output-dir",
                str(directory),
                expected_code=2 if expected == "BLOCKED" else 0,
            )
            result = json.loads(stdout)
            if expected == "BLOCKED":
                assert result["details"]["issues"]
                assert not directory.exists()
                continue
            assert result["ultimate_status"] == expected
            if "sagging_status" in entry:
                rows = {
                    row["action"]["row_id"]: row["section_status"]
                    for row in result["rows"]
                }
                assert rows["SAG:SECTION"] == entry["sagging_status"]
                assert rows["HOG:SECTION"] == entry["hogging_status"]
            assert result == json.loads((directory / "result.json").read_text())
            identity = result["result_envelope"]["result_identity"]["input_hash"]
            assert identity in (directory / "report.html").read_text()
    for case, entry in json.loads((clone / SEC02_REFERENCE).read_text())[
        "cases"
    ].items():
        label = f"column-interaction-{case}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/column_interaction_slice.py",
            "--reference",
            str(clone / SEC02_REFERENCE),
            "--case",
            case,
            "--output-dir",
            str(directory),
        )
        result = json.loads(stdout)
        assert result["envelope"]["engineering_status"] == entry.get("status", "PASS")
        assert result["calculation"]["member_acceptance"] == "NOT_EVALUATED"
        assert len(result["calculation"]["rays"]) == len(entry.get("rays", ()))
        assert result == json.loads((directory / "result.json").read_text())
        assert (
            result["envelope"]["result_identity"]["input_hash"]
            in (directory / "report.html").read_text()
        )
    for case, entry in json.loads((clone / SEC03_REFERENCE).read_text())[
        "cases"
    ].items():
        label = f"column-service-{case}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/column_service_section.py",
            "--reference",
            str(clone / SEC03_REFERENCE),
            "--case",
            case,
            "--output-dir",
            str(directory),
        )
        result = json.loads(stdout)
        assert result["envelope"]["engineering_status"] == entry["status"]
        assert result["calculation"]["member_acceptance"] == "NOT_EVALUATED"
        assert result == json.loads((directory / "result.json").read_text())
        report = (directory / "report.html").read_text()
        assert result["envelope"]["result_identity"]["input_hash"] in report
        assert "<svg" in report
    for case, entry in json.loads((clone / SERV01_REFERENCE).read_text())[
        "cases"
    ].items():
        label = f"beam-instantaneous-{case}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/beam_instantaneous_service.py",
            "--reference",
            str(clone / SERV01_REFERENCE),
            "--case",
            case,
            "--output-dir",
            str(directory),
        )
        result = json.loads(stdout)
        expected = (
            "HOLD"
            if entry["expected"] is None
            else "FAIL" if case.endswith("tight_limit") else "PASS"
        )
        assert result["envelope"]["engineering_status"] == expected
        assert result["calculation"]["long_term_status"] == "HOLD"
        assert result == json.loads((directory / "result.json").read_text())
        assert (
            result["envelope"]["result_identity"]["input_hash"]
            in (directory / "report.html").read_text()
        )
    for reference in (SERV02_REFERENCE, SERV02_UNEQUAL_REFERENCE):
        for case, entry in json.loads((clone / reference).read_text())["cases"].items():
            label = f"beam-service-history-{case}"
            directory = output / label
            stdout = run(
                label,
                "Python/examples/beam_finite_service_history.py",
                "--reference",
                str(clone / reference),
                "--case",
                case,
                "--output-dir",
                str(directory),
            )
            result = json.loads(stdout)
            if reference == SERV02_UNEQUAL_REFERENCE:
                _check_unequal_service_replay(entry["expected"], result)
            else:
                assert result["envelope"]["engineering_status"] == entry["status"]
            assert result == json.loads((directory / "result.json").read_text())
            assert (
                result["envelope"]["result_identity"]["input_hash"]
                in (directory / "report.html").read_text()
            )
    for reference, profile in (
        (BEAM05_REFERENCE, "beam-continuous-detailing"),
        (BEAM05_CUTOFF_REFERENCE, "beam-continuous-detailing"),
        (BEAM05_LAP_REFERENCE, "beam-continuous-detailing"),
        (BEAM05_FLANGED_REFERENCE, "beam-flanged-detailing"),
        (BEAM05_LAYERED_CUTOFF_REFERENCE, "beam-layered-cutoff"),
        (BEAM05_LAYERED_LAP_REFERENCE, "beam-layered-lap"),
        (BEAM05_LAP_RESTRAINT_REFERENCE, "beam-layered-lap-restraint"),
        (BEAM05_FLANGED_LAP_RESTRAINT_REFERENCE, "beam-flanged-lap-nominal-review"),
        (BEAM05_LAP_PLACEMENT_REFERENCE, "beam-flanged-lap-placement"),
        (BEAM05_RECTANGULAR_LAP_PLACEMENT_REFERENCE, "beam-rectangular-lap-placement"),
        (BEAM05_SUPPORT_TOP_LAP_REFERENCE, "beam-support-top-lap"),
        (BEAM05_VARIED_LINKS_REFERENCE, "beam-varied-links"),
        (BEAM05_HAUNCH_REFERENCE, "beam-haunch"),
        (BEAM05_PHYSICAL_FLANGE_REFERENCE, "beam-physical-flange"),
    ):
        for case, entry in json.loads((clone / reference).read_text())["cases"].items():
            label = f"{profile}-{case}"
            directory = output / label
            stdout = run(
                label,
                "Python/examples/beam_continuous_detailing.py",
                "--reference",
                str(clone / reference),
                "--case",
                case,
                "--output-dir",
                str(directory),
            )
            result = json.loads(stdout)
            status = entry["expected"]["status"]
            required_codes = set(entry["expected"].get("required_issue_codes", ()))
            if reference == BEAM05_LAYERED_LAP_REFERENCE and status == "PASS":
                # Retain the original specimen as a numerical control.
                status = "HOLD"
                required_codes.add("BEAM.LAP_COMPRESSION_RESTRAINT_HELD")
            assert result["envelope"]["engineering_status"] == status
            if (
                reference
                in (
                    BEAM05_LAP_PLACEMENT_REFERENCE,
                    BEAM05_RECTANGULAR_LAP_PLACEMENT_REFERENCE,
                    BEAM05_SUPPORT_TOP_LAP_REFERENCE,
                )
                and "issue" in entry["expected"]
            ):
                placement = result["calculation"]["placement"]
                assert placement["status"] == status
                assert placement["issue"] == entry["expected"]["issue"]
                if status == "PASS":
                    assert (
                        placement["minimum_overlap_mm"] == entry["minimum_overlap_mm"]
                    )
                    assert (
                        placement["minimum_grid_clearance_mm"]
                        == entry["expected"]["minimum_grid_clearance_mm"]
                    )
                    for face, strength in entry["worst_strength"].items():
                        for capacity in ("capacity_knm", "shear_capacity_kn"):
                            assert math.isclose(
                                placement["worst_strength"][face][capacity],
                                strength[capacity],
                                abs_tol=1e-7,
                            )
            assert required_codes <= {
                issue["code"] for issue in result["envelope"]["issues"]
            }
            assert result == json.loads((directory / "result.json").read_text())
            input_hash = result["envelope"]["result_identity"]["input_hash"]
            assert input_hash in (directory / "report.html").read_text()
            assert (directory / "member.svg").is_file() == (status == "PASS")
            assert (directory / "bbs.csv").is_file() == (status == "PASS")
            if reference == BEAM05_VARIED_LINKS_REFERENCE:
                _check_varied_link_replay(entry["expected"], result["calculation"])
            if reference == BEAM05_HAUNCH_REFERENCE:
                _check_haunch_replay(entry["expected"], result["calculation"])
            if reference == BEAM05_PHYSICAL_FLANGE_REFERENCE:
                _check_physical_flange_replay(entry["expected"], result)
            if status == "PASS":
                drawing = (directory / "member.svg").read_text()
                assert input_hash in drawing
                assert input_hash in (directory / "bbs.csv").read_text()
                if reference == BEAM05_FLANGED_REFERENCE:
                    assert 'data-view="section"' in drawing
                if reference == BEAM05_PHYSICAL_FLANGE_REFERENCE:
                    svg = ElementTree.fromstring(drawing)
                    elevation = next(
                        child for child in svg if child.get("data-view") == "elevation"
                    )
                    assert (
                        sum(node.get("data-piece-id") is not None for node in elevation)
                        == entry["expected"]["pieces"]
                    )
                if reference == BEAM05_HAUNCH_REFERENCE:
                    assert 'data-view="haunch-elevation"' in drawing
                    assert drawing.count("data-link-station=") == len(
                        entry["expected"]["link_checks"]
                    )
                if reference == BEAM05_LAYERED_CUTOFF_REFERENCE:
                    assert drawing.count('data-view="section"') == 2
                if reference in (
                    BEAM05_LAP_RESTRAINT_REFERENCE,
                    BEAM05_FLANGED_LAP_RESTRAINT_REFERENCE,
                    BEAM05_LAP_PLACEMENT_REFERENCE,
                    BEAM05_RECTANGULAR_LAP_PLACEMENT_REFERENCE,
                    BEAM05_SUPPORT_TOP_LAP_REFERENCE,
                ):
                    assert drawing.count('data-view="section"') == 3
                    assert result["calculation"]["lap"]["compression_restraint"][
                        "verified"
                    ]
                if reference in (
                    BEAM05_FLANGED_LAP_RESTRAINT_REFERENCE,
                    BEAM05_LAP_PLACEMENT_REFERENCE,
                    BEAM05_RECTANGULAR_LAP_PLACEMENT_REFERENCE,
                    BEAM05_SUPPORT_TOP_LAP_REFERENCE,
                ):
                    assert drawing.count('data-outline="restraint-link"') == 3
                    assert result["calculation"]["restraint_link_check"]["outputs"][
                        "placement_pass"
                    ]
    flow03 = json.loads((clone / FLOW03_BEAM_REFERENCE).read_text())
    for case, extra in (
        ("edited", ()),
        ("congested", ("--edit-centre-mm", str(flow03["congested_centre_mm"]))),
        ("changed_stiffness", ("--stiffness-dependent",)),
    ):
        label = f"beam-bar-edit-{case}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/beam_continuous_detailing.py",
            "--reference",
            str(clone / BEAM05_CUTOFF_REFERENCE),
            "--case",
            "cutoff",
            "--edit-bar",
            flow03["bar_id"],
            "--edit-diameter-mm",
            str(flow03["edited_diameter_mm"]),
            "--output-dir",
            str(directory),
            *extra,
        )
        result = json.loads(stdout)
        assert result["envelope"]["engineering_status"] == flow03["states"][case]
        assert (directory / "member.svg").is_file() == (case == "edited")
        assert (directory / "bbs.csv").is_file() == (case == "edited")
    if version_at_least_030:
        reference = clone / FLOW03_LAYERED_REFERENCE
        frozen = json.loads(reference.read_text(encoding="utf-8"))
        cases = {
            "base": frozen["base_expected"],
            **{name: row["expected"] for name, row in frozen["cases"].items()},
        }
        for case, expected in cases.items():
            label = f"beam-layered-cage-edit-{case}"
            directory = output / label
            result = json.loads(
                run(
                    label,
                    FLOW03_LAYERED_EXAMPLE,
                    "--reference",
                    str(reference),
                    "--case",
                    case,
                    "--output-dir",
                    str(directory),
                )
            )
            assert result["envelope"]["engineering_status"] == expected["status"]
            assert (directory / "report.html").is_file() == expected["report_available"]
            assert (directory / "member.svg").is_file() == expected[
                "checked_drawing_available"
            ]
            assert (directory / "bbs.csv").is_file() == expected["bbs_available"]
            if expected["bbs_available"]:
                bbs = result["calculation"]["bbs"]["outputs"]["bbs"]
                assert math.isclose(
                    bbs["scheduled_steel_mass_kg"],
                    expected["bbs"]["total_mass_kg"],
                    rel_tol=1e-9,
                )
    if version_at_least_030:
        run("duct01-independent-reference", DUCT01_CHECKER)
        frozen = json.loads((clone / DUCT01_REFERENCE).read_text(encoding="utf-8"))
        payload = {
            **frozen["request"],
            "applicability_reference": "Declared IS 13920 regular interior specimen.",
        }
        for case, changes in (
            ("PASS", {}),
            ("HOLD", frozen["controls"]["missing_direction"]["changes"]),
        ):
            label = f"ductile-interior-joint-{case.lower()}"
            directory = output / label
            request_file = output / f"{label}-input.json"
            request_file.write_text(json.dumps(payload | changes), encoding="utf-8")
            result = json.loads(
                run(
                    label,
                    DUCT01_EXAMPLE,
                    "--request",
                    str(request_file),
                    "--output-dir",
                    str(directory),
                )
            )
            assert result["envelope"]["engineering_status"] == case
            assert (directory / "report.html").is_file()
            assert (directory / "joint.svg").is_file() == (case == "PASS")
            assert (directory / "bbs.csv").is_file() == (case == "PASS")
        run("duct02-independent-reference", DUCT02_CHECKER)
        frozen = json.loads((clone / DUCT02_REFERENCE).read_text(encoding="utf-8"))
        payload = {
            **frozen["request"],
            "schema_version": "ductile-exterior-joint/v1",
            "applicability_reference": "Declared IS 13920 regular exterior specimen.",
        }
        exterior_cases = [
            ("baseline", {}, "PASS"),
            *(
                (name, control["changes"], control["expected"]["status"])
                for name, control in frozen["controls"].items()
            ),
        ]
        for case, changes, expected in exterior_cases:
            label = f"ductile-exterior-joint-{case}"
            directory = output / label
            request_file = output / f"{label}-input.json"
            request_file.write_text(json.dumps(payload | changes), encoding="utf-8")
            result = json.loads(
                run(
                    label,
                    DUCT01_EXAMPLE,
                    "--request",
                    str(request_file),
                    "--output-dir",
                    str(directory),
                )
            )
            assert result["workflow_id"] == "DUCT02_EXTERIOR_JOINT"
            assert result["envelope"]["engineering_status"] == expected
            assert (directory / "report.html").is_file()
            assert (directory / "joint.svg").is_file() == (expected == "PASS")
            assert (directory / "bbs.csv").is_file() == (expected == "PASS")
        run("project03-independent-reference", PROJECT03_CHECKER)
        document = json.loads((clone / PROJECT03_REFERENCE).read_text(encoding="utf-8"))
        source = (clone / PROJECT03_ACTIONS).read_text(encoding="utf-8")
        for name, control in {"baseline": None, **document["controls"]}.items():
            packet = json.loads(source)
            if control is not None:
                parent = packet
                for key in control["path"][:-1]:
                    parent = parent[key]
                key = control["path"][-1]
                if control["operation"] == "delete":
                    del parent[key]
                else:
                    parent[key] = control["value"]
            label = f"ductile-frame-cut-{name}"
            input_file = output / f"{label}-input.json"
            input_file.write_text(json.dumps(packet), encoding="utf-8")
            directory = output / label
            result = json.loads(
                run(
                    label,
                    PROJECT03_EXAMPLE,
                    "--request",
                    str(input_file),
                    "--output-dir",
                    str(directory),
                )
            )
            expected = document["expected"] if control is None else control["expected"]
            passing = expected["status"] == "PASS"
            assert result["workflow_id"] == "PROJECT03_DUCTILE_FRAME_CUT"
            assert result["envelope"]["engineering_status"] == expected["status"]
            assert (directory / "report.html").is_file()
            assert (directory / "frame.svg").is_file() == passing
            assert (directory / "bbs.csv").is_file() == passing
            if passing:
                marks = result["calculation"]["artifact_reconciliation"]
                assert (
                    marks["unique_cut_piece_count"]
                    == expected["artifact_reconciliation"]["unique_cut_piece_count"]
                )
    for option, expected in (
        ((), "COMPLETE_FOR_DECLARED_ROWS"),
        (("--alternate-units",), "COMPLETE_FOR_DECLARED_ROWS"),
        (("--missing-combination",), "HOLD"),
    ):
        suffix = option[0].removeprefix("--") if option else "native-units"
        stdout = run(
            f"etabs-paired-forces-{suffix}",
            "Python/examples/etabs_paired_forces.py",
            "--reference",
            str(clone / FLOW04_REFERENCE),
            *option,
        )
        result = json.loads(stdout)
        assert result["engineering"] == "not_evaluated"
        assert result["outputs"]["status"] == expected
    directory = output / "beam-section-catalogue"
    stdout = run(
        "beam-section-catalogue",
        "Python/examples/beam_section_catalogue.py",
        "--reference",
        str(clone / FLOW02_REFERENCE),
        "--output-dir",
        str(directory),
    )
    result = json.loads(stdout)
    expected = json.loads((clone / FLOW02_REFERENCE).read_text())["expected"]
    assert result["envelope"]["engineering_status"] == "PASS"
    assert result["calculation"]["eligible_ids"] == expected["eligible_ids"]
    assert result == json.loads((directory / "result.json").read_text())
    assert (
        result["envelope"]["result_identity"]["input_hash"]
        in (directory / "report.html").read_text()
    )
    for name in (
        "beam_comparator_reference",
        "layered_column_section",
        "beam_section_closure",
        "torsion_station_reference",
    ):
        stdout = run(name, f"Python/examples/{name}.py")
        payload = json.loads(stdout)
        (output / f"{name}.json").write_text(json.dumps(payload, indent=2) + "\n")
        if name == "torsion_station_reference":
            from structural_lib import beam

            assert payload["member_admission"] == "HOLD"
            for case, expected in (
                ("adequate_links", beam.EngineeringState.PASS),
                ("corner_geometry_shortfall", beam.EngineeringState.FAIL),
            ):
                assert payload["station_results"][case]["engineering"] == expected
    run(
        "four-corner",
        "Python/examples/four_corner_column_member.py",
        "--output-dir",
        str(output / "four-corner"),
    )
    for layout in (
        "eight_bar",
        "six_bar_omit_x_face_midpoints",
        "six_bar_omit_y_face_midpoints",
    ):
        label = f"tied-rectangular-{layout}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/tied_rectangular_column_member.py",
            "--layout",
            layout,
            "--output-dir",
            str(directory),
        )
        member = json.loads(stdout)
        assert member == json.loads((directory / "result.json").read_text())
        assert member["envelope"]["engineering_status"] == "PASS"
        assert member["calculation"]["layout"] == layout
        input_hash = member["envelope"]["result_identity"]["input_hash"]
        assert input_hash in (directory / "report.html").read_text()
    col03_cases = json.loads((clone / COL03_REFERENCE).read_text())["cases"]
    for case, expected in col03_cases.items():
        label = f"positioned-rectangular-{case}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/positioned_rectangular_column_member.py",
            "--case",
            case,
            "--output-dir",
            str(directory),
        )
        member = json.loads(stdout)
        assert member == json.loads((directory / "result.json").read_text())
        assert member["envelope"]["engineering_status"] == expected["member_status"]
        input_hash = member["envelope"]["result_identity"]["input_hash"]
        assert input_hash in (directory / "report.html").read_text()
    col04_cases = json.loads((clone / COL04_REFERENCE).read_text())["cases"]
    for case in (
        "minor_slender",
        "both_slender",
        "mixed",
        "supplied_second_order",
        "overload",
        "stale_revision",
        "conflicting_summary",
    ):
        label = f"slender-rectangular-{case}"
        directory = output / label
        expected = col04_cases[case]["expected"]
        reject = expected["member_status"] == "REJECT"
        stdout = run(
            label,
            "Python/examples/slender_rectangular_column_member.py",
            "--reference",
            str(clone / COL04_REFERENCE),
            "--case",
            case,
            "--output-dir",
            str(directory),
            expected_code=2 if reject else 0,
        )
        member = json.loads(stdout)
        if reject:
            assert member["details"]["issues"][0]["code"] == expected["issue"]
            assert not directory.exists()
        else:
            assert member == json.loads((directory / "result.json").read_text())
            assert member["envelope"]["engineering_status"] == expected["member_status"]
            input_hash = member["envelope"]["result_identity"]["input_hash"]
            assert input_hash in (directory / "report.html").read_text()
            assert input_hash in (directory / "section.svg").read_text()
    col05_cases = json.loads((clone / COL05_REFERENCE).read_text())["cases"]
    for case in (
        "tied",
        "spiral",
        "spiral_wide",
        "spiral_ordinary_wide",
        "axial_tied",
        "axial_spiral",
        "spiral_missing_anchor",
        "overload",
    ):
        label = f"circular-column-{case}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/circular_column_member.py",
            "--reference",
            str(clone / COL05_REFERENCE),
            "--case",
            case,
            "--output-dir",
            str(directory),
        )
        member = json.loads(stdout)
        assert member == json.loads((directory / "result.json").read_text())
        assert (
            member["envelope"]["engineering_status"]
            == col05_cases[case]["expected"]["member_status"]
        )
        input_hash = member["envelope"]["result_identity"]["input_hash"]
        assert input_hash in (directory / "report.html").read_text()
        assert input_hash in (directory / "section.svg").read_text()
    col06_cases = json.loads((clone / COL06_REFERENCE).read_text())["cases"]
    for case, entry in col06_cases.items():
        label = f"column-catalogue-{case}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/column_catalogue_selection.py",
            "--reference",
            str(clone / COL06_REFERENCE),
            "--case",
            case,
            "--output-dir",
            str(directory),
        )
        result = json.loads(stdout)
        assert result == json.loads((directory / "result.json").read_text())
        expected = entry["expected"]
        calculation = result["calculation"]
        assert (
            result["envelope"]["engineering_status"] == expected["engineering_status"]
        )
        assert calculation["terminal_state"] == expected["terminal_state"]
        assert calculation["selected_id"] == expected["selected_id"]
        input_hash = result["envelope"]["result_identity"]["input_hash"]
        report = (directory / "report.html").read_text()
        drawing = directory / "section.svg"
        assert input_hash in report
        if expected["selected_id"] is None:
            assert not drawing.exists()
        else:
            child = calculation["selected"]["checked_member"]
            child_hash = child["envelope"]["result_identity"]["input_hash"]
            assert child_hash in report
            svg = drawing.read_text()
            assert input_hash in svg and child_hash in svg
            ElementTree.fromstring(svg)
    for prefix, reference in (
        ("column-member-detailing", COL07_REFERENCE),
        ("column-mixed-detailing", COL07_MIXED_REFERENCE),
        ("column-slender-detailing", COL07_SLENDER_REFERENCE),
        ("column-contact-splice", COL07_SPLICE_REFERENCE),
        ("column-corner-splice", COL07_CORNER_REFERENCE),
    ):
        col07_cases = json.loads((clone / reference).read_text())["cases"]
        for case, entry in col07_cases.items():
            label = f"{prefix}-{case}"
            directory = output / label
            stdout = run(
                label,
                "Python/examples/column_member_detailing.py",
                "--reference",
                str(clone / reference),
                *(("--positioned",) if reference == COL07_MIXED_REFERENCE else ()),
                *(("--slender",) if reference == COL07_SLENDER_REFERENCE else ()),
                "--case",
                case,
                "--output-dir",
                str(directory),
            )
            member = json.loads(stdout)
            assert member == json.loads((directory / "result.json").read_text())
            assert (
                member["envelope"]["engineering_status"] == entry["expected"]["status"]
            )
            input_hash = member["envelope"]["result_identity"]["input_hash"]
            report = (directory / "report.html").read_text()
            assert input_hash in report
            drawing = directory / "member.svg"
            if (
                version_at_least_030
                and entry["expected"].get("issue") == "COLUMN.COMBINED_SHEAR"
            ):
                assert not drawing.exists()
                assert "Checked drawing withheld" in report
            else:
                svg = drawing.read_text()
                assert input_hash in svg
                ElementTree.fromstring(svg)
            bbs = directory / "bbs.csv"
            assert bbs.is_file() == entry["expected"].get(
                "bbs_available", entry["expected"]["status"] == "PASS"
            )
            if bbs.is_file():
                assert input_hash in bbs.read_text()
    for case, entry in json.loads((clone / COL07_CIRCULAR_REFERENCE).read_text())[
        "cases"
    ].items():
        label = f"circular-column-detailing-{case}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/circular_column_detailing.py",
            "--reference",
            str(clone / COL07_CIRCULAR_REFERENCE),
            "--case",
            case,
            "--output-dir",
            str(directory),
        )
        result = json.loads(stdout)
        status = entry["expected"]["status"]
        assert result["envelope"]["engineering_status"] == status
        assert result == json.loads((directory / "result.json").read_text())
        input_hash = result["envelope"]["result_identity"]["input_hash"]
        assert input_hash in (directory / "report.html").read_text()
        assert (directory / "member.svg").is_file() == (status == "PASS")
        assert (directory / "bbs.csv").is_file() == (status == "PASS")
        if status == "PASS":
            assert input_hash in (directory / "member.svg").read_text()
            assert input_hash in (directory / "bbs.csv").read_text()
    for name, args in (("d2-hold", ()), ("d3-pass", ("--with-serviceability",))):
        run(
            name,
            "Python/examples/physical_torsion_member.py",
            "--output-dir",
            str(output / name),
            *args,
        )
    run(
        "ordinary-members",
        "docs/verification/replay_library_027_members.py",
        "--example",
        str(clone / "Python/examples/complete_member_workflow.py"),
        "--output-dir",
        str(output / "ordinary-members"),
    )
    run(
        "t-members",
        "docs/verification/replay_library_027_t_member.py",
        "--example",
        str(clone / "Python/examples/t_beam_member.py"),
        "--output-dir",
        str(output / "t-members"),
        "--require-site-packages",
    )
    configuration = clone / "pytest.ini"
    configuration.write_text("[pytest]\n")
    junit = output / "beam-column-consumer-tests.xml"
    code = pytest.main(
        [
            "-q",
            "-c",
            str(configuration),
            "--confcutdir",
            str(clone),
            "--import-mode=importlib",
            "--basetemp",
            str(output / "test-artifacts"),
            "--junitxml",
            str(junit),
            *(str(clone / name) for name in TESTS),
            *(
                (
                    str(clone / FLOW03_LAYERED_TEST),
                    str(clone / WORKBENCH_TEST),
                    str(clone / SL04_SL05_TEST),
                    str(clone / SL06_TEST),
                    *(str(clone / name) for name in COL07_030_TESTS),
                    str(clone / DUCT01_TEST),
                    str(clone / DUCT02_TEST),
                    str(clone / PROJECT03_TEST),
                )
                if version_at_least_030
                else ()
            ),
        ]
    )
    suites = ElementTree.parse(junit).getroot().findall("testsuite")
    counts = {
        key: sum(int(suite.attrib.get(key, 0)) for suite in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }
    if (
        code != 0
        or not counts["tests"]
        or any(counts[key] for key in ("failures", "errors", "skipped"))
    ):
        raise AssertionError(f"Installed beam/column consumer tests failed: {counts}")
    return {
        "status": "PASS",
        "verification_tools": "Declared dev,dxf,report extras; separate from base-only profiles",
        "driver_inputs_sha256": hashes,
        "commands": commands,
        "tests": counts,
        "junit": str(junit),
        "t_member_journeys": json.loads(
            (output / "t-members/receipt.json").read_text()
        ),
        "professional_approval": False,
    }
