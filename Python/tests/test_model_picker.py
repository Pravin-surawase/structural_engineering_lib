"""Tests for the deterministic low-token model picker."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

picker = importlib.import_module("scripts.model_picker")


@pytest.mark.parametrize(
    ("query", "profile"),
    [
        ("format the worklog and regenerate index metadata", "spark-low"),
        ("fix the known lint assertion test", "spark-low"),
        ("implement a normal FastAPI endpoint", "terra-medium"),
        ("diagnose an intermittent cross-layer architecture failure", "terra-high"),
        ("verify the IS456 reinforcement capacity formula", "terra-high"),
    ],
)
def test_model_picker_routes_task_shape(query: str, profile: str) -> None:
    assert picker.recommend(query).profile == profile


def test_critical_work_starts_on_terra_and_approval_gates_sol() -> None:
    result = picker.recommend("production structural release", risk="critical")

    assert result.profile == "terra-high"
    assert result.approval_required is False
    assert result.fallback_profile == "sol-high"
    assert result.fallback_requires_approval is True
    assert "request approval" in result.rationale


@pytest.mark.parametrize(
    "query",
    [
        "plan the next important architecture milestone",
        "brainstorm a complicated migration strategy",
    ],
)
def test_substantial_planning_uses_efficient_terra_default(query: str) -> None:
    result = picker.recommend(query)

    expected = (
        "terra-high"
        if "important" in query or "complicated" in query
        else "terra-medium"
    )
    assert result.profile == expected
    assert result.approval_required is False


def test_mechanical_planning_doc_update_uses_terra_low() -> None:
    result = picker.recommend("format the planning docs")

    assert result.profile == "spark-low"
    assert result.relative_token_rate is None
    assert result.fallback_profile == "terra-low"


def test_main_orchestrator_advises_terra_without_overriding_user_choice() -> None:
    result = picker.recommend("format a simple status note", orchestrator=True)

    assert result.profile == "terra-medium"
    assert result.approval_required is False


def test_low_risk_override_prefers_terra_low() -> None:
    result = picker.recommend("implement a small helper", risk="low")

    assert result.profile == "terra-low"
    assert result.relative_token_rate == 10


def test_model_policy_profiles_are_unique_and_complete() -> None:
    policy = json.loads(
        (REPO_ROOT / "agents" / "model_policy.json").read_text(encoding="utf-8")
    )
    profiles = policy["profiles"]
    ids = {profile["id"] for profile in profiles}

    assert len(ids) == len(profiles)
    assert {
        "spark-low",
        "terra-low",
        "terra-medium",
        "terra-high",
        "sol-medium",
        "sol-high",
    } <= ids
    assert policy["unavailable_models"] == ["gpt-5.6-luna"]
    assert policy["defaults"]["subagent_profile"] == "terra-low"
    assert policy["defaults"]["parent_profile"] == "user-selected"
    assert policy["defaults"]["max_concurrent_subagents"] == 2
    assert policy["preview_models"] == [
        {
            "model": "gpt-5.3-codex-spark",
            "status": "preview",
            "mode": "text-only",
            "billing": "preview-limited and dynamic",
            "quality_note": "Used only for bounded execution and explicit, verification-forward work.",
            "capability_note": "No fixed model-level quality score or guaranteed availability in this repository.",
        }
    ]


def test_model_table_handles_unpriced_preview_profile() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/model_picker.py", "--table"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "spark-low" in result.stdout
    assert "preview" in result.stdout
    assert "Traceback" not in result.stderr
