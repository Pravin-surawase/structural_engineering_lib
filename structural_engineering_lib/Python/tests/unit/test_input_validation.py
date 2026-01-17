import pytest

from structural_lib import flexure, shear


def _has_error_with_field(errors, field: str) -> bool:
    """Check if errors list contains an error with the given field."""
    return any(e.field is not None and field.lower() in e.field.lower() for e in errors)


def _has_error_with_message(errors, message_substring: str) -> bool:
    """Check if errors list contains an error with the given message substring."""
    return any(message_substring.lower() in e.message.lower() for e in errors)


@pytest.mark.parametrize(
    "kwargs, expected_substring",
    [
        (
            {
                "b": 0.0,
                "d": 450.0,
                "d_total": 500.0,
                "mu_knm": 100.0,
                "fck": 25.0,
                "fy": 500.0,
            },
            "b",  # Only b is invalid, so only b should be mentioned
        ),
        (
            {
                "b": 230.0,
                "d": -1.0,
                "d_total": 500.0,
                "mu_knm": 100.0,
                "fck": 25.0,
                "fy": 500.0,
            },
            "d",  # Only d is invalid, so only d should be mentioned
        ),
        (
            {
                "b": 230.0,
                "d": 450.0,
                "d_total": 450.0,
                "mu_knm": 100.0,
                "fck": 25.0,
                "fy": 500.0,
            },
            "d_total",
        ),
        (
            {
                "b": 230.0,
                "d": 450.0,
                "d_total": 500.0,
                "mu_knm": 100.0,
                "fck": 0.0,
                "fy": 500.0,
            },
            "fck",
        ),
        (
            {
                "b": 230.0,
                "d": 450.0,
                "d_total": 500.0,
                "mu_knm": 100.0,
                "fck": 25.0,
                "fy": 0.0,
            },
            "fy",
        ),
    ],
)
def test_flexure_design_singly_reinforced_rejects_invalid_inputs(
    kwargs, expected_substring
):
    res = flexure.design_singly_reinforced(**kwargs)
    assert res.is_safe is False
    # Check that error for the expected field is in the errors list
    assert _has_error_with_field(
        res.errors, expected_substring
    ) or _has_error_with_message(res.errors, expected_substring)


def test_flexure_design_doubly_reinforced_rejects_nonpositive_d_dash():
    b, d, d_total = 230.0, 450.0, 500.0
    res = flexure.design_doubly_reinforced(
        b=b,
        d=d,
        d_dash=0.0,
        d_total=d_total,
        mu_knm=200.0,
        fck=25.0,
        fy=415.0,
    )
    assert res.is_safe is False
    # Check for d' error in errors list
    assert (
        _has_error_with_field(res.errors, "d_dash")
        or _has_error_with_message(res.errors, "d'")
        or _has_error_with_message(res.errors, "d_dash")
    )
    assert any(err.code == "E_INPUT_010" for err in res.errors)


@pytest.mark.parametrize(
    "kwargs, expected_field",
    [
        (
            {
                "vu_kn": 100.0,
                "b": 0.0,
                "d": 450.0,
                "fck": 25.0,
                "fy": 415.0,
                "asv": 100.0,
                "pt": 1.0,
            },
            "b",  # Only b is invalid - new error system reports individual fields
        ),
        (
            {
                "vu_kn": 100.0,
                "b": 230.0,
                "d": 0.0,
                "fck": 25.0,
                "fy": 415.0,
                "asv": 100.0,
                "pt": 1.0,
            },
            "d",  # Only d is invalid - new error system reports individual fields
        ),
        (
            {
                "vu_kn": 100.0,
                "b": 230.0,
                "d": 450.0,
                "fck": 0.0,
                "fy": 415.0,
                "asv": 100.0,
                "pt": 1.0,
            },
            "fck",
        ),
        (
            {
                "vu_kn": 100.0,
                "b": 230.0,
                "d": 450.0,
                "fck": 25.0,
                "fy": 0.0,
                "asv": 100.0,
                "pt": 1.0,
            },
            "fy",
        ),
        (
            {
                "vu_kn": 100.0,
                "b": 230.0,
                "d": 450.0,
                "fck": 25.0,
                "fy": 415.0,
                "asv": 0.0,
                "pt": 1.0,
            },
            "asv",
        ),
        (
            {
                "vu_kn": 100.0,
                "b": 230.0,
                "d": 450.0,
                "fck": 25.0,
                "fy": 415.0,
                "asv": 100.0,
                "pt": -0.1,
            },
            "pt",
        ),
    ],
)
def test_shear_design_rejects_invalid_inputs(kwargs, expected_field):
    res = shear.design_shear(**kwargs)
    assert res.is_safe is False
    # Check that error for the expected field is in the errors list
    assert _has_error_with_field(res.errors, expected_field) or _has_error_with_message(
        res.errors, expected_field
    )
