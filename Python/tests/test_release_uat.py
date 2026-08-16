"""The exact-wheel acceptance matrix remains data-driven and executable."""

from structural_lib.release_uat import run


def test_release_negative_matrix_and_public_examples_pass() -> None:
    receipt = run()

    assert receipt["status"] == "PASS"
    assert receipt["case_count"] == 19
    assert all(case["status"] == "PASS" for case in receipt["cases"])
    assert receipt["public_examples"] == {
        "readme_beam": True,
        "python_readme_batch": True,
    }
    assert receipt["qualified_review_required"] is True
    assert receipt["professional_approval"] is False
