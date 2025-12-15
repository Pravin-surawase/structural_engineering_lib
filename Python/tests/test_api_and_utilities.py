import pytest

from structural_lib import api, ductile, utilities


def test_get_library_version_nonempty():
    # Keep this intentionally loose: version bumps should not break tests.
    v = api.get_library_version()
    assert isinstance(v, str)
    assert v.strip() != ""


def test_check_beam_ductility_wrapper_matches_core():
    inputs = dict(b=300, D=500, d=450, fck=25, fy=500, min_long_bar_dia=16)
    assert api.check_beam_ductility(**inputs) == ductile.check_beam_ductility(**inputs)


def test_linear_interp_basic():
    assert utilities.linear_interp(5.0, 0.0, 0.0, 10.0, 100.0) == pytest.approx(50.0)


def test_linear_interp_zero_div_guard():
    # If x1 == x2, function should return y1 deterministically.
    assert utilities.linear_interp(123.0, 1.0, 7.0, 1.0, 999.0) == 7.0


def test_round_to():
    assert utilities.round_to(1.23456, 2) == 1.23
