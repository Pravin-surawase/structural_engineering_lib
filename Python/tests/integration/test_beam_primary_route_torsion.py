"""Focused contract tests for primary-route beam torsion integration."""

from dataclasses import asdict

import pytest

from structural_lib.services.api import design_beam_is456


@pytest.fixture
def ordinary_beam() -> dict[str, float | str]:
    return {
        "units": "IS456",
        "mu_knm": 150.0,
        "vu_kn": 75.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 457.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
        "d_dash_mm": 43.0,
    }


def test_zero_torsion_preserves_primary_service_result(
    ordinary_beam: dict[str, float | str],
) -> None:
    implicit_zero = design_beam_is456(**ordinary_beam)
    explicit_zero = design_beam_is456(**ordinary_beam, tu_knm=0.0)

    assert asdict(explicit_zero) == asdict(implicit_zero)
    assert explicit_zero.flexure.Ast_required == pytest.approx(863.7612750126042)
    assert explicit_zero.shear.tau_v == pytest.approx(0.5470459518599562)
    assert explicit_zero.torsion is None
    assert explicit_zero.Me_knm is None
    assert explicit_zero.Ve_kn is None


def test_safe_torsion_drives_primary_equivalent_action_design(
    ordinary_beam: dict[str, float | str],
) -> None:
    zero = design_beam_is456(**ordinary_beam)
    result = design_beam_is456(
        **ordinary_beam,
        tu_knm=10.0,
        cover_mm=25.0,
        stirrup_dia_mm=8.0,
    )

    assert result.is_ok is True
    assert result.torsion is not None
    assert result.Me_knm == pytest.approx(165.68627450980392)
    assert result.Ve_kn == pytest.approx(128.33333333333334)
    assert result.flexure.Ast_required > zero.flexure.Ast_required
    assert result.shear.tau_v == pytest.approx(result.Ve_kn * 1000 / (300.0 * 457.0))
    assert result.torsion.Asv_total > 0
    assert result.torsion.Al_torsion > 0
    assert result.torsion.requires_closed_stirrups is True
    assert result.torsion.clause_refs["Ve"] == "IS 456 Cl 41.3.1"
    assert "torsion" in result.utilizations


def test_unsafe_torsion_fails_combined_primary_result() -> None:
    result = design_beam_is456(
        units="IS456",
        mu_knm=300.0,
        vu_kn=200.0,
        tu_knm=100.0,
        b_mm=200.0,
        D_mm=400.0,
        d_mm=350.0,
        fck_nmm2=20.0,
        fy_nmm2=500.0,
        d_dash_mm=50.0,
        cover_mm=40.0,
        stirrup_dia_mm=8.0,
    )

    assert result.is_ok is False
    assert result.torsion is not None
    assert result.torsion.is_safe is False
    assert any(item.startswith("torsion (") for item in result.failed_checks)
    assert any(error.code == "E_TORSION_001" for error in result.torsion.errors)
    assert result.torsion.clause_refs["tau_ve"] == "IS 456 Cl 41.3.1"


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"fck_nmm2": 50.0}, "fck_nmm2 from 15 to 40"),
        ({"fy_nmm2": 550.0}, "fy_nmm2 <= 500"),
        ({"cover_mm": None}, "cover_mm is required"),
    ],
)
def test_primary_torsion_fails_closed_outside_documented_scope(
    ordinary_beam: dict[str, float | str],
    overrides: dict[str, float | None],
    message: str,
) -> None:
    inputs = {**ordinary_beam, "tu_knm": 10.0, "cover_mm": 25.0, **overrides}

    with pytest.raises(ValueError, match=message):
        design_beam_is456(**inputs)


def test_service_contract_returns_existing_serviceability_results(
    ordinary_beam: dict[str, float | str],
) -> None:
    result = design_beam_is456(
        **ordinary_beam,
        deflection_params={
            "span_mm": 5000.0,
            "d_mm": 457.0,
            "support_condition": "simply_supported",
        },
        crack_width_params={
            "exposure_class": "moderate",
            "acr_mm": 40.0,
            "cmin_mm": 25.0,
            "h_mm": 500.0,
            "x_mm": 150.0,
            "fs_service_nmm2": 180.0,
        },
    )

    assert result.deflection is not None
    assert result.deflection.is_ok is True
    assert result.deflection.computed["ld_ratio"] == pytest.approx(5000 / 457)
    assert result.crack_width is not None
    assert result.crack_width.is_ok is True
    assert result.crack_width.computed["wcr_mm"] == pytest.approx(0.09947368421052633)
