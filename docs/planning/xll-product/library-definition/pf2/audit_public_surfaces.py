"""Prove that the PF2 disposition rules cover the current public surfaces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import structural_lib
from structural_lib.services import api
from structural_lib.services.family_facade_registry import FAMILY_FACADE_WORKFLOWS


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[4]


def load(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def exported_callables(module: Any) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    for name in module.__all__:
        value = getattr(module, name)
        if callable(value):
            records.append((name, getattr(value, "__module__", "")))
    return records


def main() -> None:
    baseline = load(ROOT / "baseline.json")
    surface = next(
        item
        for item in baseline["deliverables"]
        if item["id"] == "PF2-D2-public-surface-map"
    )
    counts = surface["current_counts"]
    root_callables = exported_callables(structural_lib)
    api_callables = exported_callables(api)
    require(len(structural_lib.__all__) == counts["python_root_exports"], "Root export count drifted")
    require(len(root_callables) == counts["python_root_callable_exports"], "Root callable count drifted")
    require(len(api.__all__) == counts["python_services_api_exports"], "services.api export count drifted")
    require(len(api_callables) == counts["python_services_api_callable_exports"], "services.api callable count drifted")

    rules = sorted(surface["python_module_disposition_rules"], key=lambda row: row["order"])
    unmatched: list[tuple[str, str]] = []
    for name, module_name in root_callables:
        if not any(
            module_name.startswith(prefix)
            for rule in rules
            for prefix in rule["module_prefixes"]
        ):
            unmatched.append((name, module_name))
    require(not unmatched, f"Unclassified Python public callables: {unmatched[:10]}")

    advertised = load(
        REPO_ROOT / "Python/structural_lib/data/advertised_entry_points_v1.json"
    )["entry_points"]
    require(len(advertised) == counts["advertised_cli_entries"], "Advertised CLI count drifted")
    require(
        len(FAMILY_FACADE_WORKFLOWS) == counts["advertised_family_facades"],
        "Family facade count drifted",
    )
    expected_advertised = {
        row
        for rule in surface["advertised_surface_rules"]
        for row in rule["entries"]
    }
    actual_advertised = {row["command"] for row in advertised} | {
        row.journey_id for row in FAMILY_FACADE_WORKFLOWS
    }
    require(actual_advertised == expected_advertised, "Advertised disposition coverage drifted")

    print(
        "PF2 surface coverage: "
        f"{len(structural_lib.__all__)} root exports/{len(root_callables)} callable, "
        f"{len(api.__all__)} services exports, {len(advertised)} CLI entries and "
        f"{len(FAMILY_FACADE_WORKFLOWS)} family facades."
    )


if __name__ == "__main__":
    main()
