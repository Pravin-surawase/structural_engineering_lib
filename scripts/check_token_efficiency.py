#!/usr/bin/env python3
"""Validate repository-side Codex token-efficiency controls.

This checks configuration and context-size proxies. It deliberately does not
claim to read provider billing or account usage.

When to use: At session start or after editing Codex/model policy files.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = REPO_ROOT / ".codex" / "config.toml"
POLICY_DOC = REPO_ROOT / "docs" / "guidelines" / "ai-token-efficiency.md"
MODEL_POLICY = REPO_ROOT / "agents" / "model_policy.json"

ACTIVE_INSTRUCTIONS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "CLAUDE.md",
    REPO_ROOT / ".github" / "agents" / "orchestrator.agent.md",
    REPO_ROOT / "docs" / "contributing" / "agent-collaboration-framework.md",
)

FORBIDDEN_ACTIVE_TEXT = (
    "/usage daily",
    "/usage weekly",
    "up to **5 concurrent agents**",
    "read their ENTIRE `.agent.md` file",
)

TASK_PREAMBLE = """Work in low-token mode.

Use one Sol High main orchestrator for intake, planning, delegation, integration,
and final review. Keep Fast mode off. Use Luna for clear repetitive work and
Terra for normal implementation. Ask before using Sol profiles other than Sol
High. Default to no subagents; use no more than two only for independent,
bounded work. Give each a concise packet with objective, exact files, non-goals,
pitfalls, acceptance criteria, tests, and return format—never full conversation
history. Verify every result before accepting it. Run targeted tests during
development and the full gate once at closeout. Close subagents and stop when done."""


def _load_config() -> dict:
    with CONFIG.open("rb") as handle:
        return tomllib.load(handle)


def _context_stats(path: Path) -> dict[str, int | str]:
    size = path.stat().st_size
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "bytes": size,
        "estimated_tokens": math.ceil(size / 4),
    }


def validate() -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not CONFIG.exists():
        errors.append("missing .codex/config.toml")
        config: dict = {}
    else:
        config = _load_config()

    agents = config.get("agents", {})
    features = config.get("features", {})

    expected = {
        "model": "gpt-5.6-sol",
        "model_reasoning_effort": "high",
        "model_verbosity": "low",
    }
    for key, value in expected.items():
        if config.get(key) != value:
            errors.append(f"{key} must be {value!r}")

    if agents.get("max_concurrent_threads_per_session") != 2:
        errors.append("agents.max_concurrent_threads_per_session must be 2")
    if agents.get("default_subagent_model") != "gpt-5.6-luna":
        errors.append("agents.default_subagent_model must be 'gpt-5.6-luna'")
    if agents.get("default_subagent_reasoning_effort") != "low":
        errors.append("agents.default_subagent_reasoning_effort must be 'low'")
    if features.get("fast_mode") is not False:
        errors.append("features.fast_mode must be false")

    if not POLICY_DOC.exists():
        errors.append("missing canonical token-efficiency guideline")
    if not MODEL_POLICY.exists():
        errors.append("missing agents/model_policy.json")
    else:
        model_policy = json.loads(MODEL_POLICY.read_text(encoding="utf-8"))
        rates = model_policy.get("relative_token_rates", {})
        if rates != {
            "gpt-5.6-luna": 1,
            "gpt-5.6-terra": 10,
            "gpt-5.6-sol": 25,
        }:
            errors.append("model policy relative token rates are stale")
        if model_policy.get("defaults", {}).get("max_concurrent_subagents") != 2:
            errors.append("model policy must cap concurrent subagents at 2")
        if model_policy.get("defaults", {}).get("subagent_profile") != "luna-low":
            errors.append("model policy must default subagents to luna-low")
        if model_policy.get("defaults", {}).get("parent_profile") != "sol-high":
            errors.append("model policy must default the main orchestrator to sol-high")
        profile_ids = {
            profile.get("id") for profile in model_policy.get("profiles", [])
        }
        required_profiles = {
            "luna-low",
            "luna-medium",
            "luna-high",
            "terra-low",
            "terra-medium",
            "terra-high",
            "sol-medium",
            "sol-high",
        }
        if not required_profiles <= profile_ids:
            errors.append("model policy is missing required routing profiles")

    for path in ACTIVE_INSTRUCTIONS:
        if not path.exists():
            errors.append(
                f"missing active instruction file: {path.relative_to(REPO_ROOT)}"
            )
            continue
        content = path.read_text(encoding="utf-8")
        for text in FORBIDDEN_ACTIVE_TEXT:
            if text in content:
                errors.append(
                    f"stale token policy in {path.relative_to(REPO_ROOT)}: {text}"
                )

    root_agents = REPO_ROOT / "AGENTS.md"
    if (
        root_agents.exists()
        and "## Token-Efficiency Policy (MANDATORY)"
        not in root_agents.read_text(encoding="utf-8")
    ):
        errors.append("AGENTS.md is missing the mandatory token-efficiency section")

    context_files = [path for path in ACTIVE_INSTRUCTIONS[:3] if path.exists()]
    context = [_context_stats(path) for path in context_files]
    for stat in context:
        if stat["bytes"] > 24_000:
            warnings.append(
                f"large active instruction file: {stat['path']} ({stat['bytes']} bytes)"
            )

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "context": context,
        "usage_note": "Use /status and Settings > Usage for provider usage; local checks are proxies only.",
    }


def _print_human(result: dict) -> None:
    state = "PASS" if result["ok"] else "FAIL"
    print(f"Token-efficiency policy: {state}")
    for error in result["errors"]:
        print(f"  ERROR: {error}")
    for warning in result["warnings"]:
        print(f"  WARN: {warning}")
    print("Context proxies (estimated at bytes / 4, not billing tokens):")
    for stat in result["context"]:
        print(
            f"  {stat['path']}: {stat['bytes']} bytes, "
            f"~{stat['estimated_tokens']} tokens"
        )
    print(result["usage_note"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="print machine-readable output"
    )
    parser.add_argument(
        "--prompt", action="store_true", help="print the reusable low-token preamble"
    )
    args = parser.parse_args()

    if args.prompt:
        print(TASK_PREAMBLE)
        return 0

    result = validate()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_human(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
