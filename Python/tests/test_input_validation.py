import pytest

from structural_lib import flexure, shear


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
    assert expected_substring.lower() in res.error_message.lower()


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
    assert "d'" in res.error_message.lower()
    assert any(err.code == "E_INPUT_010" for err in res.errors)


@pytest.mark.parametrize(
    "kwargs, expected_substring",
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
            "b and d",
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
            "b and d",
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
def test_shear_design_rejects_invalid_inputs(kwargs, expected_substring):
    res = shear.design_shear(**kwargs)
    assert res.is_safe is False
    assert expected_substring.lower() in res.remarks.lower()
