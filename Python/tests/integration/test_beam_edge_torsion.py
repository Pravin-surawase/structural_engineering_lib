"""Check same-row edge-beam torsion and the independent transfer boundary."""

import json
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CASES = json.loads(
    (ROOT / "docs/verification/library-029-beam07-equilibrium-torsion.json").read_text()
)["cases"]
EXAMPLE = runpy.run_path(str(ROOT / "Python/examples/physical_torsion_member.py"))


@pytest.mark.parametrize("name", CASES)
def test_edge_beam_preserves_signed_rows_and_physical_transfer(name):
    fixture = CASES[name]
    workflow = EXAMPLE["run_workflow"](
        load_n_per_mm=fixture["uniform_load_n_per_mm"],
        torsion_eccentricity_mm=fixture["eccentricity_mm"],
        link_pitch_mm=fixture["link_spacing_mm"],
        declared_transfer=name != "missing_transfer",
        omit_checks=("support_transfer",) if name == "missing_transfer" else (),
    )
    result = workflow.results["edge_torsion"]
    expected = fixture["status"]
    assert result.engineering == (
        "not_evaluated" if expected == "HOLD" else expected.lower()
    )
    snapshot = workflow.results["actions"]
    assert result.outputs["action_snapshot_id"] == snapshot.result_id
    for leaf, source, expected_row in zip(
        result.outputs["station_checks"],
        snapshot.outputs["rows"],
        fixture["rows"],
        strict=True,
    ):
        action, output = leaf["effective_inputs"]["action"]["value"], leaf["outputs"]
        assert action["row_id"] == source["source_row_id"]
        assert action["source_identity"] == source["row_id"]
        for key in ("v2_kn", "m3_knm", "torsion_knm"):
            assert action[key] == pytest.approx(expected_row[key], abs=1e-8)
        for actual, reference in (
            ("equivalent_shear_kn", "equivalent_shear_kn"),
            ("primary_equivalent_moment_knm", "primary_moment_knm"),
            ("opposite_equivalent_moment_knm", "opposite_moment_knm"),
            ("required_link_area_per_spacing_mm", "required_link_area_per_spacing_mm"),
            ("provided_link_area_per_spacing_mm", "provided_link_area_per_spacing_mm"),
        ):
            assert output[actual] == pytest.approx(expected_row[reference], abs=1e-8)
    if name == "missing_transfer":
        assert result.outputs["transfer"] is None
        assert result.diagnostics[0].code == "EDGE.TRANSFER_HELD"
        return
    if expected == "PASS":
        assert result.outputs["transfer"]["outputs"]["global_equilibrium_pass"]
        for check in result.outputs["transfer"]["outputs"]["checks"]:
            assert check["force_kn"] == pytest.approx(fixture["support_reaction_kn"])
            assert check["external_torque_knm"] == pytest.approx(
                fixture["support_external_torque_knm"]
            )
        assert len(result.outputs["anchors"]) == 2
        assert all(
            check["engineering"] == "pass" for check in result.outputs["anchors"]
        )
    if name == "inadequate_links":
        assert any(
            issue.code == "TORSION.TRANSVERSE_REINFORCEMENT"
            for issue in result.diagnostics
        )
    if name == "inadequate_longitudinal":
        assert any(
            issue.code == "TORSION.LONGITUDINAL_REINFORCEMENT"
            for issue in result.diagnostics
        )


def test_edge_report_uses_checked_result_identity(tmp_path):
    workflow = EXAMPLE["run_workflow"]()
    EXAMPLE["write_artifacts"](workflow, tmp_path)
    payload = json.loads((tmp_path / "calculation.json").read_text())
    result = workflow.results["edge_torsion"]
    assert payload["edge_torsion_status"] == "PASS"
    assert payload["results"]["edge_torsion"] == result.to_dict()
    assert result.result_id in (tmp_path / "report.html").read_text()
