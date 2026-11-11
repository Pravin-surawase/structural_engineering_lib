"""Replay the bounded INDIA-1D one-way solid-slab reference case.

Run from a source checkout or a copied file alongside an installed package::

    python slab_one_way_reference.py --case baseline

This example uses the maintained public service route.  It records a bounded
software calculation, not a generated load envelope, direct-deflection or
crack-width verification, automatic slab-shear design, or engineering approval.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Any

from structural_lib.services.api import design_complete_one_way_slab_is456

_CASE_NAMES = ("baseline", "capacity-fail", "review-limit-fail")


def request_for(case: str) -> dict[str, Any]:
    """Return the flat HTTP-shaped request for one frozen worked-case control."""
    request: dict[str, Any] = {
        "short_effective_span_mm": 3000.0,
        "long_effective_span_mm": 7500.0,
        "thickness_mm": 150.0,
        "d_mm": 125.0,
        "factored_area_load_kn_per_m2": 10.0,
        "fck_n_per_mm2": 20.0,
        "fy_n_per_mm2": 415.0,
        "main_bar_diameter_mm": 10.0,
        "main_bar_spacing_mm": 250.0,
        "distribution_bar_diameter_mm": 8.0,
        "distribution_bar_spacing_mm": 250.0,
        "strip_width_mm": 1000.0,
        "reviewed_base_span_depth_limit": 20.0,
        "reviewed_aggregate_modification_factor": 1.2,
        "serviceability_limit_source_reference": "example-review-limit:INDIA-1D",
        "serviceability_limit_source_is_approved": True,
        "qualified_serviceability_acceptance_reference": "example-review:INDIA-1D",
        "qualified_serviceability_acceptance_acknowledged": True,
    }
    if case == "capacity-fail":
        request["factored_area_load_kn_per_m2"] = 50.0
    elif case == "review-limit-fail":
        request["reviewed_aggregate_modification_factor"] = 1.0
    elif case != "baseline":
        raise ValueError(f"case must be one of: {', '.join(_CASE_NAMES)}")
    return request


def run_case(case: str) -> dict[str, Any]:
    """Run one control case and retain the actual public result unchanged."""
    request = request_for(case)
    result = design_complete_one_way_slab_is456(**request)
    return {"case": case, "request": request, "result": asdict(result)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=_CASE_NAMES, default="baseline")
    args = parser.parse_args()
    print(json.dumps(run_case(args.case), allow_nan=False, sort_keys=True))


if __name__ == "__main__":
    main()
