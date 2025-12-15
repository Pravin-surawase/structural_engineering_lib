import json

import pytest

from structural_lib.excel_integration import (
    BeamDesignData,
    ProcessingResult,
    export_schedule_to_csv,
    generate_detailing_schedule,
    generate_summary_report,
    load_beam_data_from_csv,
    load_beam_data_from_json,
    batch_generate_dxf,
    process_single_beam,
)

from structural_lib.detailing import (
    BarArrangement,
    BeamDetailingResult,
    StirrupArrangement,
)


def test_beam_design_data_from_dict_unknown_keys_use_lowercase():
    # Unknown keys should be normalized via key.lower() without breaking required parsing.
    beam = BeamDesignData.from_dict(
        {
            "BeamID": "B1",
            "Story": "S1",
            "b": 300,
            "D": 500,
            "Span": 4000,
            "Cover": 40,
            "fck": 25,
            "fy": 500,
            "Mu": 150,
            "Vu": 100,
            "Ast_req": 900,
            "Asc_req": 0,
            "Stirrup_Dia": 8,
            "Stirrup_Spacing": 150,
            "WeirdKey": "IGNORED",
        }
    )

    assert beam.beam_id == "B1"
    assert beam.story == "S1"


def test_load_beam_data_from_json_invalid_format(tmp_path):
    p = tmp_path / "bad.json"
    # Dict but missing 'beams' key, and not a list => invalid
    p.write_text(json.dumps({"foo": 123}), encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON format"):
        load_beam_data_from_json(str(p))


def test_batch_generate_dxf_unsupported_extension(tmp_path):
    p = tmp_path / "input.txt"
    p.write_text("hello", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file format"):
        batch_generate_dxf(str(p), str(tmp_path / "out"))


def test_process_single_beam_can_skip_dxf_when_disabled(tmp_path):
    beam = BeamDesignData.from_dict(
        {
            "BeamID": "B1",
            "Story": "S1",
            "b": 300,
            "D": 500,
            "Span": 4000,
            "Cover": 40,
            "fck": 25,
            "fy": 500,
            "Mu": 150,
            "Vu": 100,
            "Ast_req": 900,
            "Asc_req": 0,
            "Stirrup_Dia": 8,
            "Stirrup_Spacing": 150,
        }
    )

    res = process_single_beam(beam, str(tmp_path / "out"), generate_dxf=False)
    assert res.success is True
    assert res.dxf_path is None
    assert res.detailing is not None


def test_process_single_beam_reports_missing_ezdxf(monkeypatch, tmp_path):
    # Force the integration layer to behave as if ezdxf is unavailable.
    import structural_lib.excel_integration as excel_integration

    monkeypatch.setattr(excel_integration, "EZDXF_AVAILABLE", False, raising=True)

    beam = BeamDesignData.from_dict(
        {
            "BeamID": "B1",
            "Story": "S1",
            "b": 300,
            "D": 500,
            "Span": 4000,
            "Cover": 40,
            "fck": 25,
            "fy": 500,
            "Mu": 150,
            "Vu": 100,
            "Ast_req": 900,
            "Asc_req": 0,
            "Stirrup_Dia": 8,
            "Stirrup_Spacing": 150,
        }
    )

    res = process_single_beam(beam, str(tmp_path / "out"), generate_dxf=True)
    assert res.success is True
    assert res.dxf_path is None
    assert res.detailing is not None
    assert res.error is not None
    assert "ezdxf not installed" in res.error


def test_process_single_beam_generates_dxf_when_available(monkeypatch, tmp_path):
    import structural_lib.excel_integration as excel_integration

    # Force DXF path and stub the generator.
    monkeypatch.setattr(excel_integration, "EZDXF_AVAILABLE", True, raising=True)

    called = {"path": None}

    def _fake_generate_beam_dxf(detailing, out_path):
        called["path"] = out_path
        return out_path

    monkeypatch.setattr(
        excel_integration, "generate_beam_dxf", _fake_generate_beam_dxf, raising=True
    )

    beam = BeamDesignData.from_dict(
        {
            "BeamID": "B1",
            "Story": "S1",
            "b": 300,
            "D": 500,
            "Span": 4000,
            "Cover": 40,
            "fck": 25,
            "fy": 500,
            "Mu": 150,
            "Vu": 100,
            "Ast_req": 900,
            "Asc_req": 0,
            "Stirrup_Dia": 8,
            "Stirrup_Spacing": 150,
        }
    )

    out_dir = tmp_path / "out"
    res = process_single_beam(beam, str(out_dir), generate_dxf=True)
    assert res.success is True
    assert res.dxf_path is not None
    assert called["path"] == res.dxf_path
    assert out_dir.exists()


def test_batch_generate_dxf_json_extension(monkeypatch, tmp_path, capsys):
    import structural_lib.excel_integration as excel_integration

    p = tmp_path / "beams.json"
    p.write_text(
        json.dumps(
            [
                {
                    "BeamID": "B1",
                    "Story": "S1",
                    "b": 300,
                    "D": 500,
                    "Span": 4000,
                    "Cover": 40,
                    "fck": 25,
                    "fy": 500,
                    "Mu": 150,
                    "Vu": 100,
                    "Ast_req": 900,
                    "Asc_req": 0,
                    "Stirrup_Dia": 8,
                    "Stirrup_Spacing": 150,
                }
            ]
        ),
        encoding="utf-8",
    )

    def _stub_process_single_beam(
        beam, output_folder, is_seismic=False, generate_dxf=True
    ):
        return ProcessingResult(
            beam_id=beam.beam_id,
            story=beam.story,
            success=True,
            dxf_path=None,
            detailing=None,
            error=None,
        )

    monkeypatch.setattr(
        excel_integration, "process_single_beam", _stub_process_single_beam
    )

    res = batch_generate_dxf(str(p), str(tmp_path / "out"), is_seismic=False)
    assert len(res) == 1
    out = capsys.readouterr().out
    assert "S1/B1" in out


def test_beam_design_data_from_dict_applies_defaults_and_computes_d():
    beam = BeamDesignData.from_dict(
        {
            "BeamID": "B1",
            "Story": "S1",
            "b": 300,
            "D": 500,
            "Span": 4000,
            "Cover": "",  # should default to 40
            "fck": 25,
            "fy": 500,
            "Mu": 150,
            "Vu": 100,
            "Ast_req": 900,
            "Asc_req": "",  # should default to 0
            "Stirrup_Dia": 8,
            "Stirrup_Spacing": 150,
            "Status": "",  # should default to OK
        }
    )

    assert beam.cover == 40.0
    assert beam.d == pytest.approx(500.0 - 40.0)
    assert beam.Asc_req == 0.0
    assert beam.status == "OK"


def test_load_beam_data_from_csv_skips_invalid_rows_and_warns(tmp_path, capsys):
    p = tmp_path / "beams.csv"
    p.write_text(
        "BeamID,Story,b,D,Span,Cover,fck,fy,Mu,Vu,Ast_req,Asc_req,Stirrup_Dia,Stirrup_Spacing\n"
        "B1,S1,300,500,4000,40,25,500,150,100,900,0,8,150\n"
        "B2,S1,BAD,500,4000,40,25,500,150,100,900,0,8,150\n",
        encoding="utf-8",
    )

    beams = load_beam_data_from_csv(str(p))
    assert len(beams) == 1
    assert beams[0].beam_id == "B1"

    out = capsys.readouterr().out
    assert "Warning: Skipping row" in out


def test_batch_generate_dxf_logs_progress(monkeypatch, tmp_path, capsys):
    import structural_lib.excel_integration as excel_integration

    p = tmp_path / "beams.csv"
    p.write_text(
        "BeamID,Story,b,D,Span,Cover,fck,fy,Mu,Vu,Ast_req,Asc_req,Stirrup_Dia,Stirrup_Spacing\n"
        "B1,S1,300,500,4000,40,25,500,150,100,900,0,8,150\n",
        encoding="utf-8",
    )

    def _stub_process_single_beam(
        beam, output_folder, is_seismic=False, generate_dxf=True
    ):
        return ProcessingResult(
            beam_id=beam.beam_id,
            story=beam.story,
            success=True,
            dxf_path=None,
            detailing=None,
            error=None,
        )

    monkeypatch.setattr(
        excel_integration, "process_single_beam", _stub_process_single_beam
    )

    res = batch_generate_dxf(str(p), str(tmp_path / "out"), is_seismic=False)
    assert len(res) == 1
    assert res[0].success is True

    out = capsys.readouterr().out
    assert "S1/B1" in out


def test_generate_summary_report_includes_failed_and_generated_files(tmp_path):
    results = [
        ProcessingResult(
            beam_id="B1",
            story="S1",
            success=False,
            dxf_path=None,
            detailing=None,
            error="boom",
        ),
        ProcessingResult(
            beam_id="B2",
            story="S1",
            success=True,
            dxf_path=str(tmp_path / "B2.dxf"),
            detailing=None,
            error=None,
        ),
    ]

    report = generate_summary_report(results)
    assert "Failed Beams" in report
    assert "S1/B1" in report
    assert "Generated Files" in report
    assert "B2.dxf" in report


def test_generate_detailing_schedule_and_export_to_csv(tmp_path):
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
        bottom_bars=[
            BarArrangement(
                count=2, diameter=16, area_provided=402, spacing=120, layers=1
            ),
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=110, layers=1
            ),
        ],
        stirrups=[
            StirrupArrangement(diameter=8, legs=2, spacing=100, zone_length=1000),
            StirrupArrangement(diameter=8, legs=2, spacing=150, zone_length=2000),
        ],
        ld_tension=600,
        ld_compression=500,
        lap_length=700,
        is_valid=True,
        remarks="OK",
    )

    results = [
        ProcessingResult(
            beam_id="B0",
            story="S1",
            success=False,
            dxf_path=None,
            detailing=None,
            error="fail",
        ),
        ProcessingResult(
            beam_id="B1",
            story="S1",
            success=True,
            dxf_path=str(tmp_path / "B1.dxf"),
            detailing=detailing,
            error=None,
        ),
        ProcessingResult(
            beam_id="B2",
            story="S1",
            success=True,
            dxf_path=None,
            detailing=None,
            error=None,
        ),
    ]

    schedule = generate_detailing_schedule(results)
    assert len(schedule) == 1
    row = schedule[0]
    assert row["Story"] == "S1"
    assert row["Beam"] == "B1"
    assert row["Bottom_Main"] == "3-16φ"
    assert row["Top_Main"] == "2-16φ"
    assert row["Stirrups_End"].startswith("2L-8φ")

    out_csv = tmp_path / "schedule.csv"
    export_schedule_to_csv(schedule, str(out_csv))
    assert out_csv.exists()

    content = out_csv.read_text(encoding="utf-8")
    assert "Story" in content.splitlines()[0]
    assert "Beam" in content.splitlines()[0]


def test_generate_detailing_schedule_with_single_stirrup_uses_end_for_mid(tmp_path):
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
        bottom_bars=[
            BarArrangement(
                count=3, diameter=16, area_provided=603, spacing=110, layers=1
            )
        ],
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
    assert len(schedule) == 1
    assert schedule[0]["Stirrups_Mid"].startswith("2L-8φ")


def test_excel_integration_cli_main_with_schedule(monkeypatch, tmp_path, capsys):
    import structural_lib.excel_integration as excel_integration

    # Stub the batch processing to avoid heavy work.
    fake_results = [
        ProcessingResult(
            beam_id="B1",
            story="S1",
            success=True,
            dxf_path=None,
            detailing=None,
            error=None,
        )
    ]

    monkeypatch.setattr(
        excel_integration, "batch_generate_dxf", lambda *_args, **_kwargs: fake_results
    )
    monkeypatch.setattr(
        excel_integration, "generate_summary_report", lambda _r: "SUMMARY"
    )
    monkeypatch.setattr(
        excel_integration,
        "generate_detailing_schedule",
        lambda _r: [{"Story": "S1", "Beam": "B1"}],
    )

    schedule_path = tmp_path / "schedule.csv"

    monkeypatch.setattr(
        __import__("sys"),
        "argv",
        [
            "excel_integration",
            str(tmp_path / "in.csv"),
            "-o",
            str(tmp_path / "out"),
            "--schedule",
            str(schedule_path),
        ],
        raising=True,
    )

    excel_integration.main()

    out = capsys.readouterr().out
    assert "Processing:" in out
    assert "SUMMARY" in out
    assert "Schedule exported to" in out


def test_excel_integration_runs_as_main_via_runpy(tmp_path, monkeypatch):
    # Covers the module-level __main__ guard deterministically with an empty CSV.
    import runpy
    import sys

    p = tmp_path / "empty.csv"
    p.write_text(
        "BeamID,Story,b,D,Span,Cover,fck,fy,Mu,Vu,Ast_req,Asc_req,Stirrup_Dia,Stirrup_Spacing\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        __import__("sys"),
        "argv",
        ["excel_integration", str(p), "-o", str(tmp_path / "out")],
        raising=True,
    )

    # Should run without exceptions (no beams => no DXF generation).
    sys.modules.pop("structural_lib.excel_integration", None)
    runpy.run_module("structural_lib.excel_integration", run_name="__main__")
