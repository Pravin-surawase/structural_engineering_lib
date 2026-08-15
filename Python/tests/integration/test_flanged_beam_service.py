"""INDIA-1A composed T-beam service and boundary evidence."""

from __future__ import annotations

import pytest

from structural_lib.services.api import design_flanged_beam_is456


@pytest.fixture
def benchmark_t_beam() -> dict[str, float | str]:
    """Validation-pack B3 geometry with an explicit combined shear case."""
    return {
        "units": "IS456",
        "beam_type": "T",
        "moment_region": "sagging",
        "load_case_basis": "single_factored_case",
        "mu_knm": 200.0,
        "vu_kn": 150.0,
        "bw_mm": 300.0,
        "D_mm": 550.0,
        "d_mm": 500.0,
        "span_mm": 6000.0,
        "flange_thickness_mm": 150.0,
        "flange_overhang_left_mm": 350.0,
        "flange_overhang_right_mm": 350.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }


def test_composed_t_beam_matches_b3_and_uses_web_for_shear(
    benchmark_t_beam: dict[str, float | str],
) -> None:
    """B3 flexure is independently pinned; shear must use bw, not bf."""
    result = design_flanged_beam_is456(**benchmark_t_beam)

    assert result.is_ok is True
    assert result.bf_geometric_mm == pytest.approx(1000.0)
    assert result.bf_effective_mm == pytest.approx(1000.0)
    assert result.design.flexure.Mu_lim == pytest.approx(835.038, abs=1.0)
    assert result.design.flexure.Ast_required == pytest.approx(956.6, abs=10.0)
    assert result.design.flexure.xu == pytest.approx(46.24, abs=1.0)
    assert result.design.shear.tau_v == pytest.approx(1.0)
    assert result.design.clause_refs["flexure"] == (
        "IS 456 Cl 23.1.2 and 38.1; Annex G"
    )
    assert result.clause_refs["effective_flange_width"] == "IS 456 Cl 23.1.2"
    assert "Load-envelope generation" in result.holds[0]
    serialized = result.to_dict()
    assert serialized["design"]["flexure"]["section_type"] == "UNDER_REINFORCED"
    assert serialized["explicit_units"]["moment"] == "kN·m"


def test_effective_flange_width_is_limited_by_span_and_flange_depth(
    benchmark_t_beam: dict[str, float | str],
) -> None:
    result = design_flanged_beam_is456(
        **{
            **benchmark_t_beam,
            "span_mm": 3000.0,
            "flange_thickness_mm": 100.0,
            "flange_overhang_left_mm": 1000.0,
            "flange_overhang_right_mm": 1000.0,
        }
    )

    assert result.bf_geometric_mm == pytest.approx(2300.0)
    assert result.bf_effective_mm == pytest.approx(1400.0)


def test_explicit_serviceability_inputs_are_composed_without_geometry_drift(
    benchmark_t_beam: dict[str, float | str],
) -> None:
    result = design_flanged_beam_is456(
        **benchmark_t_beam,
        deflection_params={
            "span_mm": 6000.0,
            "d_mm": 500.0,
            "support_condition": "simply_supported",
        },
        crack_width_params={
            "exposure_class": "moderate",
            "acr_mm": 40.0,
            "cmin_mm": 25.0,
            "h_mm": 550.0,
            "x_mm": 150.0,
            "fs_service_nmm2": 180.0,
        },
    )

    assert result.design.deflection is not None
    assert result.design.deflection.is_ok is True
    assert result.design.crack_width is not None
    assert result.design.crack_width.is_ok is True


def test_unsafe_web_shear_fails_the_composed_result(
    benchmark_t_beam: dict[str, float | str],
) -> None:
    result = design_flanged_beam_is456(**{**benchmark_t_beam, "vu_kn": 500.0})

    assert result.is_ok is False
    assert result.design.shear.is_safe is False
    assert any(item.startswith("shear") for item in result.design.failed_checks)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"beam_type": "L"}, "FLANGED_SECTION_SCOPE_HOLD"),
        ({"moment_region": "hogging"}, "FLANGED_MOMENT_SCOPE_HOLD"),
        ({"load_case_basis": "generate_envelope"}, "LOAD_ENVELOPE_SCOPE_HOLD"),
        ({"tu_knm": 5.0}, "FLANGED_TORSION_SCOPE_HOLD"),
        (
            {"torsion_redistribution_basis": "compatibility"},
            "TORSION_REDISTRIBUTION_SCOPE_HOLD",
        ),
    ],
)
def test_out_of_scope_routes_fail_closed(
    benchmark_t_beam: dict[str, float | str],
    overrides: dict[str, float | str],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        design_flanged_beam_is456(**{**benchmark_t_beam, **overrides})


def test_serviceability_geometry_mismatch_fails_closed(
    benchmark_t_beam: dict[str, float | str],
) -> None:
    with pytest.raises(ValueError, match="SERVICEABILITY_GEOMETRY_HOLD"):
        design_flanged_beam_is456(
            **benchmark_t_beam,
            deflection_params={
                "span_mm": 5000.0,
                "d_mm": 500.0,
                "support_condition": "simply_supported",
            },
        )
