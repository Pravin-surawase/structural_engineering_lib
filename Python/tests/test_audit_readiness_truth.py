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
            "check_function_quality.py": (0, "Summary: all pass", ""),
            "audit_input_validation.py": (0, "Overall Grade: A", ""),
        },
    )

    assert report.passed == 3
    assert report.verdict == "PASS"
