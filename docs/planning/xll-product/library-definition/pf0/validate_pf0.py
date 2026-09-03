"""Validate PF0 charter completeness and cross-file traceability."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROGRAMME_ROOT = ROOT.parent
EXPECTED_DELIVERABLES = {
    "PF0-D1-charter",
    "PF0-D2-owner-map",
    "PF0-D3-success-measures",
    "PF0-D4-glossary",
    "PF0-D5-scope-authority",
}
EXPECTED_PHASES = {f"PF{number}" for number in range(12)}
REQUIRED_CATEGORIES = {
    "product fitness",
    "engineering correctness",
    "engineering completeness",
    "professional API",
    "library reuse",
    "interoperability",
    "auditability",
    "Excel usability",
    "ETABS integrity",
    "construction outputs",
    "performance",
    "maintainability",
    "migration",
    "delivery evidence",
}
REQUIRED_TERMS = {
    "application adapter",
    "applicability",
    "approval",
    "capacity",
    "check",
    "common capability set",
    "completeness",
    "concurrent action vector",
    "effective inputs",
    "engineering outcome",
    "optional input",
    "professional signature",
    "reanalysis",
    "reusable library",
    "worksheet function",
}


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique(values: list[str], label: str) -> None:
    require(len(values) == len(set(values)), f"Duplicate {label}: {values}")


def main() -> None:
    programme = load(PROGRAMME_ROOT / "programme.json")
    register = load(PROGRAMME_ROOT / "decision-register.json")
    owners = load(ROOT / "owner-map.json")
    measures = load(ROOT / "success-measures.json")
    glossary = load(ROOT / "glossary.json")
    authority = load(ROOT / "scope-authority.json")
    charter = (ROOT / "charter.md").read_text(encoding="utf-8")

    pf0 = next(phase for phase in programme["phases"] if phase["id"] == "PF0")
    require(set(pf0["deliverables"]) == EXPECTED_DELIVERABLES, "PF0 deliverable set differs")
    require(pf0["completion"]["state"] == "complete", "PF0 completion is not recorded")
    evidence_paths = pf0["completion"]["evidence_paths"]
    require(
        len(evidence_paths) == 7,
        "PF0 completion must identify five outputs, its exit review and its validator",
    )
    for relative_path in evidence_paths:
        require((PROGRAMME_ROOT / relative_path).is_file(), f"Missing PF0 evidence: {relative_path}")

    role_ids = [role["id"] for role in owners["roles"]]
    unique(role_ids, "role IDs")
    role_set = set(role_ids)
    require("ROLE-PRODUCT" in role_set, "Product owner is missing")
    require("ROLE-ENGINEERING" in role_set, "Engineering authority is missing")
    require("ROLE-ARCHITECTURE" in role_set, "Architecture owner is missing")

    workflow_ids = [workflow["id"] for workflow in owners["workflows"]]
    unique(workflow_ids, "workflow IDs")
    workflow_set = set(workflow_ids)
    for user in owners["users"]:
        require(set(user["primary_workflows"]) <= workflow_set, f"{user['id']} cites an unknown workflow")
    for workflow in owners["workflows"]:
        require(workflow["outcome_owner"] in role_set, f"{workflow['id']} has an unknown owner")
        require(workflow["trigger"].strip(), f"{workflow['id']} has no trigger")
        require(workflow["completed_outcome"].strip(), f"{workflow['id']} has no completed outcome")
    for decision in owners["decision_ownership"]:
        require(decision["accountable"] in role_set, f"Unknown accountable role in {decision['decision_area']}")
        require(set(decision["responsible"]) <= role_set, f"Unknown responsible role in {decision['decision_area']}")
        require(set(decision["consulted"]) <= role_set, f"Unknown consulted role in {decision['decision_area']}")

    measure_ids = [measure["id"] for measure in measures["measures"]]
    unique(measure_ids, "measure IDs")
    categories = {measure["category"] for measure in measures["measures"]}
    require(categories == REQUIRED_CATEGORIES, f"Success categories differ: {sorted(categories ^ REQUIRED_CATEGORIES)}")
    for measure in measures["measures"]:
        require(measure["desired_outcome"].strip(), f"{measure['id']} has no desired outcome")
        require(measure["measure"].strip(), f"{measure['id']} has no measure")
        require(measure["target"].strip(), f"{measure['id']} has no target")
        require(measure["accountable_owner"] in role_set, f"{measure['id']} has an unknown owner")
        require(
            measure["definition_owner_phase"] in EXPECTED_PHASES,
            f"{measure['id']} has an unknown definition-owner phase",
        )

    terms = [entry["term"].casefold() for entry in glossary["terms"]]
    unique(terms, "glossary terms")
    require(REQUIRED_TERMS <= set(terms), f"Required glossary terms missing: {sorted(REQUIRED_TERMS - set(terms))}")
    for entry in glossary["terms"]:
        require(entry["definition"].strip(), f"{entry['term']} has no definition")
        require(entry["detail_owner_phase"] in EXPECTED_PHASES, f"{entry['term']} has an unknown owner phase")

    authority_phases = [entry["phase"] for entry in authority["phase_authority"]]
    unique(authority_phases, "phase-authority records")
    require(set(authority_phases) == EXPECTED_PHASES, "PF0-PF11 authority coverage is incomplete")
    require(authority["chartered_scope"]["implementation_deliverables"] == [], "PF0 contains an implementation deliverable")
    require(authority["excluded_from_this_programme"], "PF0 exclusions are missing")

    d01 = next(decision for decision in register["decisions"] if decision["id"] == "D01")
    require(d01["resolution_phase"] == "PF0", "D01 is assigned to the wrong phase")
    require(d01["state"] == "resolved", "D01 is not resolved")
    require(d01["decision_record"]["selected_direction"].strip(), "D01 selected direction is empty")
    require(set(d01["decision_record"]["evidence_paths"]) >= {
        "pf0/charter.md",
        "pf0/owner-map.json",
        "pf0/success-measures.json",
    }, "D01 required evidence is incomplete")
    for evidence_path in d01["decision_record"]["evidence_paths"]:
        require((PROGRAMME_ROOT / evidence_path).is_file(), f"D01 evidence is missing: {evidence_path}")

    charter_markers = [
        "native Python and native .NET",
        "standalone reinforced-concrete beam",
        "Excel and ETABS",
        "No implementation deliverable",
    ]
    normalized_charter = " ".join(charter.casefold().split())
    for marker in charter_markers:
        require(marker.casefold() in normalized_charter, f"Charter marker missing: {marker}")

    deliverable_files = {
        owners["deliverable_id"],
        measures["deliverable_id"],
        glossary["deliverable_id"],
        authority["deliverable_id"],
    }
    require(deliverable_files == EXPECTED_DELIVERABLES - {"PF0-D1-charter"}, "PF0 JSON deliverable IDs differ")

    print(
        "Validated PF0: "
        f"{len(owners['users'])} user groups, {len(owners['workflows'])} workflows, "
        f"{len(role_ids)} roles, {len(measure_ids)} success measures, "
        f"{len(terms)} glossary terms and {len(authority_phases)} phase-authority records."
    )


if __name__ == "__main__":
    main()
