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


def test_mm_to_m_basic():
    assert utilities.mm_to_m(1500) == 1.5


def test_m_to_mm_basic():
    assert utilities.m_to_mm(1.5) == 1500.0


def test_mm_to_m_round_trip():
    # Test round-trip conversion: m_to_mm(mm_to_m(x)) == x
    x = 2500.0
    assert utilities.m_to_mm(utilities.mm_to_m(x)) == pytest.approx(x)


def test_mm_to_m_zero():
    assert utilities.mm_to_m(0) == 0.0


def test_m_to_mm_zero():
    assert utilities.m_to_mm(0) == 0.0


def test_mm_to_m_negative():
    # Negative values should work correctly
    assert utilities.mm_to_m(-1500) == -1.5


def test_m_to_mm_negative():
    # Negative values should work correctly
    assert utilities.m_to_mm(-1.5) == -1500.0
