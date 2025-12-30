import pytest

from structural_lib import flexure
from structural_lib.types import BeamType


def test_effective_flange_width_t_code_limit():
    bf = flexure.calculate_effective_flange_width(
        bw_mm=300.0,
        span_mm=6000.0,
        df_mm=120.0,
        flange_overhang_left_mm=1000.0,
        flange_overhang_right_mm=1000.0,
        beam_type=BeamType.FLANGED_T,
    )

    assert bf == pytest.approx(2020.0, rel=0.0, abs=1e-6)


def test_effective_flange_width_l_geometry_limit():
    bf = flexure.calculate_effective_flange_width(
        bw_mm=300.0,
        span_mm=6000.0,
        df_mm=100.0,
        flange_overhang_left_mm=500.0,
        flange_overhang_right_mm=0.0,
        beam_type="L",
    )

    assert bf == pytest.approx(800.0, rel=0.0, abs=1e-6)


def test_effective_flange_width_rectangular_rejects_overhangs():
    with pytest.raises(
        ValueError, match="Rectangular beam cannot have flange overhangs"
    ):
        flexure.calculate_effective_flange_width(
            bw_mm=300.0,
            span_mm=5000.0,
            df_mm=120.0,
            flange_overhang_left_mm=200.0,
            flange_overhang_right_mm=0.0,
            beam_type=BeamType.RECTANGULAR,
        )


def test_effective_flange_width_invalid_beam_type():
    with pytest.raises(ValueError, match="beam_type must be"):
        flexure.calculate_effective_flange_width(
            bw_mm=300.0,
            span_mm=5000.0,
            df_mm=120.0,
            flange_overhang_left_mm=200.0,
            flange_overhang_right_mm=200.0,
            beam_type="I",
        )


def test_effective_flange_width_negative_overhang_rejected():
    with pytest.raises(ValueError, match="Flange overhangs must be >= 0"):
        flexure.calculate_effective_flange_width(
            bw_mm=300.0,
            span_mm=5000.0,
            df_mm=120.0,
            flange_overhang_left_mm=-10.0,
            flange_overhang_right_mm=0.0,
            beam_type="T",
        )
