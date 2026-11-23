from __future__ import annotations

import base64
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "examples" / "floor_review" / "demo_intake.py"
spec = importlib.util.spec_from_file_location("demo_intake", DEMO)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
handle_demo_intake = module.handle_demo_intake


def _file(path: Path) -> dict[str, str]:
    return {"name": path.name, "data": base64.b64encode(path.read_bytes()).decode()}


def test_prepared_and_bound_paired_packets_produce_reviews():
    examples = ROOT / "examples" / "floor_review"
    prepared = handle_demo_intake(
        {"mode": "review", "files": [_file(examples / "prepared.csv")]}
    )
    assert prepared["kind"] == "review"
    packet = examples / "etabs-paired"
    paired = handle_demo_intake(
        {
            "mode": "review",
            "files": [
                _file(packet / name)
                for name in ("packet.json", "beam-forces.csv", "column-forces.csv")
            ],
        }
    )
    assert paired["kind"] == "review"
    assert paired["result"]["profile"] == "etabs-paired"


def test_identified_blocked_manifest_returns_its_review_diagnostics():
    packet = ROOT / "examples" / "floor_review" / "etabs-paired" / "packet.json"
    result = handle_demo_intake({"mode": "preview", "files": [_file(packet)]})
    assert result["kind"] == "review"
    assert result["result"]["intake_status"] == "BLOCKED"
    assert result["result"]["issues"]


def test_unbound_csv_is_previewed_and_never_reviewed():
    raw = b"TABLE:  Element Forces - Beams\nStory,Beam,M3,V2\nL2,B1,-120,35\n"
    file = {"name": "forces.csv", "data": base64.b64encode(raw).decode()}
    preview = handle_demo_intake({"mode": "preview", "files": [file]})
    assert preview["kind"] == "tables"
    assert preview["tables"][0]["headers"] == ["Story", "Beam", "M3", "V2"]
    assert preview["tables"][0]["rows"] == [["L2", "B1", "-120", "35"]]
    assert preview["tables"][0]["first_row_number"] == 3
    review = handle_demo_intake({"mode": "review", "files": [file]})
    assert review["kind"] == "tables"
    assert any(
        item["code"] == "UNBOUND_EXPORT_INTAKE_ONLY" for item in review["issues"]
    )


def test_xlsx_e2k_and_edb_boundaries():
    examples = ROOT / "examples" / "floor_review"
    xlsx = handle_demo_intake(
        {"mode": "preview", "files": [_file(examples / "prepared.xlsx")]}
    )
    assert xlsx["kind"] in {"review", "tables"}
    e2k = {"name": "identity.e2k", "data": base64.b64encode(b"$ FILE").decode()}
    archival = handle_demo_intake({"mode": "preview", "files": [e2k]})
    assert archival["kind"] == "tables"
    assert archival["issues"][0]["code"] == "E2K_ARCHIVAL_ONLY"
    edb = {"name": "model.edb", "data": base64.b64encode(b"binary").decode()}
    assert handle_demo_intake({"mode": "preview", "files": [edb]})["kind"] == "error"
    traversal = {"name": "../forces.csv", "data": base64.b64encode(b"x").decode()}
    assert (
        handle_demo_intake({"mode": "preview", "files": [traversal]})["kind"] == "error"
    )


def test_rejects_cross_platform_unsafe_names_and_malformed_mode():
    data = base64.b64encode(b"header\nvalue\n").decode()
    for name in ("CON.csv", "a:b.csv", "one\\two.csv", "table.exe"):
        assert (
            handle_demo_intake(
                {"mode": "preview", "files": [{"name": name, "data": data}]}
            )["kind"]
            == "error"
        )
    assert handle_demo_intake({"mode": ["preview"], "files": []})["kind"] == "error"


def test_generic_csv_first_row_is_header_not_title():
    data = base64.b64encode(b"Story,Beam,M3\nL2,B1,-120\n").decode()
    result = handle_demo_intake(
        {"mode": "preview", "files": [{"name": "generic.csv", "data": data}]}
    )
    table = result["tables"][0]
    assert table["title"] is None
    assert table["headers"] == ["Story", "Beam", "M3"]
    assert table["rows"] == [["L2", "B1", "-120"]]


def test_bound_packet_rejects_an_extra_unaccounted_export():
    examples = ROOT / "examples" / "floor_review"
    packet = examples / "etabs-paired"
    selected = [
        _file(packet / name)
        for name in ("packet.json", "beam-forces.csv", "column-forces.csv")
    ]
    selected.append(_file(examples / "prepared.csv"))
    result = handle_demo_intake({"mode": "review", "files": selected})
    assert result["kind"] == "error"
    assert "prepared.csv" in result["message"]
