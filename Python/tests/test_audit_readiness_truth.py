"""Readiness must aggregate semantic truth instead of reporting false green."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "audit_readiness_report.py"
_SPEC = importlib.util.spec_from_file_location("audit_readiness_report", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
readiness = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = readiness
_SPEC.loader.exec_module(readiness)

_DOCS_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_docs.py"
_DOCS_SPEC = importlib.util.spec_from_file_location("check_docs", _DOCS_SCRIPT)
assert _DOCS_SPEC is not None and _DOCS_SPEC.loader is not None
docs_check = importlib.util.module_from_spec(_DOCS_SPEC)
sys.modules[_DOCS_SPEC.name] = docs_check
_DOCS_SPEC.loader.exec_module(docs_check)

_INPUT_AUDIT_SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "audit_input_validation.py"
)
_INPUT_AUDIT_SPEC = importlib.util.spec_from_file_location(
    "audit_input_validation", _INPUT_AUDIT_SCRIPT
)
assert _INPUT_AUDIT_SPEC is not None and _INPUT_AUDIT_SPEC.loader is not None
input_audit = importlib.util.module_from_spec(_INPUT_AUDIT_SPEC)
sys.modules[_INPUT_AUDIT_SPEC.name] = input_audit
_INPUT_AUDIT_SPEC.loader.exec_module(input_audit)


def _collect(monkeypatch, outcomes: dict[str, tuple[int, str, str]]):
    calls: list[tuple[str, tuple[str, ...]]] = []

    def fake_run_script(path: str, args=None):
        calls.append((path, tuple(args or ())))
        return outcomes[Path(path).name]

    monkeypatch.setattr(readiness, "run_script", fake_run_script)
    report = readiness.AuditReport()
    readiness.collect_contract_truth_evidence(report)
    report.calculate_verdict()
    return report, calls


def test_required_api_parity_failure_makes_readiness_fail(monkeypatch) -> None:
    report, _calls = _collect(
        monkeypatch,
        {
            "test_api_parity.py": (1, "3/3 parity vectors failed", ""),
            "check_public_route_safety.py": (0, "20 targets passed", ""),
            "check_function_quality.py": (0, "Summary: 88 functions", ""),
            "audit_input_validation.py": (0, "UNPROVEN 0", ""),
        },
    )

    parity = next(item for item in report.evidence if "Parity" in item.name)
    assert parity.required is True
    assert parity.status == "FAIL"
    assert report.verdict == "FAIL"


def test_advisory_quality_debt_prevents_false_green(monkeypatch) -> None:
    report, calls = _collect(
        monkeypatch,
        {
            "test_api_parity.py": (0, "3/3 parity vectors passed", ""),
            "check_public_route_safety.py": (0, "20 targets passed", ""),
            "check_function_quality.py": (
                1,
                "Summary: 88 functions, 26 pass, 62 fail",
                "",
            ),
            "audit_input_validation.py": (1, "UNPROVEN 4", ""),
        },
    )

    assert report.failed == 0
    assert report.warnings == 2
    assert report.verdict == "PARTIAL"
    assert ("scripts/check_function_quality.py", ("--summary", "--strict")) in calls


def test_all_contract_truth_controls_can_report_pass(monkeypatch) -> None:
    report, _calls = _collect(
        monkeypatch,
        {
            "test_api_parity.py": (0, "3/3 parity vectors passed", ""),
            "check_public_route_safety.py": (0, "20 targets passed", ""),
            "check_function_quality.py": (0, "Summary: all pass", ""),
            "audit_input_validation.py": (0, "UNPROVEN 0", ""),
        },
    )

    assert report.passed == 4
    assert report.verdict == "PASS"


def test_public_route_regression_failure_makes_readiness_fail(monkeypatch) -> None:
    report, calls = _collect(
        monkeypatch,
        {
            "test_api_parity.py": (0, "3/3 parity vectors passed", ""),
            "check_public_route_safety.py": (1, "1 failed, 53 passed", ""),
            "check_function_quality.py": (0, "Summary: all pass", ""),
            "audit_input_validation.py": (0, "UNPROVEN 0", ""),
        },
    )

    safety = next(item for item in report.evidence if "Safety" in item.name)
    assert safety.required is True
    assert safety.status == "FAIL"
    assert report.verdict == "FAIL"
    assert ("scripts/check_public_route_safety.py", ()) in calls


@pytest.mark.parametrize(
    ("verdict", "expected"),
    [("PASS", 0), ("FAIL", 1), ("PARTIAL", 2), ("UNKNOWN", 1)],
)
def test_readiness_exit_code_is_decisive(verdict: str, expected: int) -> None:
    assert readiness.verdict_exit_code(verdict) == expected


def test_owner_selected_documentation_hard_cap_is_500() -> None:
    assert docs_check.DOC_BUDGET_WARN == 350
    assert docs_check.DOC_BUDGET_FAIL == 500


@pytest.mark.parametrize(("unproven", "expected"), [(0, 0), (1, 1), (12, 1)])
def test_input_validation_diagnostic_exit_is_decisive(
    unproven: int, expected: int
) -> None:
    report = {
        "summary": {
            "unproven_count": unproven,
        }
    }
    assert input_audit.diagnostic_exit_code(report) == expected


def _analyze_source(source: str, function_name: str = "route"):
    tree = input_audit.ast.parse(source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, input_audit.ast.FunctionDef) and node.name == function_name
    )
    return input_audit._analyze_function(
        function,
        relative_module="synthetic.py",
        filepath=Path("synthetic.py"),
        inventory_basis="synthetic test",
        routes=("synthetic.route",),
    )


def test_input_auditor_attributes_keyword_only_guards_per_parameter() -> None:
    finding = _analyze_source("""
def route(*, guarded: float, unresolved: float) -> float:
    if guarded <= 0:
        raise ValueError("guarded")
    return guarded + unresolved
""")
    statuses = {item.name: item.status for item in finding.parameters}
    assert statuses == {
        "guarded": input_audit.ValidationStatus.PROVEN,
        "unresolved": input_audit.ValidationStatus.UNPROVEN,
    }


def test_input_auditor_recognizes_delegated_validator_and_typed_model() -> None:
    finding = _analyze_source("""
def route(value: float, model: BeamInput, mode: str) -> float:
    require_finite_real("value", value)
    return value
""")
    statuses = {item.name: item.status for item in finding.parameters}
    assert statuses == {
        "value": input_audit.ValidationStatus.DELEGATED,
        "model": input_audit.ValidationStatus.DELEGATED,
        "mode": input_audit.ValidationStatus.NOT_APPLICABLE,
    }


def test_input_auditor_recognizes_guarded_development_length_adapter() -> None:
    finding = _analyze_source("""
def route(bar_diameter: float, fck: float, fy: float) -> dict[str, float]:
    return calculate_development_length(
        bar_dia=bar_diameter,
        fck=fck,
        fy=fy,
    )
""")

    assert {item.name: item.status for item in finding.parameters} == {
        "bar_diameter": input_audit.ValidationStatus.DELEGATED,
        "fck": input_audit.ValidationStatus.DELEGATED,
        "fy": input_audit.ValidationStatus.DELEGATED,
    }


def test_input_auditor_does_not_treat_raw_collection_hint_as_validation() -> None:
    finding = _analyze_source("""
def route(values: list[float]) -> float:
    return sum(values)
""")
    assert finding.parameters[0].status is input_audit.ValidationStatus.UNPROVEN


def test_input_auditor_does_not_treat_ordinary_object_hint_as_model_validation() -> (
    None
):
    finding = _analyze_source("""
def route(path: Path, callback: Callable) -> float:
    return 1.0
""")
    assert all(
        item.status is input_audit.ValidationStatus.UNPROVEN
        for item in finding.parameters
    )


def test_input_auditor_nested_function_state_does_not_leak() -> None:
    finding = _analyze_source("""
def route(value: float) -> float:
    def nested() -> None:
        if value <= 0:
            raise ValueError("nested")
    return value
""")
    assert finding.parameters[0].status is input_audit.ValidationStatus.UNPROVEN


def test_current_input_audit_uses_registry_and_reports_every_unproven() -> None:
    root = Path(__file__).resolve().parents[2]
    functions = input_audit.audit_directory(root)
    report = input_audit.generate_report(functions)

    assert report["schema_version"] == "input-validation-ownership/v1"
    assert report["summary"]["total_functions"] == len(functions)
    assert report["summary"]["unproven_count"] == len(report["unresolved_parameters"])
    assert all(item["status"] == "UNPROVEN" for item in report["unresolved_parameters"])
    assert any(item.inventory_basis == "classified public owner" for item in functions)
    assert any(
        item.inventory_basis == "explicit lower-level compatibility helper"
        for item in functions
    )
