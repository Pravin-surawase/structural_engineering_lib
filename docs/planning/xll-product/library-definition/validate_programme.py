"""Validate structural library definition programme structure and traceability."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED_PHASES = [f"PF{number}" for number in range(12)]
EXPECTED_OPERATIONS = [f"AO{number:02d}" for number in range(1, 27)]
REQUIRED_CAPABILITIES = {
    "CAP-FOUND",
    "CAP-ANALYSIS",
    "CAP-FLEXURE",
    "CAP-SHEAR",
    "CAP-TORSION",
    "CAP-SLS",
    "CAP-DETAIL",
    "CAP-CONSTRUCT",
    "CAP-FAB",
    "CAP-COST",
    "CAP-FORMWORK",
    "CAP-OPT",
    "CAP-ETABS",
    "CAP-EXCEL",
    "CAP-REPORT",
    "CAP-PACKAGE",
    "CAP-PERF",
}


def load(name: str) -> dict:
    with (ROOT / name).open(encoding="utf-8") as stream:
        return json.load(stream)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    programme = load("programme.json")
    register = load("decision-register.json")
    phases = programme["phases"]
    phase_ids = [phase["id"] for phase in phases]

    require(phase_ids == EXPECTED_PHASES, f"Expected ordered phases {EXPECTED_PHASES}; found {phase_ids}")
    require(programme["automation_operations"] == EXPECTED_OPERATIONS, "AO01-AO26 coverage is incomplete or out of order")
    require(programme["definition_phase_prefix"] != programme["implementation_phase_prefix"], "Definition and implementation phase prefixes must differ")

    seen_deliverables: set[str] = set()
    for index, phase in enumerate(phases):
        require(phase["purpose"].strip(), f"{phase['id']} has no purpose")
        require(len(phase["deliverables"]) >= 3, f"{phase['id']} needs at least three concrete deliverables")
        require(len(phase["exit_criteria"]) >= 3, f"{phase['id']} needs at least three exit criteria")
        allowed_dependencies = set(phase_ids[:index])
        require(set(phase["depends_on"]) <= allowed_dependencies, f"{phase['id']} depends on a later or unknown phase")
        for deliverable in phase["deliverables"]:
            require(deliverable.startswith(f"{phase['id']}-D"), f"{deliverable} is not owned by {phase['id']}")
            require(deliverable not in seen_deliverables, f"Duplicate deliverable {deliverable}")
            seen_deliverables.add(deliverable)

    capability_ids = {capability["id"] for capability in programme["capability_families"]}
    require(capability_ids == REQUIRED_CAPABILITIES, f"Capability coverage differs: {sorted(capability_ids ^ REQUIRED_CAPABILITIES)}")
    for capability in programme["capability_families"]:
        for field in ("definition_phase", "assurance_phase", "application_phase"):
            require(capability[field] in phase_ids, f"{capability['id']} has unknown {field}")

    decisions = register["decisions"]
    decision_ids = [decision["id"] for decision in decisions]
    expected_decisions = [f"D{number:02d}" for number in range(1, len(decisions) + 1)]
    require(decision_ids == expected_decisions, "Decision IDs must be unique, contiguous and ordered")
    covered_resolution_phases: set[str] = set()
    for decision in decisions:
        require(decision["resolution_phase"] in phase_ids, f"{decision['id']} has unknown resolution phase")
        require(decision["question"].strip(), f"{decision['id']} has no question")
        require(decision["current_direction"].strip(), f"{decision['id']} has no current direction")
        require(decision["required_evidence"], f"{decision['id']} has no required evidence")
        covered_resolution_phases.add(decision["resolution_phase"])

    require(covered_resolution_phases == set(phase_ids), "Every phase must own at least one consequential decision")
    require(len(programme["completion_definition"]) >= 5, "Completion definition is too small")
    print(
        f"Validated {len(phases)} phases, {len(seen_deliverables)} deliverables, "
        f"{len(decisions)} decisions, {len(capability_ids)} capability families and "
        f"{len(programme['automation_operations'])} automation operations."
    )


if __name__ == "__main__":
    main()
