"""Regression checks for repository examples advertised to external users."""

from __future__ import annotations

import csv
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest


def test_canonical_workflows_use_public_types_and_complete_user_journeys(
    tmp_path: Path,
) -> None:
    script = Path(__file__).resolve().parents[1] / "examples" / "canonical_workflows.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["beam_bbs_weight_kg"] > 0
    assert result["column_status"] == result["slab_status"] == "PASS"
    assert result["column_check_passed"] is True
    assert result["review_required"] is True
    assert result["rejected_fields"] == ["geometry.b_mm"]
    assert not list(tmp_path.iterdir())


def test_synthetic_pipeline_uses_strict_cli_contract(tmp_path: Path) -> None:
    python_root = Path(__file__).resolve().parents[1]
    script = python_root / "examples" / "full_pipeline_synthetic.py"
    output_dir = tmp_path / "synthetic"

    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--count",
            "3",
            "--skip-dxf",
            "--output-dir",
            str(output_dir),
        ],
        cwd=python_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert (output_dir / "results.json").is_file()
    assert (output_dir / "schedule.csv").is_file()

    with (output_dir / "beams_synthetic_3.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 3
    assert "eff_d" in rows[0]
    assert "Ast_req" not in rows[0]
    assert "Asc_req" not in rows[0]


def _run_cli(*args: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "structural_lib", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_shipped_starter_completes_with_actual_bar_centroid_depths(
    tmp_path: Path,
) -> None:
    source = Path(__file__).resolve().parents[1] / "examples/sample_beam_design.csv"
    results = tmp_path / "results.json"
    schedule = tmp_path / "schedule.csv"
    _run_cli("design", str(source), "-o", str(results))
    _run_cli("detail", str(results), "-o", str(tmp_path / "detailing.json"))
    _run_cli("bbs", str(results), "-o", str(schedule))
    _run_cli(
        "report", str(results), "--format=json", "-o", str(tmp_path / "report.json")
    )

    payload = json.loads(results.read_text(encoding="utf-8"))
    json.dumps(payload, allow_nan=False)
    expected = {
        "B1": (444, 16, 5),
        "B2": (394, 16, 4),
        "B3": (540, 20, 4),
        "B4": (442, 20, 4),
        "B5": (630, 20, 6),
    }
    assert {b["beam_id"] for b in payload["beams"]} == set(expected)
    for beam in payload["beams"]:
        depth, diameter, count = expected[beam["beam_id"]]
        assert beam["is_ok"] is True
        assert beam["geometry"]["d_mm"] == depth
        assert beam["design_inputs"]["d_mm"] == depth
        assert beam["effective_depth_resolution"]["source"] == "DERIVED"
        for zone in beam["detailing"]["bottom_bars"]:
            assert (zone["diameter"], zone["count"]) == (diameter, count)
        geometry = beam["geometry"]
        link = beam["effective_depth_resolution"]["effective_depth_basis"][
            "stirrup_diameter_mm"
        ]
        # Independent physical centroid, rather than D minus clear cover alone.
        assert depth == geometry["D_mm"] - geometry["cover_mm"] - link - diameter / 2

    with schedule.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    members = {r["member_id"] for r in rows if r["member_id"]}
    assert members == set(expected)
    assert sum(int(r["no_of_bars"]) for r in rows if r["member_id"] in expected) == 271
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    for beam in report["beams"]:
        asv = next(x for x in beam["input_sanity"] if x["field"] == "asv_mm2")
        assert asv["status"] == "OK" and asv["value"] > 0


def test_shipped_starter_dxf_matches_its_schedule_marks(tmp_path: Path) -> None:
    ezdxf = pytest.importorskip("ezdxf")
    from structural_lib.services.dxf_export import compare_bbs_dxf_marks

    source = Path(__file__).resolve().parents[1] / "examples/sample_beam_design.csv"
    results, schedule, drawing = (
        tmp_path / n for n in ("results.json", "schedule.csv", "drawing.dxf")
    )
    _run_cli("design", str(source), "-o", str(results))
    _run_cli("bbs", str(results), "-o", str(schedule))
    _run_cli("dxf", str(results), "-o", str(drawing))
    comparison = compare_bbs_dxf_marks(str(schedule), str(drawing))
    assert comparison["ok"], comparison
    texts = list(ezdxf.readfile(drawing).modelspace().query("TEXT"))
    for beam in json.loads(results.read_text(encoding="utf-8"))["beams"]:
        span = beam["geometry"]["span_mm"]
        span_text = next(t for t in texts if t.dxf.text == f"{int(span)} mm")
        bottom = next(
            t
            for t in texts
            if t.dxf.text.startswith(f"Bottom Mid: {beam['beam_id']}-B-M-")
        )
        span_at, bottom_at = span_text.get_placement()[1], bottom.get_placement()[1]
        assert span_at.y - bottom_at.y >= span_text.dxf.height + 25
        stirrup = next(
            t
            for t in texts
            if t.dxf.text.startswith(f"Stirrup Mid: {beam['beam_id']}-")
        )
        stirrup_at = stirrup.get_placement()[1]
        assert bottom_at.y - bottom.dxf.height - stirrup_at.y >= 25
        origin_x = span_at.x - span / 2
        notes = [
            t
            for t in texts
            if t.dxf.text.startswith("Ld =")
            and abs(t.dxf.insert.x - origin_x) < 1e-6
            and t.dxf.insert.y < bottom_at.y
        ]
        note = max(notes, key=lambda t: t.dxf.insert.y)
        assert (bottom_at.y - bottom.dxf.height) - (
            note.dxf.insert.y + note.dxf.height
        ) >= 25
        assert (
            stirrup_at.y - stirrup.dxf.height - (note.dxf.insert.y + note.dxf.height)
            >= 25
        )


@pytest.mark.parametrize(
    "guide, expected_beams",
    [("python-quickstart.md", 5), ("beginners-guide.md", 1), ("colab-workflow.md", 3)],
)
def test_promoted_starter_guide_cells_complete(
    tmp_path: Path, monkeypatch, guide: str, expected_beams: int
) -> None:
    if guide == "colab-workflow.md":
        pytest.importorskip("ezdxf")  # Explicit [dxf] prerequisite in the first cell.
    root = Path(__file__).resolve().parents[2]
    text = (root / "docs/getting-started" / guide).read_text(encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    csv_block = re.search(r"```csv\n(.*?)\n```", text, re.S)
    if csv_block:
        Path("beams.csv").write_text(csv_block[1] + "\n", encoding="utf-8")
        if guide == "python-quickstart.md":
            assert (
                csv_block[1].strip()
                == (root / "Python/examples/sample_beam_design.csv")
                .read_text(encoding="utf-8")
                .strip()
            )
    namespace = {"__name__": "starter_recipe"}
    for block in re.findall(r"```python\n(.*?)\n```", text, re.S):
        if block.lstrip().startswith("%pip"):
            continue  # Exact pin/extra resolution is checked separately, never install during tests.
        if "from google.colab import files" in block:
            for name in (
                "results.json",
                "detailing.json",
                "schedule.csv",
                "drawings.dxf",
                "report.html",
            ):
                assert Path(name).is_file()
            continue  # Colab Files UI is host-specific; check all supplied artifacts locally.
        if block.lstrip().startswith("!python"):
            for line in block.splitlines():
                if not line.strip():
                    continue
                tokens = shlex.split(line.removeprefix("!"))
                assert tokens[:3] == ["python", "-m", "structural_lib"]
                _run_cli(*tokens[3:])
        else:
            exec(
                compile(block, str(root / "docs/getting-started" / guide), "exec"),
                namespace,
            )
    if guide != "colab-workflow.md":
        _run_cli("design", "beams.csv", "-o", "results.json")
        _run_cli("bbs", "results.json", "-o", "schedule.csv")
        _run_cli("report", "results.json", "--format=html", "-o", "report.html")
    results = json.loads(Path("results.json").read_text(encoding="utf-8"))
    assert len(results["beams"]) == expected_beams
    assert all(beam["is_ok"] is True for beam in results["beams"])
    if guide == "colab-workflow.md":
        # The old 230 mm B2 does not fit the generated bars in one layer.
        # Fix the starter geometry, while retaining the unverified-layout gate.
        source = Path("beams.csv")
        source.write_text(
            source.read_text(encoding="utf-8").replace(
                "B2,Ground,240,", "B2,Ground,230,"
            ),
            encoding="utf-8",
        )
        rejected = subprocess.run(
            [
                sys.executable,
                "-m",
                "structural_lib",
                "design",
                "beams.csv",
                "-o",
                "rejected.json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert rejected.returncode != 0
        assert "DETAILING_EFFECTIVE_DEPTH_UNVERIFIED" in rejected.stderr
        assert not Path("rejected.json").exists()


def test_external_cli_harness_uses_the_shipped_strict_starter() -> None:
    import importlib.util

    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location(
        "external_cli_test", root / "scripts/external_cli_test.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkey_name = spec.name
    previous = sys.modules.get(monkey_name)
    try:
        sys.modules[monkey_name] = module
        spec.loader.exec_module(module)
        assert module.SAMPLE_BEAM_DESIGN_CSV == (
            root / "Python/examples/sample_beam_design.csv"
        ).read_text(encoding="utf-8")
    finally:
        if previous is None:
            sys.modules.pop(monkey_name, None)
        else:
            sys.modules[monkey_name] = previous
