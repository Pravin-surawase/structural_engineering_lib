"""The exact-wheel acceptance matrix remains data-driven and executable."""

from structural_lib.release_uat import run


def test_release_negative_matrix_and_public_examples_pass() -> None:
    receipt = run()

    assert receipt["status"] == "PASS"
    assert receipt["case_count"] == 29
    assert all(case["status"] == "PASS" for case in receipt["cases"])
    assert receipt["public_examples"] == {
        "readme_beam": True,
        "python_readme_batch": True,
    }
    assert receipt["qualified_review_required"] is True
    assert receipt["professional_approval"] is False
    inventory = receipt["advertised_entry_points"]
    assert inventory["schema_version"] == "advertised-entry-point-inventory/v1"
    assert inventory["entry_count"] == 12
    assert {entry["command"] for entry in inventory["entries"]} == {
        "install-preflight",
        "capabilities",
        "design",
        "bbs",
        "detail",
        "dxf",
        "validate",
        "mark-diff",
        "smart",
        "job",
        "report",
        "critical",
    }
