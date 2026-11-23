# SPDX-License-Identifier: MIT
"""Local one-floor geometry, action preview and bounded IS 456 review."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal

from pydantic import ValidationError

from structural_lib.core.errors import CalculationError, InputContractError
from structural_lib.core.result_contract import ReviewStatus
from structural_lib.core.version import get_runtime_version

from . import canonical_beam
from .batch import validate_project_beam_batch_v1
from .beam_continuous import check_section_beam
from .cli_design import CLIDesignBlockedError, CLIDesignRecordV1
from .contracts.beam import BeamDesignInputV1
from .contracts.beam_continuous import BeamSectionCheckRequestV1
from .contracts.common import model_validate_or_error
from .floor_etabs import issue, load_etabs_floor_v1
from .floor_prepared import load_prepared_floor_v1

FloorReviewProfile = Literal[
    "prepared-csv", "prepared-xlsx", "prepared-json", "etabs-snapshot", "etabs-paired"
]
FLOOR_REVIEW_PROFILES = (
    "prepared-csv",
    "prepared-xlsx",
    "prepared-json",
    "etabs-snapshot",
    "etabs-paired",
)
_PREPARED_SCOPE = "rectangular-section-strength-sizing"
_PAIRED_SCOPE = "rectangular-section-uls-strength-at-declared-stations"


def _unevaluated(reason: str) -> dict[str, Any]:
    return {
        "calculation_status": "NOT_EVALUATED",
        "engineering_status": "NOT_EVALUATED",
        "reason": reason,
    }


def _hold_member(member: dict[str, Any], code: str, message: str) -> dict[str, Any]:
    return {
        **_unevaluated(code),
        "issues": [issue(code, member["member_id"], message)],
    }


def _prepared_design(
    record: CLIDesignRecordV1, member: dict[str, Any]
) -> dict[str, Any]:
    # This profile sizes flexural steel and transverse pitch for one signed
    # factored action pair. Its equal face centroid assumption is declared in
    # the template contract. It is not an actual reinforcement check.
    source = record.project_payload["source_metadata"]
    request = model_validate_or_error(
        BeamDesignInputV1,
        {
            "identity": {
                "member_id": member["member_id"],
                "story": record.story,
                "case_id": "prepared-controlling-action",
            },
            "section": {
                "span_mm": record.span,
                "b_mm": record.b,
                "D_mm": record.D,
                "d_mm": record.d,
            },
            "materials": {"fck_nmm2": record.fck, "fy_nmm2": record.fy},
            "actions": {
                "mu_knm": abs(record.Mu),
                "vu_kn": abs(record.Vu),
                "primary_tension_face": "TOP" if record.Mu < 0 else "BOTTOM",
            },
            "calculation_basis": {
                "d_dash_mm": record.D - record.d,
                "asv_mm2": 2 * math.pi * (record.stirrup_dia / 2) ** 2,
            },
            "source_provenance": f"{source['input_artifact_sha256']}:{source['source_row_number']}",
        },
    )
    result = canonical_beam.design(request)
    calculation = result.to_dict()
    # The sizing calculation can prescribe a tighter pitch. Retain the
    # engineer's proposed pitch and its own disposition without implying a cage check.
    shear = result.calculation.shear
    maximum = shear.spacing if shear and shear.is_safe else None
    pitch_status = (
        "NOT_EVALUATED"
        if maximum is None
        else "PASS"
        if record.stirrup_spacing <= maximum
        else "FAIL"
    )
    status = result.engineering_status.value
    if pitch_status == "FAIL":
        status = "FAIL"
    return {
        "scope": _PREPARED_SCOPE,
        "calculation_status": result.calculation_status.value,
        "engineering_status": status,
        "result": calculation,
        "proposed_link_pitch": {
            "supplied_mm": record.stirrup_spacing,
            "maximum_mm": maximum,
            "status": pitch_status,
        },
        "governing": {
            "source_row_number": source["source_row_number"],
            "input_artifact_sha256": source["input_artifact_sha256"],
            "utilization": calculation["calculation"]["governing_utilization"],
        },
    }


def _prepared(
    path: Path, profile: str, evaluate: bool, package: dict[str, Any]
) -> None:
    source_format = profile.removeprefix("prepared-")
    intake = load_prepared_floor_v1(path, source_format=source_format)
    package["artifacts"].append(
        {
            "role": "prepared_beams",
            "file": path.name,
            "sha256": intake.source_sha256,
            "source_rows": intake.source_rows,
            **({"worksheet": "Beams"} if source_format == "xlsx" else {}),
        }
    )
    validations = validate_project_beam_batch_v1(
        [
            {
                **record.project_payload,
                "mu_knm": abs(record.Mu),
                "vu_kn": abs(record.Vu),
            }
            for record in intake.records
        ]
    )
    for record, validation in zip(intake.records, validations, strict=True):
        row = record.project_payload["source_metadata"]["source_row_number"]
        package["issues"].extend(
            issue(item.code, f"rows[{row}].{item.path}", item.message)
            for item in validation.issues
        )
    if package["issues"]:
        return
    stories = {record.story for record in intake.records}
    if len(stories) != 1:
        package["issues"].append(
            issue(
                "FLOOR.MULTIPLE_STORIES",
                "story",
                "Supply exactly one story in a prepared floor file.",
            )
        )
        return
    package["provenance"]["review_story"] = next(iter(stories))
    package["intake_status"] = "ACCEPTED"
    for record in intake.records:
        source = record.project_payload["source_metadata"]
        inputs = {
            key: value
            for key, value in record.project_payload.items()
            if key not in ("source_metadata", "schema_version")
        }
        member = {
            "member_id": inputs["member_id"],
            "story": record.story,
            "label": record.beam_id,
            "member_kind": "beam",
            "geometry": {
                "span_mm": record.span,
                "b_mm": record.b,
                "D_mm": record.D,
                "d_mm": record.d,
            },
            "canonical_input": {
                **inputs,
                "span_mm": record.span,
                "clear_cover_mm": record.cover,
                "stirrup_diameter_mm": record.stirrup_dia,
                "stirrup_spacing_mm": record.stirrup_spacing,
            },
            "signed_actions": [
                {
                    "mu_knm": record.Mu,
                    "vu_kn": record.Vu,
                    "basis": "supplied_factored_action_pair",
                }
            ],
            "source_identity": source,
            "evaluation": _unevaluated("PREVIEW"),
        }
        if evaluate:
            try:
                member["evaluation"] = _prepared_design(record, member)
            except InputContractError as exc:
                member["evaluation"] = {
                    **_unevaluated("FLOOR.STRICT_REQUEST_REJECTED"),
                    "issues": [item.to_dict() for item in exc.issues],
                }
            except CalculationError:
                member["evaluation"] = _calculation_error(member["member_id"])
        package["members"].append(member)


def _calculation_error(member_id: str) -> dict[str, Any]:
    return {
        "calculation_status": "ERROR",
        "engineering_status": "NOT_EVALUATED",
        "issues": [
            issue(
                "FLOOR.CALCULATION_ERROR",
                member_id,
                "The maintained calculation did not complete.",
            )
        ],
    }


def _native_status(section_statuses: Sequence[str]) -> str:
    if "FAIL" in section_statuses:
        return "FAIL"
    if "HOLD" in section_statuses:
        return "HOLD"
    return "PASS"


def _evaluate_native(member: dict[str, Any], analysis_revision: str) -> dict[str, Any]:
    geometry = member["geometry"]
    section = geometry["section"]
    if section is None:
        return _hold_member(
            member,
            "FLOOR.SECTION_BASIS_MISSING",
            "Supply the checked physical section, bars and two-leg links for each declared station.",
        )
    if section["analysis_revision"] != analysis_revision:
        return _hold_member(
            member,
            "FLOOR.STALE_SECTION",
            "Section and reinforcement evidence must be tied to this analysis revision.",
        )
    e2 = geometry["local_axes"]["e2"]
    if not (
        math.isclose(e2["z"], 1.0, rel_tol=0, abs_tol=1e-9)
        and math.hypot(e2["x"], e2["y"]) <= 1e-9
        and math.isclose(
            geometry["i_mm"]["z"], geometry["j_mm"]["z"], rel_tol=0, abs_tol=1e-6
        )
    ):
        return _hold_member(
            member,
            "FLOOR.SECTION_AXES_UNSUPPORTED",
            "Section checks require a horizontal beam and local 2 up. Review the supplied axis orientation.",
        )
    rows = [row for row in member["signed_actions"] if row["design_use"] == "ultimate"]
    if not rows:
        return _hold_member(
            member,
            "FLOOR.ULTIMATE_ROWS_MISSING",
            "Declare at least one ultimate combination for the section check.",
        )
    if any(row[key] != 0 for row in rows for key in ("p_n", "v3_n", "t_nmm", "m2_nmm")):
        return _hold_member(
            member,
            "FLOOR.ACTION_OUTSIDE_SECTION_PROFILE",
            "The beam check admits M3 and V2 only. Review the other signed components in the source rows.",
        )

    by_station: dict[float, list[dict[str, Any]]] = defaultdict(list)
    declared_stations = member["source_identity"]["required_stations_mm"]
    for row in rows:
        station = min(
            declared_stations, key=lambda value: abs(value - row["object_station_mm"])
        )
        by_station[station].append(row)
    results, statuses = [], []
    governing: dict[str, dict[str, Any]] = {}
    for index, (station, actions) in enumerate(sorted(by_station.items()), start=1):
        station_id = f"station-{index}"
        source_by_id = {row["source_row_id"]: row for row in actions}
        request = model_validate_or_error(
            BeamSectionCheckRequestV1,
            {
                **section,
                "member_id": member["member_id"],
                "current_analysis_revision": analysis_revision,
                "stations": [
                    {"station_id": station_id, "x_mm": station, "side": "CONTINUOUS"}
                ],
                "combinations": [
                    {
                        "combination_id": row["load_case_id"],
                        "kind": "ULS",
                        "required_station_ids": [station_id],
                    }
                    for row in actions
                ],
                "actions": [
                    {
                        "row_id": row["source_row_id"],
                        "combination_id": row["load_case_id"],
                        "station_id": station_id,
                        "mu_knm": row["m3_nmm"] / 1_000_000,
                        "vu_kn": row["v2_n"] / 1000,
                    }
                    for row in actions
                ],
            },
        )
        checked = check_section_beam(request)
        statuses.append(checked.ultimate_status)
        results.append(
            {
                "station_mm": station,
                "status": checked.ultimate_status,
                "rows": [row.to_dict() for row in checked.rows],
                "governing_rows": checked.governing_rows,
                "result_envelope": checked.result_envelope.to_dict(),
            }
        )
        checked_by_id = {row.action.row_id: row for row in checked.rows}
        for check, row_id in checked.governing_rows.items():
            row = checked_by_id[row_id]
            utilization = (
                row.shear_utilization if check == "shear" else row.flexure_utilization
            )
            if utilization is not None and (
                check not in governing or utilization > governing[check]["utilization"]
            ):
                source = source_by_id[row_id]
                governing[check] = {
                    "utilization": utilization,
                    "source_row_id": row_id,
                    "combination": source["load_case_id"],
                    "station_mm": station,
                    "m3_nmm": source["m3_nmm"],
                    "v2_n": source["v2_n"],
                }

    return {
        "scope": _PAIRED_SCOPE,
        "calculation_status": "COMPLETED",
        "engineering_status": _native_status(statuses),
        "section_checks": results,
        "governing": governing,
    }


def _etabs(path: Path, profile: str, evaluate: bool, package: dict[str, Any]) -> None:
    intake = load_etabs_floor_v1(path, profile=profile)
    package.update(
        intake_status=intake.status,
        artifacts=intake.artifacts,
        provenance=intake.provenance,
        members=intake.members,
        issues=intake.issues,
    )
    story = intake.provenance["review_story"]
    analysis_revision = intake.provenance["current_basis"]["analysis_revision"]
    if intake.status == "ACCEPTED" and not any(
        member["story"] == story and member["member_kind"] == "beam"
        for member in intake.members
    ):
        package["issues"].append(
            issue(
                "FLOOR.STORY_NOT_FOUND",
                "review_story",
                "The requested story has no beam in this packet.",
            )
        )
        package["intake_status"] = "BLOCKED"
    for member in intake.members:
        if package["intake_status"] != "ACCEPTED":
            evaluation = _unevaluated("ETABS_INTAKE_UNRESOLVED")
        elif member["story"] != story:
            evaluation = _unevaluated("OUTSIDE_REVIEW_STORY")
        elif member["member_kind"] != "beam":
            evaluation = _unevaluated("COLUMN_INTAKE_ONLY")
        elif profile == "etabs-snapshot":
            evaluation = _unevaluated("SNAPSHOT_ENVELOPE_PREVIEW_ONLY")
        elif not evaluate:
            evaluation = _unevaluated("PREVIEW")
        else:
            try:
                evaluation = _evaluate_native(member, analysis_revision)
            except InputContractError as exc:
                evaluation = {
                    **_unevaluated("FLOOR.SECTION_REQUEST_REJECTED"),
                    "issues": [item.to_dict() for item in exc.issues],
                }
            except CalculationError:
                evaluation = _calculation_error(member["member_id"])
        member["evaluation"] = evaluation
        for row in member.get("signed_actions", []):
            if profile != "etabs-paired":
                disposition = "SNAPSHOT_PREVIEW"
            elif row["design_use"] != "ultimate":
                disposition = "NON_ULTIMATE_PREVIEW"
            elif evaluation["calculation_status"] == "COMPLETED":
                disposition = "SECTION_CHECK_RUN"
            else:
                disposition = evaluation.get("reason", "NOT_EVALUATED")
            row["evaluation_disposition"] = disposition


def review_floor_v1(
    path: Path | str, *, profile: FloorReviewProfile, evaluate: bool = False
) -> dict[str, Any]:
    """Return a portable preview or scoped calculation with source and review evidence."""
    package: dict[str, Any] = {
        "schema_version": "local-floor-review/v1",
        "profile": profile,
        "mode": "review" if evaluate else "preview",
        "library_version": get_runtime_version(),
        "intake_status": "BLOCKED",
        "review_status": ReviewStatus.QUALIFIED_REVIEW_REQUIRED.value,
        "engineering_approval": "UNREVIEWED",
        "artifacts": [],
        "provenance": {},
        "members": [],
        "issues": [],
    }
    try:
        if profile.startswith("prepared-") and profile in FLOOR_REVIEW_PROFILES:
            _prepared(Path(path), profile, evaluate, package)
        elif profile in ("etabs-snapshot", "etabs-paired"):
            _etabs(Path(path), profile, evaluate, package)
        else:
            raise ValueError(f"Unknown floor review source profile {profile!r}.")
    except CLIDesignBlockedError as exc:
        package["issues"].extend(asdict(item) for item in exc.issues)
    except InputContractError as exc:
        package["issues"].extend(item.to_dict() for item in exc.issues)
    except ValidationError as exc:
        package["issues"].extend(
            issue("FLOOR.INPUT_INVALID", ".".join(map(str, item["loc"])), item["msg"])
            for item in exc.errors(include_input=False, include_url=False)
        )
    except (OSError, ValueError) as exc:
        package["issues"].append(issue("FLOOR.SOURCE_UNAVAILABLE", "input", str(exc)))

    evaluations = [member["evaluation"] for member in package["members"]]
    exception_counts = Counter(item["code"] for item in package["issues"])
    exception_counts.update(item["reason"] for item in evaluations if "reason" in item)
    exception_counts.update(
        item["code"]
        for evaluation in evaluations
        if "reason" not in evaluation
        for item in evaluation.get("issues", ())
    )
    exception_counts.update(
        f"FLOOR.CHECK_{evaluation['engineering_status']}"
        for evaluation in evaluations
        if evaluation["engineering_status"] in ("FAIL", "HOLD")
    )
    package["summary"] = {
        "members": len(evaluations),
        "engineering_statuses": dict(
            Counter(item["engineering_status"] for item in evaluations)
        ),
        "exceptions": dict(exception_counts),
    }
    return package
