from structural_lib.api import design_beam_is456
from structural_lib.insights import sensitivity_analysis


def _base_params():
    return {
        "units": "IS456",
        "mu_knm": 120.0,
        "vu_kn": 80.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }


def test_sensitivity_deterministic():
    params = _base_params()
    s1, r1 = sensitivity_analysis(design_beam_is456, params, ["d_mm", "b_mm"])
    s2, r2 = sensitivity_analysis(design_beam_is456, params, ["d_mm", "b_mm"])

    assert s1 == s2
    assert r1 == r2


def test_sensitivity_depth_more_critical():
    params = _base_params()
    sensitivities, robustness = sensitivity_analysis(
        design_beam_is456, params, ["d_mm", "b_mm"]
    )
    assert robustness.score >= 0.0
    assert robustness.score <= 1.0

    by_param = {item.parameter: item for item in sensitivities}
    assert abs(by_param["d_mm"].sensitivity) >= abs(by_param["b_mm"].sensitivity)
