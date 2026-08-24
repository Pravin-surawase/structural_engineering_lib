"""LIB-PRO-007-P7 compatibility ownership and caller convergence."""

from __future__ import annotations

import ast
import importlib
import importlib.util
import inspect
import json
import sys
import warnings
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

import structural_lib
from structural_lib import api as compatibility_api
from structural_lib.services import api as service_api
from structural_lib.services.adapters import ETABSAdapter

pytestmark = pytest.mark.repo_only

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / "scripts" / "generate_api_classification.py"
_LEDGER_PATH = _REPO_ROOT / "docs/reference/api-compatibility-ledger.json"
_SPEC = importlib.util.spec_from_file_location("p7_api_classification", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
classification = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = classification
_SPEC.loader.exec_module(classification)


def _resolve(qualified_path: str) -> Any:
    parts = qualified_path.split(".")
    for split in range(len(parts), 0, -1):
        try:
            value: Any = importlib.import_module(".".join(parts[:split]))
        except ModuleNotFoundError:
            continue
        for part in parts[split:]:
            value = getattr(value, part)
        return value
    raise AssertionError(f"Could not resolve {qualified_path}")


@pytest.fixture(scope="module")
def ledger() -> dict[str, Any]:
    return classification.build_compatibility_ledger()


def test_facade_projection_ledger_reconciles_live_classification(
    ledger: dict[str, Any],
) -> None:
    reconciliation = ledger["classification_reconciliation"]

    assert reconciliation["exactly_reconciled"] is True
    assert reconciliation["classification_projection_count"] == sum(
        surface["classified_symbol_count"]
        for surface in classification.build_registry()["surfaces"]
    )
    assert reconciliation["ledger_projection_count"] == len(
        ledger["facade_projections"]
    )
    assert ledger["summary"]["blocked_ambiguous_caller_count"] == 0
    assert ledger["blocked_ambiguous_callers"] == []


def test_all_facade_projections_preserve_object_and_signature_identity(
    ledger: dict[str, Any],
) -> None:
    for projection in ledger["facade_projections"]:
        module_name, public_name = projection["qualified_path"].rsplit(".", 1)
        exposed = getattr(importlib.import_module(module_name), public_name)
        owner = _resolve(projection["canonical_owner"])

        if projection["identity_behavior"] == "MODULE_NAMESPACE_DELEGATE":
            assert isinstance(exposed, ModuleType)
            assert isinstance(owner, ModuleType)
            symbol_owners = projection["namespace_symbol_owners"]
            assert symbol_owners
            assert all(
                hasattr(exposed, name)
                and getattr(exposed, name) is _resolve(symbol_owner)
                for name, symbol_owner in symbol_owners.items()
            )
        else:
            assert exposed is owner, projection["qualified_path"]
            assert classification._signature(exposed) == projection["signature"]
            for facade in projection["facades_exposing_same_object"]:
                assert (
                    getattr(importlib.import_module(facade), projection["public_name"])
                    is owner
                )


def test_root_stub_modules_are_pure_identity_delegates(
    ledger: dict[str, Any],
) -> None:
    for module_record in ledger["root_stub_modules"]:
        source = _REPO_ROOT / module_record["source_path"]
        tree = ast.parse(source.read_text(encoding="utf-8"))

        assert not any(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            for node in tree.body
        )
        assert module_record["proposed_disposition"] == (
            "DELEGATING_COMPATIBILITY_SHIM"
        )

    for projection in ledger["root_stub_projections"]:
        exposed = _resolve(projection["qualified_path"])
        owner = _resolve(projection["canonical_owner"])

        assert exposed is owner, projection["qualified_path"]
        if projection["identity_behavior"] == "OPTIONAL_DEPENDENCY_SAME_OBJECT":
            assert projection["kind"] == "optional_dependency_proxy"
            assert projection["signature"] == ""
            assert projection["runtime_availability"] == "OPTIONAL_EZDXF"
        else:
            assert classification._signature(exposed) == projection["signature"]


def test_optional_dependency_stub_identity_is_environment_independent() -> None:
    for qualified_path in classification._OPTIONAL_DEPENDENCY_STUB_SYMBOLS:
        owner = qualified_path.replace(
            "structural_lib.dxf_export", "structural_lib.services.dxf_export"
        )
        installed = classification._stub_projection_identity(
            qualified_path, owner, object()
        )
        absent = classification._stub_projection_identity(qualified_path, owner, None)

        assert installed == absent
        assert installed["identity_behavior"] == "OPTIONAL_DEPENDENCY_SAME_OBJECT"


def test_signature_identity_is_python_version_independent() -> None:
    assert classification._signature(structural_lib.LoadType) == "(value)"

    model_signature = classification._signature(structural_lib.BeamGeometry)
    assert "Annotated[" in model_signature
    assert "typing.Annotated[" not in model_signature


def test_api_hub_is_an_identity_only_subset(ledger: dict[str, Any]) -> None:
    record = ledger["additional_module_records"][0]
    hub = importlib.import_module("structural_lib.services.api_hub")

    assert record["qualified_path"] == hub.__name__
    assert record["identity_mismatches"] == []
    assert record["proposed_disposition"] == "DELEGATING_COMPATIBILITY_SHIM"
    assert set(hub.__all__) < set(service_api.__all__)
    assert all(getattr(hub, name) is getattr(service_api, name) for name in hub.__all__)


def test_deprecated_stub_warning_metadata_matches_runtime(
    ledger: dict[str, Any],
) -> None:
    deprecated_modules = [
        item
        for item in ledger["root_stub_modules"]
        if item["migration_metadata"]["status"] == "DEPRECATED_IMPORT_PATH"
    ]

    assert deprecated_modules
    for item in deprecated_modules:
        expected = item["migration_metadata"]["warning"]
        module = importlib.import_module(item["qualified_path"])
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always", DeprecationWarning)
            importlib.reload(module)

        deprecations = [
            warning
            for warning in captured
            if issubclass(warning.category, DeprecationWarning)
        ]
        assert len(deprecations) == 1
        assert str(deprecations[0].message) == expected["message"]
        assert expected["category"] == "DeprecationWarning"
        assert expected["stacklevel"] == 2
        assert (
            Path(deprecations[0].filename).resolve()
            != (_REPO_ROOT / item["source_path"]).resolve()
        )


def test_p5_legacy_helpers_are_explicitly_held_without_deprecation_warning() -> None:
    held_names = (
        "normalize_etabs_forces",
        "load_etabs_csv",
        "create_job_from_etabs",
        "create_jobs_from_etabs_csv",
    )

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always", DeprecationWarning)
        importlib.reload(compatibility_api)

    assert not [item for item in captured if item.category is DeprecationWarning]
    for name in held_names:
        owner = getattr(service_api, name)
        metadata = owner.__compatibility__

        assert getattr(structural_lib, name) is owner
        assert getattr(compatibility_api, name) is owner
        assert metadata["status"] == "HELD_COMPATIBILITY"
        assert metadata["removal_version"] is None
        assert any(
            token in metadata["limitation"].lower()
            for token in ("snapshot", "projectbeamdesigninputv1")
        )
        assert not hasattr(owner, "__deprecated__")

    assert ETABSAdapter.__compatibility__["status"] == "CANONICAL_OWNER"
    assert ETABSAdapter.__compatibility__["removal_version"] is None
    assert "lossless" in ETABSAdapter.__compatibility__["limitation"].lower()


def test_maintained_callers_have_no_ambiguous_legacy_route(
    ledger: dict[str, Any],
) -> None:
    assert ledger["blocked_ambiguous_callers"] == []
    assert all(
        caller["disposition"]
        in {
            "DELEGATING_COMPATIBILITY_SHIM",
            "INTENTIONAL_PUBLIC_FACADE",
            "MAINTAINED_CALLER_MIGRATED",
            "OUT_OF_SCOPE_PRESERVED",
        }
        for caller in ledger["caller_records"]
    )


def test_caller_scan_uses_tracked_allowlist_and_excludes_generated_site(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    maintained = tmp_path / "docs" / "maintained.md"
    generated = tmp_path / "site" / "search" / "search_index.json"
    maintained.parent.mkdir(parents=True)
    generated.parent.mkdir(parents=True)
    maintained.write_text("structural_lib.design_beam_is456", encoding="utf-8")
    generated.write_text("structural_lib.legacy_unknown", encoding="utf-8")

    git_result = classification.subprocess.CompletedProcess(
        args=["git", "ls-files", "--cached", "-z"],
        returncode=0,
        stdout=b"docs/maintained.md\0site/search/search_index.json\0",
    )
    monkeypatch.setattr(classification, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        classification.subprocess, "run", lambda *args, **kwargs: git_result
    )

    assert classification._iter_text_files() == [maintained]


def test_generated_ledger_matches_live_build(ledger: dict[str, Any]) -> None:
    checked_in = classification._unpack_compatibility_ledger(
        json.loads(_LEDGER_PATH.read_text(encoding="utf-8"))
    )

    assert classification._normalized(checked_in) == classification._normalized(ledger)


def test_checked_in_ledger_uses_lossless_small_file_encoding(
    ledger: dict[str, Any],
) -> None:
    checked_in = json.loads(_LEDGER_PATH.read_text(encoding="utf-8"))

    assert checked_in["encoding"] == "column-dictionary-v1"
    assert _LEDGER_PATH.stat().st_size < 500 * 1024
    assert classification._unpack_compatibility_ledger(checked_in) == ledger


@pytest.mark.parametrize(
    "name",
    [
        "optimize_beam_cost",
        "SuppliedBeamReinforcementV1",
        "evaluate_supplied_beam_reinforcement_v1",
        "TensionBarAnchorageResultV1",
        "evaluate_tension_bar_anchorage_v1",
        "GravityPracticalActionV1",
        "run_gravity_workflow_with_book_v1",
        "normalize_etabs_forces",
        "design_beam_is456",
    ],
)
def test_representative_p1_p6_entrypoints_share_one_object(name: str) -> None:
    owner = getattr(service_api, name)

    assert getattr(structural_lib, name) is owner
    assert getattr(compatibility_api, name) is owner
    assert inspect.signature(getattr(structural_lib, name)) == inspect.signature(owner)
    assert inspect.signature(getattr(compatibility_api, name)) == inspect.signature(
        owner
    )


def test_p7_records_no_authorized_deletion_or_retirement_candidate(
    ledger: dict[str, Any],
) -> None:
    assert ledger["retirement_candidates"] == []
    assert ledger["authorization"] == {
        "deletion_authorized": False,
        "public_contract_break_authorized": False,
        "release_authorized": False,
        "professional_approval": False,
        "engineering_use_approval": False,
    }
