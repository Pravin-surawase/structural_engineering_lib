import builtins
import importlib
import math
import runpy
import sys

import pytest

from structural_lib import materials, tables


def test_get_tc_for_grade_unknown_grade_falls_back_to_m40_column():
    # Internal helper: unknown grade should fall back to M40 column.
    # Use a mid pt to ensure interpolation path is exercised.
    tc_unknown = tables._get_tc_for_grade(999, 0.5)
    tc_m40 = tables._get_tc_for_grade(40, 0.5)
    assert tc_unknown == pytest.approx(tc_m40)


def test_get_tc_for_grade_clamps_pt_low_and_high():
    # Below min clamps to 0.15
    assert tables._get_tc_for_grade(20, 0.01) == pytest.approx(
        tables._get_tc_for_grade(20, 0.15)
    )

    # Above max clamps to 3.0
    assert tables._get_tc_for_grade(20, 99.0) == pytest.approx(
        tables._get_tc_for_grade(20, 3.0)
    )


def test_get_tc_for_grade_nan_pt_returns_last_value():
    # Robustness: NaN should not match any interval and returns last entry.
    tc = tables._get_tc_for_grade(20, float("nan"))
    assert tc == pytest.approx(0.82)


def test_get_steel_stress_other_grade_fallback_branches():
    # Cover the fallback branch for grades other than 250/415/500.
    fy = 600.0

    # Below yield_strain but strain*Es exceeds 0.87fy => min(...) path clamps to 0.87fy.
    s = materials.get_steel_stress(0.003, fy)
    assert s == pytest.approx(0.87 * fy)

    # Below yield_strain and strain*Es below 0.87fy => linear.
    s2 = materials.get_steel_stress(0.001, fy)
    assert s2 == pytest.approx(200000.0 * 0.001)

    # Above yield_strain => plateau.
    # yield_strain = 0.87fy/Es + 0.002
    yield_strain = (0.87 * fy) / 200000.0 + 0.002
    s3 = materials.get_steel_stress(yield_strain + 1e-6, fy)
    assert s3 == pytest.approx(0.87 * fy)


def test_get_fcr_positive_value():
    assert materials.get_fcr(25) == pytest.approx(0.7 * math.sqrt(25))


def test_calculate_tv_handles_zero_bd():
    from structural_lib import shear

    assert shear.calculate_tv(100.0, b=0.0, d=450.0) == 0.0
    assert shear.calculate_tv(100.0, b=230.0, d=0.0) == 0.0


def test_shear_spacing_clamps_to_min_reinf_limit():
    # Cover the final clamp: spacing > max_spacing_min_reinf.
    from structural_lib import shear

    res = shear.design_shear(
        vu_kn=310.0,
        b=1000.0,
        d=1000.0,
        fck=20.0,
        fy=415.0,
        asv=100.0,
        pt=0.15,
    )

    assert res.is_safe is True
    max_spacing_min_reinf = (0.87 * 415.0 * 100.0) / (0.4 * 1000.0)
    assert res.spacing == pytest.approx(max_spacing_min_reinf)


def test_ductile_geometry_failure_branches():
    from structural_lib import ductile

    ok, msg, errors = ductile.check_geometry(150, 450)
    assert ok is False
    assert "Width" in msg
    assert len(errors) == 1

    ok, msg, errors = ductile.check_geometry(250, 0)
    assert ok is False
    assert "Invalid depth" in msg

    ok, msg, errors = ductile.check_geometry(200, 1000)
    assert ok is False
    assert "Width/Depth" in msg

    res = ductile.check_beam_ductility(
        b=150, D=450, d=400, fck=25, fy=500, min_long_bar_dia=16
    )
    assert res.is_geometry_valid is False
    assert res.remarks != "Compliant"
    assert len(res.errors) >= 1


def test_detailing_bar_type_plain_and_arrangement_branches():
    from structural_lib import detailing

    # Cover bar_type == plain branch
    tau_def = detailing.get_bond_stress(25, bar_type="deformed")
    tau_plain = detailing.get_bond_stress(25, bar_type="plain")
    assert tau_plain == pytest.approx(tau_def / 1.6)

    # Cover ast_required <= 0 branch
    arr = detailing.select_bar_arrangement(ast_required=0.0, b=230, cover=25)
    assert arr.count == 2
    assert arr.layers == 1

    # Force 2-layer path by making a single layer spacing invalid.
    # Small width + large bar count makes spacing fail, then max_layers>1 triggers split.
    arr2 = detailing.select_bar_arrangement(
        ast_required=5000.0,
        b=150,
        cover=40,
        stirrup_dia=10,
        preferred_dia=25,
        max_layers=2,
    )
    assert arr2.layers == 2


def test_detailing_select_bar_arrangement_auto_selects_25mm_dia():
    # Cover the auto-select branch where ast_required >= 2000 -> preferred_dia = 25.
    from structural_lib import detailing

    arr = detailing.select_bar_arrangement(
        ast_required=2500.0, b=230, cover=25, max_layers=1
    )
    assert arr.diameter == 25


def test_detailing_get_bond_stress_for_fck_above_max_grade_hits_no_break_path():
    from structural_lib import detailing

    ok = detailing.get_bond_stress(100, bar_type="deformed")
    assert ok > 0


def test_flexure_calculate_ast_required_clamps_term2(monkeypatch):
    # Cover the safety clamp term2>1.0 branch by stubbing Mu_lim high enough
    # so the over-reinforced early return doesn't trigger.
    from structural_lib import flexure

    monkeypatch.setattr(flexure, "calculate_mu_lim", lambda *_args, **_kwargs: 1e12)

    ast = flexure.calculate_ast_required(b=230, d=450, mu_knm=1e6, fck=20, fy=415)
    assert ast > 0


def test_flexure_singly_reinforced_hits_max_steel_exceeded():
    from structural_lib import flexure

    # Keep geometry valid, but use an unrealistically low fy to push Ast_min
    # above Ast_max and cover the max-steel branch deterministically.
    res = flexure.design_singly_reinforced(
        b=300, d=500, d_total=550, mu_knm=0.0, fck=25, fy=10
    )
    assert res.is_safe is False
    assert "maximum" in res.error_message.lower()


def test_flexure_calculate_ast_required_over_reinforced_returns_minus_one():
    from structural_lib import flexure

    mu_lim = flexure.calculate_mu_lim(230, 450, 25, 415)
    ast = flexure.calculate_ast_required(230, 450, mu_lim + 1.0, 25, 415)
    assert ast == -1.0


def test_flexure_doubly_reinforced_denom_nonpositive_path():
    from structural_lib import flexure
    from structural_lib import materials as mat

    b = 300.0
    d = 500.0
    d_total = 550.0
    fck = 40.0
    fy = 415.0
    xu_max = mat.get_xu_max_d(fy) * d
    d_dash = xu_max - 0.1  # keep valid geometry but make strain very small

    mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
    res = flexure.design_doubly_reinforced(
        b, d, d_dash, d_total, mu_lim + 10.0, fck, fy
    )
    assert res.is_safe is False
    assert "invalid section geometry" in res.error_message.lower()


def test_flexure_doubly_reinforced_hits_asc_exceeds_max_branch():
    from structural_lib import flexure

    # Keep geometry valid; drive Mu very high so Asc exceeds the 4% bD max.
    res = flexure.design_doubly_reinforced(
        b=300.0,
        d=500.0,
        d_dash=50.0,
        d_total=550.0,
        mu_knm=1e6,
        fck=25.0,
        fy=415.0,
    )
    assert res.is_safe is False
    assert "asc exceeds" in res.error_message.lower()


def test_flexure_flanged_beam_hits_yf_clamp_and_ast_max_exceeded():
    from structural_lib import flexure

    # 1) Doubly reinforced T-beam branch: mu > mu_lim_t.
    # Choose d >> Df and Df/d > 0.2 so yf expression exceeds Df and clamps.
    res_doubly = flexure.design_flanged_beam(
        bw=300,
        bf=900,
        d=1000,
        Df=203,
        d_total=1050,
        mu_knm=5000.0,
        fck=25,
        fy=415,
    )
    assert res_doubly.ast_required > 0

    # Also cover the non-clamping case in the same branch (yf <= Df).
    res_doubly_no_clamp = flexure.design_flanged_beam(
        bw=300,
        bf=900,
        d=1000,
        Df=300,
        d_total=1050,
        mu_knm=5000.0,
        fck=25,
        fy=415,
    )
    assert res_doubly_no_clamp.ast_required > 0

    # 2) Singly reinforced T-beam solver branch: mu between capacity_at_df and mu_lim_t.
    # Pick mu close to mu_lim_t to drive xu high enough that yf expressions exceed Df
    # and the clamp paths execute.
    res_solver = flexure.design_flanged_beam(
        bw=300,
        bf=300,
        d=1000,
        Df=205,
        d_total=1200,
        mu_knm=1033.0,
        fck=25,
        fy=415,
    )
    assert res_solver.ast_required > 0


def test_flexure_flanged_beam_solver_hits_minimum_steel_branch_low_fck():
    # Use a very low fck to make required Ast small relative to Ast_min,
    # while still forcing the web-neutral-axis solver path.
    from structural_lib import flexure

    res = flexure.design_flanged_beam(
        bw=300,
        bf=300,
        d=1000,
        Df=205,
        d_total=1200,
        mu_knm=25.0,
        fck=1.0,
        fy=415,
    )

    assert res.ast_required > 0
    assert "minimum steel" in res.error_message.lower()


def test_flexure_flanged_beam_solver_hits_ast_max_exceeded_branch():
    from structural_lib import flexure

    # Force the combined (web + flange) Ast to exceed the 4% bw*d_total cap.
    # Keep geometry valid (d_total > d).
    res = flexure.design_flanged_beam(
        bw=150,
        bf=800,
        d=450,
        Df=80,
        d_total=500,
        mu_knm=600.0,
        fck=20,
        fy=415,
    )

    assert res.is_safe is False
    assert "maximum" in res.error_message.lower()


def test_tables_get_tc_value_breaks_on_upper_grade_boundary():
    # fck between 20 and 25 should pick 20 (nearest lower grade), executing the break path.
    assert tables.get_tc_value(22.0, 0.5) == pytest.approx(
        tables.get_tc_value(20.0, 0.5)
    )


def test_tables_get_tc_max_value_interpolation_segments():
    # Hit each interpolation segment branch.
    assert tables.get_tc_max_value(17.5) == pytest.approx(
        tables.utilities.linear_interp(17.5, 15.0, 2.5, 20.0, 2.8)
    )
    assert tables.get_tc_max_value(32.0) == pytest.approx(
        tables.utilities.linear_interp(32.0, 30.0, 3.5, 35.0, 3.7)
    )
    assert tables.get_tc_max_value(37.0) == pytest.approx(
        tables.utilities.linear_interp(37.0, 35.0, 3.7, 40.0, 4.0)
    )


def test_excel_integration_process_single_beam_exception_path(monkeypatch, tmp_path):
    from structural_lib import excel_integration

    beam = excel_integration.BeamDesignData(
        beam_id="B1",
        story="S1",
        b=230,
        D=450,
        d=400,
        span=4000,
        cover=40,
        fck=25,
        fy=415,
        Mu=100,
        Vu=100,
        Ast_req=1000,
        Asc_req=0,
        stirrup_dia=8,
        stirrup_spacing=150,
        status="OK",
    )

    def boom(*_a, **_k):
        raise RuntimeError("boom")

    monkeypatch.setattr(excel_integration, "create_beam_detailing", boom)
    res = excel_integration.process_single_beam(
        beam, str(tmp_path), is_seismic=False, generate_dxf=False
    )
    assert res.success is False
    assert "boom" in (res.error or "")


def test_excel_integration_generate_detailing_schedule_handles_missing_bottom_bars():
    from structural_lib.excel_integration import (
        ProcessingResult,
        generate_detailing_schedule,
    )
    from structural_lib.detailing import (
        BeamDetailingResult,
        BarArrangement,
        StirrupArrangement,
    )

    detailing = BeamDetailingResult(
        beam_id="B1",
        story="S1",
        b=300,
        D=500,
        span=4000,
        cover=40,
        top_bars=[
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=120, layers=1
            )
        ],
        bottom_bars=[],
        stirrups=[
            StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000)
        ],
        ld_tension=600,
        ld_compression=500,
        lap_length=700,
        is_valid=True,
        remarks="OK",
    )

    results = [
        ProcessingResult(
            beam_id="B1",
            story="S1",
            success=True,
            dxf_path=None,
            detailing=detailing,
            error=None,
        )
    ]
    schedule = generate_detailing_schedule(results)
    assert schedule[0]["Bottom_Main"] == "-"


def test_excel_integration_export_schedule_to_csv_empty_schedule_noop(tmp_path):
    from structural_lib.excel_integration import export_schedule_to_csv

    export_schedule_to_csv([], str(tmp_path / "schedule.csv"))


def test_excel_integration_from_dict_keeps_provided_eff_d_value():
    from structural_lib.excel_integration import BeamDesignData

    data = {
        "beam_id": "B1",
        "story": "S1",
        "b": 230,
        "D": 450,
        "eff_d": 410,
        "span": 4000,
        "cover": 40,
        "fck": 25,
        "fy": 415,
        "Mu": 100,
        "Vu": 100,
        "Ast_req": 1000,
        "stirrup_dia": 8,
        "stirrup_spacing": 150,
    }

    beam = BeamDesignData.from_dict(data)
    assert beam.d == pytest.approx(410.0)


def test_excel_integration_from_dict_d_does_not_override_explicit_D():
    # Covers the conflict-handling branch where legacy lowercase 'd' (meaning depth)
    # should not overwrite an explicitly provided 'D'.
    from structural_lib.excel_integration import BeamDesignData

    data = {
        "beam_id": "B1",
        "story": "S1",
        "b": 230,
        "D": 450,
        "d": 999,
        "span": 4000,
        "cover": 40,
        "fck": 25,
        "fy": 415,
        "Mu": 100,
        "Vu": 100,
        "Ast_req": 1000,
        "stirrup_dia": 8,
        "stirrup_spacing": 150,
    }

    beam = BeamDesignData.from_dict(data)
    assert beam.D == pytest.approx(450.0)
    assert beam.d == pytest.approx(410.0)


def test_dxf_export_runs_as_main_help_exits_cleanly(monkeypatch):
    # Covers the __main__ guard without requiring ezdxf or input files.
    monkeypatch.setattr(sys, "argv", ["structural_lib.dxf_export", "--help"])
    with pytest.raises(SystemExit):
        sys.modules.pop("structural_lib.dxf_export", None)
        runpy.run_module("structural_lib.dxf_export", run_name="__main__")


def test_dxf_export_importerror_sets_ezdxf_unavailable(monkeypatch):
    # Force the top-level ezdxf import to fail so the ImportError branch executes.
    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "ezdxf" or name.startswith("ezdxf."):
            raise ImportError("forced")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    sys.modules.pop("structural_lib.dxf_export", None)
    sys.modules.pop("ezdxf", None)

    mod = importlib.import_module("structural_lib.dxf_export")
    assert mod.EZDXF_AVAILABLE is False


def test_flexure_flanged_bisection_else_branch_with_nan_mu():
    # Use NaN Mu to ensure the bisection loop never meets the convergence check
    # (abs(NaN) < tol is False) and the for-else fallback executes.
    from structural_lib import flexure

    res = flexure.design_flanged_beam(
        bw=300,
        bf=900,
        d=450,
        Df=120,
        d_total=500,
        mu_knm=float("nan"),
        fck=25,
        fy=415,
    )

    assert math.isfinite(res.xu)
    assert res.ast_required > 0
