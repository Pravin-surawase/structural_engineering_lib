"""Observable ETABS discovery behavior, entirely independent of installed ETABS."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only
_SPEC = importlib.util.spec_from_file_location(
    "etabs_api", Path(__file__).resolve().parents[2] / "scripts/etabs_api.py"
)
assert _SPEC and _SPEC.loader
api = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(api)


@pytest.fixture(scope="module")
def catalog():
    return api.load_catalog()


def test_portable_catalog_covers_every_present_method_and_routes_workflows(catalog):
    report = api.coverage(catalog, api.load_workflows())
    assert report["method_names_present"] > 1000
    assert report["methods_with_help"] == report["method_names_present"]
    assert report["target_methods_invoked"] == 0
    assert api.validate(catalog, api.load_workflows()) == []


def test_method_card_preserves_paths_enums_and_actual_defaults(catalog):
    card = api.card(catalog, api.select_member(catalog, "cFrameObj.SetSection"), {})
    assert card["object_path"] == "SapModel.FrameObj.SetSection"
    assert card["effect"] == "write"
    params = {p["Name"]: p for p in card["signatures"][0]["Parameters"]}
    assert not params["PropName"]["HasDefaultValue"]
    assert params["ItemType"]["HasDefaultValue"]
    assert params["ItemType"]["DefaultValue"] == 0
    assert card["enums"][0]["Type"] == "ETABSv1.eItemType"
    force = api.card(catalog, api.select_member(catalog, "FrameForce"), {})
    assert force["object_path"] == "SapModel.Results.FrameForce"
    assert (
        api.navigation(catalog)["ETABSv1.cAnalysisResultsSetup"]
        == "SapModel.Results.Setup"
    )


def test_missing_ambiguous_and_unknown_methods_cannot_gain_qualification(catalog):
    missing = api.select_member(catalog, "cDesignConcrete.GetComboStrength")
    assert missing["Status"] == "missing" and not missing["Methods"]
    with pytest.raises(ValueError, match="Expected one exact method"):
        api.select_member(catalog, "GetNameList")
    with pytest.raises(ValueError, match="found 0"):
        api.select_member(catalog, "cFile.Close")
    unknown = next(
        m
        for m in catalog["inventory"]["Members"]
        if m["Capability"]["Effect"] == "unclassified"
    )
    assert api.card(catalog, unknown, {})["effect"] == "unclassified"
    assert (
        api.select_member(catalog, "cDatabaseTables.GetTableForDisplayCSVFile")[
            "Capability"
        ]["Effect"]
        == "external_file_write"
    )


def test_task_search_finds_methods_and_cli_pages_without_dumping_inventory(
    catalog, capsys
):
    names = [
        m["method"] for m in api.search(catalog, "beam forces", api.load_workflows())
    ]
    assert "ETABSv1.cAnalysisResults.FrameForce" in names
    assert api.main(["search", "GetNameList", "--limit", "2", "--offset", "1"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert len(result["results"]) == 2 < result["total"]
    assert result["offset"] == 1


def test_interface_map_accounts_for_every_method_without_upgrading_evidence(catalog):
    rows = api.interface_coverage(catalog, api.load_workflows())
    inv = catalog["inventory"]
    assert {row["interface"] for row in rows} == set(inv["Interfaces"])
    assert len(rows) == len(inv["Interfaces"])
    assert sum(row["present_methods"] for row in rows) == sum(
        bool(member["Methods"]) for member in inv["Members"]
    )
    assert sum(row["properties"] for row in rows) == len(inv["Properties"])
    assert sum(row["missing_candidates"] for row in rows) == sum(
        not member["Methods"] for member in inv["Members"]
    )
    for row in rows:
        assert (
            row["recipe_mapped_methods"] + row["without_recipe"]
            == row["present_methods"]
        )
        assert row["documented_methods"] <= row["present_methods"]
    analysis = next(row for row in rows if row["interface"] == "ETABSv1.cAnalyze")
    assert "owned_reanalysis" in analysis["workflows"]
    assert not api.select_member(catalog, "cAnalyze.RunAnalysis")["RegisteredGetters"]
    missing = next(row for row in rows if row["interface"] == "ETABSv1.cDesignConcrete")
    assert missing["missing_candidates"] == 1


def test_coverage_cli_pages_filters_navigation_and_keeps_global_totals(capsys):
    assert api.main(["coverage", "--limit", "2", "--offset", "1"]) == 0
    page = json.loads(capsys.readouterr().out)
    assert len(page["interfaces"]) == 2 < page["total_interfaces"]
    assert page["offset"] == 1
    assert api.main(["coverage", "--filter", "sapmodel.results"]) == 0
    filtered = json.loads(capsys.readouterr().out)
    assert filtered["matching_interfaces"] < page["total_interfaces"]
    assert {row["interface"] for row in filtered["interfaces"]} == {
        "ETABSv1.cAnalysisResults",
        "ETABSv1.cAnalysisResultsSetup",
    }
    assert filtered["totals"] == page["totals"]
    assert "Live qualification is not inferred" in filtered["qualification"]


def test_workflow_verification_links_fail_when_evidence_or_tests_disappear(catalog):
    flows = copy.deepcopy(api.load_workflows())
    flows["forces"]["verification"]["evidence"].append("absent-evidence.json")
    flows["recovery"]["verification"]["tests"] = ["absent-tests.cs"]
    flows["owned_reanalysis"]["verification"]["qualification"] = ""
    errors = api.validate(catalog, flows)
    assert any("forces: missing evidence absent-evidence.json" in err for err in errors)
    assert any("recovery: missing test absent-tests.cs" in err for err in errors)
    assert any("owned_reanalysis: missing verification scope" in err for err in errors)


@pytest.fixture
def source_files(tmp_path):
    assembly = tmp_path / "ETABSv1.dll"
    assembly.write_bytes(b"metadata fixture, not a loadable DLL")
    chm = tmp_path / "fixture.chm"
    chm.write_bytes(b"fixture only")
    root = tmp_path / "help"
    (root / "html").mkdir(parents=True)
    topic = root / "html/frame.htm"
    topic.write_text(
        '<html><head><meta name="Microsoft.Help.Id" content="M:ETABSv1.cAnalysisResults.FrameForce" /></head><body>Assembly (2.16.0.0)<h4>Parameters</h4><dl><dt>Name</dt><dd>Frame identifier<script>forbidden()</script></dd></dl><h4>Return Value</h4><p>Status</p></body></html>',
        encoding="utf-8",
    )
    inventory = tmp_path / "inventory.json"
    inv = {
        "SchemaVersion": "structural.etabs_api_inventory/v2",
        "TargetMethodsInvoked": 0,
        "AssemblyIdentity": "fixture",
        "Members": [],
        "Properties": [],
        "Interfaces": [],
        "Enums": [],
    }
    inventory.write_text(
        json.dumps(
            {
                "sourceAssemblySha256": api.digest(assembly),
                "sourceAssemblyFileVersion": "2.16.0.0",
                "inventory": inv,
            }
        ),
        encoding="utf-8",
    )
    return inventory, assembly, chm, root


def test_refresh_is_deterministic_and_rejects_changed_source_or_help(source_files):
    first = api.build_catalog(*source_files)
    assert first == api.build_catalog(*source_files)
    _, assembly, _, root = source_files
    original = assembly.read_bytes()
    assembly.write_bytes(b"changed assembly")
    with pytest.raises(ValueError, match="Assembly differs"):
        api.build_catalog(*source_files)
    assembly.write_bytes(original)
    topic = root / "html/frame.htm"
    topic.write_text(
        topic.read_text().replace("2.16.0.0", "2.15.0.0"), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="file-version mismatch"):
        api.build_catalog(*source_files)


def test_local_help_returns_only_requested_section_and_rejects_drift(
    source_files, catalog
):
    built = api.build_catalog(*source_files)
    member = api.select_member(catalog, "FrameForce")
    root = source_files[3]
    text = api.read_help(built, member, root, "parameters")
    assert "Frame identifier" in text
    assert "forbidden" not in text and "Status" not in text
    assert api.read_help(built, member, root, "returns") == "Status"
    (root / "html/frame.htm").write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="differs from the pinned"):
        api.read_help(built, member, root, "parameters")


def test_installed_hash_check_fails_without_silently_rebinding(tmp_path, capsys):
    dll = tmp_path / "different.dll"
    dll.write_bytes(b"different")
    assert api.main(["check", "--assembly", str(dll)]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "FAIL"
    assert not result["installed_identity_checked"]
    assert "assembly drift" in result["errors"][0]


def test_workflow_reference_breakage_is_reported(catalog):
    workflows = copy.deepcopy(api.load_workflows())
    workflows["forces"]["methods"].append("ETABSv1.cFile.Invented")
    assert any(
        "unknown method" in message for message in api.validate(catalog, workflows)
    )
