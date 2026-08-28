"""The exact-wheel acceptance matrix remains data-driven and executable."""

from structural_lib.release_uat import run


def test_release_negative_matrix_and_public_examples_pass() -> None:
    receipt = run()

    assert receipt["status"] == "PASS"
    assert receipt["case_count"] == 29
    assert all(case["status"] == "PASS" for case in receipt["cases"])
    assert receipt["public_examples"] == {
        "maintained_beam_service": True,
        "python_readme_batch": True,
    }
    assert receipt["qualified_review_required"] is True
    assert receipt["professional_approval"] is False
    inventory = receipt["advertised_entry_points"]
    assert inventory["schema_version"] == "advertised-entry-point-inventory/v2"
    assert inventory["entry_count"] == 28
    assert inventory["cli_entry_count"] == 15
    assert inventory["family_facade_entry_count"] == 13
    gravity = next(
        entry for entry in inventory["entries"] if entry["id"] == "cli.gravity-v1"
    )
    assert gravity == {
        "id": "cli.gravity-v1",
        "command": "gravity-v1",
        "classification": "calculation_entry",
        "acceptance": ["test_cli_emits_same_versioned_bundle_from_json_request"],
    }
    excel = next(
        entry for entry in inventory["entries"] if entry["id"] == "cli.excel-v1"
    )
    assert excel == {
        "id": "cli.excel-v1",
        "command": "excel-v1",
        "classification": "calculation_entry",
        "acceptance": ["test_cli_requires_preview_hash_and_matches_python_result"],
    }
    assert {
        entry["command"] for entry in inventory["entries"] if "command" in entry
    } == {
        "install-preflight",
        "capabilities",
        "gravity-v1",
        "excel-v1",
        "beam-v1",
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
    family_entries = [
        entry for entry in inventory["entries"] if entry["id"].startswith("python.")
    ]
    assert len(family_entries) == 13
    assert all(entry["cookbook_path"].endswith(".md") for entry in family_entries)
    assert all(
        entry["acceptance"]
        == [
            "r0_exact_wheel_recipe",
            "r0_strict_field_contract_audit",
            "r0_finite_json_consumer",
        ]
        for entry in family_entries
    )
