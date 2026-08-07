"""Tests for the deterministic low-token model picker."""

from __future__ import annotations

import importlib
import json
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
        ("format the worklog and regenerate index metadata", "luna-low"),
        ("fix the known lint assertion test", "luna-high"),
        ("implement a normal FastAPI endpoint", "terra-medium"),
        ("diagnose an intermittent cross-layer architecture failure", "terra-high"),
        ("verify the IS456 reinforcement capacity formula", "terra-high"),
    ],
)
def test_model_picker_routes_task_shape(query: str, profile: str) -> None:
    assert picker.recommend(query).profile == profile


def test_critical_work_stops_before_sol_without_approval() -> None:
    result = picker.recommend("production structural release", risk="critical")

    assert result.profile == "terra-xhigh"
    assert result.approval_required is False
    assert result.fallback_profile == "sol-high"
    assert result.fallback_requires_approval is True


def test_low_risk_override_prefers_luna() -> None:
    result = picker.recommend("implement a small helper", risk="low")

    assert result.profile == "luna-medium"
    assert result.relative_token_rate == 1


def test_model_policy_profiles_are_unique_and_complete() -> None:
    policy = json.loads(
        (REPO_ROOT / "agents" / "model_policy.json").read_text(encoding="utf-8")
    )
    profiles = policy["profiles"]
    ids = {profile["id"] for profile in profiles}

    assert len(ids) == len(profiles)
    assert {"luna-high", "luna-xhigh", "terra-high", "sol-medium", "sol-high"} <= ids
    assert policy["defaults"]["max_concurrent_subagents"] == 2
