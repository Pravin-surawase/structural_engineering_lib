"""Validate the completed PF0-PF11 structural library definition baseline."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PHASES = [f"PF{number}" for number in range(12)]
AOS = [f"AO{number:02d}" for number in range(1, 27)]
FOS = [f"FO{number:02d}" for number in range(1, 9)]
WORK_PACKETS = [f"WP{number:02d}" for number in range(1, 13)]


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def deliverables(baseline: dict) -> dict[str, dict]:
    records = {item["id"]: item for item in baseline["deliverables"]}
    require(len(records) == len(baseline["deliverables"]), f"{baseline['phase_id']} has duplicate deliverable IDs")
    return records


def ids(records: list[dict], field: str = "id") -> list[str]:
    return [record[field] for record in records]


def require_local_sources(phase_dir: Path, baseline: dict) -> None:
    for source in baseline["source_evidence"]:
        require((phase_dir / source).resolve().exists(), f"{baseline['phase_id']} source evidence is missing: {source}")


def main() -> None:
    programme = load(ROOT / "programme.json")
    register = load(ROOT / "decision-register.json")
    phase_records = {phase["id"]: phase for phase in programme["phases"]}

    require(list(phase_records) == PHASES, "Programme phases are incomplete or out of order")
    require(programme["phase_progress"] == {"completed": PHASES, "next": []}, "PF0-PF11 must all be complete with no next definition phase")

    decisions = {decision["id"]: decision for decision in register["decisions"]}
    require(list(decisions) == [f"D{number:02d}" for number in range(1, 24)], "D01-D23 must be contiguous and ordered")
    for decision in decisions.values():
        require(decision.get("state") == "resolved", f"{decision['id']} is unresolved")
        record = decision.get("decision_record", {})
        require(record.get("selected_direction"), f"{decision['id']} has no selected direction")
        require(record.get("downstream_effects"), f"{decision['id']} has no downstream effects")
        for evidence in record.get("evidence_paths", []):
            require((ROOT / evidence).resolve().is_file(), f"{decision['id']} evidence is missing: {evidence}")

    baselines: dict[str, dict] = {}
    for phase_id, phase in phase_records.items():
        completion = phase.get("completion", {})
        require(completion.get("state") == "complete", f"{phase_id} lacks a complete programme record")
        require(set(completion.get("decision_ids", [])) == {decision["id"] for decision in decisions.values() if decision["resolution_phase"] == phase_id}, f"{phase_id} completion decision IDs differ from the register")
        for evidence in completion.get("evidence_paths", []):
            require((ROOT / evidence).resolve().is_file(), f"{phase_id} completion evidence is missing: {evidence}")
        if phase_id == "PF0":
            continue
        phase_dir = ROOT / phase_id.lower()
        require((phase_dir / "README.md").is_file(), f"{phase_id} README is missing")
        baseline = load(phase_dir / "baseline.json")
        baselines[phase_id] = baseline
        require(baseline["phase_id"] == phase_id and baseline["state"] == "complete", f"{phase_id} baseline identity/state is invalid")
        require(set(baseline["decision_ids"]) == set(completion["decision_ids"]), f"{phase_id} baseline decisions differ from completion")
        require(set(deliverables(baseline)) == set(phase["deliverables"]), f"{phase_id} deliverables differ from the programme")
        require(len(baseline.get("exit_evidence", [])) >= len(phase["exit_criteria"]), f"{phase_id} exit evidence is incomplete")
        require_local_sources(phase_dir, baseline)

    pf3 = deliverables(baselines["PF3"])
    require(ids(pf3["PF3-D1-capability-map"]["records"]) == [item["id"] for item in programme["capability_families"]], "PF3 capability map differs from the programme")
    require(ids(pf3["PF3-D4-ao01-ao26-crosswalk"]["records"], "operation") == AOS, "PF3 lacks exact AO01-AO26 coverage")

    pf4 = deliverables(baselines["PF4"])
    require(len(pf4["PF4-D1-quantity-dictionary"]["records"]) == 37, "PF4 must define 37 quantity meanings")

    pf5 = deliverables(baselines["PF5"])
    foundations = pf5["PF5-D1-operation-catalogue"]["foundation_operations"]
    operations = pf5["PF5-D1-operation-catalogue"]["operations"]
    require(ids(foundations) == FOS, "PF5 lacks exact FO01-FO08 coverage")
    require(ids(operations) == AOS, "PF5 lacks exact AO01-AO26 coverage")
    for operation in foundations + operations:
        require(operation.get("valid_example") and operation.get("non_success_example"), f"{operation['id']} lacks valid/non-success examples")

    pf6 = deliverables(baselines["PF6"])
    parity = pf6["PF6-D1-common-capability-matrix"]
    require(len(parity["capabilities"]) == 17, "PF6 parity must cover all 17 capabilities")
    parity_operations = [operation for group in parity["operations"] for operation in group["ids"]]
    require(sorted(parity_operations) == sorted(FOS + AOS), "PF6 parity must cover FO01-FO08 and AO01-AO26 exactly")

    pf7 = deliverables(baselines["PF7"])
    require(ids(pf7["PF7-D1-assurance-matrix"]["records"], "operation") == AOS, "PF7 lacks assurance for AO01-AO26")

    pf8 = deliverables(baselines["PF8"])
    require(len(pf8["PF8-D5-installed-acceptance-plan"]["scenarios"]) == 10, "PF8 must retain ten installed acceptance scenarios")

    pf9 = deliverables(baselines["PF9"])
    budgets = pf9["PF9-D4-performance-budgets"]["budgets"]
    require(ids(budgets) == ["PERF-SCALAR", "PERF-MEMBER-BATCH", "PERF-CANDIDATE-SEARCH", "PERF-SERIALIZATION", "PERF-WORKBOOK", "PERF-ETABS-ACQUISITION"], "PF9 must define the six independent performance classes")

    pf10 = deliverables(baselines["PF10"])
    disposition = pf10["PF10-D1-api-disposition-ledger"]
    counts = disposition["coverage_baseline"]
    expected_counts = {
        "python_root_exports": 489,
        "python_root_callable_exports": 466,
        "python_services_api_exports": 245,
        "advertised_cli_entries": 15,
        "advertised_family_facades": 13,
        "csharp_working_operations": 5,
        "csharp_excel_functions": 4,
    }
    for name, expected in expected_counts.items():
        require(counts[name] == expected, f"PF10 coverage count {name} must be {expected}")
    require(len(disposition["python_module_groups"]) == 9 and len(disposition["csharp_groups"]) == 11, "PF10 disposition groups are incomplete")
    require(len(pf10["PF10-D2-migration-matrix"]["semantic_translations"]) == 10, "PF10 must define ten semantic translations")

    pf11 = deliverables(baselines["PF11"])
    trace = pf11["PF11-D2-traceability-report"]
    require(ids(trace["records"], "operation") == AOS, "PF11 traceability must cover AO01-AO26")
    require(list(trace["foundation_operation_packets"]) == FOS, "PF11 traceability must cover FO01-FO08")
    backlog = pf11["PF11-D3-implementation-backlog"]
    packets = backlog["work_packets"]
    require(ids(packets) == WORK_PACKETS, "PF11 backlog must contain WP01-WP12 in order")
    packet_ids = set(WORK_PACKETS)
    require(all(record["work_packet"] in packet_ids for record in trace["records"]), "PF11 AO trace points to an unknown packet")
    require(set(trace["foundation_operation_packets"].values()) <= packet_ids, "PF11 FO trace points to an unknown packet")
    covered_operations = {operation for packet in packets for operation in packet["operations"]}
    require(set(FOS + AOS) <= covered_operations, "PF11 work packets do not cover every FO/AO operation")
    milestones = {item["id"]: item["work_packets"] for item in backlog["milestone_prs"]}
    require(milestones == {"IMP-M1": WORK_PACKETS[:8], "IMP-M2": ["WP09"], "IMP-M3": WORK_PACKETS[9:]}, "PF11 milestone grouping differs from the three-PR blueprint")
    acceptance = pf11["PF11-D5-acceptance-evidence-matrix"]["records"]
    require(ids(acceptance, "work_packet") == WORK_PACKETS, "PF11 acceptance evidence must cover WP01-WP12")
    require(all(record.get("required_evidence") for record in acceptance), "Every PF11 work packet needs acceptance evidence")
    first_packet = pf11["PF11-D6-first-work-packet"]
    require(first_packet["packet_id"] == "WP01", "PF11 first packet must be WP01")
    require(len(first_packet["commit_sequence"]) == 4 and first_packet["acceptance"], "WP01 commit and acceptance boundaries are incomplete")

    print(
        "Definition complete: 12 phases, 60 deliverables, 23 resolved decisions, "
        "17 capabilities, 34 semantic operations, 6 performance classes and 12 work packets validated."
    )


if __name__ == "__main__":
    main()
