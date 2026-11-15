#!/usr/bin/env python3
"""Check frozen supplied slab actions through the canonical slab facade.

The fixture supplies actions and, for the external route, coefficient evidence.
It is a reproducible software reference, not a load-generation or direct-
deflection workflow and not an engineering approval.
"""

from __future__ import annotations

import argparse
import copy
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from structural_lib.design.is456 import slab

_REFERENCE_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs/verification/library-030-sl06-actions.json"
)
_SPECIMENS = ("B02", "B04")
_ROUTES = ("external", "builtin")


def _fixture_value(mapping: Mapping[str, Any], key: str) -> Any:
    """Return a required fixture value with a concise malformed-fixture error."""
    try:
        return mapping[key]
    except KeyError as error:
        raise ValueError(f"reference fixture is missing {key!r}") from error


def request_payload(
    fixture: Mapping[str, Any],
    specimen_name: str,
    route_name: str,
    scenario: str = "baseline",
) -> dict[str, Any]:
    """Materialize one public ``slab-action-set-input/v1`` request mapping.

    ``scenario`` accepts ``baseline`` and the named controls in the selected
    specimen's immutable fixture.  It deliberately returns a plain mapping so
    JSON/HTTP callers and this command-line reference share the same loader.
    """
    if specimen_name not in _SPECIMENS:
        raise ValueError(f"specimen must be one of {_SPECIMENS}, got {specimen_name!r}")
    if route_name not in _ROUTES:
        raise ValueError(f"route must be one of {_ROUTES}, got {route_name!r}")

    specimens = _fixture_value(fixture, "specimens")
    specimen = _fixture_value(specimens, specimen_name)
    controls = _fixture_value(specimen, "controls")
    if scenario == "baseline":
        control: Mapping[str, Any] = {}
    else:
        control = _fixture_value(controls, scenario)

    common = copy.deepcopy(
        _fixture_value(specimen, "geometry_material_and_support_inputs")
    )
    materials = {
        "fck_nmm2": common.pop("fck_n_per_mm2"),
        "fy_nmm2": common.pop("fy_n_per_mm2"),
    }
    reinforcement = copy.deepcopy(_fixture_value(specimen, "reinforcement_inputs"))
    geometry: dict[str, Any]
    if specimen_name == "B02":
        geometry = {
            "short_effective_span_mm": common.pop("short_effective_span_mm"),
            "long_effective_span_mm": common.pop("long_effective_span_mm"),
            "thickness_mm": common.pop("thickness_mm"),
            "effective_depth_mm": common.pop("d_mm"),
            "strip_width_mm": 1000.0,
            "number_of_spans": common.pop("number_of_spans"),
            "maximum_span_variation_percent": common.pop(
                "maximum_span_variation_percent"
            ),
            "uniform_cross_section_acknowledged": common.pop(
                "uniform_cross_section_acknowledged"
            ),
        }
        substantially_uniform_load_acknowledged = common.pop(
            "substantially_uniform_load_acknowledged"
        )
        redistribution_applied = common.pop("redistribution_applied")
        kind = "continuous_one_way"
    else:
        geometry = common
        kind = "two_way_panel"

    if specimen_name == "B02" and common:
        # All B02 fields were consumed above; B04 has no remaining material
        # fields after its geometry is copied.
        raise ValueError(f"unexpected fixture geometry fields: {sorted(common)}")

    coefficient_route = _fixture_value(
        _fixture_value(specimen, "coefficient_routes"), route_name
    )
    coefficient_inputs = copy.deepcopy(_fixture_value(coefficient_route, "inputs"))
    row_lookup = _fixture_value(specimen, "rows")
    input_order = control.get("input_order", list(row_lookup))
    rows: list[dict[str, Any]] = []
    for row_id in input_order:
        row_input = copy.deepcopy(
            _fixture_value(_fixture_value(row_lookup, row_id), "input")
        )
        if control.get("replace_B_load_with_A_load") and row_id == "B":
            row_input["factored_area_load_kn_per_m2"] = _fixture_value(
                _fixture_value(row_lookup, "A"), "input"
            )["factored_area_load_kn_per_m2"]
        coefficient_basis: dict[str, Any] = {"kind": route_name, **coefficient_inputs}
        # The continuous built-in action set derives its fixed action from the
        # row's supplied area load; its per-row basis has no duplicate load key.
        rows.append({**row_input, "coefficient_basis": coefficient_basis})

    serviceability_evidence: Any = copy.deepcopy(
        _fixture_value(specimen, "shared_reviewed_service_basis")
    )
    if control.get("set_shared_service_basis_to_null"):
        serviceability_evidence = None

    payload: dict[str, Any] = {
        "kind": kind,
        "identity": {"family_id": "slab", "case_id": f"SLAB-{specimen_name}-SL06"},
        "geometry_revision": _fixture_value(specimen, "geometry_revision"),
        "reinforcement_revision": _fixture_value(specimen, "reinforcement_revision"),
        "geometry": geometry,
        "materials": materials,
        "reinforcement": reinforcement,
        "serviceability_evidence": serviceability_evidence,
        "required_row_ids": copy.deepcopy(_fixture_value(specimen, "required_row_ids")),
        "rows": rows,
    }
    if specimen_name == "B02":
        payload["substantially_uniform_load_acknowledged"] = (
            substantially_uniform_load_acknowledged
        )
        payload["redistribution_applied"] = redistribution_applied
    return payload


def _read_fixture(reference: Path) -> Mapping[str, Any]:
    return json.loads(reference.read_text(encoding="utf-8"))


def run_reference(
    reference: Path, specimen_name: str, route_name: str, scenario: str
) -> dict[str, Any]:
    """Run one frozen request and return finite JSON-ready public output."""
    payload = request_payload(
        _read_fixture(reference), specimen_name, route_name, scenario
    )
    request = slab.load_action_set(payload)
    result = slab.check_action_set(request)
    return result.to_dict()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=_REFERENCE_PATH)
    parser.add_argument("--specimen", choices=_SPECIMENS, default="B02")
    parser.add_argument("--route", choices=_ROUTES, default="builtin")
    parser.add_argument("--scenario", default="baseline")
    args = parser.parse_args()
    try:
        output = run_reference(args.reference, args.specimen, args.route, args.scenario)
    except slab.InputContractError as error:
        # ``duplicate_id`` is an intentional control: show the public,
        # structured input failure without translating it into a status result.
        output = {"input_error": [issue.to_dict() for issue in error.issues]}
        print(json.dumps(output, allow_nan=False, sort_keys=True))
        return 0 if args.scenario == "duplicate_id" else 2
    print(json.dumps(output, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
