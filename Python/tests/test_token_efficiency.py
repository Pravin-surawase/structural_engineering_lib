"""Regression tests for repository-side token-efficiency controls."""

from __future__ import annotations

import json
import subprocess
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_project_codex_defaults_are_low_token() -> None:
    with (REPO_ROOT / ".codex" / "config.toml").open("rb") as handle:
        config = tomllib.load(handle)

    assert "model" not in config
    assert "model_reasoning_effort" not in config
    assert config["model_verbosity"] == "low"
    assert config["agents"]["max_concurrent_threads_per_session"] == 2
    assert config["agents"]["default_subagent_model"] == "gpt-5.6-luna"
    assert config["agents"]["default_subagent_reasoning_effort"] == "low"
    assert config["features"]["fast_mode"] is False


def test_token_efficiency_checker_passes() -> None:
    result = subprocess.run(
        [
            str(REPO_ROOT / ".venv" / "bin" / "python"),
            "scripts/check_token_efficiency.py",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Token-efficiency policy: PASS" in result.stdout
    assert "not billing tokens" in result.stdout


def test_low_token_prompt_is_bounded_and_actionable() -> None:
    result = subprocess.run(
        [
            str(REPO_ROOT / ".venv" / "bin" / "python"),
            "scripts/check_token_efficiency.py",
            "--prompt",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    prompt = " ".join(result.stdout.split())
    assert "no more than two" in prompt
    assert "never full conversation history" in prompt
    assert "Respect the parent model and reasoning selected by the user" in prompt
    assert "ask before any Sol escalation" in prompt
    assert "pitfalls, acceptance criteria, tests, and return format" in prompt
    assert len(result.stdout.splitlines()) <= 12


def test_quick_gate_enforces_token_policy() -> None:
    check_all = (REPO_ROOT / "scripts" / "check_all.py").read_text(encoding="utf-8")

    assert 'Check("Token efficiency", _py("check_token_efficiency.py"))' in check_all
    assert '"governance": ["Repo hygiene", "Token efficiency"]' in check_all


def test_verified_model_rates_are_checked_in() -> None:
    policy = json.loads(
        (REPO_ROOT / "agents" / "model_policy.json").read_text(encoding="utf-8")
    )

    assert policy["relative_token_rates"] == {
        "gpt-5.6-luna": 1,
        "gpt-5.6-terra": 10,
        "gpt-5.6-sol": 25,
    }
