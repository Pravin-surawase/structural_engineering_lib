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
            "audit_input_validation.py": (0, "Overall Grade: A", ""),
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
            "audit_input_validation.py": (1, "Overall Grade: F", ""),
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
            "audit_input_validation.py": (0, "Overall Grade: A", ""),
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
            "audit_input_validation.py": (0, "Overall Grade: A", ""),
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


@pytest.mark.parametrize(
    ("high_risk", "coverage", "expected"),
    [(0, 90.0, 0), (1, 100.0, 1), (0, 89.9, 1)],
)
def test_input_validation_diagnostic_exit_is_decisive(
    high_risk: int, coverage: float, expected: int
) -> None:
    report = {
        "summary": {
            "high_risk_count": high_risk,
            "average_coverage_percent": coverage,
        }
    }
    assert input_audit.diagnostic_exit_code(report) == expected
